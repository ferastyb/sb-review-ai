# web_search.py
import requests
from bs4 import BeautifulSoup

def find_relevant_ad(sb_summary):
    """
    Perform a basic web search to suggest a relevant Airworthiness Directive (AD)
    based on SB summary text. Returns the first matching URL or 'Not found'.
    """
    try:
        query = f"site:drs.faa.gov Airworthiness Directive {sb_summary}"
        url = f"https://www.google.com/search?q={query}"
        headers = {"User-Agent": "Mozilla/5.0"}

        response = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(response.text, "html.parser")

        # Attempt to get the first link from the search results
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if href.startswith("http") and "drs.faa.gov" in href:
                return href

        return "Not found"
    except Exception as e:
        print("Search error:", e)
        return "Not found"
