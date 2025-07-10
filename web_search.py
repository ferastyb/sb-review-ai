# web_search.py
import re
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}


def extract_ad_number(text):
    match = re.search(r"Airworthiness Directive\s+(20\d{2}-\d{2}-\d{2})", text)
    return match.group(1) if match else "Not found"


def extract_effective_date(text):
    match = re.search(r"Effective\s+Date:?[\s\n]*(\w+\s+\d{1,2},\s+\d{4})", text, re.IGNORECASE)
    return match.group(1) if match else "N/A"


def extract_applicability(text):
    match = re.search(r"Applicability(?:\.|:)?\s*(.+?)(?:\n\n|\n\s*\n|Amendment)", text, re.IGNORECASE | re.DOTALL)
    return match.group(1).strip() if match else "N/A"


def extract_amendment(text):
    match = re.search(r"Amendment\s+39-\d+", text)
    return match.group(0) if match else "N/A"


def extract_sb_reference(sb_id):
    match = re.search(r"SB(\d{6})", sb_id)
    return match.group(1) if match else None


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
    sb_ref = extract_sb_reference(sb_id)
    if not sb_ref:
        return "Not found", "N/A", "N/A", "N/A", "N/A"

    sb_variants = [
        sb_id,
        sb_ref,
        f"SB{sb_ref}",
        f"Boeing SB {sb_ref}",
        f"{ata}{sb_ref[-2:]}" if len(sb_ref) == 6 else ""
    ]

    queries = [f"site:federalregister.gov Airworthiness Directive {variant}" for variant in sb_variants]

    for query in queries:
        urls = bing_search(query)
        for url in urls:
            try:
                response = requests.get(url, headers=HEADERS, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, "html.parser")
                    text = soup.get_text(separator="\n")

                    if any(ref in text for ref in sb_variants):
                        ad_number = extract_ad_number(text)
                        effective_date = extract_effective_date(text)
                        applicability = extract_applicability(text)
                        amendment = extract_amendment(text)
                        return ad_number, effective_date, url, applicability, amendment
            except Exception:
                continue

    return "Not found", "N/A", "N/A", "N/A", "N/A"
