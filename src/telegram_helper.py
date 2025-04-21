import logging
from telegram import Bot
from .config import BOT_TOKEN, CHAT_ID, CMD, USER_NAME, USER_ID

bot = Bot(token=BOT_TOKEN)

async def send_to_telegram(title, link):
    msg_default = (
        f"🎬 <b>New Post Just Dropped!</b>\n\n"
        f"📌 <b>Title:</b> {title}\n"
        f"🔗 <b>Download:</b> {link or '🚫 No GoFile Link Found'}\n"
        f"🌐 <i>Scraped from <a href='https://telegram.me/LeechFlix'>SkyMoviesHD</a></i>"
    )

    msg_leech = (
        f"⚡ /{CMD} {link or 'None'}\n"
        f"Tag: @{USER_NAME} {USER_ID}"
    )

    try:
        await bot.send_message(chat_id=CHAT_ID[0], text=msg_default, parse_mode="HTML")
        logging.info("✅ Sent to Update Channel")

        if link:  # Only send to CHAT_ID[1] if there is a link
            await bot.send_message(chat_id=CHAT_ID[1], text=msg_leech, parse_mode="HTML")
            logging.info("✅ Sent to Leech Channel")

    except Exception as e:
        logging.error(f"❌ Telegram sending error: {e}")
