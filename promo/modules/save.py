from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from pyrogram.errors import FloodWait
from promo import app, apps
from pyrogram.enums import ChatType
from promo.modules.sudo import sudo_users, is_sudo
from promo.modules.usernames import usernames
from pymongo import MongoClient
import asyncio
import config
import random
import pytz
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from promo.modules.block import blocked

client = MongoClient(config.MONGO_DB_URI)
db = client['MAIN']
users_collection = db['users']
forwarded = db['forwarded']

words = {
    "telegram": ["telegram", "tg", "tele", "Telegram", "wire", "cable", "cablegram", "letter telegram", "night letter", "overseas telegram"],
    "instagram": ["instagram", "ig", "meta", "metaverse", "facebook"],
    "other": ["other", "services", "Tiktok", "tiktok", "whatsapp", "wp", "yt", "youtube", "usernames", "facebook", "meta", "usernames", "market", "market place", "markets"],
    "exchange": ["crypto", "exchange", "money", "deals", "exchanges", "crypto", "forex", "trading"]
}

tasks = {}
savedb = {}
sendedFunc = {}
app_shuffled_lists = {}

@app.on_message(filters.command("save") & filters.group)
async def saveFuncs(_, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    if blocked.find_one({'user_id': message.from_user.id}):
        await message.reply_text("You are blocked from using this bot.")
        return

    if not await is_sudo(user_id):
        await message.reply_text("You're not a sudo user.")
        return

    if message.from_user.username:
        log_message = f"#save: Used in @{message.chat.username} by @{message.from_user.username}."
    else:
        log_message = f"#save: Used in @{message.chat.username} by {message.from_user.first_name}."
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(f'{message.from_user.first_name}', user_id=f'{message.from_user.id}')]])
    await app.send_message(config.LOGS_CHANNEL_ID, log_message, reply_markup=keyboard)

    if message.chat.type == ChatType.SUPERGROUP:
        if message.reply_to_message:
            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("Telegram", callback_data="mode_telegram"),
                    InlineKeyboardButton("Instagram", callback_data="mode_instagram")
                ],
                [
                    InlineKeyboardButton("Others", callback_data="mode_other"),
                    InlineKeyboardButton("Exchange", callback_data="mode_exchange")
                ],
                [
                    InlineKeyboardButton("Close", callback_data="closetf")
                ]
            ])
            await message.reply_text(
                "Choose what is your ad about:",
                reply_markup=keyboard
            )
            if chat_id not in savedb:
                savedb[chat_id] = {}
            savedb[chat_id][user_id] = {"user": message.from_user.id, "message": message.reply_to_message.id, "mode": None}
        else:
            await message.reply_text("You need to reply to a message to use this command.", disable_web_page_preview=True)
    else:
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(f'guide', url=config.GROUP_LINK)]])
        await message.reply_text("This command is for groups only.", reply_markup=keyboard)

@app.on_callback_query(filters.regex("closetf"))
async def closeTF(_, q: CallbackQuery):
    await q.message.delete()

@app.on_callback_query(filters.regex(r"mode_telegram|mode_instagram|mode_other|mode_exchange"))
async def modeSelection(_, query: CallbackQuery):
    global savedb
    mode = query.data.split("_")[1]
    chat_id = query.message.chat.id
    user_id = query.from_user.id

    if chat_id not in savedb or user_id not in savedb[chat_id]:
        savedb[chat_id] = {user_id: {"user": query.from_user.id}}

    savedb[chat_id][user_id]["mode"] = mode

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Start", callback_data="hnn_process"), InlineKeyboardButton("Stop", callback_data="noo_process")],
        [InlineKeyboardButton("Back", callback_data="go_back")]
    ])

    await query.message.edit_text(
        f"Broadcast mode selected: {mode.capitalize()}",
        reply_markup=keyboard
    )

@app.on_callback_query(filters.regex("go_back"))
async def goBack(_, q: CallbackQuery):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Telegram", callback_data="mode_telegram"),
         InlineKeyboardButton("Instagram", callback_data="mode_instagram")],
        [InlineKeyboardButton("Others", callback_data="mode_other"),
         InlineKeyboardButton("Exchange", callback_data="mode_exchange")],
        [InlineKeyboardButton("Close", callback_data="closetf")]
    ])
    await q.message.edit_text(
        f"Choose the mode of your broadcast:",
        reply_markup=keyboard
    )

@app.on_callback_query(filters.regex("hnn_process"))
async def startProcessFunc(_, query: CallbackQuery):
    chat_id = query.message.chat.id
    user_id = query.from_user.id

    if user_id in sendedFunc and sendedFunc[user_id].get(chat_id):
        await query.answer("Process is already running.", show_alert=True)
        return

    user = users_collection.find_one({"user_id": user_id})
    if not user:
        users_collection.insert_one({"user_id": user_id, "credits": 5})
        remaining = 5
    else:
        remaining = user.get("credits", 5)

    if remaining <= 0:
        await query.answer("You have run out of credits. Please come back tomorrow.", show_alert=True)
        return

    remaining -= 1
    users_collection.update_one({"user_id": user_id}, {"$set": {"credits": remaining}})

    if savedb.get(chat_id) and savedb[chat_id].get(user_id) and savedb[chat_id][user_id]["user"] == user_id:
        sendedFunc.setdefault(user_id, {})[chat_id] = True
        for appint in apps:
            app_shuffled_lists[appint] = usernames[:]
            random.shuffle(app_shuffled_lists[appint])
            tasks[user_id] = {
                chat_id: [
                    asyncio.create_task(sendOrForwardMessages(appint, chat_id, user_id, app_shuffled_lists[appint]))
                ]
            }
        await query.answer(f"Process started. You have {remaining} credits remaining.", show_alert=True)
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(f'{query.from_user.first_name}', user_id=f'{query.from_user.id}')]])
        await app.send_message(config.LOGS_CHANNEL_ID, f'#start : Process started by {query.from_user.first_name}.', reply_markup=keyboard)
    else:
        await query.answer("You haven't saved any message yet.", show_alert=True)



@app.on_callback_query(filters.regex("noo_process"))
async def stopProcessFunc(_, query: CallbackQuery):
    chat_id = query.message.chat.id
    user_id = query.from_user.id
    if user_id in sendedFunc and sendedFunc[user_id].get(chat_id):
        for task in tasks.get(user_id, {}).get(chat_id, []):
            task.cancel()
        del tasks[user_id][chat_id]
        sendedFunc[user_id][chat_id] = False
        await query.answer("Process stopped.", show_alert=True)
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(f'{query.from_user.first_name}', user_id=f'{query.from_user.id}')]])
        await app.send_message(config.LOGS_CHANNEL_ID, f'#stop : Process stopped by {query.from_user.first_name}.', reply_markup=keyboard)
    else:
        await query.answer("Process is not running.", show_alert=True)


async def sendOrForwardMessages(appint, chat_id, user_id, sufflelist):
    global savedb, sendedFunc
    while sendedFunc.get(user_id, {}).get(chat_id):
        for username in sufflelist:
            try:
                await appint.join_chat(f'{username}')
                group = await appint.get_chat(f'{username}')
            except Exception as e:
                await app.send_message(config.ERROR_CHANNEL_ID, f"Error fetching chat @{username}: `{str(e)}`")
                continue

            if chat_id in savedb and user_id in savedb[chat_id] and savedb[chat_id][user_id].get("mode"):
                mode = savedb[chat_id][user_id]["mode"]
                if mode in words:
                    try:
                        if group.is_forum:
                            found = False
                            async for forum in appint.get_forum_topics(f'{username}'):
                                forumlower = forum.title.lower()
                                if any(keyword in forumlower for keyword in words[mode]):
                                    msg = await appint.forward_messages(group.id, from_chat_id=chat_id, message_ids=savedb[chat_id][user_id]["message"], message_thread_id=forum.id)
                                    await asyncio.sleep(3)
                                    if group.username:
                                        link = f"https://t.me/{group.username}/{msg.message_thread_id}/{msg.id}"
                                    else:
                                        link = f"https://t.me/c/{str(group.id)[4:]}/{msg.message_thread_id}/{msg.id}"
                                    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(f'{group.title}', url=f'{link}')]])
                                    await app.send_message(config.LOGS_CHANNEL_ID, f"forwarded in forum with @{appint.me.username}", reply_markup=keyboard)
                                    
                                    for_doc = forwarded.find_one({'user_id': user_id})
                                    if for_doc:
                                        count = for_doc['count'] + 1
                                        forwarded.update_one({'user_id': user_id}, {'$set': {'count': count}})
                                    else:
                                        forwarded.insert_one({'user_id': user_id, 'count': 1})
                                    
                                    await asyncio.sleep(config.TIME_DIFF)
                                    found = True
                                    break
                            if not found:
                                await app.send_message(config.ERROR_CHANNEL_ID, f"No forum found for mode `{mode}` in @{group.username}")
                                await asyncio.sleep(3)
                        else:
                            msg = await appint.forward_messages(group.id, from_chat_id=chat_id, message_ids=savedb[chat_id][user_id]["message"])
                            await asyncio.sleep(3)
                            if group.username:
                                link = f"https://t.me/{group.username}/{msg.id}"
                            else:
                                link = f"https://t.me/c/{str(group.id)[4:]}/{msg.id}"
                            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(f'{group.title}', url=f'{link}')]])
                            await app.send_message(config.LOGS_CHANNEL_ID, f"forwarded in group with @{appint.me.username}", reply_markup=keyboard)

                            for_doc = forwarded.find_one({'user_id': user_id})
                            if for_doc:
                                count = for_doc['count'] + 1
                                forwarded.update_one({'user_id': user_id}, {'$set': {'count': count}})
                            else:
                                forwarded.insert_one({'user_id': user_id, 'count': 1})
                            
                            await asyncio.sleep(300)
                    except Exception as e:
                        continue
                else:
                    await asyncio.sleep(3)
                    continue
            else:
                await asyncio.sleep(3)
                continue

@app.on_message(filters.command('state'))
async def state(_, m: Message):
    await m.reply_text('Change the state by using these following buttons.\nMake sure you have used /save before using this command.', reply_markup=buttons)

@app.on_message(filters.command('invite') & filters.group)
async def inviteAss(_, message: Message):
    user_id = message.from_user.id
    
    if blocked.find_one({'user_id': message.from_user.id}):
        await message.reply_text("You are blocked from using this bot.")
        return

    if not await is_sudo(user_id):
        await message.reply_text("You're not a sudo user.")
        return
        
    if message.chat.type == ChatType.SUPERGROUP:
        try:
            link = await app.export_chat_invite_link(message.chat.id)
            for appint in apps:
                try:
                    await appint.join_chat(link)
                    await asyncio.sleep(1.5)
                except Exception as e:
                    await message.reply(f"Error joining chat with {appint.name}: {e}")
            await message.reply("Assistants joined successfully.")
        except Exception as e:
            await message.reply(f"Error inviting assistant, ask owner to add manually.\n\n{str(e)}")



async def resetcred():
    while True:
        now = datetime.utcnow()
        next_midnight = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        wait_time = (next_midnight - now).total_seconds()
        await asyncio.sleep(wait_time)
        users_collection.update_many({}, {"$set": {"credits": 5}})
        msg = await app.send_message(config.GROUP_ID, "Credits for all users have been reset.")
        await app.pin_chat_message(message.chat.id, msg.id)

asyncio.ensure_future(resetcred())
