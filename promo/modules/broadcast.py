import asyncio
from pymongo import MongoClient
import config
from promo import app
from pyrogram import filters
from pyrogram.types import Message

client = MongoClient(config.MONGO_DB_URI)
db = client['MAIN']
userscol = db['users']

user_ids = [user['user_id'] for user in userscol.find({}, {"user_id": 1})]

@app.on_message(filters.command('broadcast') & filters.user(config.OWNER_ID))
async def broadcast(_, m: Message):
    if m.chat.type != 'ChatType.PRIVATE':
        await m.reply_text("您不能在群组中使用此命令。")
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

            await m.reply_text(f"广播消息至 `{successful_count}` 用户!")
        except Exception as e:
            await m.reply_text(f"糟糕！广播时出错：{str(e)}")
    else:
        await m.reply_text("回复您想要广播的消息。")
