#!/bin/bash
# Bot runner - keeps bot running 24/7 with auto-restart

cd /home/tr4m0ryp/.openclaw/workspace/Invite_bot_telegram

while true; do
    echo "[$(date)] Starting bot..." >> /tmp/bot_daemon.log
    python3 src/bot/working_bot.py >> /tmp/bot_daemon.log 2>&1
    echo "[$(date)] Bot crashed/exited. Restarting in 5 seconds..." >> /tmp/bot_daemon.log
    sleep 5
done
