from pyrogram import Client, filters
from config import MONGO_DB_URI
from pymongo import MongoClient
from promo import app 
from pyrogram.types import Message
import config

client = MongoClient(config.MONGO_DB_URI)
db = client['MAIN']
users_collection = db['users']

@app.on_message(filters.command('reset') & filters.user(config.NIGGERS))
async def resetcred(_, message: Message):
    parts = message.text.split()
    if len(parts) != 2:
        await message.reply_text("Usage: /reset <user_id>")
        return

    target = int(parts[1])
    user = users_collection.find_one({"user_id": target})
    
    if not user:
        await message.reply_text(f"No data found for user ID {target}.")
        return
    users_collection.update_one({"user_id": target}, {"$set": {"credits": 5}})
    await message.reply_text(f"Credits for user `{target}` have been reset to 5.")
