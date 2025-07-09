import requests
from bs4 import BeautifulSoup
import re

def find_relevant_ad(sb_id, ata, system):
    query = f"Boeing SB {sb_id} site:federalregister.gov"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        # Search for related AD on Google (via DuckDuckGo proxy)
        search_url = f"https://html.duckduckgo.com/html/?q={query}"
        res = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")

        links = soup.find_all("a", href=True)
        ad_link = None
        for link in links:
            href = link["href"]
            if "federalregister.gov/documents" in href and "/airworthiness-directives" in href:
                ad_link = href
                break

        if not ad_link:
            # Retry with ATA/system if SB ID search failed
            alt_query = f"Boeing ATA {ata} {system} Airworthiness Directive site:federalregister.gov"
            search_url = f"https://html.duckduckgo.com/html/?q={alt_query}"
            res = requests.get(search_url, headers=headers, timeout=10)
            soup = BeautifulSoup(res.text, "html.parser")
            links = soup.find_all("a", href=True)
            for link in links:
                href = link["href"]
                if "federalregister.gov/documents" in href and "/airworthiness-directives" in href:
                    ad_link = href
                    break

        if not ad_link:
            return {"ad_number": "Not found", "effective_date": "N/A"}

        # Open the AD page and extract title + effective date
        ad_res = requests.get(ad_link, headers=headers, timeout=10)
        ad_soup = BeautifulSoup(ad_res.text, "html.parser")

        title_tag = ad_soup.find("h1")
        ad_number = title_tag.text.strip() if title_tag else "Unknown AD"

        date_text = ad_res.text
        match = re.search(r"Effective\s+date\s*:?\s*(\w+ \d{1,2}, \d{4})", date_text, re.IGNORECASE)
        effective_date = match.group(1) if match else "N/A"

        return {
            "ad_number": ad_number,
            "effective_date": effective_date
        }

    except Exception as e:
        print(f"🌐 AD lookup failed: {e}")
        return {"ad_number": "Lookup failed", "effective_date": "N/A"}
