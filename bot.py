"""
Enhanced Telegram Lottery Bot with multi-language support and comprehensive logging.

Features:
- Multi-language support (English, Arabic, Russian, Spanish, Chinese)
- Comprehensive logging to Telegram channel
- Language detection and user preference storage
- Inline mode support
- Enhanced error handling and code quality
- Modular structure with clean separation of concerns

Author: Enhanced by OpenHands AI Assistant
"""

import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery, 
    Message, 
    InlineQuery, 
    InlineQueryResultArticle,
    InputTextMessageContent
)

# Import our modules
from src.helpers.config import load_settings
from src.database.db import (
    init_db,
    get_next_ticket_number,
    add_ticket,
    get_active_tickets_by_user,
    get_active_ticket_by_number,
    get_ticket_by_number_any_status,
    set_ticket_status,
    get_random_active_ticket,
    archive_lottery,
    set_user_language,
    get_user_language,
)
from src.helpers.bot import (
    admin_menu, 
    user_menu, 
    back_menu, 
    lottery_inline_actions, 
    user_tickets_inline_keyboard,
    get_welcome_inline_keyboard
)
from src.commands.utils import draw_lock, is_admin, parse_int_safe
from utils.language import get_user_lang, get_text, load_translations
from utils.logger import init_logger, get_logger
from handlers.start import register_start_handlers


# FSM States
class AskTicketNumber(StatesGroup):
    admin_view = State()
    admin_delete = State()


class AskReason(StatesGroup):
    reject_reason = State()
    delete_reason = State()


class UploadPhoto(StatesGroup):
    waiting_for_photo = State()


# Global settings variable
_settings = None


def get_settings():
    """Get global settings instance."""
    return _settings


async def start_menu(message: Message) -> None:
    """Display main menu based on user role."""
    try:
        settings = get_settings()
        user = message.from_user
        
        if not user:
            return
            
        # Log menu access
        logger = get_logger()
        if logger:
            await logger.log_user_action(user, "menu_access")
        
        # Get user's language and localized texts
        user_lang = await get_user_language(user.id) or get_user_lang(user.language_code)
        
        if is_admin(user.id, settings.admin_ids):
            # Admin menu
            menu_text = get_text(user.id, "admin_main_menu")
            start_draw_text = get_text(user.id, "start_draw")
            show_photo_text = get_text(user.id, "show_photo")
            delete_ticket_text = get_text(user.id, "delete_ticket")
            archive_text = get_text(user.id, "archive_lottery")
            settings_text = get_text(user.id, "check_settings")
            back_text = get_text(user.id, "back_to_menu")
            
            keyboard = admin_menu(
                start_draw_text=start_draw_text,
                show_photo_text=show_photo_text,
                delete_ticket_text=delete_ticket_text,
                archive_text=archive_text,
                settings_text=settings_text,
                back_text=back_text
            )
        else:
            # User menu
            menu_text = get_text(user.id, "main_menu")
            upload_text = get_text(user.id, "upload_photo")
            tickets_text = get_text(user.id, "my_tickets")
            back_text = get_text(user.id, "back_to_menu")
            
            keyboard = user_menu(
                upload_text=upload_text,
                tickets_text=tickets_text,
                back_text=back_text
            )
        
        await message.answer(menu_text, reply_markup=keyboard)
        
    except Exception as e:
        logging.error(f"Error in start_menu: {e}")
        await message.answer("Main Menu", reply_markup=user_menu())


async def check_settings(message: Message) -> None:
    """Display bot settings (admin only)."""
    try:
        settings = get_settings()
        user = message.from_user
        
        if not user or not is_admin(user.id, settings.admin_ids):
            insufficient_text = get_text(user.id, "insufficient_rights")
            await message.answer(insufficient_text)
            return
        
        # Log admin action
        logger = get_logger()
        if logger:
            await logger.log_admin_action(user, "check_settings")
        
        settings_text = get_text(
            user.id, 
            "settings_info",
            log_channel_id=settings.log_channel_id or "Not set",
            admin_ids=settings.admin_ids,
            bot_token=settings.bot_token[:10]
        )
        
        await message.answer(settings_text, parse_mode="HTML")
        
    except Exception as e:
        logging.error(f"Error in check_settings: {e}")
        await message.answer("Error checking settings")


async def start_photo_upload(message: Message, state: FSMContext) -> None:
    """Start photo upload process."""
    try:
        user = message.from_user
        if not user:
            return
            
        # Log action
        logger = get_logger()
        if logger:
            await logger.log_user_action(user, "start_photo_upload")
        
        await state.set_state(UploadPhoto.waiting_for_photo)
        
        instructions_text = get_text(user.id, "photo_upload_instructions")
        back_text = get_text(user.id, "back_to_menu")
        
        await message.answer(
            instructions_text,
            reply_markup=back_menu(back_text),
            parse_mode="HTML"
        )
        
    except Exception as e:
        logging.error(f"Error in start_photo_upload: {e}")
        await message.answer("Error starting photo upload")


async def handle_upload_photo(message: Message, state: FSMContext) -> None:
    """Handle uploaded photo."""
    try:
        settings = get_settings()
        user = message.from_user
        
        if not user:
            return
        
        # Check if we're in the correct state
        current_state = await state.get_state()
        if current_state != UploadPhoto.waiting_for_photo:
            return
        
        if not message.photo:
            error_text = get_text(user.id, "send_photo_only")
            back_text = get_text(user.id, "back_to_menu")
            await message.answer(
                error_text,
                reply_markup=back_menu(back_text),
                parse_mode="HTML"
            )
            return
        
        # Process photo
        largest_photo = max(message.photo, key=lambda p: p.file_size or 0)
        file_id = largest_photo.file_id
        ticket_number = await get_next_ticket_number()
        await add_ticket(ticket_number, user.id, user.username, file_id)
        
        # Clear state
        await state.clear()
        
        # Log action
        logger = get_logger()
        if logger:
            await logger.log_user_action(
                user, 
                "photo_uploaded", 
                additional_info=f"Ticket #{ticket_number}"
            )
        
        # Send confirmation to user
        confirmation_text = get_text(user.id, "photo_registered", ticket_number=ticket_number)
        upload_text = get_text(user.id, "upload_photo")
        tickets_text = get_text(user.id, "my_tickets")
        back_text = get_text(user.id, "back_to_menu")
        
        await message.answer(
            confirmation_text,
            reply_markup=user_menu(upload_text, tickets_text, back_text),
            parse_mode="HTML"
        )
        
        # Notify group
        group_notification = get_text(
            user.id, 
            "user_got_ticket", 
            username=user.username or str(user.id),
            ticket_number=ticket_number
        )
        await message.bot.send_message(
            chat_id=settings.group_chat_id,
            text=group_notification,
        )
        
    except Exception as e:
        logging.error(f"Error in handle_upload_photo: {e}")
        await message.answer("Error processing photo")


async def handle_my_tickets(message: Message) -> None:
    """Display user's tickets."""
    try:
        user = message.from_user
        if not user:
            return
            
        # Log action
        logger = get_logger()
        if logger:
            await logger.log_user_action(user, "view_my_tickets")
        
        rows = await get_active_tickets_by_user(user.id)
        if not rows:
            no_tickets_text = get_text(user.id, "no_tickets")
            await message.answer(no_tickets_text)
            return
        
        # Extract ticket numbers
        ticket_numbers = [row[0] for row in rows]
        
        # Create inline keyboard
        keyboard = user_tickets_inline_keyboard(ticket_numbers)
        
        tickets_text = get_text(user.id, "your_tickets", count=len(ticket_numbers))
        await message.answer(tickets_text, reply_markup=keyboard)
        
    except Exception as e:
        logging.error(f"Error in handle_my_tickets: {e}")
        await message.answer("Error retrieving tickets")


async def admin_start_draw(message: Message) -> None:
    """Start lottery draw (admin only)."""
    try:
        settings = get_settings()
        user = message.from_user
        
        if not user or not is_admin(user.id, settings.admin_ids):
            insufficient_text = get_text(user.id, "insufficient_rights")
            await message.answer(insufficient_text)
            return
            
        if draw_lock.locked:
            draw_progress_text = get_text(user.id, "draw_in_progress")
            await message.answer(draw_progress_text)
            return
            
        # Log admin action
        logger = get_logger()
        if logger:
            await logger.log_admin_action(user, "start_draw")
        
        async with draw_lock:
            ticket = await get_random_active_ticket()
            if not ticket:
                no_tickets_text = get_text(user.id, "no_active_tickets")
                await message.answer(no_tickets_text)
                return
                
            # Send draw result with action buttons
            draw_text = get_text(
                user.id, 
                "draw_result", 
                ticket_number=ticket["ticket_number"],
                username=ticket["username"]
            )
            confirm_text = get_text(user.id, "confirm_winner")
            reject_text = get_text(user.id, "reject_ticket")
            
            await message.answer_photo(
                ticket["file_id"],
                caption=draw_text,
                reply_markup=lottery_inline_actions(
                    ticket["ticket_number"],
                    confirm_text,
                    reject_text
                ),
            )
            
    except Exception as e:
        logging.error(f"Error in admin_start_draw: {e}")
        await message.answer("Error starting draw")


async def admin_confirm_winner(callback: CallbackQuery) -> None:
    """Confirm lottery winner (admin only)."""
    try:
        settings = get_settings()
        user = callback.from_user
        
        if not user or not is_admin(user.id, settings.admin_ids):
            no_rights_text = get_text(user.id, "no_rights")
            await callback.answer(no_rights_text, show_alert=True)
            return
            
        if not callback.data or not callback.data.startswith("confirm_win:"):
            return
            
        num = parse_int_safe(callback.data.split(":", 1)[1])
        if num is None:
            incorrect_number_text = get_text(user.id, "incorrect_ticket_number")
            await callback.answer(incorrect_number_text, show_alert=True)
            return
            
        ticket = await get_ticket_by_number_any_status(num)
        if not ticket or ticket["status"] != "active":
            unavailable_text = get_text(user.id, "ticket_unavailable")
            await callback.answer(unavailable_text, show_alert=True)
            return
            
        # Mark ticket as rejected so winner doesn't participate again
        await set_ticket_status(num, "rejected", None)
        
        # Log admin action
        logger = get_logger()
        if logger:
            await logger.log_admin_action(
                user, 
                "confirm_winner", 
                target=f"Ticket #{num}",
                reason=f"Winner: @{ticket['username']}"
            )
        
        # Announce winner
        winner_text = get_text(
            user.id,
            "winner_announced",
            ticket_number=num,
            username=ticket['username']
        )
        await callback.message.bot.send_message(
            settings.group_chat_id,
            winner_text,
        )
        
        await callback.message.edit_reply_markup(reply_markup=None)
        
        published_text = get_text(user.id, "winner_published")
        await callback.answer(published_text)
        
    except Exception as e:
        logging.error(f"Error in admin_confirm_winner: {e}")
        await callback.answer("Error confirming winner")


async def handle_inline_query(inline_query: InlineQuery) -> None:
    """Handle inline queries for inline mode support."""
    try:
        user = inline_query.from_user
        query = inline_query.query.strip()
        
        # Log inline query
        logger = get_logger()
        if logger:
            await logger.log_user_action(
                user, 
                "inline_query", 
                additional_info=f"Query: '{query}'"
            )
        
        # Simple inline response
        results = [
            InlineQueryResultArticle(
                id="lottery_info",
                title="🎉 Lottery Bot",
                description="Join our exciting lottery! Upload photos to win prizes!",
                input_message_content=InputTextMessageContent(
                    message_text="🎉 Join our exciting lottery! Upload your photos to participate and win amazing prizes! 🏆"
                )
            )
        ]
        
        if query:
            # Add query-specific result
            results.append(
                InlineQueryResultArticle(
                    id="search_result",
                    title=f"🔍 Search: {query}",
                    description="Click to share this search",
                    input_message_content=InputTextMessageContent(
                        message_text=f"🔍 Searching for: {query}\n\nJoin our lottery bot for exciting prizes!"
                    )
                )
            )
        
        await inline_query.answer(results, cache_time=300)
        
    except Exception as e:
        logging.error(f"Error in handle_inline_query: {e}")


async def user_view_ticket_callback(callback: CallbackQuery) -> None:
    """Handle ticket view callback."""
    try:
        user = callback.from_user
        if not user:
            return
            
        if not callback.data or not callback.data.startswith("view_ticket:"):
            incorrect_text = get_text(user.id, "incorrect_request")
            await callback.answer(incorrect_text, show_alert=True)
            return
        
        num = parse_int_safe(callback.data.split(":", 1)[1])
        if num is None:
            incorrect_number_text = get_text(user.id, "incorrect_ticket_number")
            await callback.answer(incorrect_number_text, show_alert=True)
            return
        
        ticket = await get_active_ticket_by_number(num)
        if not ticket:
            not_found_text = get_text(user.id, "ticket_not_found")
            await callback.answer(not_found_text, show_alert=True)
            return
        
        if ticket["user_id"] != user.id:
            no_access_text = get_text(user.id, "no_access_ticket")
            await callback.answer(no_access_text, show_alert=True)
            return
        
        # Log action
        logger = get_logger()
        if logger:
            await logger.log_user_action(
                user, 
                "view_ticket", 
                additional_info=f"Ticket #{num}"
            )
        
        ticket_text = get_text(user.id, "your_ticket", ticket_number=num)
        await callback.message.answer_photo(
            ticket["file_id"], 
            caption=ticket_text
        )
        await callback.answer()
        
    except Exception as e:
        logging.error(f"Error in user_view_ticket_callback: {e}")
        await callback.answer("Error viewing ticket")


async def admin_archive(message: Message) -> None:
    """Archive lottery (admin only)."""
    try:
        settings = get_settings()
        user = message.from_user
        
        if not user or not is_admin(user.id, settings.admin_ids):
            insufficient_text = get_text(user.id, "insufficient_rights")
            await message.answer(insufficient_text)
            return
        
        # Log admin action
        logger = get_logger()
        if logger:
            await logger.log_admin_action(user, "archive_lottery")
        
        await archive_lottery()
        
        archived_text = get_text(user.id, "lottery_archived")
        await message.bot.send_message(
            settings.group_chat_id,
            archived_text,
        )
        
    except Exception as e:
        logging.error(f"Error in admin_archive: {e}")
        await message.answer("Error archiving lottery")


async def main() -> None:
    """Main bot function."""
    try:
        global _settings
        
        # Load settings and initialize database
        _settings = load_settings()
        await init_db()
        
        # Load translations
        load_translations()
        
        # Initialize bot
        bot = Bot(
            token=_settings.bot_token,
            default=DefaultBotProperties(parse_mode="HTML")
        )
        dp = Dispatcher()
        
        # Initialize logger
        init_logger(bot, _settings.log_channel_id)
        
        # Log system startup
        logger = get_logger()
        if logger:
            await logger.log_system_event(
                "Bot started",
                f"Languages loaded, database initialized, log channel: {_settings.log_channel_id}"
            )
        
        # Register start handlers
        register_start_handlers(dp, _settings)
        
        # Register user handlers
        dp.message.register(start_photo_upload, F.text.in_([
            "📸 Upload New Photo", "📸 Загрузить новое фото", "📸 رفع صورة جديدة",
            "📸 Subir Nueva Foto", "📸 上传新照片"
        ]))
        dp.message.register(handle_upload_photo, F.photo, UploadPhoto.waiting_for_photo)
        dp.message.register(handle_my_tickets, F.text.in_([
            "🎟 View My Lottery Tickets", "🎟 Посмотреть мои лотерейные билетики",
            "🎟 عرض تذاكر اليانصيب الخاصة بي", "🎟 Ver Mis Boletos de Lotería", "🎟 查看我的抽奖券"
        ]))
        
        # Register admin handlers
        dp.message.register(admin_start_draw, F.text.in_([
            "🎲 Start Draw", "🎲 Запустить розыгрыш", "🎲 بدء السحب",
            "🎲 Iniciar Sorteo", "🎲 开始抽奖"
        ]))
        dp.message.register(check_settings, F.text.in_([
            "🔧 Check Settings", "🔧 Проверить настройки", "🔧 فحص الإعدادات",
            "🔧 Verificar Configuración", "🔧 检查设置"
        ]))
        dp.message.register(admin_archive, F.text.in_([
            "📦 Archive Lottery", "📦 Архивировать лотерею", "📦 أرشفة اليانصيب",
            "📦 Archivar Lotería", "📦 归档抽奖"
        ]))
        
        # Register callback handlers
        dp.callback_query.register(admin_confirm_winner, F.data.startswith("confirm_win:"))
        dp.callback_query.register(user_view_ticket_callback, F.data.startswith("view_ticket:"))
        
        # Register menu handlers
        dp.message.register(start_menu, F.text.in_([
            "⬅️ Back to Menu", "⬅️ В меню", "⬅️ العودة للقائمة",
            "⬅️ Volver al Menú", "⬅️ 返回菜单"
        ]))
        
        # Register inline query handler
        dp.inline_query.register(handle_inline_query)
        
        # Start polling
        logging.info("Bot started successfully!")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
        
    except Exception as e:
        logging.error(f"Error in main: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())