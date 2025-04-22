import logging
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import tempfile

def get_fresh_driver():
    temp_user_data = tempfile.mkdtemp()
    chrome_options = Options()
    chrome_options.add_argument(f"--user-data-dir={temp_user_data}")
    chrome_options.add_argument("--headless=new")  # Optional: use old "--headless" if needed
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    return webdriver.Chrome(options=chrome_options)

def hubcloud_direct_links(url):
    try:
        print("🔁 Trying to get direct HubCloud link with Selenium...")
        driver = get_fresh_driver()
        driver.get(url)
        logging.info(f"📎 Found redirect URL: {url}")
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        links = [a['href'] for a in soup.find_all("a", href=True) if "pixeldrain" in a['href'] or "r2.dev" in a['href']]
        if links:
            logging.info("✅ Found direct links without JS rendering.")
            return links

        logging.warning("⚠️ Direct download link not found.")
        logging.info("🔁 Falling back to Selenium for dynamic content...")

        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        time.sleep(7)

        elems = driver.find_elements("xpath", "//a[contains(@href, 'pixeldrain') or contains(@href, 'r2.dev') or contains(@href, 'workers.dev')]")
        final_links = [e.get_attribute("href") for e in elems if e.get_attribute("href")]

        driver.quit()

        if final_links:
            logging.info("✅ Final Download Link(s):")
            for link in final_links:
                logging.info(link)
        else:
            logging.warning("⚠️ No download links found via Selenium.")

        return final_links
    except Exception as e:
        logging.error(f"❌ Error in hubcloud_direct_links: {e}")
        return []