import logging
import requests
from bs4 import BeautifulSoup
from .config import BASE_URL, HEADERS
from .telegram_helper import send_to_telegram

sent_posts = set()

def get_gofile_link(intermediate_url):
    try:
        logging.info(f"🔍 Fetching GoFile intermediate URL: {intermediate_url}")
        response = requests.get(intermediate_url, headers=HEADERS, timeout=15)
        if response.status_code != 200:
            logging.warning(f"⚠️ Unexpected status code: {response.status_code}")
            return None

        soup = BeautifulSoup(response.text, "html.parser")
        for a in soup.find_all("a", href=True):
            href = a['href']
            if "gofile.io" in href:
                logging.info(f"📎 Found GoFile link: {href}")
                return href
        logging.warning("⚠️ No GoFile link found.")
        return None
    except Exception as e:
        logging.error(f"❌ Error in get_gofile_link: {e}")
        return None

def get_hubcloud_link(intermediate_url):
    try:
        logging.info(f"🔍 Fetching HubCloud intermediate URL: {intermediate_url}")
        response = requests.get(intermediate_url, headers=HEADERS, timeout=15)
        if response.status_code != 200:
            logging.warning(f"⚠️ Unexpected status code: {response.status_code}")
            return None

        soup = BeautifulSoup(response.text, "html.parser")
        for a in soup.find_all("a", href=True):
            href = a['href']
            if "hubcloud.ink" in href:
                logging.info(f"📎 Found HubCloud link: {href}")
                return href
        logging.warning("⚠️ No HubCloud link found.")
        return None
    except Exception as e:
        logging.error(f"❌ Error in get_hubcloud_link: {e}")
        return None

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
            if sibling.name == 'div' and sibling.get('class') and 'Fmvideo' in sibling.get('class'):
                a_tag = sibling.find('a', href=True)
                if not a_tag:
                    continue

                title = a_tag.text.strip()
                post_url = BASE_URL + "/" + a_tag['href'].lstrip('/')

                if post_url in sent_posts:
                    logging.info(f"⏩ Skipping already sent post: {title}")
                    continue

                logging.info(f"📄 Found post: {title} -> {post_url}")

                watch_online_link = None
                gofile_link = None
                hubcloud_link = None

                try:
                    post_resp = requests.get(post_url, headers=HEADERS)
                    post_soup = BeautifulSoup(post_resp.text, 'html.parser')

                    # Fetch Watch Online link
                    watch_online_link_tag = post_soup.find('a', href=True, string=lambda s: s and "WATCH ONLINE" in s)
                    if watch_online_link_tag:
                        watch_online_link = watch_online_link_tag['href']
                        logging.info(f"📎 Found Watch Online link: {watch_online_link}")

                    # Fetch GoFile link
                    server01_link = post_soup.find('a', href=True, string=lambda s: s and "SERVER 01" in s.upper())
                    if server01_link:
                        intermediate_url = server01_link['href']
                        gofile_link = get_gofile_link(intermediate_url)
                    else:
                        logging.warning("⚠️ SERVER 01 link not found.")

                    # Fetch HubCloud link
                    hubcloud_link_tag = post_soup.find('a', href=True, string=lambda s: s and "HubCloud" in s)
                    if hubcloud_link_tag:
                        hubcloud_link = hubcloud_link_tag['href']
                        logging.info(f"📎 Found HubCloud link: {hubcloud_link}")
                    else:
                        logging.warning("⚠️ HubCloud link not found.")

                except Exception as e:
                    logging.error(f"❌ Error fetching post page: {e}")

                # Call send_to_telegram with all the links
                await send_to_telegram(title, watch_online_link, gofile_link, hubcloud_link)
                sent_posts.add(post_url)
                count += 1
                if count >= 8:
                    break

    except Exception as e:
        logging.error(f"❌ Error in fetch_latest_posts: {e}")