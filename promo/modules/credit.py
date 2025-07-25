from datetime import datetime, timedelta
import pytz
from pyrogram import Client, filters
from pymongo import MongoClient
from promo import app
from pyrogram.types import Message
from promo.database import userscollection, sudo_users, blocked
from datetime import datetime, timedelta
from pytz import timezone

async def is_sudo(user_id):
    return sudo_users.find_one({"user_id": user_id}) is not None

@app.on_message(filters.command('credit'))
async def creditinfo(_, message: Message):

    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    else:
        user_id = message.from_user.id

    try:
        user = await app.get_users(user_id)
    except Exception as e:
        print(str(e))

    if not await is_sudo(message.from_user.id):
        await message.reply_text("You are not a sudo user.")
        return

    if message.reply_to_message and not await is_sudo(user_id):
        await message.reply_text("Replied user isn't a sudo user.")
        return

    user = await userscollection.find_one({"user_id": user_id})

    if not user:
        credits = 0
    else:
        credits = user.get("credits", 0)

    utc_now = datetime.utcnow()
    
    utc = pytz.utc
    china_tz = pytz.timezone('Asia/Shanghai')
    china_now = utc_now.astimezone(china_tz)
    next_reset = (china_now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    time_until_reset = next_reset - china_now
    hours_left = time_until_reset.total_seconds() // 3600
    minutes_left = (time_until_reset.total_seconds() % 3600) // 60

    resp = (
        f"Current credits: `{credits}`\n"
        f"Time to reset: `{int(hours_left)}` hours and `{int(minutes_left)}` minutes.\n"
        f"Reset will occur at: {next_reset.strftime('%Y-%m-%d %H:%M:%S')} (China Time)"
    )

    await message.reply_text(resp)
