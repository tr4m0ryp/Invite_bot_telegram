#!/usr/bin/env python3
"""
 * @file    handlers.py
 * @brief   Telegram event handlers
 * @author  tr4m0ryp
 * @date    2026-01-31
 * @version 1.0.0
 * @copyright MIT License
 * 
 * @repository https://github.com/tr4m0ryp/Invite_bot_telegram
 * @license MIT
"""

import asyncio
from telethon import events, Button
from telethon.tl.types import Channel, Chat

from src.bot.config import bot_client, user_client, user_state
from src.bot.migration import migrate_members


def build_group_buttons(groups, prefix):
    """
    @brief Build inline keyboard buttons for group selection
    
    @param groups List of group/channel entities
    @param prefix Prefix for callback data
    @return List of button rows
    """
    buttons = []
    for group in groups:
        buttons.append(Button.inline(group.title, f"{prefix}_{group.id}".encode()))
    return [buttons[i:i+2] for i in range(0, len(buttons), 2)]


@bot_client.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    """@brief Handle /start command"""
    user_state[event.sender_id] = {}
    await event.respond(
        "Welcome to the Telegram Migration Bot made by @tr4m0ryp!\n\n"
        "This bot helps you migrate users from one group to another.\n"
        "Make sure your user account (logged in by phone) can invite users.\n"
        "Click the button below to start migration or type /help for more info.",
        buttons=[Button.inline("Start Migration", b"init_migration")]
    )


@bot_client.on(events.NewMessage(pattern='/help'))
async def help_handler(event):
    """@brief Handle /help command"""
    help_text = (
        "Telegram Migration Bot - Help\n\n"
        "1. Start the bot with /start.\n"
        "2. Click Start Migration to begin.\n"
        "3. Select source group (where to collect users from).\n"
        "4. Select target group (where to add users).\n"
        "5. The bot will start migration and show progress.\n\n"
        "Note: Uses user account for invites to avoid API restrictions."
    )
    await event.respond(help_text)


@bot_client.on(events.CallbackQuery)
async def callback_handler(event):
    """@brief Handle callback queries from inline buttons"""
    sender_id = event.sender_id
    data = event.data.decode('utf-8')
    
    if data == "init_migration":
        await handle_init_migration(event, sender_id)
    elif data.startswith("source_"):
        await handle_source_selection(event, sender_id, data)
    elif data.startswith("target_"):
        await handle_target_selection(event, sender_id, data)
    elif data == "start_migration":
        await event.edit("Migration is starting. Please wait...")
        asyncio.create_task(migrate_members(event, sender_id))


async def handle_init_migration(event, sender_id):
    """@brief Show source group selection"""
    dialogs = await user_client.get_dialogs()
    groups = [d.entity for d in dialogs if isinstance(d.entity, (Channel, Chat)) and hasattr(d.entity, 'title')]
    
    if not groups:
        await event.edit("No groups or channels found in your account.")
        return
    
    user_state[sender_id]['all_groups'] = {str(g.id): g for g in groups}
    buttons = build_group_buttons(groups, "source")
    await event.edit("Select the source group:", buttons=buttons)


async def handle_source_selection(event, sender_id, data):
    """@brief Handle source group selection"""
    group_id = data.split("_", 1)[1]
    all_groups = user_state[sender_id].get('all_groups', {})
    source_group = all_groups.get(group_id)
    
    if not source_group:
        await event.answer("Source group not found.", alert=True)
        return
    
    user_state[sender_id]['source'] = source_group
    remaining_groups = [g for gid, g in all_groups.items() if gid != group_id]
    
    if not remaining_groups:
        await event.edit("No other groups available as target.")
        return
    
    buttons = build_group_buttons(remaining_groups, "target")
    await event.edit(
        f"Source: {source_group.title}\n\nSelect target group:",
        buttons=buttons
    )


async def handle_target_selection(event, sender_id, data):
    """@brief Handle target group selection"""
    group_id = data.split("_", 1)[1]
    all_groups = user_state[sender_id].get('all_groups', {})
    target_group = all_groups.get(group_id)
    
    if not target_group:
        await event.answer("Target group not found.", alert=True)
        return
    
    user_state[sender_id]['target'] = target_group
    await event.edit(
        f"Target: {target_group.title}\n\nClick to start migration:",
        buttons=[Button.inline("Start Migration", b"start_migration")]
    )
