#!/usr/bin/env python3
"""
 * @file    migration.py
 * @brief   Member migration logic
 * @author  tr4m0ryp
 * @date    2026-01-31
 * @version 1.0.0
 * @copyright MIT License
 * 
 * @repository https://github.com/tr4m0ryp/Invite_bot_telegram
 * @license MIT
"""

import time
from datetime import timedelta

from telethon.tl.types import InputPeerChannel, InputPeerUser
from telethon.tl.functions.channels import InviteToChannelRequest
from telethon.errors.rpcerrorlist import PeerFloodError, UserPrivacyRestrictedError

from src.bot.config import user_client, user_state


async def migrate_members(event, sender_id):
    """
    @brief Execute the member migration process
    
    @param event The callback query event
    @param sender_id The user ID initiating the migration
    """
    source = user_state[sender_id].get('source')
    target = user_state[sender_id].get('target')
    
    if not source or not target:
        await event.respond("Error: Source or target group not selected.")
        return
    
    try:
        progress_msg = await event.respond(f"Scraping members from {source.title}...")
        members = await user_client.get_participants(source, aggressive=True)
        total_members = len(members)
        await progress_msg.edit(
            f"Found {total_members} members in {source.title}.\n"
            f"Starting migration to {target.title}..."
        )
    except Exception as e:
        await event.respond(f"Error during scraping: {e}")
        return
    
    target_entity = InputPeerChannel(target.id, target.access_hash)
    error_count = 0
    success_count = 0
    bot_count = 0
    start_time = time.time()
    
    progress = await event.respond(format_progress(0, total_members, 0, 0, 0, "00:00:00", "calculating..."))
    
    for idx, member in enumerate(members, start=1):
        if getattr(member, 'bot', False):
            bot_count += 1
        else:
            try:
                user_to_add = InputPeerUser(member.id, member.access_hash)
                await user_client(InviteToChannelRequest(target_entity, [user_to_add]))
                success_count += 1
            except PeerFloodError:
                await event.respond("Flood error: Too many requests. Stopping.")
                break
            except UserPrivacyRestrictedError:
                error_count += 1
            except Exception as e:
                error_count += 1
                if error_count > 10:
                    await event.respond("Too many errors. Migration stopped.")
                    break
        
        elapsed_str, eta_str = calculate_time(start_time, idx, total_members)
        progress_text = format_progress(
            idx, total_members, success_count, error_count, bot_count,
            elapsed_str, eta_str
        )
        
        try:
            await progress.edit(progress_text)
        except:
            pass
        
        await asyncio.sleep(10)
    
    final_elapsed = str(timedelta(seconds=int(time.time() - start_time)))
    await progress.edit(
        f"Migration completed!\n\n"
        f"Total: {total_members}\n"
        f"Added: {success_count}\n"
        f"Errors: {error_count}\n"
        f"Bots skipped: {bot_count}\n"
        f"Time: {final_elapsed}"
    )


def format_progress(processed, total, success, errors, bots, elapsed, eta):
    """@brief Format progress message"""
    return (
        "Migration progress:\n"
        f"Processed: {processed}/{total}\n"
        f"Successfully added: {success}\n"
        f"Errors: {errors}\n"
        f"Bots: {bots}\n"
        f"Elapsed: {elapsed}\n"
        f"ETA: {eta}"
    )


def calculate_time(start_time, current_idx, total):
    """@brief Calculate elapsed time and ETA"""
    import asyncio
    elapsed = time.time() - start_time
    avg_time = elapsed / current_idx
    eta = avg_time * (total - current_idx)
    elapsed_str = str(timedelta(seconds=int(elapsed)))
    eta_str = str(timedelta(seconds=int(eta)))
    return elapsed_str, eta_str
