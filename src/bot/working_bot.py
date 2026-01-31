#!/usr/bin/env python3
"""
Working Telegram Migration Bot
Run this directly to test: python3 working_bot.py
"""

import asyncio
import logging
from telethon import TelegramClient, events, Button
from telethon.tl.types import Channel, Chat
from telethon.tl.functions.channels import InviteToChannelRequest
from telethon.errors import FloodWaitError

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Credentials
API_ID = 25155557
API_HASH = 'e1c603972b368b326ea68730378e877b'
BOT_TOKEN = '8016881248:AAF6FuSlITftpONtqH1SSyPUBeEGiO7vbac'

# Create clients - separate sessions
user_client = TelegramClient('user_session', API_ID, API_HASH)
bot_client = TelegramClient('bot_session_new', API_ID, API_HASH)  # Fresh session

# State storage
user_state = {}

@bot_client.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    """Handle /start command"""
    logger.info(f'[RECEIVED] /start from user {event.sender_id}')
    
    user_state[event.sender_id] = {}
    
    await event.respond(
        'Welcome to the Migration Bot!\n\n'
        'I can help you migrate members from one group to another.',
        buttons=[Button.inline('Start Migration', b'init')]
    )
    
    logger.info('[SENT] Welcome message')

async def invite_individual(user_client, target_entity, members, event):
    """Fallback: Invite members one by one if batch fails"""
    failed = 0
    for member in members:
        try:
            await user_client(InviteToChannelRequest(target_entity, [member]))
            await asyncio.sleep(2)  # Short delay between individual invites
        except Exception as e:
            failed += 1
            logger.error(f'Individual invite failed for {member.id}: {e}')
    return failed


@bot_client.on(events.CallbackQuery)
async def callback_handler(event):
    """Handle button clicks"""
    user_id = event.sender_id
    data = event.data.decode()

    logger.info(f'[CALLBACK] User {user_id}: {data}')
    
    try:
        if data == 'init':
            # Get user's groups
            await event.edit('Loading your groups...')
            
            dialogs = await user_client.get_dialogs()
            groups = [
                d.entity for d in dialogs 
                if isinstance(d.entity, (Channel, Chat)) 
                and hasattr(d.entity, 'title')
            ]
            
            if not groups:
                await event.edit('No groups found in your account.')
                return
            
            # Store groups
            user_state[user_id] = {'all': {str(g.id): g for g in groups}}
            
            # Create buttons (2 per row)
            buttons = []
            for group in groups[:20]:  # Limit to 20 groups
                title = group.title[:20] + '...' if len(group.title) > 20 else group.title
                buttons.append(Button.inline(title, f"src_{group.id}".encode()))
            
            rows = [buttons[i:i+2] for i in range(0, len(buttons), 2)]
            
            await event.edit(
                'Select SOURCE group\n(from which to migrate members):',
                buttons=rows
            )
            
        elif data.startswith('src_'):
            group_id = data.split('_')[1]
            all_groups = user_state[user_id].get('all', {})
            source = all_groups.get(group_id)
            
            if not source:
                await event.answer('Group not found', alert=True)
                return
            
            user_state[user_id]['source'] = source
            
            # Show remaining groups as targets
            remaining = [g for gid, g in all_groups.items() if gid != group_id]
            buttons = [
                Button.inline(
                    (g.title[:20] + '...') if len(g.title) > 20 else g.title, 
                    f"dst_{g.id}".encode()
                ) 
                for g in remaining[:20]
            ]
            rows = [buttons[i:i+2] for i in range(0, len(buttons), 2)]
            
            await event.edit(
                f'Source: {source.title}\n\n'
                f'Now select TARGET group\n(where to add members):',
                buttons=rows
            )
            
        elif data.startswith('dst_'):
            group_id = data.split('_')[1]
            all_groups = user_state[user_id].get('all', {})
            target = all_groups.get(group_id)
            
            if not target:
                await event.answer('Group not found', alert=True)
                return
            
            user_state[user_id]['target'] = target
            source = user_state[user_id]['source']
            
            await event.edit(
                f'Migration Summary:\n\n'
                f'From: {source.title}\n'
                f'To: {target.title}\n\n'
                f'Click START to begin:',
                buttons=[Button.inline('START MIGRATION', b'go')]
            )
            
        elif data == 'go':
            await event.edit('Migration started! Please wait...')
            await event.respond(
                'Processing members...\n'
                'This may take several minutes.\n\n'
                'You will receive updates on progress.'
            )
            
            # Get source and target
            source = user_state[user_id].get('source')
            target = user_state[user_id].get('target')
            
            if not source or not target:
                await event.respond('Error: Source or target not selected.')
                return
            
            try:
                # Get members from source
                await event.respond(f'Getting members from {source.title}...')
                source_entity = await user_client.get_entity(source)
                target_entity = await user_client.get_entity(target)
                
                members = []
                async for member in user_client.iter_participants(source_entity):
                    if not member.bot and member.id != user_id:
                        members.append(member)
                
                total = len(members)
                await event.respond(f'Found {total} members to migrate.')
                
                # Add members to target with optimized rate limiting
                added = 0
                failed = 0
                consecutive_failures = 0
                MAX_CONSECUTIVE_FAILURES = 3
                DAILY_INVITE_LIMIT = 200
                BATCH_SIZE = 10  # Invite 10 users per request
                base_delay = 5   # Start with 5 second delay
                current_delay = base_delay
                
                await event.respond(
                    f'Starting migration with optimized settings:\n'
                    f'- Batch size: {BATCH_SIZE} users per request\n'
                    f'- Daily limit: {DAILY_INVITE_LIMIT}\n'
                    f'- Adaptive delay starting at {base_delay}s'
                )
                
                # Process members in batches
                for batch_start in range(0, min(len(members), DAILY_INVITE_LIMIT), BATCH_SIZE):
                    batch = members[batch_start:batch_start + BATCH_SIZE]
                    batch_end = min(batch_start + len(batch), len(members), DAILY_INVITE_LIMIT)
                    
                    try:
                        # Try to invite the batch
                        await user_client(InviteToChannelRequest(
                            target_entity,
                            batch
                        ))
                        added += len(batch)
                        consecutive_failures = 0
                        
                        # Reduce delay slightly on success (minimum 5s)
                        current_delay = max(base_delay, current_delay - 1)
                        
                        # Progress update every 5 batches (50 users)
                        if (batch_start // BATCH_SIZE) % 5 == 0:
                            await event.respond(
                                f'Progress: {batch_end}/{total} ({added} added, {failed} failed)\n'
                                f'Current delay: {current_delay}s'
                            )
                        
                        logger.info(f'Batch added: {len(batch)} users, next delay: {current_delay}s')
                        
                    except FloodWaitError as e:
                        # Telegram rate limit - must wait
                        wait_time = e.seconds
                        logger.warning(f'Rate limit hit, waiting {wait_time}s')
                        await event.respond(
                            f'Rate limit hit for batch.\n'
                            f'Waiting {wait_time} seconds...'
                        )
                        await asyncio.sleep(wait_time)
                        
                        # Retry this batch once after wait
                        try:
                            await user_client(InviteToChannelRequest(
                                target_entity,
                                batch
                            ))
                            added += len(batch)
                            consecutive_failures = 0
                            current_delay = base_delay * 2  # Increase delay after flood wait
                            await event.respond(f'Batch retry successful. Increased delay to {current_delay}s')
                        except Exception as e2:
                            # If batch still fails, try individual invites
                            failed += await invite_individual(
                                user_client, target_entity, batch, event
                            )
                            consecutive_failures += 1

                    except Exception as e:
                        # Batch failed, try individual invites
                        logger.error(f'Batch failed: {e}')
                        failed_in_batch = await invite_individual(
                            user_client, target_entity, batch, event
                        )
                        failed += failed_in_batch
                        added += (len(batch) - failed_in_batch)
                        consecutive_failures += 1
                        
                        # Exponential backoff on consecutive failures
                        if consecutive_failures > 0:
                            current_delay = min(30, base_delay * (2 ** consecutive_failures))
                            logger.info(f'Increased delay to {current_delay}s due to failures')
                    
                    # Check if we've hit daily limit
                    if added >= DAILY_INVITE_LIMIT:
                        remaining = len(members) - DAILY_INVITE_LIMIT
                        await event.respond(
                            f'Daily limit of {DAILY_INVITE_LIMIT} invites reached.\n'
                            f'{remaining} members remaining for tomorrow.\n'
                            f'Session complete: {added} added, {failed} failed'
                        )
                        break
                    
                    # Adaptive delay between batches
                    await asyncio.sleep(current_delay)
                    
                    # If too many consecutive failures, long cooldown
                    if consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
                        cooldown = 300  # 5 minutes
                        logger.warning(f'{consecutive_failures} failures, cooling down {cooldown}s')
                        await event.respond(
                            f'Multiple failures. Cooling down for 5 minutes...\n'
                            f'Progress so far: {added}/{batch_end}'
                        )
                        await asyncio.sleep(cooldown)
                        consecutive_failures = 0
                        current_delay = base_delay * 2
                        await event.respond(f'Cooldown complete. Resuming with {current_delay}s delay...')
                
                await event.respond(
                    f'Migration complete!\n\n'
                    f'Total: {total}\n'
                    f'Added: {added}\n'
                    f'Failed: {failed}'
                )
                
            except Exception as e:
                logger.error(f'Migration error: {e}')
                await event.respond(f'Error during migration: {str(e)[:200]}')
            
    except Exception as e:
        logger.error(f'Error: {e}')
        await event.answer(f'Error: {str(e)[:50]}', alert=True)

async def main():
    """Main function"""
    logger.info('='*50)
    logger.info('Starting Telegram Migration Bot')
    logger.info('='*50)
    
    # Connect user client (for accessing groups)
    logger.info('Connecting user client...')
    await user_client.connect()
    
    if not await user_client.is_user_authorized():
        logger.error('User client not authenticated!')
        return
    
    me = await user_client.get_me()
    logger.info(f'User client: {me.first_name} (@{me.username})')
    
    # Start bot client
    logger.info('Starting bot client...')
    await bot_client.start(bot_token=BOT_TOKEN)
    
    bot_me = await bot_client.get_me()
    logger.info(f'Bot client: @{bot_me.username}')
    logger.info('='*50)
    logger.info('Bot is running! Send /start to test.')
    logger.info('Press Ctrl+C to stop.')
    logger.info('='*50)
    
    # Keep both running
    await asyncio.gather(
        user_client.run_until_disconnected(),
        bot_client.run_until_disconnected()
    )

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info('\nBot stopped by user.')
    except Exception as e:
        logger.error(f'Fatal error: {e}')
        raise
