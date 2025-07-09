import requests
from bs4 import BeautifulSoup
import re

FEDERAL_REGISTER_SEARCH = "https://www.federalregister.gov/documents/search"
FEDERAL_REGISTER_BASE = "https://www.federalregister.gov"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def find_relevant_ad(sb_id, ata, system):
    try:
        query = f"{sb_id} OR ATA {ata} {system}"
        params = {
            "conditions[term]": query,
            "conditions[type][]": "PRORULE",
            "per_page": 5,
            "order": "newest"
        }

        response = requests.get(FEDERAL_REGISTER_SEARCH, headers=HEADERS, params=params)
        soup = BeautifulSoup(response.text, "html.parser")
        
        links = soup.select(".document-result a.document-title")
        for link in links:
            ad_title = link.get_text(strip=True)
            ad_url = FEDERAL_REGISTER_BASE + link.get("href")

            ad_page = requests.get(ad_url, headers=HEADERS)
            ad_soup = BeautifulSoup(ad_page.text, "html.parser")
            ad_text = ad_soup.get_text()

            if sb_id.lower() in ad_text.lower() or ata in ad_text or system.lower() in ad_text.lower():
                # Try to extract AD number and effective date
                ad_number_match = re.search(r"AD\s+(\d{4}-\d{2}-\d{2})", ad_text)
                effective_date_match = re.search(r"effective\s+(?:on\s+)?([A-Z][a-z]+\s+\d{1,2},\s+\d{4})", ad_text)

                return {
                    "title": ad_number_match.group(1) if ad_number_match else ad_title,
                    "url": ad_url,
                    "effective_date": effective_date_match.group(1) if effective_date_match else "N/A"
                }

        return {"title": "Not found", "url": "", "effective_date": "N/A"}

    except Exception as e:
        print(f"❌ AD search failed: {e}")
        return {"title": "Not found", "url": "", "effective_date": "N/A"}
