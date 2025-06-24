import requests
from bs4 import BeautifulSoup
import logging
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import urlparse, parse_qs

# Logging setup
logging.basicConfig(level=logging.INFO)

# Headers for requests
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
}

# Setup Selenium options
options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('start-maximized')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')


def get_download_links_from_redirect(redirect_url):
    """
    Use Selenium to extract links like pixeldrain/gpdl/r2.dev after redirection.
    """
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get(redirect_url)
        time.sleep(5)

        download_links = driver.find_elements(By.XPATH,
            "//a[contains(@href, 'pixeldrain.net') or contains(@href, 'workers.dev') or contains(@href, 'r2.dev') or  contains(@href, 'cdnbaba.xyz')]"
        )

        if not download_links:
            logging.warning("⚠️ No dynamic download links found.")
            return None

        urls = [link.get_attribute('href') for link in download_links]
        logging.info(f"📎 Found dynamic download links: {urls}")
        return urls
    except Exception as e:
        logging.error(f"❌ Selenium error: {e}")
        return None
    finally:
        driver.quit()


def get_hubcloud_direct_link(hubcloud_url):
    """
    First try static scraping. If that fails, use Selenium.
    """
    try:
        response = requests.get(hubcloud_url, headers=HEADERS, timeout=15)
        if response.status_code != 200:
            logging.warning(f"⚠️ Cannot access HubCloud page: {response.status_code}")
            return None
        
        soup = BeautifulSoup(response.text, "html.parser")
        generate_button = soup.find("a", id="download", href=True)

        if not generate_button:
            logging.warning("⚠️ 'Generate Direct Download Link' button not found.")
            return None
        
        redirect_url = generate_button['href']
        logging.info(f"📎 Found redirect URL: {redirect_url}")

        # Try static redirect fetch first
        redirect_response = requests.get(redirect_url, headers=HEADERS, timeout=15)
        if redirect_response.status_code != 200:
            logging.warning("⚠️ Failed to load redirect page.")
            return None

        redirect_soup = BeautifulSoup(redirect_response.text, "html.parser")
        static_link = redirect_soup.find("a", class_="btn btn-primary h6 p-2", href=True)
        
        if static_link:
            final_url = static_link['href']
            logging.info(f"📎 Found static direct link: {final_url}")
            return [final_url]
        
        # If static link failed, fallback to Selenium
        logging.info("🔁 Falling back to Selenium for dynamic content...")
        return get_download_links_from_redirect(redirect_url)

    except Exception as e:
        logging.error(f"❌ Error in get_hubcloud_direct_link: {e}")
        return None