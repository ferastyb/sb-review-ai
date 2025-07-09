import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; ServiceBulletinBot/1.0; +https://example.com/bot)"
}

def find_relevant_ad(ata_and_system):
    """
    Search the web for a relevant AD based on ATA chapter and system/subject.
    Returns a title and link to the most relevant AD found.
    """
    query = f"site:drs.faa.gov OR site:rgl.faa.gov Airworthiness Directive {ata_and_system}"
    search_url = f"https://www.google.com/search?q={requests.utils.quote(query)}"

    try:
        response = requests.get(search_url, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            return "No AD found (search failed)"

        soup = BeautifulSoup(response.text, "html.parser")

        for link in soup.select("a"):
            href = link.get("href")
            title = link.get_text(strip=True)

            if "ad" in title.lower() and ("faa.gov" in href or "drs.faa.gov" in href):
                clean_url = extract_clean_url(href)
                return f"{title} - {clean_url}"

        return "No relevant AD found"
    except Exception as e:
        return f"Error during AD search: {str(e)}"

def extract_clean_url(href):
    """
    Extract a clean URL from a Google search result href.
    """
    try:
        if href.startswith("/url?q="):
            href = href.split("/url?q=")[1].split("&")[0]
        return href
    except Exception:
        return href
