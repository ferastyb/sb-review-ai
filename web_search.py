import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; SB-ReviewBot/1.0)"
}

def find_relevant_ad(sb_id=None, ata=None, system=None):
    """
    Search DuckDuckGo HTML for a relevant Airworthiness Directive (AD),
    using SB ID, ATA chapter, and system/subject. Returns the first good match.
    """
    parts = []
    if sb_id:
        parts.append(f'"{sb_id}"')
    if ata:
        parts.append(f'"ATA {ata}"')
    if system:
        parts.append(f'"{system}"')
    parts.append("site:regulations.gov OR site:drs.faa.gov OR site:federalregister.gov")
    parts.append("Airworthiness Directive")
    query = " ".join(parts)

    try:
        resp = requests.post(
            "https://html.duckduckgo.com/html/",
            data={"q": query},
            headers=HEADERS,
            timeout=10
        )
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for a in soup.find_all("a", class_="result__a", href=True):
            title = a.get_text()
            url = a['href']
            # Look for the AD number we expect
            if "AD" in title and sb_id in title or ata in title:
                return {"title": title.strip(), "url": url}
        return {"title": "No relevant AD found", "url": ""}
    except Exception as e:
        return {"title": "Search failed", "url": "", "error": str(e)}
