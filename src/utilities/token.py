from dotenv import load_dotenv
import os

load_dotenv()

def get_token():
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise ValueError("BOT_TOKEN is not set in .env")
    return token