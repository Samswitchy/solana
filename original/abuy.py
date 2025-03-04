import re
import requests
import json
import asyncio
import logging  
import sqlite3
from telethon import TelegramClient, events

# ✅ Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# ✅ Your Telegram API Credentials
API_ID = "19780264"
API_HASH = "cbb43586ab6e93107ac5cc6fd741c869"
PHONE_NUMBER = "+2348116267294"
CHANNEL_USERNAME = "pfultimate"  # Replace with your actual channel username

# ✅ Initialize the Telegram Client
client = TelegramClient("telegrams_session", API_ID, API_HASH)


# ✅ Database Setup
def init_db():
    """Initialize the database and create table if it doesn't exist."""
    conn = sqlite3.connect("token.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            token_name TEXT,
            token_address TEXT UNIQUE,
            twitter_link TEXT
        )
    """)
    conn.commit()
    conn.close()


def save_to_db(token_name, token_address, twitter_link):
    """Saves extracted data to the database."""
    conn = sqlite3.connect("token.db")
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT OR IGNORE INTO tokens (token_name, token_address, twitter_link) 
            VALUES (?, ?, ?)
        """, (token_name, token_address, twitter_link))
        conn.commit()
        logger.info(f"✅ Saved to DB: {token_name} - {token_address} - {twitter_link}")
    except Exception as e:
        logger.error(f"❌ Database Error: {e}")
    finally:
        conn.close()


# ✅ Extract Token Address from Message
def extract_token_address(message_text):
    match = re.search(r'([A-HJ-NP-Za-km-z1-9]{32,44})', message_text)
    return match.group(1) if match else None


# ✅ Extract Token Name from Message
def extract_token_name(message_text):
    """Extracts the token name from a Telegram message."""
    match = re.search(r'\[([\w\s\-()]+)\]', message_text)  # Extracts text inside first square brackets
    return match.group(1) if match else None


# ✅ Extract Twitter (𝕏) Link from Message
def extract_x_link(message_text):
    x_pattern = r'\[𝕏\]\((https:\/\/x\.com\/[^\)]+)\)'  
    match = re.search(x_pattern, message_text)
    return match.group(1) if match else None


# ✅ Process Incoming Messages
async def process_message(message_text):
    try:
        token_name = extract_token_name(message_text)
        token_address = extract_token_address(message_text)
        twitter_link = extract_x_link(message_text)

        if token_address:
            logger.info(f"✅ Extracted Token: {token_name} - {token_address}")
        else:
            logger.warning("❌ No token address extracted.")

        if twitter_link:
            logger.info(f"✅ Extracted X Link: {twitter_link}")
        else:
            logger.warning("❌ No Twitter link found.")

        # ✅ Save extracted data to the database
        if token_address:
            save_to_db(token_name, token_address, twitter_link)

    except Exception as e:
        logger.error(f"❌ Error in process_message: {e}")


# ✅ Handle New Messages from Telegram Channel
@client.on(events.NewMessage(chats=CHANNEL_USERNAME))
async def handle_new_message(event):
    """Handles new messages from the Telegram channel."""
    try:
        asyncio.create_task(process_message(event.message.text))  
    except Exception as e:
        logger.error(f"❌ Error processing message: {e}")


# ✅ Run Telegram Client
async def run_telegram_client():
    try:
        logger.info("🚀 Connecting to Telegram...")
        await client.start(PHONE_NUMBER)  # ✅ Removed PHONE_NUMBER, not needed
        logger.info("🟢 Connected")
        logger.info("📩 Client is running. Waiting for new messages...")
        await client.run_until_disconnected()
    except Exception as e:
        logger.error(f"❌ Error: {e}. Reconnecting...")


# ✅ Main Function
async def main():
    init_db()  # Ensure database is set up before starting
    await run_telegram_client()


if __name__ == "__main__":
    asyncio.run(main())
