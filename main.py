
import asyncio # Модуль для роботи з асинхронним кодом.Він дозволяє боту чекати нові повідомлення,не зупиняючи всю програму.
import os # Через нього ми отримаємо токен із файлу .env.

from aiogram import Bot, Dispatcher, F # Dispatcher — приймає повідомлення та передає їх потрібним функціям.
from aiogram.filters import Command, CommandStart # Фільтр, який визначає команду /start.
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove # Тип Message представляє повідомлення від користувача.
from dotenv import load_dotenv # Функція для завантаження змінних із файлу .env.
from aiogram.enums import ParseMode # щоб можна було додати HTML теги
from keyboards.main import main_keyboard # імпорт кнопок головного меню  

from database.connection import create_tables # таблиці
from database.queries import add_reminder, add_user, get_all_users # функція для додавання користувача до бази даних

from datetime import datetime, timedelta # робота з датою
from aiogram.fsm.context import FSMContext # Керування станами користувача.
from states.reminder import ReminderForm # Етапи створення нагадування.
from keyboards.reminders import confirmation_keyboard, date_keyboard # клавіатура та текст нагадування у FSM.

load_dotenv() # Читаємо дані з файлу .env.
TOKEN = os.getenv("BOT_TOKEN") # Отримуємо значення BOT_TOKEN із файлу .env.
ADMIN_ID = int(os.getenv("ADMIN_ID", "0")) # адмін панель 

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
        reply_markup=main_keyboard,
    )


@dp.message(F.text == "➕ Створити нагадування 🐇")
async def create_reminder_start(message: Message, state: FSMContext):
    # Очищаємо попередній незавершений діалог.
    await state.clear()

    # Запам’ятовуємо, що зараз очікуємо текст нагадування.
    await state.set_state(ReminderForm.text)

    await message.answer(
        "🐇 Про що тобі нагадати?\n\n"
        "Наприклад: зателефонувати лікарю",
        reply_markup=ReplyKeyboardRemove(),
    )


@dp.message(ReminderForm.text)
async def process_reminder_text(message: Message, state: FSMContext):
    # Отримуємо текст повідомлення.
    reminder_text = (message.text or "").strip()

    # Перевіряємо, що користувач надіслав текст.
    if not reminder_text:
        await message.answer("Будь ласка, напиши нагадування текстом.")
        return

    # Обмежуємо надто довгі нагадування.
    if len(reminder_text) > 500:
        await message.answer(
            "Нагадування надто довге. Максимальна довжина — 500 символів."
        )
        return

    # Тимчасово зберігаємо текст у пам’яті FSM.
    await state.update_data(reminder_text=reminder_text)

    # Переходимо до наступного етапу — вибору дати.
    await state.set_state(ReminderForm.date)

    await message.answer(
        "📅 Коли тобі нагадати?",
        reply_markup=date_keyboard,
    )


@dp.message(ReminderForm.date)
async def process_reminder_date(message: Message, state: FSMContext):
    message_text = (message.text or "").strip()
    today = datetime.now().date()

    # Скасовуємо створення нагадування.
    if message_text == "❌ Скасувати":
        await state.clear()
        await message.answer(
            "Створення нагадування скасовано.",
            reply_markup=main_keyboard,
        )
        return

    # Швидкий вибір сьогоднішньої дати.
    if message_text == "📅 Сьогодні":
        selected_date = today

    # Швидкий вибір завтрашньої дати.
    elif message_text == "📅 Завтра":
        selected_date = today + timedelta(days=1)

    # Просимо користувача ввести дату вручну.
    elif message_text == "🗓️ Ввести дату":
        await message.answer(
            "Введи дату у форматі ДД.ММ.РРРР\n\n"
            "Наприклад: 20.09.2026",
            reply_markup=ReplyKeyboardRemove(),
        )
        return

    # Перевіряємо дату, введену вручну.
    else:
        try:
            selected_date = datetime.strptime(
                message_text,
                "%d.%m.%Y",
            ).date()
        except ValueError:
            await message.answer(
                "Не вдалося розпізнати дату.\n"
                "Введи її у форматі ДД.ММ.РРРР.\n\n"
                "Наприклад: 20.09.2026"
            )
            return

    # Не дозволяємо створювати нагадування на минулу дату.
    if selected_date < today:
        await message.answer("Ця дата вже минула. Обери іншу дату.")
        return

    # Тимчасово зберігаємо дату.
    await state.update_data(reminder_date=selected_date.isoformat())

    # Переходимо до введення часу.
    await state.set_state(ReminderForm.time)

    await message.answer(
        "⏱️ Введи час у форматі ГГ:ХХ\n\n"
        "Наприклад: 18:30",
        reply_markup=ReplyKeyboardRemove(),
    )


@dp.message(ReminderForm.time)
async def process_reminder_time(message: Message, state: FSMContext):
    time_text = (message.text or "").strip()

    # Перевіряємо формат часу.
    try:
        selected_time = datetime.strptime(
            time_text,
            "%H:%M",
        ).time()
    except ValueError:
        await message.answer(
            "🐱Не вдалося розпізнати час.\n"
            "Введи його у форматі ГГ:ХХ.\n\n"
            "Наприклад: 18:30"
        )
        return

    # Отримуємо текст і дату, збережені на попередніх етапах.
    reminder_data = await state.get_data()

    reminder_text = reminder_data.get("reminder_text")
    reminder_date = reminder_data.get("reminder_date")

    if not reminder_text or not reminder_date:
        await state.clear()
        await message.answer(
            "😱Не вдалося отримати дані нагадування. Спробуй створити його ще раз.",
            reply_markup=main_keyboard,
        )
        return

    # Перетворюємо збережену дату назад на об’єкт дати.
    selected_date = datetime.strptime(
        reminder_date,
        "%Y-%m-%d",
    ).date()

    # Об’єднуємо дату і час.
    reminder_datetime = datetime.combine(
        selected_date,
        selected_time,
    )

    # Перевіряємо, що вибраний момент ще не минув.
    if reminder_datetime <= datetime.now():
        await message.answer(
            "⏳Цей час уже минув. Введи майбутній час."
        )
        return

    # Зберігаємо час і повну дату нагадування у FSM.
    await state.update_data(
        reminder_time=time_text,
        reminder_datetime=reminder_datetime.isoformat(),
    )

    # Переходимо до підтвердження.
    await state.set_state(ReminderForm.confirmation)

    await message.answer(
        "🐇 Перевір нагадування:\n\n"
        f"📝 {reminder_text}\n"
        f"📅 {selected_date.strftime('%d.%m.%Y')}\n"
        f"⏰ {selected_time.strftime('%H:%M')}",
        reply_markup=confirmation_keyboard,
    )


@dp.callback_query(
    ReminderForm.confirmation,
    F.data == "reminder_save",
)
async def save_reminder(
    callback: CallbackQuery,
    state: FSMContext,
):
    reminder_data = await state.get_data()

    reminder_text = reminder_data.get("reminder_text")
    reminder_datetime = reminder_data.get("reminder_datetime")

    if not reminder_text or not reminder_datetime:
        await state.clear()
        await callback.answer("Не вдалося отримати дані.")
        return

    await add_reminder(
        telegram_id=callback.from_user.id,
        text=reminder_text,
        remind_at=reminder_datetime,
    )

    await state.clear()
    await callback.answer("Нагадування збережено!")
    if callback.message:
        await callback.message.edit_reply_markup(reply_markup=None)


    if callback.message:
        await callback.message.answer(
            "✅ Нагадування успішно збережено!\n\n"
            f"🐇 {reminder_text}",
            reply_markup=main_keyboard,
        )


@dp.message(Command("admin_users"))  # адмін панель
async def admin_users_handler(message: Message):
    if not message.from_user or message.from_user.id != ADMIN_ID:
        return

    users = await get_all_users()

    if not users:
        await message.answer("Користувачів поки немає.")
        return

    lines = ["Користувачі бота:"]

    for number, user in enumerate(users, start=1):
        telegram_id, username, full_name, created_at = user

        username_text = f"@{username}" if username else "немає"

        lines.append(
            f"{number}. {full_name}\n"
            f"Username: {username_text}\n"
            f"Telegram ID: {telegram_id}\n"
            f"Дата додавання: {created_at}"
        )

    await message.answer("\n\n".join(lines))

# коли бот працює в терміналі пишеться "Start...",
# python -m watchfiles --filter python ".venv\Scripts\python.exe main.py" . - для запуску із перезавантаженням після змін
async def main():
    # Створюємо таблиці перед запуском бота.
    await create_tables()

    print("Start...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())


