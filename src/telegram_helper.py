import logging
from telegram import Bot
from .config import BOT_TOKEN, CHAT_ID, CMD, USER_NAME, USER_ID

bot = Bot(token=BOT_TOKEN)

async def send_to_telegram(title, watch_online_link, gofile_link, all_links, hubcloud_links):
    # Default message with all possible links
    msg_default = (
        f"🎬 <b>New Post Just Dropped!</b>\n\n"
        f"📌 <b>Title:</b> <code>{title}</code>\n\n"
        f"🔗 <b>Links:</b>\n"
        f"• <b>Watch Online:</b> {watch_online_link or '🚫 No Watch Online Link Found'}\n"
        f"• <b>GoFile Download:</b> {gofile_link or '🚫 No GoFile Link Found'}\n"
    )
    
    # If there are any Google Drive Direct links (all_links), add them
    if all_links:
        msg_default += "\n<b>Google Drive Links:</b>\n"
        for link in all_links:
            msg_default += f"• <a href='{link}'>{link}</a>\n"

    # If there are any HubCloud links, add them
    if hubcloud_links:
        msg_default += "\n<b>HubCloud Links:</b>\n"
        for link in hubcloud_links:
            msg_default += f"• <a href='{link}'>{link}</a>\n"
    
    # Final message footer
    msg_default += (
        f"\n🌐 <b>Scraped from <a href='https://telegram.me/LeechFlix'>SkyMoviesHD</a></b>"
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