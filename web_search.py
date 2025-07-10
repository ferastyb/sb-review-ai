import re
import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0"}

def extract_ad_number(text):
    match = re.search(r"AD\s+(\d{4}-\d{2}-\d{2})", text)
    return match.group(1) if match else "Not found"

def extract_effective_date(text):
    # Try several patterns to increase reliability
    patterns = [
        r"Effective\s+Date:?[\s\n]*(\w+\s+\d{1,2},\s+\d{4})",
        r"This\s+AD\s+is\s+effective\s+(\w+\s+\d{1,2},\s+\d{4})",
        r"effective\s+(\w+\s+\d{1,2},\s+\d{4})",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    return "N/A"

def extract_amendment_number(text):
    match = re.search(r"Amendment\s+39-(\d+)", text)
    return f"39-{match.group(1)}" if match else "N/A"

def extract_applicability(text):
    match = re.search(r"Applicability[\s\n:]*([^\n]+)", text, re.IGNORECASE)
    return match.group(1).strip() if match else "N/A"

def find_relevant_ad(sb_id, ata, system):
    try:
        sb_number_match = re.search(r"SB(\d{6})", sb_id)
        sb_number = sb_number_match.group(1) if sb_number_match else sb_id[-6:]
        queries = [
            f"site:federalregister.gov Boeing SB {sb_number}",
            f"site:federalregister.gov AD for Boeing SB {sb_number}",
            f"site:federalregister.gov {system} ATA {ata} AD",
        ]

        for query in queries:
            search_url = f"https://www.bing.com/search?q={query.replace(' ', '+')}"
            resp = requests.get(search_url, headers=HEADERS, timeout=10)
            soup = BeautifulSoup(resp.text, "html.parser")
            links = [a['href'] for a in soup.find_all("a", href=True) if "federalregister.gov" in a['href']]
            for url in links:
                page = requests.get(url, headers=HEADERS, timeout=10)
                page_text = BeautifulSoup(page.text, "html.parser").get_text()
                if sb_number in page_text or sb_id in page_text:
                    ad_number = extract_ad_number(page_text)
                    effective_date = extract_effective_date(page_text)
                    amendment = extract_amendment_number(page_text)
                    applicability = extract_applicability(page_text)
                    return ad_number, effective_date, url, applicability, amendment
    except Exception as e:
        print(f"❌ Error during AD search: {e}")
    return "Not found", "N/A", "", "N/A", "N/A"
