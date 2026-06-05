"""PDF/text resume reader — extracts clean text from PDF or .tex/.txt files."""
import fitz  # PyMuPDF
from pathlib import Path


def extract_resume_text(path: str) -> str:
    """Extract text from PDF, LaTeX, or plain text resume file."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Resume not found: {path}")

    suffix = p.suffix.lower()

    if suffix == ".pdf":
        doc = fitz.open(path)
        pages = [page.get_text() for page in doc]
        doc.close()
        return "\n".join(pages).strip()

    elif suffix in (".tex", ".txt", ".md"):
        return p.read_text(encoding="utf-8").strip()

    else:
        raise ValueError(f"Unsupported file type: {suffix}. Use .pdf, .tex, or .txt")
