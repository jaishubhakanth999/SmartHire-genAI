"""
Document loading and chunking.

Responsibility: turn uploaded resume bytes (or admin-submitted career-note
text) into plain text, and split long text into overlapping chunks ready for
embedding. Works on in-memory bytes rather than file paths since the FastAPI
upload endpoint never writes the file to disk.
"""

import io
from typing import List

from docx import Document as DocxDocument
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt"}


def load_pdf_bytes(data: bytes) -> str:
    reader = PdfReader(io.BytesIO(data))
    text = "\n".join((page.extract_text() or "") for page in reader.pages).strip()
    if not text:
        raise ValueError("No extractable text in this PDF. It may be a scanned image (needs OCR, unsupported).")
    return text


def load_docx_bytes(data: bytes) -> str:
    document = DocxDocument(io.BytesIO(data))
    text = "\n".join(p.text for p in document.paragraphs if p.text.strip()).strip()
    if not text:
        raise ValueError("No extractable text in this DOCX.")
    return text


def load_txt_bytes(data: bytes) -> str:
    text = data.decode("utf-8", errors="replace").strip()
    if not text:
        raise ValueError("This file is empty.")
    return text


def load_upload(filename: str, data: bytes) -> str:
    """Dispatch to the right loader based on file extension."""
    suffix = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if suffix == ".pdf":
        return load_pdf_bytes(data)
    if suffix == ".docx":
        return load_docx_bytes(data)
    if suffix == ".txt":
        return load_txt_bytes(data)
    raise ValueError(f"Unsupported file type '{suffix}'. Supported types: {sorted(SUPPORTED_EXTENSIONS)}")


def chunk_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
    """Split text into overlapping chunks ready for embedding."""
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return splitter.split_text(text)
