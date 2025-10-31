# 🎉 Enhanced Telegram Lottery Bot

A feature-rich Telegram bot for running photo-based lotteries with multi-language support and comprehensive logging.

## ✨ Features

### 🌍 Multi-Language Support
- **5 Languages**: English, Arabic, Russian, Spanish, Chinese
- **Auto-Detection**: Automatically detects user's Telegram language
- **Persistent Preferences**: Saves user language choices in database
- **Localized Interface**: All menus, messages, and buttons are translated

### 📊 Comprehensive Logging
- **User Actions**: Logs all user interactions (start, button presses, photo uploads)
- **Admin Actions**: Tracks admin operations with detailed context
- **System Events**: Monitors bot startup, errors, and system changes
- **Telegram Channel**: Sends formatted logs to specified channel
- **File Logging**: Also logs to local files for backup

### 🎯 Enhanced /start Command
- **Language Detection**: Automatically detects and sets user language
- **Inline Buttons**: 
  - "Add Me ➕" → Links to your main channel
  - "Bot Updates 🔔" → Links to updates/info channel
- **Reply Mode**: Always replies to the same message (not as new message)
- **Welcome Message**: Fully localized welcome text

### 🔧 Inline Mode Support
- **Basic Inline Queries**: Responds to inline queries with lottery information
- **Search Results**: Provides relevant results based on query
- **Logging**: Tracks inline query usage

### 🏗️ Clean Architecture
- **Modular Structure**: Separated into logical modules
- **Error Handling**: Comprehensive try-catch blocks with logging
- **Async Support**: Fully asynchronous with proper resource management
- **Type Hints**: Complete type annotations for better code quality
- **Comments**: Detailed documentation throughout codebase

## 📁 Project Structure

```
Lottery/
├── bot.py                 # Main bot entry point
├── requirements.txt       # Python dependencies
├── .env                  # Configuration file
├── README.md             # This file
│
├── data/
│   └── language.json     # Multi-language translations
│
├── handlers/
│   ├── __init__.py
│   └── start.py          # /start command handler
│
├── utils/
│   ├── __init__.py
│   ├── language.py       # Language detection and management
│   └── logger.py         # Telegram channel logging
│
└── src/                  # Legacy structure (enhanced)
    ├── helpers/
    │   ├── config.py     # Configuration management
    │   └── bot.py        # Keyboard utilities
    ├── database/
    │   └── db.py         # Database operations
    └── commands/
        └── utils.py      # Utility functions
```

## 🚀 Setup Instructions

### 1. Prerequisites
- Python 3.8+
- Telegram Bot Token (from @BotFather)
- Admin user IDs
- Group/Channel IDs for notifications and logging

### 2. Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd Lottery

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

Edit the `.env` file with your settings:

```env
# Bot Configuration
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

# Admin Configuration
ADMIN_IDS=123456789,987654321
GROUP_CHAT_ID=-1001234567890

# Logging Configuration (Optional)
LOG_CHANNEL_ID=-1001234567890

# Channel Configuration (Optional)
CHANNEL_USERNAME=your_channel_username
UPDATES_CHANNEL_USERNAME=your_updates_channel
```

### 4. Required Bot Settings

In @BotFather, make sure to:
1. **Enable Inline Mode**: `/setinline` → Enable
2. **Set Commands**: 
   ```
   start - Start the bot and show main menu
   ```

### 5. Channel Setup

For logging to work properly:
1. Add your bot to the log channel as an administrator
2. Get the channel ID (use @userinfobot or similar)
3. Set `LOG_CHANNEL_ID` in your `.env` file

### 6. Running the Bot

```bash
# Run the bot
python bot.py

# Or use the legacy entry point
python run.py
```

## 🎮 Usage

### For Users
1. **Start**: Send `/start` to begin
2. **Language**: Bot auto-detects your language or defaults to English
3. **Upload Photos**: Use "📸 Upload New Photo" to participate
4. **View Tickets**: Check your lottery tickets anytime
5. **Inline Mode**: Use `@yourbotname` in any chat for inline queries

### For Admins
1. **Start Draw**: Begin lottery draw process
2. **View Photos**: Check any ticket by number
3. **Manage Tickets**: Delete or reject tickets with reasons
4. **Archive**: Archive completed lotteries
5. **Settings**: Check bot configuration

## 📋 Log Format

The bot logs actions in this format:

```
📊 User Action Log

👤 User: @username (123456789)
🎯 Action: /start
🌐 Language: Arabic
ℹ️ Info: Detected: arabic, Used: arabic
⏰ Time: 2025-10-31 15:24:30
```

## 🌐 Supported Languages

| Language | Code | Status |
|----------|------|--------|
| English  | `en` | ✅ Complete |
| Arabic   | `ar` | ✅ Complete |
| Russian  | `ru` | ✅ Complete |
| Spanish  | `es` | ✅ Complete |
| Chinese  | `zh` | ✅ Complete |

## 🔧 Customization

### Adding New Languages
1. Edit `data/language.json`
2. Add your language key and translations
3. Update `LANGUAGE_MAPPING` in `utils/language.py`

### Modifying Messages
All text is stored in `data/language.json`. Edit the JSON file to customize messages.

### Adding Features
The modular structure makes it easy to add new features:
- Add handlers in `handlers/`
- Add utilities in `utils/`
- Update database schema in `src/database/db.py`

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**: Make sure all dependencies are installed
2. **Database Errors**: Check file permissions in the database directory
3. **Telegram Errors**: Verify bot token and channel IDs
4. **Language Issues**: Ensure `data/language.json` is valid JSON

### Debug Mode

Enable debug logging by modifying the logging level in `utils/logger.py`:

```python
logging.basicConfig(level=logging.DEBUG)
```

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For support and questions:
- Check the troubleshooting section
- Review the logs for error details
- Open an issue on GitHub

---

**Enhanced by OpenHands AI Assistant** 🤖