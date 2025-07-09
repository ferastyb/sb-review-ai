import requests
from bs4 import BeautifulSoup
import re

def find_relevant_ad(sb_id, ata, system):
    query = f"FAA AD {sb_id} {system} ATA {ata} site:federalregister.gov"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        response = requests.get(f"https://www.google.com/search?q={query}", headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        
        for a in soup.select("a"):
            href = a.get("href")
            if href and "federalregister.gov/documents" in href:
                ad_page = requests.get(href, headers=headers)
                ad_soup = BeautifulSoup(ad_page.text, "html.parser")
                title = ad_soup.find("title").text if ad_soup.find("title") else "AD Document"
                
                # Find effective date
                effective_match = re.search(r"Effective (\w+ \d{1,2}, \d{4})", ad_soup.text)
                effective_date = effective_match.group(1) if effective_match else "N/A"
                return {"title": title, "url": href, "effective_date": effective_date}

    except Exception as e:
        print(f"Web search failed: {e}")

    return {"title": "Not found", "url": "", "effective_date": "N/A"}
