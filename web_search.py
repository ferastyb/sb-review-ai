import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; SB-ReviewBot/1.0)"
}

def find_relevant_ad(sb_id=None, ata=None, system=None):
    """
    Search for relevant Airworthiness Directive (AD) based on SB ID, ATA, and system.
    Returns a dictionary with 'title' and 'url' of the first matching AD found.
    """
    # Build query from available info
    query_parts = []
    if sb_id:
        query_parts.append(f'"Service Bulletin {sb_id}"')
    if ata:
        query_parts.append(f'"ATA {ata}"')
    if system:
        query_parts.append(f'"{system}"')

    query = " ".join(query_parts) + " site:drs.faa.gov OR site:rgl.faa.gov AD"

    search_url = "https://html.duckduckgo.com/html/"
    params = {"q": query}

    try:
        response = requests.post(search_url, data=params, headers=HEADERS, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        results = soup.find_all("a", class_="result__a", href=True)

        for result in results:
            title = result.get_text()
            href = result["href"]
            if "faa.gov" in href.lower() and "ad" in title.lower():
                return {"title": title, "url": href}

        return {"title": "No relevant AD found", "url": ""}
    except Exception as e:
        return {"title": "Search failed", "url": "", "error": str(e)}
