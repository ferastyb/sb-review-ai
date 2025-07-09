import requests
from bs4 import BeautifulSoup

def find_relevant_ad(sb_id, reason):
    """
    Searches DuckDuckGo for relevant airworthiness directives based on the SB ID and reason.
    Returns the title and URL of the top result.
    """
    try:
        # Construct the query using both the Service Bulletin ID and reason
        query = f"{sb_id} {reason} site:regulations.gov OR site:ecfr.gov"
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; ServiceBulletinAI/1.0)"
        }

        # Perform the search using DuckDuckGo HTML interface
        response = requests.get(f"https://html.duckduckgo.com/html/?q={query}", headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract the first result
        result = soup.find("a", class_="result__a")
        if result and result['href']:
            title = result.get_text()
            url = result["href"]
            return f"{title}\n{url}"
        else:
            return "No relevant AD found."

    except Exception as e:
        return f"Error while searching for AD: {e}"
