import logging
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import tempfile

def get_fresh_driver():
    temp_user_data = tempfile.mkdtemp()
    chrome_options = Options()
    chrome_options.add_argument(f"--user-data-dir={temp_user_data}")
    chrome_options.add_argument("--headless=new")  # use "--headless" if "new" fails
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    return webdriver.Chrome(options=chrome_options)

def hubcloud_direct_links(url):
    driver = None
    try:
        logging.info("🔁 Trying to get direct HubCloud link...")
        logging.info(f"📎 Found redirect URL: {url}")

        # First, try static content (requests + BeautifulSoup)
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        links = [a['href'] for a in soup.find_all("a", href=True)
                 if any(x in a['href'] for x in ("pixeldrain", "r2.dev", "workers.dev"))]

        if links:
            logging.info("✅ Found direct links without JS rendering.")
            return links

        # Fallback to Selenium
        logging.warning("⚠️ Direct download link not found. Using Selenium...")

        driver = get_fresh_driver()
        driver.get(url)
        time.sleep(6)  # Adjust this for heavier pages

        elems = driver.find_elements(By.XPATH,
            "//a[contains(@href, 'pixeldrain') or contains(@href, 'r2.dev') or contains(@href, 'workers.dev')]"
        )
        final_links = [e.get_attribute("href") for e in elems if e.get_attribute("href")]

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

    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass
