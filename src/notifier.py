import asyncio
from telegram import Bot
from config.settings import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
import time
import logging

logger = logging.getLogger(__name__)

def send_new_jobs(jobs):
    # jobs is a list of new job positions
    for job in jobs:
        time.sleep(3)
        message = format_job_message(job)
        try:
            asyncio.run(send_telegram_async(message))
        except Exception as ex:
            logger.info(message)

def format_job_message(job):
    return (
        f"🔔 *New Job Found!*\n"
        f"🏢 *Company:* {job['company']}\n"
        f"💼 *Role:* {job['title']}\n"
        f"📍 *Location:* {job['location'] or 'N/A'}\n"
        f"🔗 [Apply Here]({job['link']})\n"
    )

def send_error(parser_name, error_message):
    message = f"⚠️ *Parser Error* ⚠️\n\n⚙️ *Parser:* {parser_name}\n❌ *Error:* `{error_message}`"
    try:
        asyncio.run(send_telegram_async(message))
    except Exception as ex:
        return

async def send_telegram_async(message):
    bot = Bot(token=TELEGRAM_TOKEN)
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID,
                           text=message,
                           parse_mode="Markdown")
