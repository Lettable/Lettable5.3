import asyncio
import config
from pyrogram import filters
from pyrogram.errors import FloodWait
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from pymongo import MongoClient
from pyrogram.enums import ChatType
from promo import app
from promo.modules.block import blocked

db = MongoClient(config.MONGO_DB_URI)
DATABASE = db['MAIN']
users_collection = DATABASE['users']

start_button = InlineKeyboardMarkup([
    [InlineKeyboardButton(text='Owner', user_id=6586350542)],
    [InlineKeyboardButton(text='Fuck', callback_data='fuck'),
     InlineKeyboardButton(text='Yourself', callback_data='yourself')]
])


@app.on_message(filters.command('start') & filters.private)
async def startcmd(_, message: Message):
    user_id = message.from_user.id
    user_mention = message.from_user.mention

    if blocked.find_one({'user_id': user_id}):
        await message.reply_text("You are blocked from using this bot.")
        return

    await message.reply_text("STO", reply_markup=start_button)

@app.on_callback_query(filters.regex('fuck'))
async def help_callback(_, query: CallbackQuery):
    await query.answer("Fuck")


@app.on_callback_query(filters.regex('yourself'))
async def back_callback(_, query: CallbackQuery):
    await query.answer("Yourself")

