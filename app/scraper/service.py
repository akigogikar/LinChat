from typing import List, Optional

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

from .. import vector_db


async def _fetch_html(url: str) -> str:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url)
        html = await page.content()
        await browser.close()
        return html


def _extract_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    # Remove script and style elements
    for elem in soup(["script", "style"]):
        elem.decompose()
    texts = []
    for table in soup.find_all("table"):
        texts.append(table.get_text(separator=" ", strip=True))
        table.decompose()
    texts.append(soup.get_text(separator=" ", strip=True))
    return "\n".join(t.strip() for t in texts if t.strip())


async def scrape_url(url: str, workspace_id: int | None = None) -> Optional[str]:
    """Fetch the given URL and store its contents in the vector DB."""
    try:
        html = await _fetch_html(url)
    except Exception:
        return None
    text = _extract_text(html)
    if not text:
        return None
    # Store in vector DB with url metadata
    vector_db.add_web_embeddings(url, text, workspace_id=workspace_id)
    return text


async def scrape_search(
    query: str, max_results: int = 1, workspace_id: int | None = None
) -> List[str]:
    """Search DuckDuckGo and scrape the top results."""
    import httpx

    params = {"q": query}
    resp = httpx.get("https://duckduckgo.com/html/", params=params)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    links = [a["href"] for a in soup.select("a.result__a") if a.get("href")]
    scraped = []
    for url in links[:max_results]:
        content = await scrape_url(url, workspace_id=workspace_id)
        if content:
            scraped.append(url)
    return scraped
