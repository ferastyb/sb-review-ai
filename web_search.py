import re
import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

def normalize_sb_id(sb_id):
    # Extract the numeric SB sequence: e.g., from B787-81205-SB420045-00 → 420045
    match = re.search(r"SB(\d{6})", sb_id)
    return match.group(1) if match else sb_id

def extract_ad_number(text):
    match = re.search(r"AD\s+(\d{4}-\d{2}-\d{0,2})", text)
    return match.group(1) if match else "Not found"

def extract_effective_date(text):
    # Search for phrases like: "This AD is effective April 7, 2020."
    patterns = [
        r"This AD is effective\s+([A-Za-z]+\s+\d{1,2},\s+\d{4})",
        r"Effective Date:?[\s\n]*([A-Za-z]+\s+\d{1,2},\s+\d{4})",
        r"effective as of\s+([A-Za-z]+\s+\d{1,2},\s+\d{4})"
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    return "N/A"

def extract_applicability(text):
    # Extract "Applicability" section or sentence
    match = re.search(r"Applicability[\s\S]{0,50}:\s*([\s\S]*?)\n\n", text, re.IGNORECASE)
    return match.group(1).strip() if match else "N/A"

def extract_amendment_number(text):
    match = re.search(r"Amendment\s+39-(\d+)", text)
    return f"39-{match.group(1)}" if match else "N/A"

def bing_search(query, num_results=5):
    try:
        search_url = f"https://www.bing.com/search?q={query.replace(' ', '+')}"
        response = requests.get(search_url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        links = []
        for a in soup.find_all("a", href=True):
            href = a['href']
            if "federalregister.gov/documents/" in href and href not in links:
                links.append(href)
            if len(links) >= num_results:
                break
        return links
    except Exception:
        return []

def find_relevant_ad(sb_id, ata, system):
    sb_number = normalize_sb_id(sb_id)
    query = f"site:federalregister.gov AD for Boeing SB {sb_number}"

    results = bing_search(query)
    for url in results:
        try:
            resp = requests.get(url, headers=HEADERS, timeout=10)
            if resp.status_code != 200:
                continue

            soup = BeautifulSoup(resp.text, "html.parser")
            text = soup.get_text()

            # Check if the SB number or system is mentioned in the page
            if sb_number in text or system.lower() in text.lower():
                ad_number = extract_ad_number(text)
                effective_date = extract_effective_date(text)
                applicability = extract_applicability(text)
                amendment = extract_amendment_number(text)
                return ad_number, effective_date, url, applicability, amendment
        except Exception:
            continue

    return "Not found", "N/A", "N/A", "N/A", "N/A"
