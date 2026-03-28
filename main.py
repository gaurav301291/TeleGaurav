import os
import asyncio
from aiohttp import web
from pyrogram import Client, filters
from pytgcalls import PyTgCalls
from dotenv import load_dotenv

# Load environment variables for local testing 
# (Render will automatically use the ones you set in their dashboard)
load_dotenv()

# --- 1. Connection for Bot Token and Variables ---
# Pulling the exact mandatory variables required by the TelecastBot repo
API_ID = os.environ.get("API_ID")
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
SESSION_STRING = os.environ.get("SESSION_STRING")
CHAT = os.environ.get("CHAT")
PORT = os.environ.get("PORT", "8080")  # Render assigns this dynamically

# Safety check
if not all([API_ID, API_HASH, BOT_TOKEN, SESSION_STRING, CHAT]):
    print("WARNING: Missing one or more mandatory environment variables. Check Render settings!")

# --- 2. Initialize the Clients ---
# The Bot Client
app = Client(
    "TelecastBot",
    api_id=int(API_ID) if API_ID else 0,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# The User Session Client (Needed to actually join voice chats)
user_app = Client(
    "TelecastUser",
    api_id=int(API_ID) if API_ID else 0,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)
call_py = PyTgCalls(user_app)

@app.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply_text("TelecastBot is alive and streaming from Render! 🚀")

# --- 3. Render Web Server (Prevents Crash) ---
async def handle_health_check(request):
    return web.Response(text="Bot is running successfully!")

async def start_web_server():
    server = web.Application()
    server.router.add_get("/", handle_health_check)
    runner = web.AppRunner(server)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(PORT))
    await site.start()
    print(f"Web server listening on port {PORT} for Render health checks.")

# --- 4. Main Execution Loop ---
async def main():
    # Start the web server to satisfy Render
    await start_web_server()
    
    # Start the Pyrogram Bot client
    print("Starting Telegram Bot...")
    await app.start()
    
    # Start the User Client and PyTgCalls
    if SESSION_STRING:
        print("Starting User Client for Voice Chats...")
        await user_app.start()
        await call_py.start()
    
    print("Bot is fully operational!")
    
    # Keep the script running indefinitely
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
