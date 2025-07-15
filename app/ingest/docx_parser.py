from typing import List, Dict
from docx import Document


def parse_docx(path: str) -> List[Dict]:
    """Parse DOCX and return text chunks."""
    document = Document(path)
    chunks = []
    for i, para in enumerate(document.paragraphs, start=1):
        text = para.text.strip()
        if text:
            chunks.append({"page": i, "text": text})
    return chunks
