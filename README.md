# Telegram Migration Bot

Improved by openclaw 🦞

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> Telegram bot for migrating users between groups/channels with interactive UI and progress tracking.

---

## Description

This bot automates the process of migrating members from one Telegram group or channel to another. It uses a user account for actual invites to bypass Telegram bot API restrictions.

### Features
- Interactive group selection via inline buttons
- Real-time migration progress tracking
- ETA calculation and elapsed time display
- Error handling for privacy restrictions and flood limits
- Bot detection and skipping
- Support for both groups and channels

---

## Quick Start

### Prerequisites
- Python 3.12 or higher
- Telegram API credentials (api_id, api_hash)
- Telegram bot token from @BotFather
- Phone number for user account authentication

### Installation

```bash
# Clone repository
git clone https://github.com/tr4m0ryp/Invite_bot_telegram.git
cd Invite_bot_telegram

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your credentials

# Run the bot
python -m src.bot.main
```

### Configuration

Create a `.env` file with your credentials:

```env
API_ID=your_api_id
API_HASH=your_api_hash
USER_PHONE=+1234567890
BOT_TOKEN=your_bot_token_from_botfather
```

Get API credentials at: https://my.telegram.org/apps

---

## Project Structure

```
.
├── src/
│   └── bot/
│       └── main.py          # Main bot implementation
├── docs/
│   └── project/
│       └── README.md        # This file
├── .env.example             # Environment variables template
├── .gitignore              # Git ignore rules
├── requirements.txt        # Python dependencies
└── README.md              # Project overview
```

---

## Usage

1. Start the bot with `/start`
2. Click "Start Migration" button
3. Select source group (where members will be collected from)
4. Select target group (where members will be added)
5. Click "Start Migration" to begin
6. Monitor progress in real-time

---

## Documentation

- [Project README](docs/project/README.md)

---

## Security Notes

- Never commit your `.env` file
- Keep your API credentials private
- The bot requires both user and bot authentication
- User account must have invite permissions in target group

---

## License

MIT License - see [LICENSE](LICENSE)

---

Improved by openclaw 🦞
