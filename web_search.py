import re
import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

def extract_ad_number(text):
    match = re.search(r"AD\s+(\d{4}-\d{2}-\d{2})", text)
    return match.group(1) if match else "Not found"

def extract_effective_date(text):
    match = re.search(r"Effective\s+Date:?[\s\n]*(\w+\s+\d{1,2},\s+\d{4})", text, re.IGNORECASE)
    return match.group(1) if match else "N/A"

def bing_search(query, num_results=5):
    try:
        search_url = f"https://www.bing.com/search?q={query}".replace(" ", "+")
        response = requests.get(search_url, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            return []

        soup = BeautifulSoup(response.text, "html.parser")
        links = []
        for a in soup.find_all("a", href=True):
            href = a['href']
            if "federalregister.gov" in href and href not in links:
                links.append(href)
            if len(links) >= num_results:
                break
        return links
    except Exception:
        return []

def find_relevant_ad(parsed_sb_number, ata, system):
    try:
        # Example query: AD for Boeing SB 420045 Common Core System ATA 42
        query = f"AD for Boeing SB {parsed_sb_number} {system} ATA {ata} site:federalregister.gov"
        results = bing_search(query)

        for url in results:
            try:
                response = requests.get(url, timeout=10, headers=HEADERS)
                if response.status_code == 200:
                    page_text = BeautifulSoup(response.text, "html.parser").get_text()
                    if parsed_sb_number in page_text or ata in page_text or system.lower() in page_text.lower():
                        ad_number = extract_ad_number(page_text)
                        effective_date = extract_effective_date(page_text)
                        return ad_number, effective_date
            except Exception:
                continue
    except Exception:
        pass

    return "Not found", "N/A"
