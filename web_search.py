import re
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

def extract_ad_details(text):
    ad_number = "Not found"
    effective_date = "N/A"
    applicability = "N/A"
    amendment_number = "N/A"

    ad_match = re.search(r"AD\s+(\d{4}-\d{2}-\d{2})", text)
    if ad_match:
        ad_number = ad_match.group(1)

    date_match = re.search(r"Effective\s+Date:?[\s\n]*(\w+\s+\d{1,2},\s+\d{4})", text, re.IGNORECASE)
    if date_match:
        effective_date = date_match.group(1)

    applicability_match = re.search(r"Applicability[\s\S]{0,100}This AD applies to[\s\S]*?\.", text, re.IGNORECASE)
    if applicability_match:
        applicability = applicability_match.group(0).strip()

    amendment_match = re.search(r"Amendment\s+39-\d+", text)
    if amendment_match:
        amendment_number = amendment_match.group(0)

    return ad_number, effective_date, applicability, amendment_number

def bing_search(query, num_results=5):
    search_url = f"https://www.bing.com/search?q={query.replace(' ', '+')}"
    try:
        response = requests.get(search_url, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            return []

        soup = BeautifulSoup(response.text, "html.parser")
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
        parsed_sb = re.search(r"(\d{2})(\d{4})", sb_id)
        sb_number_simple = parsed_sb.group(1) + parsed_sb.group(2) if parsed_sb else sb_id

        queries = [
            f"site:federalregister.gov Airworthiness Directive Boeing SB {sb_number_simple}",
            f"site:federalregister.gov Boeing {sb_number_simple} AD",
            f"site:federalregister.gov AD for Boeing ATA {ata} {system}"
        ]

        for query in queries:
            links = bing_search(query)
            for url in links:
                try:
                    res = requests.get(url, headers=HEADERS, timeout=10)
                    if res.status_code != 200:
                        continue

                    page_text = BeautifulSoup(res.text, "html.parser").get_text(separator="\n")

                    if sb_number_simple in page_text or sb_id in page_text or system.lower() in page_text.lower():
                        ad_number, eff_date, applicability, amendment = extract_ad_details(page_text)
                        return ad_number, eff_date, url, applicability, amendment
                except Exception:
                    continue
    except Exception:
        pass

    return "Not found", "N/A", "N/A", "N/A", "N/A"
