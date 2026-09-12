"""
Generic document loading.

Responsibility: turn files on disk into raw text, regardless of format.
Used for resumes, job descriptions and career notes alike. Knows about file
formats (.pdf via PyPDF, .docx via python-docx, .txt directly) and nothing
about what the text means -- that is resume_parser.py's job for CVs, and
plain metadata tagging for everything else.
"""

from pathlib import Path
from typing import Any, Dict, List, Union

from docx import Document as DocxDocument
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader

PathLike = Union[str, Path]

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt"}

# Files we skip when scanning a data/ directory -- documentation, not corpus.
_IGNORED_NAMES = {"readme.md", ".gitkeep"}


def load_pdf(path: PathLike) -> str:
    """Extract text from a single PDF file."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {path}")
    reader = PdfReader(str(path))
    text = "\n".join((page.extract_text() or "") for page in reader.pages).strip()
    if not text:
        raise ValueError(
            f"No extractable text in '{path}'. It may be a scanned image PDF "
            "(would need OCR, which this project does not use)."
        )
    return text


def load_docx(path: PathLike) -> str:
    """Extract text from a single DOCX file."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"DOCX not found: {path}")
    document = DocxDocument(str(path))
    text = "\n".join(p.text for p in document.paragraphs if p.text.strip()).strip()
    if not text:
        raise ValueError(f"No extractable text in '{path}'.")
    return text


def load_txt(path: PathLike) -> str:
    """Read a plain text file."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Text file not found: {path}")
    text = path.read_text(encoding="utf-8", errors="replace").strip()
    if not text:
        raise ValueError(f"'{path}' is empty.")
    return text


def load_file(path: PathLike) -> str:
    """Dispatch to the right loader based on file extension."""
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return load_pdf(path)
    if suffix == ".docx":
        return load_docx(path)
    if suffix == ".txt":
        return load_txt(path)
    raise ValueError(
        f"Unsupported file type '{suffix}' for '{path}'. "
        f"Supported types: {sorted(SUPPORTED_EXTENSIONS)}"
    )


def load_directory(directory: PathLike) -> List[Dict[str, Any]]:
    """
    Load every supported file in a directory into (text, metadata) records.

    Returns a list of {"text": str, "metadata": {"source": str, "filename": str}}.
    Hidden files, README.md and .gitkeep are skipped. A file that fails to
    load (corrupt, empty, scanned-image PDF) is skipped with a printed
    warning rather than aborting the whole batch -- one bad file in a folder
    of fifty should not block the other forty-nine.
    """
    directory = Path(directory)
    if not directory.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")

    documents: List[Dict[str, Any]] = []
    for path in sorted(directory.iterdir()):
        if not path.is_file():
            continue
        if path.name.startswith(".") or path.name.lower() in _IGNORED_NAMES:
            continue
        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue
        try:
            text = load_file(path)
        except (FileNotFoundError, ValueError) as exc:
            print(f"[loader] skipping '{path.name}': {exc}")
            continue
        documents.append({"text": text, "metadata": {"source": str(path), "filename": path.name}})
    return documents


def chunk_documents(
    documents: List[Dict[str, Any]],
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> List[Dict[str, Any]]:
    """
    Split loaded documents into overlapping chunks ready for embedding.

    `documents` is the list of {"text", "metadata"} dicts returned by
    load_directory(). Returns the same shape, one entry per chunk, with the
    original metadata carried over onto every chunk plus a `chunk_index`.
    """
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks: List[Dict[str, Any]] = []
    for doc in documents:
        pieces = splitter.split_text(doc["text"])
        for i, piece in enumerate(pieces):
            metadata = dict(doc["metadata"])
            metadata["chunk_index"] = i
            chunks.append({"text": piece, "metadata": metadata})
    return chunks


if __name__ == "__main__":
    # Quick manual smoke test:
    #   python -m src.parsing.loader data/career_notes
    import sys

    target = sys.argv[1] if len(sys.argv) > 1 else "data/career_notes"
    docs = load_directory(target)
    print(f"Loaded {len(docs)} document(s) from '{target}'")
    for d in docs:
        print(f"  - {d['metadata']['filename']}: {len(d['text'])} chars")
    chunked = chunk_documents(docs)
    print(f"Chunked into {len(chunked)} piece(s)")
