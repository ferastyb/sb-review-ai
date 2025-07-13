import re
import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}


def extract_ad_number(text):
    match = re.search(r"AD\s+(\d{4}-\d{2}-\d{2})", text)
    return match.group(1) if match else "Not found"


def extract_effective_date(text):
    patterns = [
        r"Effective Date[:\s]+([A-Za-z]+\s+\d{1,2},\s+\d{4})",
        r"This AD is effective\s+([A-Za-z]+\s+\d{1,2},\s+\d{4})"
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    return "N/A"


def extract_amendment_number(text):
    match = re.search(r"Amendment\s+39-\d+", text)
    return match.group(0) if match else "N/A"


def extract_applicability(text):
    match = re.search(r"Applicability[\s\S]{0,1000}?(?:\n\n|\r\n\r\n|\Z)", text, re.IGNORECASE)
    return match.group(0).strip() if match else "N/A"


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


def find_relevant_ad(sb_id, ata, system):
    sb_number = re.search(r"(\d{6})", sb_id)
    if not sb_number:
        return "Not found", "N/A", "N/A", "N/A", "N/A"

    sb_seq = sb_number.group(1)
    query = f"site:federalregister.gov Airworthiness Directive SB {sb_seq} ATA {ata} {system}"

    results = bing_search(query)

    for url in results:
        try:
            response = requests.get(url, timeout=10, headers=HEADERS)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                page_text = soup.get_text()

                if sb_seq in page_text or ata in page_text or system.lower() in page_text.lower():
                    ad_number = extract_ad_number(page_text)
                    effective_date = extract_effective_date(page_text)
                    amendment = extract_amendment_number(page_text)
                    applicability = extract_applicability(page_text)
                    return ad_number, effective_date, url, applicability, amendment
        except Exception:
            continue

    return "Not found", "N/A", "N/A", "N/A", "N/A"
