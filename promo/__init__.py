import asyncio
import logging
import time
from pyrogram import Client, filters
from pyrogram.errors import PeerIdInvalid, ChannelInvalid, FloodWait
from pyrogram.types import BotCommand
from config import API_ID, API_HASH, BOT_TOKEN, GROUP_ID
import config

logging.basicConfig(
    format="[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s",
    level=logging.INFO,
    datefmt="%d-%b-%y %H:%M:%S",
)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
LOGGER = logging.getLogger(__name__)

apps = []

sessions = [
    config.SESSION2,
    config.SESSION3,
    config.SESSION4,
    config.SESSION5,
    config.SESSION6
]

for i, session in enumerate(sessions, start=2):
    if session:
        austin = Client(
            f"Adbot{i-1}",
            api_id=API_ID,
            api_hash=API_HASH,
            session_string=str(session),
        )
        apps.append(austin)

app = Client(
    "Lettable",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
)

boot = time.time()
async def austinOG():
    try:
        await app.start()
        await asyncio.gather(*(austin.start() for austin in apps))
        await asyncio.sleep(2)
    except FloodWait as ex:
        LOGGER.warning(ex)
        await asyncio.sleep(ex.value)

    print(1)
    try:
        await app.send_message(GROUP_ID, "Bot Started Successfully.")
        for austin in apps:
            await austin.send_message(GROUP_ID, f"{austin.me.mention} Started Successfully.")
            
        LOGGER.info(f"Bot Started As {app.me.first_name}")
    except Exception as e:
        print(e)
        exit()

asyncio.get_event_loop().run_until_complete(austinOG())
