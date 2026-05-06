"""Tests for the generated pure Python fallback module."""

from __future__ import annotations

from media_project import hello


def test_hello_returns_python_greeting() -> None:
    """The package exposes the pure Python greeting."""
    assert hello() == "hello from Python"
