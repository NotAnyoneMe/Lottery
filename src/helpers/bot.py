from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from typing import Optional


def get_welcome_inline_keyboard(
    channel_username: Optional[str] = None,
    updates_channel_username: Optional[str] = None,
    add_me_text: str = "Add Me ➕",
    updates_text: str = "Bot Updates 🔔"
) -> InlineKeyboardMarkup:
    """Create inline keyboard for welcome message with channel links."""
    keyboard = []
    
    if channel_username:
        # Remove @ if present and add it back
        clean_username = channel_username.lstrip('@')
        keyboard.append([
            InlineKeyboardButton(
                text=add_me_text,
                url=f"https://t.me/{clean_username}"
            )
        ])
    
    if updates_channel_username:
        # Remove @ if present and add it back
        clean_username = updates_channel_username.lstrip('@')
        keyboard.append([
            InlineKeyboardButton(
                text=updates_text,
                url=f"https://t.me/{clean_username}"
            )
        ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def user_menu(
    upload_text: str = "📸 Upload New Photo",
    tickets_text: str = "🎟 View My Lottery Tickets",
    back_text: str = "⬅️ Back to Menu"
) -> ReplyKeyboardMarkup:
    """Create user menu with localized text."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=upload_text)],
            [KeyboardButton(text=tickets_text)],
            [KeyboardButton(text=back_text)],
        ],
        resize_keyboard=True,
    )


def admin_menu(
    start_draw_text: str = "🎲 Start Draw",
    show_photo_text: str = "📷 Show Photo by Number",
    delete_ticket_text: str = "🗑 Delete Ticket",
    archive_text: str = "📦 Archive Lottery",
    settings_text: str = "🔧 Check Settings",
    back_text: str = "⬅️ Back to Menu"
) -> ReplyKeyboardMarkup:
    """Create admin menu with localized text."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=start_draw_text)],
            [KeyboardButton(text=show_photo_text)],
            [KeyboardButton(text=delete_ticket_text)],
            [KeyboardButton(text=archive_text)],
            [KeyboardButton(text=settings_text)],
            [KeyboardButton(text=back_text)],
        ],
        resize_keyboard=True,
    )


def back_menu(back_text: str = "⬅️ Back to Menu") -> ReplyKeyboardMarkup:
    """Create back menu with localized text."""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=back_text)]],
        resize_keyboard=True,
    )


def lottery_inline_actions(
    ticket_number: int,
    confirm_text: str = "✅ Confirm Winner",
    reject_text: str = "❌ Reject Ticket"
) -> InlineKeyboardMarkup:
    """Create inline keyboard for lottery draw actions."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=confirm_text, callback_data=f"confirm_win:{ticket_number}"),
                InlineKeyboardButton(text=reject_text, callback_data=f"reject_win:{ticket_number}"),
            ]
        ]
    )


def user_tickets_inline_keyboard(ticket_numbers: list) -> InlineKeyboardMarkup:
    """Создает inline-клавиатуру с номерами билетов пользователя"""
    if not ticket_numbers:
        return InlineKeyboardMarkup(inline_keyboard=[])
    
    # Создаем кнопки по 2 в ряд для компактности
    keyboard = []
    for i in range(0, len(ticket_numbers), 2):
        row = []
        for j in range(2):
            if i + j < len(ticket_numbers):
                ticket_num = ticket_numbers[i + j]
                row.append(InlineKeyboardButton(
                    text=f"🎟 №{ticket_num}", 
                    callback_data=f"view_ticket:{ticket_num}"
                ))
        keyboard.append(row)
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
