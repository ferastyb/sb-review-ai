# web_search.py
import re
import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0"}

def extract_ad_number(text):
    match = re.search(r"AD\s+(\d{4}-\d{2}-\d{?2})", text)
    return match.group(1) if match else "Not found"

def extract_effective_date(text):
    match = re.search(r"Effective\s+Date[:\s\n]*(\w+\s+\d{1,2},\s+\d{4})", text, re.IGNORECASE)
    return match.group(1) if match else "N/A"

def extract_amendment(text):
    match = re.search(r"Amendment\s+(\d+-\d+)", text)
    return match.group(1) if match else "N/A"

def extract_applicability(text):
    match = re.search(r"Applicability[\s\S]{0,200}?\n([\s\S]{0,300}?)\n", text, re.IGNORECASE)
    return match.group(1).strip() if match else "N/A"

def search_federal_register(query, num_results=5):
    try:
        search_url = f"https://www.bing.com/search?q={query.replace(' ', '+')}"
        response = requests.get(search_url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        links = []
        for a in soup.find_all("a", href=True):
            href = a['href']
            if "federalregister.gov/documents" in href and href not in links:
                links.append(href)
            if len(links) >= num_results:
                break
        return links
    except Exception:
        return []

def normalize_sb_number(sb_id):
    match = re.search(r"SB(\d{6})", sb_id)
    if match:
        return match.group(1)
    match = re.search(r"\b(\d{6})\b", sb_id)
    return match.group(1) if match else sb_id

def find_relevant_ad(sb_id, ata, system):
    normalized_sb = normalize_sb_number(sb_id)

    search_queries = [
        f"site:federalregister.gov AD for Boeing SB {normalized_sb}",
        f"site:federalregister.gov Airworthiness Directive Boeing {normalized_sb}",
        f"site:federalregister.gov Boeing SB{normalized_sb} AD",
        f"site:federalregister.gov Boeing {system} ATA {ata} AD",
    ]

    for query in search_queries:
        urls = search_federal_register(query)
        for url in urls:
            try:
                res = requests.get(url, headers=HEADERS, timeout=10)
                if res.status_code == 200:
                    page_text = BeautifulSoup(res.text, "html.parser").get_text()
                    if normalized_sb in page_text or system.lower() in page_text.lower() or ata in page_text:
                        return (
                            extract_ad_number(page_text),
                            extract_effective_date(page_text),
                            url,
                            extract_applicability(page_text),
                            extract_amendment(page_text)
                        )
            except Exception:
                continue

    return "Not found", "N/A", "N/A", "N/A", "N/A"
