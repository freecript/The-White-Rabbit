"""Клавіатури для створення нагадувань."""

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)


date_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📅 Сьогодні"),
            KeyboardButton(text="📅 Завтра"),
        ],
        [
            KeyboardButton(text="🗓️ Ввести дату"),
        ],
        [
            KeyboardButton(text="❌ Скасувати"),
        ],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder="Обери дату нагадування...",
)


confirmation_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅ Зберегти",
                callback_data="reminder_save",
            ),
            InlineKeyboardButton(
                text="✏️ Змінити",
                callback_data="reminder_edit",
            ),
        ],
        [
            InlineKeyboardButton(
                text="❌ Скасувати",
                callback_data="reminder_cancel",
            ),
        ],
    ]
)