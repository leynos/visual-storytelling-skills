#!/usr/bin/env python3
"""Run ``uv`` reliably: clean environment, global cache, offline gates.

``uv_gate.py`` is a single stdlib-only file that repositories vendor
byte-for-byte as ``scripts/uv_gate.py``. It implements the procedure in
``uv-robust-execution.md``:

* ``prepare`` runs ``uv sync --locked --offline``. Only when uv proves one of
  four recoverable misses does it run **one** online ``uv sync --locked``: a
  required file missing from the cache (``cache-miss``), an offline resolution
  that needs uncached data (``offline-resolution``), a managed Python download
  that is available but blocked by the offline switch (``missing-python``), or a
  Git source that is not cached (``missing-git-source``).
* ``run`` runs ``uv run --frozen --offline <command>``. It never goes online
  and never retries, whatever the failure.
* ``tool`` runs ``uv tool run --offline`` for a pinned tool. Like ``prepare``,
  it goes online once, and only for the same four proven misses. A tool spec is
  pinned by ``name==VERSION``, ``name@VERSION``, ``git+URL@<full commit SHA>`` or
  the direct reference ``name[extra] @ git+URL@<full commit SHA>``.

Every invocation uses a cleaned environment (no inherited Git configuration,
tokens or ``BASH_ENV``, no ``~/.lody`` on ``PATH``, no Git prompts, and
``/usr/bin/git`` for Git-backed fetches) and the global uv cache. When the
cache and the project's virtual environment are on different filesystems it
sets ``UV_LINK_MODE=copy``.

The helper never refreshes a lock file, never purges a cache and never
retries a failed test, stale lock, authentication error or missing package.
Its exit status is uv's exit status; its own refusals exit with status 2.
Failures print one ``uv-gate: <class>: ...`` line on standard error after uv's
own output, which is passed through unchanged.

Only the short, fixed ``uv cache dir`` query has a timeout. The commands uv
runs for the caller have none, because a test suite may run for a long time:
the CI job's own timeout is their bound.

Python 3.9 or later is enough: the file uses only the standard library.
"""

from __future__ import annotations

import contextlib
import enum
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import typing as typ
from pathlib import Path

if typ.TYPE_CHECKING:
    import collections.abc as cabc

VERSION = "0.2.3"
REFUSAL_STATUS = 2
ALLOW_ONLINE_VARIABLE = "UV_GATE_ALLOW_ONLINE"
SYSTEM_GIT = Path("/usr/bin/git")
TAIL_BYTES = 65536
# The cache query is short and fixed; the commands uv runs for the caller are
# bounded only by the caller's own job timeout, since a test suite may be slow.
CACHE_QUERY_SECONDS = 60

# Inherited uv switches that would override the gate's own policy: offline or
# no-cache state defeats the online step and the global cache, and the
# refresh, frozen and locked switches change freshness behind the gate's back.
STRIPPED_VARIABLES = frozenset(
    {
        "GH_TOKEN",
        "GITHUB_TOKEN",
        "BASH_ENV",
        "UV_CACHE_DIR",
        "UV_TOOL_DIR",
        "UV_OFFLINE",
        "UV_NO_CACHE",
        "UV_FROZEN",
        "UV_LOCKED",
    }
)
STRIPPED_PREFIXES = ("GIT_CONFIG_", "UV_REFRESH", "UV_UPGRADE")

# Flags that would make a gate refresh, upgrade or purge instead of read the
# prepared environment. The procedure forbids all of them as automatic recovery.
FORBIDDEN_FLAGS = (
    "--no-offline",
    "--no-cache",
    "--no-frozen",
    "--no-locked",
    "--locked",
    "--frozen",
    "--offline",
)
# Whole families, so ``--refresh-package`` and friends are refused too.
FORBIDDEN_PREFIXES = ("--refresh", "--upgrade", "--reinstall")
# Short aliases: ``-U`` (upgrade), ``-P`` (upgrade package), ``-n`` (no cache).
FORBIDDEN_SHORT = "UPn"
FULL_SHA = re.compile(r"[0-9a-f]{40}")
PINNED_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*(?:\[[^\]]+\])?")
PINNED_VERSION = re.compile(r"[A-Za-z0-9][A-Za-z0-9._+!-]*")
# PEP 508 direct reference to a Git URL: `name[extra] @ git+URL@ref`.
DIRECT_REFERENCE = re.compile(
    rf"(?P<name>{PINNED_NAME.pattern})\s*@\s*(?P<url>git\+\S+)"
)


class Kind(enum.Enum):
    """The classes of uv failure that the helper tells apart."""

    CACHE_MISS = "cache-miss"
    OFFLINE_RESOLUTION = "offline-resolution"
    STALE_LOCK = "stale-lock"
    MISSING_LOCK = "missing-lock"
    MISSING_PACKAGE = "missing-package"
    MISSING_REVISION = "missing-revision"
    MISSING_PYTHON = "missing-python"
    MISSING_GIT_SOURCE = "missing-git-source"
    AUTH = "auth"
    UNKNOWN = "unknown"


# Order matters: the first matching signature wins. Whitespace is matched
# loosely because uv wraps its messages at the terminal width.
SIGNATURES: tuple[tuple[Kind, re.Pattern[str]], ...] = (
    (Kind.STALE_LOCK, re.compile(r"lockfile\s+at\s+`?uv\.lock`?\s+needs\s+to\s+be")),
    (Kind.MISSING_LOCK, re.compile(r"Unable\s+to\s+find\s+lockfile")),
    (
        Kind.CACHE_MISS,
        re.compile(
            r"Network\s+connectivity\s+is\s+disabled,\s+but\s+the\s+requested\s+data"
            r"\s+wasn't\s+found\s+in\s+the\s+cache"
        ),
    ),
    (
        Kind.AUTH,
        re.compile(
            r"terminal\s+prompts\s+disabled|could\s+not\s+read\s+(?:Username|Password)"
            r"|Authentication\s+failed|Permission\s+denied\s+\(publickey\)"
            r"|Repository\s+not\s+found|\b40[13]\s+(?:Unauthorized|Forbidden)"
            r"|status\s+code\s+40[13]",
            re.IGNORECASE,
        ),
    ),
    (
        Kind.MISSING_REVISION,
        re.compile(
            r"failed\s+to\s+find\s+branch,\s+tag,\s+or\s+commit"
            r"|unknown\s+revision\s+or\s+path"
        ),
    ),
    (
        Kind.MISSING_PACKAGE,
        re.compile(r"was\s+not\s+found\s+in\s+the\s+package\s+registry"),
    ),
    (
        # Both lines are required: the header alone also appears when no download
        # exists, and only the hint proves that going online can fix it. Recorded
        # from uv 0.13.0; another wording is `unknown`.
        Kind.MISSING_PYTHON,
        re.compile(
            r"No\s+interpreter\s+found\s+for\s+[^\n]+?\s+in\s+managed\s+installations"
            r"(?s:.*)A\s+managed\s+Python\s+download\s+is\s+available\s+for\s+"
            r"[^\n]+?,\s+but\s+uv\s+is\s+set\s+to\s+offline\s+mode"
        ),
    ),
    (
        # uv's own sentence for a Git source that is not in the cache, recorded
        # from uv 0.13.0 (the version setup-uv installed on 2026-10-11). uv 0.9.21
        # prints only "Git operation failed" without the reason, which stays
        # `unknown`: that wording also covers a failed fetch, which a retry may
        # not fix. A different wording in any other uv version is `unknown` too.
        Kind.MISSING_GIT_SOURCE,
        re.compile(
            r"Remote\s+Git\s+fetches\s+are\s+not\s+allowed\s+because\s+network"
            r"\s+connectivity\s+is\s+disabled"
        ),
    ),
    (
        Kind.OFFLINE_RESOLUTION,
        re.compile(
            r"not\s+found\s+in\s+the\s+cache(?s:.*)network\s+was\s+disabled"
            r"|network\s+was\s+disabled(?s:.*)not\s+found\s+in\s+the\s+cache"
            # The variant for a package that a requirement needs but the cache
            # lacks: "needs to be downloaded from a registry" with the hint
            # "registry packages may only be read from the cache".
            r"|needs\s+to\s+be\s+downloaded\s+from\s+a\s+registry"
            r"(?s:.*)network\s+was\s+disabled"
        ),
    ),
)

# The failure classes that earn the one online attempt in `prepare` and `tool`.
# `run` never goes online, so none of them applies to it.
ONLINE_RECOVERABLE = frozenset(
    {
        Kind.CACHE_MISS,
        Kind.OFFLINE_RESOLUTION,
        Kind.MISSING_PYTHON,
        Kind.MISSING_GIT_SOURCE,
    }
)

ADVICE = {
    Kind.CACHE_MISS: "a required file is not in the uv cache",
    Kind.OFFLINE_RESOLUTION: (
        "offline resolution needs data that is not in the uv cache"
    ),
    Kind.STALE_LOCK: (
        "uv.lock is out of date. Run `uv lock` yourself and commit it; the gate "
        "never refreshes a lock file"
    ),
    Kind.MISSING_LOCK: (
        "uv.lock is missing. Create it with `uv lock`, commit it, and run again"
    ),
    Kind.MISSING_PYTHON: (
        "a managed Python interpreter is not installed and uv is offline"
    ),
    Kind.MISSING_GIT_SOURCE: ("a Git source is not in the uv cache and uv is offline"),
    Kind.MISSING_PACKAGE: (
        "a package or version does not exist in the registry; not retried"
    ),
    Kind.MISSING_REVISION: (
        "a Git revision does not exist at the pinned source; not retried"
    ),
    Kind.AUTH: (
        "authentication failed or the repository is not accessible with the "
        "current credentials; not retried. Fix the credential, not the gate"
    ),
    Kind.UNKNOWN: "uv failed for a reason the gate does not retry",
}


class GateError(Exception):
    """A refusal by the helper itself, reported with exit status 2."""


def _discard_stderr() -> None:
    """Point standard error at the null device once its reader has gone.

    A write that fails leaves its bytes buffered, and the interpreter would
    then fail again flushing them at exit and replace uv's status with 120.
    Redirecting descriptor 2 lets the buffer flush and later writes succeed.
    """
    with contextlib.suppress(OSError, ValueError):
        descriptor = os.open(os.devnull, os.O_WRONLY)
        os.dup2(descriptor, 2)
        os.close(descriptor)


def say(message: str) -> None:
    """Print one ``uv-gate:`` line on standard error.

    A closed standard error, as under ``make test 2>&1 | head``, never changes
    the exit status: the line is dropped and the helper carries on.
    """
    try:
        sys.stderr.write(f"uv-gate: {message}\n")
        sys.stderr.flush()
    except (OSError, ValueError):
        _discard_stderr()


def classify(text: str) -> Kind:
    """Name the class of uv failure shown in ``text``.

    Parameters
    ----------
    text:
        The tail of uv's standard error.

    Returns
    -------
    Kind
        The first matching class, or ``Kind.UNKNOWN`` when none matches.

    Examples
    --------
    >>> classify("Unable to find lockfile at `uv.lock`.") is Kind.MISSING_LOCK
    True
    >>> classify("everything exploded") is Kind.UNKNOWN
    True
    """
    for kind, pattern in SIGNATURES:
        if pattern.search(text):
            return kind
    return Kind.UNKNOWN


def clean_environment(environ: cabc.Mapping[str, str], home: Path) -> dict[str, str]:
    """Return ``environ`` without inherited Git, token and uv-location state.

    Parameters
    ----------
    environ:
        The environment to clean; it is not modified.
    home:
        The home directory whose ``.lody`` tree is removed from ``PATH``.

    Returns
    -------
    dict[str, str]
        A new environment with ``GIT_TERMINAL_PROMPT=0`` set.
    """
    env = {
        key: value
        for key, value in environ.items()
        if key not in STRIPPED_VARIABLES and not key.startswith(STRIPPED_PREFIXES)
    }
    lody = str(home / ".lody")
    env["PATH"] = os.pathsep.join(
        item
        for item in env.get("PATH", "").split(os.pathsep)
        if item != lody and not item.startswith(lody + os.sep)
    )
    env["GIT_TERMINAL_PROMPT"] = "0"
    return env


def device_of(path: Path) -> int:
    """Return the device number (``st_dev``) of ``path``.

    Raises
    ------
    OSError
        When ``path`` cannot be inspected; ``build_context`` turns this into a
        ``GateError`` at the command boundary.
    """
    return path.stat().st_dev


def needs_copy_mode(
    environment_dir: Path,
    cache_dir: Path,
    device: cabc.Callable[[Path], int] = device_of,
) -> bool:
    """Report whether two resolved directories are on different devices.

    ``uv`` hard-links cached files when the cache and the environment share a
    filesystem and copies them otherwise. The arguments are already resolved,
    so the only environmental access is ``device``.

    Parameters
    ----------
    environment_dir:
        The resolved directory that will hold the project environment (or the
        repository root while the environment does not exist yet).
    cache_dir:
        The resolved global cache directory.
    device:
        Returns the device number of a path. Tests inject it to feed two
        different devices without a second filesystem.

    Returns
    -------
    bool
        ``True`` when ``UV_LINK_MODE=copy`` is required.

    Raises
    ------
    OSError
        When a device query fails (propagated from ``device``).
    """
    return device(environment_dir) != device(cache_dir)


def probe_link_paths(
    cache: Path, environment_path: Path, repo: Path
) -> tuple[Path, Path]:
    """Resolve the two directories whose devices decide the link mode.

    The environment's own location is used when it exists, since a ``.venv``
    may be a symlink to another filesystem; otherwise the repository root is.

    Parameters
    ----------
    cache:
        The global cache directory.
    environment_path:
        The project's virtual environment, which may not exist yet.
    repo:
        The repository root, used when the environment does not exist.

    Returns
    -------
    tuple[Path, Path]
        The resolved environment (or repository) directory and cache directory.

    Raises
    ------
    GateError
        When a path cannot be inspected or resolved.
    """
    try:
        target = environment_path if environment_path.exists() else repo
        return target.resolve(), cache.resolve()
    except OSError as exc:
        message = f"cannot resolve the uv cache and project paths: {exc}"
        raise GateError(message) from exc


def copy_mode_required(
    cache: Path,
    environment_path: Path,
    repo: Path,
    device: cabc.Callable[[Path], int] = device_of,
) -> bool:
    """Probe the paths, then report whether copy mode is needed.

    Raises
    ------
    GateError
        When a path cannot be resolved or a device query fails.
    """
    environment_dir, cache_dir = probe_link_paths(cache, environment_path, repo)
    try:
        return needs_copy_mode(environment_dir, cache_dir, device)
    except OSError as exc:
        message = f"cannot compare the filesystems of the uv cache and project: {exc}"
        raise GateError(message) from exc


class Context:
    """The cleaned environment, the located uv and the selected cache."""

    def __init__(self, env: dict[str, str], uv: str, cache: Path) -> None:
        """Hold the resolved execution context."""
        self.env = env
        self.uv = uv
        self.cache = cache
        self._shim_dir: str | None = None

    def install_git_shim(self) -> None:
        """Put ``/usr/bin/git`` first on ``PATH`` through a one-file shim dir."""
        if not (SYSTEM_GIT.is_file() and os.access(SYSTEM_GIT, os.X_OK)):
            return
        self._shim_dir = tempfile.mkdtemp(prefix="uv-gate-git-")
        (Path(self._shim_dir) / "git").symlink_to(SYSTEM_GIT)
        self.env["PATH"] = os.pathsep.join([self._shim_dir, self.env["PATH"]])

    def close(self) -> None:
        """Remove the Git shim directory, if one was made."""
        if self._shim_dir is not None:
            shutil.rmtree(self._shim_dir, ignore_errors=True)
            self._shim_dir = None


def _query_cache_dir(uv: str, env: dict[str, str]) -> Path:
    """Ask uv for the global cache directory with no config and no override."""
    try:
        process = subprocess.Popen(  # noqa: S603  # fixed argv, no shell
            [uv, "--no-config", "cache", "dir"],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        stdout, stderr = process.communicate(timeout=CACHE_QUERY_SECONDS)
    except OSError as exc:
        message = f"cannot run {uv} to find the cache directory: {exc}"
        raise GateError(message) from exc
    except subprocess.TimeoutExpired as exc:
        process.kill()
        process.communicate()
        message = (
            f"`{uv} --no-config cache dir` did not answer within {CACHE_QUERY_SECONDS}s"
        )
        raise GateError(message) from exc
    if process.returncode != 0 or not stdout.strip():
        message = (
            f"`{uv} --no-config cache dir` failed with status {process.returncode}: "
            f"{stderr.strip()}"
        )
        raise GateError(message)
    return Path(stdout.strip())


def _locate_uv(env: cabc.Mapping[str, str]) -> str:
    """Find uv on the cleaned ``PATH``, or refuse."""
    try:
        found = shutil.which("uv", path=env["PATH"])
        if found is not None:
            return str(Path(found).resolve())
    except OSError as exc:
        message = f"cannot look for uv on the cleaned PATH: {exc}"
        raise GateError(message) from exc
    message = "uv is not available on the cleaned PATH; install uv and retry"
    raise GateError(message)


def _ensure_cache(cache: Path) -> Path:
    """Create the cache directory, or refuse."""
    try:
        cache.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        message = f"cannot create the uv cache directory {cache}: {exc}"
        raise GateError(message) from exc
    return cache


def _with_git_shim(context: Context) -> Context:
    """Install the Git shim, closing the context and refusing on failure."""
    try:
        context.install_git_shim()
    except OSError as exc:
        context.close()
        message = f"cannot set up the Git shim directory: {exc}"
        raise GateError(message) from exc
    return context


def build_context(
    environ: cabc.Mapping[str, str],
    repo: Path,
    home: Path | None = None,
    device: cabc.Callable[[Path], int] = device_of,
) -> Context:
    """Build the cleaned environment, locate uv and select the cache.

    Parameters
    ----------
    environ:
        The inherited environment.
    repo:
        The repository root (normally the current directory).
    home:
        The home directory, defaulting to ``Path.home()``.
    device:
        Returns a path's device number; injected by tests, see
        ``needs_copy_mode``.

    Returns
    -------
    Context
        The ready context. Call ``Context.close`` when finished.

    Raises
    ------
    GateError
        When uv is absent from the cleaned ``PATH``, the cache directory
        cannot be found or created, or the filesystems cannot be compared.
    """
    env = clean_environment(environ, home or Path.home())
    uv = _locate_uv(env)
    cache = _ensure_cache(_query_cache_dir(uv, env))
    env["UV_CACHE_DIR"] = str(cache)
    configured = env.get("UV_PROJECT_ENVIRONMENT")
    environment_path = (repo / configured) if configured else repo / ".venv"
    if copy_mode_required(cache, environment_path, repo, device):
        env["UV_LINK_MODE"] = "copy"
    return _with_git_shim(Context(env, uv, cache))


def _forward_stderr(chunk: bytes) -> bool:
    """Write ``chunk`` to our standard error; report whether forwarding can go on."""
    try:
        sys.stderr.buffer.write(chunk)
        sys.stderr.buffer.flush()
    except (OSError, ValueError):
        _discard_stderr()
        return False
    return True


def _run_streaming(argv: list[str], env: dict[str, str]) -> tuple[int, str]:
    """Run ``argv``, passing standard error through while keeping its tail."""
    tail = bytearray()
    try:
        process = subprocess.Popen(  # noqa: S603  # fixed argv, no shell
            argv, env=env, stderr=subprocess.PIPE
        )
    except OSError as exc:
        message = f"cannot start {argv[0]}: {exc}"
        raise GateError(message) from exc
    stream = process.stderr
    if stream is None:  # pragma: no cover - PIPE was requested
        return process.wait(), ""

    def pump() -> None:
        """Copy the child's standard error to ours, keeping the last bytes.

        A failed write stops the forwarding but never the reading: a child
        that blocks on a full pipe would otherwise hang ``process.wait()``.
        """
        forwarding = True
        while chunk := os.read(stream.fileno(), 4096):
            tail.extend(chunk)
            del tail[:-TAIL_BYTES]
            forwarding = forwarding and _forward_stderr(chunk)

    reader = threading.Thread(target=pump)
    reader.start()
    try:
        status = process.wait()
    except BaseException:
        process.terminate()
        raise
    finally:
        reader.join()
    return status, tail.decode("utf-8", errors="replace")


def _online_allowed(env: cabc.Mapping[str, str]) -> bool:
    """Report whether the single bounded online step may run."""
    return env.get(ALLOW_ONLINE_VARIABLE, "1") != "0"


TOOL_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")


def describe_spec(spec: str) -> str:
    """Name a tool specification without its URL, credentials or version.

    A pinned Git specification can carry URL userinfo or query strings, so
    logs and refusals use only the package name, or a fixed label for Git URLs.
    """
    if spec.startswith("git+"):
        return "a git+ URL"
    found = TOOL_NAME.match(spec)
    return found.group(0) if found else "an unnamed tool"


def _report(kind: Kind, status: int, *, where: str) -> None:
    """Explain a failure that the helper will not retry."""
    say(f"{kind.value}: {where} failed with status {status}. {ADVICE[kind]}.")


def _is_forbidden_short(name: str) -> bool:
    """Report whether ``name`` is, or clusters, a forbidden single-dash alias.

    A first letter in ``FORBIDDEN_SHORT`` is always refused. A purely
    alphabetic cluster such as ``-qU`` is refused when any letter is
    forbidden, so a boolean flag cannot smuggle ``-U`` or ``-n`` behind
    another. That also refuses a value glued to a short option (``-pPyPy``),
    which fails closed; write ``-p PyPy`` instead.
    """
    if name[:1] != "-" or name[1:2] in {"", "-"}:
        return False
    letters = name[1:]
    return letters[0] in FORBIDDEN_SHORT or (
        letters.isalpha() and any(flag in FORBIDDEN_SHORT for flag in letters)
    )


def _is_forbidden(name: str) -> bool:
    """Report whether ``name`` overrides the gate's own policy."""
    return (
        name in FORBIDDEN_FLAGS
        or name.startswith(FORBIDDEN_PREFIXES)
        or _is_forbidden_short(name)
    )


def _refuse_forbidden(arguments: cabc.Sequence[str]) -> None:
    """Refuse flags that would refresh, upgrade or go online implicitly."""
    for argument in arguments:
        name = argument.split("=", 1)[0]
        if _is_forbidden(name):
            message = (
                f"{name} is not allowed: the gate controls locking, freshness "
                "and network use itself"
            )
            raise GateError(message)


def prepare(ctx: Context, sync_args: cabc.Sequence[str]) -> int:
    """Prepare dependencies offline, going online once for a proven miss.

    Parameters
    ----------
    ctx:
        The execution context.
    sync_args:
        Extra ``uv sync`` arguments (groups, extras, Python version) that the
        gates must also use.

    Returns
    -------
    int
        uv's exit status.
    """
    offline = [ctx.uv, "sync", "--locked", "--offline", *sync_args]
    status, text = _run_streaming(offline, ctx.env)
    if status == 0:
        return 0
    kind = classify(text)
    if kind not in ONLINE_RECOVERABLE:
        _report(kind, status, where="uv sync --locked --offline")
        return status
    if not _online_allowed(ctx.env):
        say(
            f"{kind.value}: {ADVICE[kind]}; the online retry is disabled by "
            f"{ALLOW_ONLINE_VARIABLE}=0."
        )
        return status
    say(f"{kind.value}: {ADVICE[kind]}; running one online `uv sync --locked`.")
    online = [ctx.uv, "sync", "--locked", *sync_args]
    status, text = _run_streaming(online, ctx.env)
    if status != 0:
        _report(classify(text), status, where="uv sync --locked")
    return status


def run_gate(
    ctx: Context, uv_args: cabc.Sequence[str], command: cabc.Sequence[str]
) -> int:
    """Run ``command`` in the prepared environment, offline and frozen.

    Parameters
    ----------
    ctx:
        The execution context.
    uv_args:
        Extra ``uv run`` arguments (groups, extras, Python version).
    command:
        The command to run.

    Returns
    -------
    int
        The command's exit status.
    """
    argv = [ctx.uv, "run", "--frozen", "--offline", *uv_args, *command]
    status, text = _run_streaming(argv, ctx.env)
    if status != 0:
        kind = classify(text)
        if kind is not Kind.UNKNOWN:
            say(f"{kind.value}: {ADVICE[kind]}. Run `prepare` first if needed.")
    return status


def tool_spec(tool_args: cabc.Sequence[str], command: cabc.Sequence[str]) -> str:
    """Return the tool specification that ``uv tool run`` would execute.

    Parameters
    ----------
    tool_args:
        Options placed before ``--``; ``--from SPEC`` names the package.
    command:
        The words after ``--``; the first is the executable.

    Returns
    -------
    str
        The ``--from`` value, or the executable when ``--from`` is absent.

    Raises
    ------
    GateError
        When there is nothing to run.
    """
    for index, argument in enumerate(tool_args):
        if argument == "--from" and index + 1 < len(tool_args):
            return tool_args[index + 1]
        if argument.startswith("--from="):
            return argument.split("=", 1)[1]
    if not command:
        message = "tool needs `--from SPEC` or a command after `--`"
        raise GateError(message)
    return command[0]


def is_pinned(spec: str) -> bool:
    """Report whether ``spec`` pins an exact version or a full commit.

    Accepted: ``name==1.2.3``, ``name@1.2.3``, ``git+URL@<40 hex digits>`` and
    the same Git URL as a direct reference, ``name[extra] @ git+URL@<40 hex
    digits>``. Rejected: bare names, ranges, ``@latest`` and Git refs that are
    not a full commit SHA, in either Git form.

    Examples
    --------
    >>> is_pinned("ruff==0.16.4"), is_pinned("typos@1.2.3"), is_pinned("ruff")
    (True, True, False)
    >>> is_pinned("cibuildwheel>=2.16"), is_pinned("tool@latest")
    (False, False)
    >>> sha = "0123456789abcdef0123456789abcdef01234567"
    >>> is_pinned(f"tool[extra] @ git+https://example.invalid/t.git@{sha}")
    True
    >>> is_pinned("tool[extra] @ git+https://example.invalid/t.git@main")
    False
    """
    direct = DIRECT_REFERENCE.fullmatch(spec)
    if direct is not None:
        return is_pinned(direct.group("url"))
    if spec.startswith("git+"):
        location = spec.split("#", 1)[0]
        _, found, ref = location.rpartition("@")
        return bool(found and FULL_SHA.fullmatch(ref))
    return any(_is_exact_pin(spec, separator) for separator in ("==", "@"))


def _is_exact_pin(spec: str, separator: str) -> bool:
    """Report whether ``spec`` is ``name<separator>version`` with a real version."""
    name, found, version = spec.partition(separator)
    if not found or version == "latest":
        return False
    return bool(PINNED_NAME.fullmatch(name) and PINNED_VERSION.fullmatch(version))


def tool(
    ctx: Context, tool_args: cabc.Sequence[str], command: cabc.Sequence[str]
) -> int:
    """Run a pinned tool offline, warming it online once on a proven miss.

    Parameters
    ----------
    ctx:
        The execution context.
    tool_args:
        Options for ``uv tool run`` placed before ``--``.
    command:
        The executable and its arguments.

    Returns
    -------
    int
        The tool's exit status.

    """
    spec = tool_spec(tool_args, command)
    base = [ctx.uv, "tool", "run"]
    status, text = _run_streaming([*base, "--offline", *tool_args, *command], ctx.env)
    if status == 0:
        return 0
    kind = classify(text)
    if kind not in ONLINE_RECOVERABLE:
        _report(kind, status, where="uv tool run --offline")
        return status
    if not _online_allowed(ctx.env):
        say(
            f"{kind.value}: {ADVICE[kind]}; the online retry is disabled by "
            f"{ALLOW_ONLINE_VARIABLE}=0."
        )
        return status
    say(f"{kind.value}: {ADVICE[kind]}; warming {describe_spec(spec)} online once.")
    status, text = _run_streaming([*base, *tool_args, *command], ctx.env)
    if status != 0:
        _report(classify(text), status, where="uv tool run")
    return status


USAGE = """\
usage: uv_gate.py prepare [UV_SYNC_ARGS...]
       uv_gate.py run [UV_RUN_ARGS...] -- COMMAND [ARGS...]
       uv_gate.py tool [--from SPEC] [UV_TOOL_RUN_ARGS...] -- EXECUTABLE [ARGS...]

prepare  uv sync --locked --offline; one online `uv sync --locked` only when
         uv proves a file is missing from the cache.
run      uv run --frozen --offline; never online, never retried.
tool     uv tool run --offline for a pinned tool; warmed online once on a
         proven cache miss.

Set UV_GATE_ALLOW_ONLINE=0 to forbid the online step entirely.
"""


def _split(arguments: cabc.Sequence[str]) -> tuple[list[str], list[str]]:
    """Split ``arguments`` at the first ``--``."""
    items = list(arguments)
    if "--" not in items:
        return items, []
    index = items.index("--")
    return items[:index], items[index + 1 :]


def main(
    argv: cabc.Sequence[str] | None = None,
    environ: cabc.Mapping[str, str] | None = None,
) -> int:
    """Run the helper and return its exit status.

    Parameters
    ----------
    argv:
        Arguments after the program name; defaults to ``sys.argv[1:]``.
    environ:
        The inherited environment; defaults to ``os.environ``.

    Returns
    -------
    int
        uv's exit status, or 2 when the helper itself refuses.
    """
    args = list(sys.argv[1:] if argv is None else argv)
    if args[:1] in (["-V"], ["--version"]):
        sys.stdout.write(f"uv_gate {VERSION}\n")
        return 0
    if not args or args[0] in {"-h", "--help"}:
        sys.stderr.write(USAGE)
        return REFUSAL_STATUS if not args else 0
    subcommand, rest = args[0], args[1:]
    if subcommand not in {"prepare", "run", "tool"}:
        say(f"unknown subcommand {subcommand!r}")
        sys.stderr.write(USAGE)
        return REFUSAL_STATUS
    status, refused = _dispatch(subcommand, rest, environ)
    outcome = "refused" if refused else "ok" if status == 0 else "failed"
    say(f"metric uv-gate.{subcommand}={outcome}")
    return status


def validate_request(subcommand: str, rest: cabc.Sequence[str]) -> None:
    """Check a request without touching the environment or the filesystem.

    Parameters
    ----------
    subcommand:
        One of ``prepare``, ``run`` or ``tool``.
    rest:
        The arguments after the subcommand.

    Raises
    ------
    GateError
        For a forbidden flag, a missing command, or an unpinned tool.
    """
    before, after = (list(rest), []) if subcommand == "prepare" else _split(rest)
    _refuse_forbidden(before)
    if subcommand == "run" and not after:
        message = "run needs a command after `--`"
        raise GateError(message)
    if subcommand == "tool":
        spec = tool_spec(before, after)
        if not is_pinned(spec):
            message = (
                f"tool spec for {describe_spec(spec)} is not pinned; use "
                "name==VERSION, name@VERSION or git+URL@<full commit SHA>"
            )
            raise GateError(message)


def _dispatch(
    subcommand: str,
    rest: cabc.Sequence[str],
    environ: cabc.Mapping[str, str] | None,
) -> tuple[int, bool]:
    """Run ``subcommand``; return its status and whether the helper refused."""
    context: Context | None = None
    try:
        validate_request(subcommand, rest)
        context = build_context(os.environ if environ is None else environ, Path.cwd())
        if subcommand == "prepare":
            return prepare(context, rest), False
        before, after = _split(rest)
        if subcommand == "run":
            return run_gate(context, before, after), False
        return tool(context, before, after), False
    except GateError as exc:
        say(str(exc))
        return REFUSAL_STATUS, True
    finally:
        if context is not None:
            context.close()


if __name__ == "__main__":
    sys.exit(main())
