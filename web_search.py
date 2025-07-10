import re
import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

def extract_ad_number(text):
    match = re.search(r"(AD\s+)?(\d{4}-\d{2}-\d{0,2})", text)
    return match.group(2) if match else "Not found"

def extract_effective_date(text):
    match = re.search(r"(Effective Date|Effective):?\s*(\w+\s+\d{1,2},\s+\d{4})", text, re.IGNORECASE)
    return match.group(2) if match else "N/A"

def bing_search(query, num_results=5):
    search_url = f"https://www.bing.com/search?q={query.replace(' ', '+')}"
    try:
        response = requests.get(search_url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        results = []

        for a in soup.find_all("a", href=True):
            href = a["href"]
            if any(domain in href for domain in ["federalregister.gov", "faa.gov"]):
                results.append(href)
            if len(results) >= num_results:
                break

        return results
    except Exception:
        return []

def find_relevant_ad(sb_id, ata, system):
    search_query = f"{sb_id} {system} ATA {ata} site:faa.gov OR site:federalregister.gov"
    results = bing_search(search_query)

    for url in results:
        try:
            res = requests.get(url, headers=HEADERS, timeout=10)
            if res.status_code == 200:
                page_text = BeautifulSoup(res.text, "html.parser").get_text(separator=" ", strip=True)
                if sb_id in page_text or ata in page_text or system.lower() in page_text.lower():
                    ad_number = extract_ad_number(page_text)
                    ad_date = extract_effective_date(page_text)
                    return ad_number, ad_date
        except Exception:
            continue

    return "Not found", "N/A"
