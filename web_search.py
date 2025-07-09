import requests
from bs4 import BeautifulSoup
import re

# Manual override for known matches
KNOWN_SB_AD_MAP = {
    "420045": {
        "title": "AD 2020-06-14 - Loss of Stale Data Monitoring in CCS",
        "link": "https://www.federalregister.gov/documents/2020/03/23/2020-06092/airworthiness-directives-the-boeing-company-airplanes"
    }
}

def find_relevant_ad(sb_id, ata=None, system=None):
    # Check manual mapping first
    for key in KNOWN_SB_AD_MAP:
        if key in sb_id:
            return KNOWN_SB_AD_MAP[key]

    query_parts = [sb_id]
    if ata:
        query_parts.append(f"ATA {ata}")
    if system:
        query_parts.append(system)

    query = " ".join(query_parts) + " site:federalregister.gov OR site:faa.gov"
    print("🔍 Searching:", query)

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    params = {
        "q": query
    }

    try:
        res = requests.get("https://html.duckduckgo.com/html/", headers=headers, params=params, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        results = soup.select(".result__a")[:10]

        for link_tag in results:
            href = link_tag.get("href")
            if href and any(domain in href for domain in ["faa.gov", "federalregister.gov"]):
                page = requests.get(href, headers=headers, timeout=10)
                if "Airworthiness Directive" in page.text or re.search(r"AD\s?\d{4}-\d{2}-\d{2}", page.text):
                    title = link_tag.text.strip()
                    return {
                        "title": title,
                        "link": href
                    }

    except Exception as e:
        print(f"❌ Web search failed: {e}")

    return {
        "title": "No relevant AD found",
        "link": ""
    }
