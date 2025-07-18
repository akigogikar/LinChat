from typing import List, Dict
import re
import zlib
import base64


def parse_pdf(path: str) -> List[Dict]:
    """Extract text from a basic PDF containing ASCII85 and Flate streams."""
    with open(path, "rb") as f:
        data = f.read()

    texts = []
    for match in re.finditer(rb'stream\n(.*?)endstream', data, flags=re.S):
        stream = match.group(1).strip()
        try:
            decoded = base64.a85decode(stream, adobe=True)
            decompressed = zlib.decompress(decoded)
        except Exception:
            continue
        decoded_text = decompressed.decode("utf-8", errors="ignore")
        parts = re.findall(r"\(([^)]*)\)", decoded_text)
        if parts:
            texts.append(" ".join(parts))
    if not texts:
        return []
    combined = "\n".join(texts)
    return [{"page": 1, "text": combined}]
