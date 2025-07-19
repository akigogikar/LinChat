import os
import httpx
from typing import Tuple, List, Dict

SERVICE_URL = os.getenv("ANALYSIS_SERVICE_URL", "http://localhost:8001/analysis")


async def analyze_file(path: str) -> Tuple[List[Dict], str | None]:
    """Upload a file to the Rust analysis service and return stats and chart."""
    async with httpx.AsyncClient() as client:
        with open(path, "rb") as f:
            resp = await client.post(SERVICE_URL, files={"file": f})
    resp.raise_for_status()
    data = resp.json()
    chart = resp.headers.get("Chart")
    return data, chart
