"""
Start command handler for the Telegram Lottery Bot.
Handles /start command with language detection and welcome message.
"""

from aiogram import F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.helpers.config import Settings

from utils.language import get_user_lang, get_text
from utils.logger import get_logger
from src.database.db import set_user_language, get_user_language
from src.helpers.bot import get_welcome_inline_keyboard


async def handle_start_command(message: Message, state: FSMContext, settings: 'Settings') -> None:
    """
    Handle /start command with language detection and logging.
    
    Args:
        message: Telegram message object
        state: FSM context
        settings: Bot settings
    """
    try:
        # Clear any existing state
        await state.clear()
        
        user = message.from_user
        if not user:
            return
            
        # Get logger instance
        logger = get_logger()
        
        # Detect user language
        detected_language = get_user_lang(user.language_code)
        
        # Check if user already has a saved language preference
        saved_language = await get_user_language(user.id)
        
        # Use saved language if available, otherwise use detected language
        user_language = saved_language or detected_language
        
        # Save language preference if it's new or different
        if not saved_language or saved_language != detected_language:
            await set_user_language(user.id, user_language)
        
        # Log user action
        if logger:
            await logger.log_user_action(
                user=user,
                action="/start",
                language=user_language,
                additional_info=f"Detected: {detected_language}, Used: {user_language}"
            )
        
        # Get localized welcome message
        welcome_text = get_text(user.id, "welcome")
        add_me_text = get_text(user.id, "add_me")
        updates_text = get_text(user.id, "updates")
        
        # Create inline keyboard with channel links
        inline_keyboard = get_welcome_inline_keyboard(
            channel_username=settings.channel_username,
            updates_channel_username=settings.updates_channel_username,
            add_me_text=add_me_text,
            updates_text=updates_text
        )
        
        # Send welcome message (reply to the same message)
        await message.reply(
            text=welcome_text,
            reply_markup=inline_keyboard,
            parse_mode="HTML"
        )
        
    except Exception as e:
        # Log error and send fallback message
        if logger:
            await logger.log_system_event(
                event="Error in start command",
                details=f"User {user.id if user else 'Unknown'}: {str(e)}"
            )
        
        # Send fallback English message
        await message.reply(
            "🎉 Welcome to the Lottery Bot!\n\n"
            "Upload your photos to participate in exciting lotteries and win amazing prizes! 🏆"
        )


def register_start_handlers(dp, settings: 'Settings'):
    """Register start command handlers."""
    
    async def start_wrapper(message: Message, state: FSMContext):
        await handle_start_command(message, state, settings)
    
    dp.message.register(start_wrapper, CommandStart())