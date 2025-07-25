import re
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton as IKB
from pyrogram.types import InlineKeyboardMarkup as IKM
from pyrogram.types import CallbackQuery, Message
from promo import app, apps
from pymongo import MongoClient
import config
from promo.modules.block import blocked

client = MongoClient(config.MONGO_DB_URI)
db = client['MAIN']

app2 = apps[1]

database = {}
pattern = re.compile(r"^[a-zA-Z0-9_]+$")

@app.on_message(filters.command('list') & filters.private)
async def start_list(_, message: Message):
    user_id = message.from_user.id

    if blocked.find_one({'user_id': message.from_user.id}):
        await message.reply_text("You are blocked from using this bot.")
        return

    if user_id not in database:
        database[user_id] = {}

    if 'list_state' not in database[user_id] or not database[user_id]['list_state']:
        database[user_id]['list_state'] = False

    if not database[user_id]['list_state']:
        keyboard = IKM([
            [IKB(text='Discord', callback_data='list_mode_discord')],
            [IKB(text='Instagram', callback_data='list_mode_instagram')],
            [IKB(text='Kick', callback_data='list_mode_kick')],
            [IKB(text='Minecraft', callback_data='list_mode_minecraft')],
            [IKB(text='Telegram', callback_data='list_mode_telegram')],
            [IKB(text='Tiktok', callback_data='list_mode_tiktok')],
            [IKB(text='Twitch', callback_data='list_mode_twitch')],
            [IKB(text='Twitter', callback_data='list_mode_twitter')],
            [IKB(text='Snapchat', callback_data='list_mode_snapchat')],
        ])
        
        await app.send_message(message.chat.id, 'Hello, which platform would you like to create a listing for?', reply_markup=keyboard)
        database[user_id]['list_state'] = True
    else:
        await message.reply_text('You already have an unprocessed request. Run /cancel to cancel your request.')

@app.on_callback_query(filters.regex(r"^list_mode_"))
async def handle_list_mode(_, query: CallbackQuery):
    user_id = query.from_user.id
    mode = query.data.split("_")[2]

    if user_id in database and database[user_id]['list_state']:
        database[user_id]['list_mode'] = mode

        keyboard = IKM([
            [IKB("Back", callback_data="list_back")],
            [IKB("Cancel", callback_data="list_cancel")]
        ])

        text = (
            f'**Platform**: {mode.capitalize()}\n\n'
            f'Please enter the username you will be selling'
        )

        await query.message.edit_text(text=text, reply_markup=keyboard)

@app.on_callback_query(filters.regex('list_back'))
async def go_back(_, query: CallbackQuery):
    user_id = query.from_user.id

    if user_id in database and database[user_id]['list_state']:
        keyboard = IKM([
            [IKB(text='Discord', callback_data='list_mode_discord')],
            [IKB(text='Instagram', callback_data='list_mode_instagram')],
            [IKB(text='Kick', callback_data='list_mode_kick')],
            [IKB(text='Minecraft', callback_data='list_mode_minecraft')],
            [IKB(text='Telegram', callback_data='list_mode_telegram')],
            [IKB(text='Tiktok', callback_data='list_mode_tiktok')],
            [IKB(text='Twitch', callback_data='list_mode_twitch')],
            [IKB(text='Twitter', callback_data='list_mode_twitter')],
            [IKB(text='Snapchat', callback_data='list_mode_snapchat')],
        ])

        await query.message.edit_text('Which platform would you like to create a listing for?', reply_markup=keyboard)
        database[user_id].pop('list_mode', None)

@app.on_message(filters.text & filters.private)
async def get_user_input(_, message: Message):
    user_id = message.from_user.id

    if user_id in database and database[user_id]['list_state']:
        if message.text.lower() == '/cancel':
            database[user_id]['list_state'] = False
            database[user_id].pop('list_mode', None)
            database[user_id].pop('list_username', None)
            database[user_id].pop('list_price', None)
            database[user_id].pop('list_additional', None)
            await message.reply_text("Your request has been canceled.")
            return

        if 'list_mode' in database[user_id] and 'list_username' not in database[user_id]:
            username = message.text

            if pattern.match(username):
                database[user_id]['list_username'] = username

                keyboard = IKM([[IKB(text='Cancel', callback_data='list_cancel')]])

                text = (
                    f'**Platform**: {database[user_id]["list_mode"].capitalize()}\n'
                    f'**Username**: {database[user_id]["list_username"]}\n\n'
                    f'Please enter the price of this listing'
                )

                await app.send_message(message.chat.id, text=text, reply_markup=keyboard)
            else:
                await message.reply_text("Username is invalid. Please provide a valid username containing only letters, digits, and underscores (_).")
        elif 'list_username' in database[user_id] and 'list_price' not in database[user_id]:
            try:
                database[user_id]['list_price'] = float(message.text)
            except ValueError:
                await message.reply_text("Please enter a valid price.")
                return

            keyboard = IKM([[IKB(text='Cancel', callback_data='list_cancel')]])

            text = (
                f'**Platform**: {database[user_id]["list_mode"].capitalize()}\n'
                f'**Username**: {database[user_id]["list_username"]}\n'
                f'**Price**: {database[user_id]["list_price"]}\n\n'
                f'Please enter any additional info for this listing (256 characters maximum)'
            )

            await app.send_message(message.chat.id, text=text, reply_markup=keyboard)
        elif 'list_price' in database[user_id] and 'list_additional' not in database[user_id]:
            additional_info = message.text
            if len(additional_info) > 256:
                await message.reply_text("Additional info is too long. Please limit it to 256 characters.")
                return

            database[user_id]['list_additional'] = additional_info

            keyboard = IKM([
                [IKB(text='Process', callback_data='list_process')],
                [IKB(text='Cancel', callback_data='list_cancel')]
            ])

            text = (
                f'**Platform**: {database[user_id]["list_mode"].capitalize()}\n'
                f'**Username**: {database[user_id]["list_username"]}\n'
                f'**Price**: {database[user_id]["list_price"]}\n'
                f'**Additional Info**: {database[user_id]["list_additional"]}\n\n'
                f'Click **Process** below to send your application.\n\n'
                f'Ensure you have the `Forwarded Messages` privacy setting set to `Everybody`, otherwise your listing will automatically be rejected.'
            )

            await app.send_message(message.chat.id, text=text, reply_markup=keyboard)

@app.on_callback_query(filters.regex('list_process'))
async def process_listing(_, query: CallbackQuery):
    user_id = query.from_user.id

    if user_id in database and 'list_mode' in database[user_id]:
        mode = database[user_id]['list_mode']
        username = database[user_id]['list_username']
        price = database[user_id]['list_price']
        additional = database[user_id]['list_additional']

        text = (
            f"Username: {username}\n"
            f"BIN: ${price}\n"
            f"Additional Info: `{additional}`\n"
        )

        group = await app2.get_chat(config.MARKETPLACE_ID)
        async for topic in app2.get_forum_topics(config.MARKETPLACE_ID):
            if mode.lower() in topic.title.lower():
                keyboard = IKM([[IKB(text='Contact Owner', user_id=user_id)]])

                message = await app.send_message(config.MARKETPLACE_ID, text=text, message_thread_id=topic.id, reply_markup=keyboard)
                
                link = f"https://t.me/{group.username}/{message.message_thread_id}/{message.id}"
                await query.answer('Your ad has been listed', show_alert=True)
                keyboard = IKM([[IKB(text='View Listing', url=link)]])

                await app.send_message(user_id, "Your ad has been listed successfully!", reply_markup=keyboard)

                database[user_id]['list_state'] = False
                database[user_id].pop('list_mode', None)
                database[user_id].pop('list_username', None)
                database[user_id].pop('list_price', None)
                database[user_id].pop('list_additional', None)
                return
    else:
        await query.answer('Please choose a platform and try again.', show_alert=True)

@app.on_callback_query(filters.regex('list_cancel'))
async def cancel_listing(_, query: CallbackQuery):
    user_id = query.from_user.id

    if user_id in database:
        if database[user_id]['list_state']:
            database[user_id]['list_state'] = False
            database[user_id].pop('list_mode', None)
            database[user_id].pop('list_username', None)
            database[user_id].pop('list_price', None)
            database[user_id].pop('list_additional', None)
            await query.message.edit_text("Your request has been canceled.")
        else:
            await query.message.edit_text("No process is currently running. Use /list to start a new request.")

@app.on_message(filters.command('cancel') & filters.private)
async def cancel_command(_, message: Message):
    user_id = message.from_user.id

    if user_id in database:
        if database[user_id].get('list_state', False):
            database[user_id]['list_state'] = False
            database[user_id].pop('list_mode', None)
            database[user_id].pop('list_username', None)
            database[user_id].pop('list_price', None)
            database[user_id].pop('list_additional', None)
            await message.reply_text("Your request has been canceled.")
        else:
            await message.reply_text("No process is currently running. Use /list to start a new request.")
