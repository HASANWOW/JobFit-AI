"""Text extraction from an uploaded CV."""

from __future__ import annotations

import re
from typing import BinaryIO

from pypdf import PdfReader


def pdf_to_text(file: BinaryIO) -> str:
    """Extract the text of every page and tidy up the whitespace."""
    reader = PdfReader(file)
    pages = [page.extract_text() or "" for page in reader.pages]
    text = "\n".join(pages)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()
