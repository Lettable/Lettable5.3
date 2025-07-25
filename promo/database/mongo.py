from motor.motor_asyncio import AsyncIOMotorClient

client = AsyncIOMotorClient(config.MONGO_DB_URI)
db = client['MAIN']
blocked = db['blocked']
userscollection = db['users']