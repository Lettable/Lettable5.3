from motor.motor_asyncio import AsyncIOMotorClient
import config

client = AsyncIOMotorClient(config.MONGO_DB_URI)
db = client['MAIN']
blocked = db['blocked']
userscollection = db['users']
sudo_users = db["sudo_users"]