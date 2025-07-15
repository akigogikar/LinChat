from typing import List, Dict
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer


def parse_pdf(path: str) -> List[Dict]:
    """Parse PDF and return list of text chunks with page numbers."""
    chunks = []
    for page_number, page_layout in enumerate(extract_pages(path), start=1):
        texts = []
        for element in page_layout:
            if isinstance(element, LTTextContainer):
                texts.append(element.get_text())
        text = "\n".join(texts).strip()
        if text:
            chunks.append({"page": page_number, "text": text})
    return chunks
