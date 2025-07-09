import re
import requests
from bs4 import BeautifulSoup

# Fallback to manual search logic, since googlesearch or duckduckgo_search modules may not be available

def extract_ad_number(text):
    match = re.search(r"AD\s+(\d{4}-\d{2}-\d{2})", text)
    return match.group(1) if match else "Not found"

def extract_effective_date(text):
    match = re.search(r"Effective\s+Date:?\s*(\w+\s+\d{1,2},\s+\d{4})", text, re.IGNORECASE)
    return match.group(1) if match else "N/A"

def find_relevant_ad(sb_id, ata, system):
    # Hardcoded list of URLs for fallback
    candidate_urls = [
        "https://www.federalregister.gov/documents/2020/03/23/2020-06092/airworthiness-directives-the-boeing-company-airplanes"
    ]
    
    for url in candidate_urls:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                page_text = BeautifulSoup(response.text, "html.parser").get_text()
                if sb_id in page_text or ata in page_text or system.lower() in page_text.lower():
                    ad_number = extract_ad_number(page_text)
                    effective_date = extract_effective_date(page_text)
                    return ad_number, effective_date
        except Exception:
            continue

    return "Not found", "N/A"
