#!/usr/bin/env python3
"""
 * @file    config.py
 * @brief   Configuration and client setup
 * @author  tr4m0ryp
 * @date    2026-01-31
 * @version 1.0.0
 * @copyright MIT License
 * 
 * @repository https://github.com/tr4m0ryp/Invite_bot_telegram
 * @license MIT
"""

import os
from dotenv import load_dotenv
from telethon import TelegramClient

# Load environment variables from .env file
load_dotenv()

# ============================================================================
# CONFIGURATION
# ============================================================================
API_ID = int(os.environ.get('API_ID', 0))
API_HASH = os.environ.get('API_HASH')
USER_PHONE = os.environ.get('USER_PHONE')
BOT_TOKEN = os.environ.get('BOT_TOKEN')

# ============================================================================
# CLIENTS
# ============================================================================
user_client = TelegramClient('user_session', API_ID, API_HASH)
bot_client = TelegramClient('bot_session', API_ID, API_HASH)

# ============================================================================
# STATE MANAGEMENT
# ============================================================================
user_state = {}
