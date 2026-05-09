"""Markdown table extraction for media-project inputs."""

from __future__ import annotations

import html.parser as html_parser
import re

import markdown as markdown_lib

type MarkdownRow = dict[str, str]


class MarkdownTableError(ValueError):
    """Raised when a Markdown table cannot be parsed."""


class _TableHtmlParser(html_parser.HTMLParser):
    """Collect HTML table cell text produced from Markdown input."""

    def __init__(self) -> None:
        """Create an empty parser state for Markdown table extraction."""
        super().__init__()
        self._active_cell: str | None = None
        self._active_row: list[str] | None = None
        self._active_cells: list[list[str]] = []
        self.tables: list[list[list[str]]] = []
        self._table: list[list[str]] | None = None

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        """Track table, row, and cell starts while parsing HTML."""
        del attrs
        if tag == "table":
            self._table = []
        elif tag == "tr" and self._table is not None:
            self._active_row = []
        elif tag in {"td", "th"} and self._active_row is not None:
            self._active_cell = ""

    def handle_data(self, data: str) -> None:
        """Append text to the active table cell."""
        if self._active_cell is not None:
            self._active_cell += data

    def handle_endtag(self, tag: str) -> None:
        """Finalize active cells, rows, and tables at closing tags."""
        if tag in {"td", "th"} and self._active_cell is not None:
            if self._active_row is not None:
                self._active_row.append(_collapse_whitespace(self._active_cell))
            self._active_cell = None
        elif tag == "tr" and self._active_row is not None:
            self._active_cells.append(self._active_row)
            self._active_row = None
        elif tag == "table" and self._table is not None:
            self._table.extend(self._active_cells)
            self.tables.append(self._table)
            self._active_cells = []
            self._table = None


def read_first_table(markdown_text: str) -> list[MarkdownRow]:
    """Return rows from the first GitHub-style Markdown table."""
    html = markdown_lib.markdown(markdown_text, extensions=["tables"])
    parser = _TableHtmlParser()
    parser.feed(html)
    if not parser.tables:
        msg = "No Markdown table found."
        raise MarkdownTableError(msg)

    table = parser.tables[0]
    if not table:
        msg = "Markdown table is empty."
        raise MarkdownTableError(msg)

    headings = [_normalise_heading(value) for value in table[0]]
    return [_row_from_cells(headings, row) for row in table[1:]]


def _row_from_cells(headings: list[str], cells: list[str]) -> MarkdownRow:
    """Map table cell values to normalized headings."""
    padded_cells = [*cells, *([""] * max(0, len(headings) - len(cells)))]
    return dict(zip(headings, padded_cells, strict=False))


def _normalise_heading(value: str) -> str:
    """Return a snake-case metadata key for a table heading."""
    return re.sub(r"[^a-z0-9]+", "_", value.strip().lower()).strip("_")


def _collapse_whitespace(value: str) -> str:
    """Return text with internal whitespace collapsed to single spaces."""
    return re.sub(r"\s+", " ", value).strip()
