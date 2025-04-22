import logging
from telegram import Bot
from .config import BOT_TOKEN, CHAT_ID, CMD, USER_NAME, USER_ID

bot = Bot(token=BOT_TOKEN)

async def send_to_telegram(title, watch_online_link, gofile_link, all_links, hubcloud_links):
    # Remove hubcloud links from all_links to avoid duplicates
    all_links_cleaned = [link for link in all_links if link not in hubcloud_links]

    # Message for the update channel
    msg_default = (
        f"🎬 <b>New Post Just Dropped!</b>\n\n"
        f"📌 <b>Title:</b> <code>{title}</code>\n\n"
        f"🔗 <b>Links:</b>\n"
        f"• <b>Watch Online:</b> \n{watch_online_link or '🚫 No Watch Online Link Found'}\n"
        f"• <b>GoFile Download:</b> \n{gofile_link or '🚫 No GoFile Link Found'}\n"
    )

    if all_links_cleaned:
        msg_default += "\n<b>Google Drive Links:</b>\n"
        for link in all_links_cleaned:
            msg_default += f"• <a href='{link}'>{link}</a>\n"

    if hubcloud_links:
        msg_default += "\n<b>HubCloud Links:</b>\n"
        labels = ["Pixeldrain", "Fast Server 01", "Fast Server #Recommended"]
        for i, link in enumerate(hubcloud_links):
            label = labels[i] if i < len(labels) else f"Server {i+1}"
            msg_default += f"• <a href='{link}'>{label}</a>\n"

    msg_default += "\n🌐 <b>Scraped from <a href='https://telegram.me/LeechFlix'>SkyMoviesHD</a></b>"

    # Message for the leech channel
    msg_leech = (
        f"/{CMD} {gofile_link or 'None'}\n"
        f"Tag: @{USER_NAME} {USER_ID}"
    )

    try:
        await bot.send_message(chat_id=CHAT_ID[0], text=msg_default, parse_mode="HTML", disable_web_page_preview=True)
        logging.info("✅ Sent to Update Channel")

        if gofile_link or watch_online_link or hubcloud_links:
            await bot.send_message(chat_id=CHAT_ID[1], text=msg_leech, parse_mode="HTML")
            logging.info("✅ Sent to Leech Channel")

    except Exception as e:
        logging.error(f"❌ Telegram sending error: {e}")