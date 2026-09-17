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


def reminders_list_keyboard(
    reminder_ids: list[int],
) -> InlineKeyboardMarkup:
    """Створює кнопки для видалення нагадувань."""

    keyboard = []

    for number, reminder_id in enumerate(reminder_ids, start=1):
        keyboard.append(
            [
                InlineKeyboardButton(
                    text=f"❌ Видалити нагадування №{number}",
                    callback_data=f"delete_reminder:{reminder_id}",
                )
            ]
        )

    return InlineKeyboardMarkup(inline_keyboard=keyboard)