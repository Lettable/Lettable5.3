from os import getenv

API_ID = int(getenv("API_ID", 23129036))
API_HASH = str(getenv("API_HASH", "34efb38c74d5e6b25d1bb6234396a8af"))
BOT_TOKEN = str(getenv("BOT_TOKEN", "7574524787:AAED5TK7Og0G9ybHEoXgBIYvVx6OsPU08Xc"))

MONGO_DB_URI = str(getenv("MONGO_DB_URI", "mongodb+srv://admin:24iS6oZKPi2Yxp6I@cluster0.xqwygl3.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"))