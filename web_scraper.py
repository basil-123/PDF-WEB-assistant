"""
DocuMind AI — Web Scraper
"""
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from datetime import datetime
from langchain_core.documents import Document


def scrape_url(url: str) -> list[Document]:
    """Scrapes a webpage and returns LangChain Documents."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
    except requests.RequestException as e:
        raise ValueError(f"Failed to fetch URL: {e}")

    soup = BeautifulSoup(response.text, "html.parser")

    # Remove noise
    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form", "iframe"]):
        tag.decompose()

    text = soup.get_text(separator="\n", strip=True)
    text = re.sub(r'\n{3,}', '\n\n', text)

    if len(text.strip()) < 50:
        raise ValueError("Page content too short or empty after scraping.")

    title = soup.title.string.strip() if soup.title and soup.title.string else urlparse(url).netloc

    doc = Document(
        page_content=text,
        metadata={
            "source_type": "web",
            "source_url": url,
            "source_file": title,
            "scraped_at": datetime.now().isoformat()
        }
    )
    return [doc]
