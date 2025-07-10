import re
import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0"}

def extract_ad_number(text):
    match = re.search(r"AD\s+(\d{4}-\d{2}-\d{2})", text)
    return match.group(1) if match else "Not found"

def extract_effective_date(text):
    match = re.search(r"Effective\s+Date:?[\s\n]*(\w+\s+\d{1,2},\s+\d{4})", text, re.IGNORECASE)
    return match.group(1) if match else "N/A"

def bing_search(query, num_results=5):
    try:
        search_url = f"https://www.bing.com/search?q={query.replace(' ', '+')}"
        response = requests.get(search_url, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            return []

        soup = BeautifulSoup(response.text, "html.parser")
        links = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "federalregister.gov" in href and href not in links:
                links.append(href)
            if len(links) >= num_results:
                break
        return links
    except Exception:
        return []

def extract_sb_seq(sb_id):
    # Extract the SB sequence number like 420045 from a full SB ID
    match = re.search(r"SB(\d{6})", sb_id)
    return match.group(1) if match else sb_id

def find_relevant_ad(sb_id, ata, system):
    queries = []

    sb_seq = extract_sb_seq(sb_id)
    if sb_seq:
        queries.append(f"AD for Boeing SB {sb_seq}")
        queries.append(f"Boeing SB{sb_seq} airworthiness directive site:federalregister.gov")
        queries.append(f"airworthiness directive Boeing {system} {sb_seq}")
        queries.append(f"{sb_id} airworthiness directive site:federalregister.gov")

    for query in queries:
        results = bing_search(query)
        for url in results:
            try:
                page = requests.get(url, headers=HEADERS, timeout=10)
                if page.status_code == 200:
                    page_text = BeautifulSoup(page.text, "html.parser").get_text()
                    if sb_seq in page_text or sb_id in page_text or ata in page_text or system.lower() in page_text.lower():
                        ad_number = extract_ad_number(page_text)
                        ad_date = extract_effective_date(page_text)
                        return ad_number, ad_date
            except Exception:
                continue

    return "Not found", "N/A"
