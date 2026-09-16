"""Головне меню бота."""

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup # імпорт клавіатури та кнопок для головного меню бота


main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="➕ Створити нагадування 🐇"),
        ],
        [
            KeyboardButton(text="📜 Мої нагадування⏱️"),
            KeyboardButton(text="❓ Допомога🚪"),
        ],
    ],
    resize_keyboard=True,
    input_field_placeholder="Оберіть дію...",
)