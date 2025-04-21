import asyncio
from .scraper import fetch_latest_posts

async def scheduler():
    while True:
        await fetch_latest_posts()
        await asyncio.sleep(600)
