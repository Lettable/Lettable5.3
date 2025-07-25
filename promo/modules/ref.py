import asyncio
from pyrogram import filters
from pyrogram.types import Message
from pymongo import MongoClient
from promo import app
import config
from promo.modules.block import blocked

db = MongoClient(config.MONGO_DB_URI)
DATABASE = db['MAIN']
users_collection = DATABASE['users']
referrals_collection = DATABASE['referrals']


@app.on_message(filters.command('refers'))
async def check_referrals(_, message: Message):
    user_id = message.from_user.id

    if blocked.find_one({'user_id': message.from_user.id}):
        await message.reply_text("You are blocked from using this bot.")
        return

    user_data = referrals_collection.find_one({"user_id": user_id})

    if not user_data or not user_data.get("referrals_count", 0) > 0:
        await message.reply_text("You haven't referred anyone yet.")
        return

    referrals = referrals_collection.find({"referrer_id": user_id})
    response = "Here are your referrals:\n\n"

    for referral in referrals:
        referral_user_id = referral["user_id"]
        try:
            user_info = await app.get_users(referral_user_id)
            username = user_info.username or "No username"
            mention = user_info.mention or user_info.first_name
            response += f"• {mention}\n  ID: `{referral_user_id}`\n\n"
        except Exception as e:
            response += f"• Failed to get info for `{referral_user_id}`\n\n"

    await message.reply_text(response)
