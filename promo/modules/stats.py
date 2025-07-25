from promo import app
from pyrogram import filters
from promo.modules.save import users_collection
from promo.modules.ref import referrals_collection
from promo.modules.save import forwarded
from promo.modules.credit import users_collection
from promo.modules.app import appslist
from promo.modules.block import blocked
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import os
from promo.modules.usernames import usernames
from promo.modules.sudo import is_sudo
import config

@app.on_message(filters.command("profile"))
async def checkprofile(_, message):
    user_id = message.from_user.id

    if blocked.find_one({'user_id': user_id}):
        await message.reply_text("You are blocked from using this bot.")
        return

    if not await is_sudo(user_id):
        await message.reply_text("You're not a sudo user.")
        return

    user = await app.get_users(user_id)
    user_data = users_collection.find_one({"user_id": user_id})
    credits = user_data.get("credits", 0) if user_data else 0

    ads_forwarded = forwarded.find_one({'user_id': user_id})
    num_ads = ads_forwarded.get('count', 0) if ads_forwarded else 0
    referrals_count = referrals_collection.count_documents({"referrer_id": user_id})

    response = (
        f"🌟 **Your Profile Stats** 🌟\n\n"
        f"👤 **Credits**: `{credits}`\n"
        f"🔗 **Referrals**: `{referrals_count}`\n"
        f"📢 **Ads Forwarded**: `{num_ads}`"
    )

    await message.reply_text(response)

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(text=f"{message.from_user.first_name}", user_id=f'{message.from_user.id}')]
    ])
    await app.send_message(config.LOGS_CHANNEL_ID, f"{message.from_user.first_name} checked their's stats.", reply_markup=keyboard)

@app.on_message(filters.command("stats"))
async def checkstats(_, message):
    user_id = message.from_user.id

    if blocked.find_one({'user_id': user_id}):
        await message.reply_text("You have been blocked from using this service.")
        return

    total_users = users_collection.count_documents({})
    total_chats = len(usernames)

    response = (
        f"🌐 **Total Users**: `{total_users}`\n"
        f"🤖 **Assistants Available**: `{len(appslist)}`\n"
        f"💬 **Total Chats**: `{total_chats}`\n"
    )

    await message.reply_text(response)

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(text=f"{message.from_user.first_name}", user_id=f'{message.from_user.id}')]
    ])
    await app.send_message(config.LOGS_CHANNEL_ID, f"{message.from_user.first_name} checked bot's stats.", reply_markup=keyboard)
