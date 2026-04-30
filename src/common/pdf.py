"""pdfplumber-based PDF extraction utilities."""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any

import pdfplumber

logger = logging.getLogger(__name__)


def extract_tables(pdf_path: Path) -> list[list[list[str | None]]]:
    """Extract all tables from all pages of a PDF.

    Returns a list of tables; each table is a list of rows; each row is a list of cell strings.
    """
    all_tables: list[list[list[str | None]]] = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                all_tables.append(table)
    return all_tables


def extract_text(pdf_path: Path) -> str:
    """Extract full text from all pages of a PDF, joined with newlines."""
    pages: list[str] = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            pages.append(text)
    return "\n".join(pages)


def extract_text_by_page(pdf_path: Path) -> list[str]:
    """Return list of text strings, one per page."""
    with pdfplumber.open(pdf_path) as pdf:
        return [page.extract_text() or "" for page in pdf.pages]


def find_section(text: str, section_header_pattern: str) -> str | None:
    """Extract text block following a regex section header, up to the next header."""
    pattern = re.compile(
        rf"({section_header_pattern})(.*?)(?=\n[A-Z][^\n]{{3,}}:|\Z)",
        re.IGNORECASE | re.DOTALL,
    )
    match = pattern.search(text)
    if match:
        return match.group(2).strip()
    return None


def tables_to_dicts(
    table: list[list[str | None]],
    header_row: int = 0,
) -> list[dict[str, Any]]:
    """Convert a raw pdfplumber table (list of rows) to list of dicts using the header row."""
    if not table or len(table) <= header_row:
        return []
    headers = [str(h or "").strip() for h in table[header_row]]
    rows = []
    for raw_row in table[header_row + 1 :]:
        row_dict = {
            headers[i]: str(cell or "").strip()
            for i, cell in enumerate(raw_row)
            if i < len(headers)
        }
        rows.append(row_dict)
    return rows


def extract_score_pattern(text: str, label: str) -> float | None:
    """Extract a numeric score following a label string, e.g. 'Overall Score: 67.4'."""
    pattern = re.compile(
        rf"{re.escape(label)}\s*[:\-]?\s*(\d+(?:\.\d+)?)",
        re.IGNORECASE,
    )
    match = pattern.search(text)
    if match:
        return float(match.group(1))
    return None
