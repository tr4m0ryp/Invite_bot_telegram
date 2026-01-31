#!/usr/bin/env python3
import asyncio
from telethon import TelegramClient, events, Button
from telethon.tl.types import Channel, Chat

API_ID = 25155557
API_HASH = 'e1c603972b368b326ea68730378e877b'
BOT_TOKEN = '8016881248:AAF6FuSlITftpONtqH1SSyPUBeEGiO7vbac'

user_client = TelegramClient('user_session', API_ID, API_HASH)
bot_client = TelegramClient('bot_session', API_ID, API_HASH)
user_state = {}

@bot_client.on(events.NewMessage(pattern='/start'))
async def start(event):
    user_state[event.sender_id] = {}
    await event.respond('Welcome! Click to start:', buttons=[Button.inline('Start', b'init')])

@bot_client.on(events.CallbackQuery)
async def callback(event):
    uid = event.sender_id
    data = event.data.decode()
    
    if data == 'init':
        dialogs = await user_client.get_dialogs()
        groups = [d.entity for d in dialogs if isinstance(d.entity, (Channel, Chat)) and hasattr(d.entity, 'title')]
        if not groups:
            await event.edit('No groups found.')
            return
        user_state[uid] = {'all': {str(g.id): g for g in groups}}
        buttons = [Button.inline(g.title[:20], f'src_{g.id}'.encode()) for g in groups]
        await event.edit('Select SOURCE:', buttons=[buttons[i:i+2] for i in range(0, len(buttons), 2)])

async def main():
    await user_client.connect()
    await bot_client.start(bot_token=BOT_TOKEN)
    print('Bot running!')
    await asyncio.gather(user_client.run_until_disconnected(), bot_client.run_until_disconnected())

if __name__ == '__main__':
    asyncio.run(main())
