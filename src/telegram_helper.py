import logging
import aiohttp
import re
from telegram import Bot
from .config import BOT_TOKEN, CHAT_ID, CMD, USER_NAME, USER_ID

bot = Bot(token=BOT_TOKEN)

async def get_poster_link(title):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"http://64.227.160.49:8085/api?get={title}") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("poster")
    except Exception as e:
        logging.warning(f"⚠️ Poster API error: {e}")
    return None

async def send_to_telegram(title, watch_online_link, gofile_link, all_links, hubcloud_links):
    # Remove hubcloud links from all_links to avoid duplicates
    all_links_cleaned = [link for link in all_links if link not in hubcloud_links]

    # Fetch poster link
    poster_link = await get_poster_link(clean_title_for_poster(title))

    # Message for the update channel
    msg_default = (
        f"🎬 <b>New Post Just Dropped! ✅</b>\n\n"
        f"📌 <b>Title:</b> <code>{title}</code>\n\n"
        f"<b>🔰GoFile Link🔰</b> \n• {gofile_link or '🚫 No GoFile Link Found'}\n"
    )

    if watch_online_link:
        msg_default += f"\n<b>🐬Stream Tape Link🐬</b> \n• {watch_online_link}\n"

    if hubcloud_links:
        msg_default += "\n<b>🚀HubCloud Scraped Links🚀</b>\n"
        for link in hubcloud_links:
            if "pixeldrain.net" in link:
                label = "Pixeldrain"
            elif "workers.dev" in link:
                label = "Google Server"
            elif "r2.dev" in link:
                label = "Fast Server"
            else:
                label = "Fast Server 2"
            msg_default += f"• <a href='{link}'>{label}</a>\n"

    if all_links_cleaned:
        msg_default += "\n<b>♻️All Cloud Links♻️</b>\n"
        for link in all_links_cleaned:
            msg_default += f"• <a href='{link}'>{link}</a>\n"

    msg_default += "\n<blockquote>🌐 <b>Scraped from <a href='https://telegram.me/LeechFlix'>SkyMoviesHD</a></b></blockquote>"

    # Choose a fast server link
    fast_server_link = next((l for l in hubcloud_links if "r2.dev" in l), gofile_link or 'None')

    # Message to Leech Channel with poster (if available)
    if poster_link:
        msg_leech = (
            f"/{CMD} {fast_server_link} -t {poster_link}\n"
            f"**Tag:** `@{USER_NAME}` `{USER_ID}`"
        )
    else:
        msg_leech = (
            f"/{CMD} {fast_server_link}\n"
            f"**Tag:** `@{USER_NAME}` `{USER_ID}|"
        )

    try:
        await bot.send_message(chat_id=CHAT_ID[0], text=msg_default, parse_mode="HTML", disable_web_page_preview=True)
        logging.info("✅ Sent to Update Channel")

        if gofile_link or watch_online_link or hubcloud_links:
            await bot.send_message(chat_id=CHAT_ID[1], text=msg_leech, parse_mode="HTML")
            logging.info("✅ Sent to Leech Channel")

    except Exception as e:
        logging.error(f"❌ Telegram sending error: {e}")

def clean_title_for_poster(title: str) -> str:
    """
    Extracts the 'Name (Year)' part from a full release title.
    Example: 'El Gallo (2018) 1080p HDRip...' -> 'El Gallo (2018)'
    """
    match = re.search(r'^(.*?\(\d{4}\))', title)
    if match:
        return match.group(1).strip()
    return title.strip()
