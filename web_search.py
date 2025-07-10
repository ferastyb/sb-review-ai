import re
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

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
    match = re.search(r"Applicability\s*[:\-]?\s*(.*?)\s+(Compliance|Affected|Subject|Requirement|Summary)", text, re.IGNORECASE | re.DOTALL)
    if match:
        return match.group(1).strip()
    # fallback for generic "applicability"
    match = re.search(r"Applicability\s*[:\-]?\s*(.*)", text, re.IGNORECASE)
    return match.group(1).strip() if match else "N/A"

def generate_sb_query_variants(sb_id, ata, system):
    # Extract numeric portion like 420045 from "B787-81205-SB420045-00"
    match = re.search(r"SB(\d{6})", sb_id)
    sb_number = match.group(1) if match else sb_id[-6:]

    queries = [
        f"site:federalregister.gov AD for Boeing SB {sb_number}",
        f"site:federalregister.gov Airworthiness Directive {sb_number}",
        f"site:federalregister.gov AD {sb_id}",
        f"site:federalregister.gov Boeing {sb_id} {system}",
        f"site:federalregister.gov Boeing AD {ata} {system}"
    ]
    return queries

def bing_search(query, num_results=5):
    try:
        url = f"https://www.bing.com/search?q={query.replace(' ', '+')}"
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code != 200:
            return []

        soup = BeautifulSoup(resp.text, "html.parser")
        links = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "federalregister.gov/documents/" in href and href not in links:
                links.append(href)
            if len(links) >= num_results:
                break
        return links
    except Exception:
        return []

def find_relevant_ad(sb_id, ata, system):
    try:
        queries = generate_sb_query_variants(sb_id, ata, system)

        for query in queries:
            results = bing_search(query)
            for url in results:
                try:
                    resp = requests.get(url, timeout=10, headers=HEADERS)
                    if resp.status_code == 200:
                        page_text = BeautifulSoup(resp.text, "html.parser").get_text()
                        if sb_id in page_text or sb_id[-6:] in page_text or ata in page_text or system.lower() in page_text.lower():
                            return (
                                extract_ad_number(page_text),
                                extract_effective_date(page_text),
                                url,
                                extract_applicability(page_text),
                                extract_amendment_number(page_text)
                            )
                except Exception:
                    continue
    except Exception:
        pass

    return "Not found", "N/A", "N/A", "N/A", "N/A"
