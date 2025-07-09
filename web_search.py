import requests
from bs4 import BeautifulSoup
import re


def search_web(query):
    """Search the web using DuckDuckGo HTML results."""
    url = "https://html.duckduckgo.com/html/"
    params = {"q": query}
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        res = requests.post(url, data=params, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")
        results = []
        for a in soup.find_all("a", class_="result__a", href=True):
            results.append({"title": a.text, "link": a['href']})
        return results
    except Exception as e:
        print("Search failed:", e)
        return []


def extract_ad_number(text):
    match = re.search(r"AD\s*(\d{4}-\d{2}-\d{2})", text)
    if match:
        return match.group(1)
    return None


def extract_effective_date(text):
    match = re.search(r"effective\s+date\s+is\s+(\w+\s+\d{1,2},\s+\d{4})", text, re.IGNORECASE)
    if match:
        return match.group(1)

    match = re.search(r"Effective\s*Date[:\-]?\s*(\w+\s+\d{1,2},\s+\d{4})", text, re.IGNORECASE)
    if match:
        return match.group(1)

    return None


def find_relevant_ad(sb_id, ata, system):
    query = f"{sb_id} site:federalregister.gov"
    search_results = search_web(query)

    for result in search_results:
        url = result["link"]
        try:
            page = requests.get(url, timeout=10)
            soup = BeautifulSoup(page.text, "html.parser")
            text = soup.get_text()

            if sb_id.lower() in text.lower():
                ad_number = extract_ad_number(text)
                effective_date = extract_effective_date(text)
                return {
                    "ad_number": ad_number or "Not found",
                    "effective_date": effective_date or "N/A"
                }
        except Exception as e:
            print(f"Error loading {url}: {e}")
            continue

    # fallback to ATA/system search if SB ID match fails
    fallback_query = f"{ata} {system} airworthiness directive site:federalregister.gov"
    fallback_results = search_web(fallback_query)

    for result in fallback_results:
        url = result["link"]
        try:
            page = requests.get(url, timeout=10)
            soup = BeautifulSoup(page.text, "html.parser")
            text = soup.get_text()

            if any(term.lower() in text.lower() for term in [ata, system]):
                ad_number = extract_ad_number(text)
                effective_date = extract_effective_date(text)
                return {
                    "ad_number": ad_number or "Not found",
                    "effective_date": effective_date or "N/A"
                }
        except Exception as e:
            print(f"Fallback error loading {url}: {e}")
            continue

    return {
        "ad_number": "Not found",
        "effective_date": "N/A"
    }
