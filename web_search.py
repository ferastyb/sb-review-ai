import requests
from bs4 import BeautifulSoup


def find_relevant_ad(sb_id, ata, system):
    query = f"Boeing {sb_id} site:federalregister.gov"
    search_url = f"https://www.google.com/search?q={query}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(search_url, headers=headers)
        if response.status_code != 200:
            return {"title": "Not found", "effective_date": "N/A"}

        soup = BeautifulSoup(response.text, "html.parser")
        links = [a["href"] for a in soup.select("a[href]") if "federalregister.gov/documents" in a["href"]]

        for link in links:
            try:
                ad_page = requests.get(link, headers=headers)
                ad_soup = BeautifulSoup(ad_page.text, "html.parser")
                ad_title = ad_soup.find("h1").text.strip()
                if (sb_id.split("SB")[-1][:6] in ad_title) or (ata in ad_title and system.split()[0] in ad_title):
                    effective = ad_soup.find("strong", string="Effective date:")
                    date = effective.find_next("p").text.strip() if effective else "N/A"
                    return {"title": ad_title, "effective_date": date}
            except:
                continue

        return {"title": "Not found", "effective_date": "N/A"}

    except Exception as e:
        return {"title": "Not found", "effective_date": "N/A"}
