#!/usr/bin/env python3
"""
Startup script for Telegram Migration Bot
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.bot.config import user_client, bot_client, USER_PHONE, BOT_TOKEN
from telethon.errors import SessionPasswordNeededError

async def authenticate_and_run():
    """Authenticate user and run bot"""
    await user_client.connect()
    
    if not await user_client.is_user_authorized():
        await user_client.send_code_request(USER_PHONE)
        print(f"Code sent to {USER_PHONE}", file=sys.stderr)
        
        # Read code from file
        code_file = '/home/tr4m0ryp/.openclaw/workspace/Invite_bot_telegram/.code'
        max_wait = 300  # 5 minutes
        waited = 0
        
        while not os.path.exists(code_file) and waited < max_wait:
            await asyncio.sleep(1)
            waited += 1
        
        if not os.path.exists(code_file):
            print("Timeout waiting for code", file=sys.stderr)
            return
        
        with open(code_file, 'r') as f:
            code = f.read().strip()
        
        os.remove(code_file)
        
        try:
            await user_client.sign_in(USER_PHONE, code)
        except SessionPasswordNeededError:
            # Cloud password required
            password = 'Ben10@ben10'
            await user_client.sign_in(password=password)
    
    await bot_client.start(bot_token=BOT_TOKEN)
    print("Bot is running...", file=sys.stderr)
    
    await asyncio.gather(
        bot_client.run_until_disconnected(),
        user_client.run_until_disconnected()
    )

if __name__ == '__main__':
    asyncio.run(authenticate_and_run())
