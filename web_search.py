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

def extract_amendment(text):
    match = re.search(r"Amendment\s+(\d+-\d+)", text)
    return match.group(1) if match else "N/A"

def extract_applicability(text):
    match = re.search(r"Applicability[\s:]*\n*(.+?)(?:\n{2,}|\Z)", text, re.IGNORECASE | re.DOTALL)
    return match.group(1).strip() if match else "N/A"

def google_search_frg(query, max_results=5):
    search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    try:
        resp = requests.get(search_url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        links = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "federalregister.gov" in href and href.startswith("/url?q="):
                link = href.split("/url?q=")[-1].split("&")[0]
                if link not in links:
                    links.append(link)
                if len(links) >= max_results:
                    break
        return links
    except Exception:
        return []

def normalize_sb_number(sb_id):
    match = re.search(r"SB(\d{6})", sb_id)
    return match.group(1) if match else sb_id[-6:]

def find_relevant_ad(sb_id, ata, system):
    sb_number = normalize_sb_number(sb_id)
    search_queries = [
        f"site:federalregister.gov Boeing SB {sb_number}",
        f"site:federalregister.gov AD for Boeing SB {sb_number}",
        f"site:federalregister.gov Airworthiness Directive {sb_number}",
        f"site:federalregister.gov Boeing {sb_id}",
        f"site:federalregister.gov AD {sb_number} ATA {ata}"
    ]

    for query in search_queries:
        urls = google_search_frg(query)
        for url in urls:
            try:
                page = requests.get(url, headers=HEADERS, timeout=10)
                if page.status_code != 200:
                    continue
                text = BeautifulSoup(page.text, "html.parser").get_text()
                if sb_number in text or sb_id in text or ata in text or system.lower() in text.lower():
                    ad_number = extract_ad_number(text)
                    effective_date = extract_effective_date(text)
                    amendment = extract_amendment(text)
                    applicability = extract_applicability(text)
                    return (
                        ad_number,
                        effective_date,
                        url,
                        applicability,
                        amendment
                    )
            except Exception:
                continue
    return ("Not found", "N/A", "N/A", "N/A", "N/A")
