import requests
from bs4 import BeautifulSoup
import re

def find_relevant_ad(sb_id, ata, system):
    query = f"{sb_id} AD site:federalregister.gov"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        res = requests.get(f"https://www.google.com/search?q={query}", headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")

        for link in soup.select("a"):
            href = link.get("href")
            if href and "https://www.federalregister.gov/documents/" in href:
                ad_url = href.split("&")[0].replace("/url?q=", "")
                ad_res = requests.get(ad_url, headers=headers, timeout=10)
                ad_soup = BeautifulSoup(ad_res.text, "html.parser")

                # Extract title
                title_tag = ad_soup.find("h1", class_="document-title")
                title = title_tag.text.strip() if title_tag else "Unknown AD"

                # Extract effective date
                summary_text = ad_soup.get_text()
                date_match = re.search(r"effective date.*?(\w+\s\d{1,2},\s\d{4})", summary_text, re.IGNORECASE)
                effective_date = date_match.group(1) if date_match else "N/A"

                return {
                    "title": title,
                    "effective_date": effective_date
                }

    except Exception as e:
        print("Error during AD search:", e)

    return {
        "title": "Not found",
        "effective_date": "N/A"
    }
