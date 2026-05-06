"""media-project package."""

from __future__ import annotations

PACKAGE_NAME = "media_project"

try:  # pragma: no cover - Rust optional
    rust = __import__(f"_{PACKAGE_NAME}_rs")
    hello = rust.hello  # type: ignore[attr-defined]
except ModuleNotFoundError:  # pragma: no cover - Python fallback
    from .pure import hello

__all__ = ["hello"]
