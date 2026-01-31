#!/usr/bin/env python3
"""
 * @file    main.py
 * @brief   Telegram Migration Bot - Main entry point
 * @author  tr4m0ryp
 * @date    2026-01-31
 * @version 1.0.0
 * @copyright MIT License
 * 
 * @details Entry point for the Telegram Migration Bot.
 *          Initializes clients and starts the event loop.
 * 
 * @repository https://github.com/tr4m0ryp/Invite_bot_telegram
 * @license MIT
"""

import asyncio
import getpass

from telethon.errors import SessionPasswordNeededError

from src.bot.config import user_client, bot_client, USER_PHONE, BOT_TOKEN
from src.bot import handlers  # noqa: F401 - registers handlers


async def main():
    """
    @brief Main entry point
    
    @details Connects user and bot clients, handles authentication,
             and starts the event loop.
    """
    await user_client.connect()
    if not await user_client.is_user_authorized():
        await user_client.send_code_request(USER_PHONE)
        try:
            code = input("Enter the code for user login: ")
            await user_client.sign_in(USER_PHONE, code)
        except SessionPasswordNeededError:
            password = getpass.getpass("User password: ")
            await user_client.sign_in(password=password)
    
    await bot_client.start(bot_token=BOT_TOKEN)
    print("Both clients connected. Bot is running...")
    
    await asyncio.gather(
        bot_client.run_until_disconnected(),
        user_client.run_until_disconnected()
    )


if __name__ == '__main__':
    asyncio.run(main())
