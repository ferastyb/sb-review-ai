import requests
from bs4 import BeautifulSoup
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def search_google(query):
    url = f"https://www.google.com/search?q={requests.utils.quote(query)}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    results = []

    for g in soup.select("div.g"):
        title_elem = g.find("h3")
        link_elem = g.find("a")
        if title_elem and link_elem:
            title = title_elem.text.strip()
            href = link_elem["href"]
            results.append({"title": title, "link": href})

    return results

def find_relevant_ad(sb_id, ata=None, system=None):
    query_variants = [
        f"Boeing SB {sb_id} AD site:federalregister.gov",
        f"Airworthiness Directive {sb_id} site:faa.gov",
    ]

    if ata:
        query_variants.append(f"ATA {ata} Boeing AD site:federalregister.gov")

    if system:
        query_variants.append(f"Boeing {system} AD site:federalregister.gov")

    for query in query_variants:
        print(f"🔍 Searching: {query}")
        results = search_google(query)
        for result in results:
            title = result["title"].lower()
            if "airworthiness directive" in title or "ad" in title:
                if sb_id.lower() in title or (ata and ata in title) or (system and system.lower() in title):
                    return result

    return {"title": "No relevant AD found", "link": ""}
