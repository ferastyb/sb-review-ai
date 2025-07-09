import requests
from bs4 import BeautifulSoup
import re

def find_relevant_ad(sb_id: str, ata: str, system: str) -> dict:
    """
    Search online for a related Airworthiness Directive (AD) based on the SB ID, ATA, and system.
    Returns a dict with the AD title and link, or a 'not found' message.
    """
    query = f"{sb_id} site:federalregister.gov OR site:faa.gov"
    search_url = f"https://html.duckduckgo.com/html/?q={query}"

    try:
        response = requests.get(search_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        links = soup.select(".result__a")
        for link in links:
            url = link.get("href")
            title = link.text

            # Fetch page content to look for better matches
            page = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            page_text = page.text

            # Search for AD number pattern or SB match in the content
            if re.search(rf"{sb_id}|{ata}|{system}", page_text, re.IGNORECASE):
                ad_match = re.search(r"AD\s+\d{4}-\d{2}-\d{2}", page_text)
                ad_number = ad_match.group(0) if ad_match else "Unknown AD"

                return {
                    "title": ad_number + " - " + title.strip(),
                    "link": url
                }

        return {"title": "No relevant AD found", "link": ""}
    except Exception as e:
        return {"title": f"Search error: {e}", "link": ""}
