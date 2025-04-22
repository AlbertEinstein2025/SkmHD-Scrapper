import requests
from bs4 import BeautifulSoup

def fetch_current_domain():
    try:
        url = "https://skybap.com"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the first anchor tag that links to a skymovieshd domain
        link = soup.find("a", href=True, text=lambda t: t and "skymovieshd" in t.lower())

        if link and link["href"].startswith("http"):
            return link["href"].strip("/")

        return None
    except Exception as e:
        print(f"❌ Error fetching domain: {e}")
        return None