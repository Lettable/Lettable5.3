from pyrogram import filters
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
import config
from promo.database import blocked, userscollection
from promo.utils.usernames import usernames

user_temp_data = {}

start_button = InlineKeyboardMarkup([
    [InlineKeyboardButton(text='Get Started', callback_data='get_started')],
    [InlineKeyboardButton(text='Help', callback_data='help_cb'),
     InlineKeyboardButton(text='Owner', user_id=config.OWNER_ID)]
])

@app.on_message(filters.command('start') & filters.private)
async def startcmd(_, message: Message):
    user_id = message.from_user.id
    user_mention = message.from_user.mention

    if await blocked.find_one({'user_id': user_id}):
        await message.reply_text("You are await blocked from using this bot.")
        return

    user_data = await userscollection.find_one({"user_id": user_id})
    is_new_user = user_data is None or user_data.get("new", True)

    if not is_new_user:
        button = InlineKeyboardMarkup([
    [InlineKeyboardButton(text='Chat', url='https://t.me/kojihub')],
    [InlineKeyboardButton(text='Help', callback_data='help_cb'),
     InlineKeyboardButton(text='Owner', user_id=config.OWNER_ID)]
])
    else:
        button = start_button

    await message.reply_photo(
        'https://graph.org/file/fe58c2b9f373490d1850e.png',
        caption=f"Hey {user_mention}, I'm {app.me.mention}!\n\n"
                f"➻ Elevate your telegram business with my incredible features.\n"
                f"──────────────────\n"
                f"๏ Click the help button to discover more about this rental bot for promotion purposes.",
        reply_markup=button
    )

    await userscollection.update_one(
        {"user_id": user_id},
        {"$setOnInsert": {"user_id": user_id, "new": True}},
        upsert=True
    )


@app.on_callback_query(filters.regex('get_started'))
async def get_started_cb(_, query: CallbackQuery):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Yes", callback_data="has_chats_yes"),
         InlineKeyboardButton("No", callback_data="has_chats_no")]
    ])
    
    await query.edit_message_text(
        text="Do you have Telegram chats/channels you'd like to advertise in?",
        reply_markup=keyboard
    )


@app.on_callback_query(filters.regex('has_chats_(yes|no)'))
async def handle_chats_choice(_, query: CallbackQuery):
    user_id = query.from_user.id
    choice = query.matches[0].group(1)
    
    if choice == "yes":
        await query.edit_message_text(
            "Alright! Send me a TXT file containing chat links.\n\n"
            "Format requirements:\n"
            "- Each username must start with @\n"
            "- Separate usernames with new lines\n"
            "- No duplicate usernames allowed\n\n"
            "Example:\n"
            "@username1\n"
            "@username2\n"
            "@username3"
        )
        user_temp_data[user_id] = {"state": "awaiting_file"}
    else:
        user_temp_data[user_id] = {
            "state": "confirmation",
            "chats": username
        }
        await show_confirmation(query, len(username))


async def show_confirmation(query, count):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Confirm", callback_data="confirm_chats"),
         InlineKeyboardButton("Back", callback_data="has_chats_back")]
    ])
    await query.edit_message_text(
        f"We've loaded {count} chats.\n\n"
        "Please confirm to save these chats to your account.",
        reply_markup=keyboard
    )


@app.on_message(filters.document & filters.private)
async def handle_chats_file(_, message: Message):
    user_id = message.from_user.id
    user_state = user_temp_data.get(user_id, {}).get("state")
    
    if user_state != "awaiting_file":
        return
    
    if not message.document.file_name.endswith(".txt"):
        await message.reply("Please send a valid TXT file.")
        return
    
    file = await message.download()
    
    try:
        with open(file, 'r') as f:
            content = f.read()
        
        raw_usernames = []
        duplicates = set()
        unique_usernames = set()
        
        for line in content.splitlines():
            line = line.strip()
            if line.startswith("@"):
                if line.lower() in unique_usernames:
                    duplicates.add(line.lower())
                else:
                    unique_usernames.add(line.lower())
                    raw_usernames.append(line)
        
        if duplicates:
            dup_message = "Found duplicate usernames:\n"
            dup_message += "\n".join(f"- {d}" for d in duplicates)
            dup_message += "\n\nPlease fix these duplicates and resend the file."
            await message.reply(dup_message)
            return
        
        if not raw_usernames:
            await message.reply("No valid usernames found in the file. Please check the format.")
            return
        
        user_temp_data[user_id] = {
            "state": "confirmation",
            "chats": raw_usernames
        }
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Confirm", callback_data="confirm_chats"),
             InlineKeyboardButton("Back", callback_data="has_chats_back")]
        ])
        await message.reply(
            f"Found {len(raw_usernames)} valid and unique chats.\n\n"
            "Please confirm to save these chats to your account.",
            reply_markup=keyboard
        )
    
    except Exception as e:
        await message.reply(f"Error processing file: {str(e)}")
    finally:
        import os
        if os.path.exists(file):
            os.remove(file)


@app.on_callback_query(filters.regex('confirm_chats'))
async def confirm_chats_cb(_, query: CallbackQuery):
    user_id = query.from_user.id
    user_data = user_temp_data.get(user_id)
    
    if not user_data or user_data["state"] != "confirmation":
        await query.answer("No chat data to confirm!")
        return
    
    chats = user_data["chats"]
    await userscollection.update_one(
        {"user_id": user_id},
        {"$set": {
            "chats": chats,
            "new": False
        }}
    )
    
    if user_id in user_temp_data:
        del user_temp_data[user_id]
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Back to Start", callback_data="back_cb")]
    ])
    await query.edit_message_text(
        f"Successfully saved {len(chats)} chats to your account!",
        reply_markup=keyboard
    )


@app.on_callback_query(filters.regex('has_chats_back'))
async def back_to_start(_, query: CallbackQuery):
    user_id = query.from_user.id
    
    if user_id in user_temp_data:
        del user_temp_data[user_id]
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Yes", callback_data="has_chats_yes"),
         InlineKeyboardButton("No", callback_data="has_chats_no")]
    ])
    
    await query.edit_message_text(
        text="Do you have Telegram chats/channels you'd like to promote?",
        reply_markup=keyboard
    )


@app.on_callback_query(filters.regex('help_cb'))
async def help_callback(_, query: CallbackQuery):
    text = (
        f"Here's the help menu of {app.me.mention}\n"
        "Only the users who paid rent can use these commands.\n\n"
        "➻ /save : reply to a message you want to broadcast.\n"
        "➻ /stats : stats of the bot.\n"
        "➻ /state : to start or stop the state.\n"
        "➻ /list : list a username in marketplace.\n"
        "➻ For more details join @LettableChat."
    )

    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(text='Back', callback_data='back_cb')]
    ])

    await query.edit_message_text(
        text=text,
        reply_markup=reply_markup
    )


@app.on_callback_query(filters.regex('back_cb'))
async def back_callback(_, query: CallbackQuery):
    user_id = query.from_user.id
    user_data = await userscollection.find_one({"user_id": user_id})
    is_new_user = user_data is None or user_data.get("new", True)

    if is_new_user:
        button = start_button
    else:
        button = InlineKeyboardMarkup([
            [InlineKeyboardButton(text='Chat', url='https://t.me/kojihub')],
            [InlineKeyboardButton(text='Help', callback_data='help_cb'),
            InlineKeyboardButton(text='Owner', user_id=config.OWNER_ID)]
        ])

    text = (
        f"Hey {query.from_user.mention}, I'm {app.me.mention}!\n\n"
        "➻ Elevate your telegram business with my incredible features.\n"
        "──────────────────\n"
        "Click the help button to discover more about this rental bot"
        "for promotion purposes."
    )

    await query.edit_message_text(
        text=text,
        reply_markup=button,
        disable_web_page_preview=True
    )