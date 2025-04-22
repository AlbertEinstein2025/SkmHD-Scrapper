import logging
from telegram import Bot
from .config import BOT_TOKEN, CHAT_ID, CMD, USER_NAME, USER_ID

bot = Bot(token=BOT_TOKEN)

async def send_to_telegram(title, watch_online_link, gofile_link, hubcloud_link):
    # Default message with all possible links
    msg_default = (
        f"🎬 <b>New Post Just Dropped!</b>\n\n"
        f"📌 <b>Title:</b> <code>{title}</code>\n\n"
        f"🔗 <b>Links:</b>\n"
        f"• <b>Watch Online:</b> {watch_online_link or '🚫 No Watch Online Link Found'}\n"
        f"• <b>GoFile Download:</b> {gofile_link or '🚫 No GoFile Link Found'}\n"
        f"• <b>HubCloud Download:</b> {hubcloud_link or '🚫 No HubCloud Link Found'}\n\n"
        f"🌐 <b>Scraped from <a href='https://telegram.me/LeechFlix'>SkyMoviesHD</a></b>"
    )

    # Special message for Leech channel
    msg_leech = (
        f"/{CMD} {gofile_link or 'None'}\n"
        f"Tag: @{USER_NAME} {USER_ID}"
    )

    try:
        # Send to the update channel
        await bot.send_message(chat_id=CHAT_ID[0], text=msg_default, parse_mode="HTML", disable_web_page_preview=True)
        logging.info("✅ Sent to Update Channel")

        # If there is any link, send to the Leech channel as well
        if gofile_link or watch_online_link or hubcloud_link:
            await bot.send_message(chat_id=CHAT_ID[1], text=msg_leech, parse_mode="HTML")
            logging.info("✅ Sent to Leech Channel")

    except Exception as e:
        logging.error(f"❌ Telegram sending error: {e}")