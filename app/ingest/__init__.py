import os
from .pdf_parser import parse_pdf
from .docx_parser import parse_docx
from .excel_parser import parse_excel
from .ppt_parser import parse_pptx


def parse_file(path: str):
    ext = os.path.splitext(path)[1].lower()
    if ext == '.pdf':
        return parse_pdf(path)
    elif ext in {'.docx', '.doc'}:
        return parse_docx(path)
    elif ext in {'.xlsx', '.xls'}:
        return parse_excel(path)
    elif ext in {'.pptx', '.ppt'}:
        return parse_pptx(path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")
