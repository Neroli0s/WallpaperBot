# Telegram Wallpaper Bot

A Telegram bot that allows users to change your wallpaper with a watermark feature.

## Features

- Change wallpaper through Telegram
- Watermark with username and chat ID
- Support for .png, .jpg, .jpeg, and .gif files
- Ban system for rule breakers
- Windows support for wallpaper changing

## Setup

1. Install Python 3.7 or higher
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the project directory with your Telegram bot token:
   ```
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   ```
4. Run the bot:
   ```bash
   python bot.py
   ```

## Usage

1. Start the bot with `/start`
2. Send an image (.png, .jpg, .jpeg, or .gif)
3. The bot will set it as your wallpaper with a watermark

Note: For .gif files, only the first frame will be used as the wallpaper.

## Commands

- `/start` - Start the bot and get instructions
- `/ban <user_id>` - Ban a user from using the bot

## Requirements

- Windows operating system (for wallpaper changing functionality)
- Python 3.7+
- Required Python packages (see requirements.txt) 