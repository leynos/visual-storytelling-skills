# Assistant Instructions

## Code Style and Structure

- **Code is for humans.** Write your code with clarity and empathy—assume a
  tired teammate will need to debug it at 3 a.m.
- **Comment *why*, not *what*.** Explain assumptions, edge cases, trade-offs,
  or complexity. Don't echo the obvious.
- **Clarity over cleverness.** Be concise, but favour explicit over terse or
  obscure idioms. Prefer code that's easy to follow.
- **Use functions and composition.** Avoid repetition by extracting reusable
  logic. Prefer generators or comprehensions to imperative repetition when
  readable.
- **Name things precisely.** Use clear, descriptive variable and function
  names. For booleans, prefer names with `is`, `has`, or `should`.
- **Structure logically.** Each file should encapsulate a coherent module.
  Group related code (e.g., models + utilities + fixtures) close together.
- **Group by feature, not layer.** Colocate views, logic, fixtures, and helpers
  related to a domain concept rather than splitting by type.

## Documentation Maintenance

- **Reference:** Use the markdown files within the `docs/` directory as a
  knowledge base and source of truth for project requirements, dependency
  choices, and architectural decisions.
- **Update:** When new decisions are made, requirements change, libraries are
  added/removed, or architectural patterns evolve, **proactively update** the
  relevant file(s) in the `docs/` directory to reflect the latest state. Ensure
  the documentation remains accurate and current.
- **Style:** All documentation must adhere to the
  [documentation style guide](docs/documentation-style-guide.md).

## Guidelines for Code Changes & Testing

When implementing changes, adhere to the following testing procedures:

- **New Functionality:**
  - Implement unit tests covering all new code units (functions, components,
    classes). Implement tests **before** implementing the unit.
  - Implement behavioral tests that verify the end-to-end behavior of the new
    feature from a user interaction perspective.
  - Ensure both unit and behavioral tests pass before considering the
    functionality complete.
  - Ensure that new functionality is clearly documented in the
    [users' guide](docs/users-guide.md).
  - Ensure that any design decisions made are recorded in the relevant design
    document.
- **Bug Fixes:**
  - Before fixing the bug, write a new test (unit or behavioral, whichever is
    most appropriate) that specifically targets and reproduces the bug. This
    test should initially fail.
  - Implement the bug fix.
  - Verify that the new test now passes, along with all existing tests.
  - Ensure that any design decisions made are recorded in the relevant design
    document.
- **Modifying Existing Functionality:**
  - Identify the existing behavioral and unit tests relevant to the
    functionality being changed.
  - **First, modify the tests** to reflect the new requirements or behavior.
  - Run the tests; they should now fail.
  - Implement the code changes to the functionality.
  - Verify that the modified tests (and all other existing tests) now pass.
  - Ensure that revised functionality is clearly documented in the
    [users' guide](docs/users-guide.md).
  - Ensure that any design decisions made are recorded in the relevant design
    document.
- **Refactoring:**
  - Identify or create a behavioral test that covers the functionality being
    refactored. Ensure this test passes **before** starting the refactor.
  - Perform the refactoring (e.g., extracting logic into a new unit).
  - If new units are created (e.g., a new function or component), add unit
    tests for these extracted units.
  - After the refactor, ensure the original behavioral test **still passes**
    without modification. Also ensure any new unit tests pass.

## Change Quality & Committing

- **Atomicity:** Aim for small, focused, atomic changes. Each change (and
  subsequent commit) should represent a single logical unit of work.
- **Quality Gates:** Before considering a change complete or proposing a
  commit, ensure it meets the following criteria:
  - For Python files:
    - **Testing:** Passes all relevant unit and behavioral tests according to
      the guidelines above (run `make test` to verify).
    - **Linting:** Passes lint checks (`make lint`).
    - **Formatting:** Adheres to formatting standards (run `make check-fmt` to
      verify, use `make fmt` to apply formatting).
    - **Typechecking:** Passes type checking (`make typecheck`).
  - For Markdown files (`.md` only):
    - **Linting:** Passes lint checks (`make markdownlint`).
    - **Mermaid diagrams:** Passes validation using nixie (`make nixie`)
- **Committing:**
  - Only changes that meet all the quality gates above should be committed.
  - Write clear, descriptive commit messages summarizing the change, following
    these formatting guidelines:
    - **Imperative Mood:** Use the imperative mood in the subject line (e.g.,
      "Fix bug", "Add feature" instead of "Fixed bug", "Added feature").
    - **Subject Line:** The first line should be a concise summary of the
      change (ideally 50 characters or less).
    - **Body:** Separate the subject from the body with a blank line.
      Subsequent lines should explain the *what* and *why* of the change in
      more detail, including rationale, goals, and scope. Wrap the body at 72
      characters.
    - **Formatting:** Use Markdown for any formatted text (like bullet points
      or code snippets) within the commit message body.
  - Do not commit changes that fail any of the quality gates.

## Refactoring Heuristics & Workflow

- **Recognizing Refactoring Needs:** Regularly assess the codebase for
  potential refactoring opportunities. Consider refactoring when you observe:
  - **Long Methods/Functions:** Functions or methods that are excessively long
    or try to do too many things.
  - **Duplicated Code:** Identical or very similar code blocks appearing in
    multiple places.
  - **Complex Conditionals:** Deeply nested or overly complex `if`/`else` or
    `switch` statements (high cyclomatic complexity).
  - **Large Code Blocks for Single Values:** Significant chunks of logic
    dedicated solely to calculating or deriving a single value.
  - **Primitive Obsession / Data Clumps:** Groups of simple variables (strings,
    numbers, booleans) that are frequently passed around together, often
    indicating a missing class or object structure.
  - **Excessive Parameters:** Functions or methods requiring a very long list
    of parameters.
  - **Feature Envy:** Methods that seem more interested in the data of another
    class/object than their own.
  - **Shotgun Surgery:** A single change requiring small modifications in many
    different classes or functions.
- **Post-Commit Review:** After committing a functional change or bug fix (that
  meets all quality gates), review the changed code and surrounding areas using
  the heuristics above.
- **Separate Atomic Refactors:** If refactoring is deemed necessary:
  - Perform the refactoring as a **separate, atomic commit** *after* the
    functional change commit.
  - Ensure the refactoring adheres to the testing guidelines (behavioral tests
    pass before and after, unit tests added for new units).
  - Ensure the refactoring commit itself passes all quality gates.

## Markdown Guidance

- Validate Markdown files using `make markdownlint`.
- Run `make fmt` after any documentation changes to format all Markdown
  files and fix table markup.
- Validate Mermaid diagrams in Markdown files by running `make nixie`.
- Markdown paragraphs and bullet points must be wrapped at 80 columns.
- Code blocks must be wrapped at 120 columns.
- Tables and headings must not be wrapped.
- Use dashes (`-`) for list bullets.
- Use GitHub-flavoured Markdown footnotes (`[^1]`) for references and
  footnotes.

## Additional tooling

The following tooling is available in this environment:

- `mbake` – A Makefile validator. Run using `mbake validate Makefile`.
- `strace` – Traces system calls and signals made by a process; useful for
  debugging runtime behaviour and syscalls.
- `gdb` – The GNU Debugger, for inspecting and controlling programs as they
  execute (or post-mortem via core dumps).
- `ripgrep` – Fast, recursive text search tool (`grep` alternative) that
  respects `.gitignore` files.
- `ltrace` – Traces calls to dynamic library functions made by a process.
- `valgrind` – Suite for detecting memory leaks, profiling, and debugging
  low-level memory errors.
- `bpftrace` – High-level tracing tool for eBPF, using a custom scripting
  language for kernel and application tracing.
- `lsof` – Lists open files and the processes using them.
- `htop` – Interactive process viewer (visual upgrade to `top`).
- `iotop` – Displays and monitors I/O usage by processes.
- `ncdu` – NCurses-based disk usage viewer for finding large files/folders.
- `tree` – Displays directory structure as a tree.
- `bat` – `cat` clone with syntax highlighting, Git integration, and paging.
- `delta` – Syntax-highlighted pager for Git and diff output.
- `tcpdump` – Captures and analyses network traffic at the packet level.
- `nmap` – Network scanner for host discovery, port scanning, and service
  identification.
- `lldb` – LLVM debugger, alternative to `gdb`.
- `eza` – Modern `ls` replacement with more features and better defaults.
- `fzf` – Interactive fuzzy finder for selecting files, commands, etc.
- `hyperfine` – Command-line benchmarking tool with statistical output.
- `shellcheck` – Linter for shell scripts, identifying errors and bad practices.
- `fd` – Fast, user-friendly `find` alternative with sensible defaults.
- `checkmake` – Linter for `Makefile`s, ensuring they follow best practices and
  conventions.
- `srgn` – [Structural grep](https://github.com/alexpovel/srgn), searches code
  and enables editing by syntax tree patterns.
- `difft` **(Difftastic)** – Semantic diff tool that compares code structure

## Python Development Guidelines

For Python development, refer to the detailed guidelines in the `.rules/`
directory:

- [Python Code Style Guidelines](.rules/python-00.md) - Core Python 3.13 style
  conventions
- [Python Context Managers](.rules/python-context-managers.md) - Best practices
  for context managers
- [Python Exceptions and
  Logging(.rules/python-exception-design-raising-handling-and-logging.md) -
  Throwing, catching and logging exceptions.
- [Python Generators](.rules/python-generators.md) - Generator and iterator
  patterns
- [Python Project Configuration](.rules/python-pyproject.md) - pyproject.toml
  and packaging
- [Python Return Patterns](.rules/python-return.md) - Function return
  conventions
- [Python Typing](.rules/python-typing.md) - Type annotation best practices

Additional docs:

- [Scripting Standards](docs/scripting-standards.md) - Guidance for writing
  robust scripts
