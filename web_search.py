import requests
from bs4 import BeautifulSoup
import re

def find_relevant_ad(sb_id, ata, system):
    query = f"{sb_id} OR ATA {ata} {system} site:federalregister.gov"
    search_url = f"https://www.google.com/search?q={requests.utils.quote(query)}"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(search_url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        links = [a["href"] for a in soup.select("a") if "federalregister.gov/documents" in a.get("href", "")]

        for link in links:
            ad_page = requests.get(link, headers=headers)
            ad_soup = BeautifulSoup(ad_page.text, "html.parser")

            ad_number_match = ad_soup.find("h1")
            effective_date_match = ad_soup.find("strong", string=re.compile("Effective date", re.I))

            ad_number = ad_number_match.get_text(strip=True) if ad_number_match else "Unknown"
            effective_date = effective_date_match.find_next().get_text(strip=True) if effective_date_match else "Unknown"

            return {
                "ad_number": ad_number,
                "effective_date": effective_date
            }
    except Exception as e:
        print(f"Error fetching AD: {e}")

    return {"ad_number": "Not found", "effective_date": "N/A"}
