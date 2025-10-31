"""
Logging utilities for the Telegram Lottery Bot.
Handles logging user actions to a specified Telegram channel.
"""

import logging
from datetime import datetime
from typing import Optional
from aiogram import Bot
from aiogram.types import User

# Configure Python logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class TelegramLogger:
    """Handles logging user actions to Telegram channel."""
    
    def __init__(self, bot: Bot, log_channel_id: Optional[int] = None):
        """
        Initialize Telegram logger.
        
        Args:
            bot: Aiogram Bot instance
            log_channel_id: Telegram channel ID for logging (can be None)
        """
        self.bot = bot
        self.log_channel_id = log_channel_id
        
    def set_log_channel(self, channel_id: int) -> None:
        """Set the log channel ID."""
        self.log_channel_id = channel_id
        logger.info(f"Log channel set to: {channel_id}")
    
    async def log_user_action(
        self, 
        user: User, 
        action: str, 
        language: Optional[str] = None,
        additional_info: Optional[str] = None
    ) -> None:
        """
        Log user action to the specified channel.
        
        Args:
            user: Telegram User object
            action: Action performed by user
            language: User's language (optional)
            additional_info: Additional information (optional)
        """
        try:
            # Format timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Format username (handle cases where username might be None)
            username = f"@{user.username}" if user.username else "No username"
            
            # Build log message
            log_message = (
                f"📊 <b>User Action Log</b>\n\n"
                f"👤 <b>User:</b> {username} ({user.id})\n"
                f"🎯 <b>Action:</b> {action}\n"
            )
            
            if language:
                log_message += f"🌐 <b>Language:</b> {language}\n"
            
            if additional_info:
                log_message += f"ℹ️ <b>Info:</b> {additional_info}\n"
                
            log_message += f"⏰ <b>Time:</b> {timestamp}"
            
            # Log to Python logger
            logger.info(f"User {user.id} ({username}) performed action: {action}")
            
            # Send to Telegram channel if configured
            if self.log_channel_id:
                try:
                    await self.bot.send_message(
                        chat_id=self.log_channel_id,
                        text=log_message,
                        parse_mode="HTML"
                    )
                except Exception as e:
                    logger.error(f"Failed to send log to Telegram channel {self.log_channel_id}: {e}")
            else:
                logger.warning("Log channel not configured, skipping Telegram logging")
                
        except Exception as e:
            logger.error(f"Error in log_user_action: {e}")
    
    async def log_admin_action(
        self, 
        user: User, 
        action: str, 
        target: Optional[str] = None,
        reason: Optional[str] = None
    ) -> None:
        """
        Log admin action with additional details.
        
        Args:
            user: Admin User object
            action: Admin action performed
            target: Target of the action (e.g., ticket number)
            reason: Reason for the action (optional)
        """
        additional_info = []
        if target:
            additional_info.append(f"Target: {target}")
        if reason:
            additional_info.append(f"Reason: {reason}")
            
        await self.log_user_action(
            user=user,
            action=f"[ADMIN] {action}",
            additional_info=" | ".join(additional_info) if additional_info else None
        )
    
    async def log_system_event(self, event: str, details: Optional[str] = None) -> None:
        """
        Log system events.
        
        Args:
            event: System event description
            details: Additional details (optional)
        """
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            log_message = (
                f"🤖 <b>System Event</b>\n\n"
                f"📋 <b>Event:</b> {event}\n"
            )
            
            if details:
                log_message += f"📝 <b>Details:</b> {details}\n"
                
            log_message += f"⏰ <b>Time:</b> {timestamp}"
            
            # Log to Python logger
            logger.info(f"System event: {event}")
            
            # Send to Telegram channel if configured
            if self.log_channel_id:
                try:
                    await self.bot.send_message(
                        chat_id=self.log_channel_id,
                        text=log_message,
                        parse_mode="HTML"
                    )
                except Exception as e:
                    logger.error(f"Failed to send system log to Telegram channel: {e}")
                    
        except Exception as e:
            logger.error(f"Error in log_system_event: {e}")


# Global logger instance (will be initialized in main bot file)
telegram_logger: Optional[TelegramLogger] = None


def init_logger(bot: Bot, log_channel_id: Optional[int] = None) -> TelegramLogger:
    """
    Initialize the global Telegram logger.
    
    Args:
        bot: Aiogram Bot instance
        log_channel_id: Telegram channel ID for logging
        
    Returns:
        TelegramLogger instance
    """
    global telegram_logger
    telegram_logger = TelegramLogger(bot, log_channel_id)
    logger.info("Telegram logger initialized")
    return telegram_logger


def get_logger() -> Optional[TelegramLogger]:
    """Get the global Telegram logger instance."""
    return telegram_logger