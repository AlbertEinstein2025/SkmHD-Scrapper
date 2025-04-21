import logging
from telegram import Bot
from .config import BOT_TOKEN, CHAT_ID, CMD

bot = Bot(token=BOT_TOKEN)

async def send_to_telegram(title, link):
    msg_default = f"<b>{title}</b>\n{link or 'None'}"
    msg_leech = f"/{CMD} {link or 'None'}\nTag: @SpeXtro 7062467346"
    try:
        await bot.send_message(chat_id=CHAT_ID[0], text=msg_default, parse_mode="HTML")
        logging.info("✅ Sent to Telegram (channel)")
        await bot.send_message(chat_id=CHAT_ID[1], text=msg_leech, parse_mode="HTML")
        logging.info("✅ Sent to Telegram (group)")
    except Exception as e:
        logging.error(f"❌ Telegram sending error: {e}")
