
import asyncio # Модуль для роботи з асинхронним кодом.Він дозволяє боту чекати нові повідомлення,не зупиняючи всю програму.
import os # Через нього ми отримаємо токен із файлу .env.

from aiogram import Bot, Dispatcher # Dispatcher — приймає повідомлення та передає їх потрібним функціям.
from aiogram.filters import CommandStart # Фільтр, який визначає команду /start.
from aiogram.types import Message # Тип Message представляє повідомлення від користувача.
from dotenv import load_dotenv # Функція для завантаження змінних із файлу .env.
from aiogram.enums import ParseMode # щоб можна було додати HTML теги

from database.connection import create_tables # таблиці
from database.queries import add_user # функція для додавання користувача до бази даних

load_dotenv() # Читаємо дані з файлу .env.
TOKEN = os.getenv("BOT_TOKEN") # Отримуємо значення BOT_TOKEN із файлу .env.

bot = Bot(token=TOKEN) # Створюємо об’єкт бота та передаємо йому токен.
dp = Dispatcher() # Створюємо диспетчер


# обробник команди /start.Коли користувач надішле /start,Dispatcher викличе функцію start_handler.
@dp.message(CommandStart())
async def start_handler(message: Message):
    if message.from_user:
        
        await add_user(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            full_name=message.from_user.full_name,
        )

    await message.answer(
        "<b>🔑🚪 Привіт! 👋 🎩</b>\n"
        "<i>Я бот нагадувань. 🐇☕</i>\n"
        "<i>Допоможу тобі нікуди не запізнитися ⏱️</i>\n"
        "<i>та нічого важливого не забути! ✨♠️</i>",
        parse_mode=ParseMode.HTML,
    )

# коли бот працює в терміналі пишеться "Start...",
# python -m watchfiles --filter python ".venv\Scripts\python.exe main.py" . - для запуску із перезавантаженням після змін
async def main():
    # Створюємо таблиці перед запуском бота.
    await create_tables()

    print("Start...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())


