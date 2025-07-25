# This script is just to edit the numbers of vouch/forwards automatically. you just gotta send a message in respective message and put its message ID in this here message_id=3
# Change the Username as need like "Hey Welcome to @LettablesVouches." to "Hey Welcome to @someshityousentinchannel."
# If you are a pussy and can't understand what it means hmu

from pyrogram import filters
from promo import app
import config
from pymongo import MongoClient
from pyrogram.types import Message

client = MongoClient(config.MONGO_DB_URI)
db = client["MAIN"]
vouchdb = db["vouch"]
messagedb = db["message"]

@app.on_message(filters.forwarded & filters.chat(config.VOUCH_CHANNEL_ID))
async def vouchcount(_, message: Message):
    vouch_doc = vouchdb.find_one({})

    if vouch_doc is None:
        vouchdb.insert_one({"count": 0})

    vouchdb.update_one({}, {"$inc": {"count": 1}})
    vouch_doc = vouchdb.find_one({})

    vouchcount = vouch_doc["count"]

    text = f"Hey Welcome to @LettablesVouches.\nTotal Vouch: {vouchcount}"
    await app.edit_message_text(config.VOUCH_CHANNEL_ID, message_id=3, text=text)



@app.on_message(filters.text & filters.chat(config.BROADCAST_CHANNEL_ID))
async def vouchcount(_, message: Message):
    messagdoc = messagedb.find_one({})

    if messagdoc is None:
        messagedb.insert_one({"count": 11101})

    messagedb.update_one({}, {"$inc": {"count": 1}})
    messagdoc = messagedb.find_one({})

    messagecount = messagdoc["count"]

    text = f"Welcome to @TrackAds.\nTotal Forwarded: `{messagecount}`"
    await app.edit_message_text(config.BROADCAST_CHANNEL_ID, message_id=3, text=text)
