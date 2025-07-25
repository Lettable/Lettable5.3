import asyncio
from pymongo import MongoClient
import config
from promo import app
from pyrogram import filters
from pyrogram.types import Message

client = MongoClient(config.MONGO_DB_URI)
db = client['MAIN']
users_collection = db['users']

user_ids = [user['user_id'] for user in users_collection.find({}, {"user_id": 1})]

@app.on_message(filters.command('broadcast') & filters.user(config.NIGGERS))
async def broadcast(_, m: Message):
    if m.chat.type != 'ChatType.PRIVATE':
        await m.reply_text("You can't you this command in group.")
        return
        
    if m.reply_to_message:
        try:
            msg_id = m.reply_to_message.id
            app_id = app.me.id
            successful_count = 0

            for user_id in user_ids:
                try:
                    await app.forward_messages(chat_id=user_id, from_chat_id=app_id, message_ids=msg_id)
                    successful_count += 1
                except Exception as e:
                    print(f"Error broadcasting to user {user_id}: {str(e)}")
                    continue

            await m.reply_text(f"Broadcasted message to `{successful_count}` users!")
        except Exception as e:
            await m.reply_text(f"Oops! An error occurred while broadcasting: {str(e)}")
    else:
        await m.reply_text("Reply to a message you want to broadcast.")
