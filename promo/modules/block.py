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
            await message.reply_text(f"User {user.mention} is already blocked.")
        else:
            blocked.insert_one({
                'user_id': user.id,
                'username': user.username
            })
            await message.reply_text(f"User {user.mention} has been blocked.")
    else:
        await message.reply_text("User not found.")

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
            await message.reply_text(f"User {user.mention} is not blocked.")
        else:
            blocked.delete_one({'user_id': user.id})
            await message.reply_text(f"User {user.mention} has been unblocked.")
    else:
        await message.reply_text("User not found.")

@app.on_message(filters.command('blocked'))
async def blocked_list(app, message: Message):
    blockedusers = blocked.find()
    if blocked.count_documents({}) == 0:
        await message.reply_text("No users are blocked.")
        return

    blockedlist = "Blocked Users:\n"
    for user in blockedusers:
        username = user['username']
        user_id = user['user_id']
        blockedlist += f"• @{username} (ID: `{user_id}`)\n"

    await message.reply_text(blockedlist)
