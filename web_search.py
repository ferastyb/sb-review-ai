import requests
from bs4 import BeautifulSoup
import re

FEDERAL_REGISTER_SEARCH = "https://www.federalregister.gov/documents/search"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; SBReviewAI/1.0)"
}

def extract_effective_date(text):
    match = re.search(r"Effective Date[:\s]+([A-Za-z]+ \d{1,2}, \d{4})", text)
    if match:
        return match.group(1)
    return None

def find_relevant_ad(sb_id, ata, system):
    try:
        # Build combined query
        query = f"{sb_id} OR {sb_id.split('-')[-1]} OR ATA {ata} {system}"

        params = {
            "conditions[term]": query,
            "conditions[agency_ids][]": "27",  # FAA
            "order": "newest",
            "per_page": 5
        }

        response = requests.get(FEDERAL_REGISTER_SEARCH, params=params, headers=HEADERS, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        results = soup.select(".document-wrapper")

        for result in results:
            title_elem = result.select_one(".document-title")
            url_elem = result.select_one(".document-title a")

            if not title_elem or not url_elem:
                continue

            title = title_elem.get_text(strip=True)
            url = "https://www.federalregister.gov" + url_elem.get("href")

            # Basic match check
            if any(part in title for part in [sb_id, sb_id.split('-')[-1], ata, system]):
                ad_number_match = re.search(r"\b(AD\s*\d{4}-\d{2}-\d{2})\b", title)
                ad_number = ad_number_match.group(1) if ad_number_match else "Unknown"

                # Load detail page to extract effective date
                detail_page = requests.get(url, headers=HEADERS, timeout=10)
                detail_soup = BeautifulSoup(detail_page.text, "html.parser")
                full_text = detail_soup.get_text()
                effective_date = extract_effective_date(full_text) or "N/A"

                return {
                    "title": title,
                    "url": url,
                    "ad_number": ad_number,
                    "effective_date": effective_date
                }

    except Exception as e:
        print(f"⚠️ AD search error: {e}")

    return {
        "title": "Not found",
        "url": "",
        "ad_number": "Not found",
        "effective_date": "N/A"
    }
