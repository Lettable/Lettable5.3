from pyrogram import Client, filters
from pymongo import MongoClient
import config
from pyrogram.types import Message
from promo import app

client = MongoClient(config.MONGO_DB_URI)
db = client['MAIN']
blocked = db['blocked']

@app.on_message(filters.command('block') & filters.user(config.NIGGERS))
async def blockusr(app, message: Message):
    if message.reply_to_message:
        user = message.reply_to_message.from_user
    elif message.text.split()[1].isdigit():
        user_id = int(message.text.split()[1])
        user = await app.get_users(user_id)
    else:
        username = message.text.split()[1].lstrip('@')
        user = await app.get_users(username)

    if user:
        if blocked.find_one({'user_id': user.id}):
            await message.reply_text(f"用户 {user.mention} 已被阻止。")
        else:
            blocked.insert_one({
                'user_id': user.id,
                'username': user.username
            })
            await message.reply_text(f"用户 {user.mention} 已被阻止。")
    else:
        await message.reply_text("未找到用户。")

@app.on_message(filters.command('unblock') & filters.user(config.NIGGERS))
async def unblockusr(app, message: Message):
    if message.reply_to_message:
        user = message.reply_to_message.from_user
    elif message.text.split()[1].isdigit():
        user_id = int(message.text.split()[1])
        user = await app.get_users(user_id)
    else:
        username = message.text.split()[1].lstrip('@')
        user = await app.get_users(username)

    if user:
        if not blocked.find_one({'user_id': user.id}):
            await message.reply_text(f"用户 {user.mention} 没有被阻塞。")
        else:
            blocked.delete_one({'user_id': user.id})
            await message.reply_text(f"用户 {user.mention} 已解除封锁。")
    else:
        await message.reply_text("User not found.")

@app.on_message(filters.command('blocked'))
async def blocked_list(app, message: Message):
    blockedusers = blocked.find()
    if blocked.count_documents({}) == 0:
        await message.reply_text("没有用户被阻止。")
        return

    blockedlist = "Blocked Users:\n"
    for user in blockedusers:
        username = user['username']
        user_id = user['user_id']
        blockedlist += f"• @{username} (ID: `{user_id}`)\n"

    await message.reply_text(blockedlist)
