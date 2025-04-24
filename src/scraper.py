import logging
import requests
from bs4 import BeautifulSoup
from .config import HEADERS
from .telegram_helper import send_to_telegram
from .hubcloud import get_hubcloud_direct_link
from .domain_fetcher import fetch_current_domain

sent_posts = set()
BASE_URL = fetch_current_domain()

def get_gofile_link(intermediate_url):
    try:
        logging.info(f"🔍 Fetching GoFile intermediate URL: {intermediate_url}")
        response = requests.get(intermediate_url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(response.text, "html.parser")
        for a in soup.find_all("a", href=True):
            href = a['href']
            if "gofile.io" in href:
                return href
        return None
    except Exception as e:
        logging.error(f"❌ Error in get_gofile_link: {e}")
        return None

def get_streamtape_link(intermediate_url):
    try:
        logging.info(f"🔍 Fetching StreamTape intermediate URL: {intermediate_url}")
        response = requests.get(intermediate_url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(response.text, "html.parser")
        for a in soup.find_all("a", href=True):
            href = a['href']
            if "streamtape.to" in href:
                return href
        return None
    except Exception as e:
        logging.error(f"❌ Error in get_streamtape_link: {e}")
        return None

def extract_all_drive_links_from_page(url):
    all_links, hubcloud_link = [], []
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(response.text, "html.parser")
        for a in soup.find_all("a", href=True):
            href = a.get('href', '').strip()
            if href.startswith("http") and any(domain in href for domain in [
                "hubdrive", "hubcloud", "gdflix", "gdtot", "filepress", "media.cm", "drive.google"
            ]):
                if href not in all_links:
                    all_links.append(href)
                if "hubcloud" in href:
                    direct_links = get_hubcloud_direct_link(href)
                    if direct_links:
                        hubcloud_link.extend(direct_links)
    except Exception as e:
        logging.error(f"❌ Error extracting all links: {e}")
    return all_links, hubcloud_link

async def process_post(title, post_url):
    try:
        post_resp = requests.get(post_url, headers=HEADERS)
        post_soup = BeautifulSoup(post_resp.text, 'html.parser')

        # Check for episode links inside `.Bolly`
        bolly_section = post_soup.find('div', class_='Bolly')
        if bolly_section:
            for a in bolly_section.find_all("a", href=True):
                ep_href = a['href']
                ep_title = a.get_text(strip=True)
                ep_url = ep_href if ep_href.startswith("http") else BASE_URL + "/" + ep_href.lstrip('/')
                logging.info(f"📺 Episode found: {ep_title} -> {ep_url}")
                await process_post(f"{title} - {ep_title}", ep_url)
            return  # Skip rest since episodes are already processed

        # Standard post processing
        server01_tag = post_soup.find('a', href=True, string=lambda s: s and "SERVER 01" in s.upper())
        gofile_link = get_gofile_link(server01_tag['href']) if server01_tag else None
        watch_online_link = get_streamtape_link(server01_tag['href']) if server01_tag else None

        all_links, hubcloud_link = [], []
        drive_links_tag = post_soup.find('a', href=True, string=lambda s: s and "Google Drive Direct Links" in s)
        if drive_links_tag:
            all_links, hubcloud_link = extract_all_drive_links_from_page(drive_links_tag['href'])

        await send_to_telegram(title, watch_online_link, gofile_link, all_links, hubcloud_link)

    except Exception as e:
        logging.error(f"❌ Error processing post {post_url}: {e}")

async def fetch_latest_posts():
    try:
        logging.info("🔁 Checking for latest posts...")
        response = requests.get(BASE_URL, headers=HEADERS)
        soup = BeautifulSoup(response.text, 'html.parser')

        marker = soup.find('div', class_='Robiul', string=lambda s: 'Latest Updated Movies' in s)
        if not marker:
            logging.warning("⚠️ 'Latest Updated Movies' section not found.")
            return

        count = 0
        for sibling in marker.find_next_siblings():
            if sibling.name == 'div' and 'Fmvideo' in sibling.get('class', []):
                a_tag = sibling.find('a', href=True)
                if not a_tag:
                    continue

                title = a_tag.text.strip()
                post_url = BASE_URL + "/" + a_tag['href'].lstrip('/')

                if post_url in sent_posts:
                    logging.info(f"⏩ Skipping already sent post: {title}")
                    continue

                logging.info(f"📄 Found post: {title} -> {post_url}")
                await process_post(title, post_url)
                sent_posts.add(post_url)

                count += 1
                if count >= 8:
                    break

    except Exception as e:
        logging.error(f"❌ Error in fetch_latest_posts: {e}")