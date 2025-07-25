from pyrogram import filters
from pyrogram.types import Message
from pymongo import MongoClient
from datetime import datetime
import config
from promo import app
from promo.modules.block import blocked
from promo.modules.dev import sudo_user_filter

client = MongoClient(config.MONGO_DB_URI)
db = client["MAIN"]
sudo_users = db["sudo_users"]

async def is_sudo(user_id):
    return sudo_users.find_one({"user_id": user_id}) is not None

async def add_sudo_db(user_id):
    sudo_users.insert_one({"user_id": user_id, "added_date": datetime.now()})

@app.on_message(filters.command("addsudo") & sudo_user_filter() & filters.group)
async def add_sudo(app, message: Message):
    if message.reply_to_message:
        user = message.reply_to_message.from_user
        user_id = user.id
    else:
        inputs = message.text.split()[1]
        if inputs.isdigit():
            user_id = int(inputs)
            user = await app.get_users(user_id)
        else:
            username = inputs.lstrip('@')
            user = await app.get_users(username)
            user_id = user.id

    if user:
        if not await is_sudo(user_id):
            await add_sudo_db(user_id)
            await message.reply_text(f"Added {user.mention} as sudo.")
        else:
            await message.reply_text(f"User {user.mention} is already a sudo.")
    else:
        await message.reply_text("Please provide a valid user or reply to a message to add as a sudo user.")

@app.on_message(filters.command("delsudo") & sudo_user_filter() & filters.group)
async def del_sudo(app, message: Message):
    if message.reply_to_message:
        user = message.reply_to_message.from_user
        user_id = user.id
    else:
        inputs = message.text.split()[1]
        if inputs.isdigit():
            user_id = int(inputs)
            user = await app.get_users(user_id)
        else:
            username = inputs.lstrip('@')
            user = await app.get_users(username)
            user_id = user.id

    if user:
        if await is_sudo(user_id):
            sudo_users.delete_one({"user_id": user_id})
            await message.reply_text(f"User {user.mention} removed as sudo.")
        else:
            await message.reply_text(f"User {user.mention} isn't a sudo user.")
    else:
        await message.reply_text("Please provide a valid user or reply to a message to remove as a sudo user.")

@app.on_message(filters.command("sudolist"))
async def listsudo(client, message: Message):

    if blocked.find_one({'user_id': message.from_user.id}):
        await message.reply_text("You are blocked from using this bot.")
        return

    sudo_list = sudo_users.find({})
    response = "Sudo Users:\n\n"

    for sudo_user in sudo_list:
        user_id = sudo_user["user_id"]
        response += f"➻ [ID](tg://openmessage?user_id={user_id}) : `{user_id}`\n"

    if response == "Sudo Users:\n":
        response += "No sudo users found."

    await message.reply_text(response)

async def get_all_sudo_users():
    return [entry["user_id"] for entry in sudo_users.find()]