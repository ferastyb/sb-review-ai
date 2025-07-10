# web_search.py

import re
import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

def extract_ad_number(text):
    match = re.search(r"AD\s+(\d{4}-\d{2}-\d{0,2})", text)
    return match.group(1) if match else "Not found"

def extract_effective_date(text):
    match = re.search(r"Effective\s+Date:?[\s\n]*(\w+\s+\d{1,2},\s+\d{4})", text, re.IGNORECASE)
    return match.group(1) if match else "N/A"

def extract_amendment_number(text):
    match = re.search(r"Amendment\s+(\d+-\d+)", text)
    return match.group(1) if match else "N/A"

def extract_applicability(text):
    match = re.search(r"Applicability[\s\n:]+(.+?)(?=\n[A-Z])", text, re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else "N/A"

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

def normalize_sb_number(sb_id):
    match = re.search(r"SB(\d{6})", sb_id)
    return match.group(1) if match else re.sub(r"\D", "", sb_id)

def find_relevant_ad(sb_id, ata, system):
    sb_number = normalize_sb_number(sb_id)
    queries = [
        f"AD for Boeing SB {sb_number} site:federalregister.gov",
        f"Airworthiness Directive {sb_number} site:federalregister.gov",
        f"Boeing {sb_number} AD site:federalregister.gov",
        f"{sb_number} AD federalregister.gov",
        f"Airworthiness Directive ATA {ata} {system} site:federalregister.gov"
    ]

    for query in queries:
        results = bing_search(query)
        for url in results:
            try:
                response = requests.get(url, timeout=10, headers=HEADERS)
                if response.status_code == 200:
                    text = BeautifulSoup(response.text, "html.parser").get_text()

                    # Match loose SB formats
                    if any(tag in text for tag in [sb_number, f"SB{sb_number}", f"SB {sb_number}"]):
                        ad_number = extract_ad_number(text)
                        ad_date = extract_effective_date(text)
                        amendment = extract_amendment_number(text)
                        applicability = extract_applicability(text)
                        return ad_number, ad_date, url, applicability, amendment
            except Exception:
                continue

    return "Not found", "N/A", "N/A", "N/A", "N/A"
