
import asyncio # Модуль для роботи з асинхронним кодом.Він дозволяє боту чекати нові повідомлення,не зупиняючи всю програму.
import os # Через нього ми отримаємо токен із файлу .env.

from aiogram import Bot, Dispatcher, F # Dispatcher — приймає повідомлення та передає їх потрібним функціям.
from aiogram.filters import Command, CommandStart # Фільтр, який визначає команду /start.
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove # Тип Message представляє повідомлення від користувача.
from dotenv import load_dotenv # Функція для завантаження змінних із файлу .env.
from aiogram.enums import ParseMode # щоб можна було додати HTML теги
from keyboards.main import main_keyboard # імпорт кнопок головного меню  
from database.connection import create_tables # таблиці
from zoneinfo import ZoneInfo  # Робота з часовими поясами.

# Функції для роботи з користувачами та нагадуваннями.
from database.queries import (
    add_reminder,
    add_user,
    delete_reminder,
    get_all_reminders,
    get_all_users,
    get_due_reminders,
    get_user_reminders,
    mark_reminder_as_sent,
    should_show_reminder_hint,
) 

from datetime import datetime, timedelta # робота з датою і часом
from aiogram.fsm.context import FSMContext # Керування станами користувача.
from states.reminder import ReminderForm # Етапи створення нагадування.

# Клавіатури для створення та керування нагадуваннями.
from keyboards.reminders import (
    confirmation_keyboard,
    date_keyboard,
    reminders_list_keyboard,
) 

from html import escape # Захищає текст користувача під час використання HTML-тегів.

load_dotenv() # Читаємо дані з файлу .env.
TOKEN = os.getenv("BOT_TOKEN") # Отримуємо значення BOT_TOKEN із файлу .env.
ADMIN_ID = int(os.getenv("ADMIN_ID", "0")) # адмін панель 
KYIV_TIMEZONE = ZoneInfo("Europe/Kyiv") # Робота з часовими поясами.

bot = Bot(token=TOKEN) # Створюємо об’єкт бота та передаємо йому токен.
dp = Dispatcher() # Створюємо диспетчер


# обробник команди /start.Коли користувач надішле /start,Dispatcher викличе функцію start_handler.
@dp.message(CommandStart())
async def start_handler(
    message: Message,
    state: FSMContext,
):
    # Скидаємо незавершене створення нагадування.
    await state.clear()
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


@dp.message(F.text == "❓ Допомога🚪")
async def help_handler(message: Message):
    """Показує коротку інструкцію користувачу."""

    await message.answer(
        "<b>🚪 Як користуватися ботом:</b>\n\n"
        "1️⃣ Натисни «➕ Створити нагадування 🐇».\n"
        "2️⃣ Напиши, про що тобі нагадати.\n"
        "3️⃣ Обери дату та введи час.\n"
        "4️⃣ Перевір і збережи нагадування.\n\n"
        "/start — запускає бота, скидає незавершену дію та відкриває головне меню.\n"
        "/cancel — скасовує поточне створення нагадування, очищає введені дані та повертає головне меню.\n\n"
        "📜 У розділі «Мої нагадування» можна переглянути "
        "або видалити активні нагадування.",
        parse_mode=ParseMode.HTML,
        reply_markup=main_keyboard,
    )


@dp.message(F.text == "➕ Створити нагадування 🐇")
async def create_reminder_start(
    message: Message,
    state: FSMContext,
):
    # Очищаємо попередній незавершений діалог.
    await state.clear()

    # Запам’ятовуємо, що зараз очікуємо текст нагадування.
    await state.set_state(ReminderForm.text)

    message_text = "🐇 Про що тобі нагадати?"

    # Додаємо приклад лише під час першого створення нагадування.
    if message.from_user:
        show_hint = await should_show_reminder_hint(
            message.from_user.id
        )

        if show_hint:
            message_text += "\n\nНаприклад: зателефонувати лікарю"

    await message.answer(
        message_text,
        reply_markup=ReplyKeyboardRemove(),
    )


@dp.message(F.text == "📜 Мої нагадування⏱️")
async def show_user_reminders(message: Message):
    """Показує активні нагадування користувача."""

    if not message.from_user:
        return

    reminders = await get_user_reminders(message.from_user.id)

    if not reminders:
        await message.answer(
            "📭 У тебе поки немає активних нагадувань.",
            reply_markup=main_keyboard,
        )
        return

    lines = ["<b>📜 Твої нагадування:</b>"]

    for number, reminder in enumerate(reminders, start=1):
        reminder_id, reminder_text, remind_at = reminder

        reminder_datetime = datetime.fromisoformat(remind_at)
        formatted_datetime = reminder_datetime.strftime("%d.%m.%Y о %H:%M")

        lines.append(
            f"<b>{number}. 🐇 {escape(reminder_text)}</b>\n"
            f"⏱️ {formatted_datetime}"
        )

    reminder_ids = [
        reminder[0]
        for reminder in reminders
    ]

    await message.answer(
        "\n\n".join(lines),
        parse_mode=ParseMode.HTML,
        reply_markup=reminders_list_keyboard(reminder_ids),
    )


@dp.callback_query(F.data.startswith("delete_reminder:"))
async def delete_user_reminder(callback: CallbackQuery):
    """Видаляє вибране нагадування користувача."""

    callback_data = callback.data or ""

    try:
        reminder_id = int(callback_data.split(":")[1])
    except (IndexError, ValueError):
        await callback.answer("Не вдалося визначити нагадування.")
        return

    await delete_reminder(
        reminder_id=reminder_id,
        telegram_id=callback.from_user.id,
    )

    await callback.answer("Нагадування видалено.")

    if callback.message:
        await callback.message.delete()

        await callback.message.answer(
            "❌ Нагадування видалено.\n\n"
            "Натисни «📜 Мої нагадування⏱️», щоб оновити список.",
            reply_markup=main_keyboard,
        )


@dp.message(Command("cancel"))
async def cancel_command(
    message: Message,
    state: FSMContext,
):
    """Скасовує поточне створення нагадування."""

    current_state = await state.get_state()

    # Якщо користувач зараз нічого не створює.
    if current_state is None:
        await message.answer(
            "🐇 Зараз немає дії, яку потрібно скасувати.",
            reply_markup=main_keyboard,
        )
        return

    # Видаляємо тимчасово збережені дані.
    await state.clear()

    await message.answer(
        "❌ Створення нагадування скасовано.",
        reply_markup=main_keyboard,
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
    today = datetime.now(KYIV_TIMEZONE).date()

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
        tzinfo=KYIV_TIMEZONE,
    )

    # Перевіряємо, що вибраний момент ще не минув.
    if reminder_datetime <= datetime.now(KYIV_TIMEZONE):
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


@dp.callback_query(
    ReminderForm.confirmation,
    F.data == "reminder_cancel",
)
async def cancel_reminder(
    callback: CallbackQuery,
    state: FSMContext,
):
    # Очищаємо всі тимчасово збережені дані нагадування.
    await state.clear()

    # Закриваємо очікування натискання кнопки.
    await callback.answer("Створення скасовано.")

    if callback.message:
        # Прибираємо старі кнопки підтвердження.
        await callback.message.edit_reply_markup(reply_markup=None)

        # Повертаємо користувача до головного меню.
        await callback.message.answer(
            "❌ Створення нагадування скасовано.🕳️",
            reply_markup=main_keyboard,
        )


@dp.callback_query(
    ReminderForm.confirmation,
    F.data == "reminder_edit",
)
async def edit_reminder(
    callback: CallbackQuery,
    state: FSMContext,
):
    # Видаляємо раніше введені дані.
    await state.clear()

    # Знову очікуємо текст нагадування.
    await state.set_state(ReminderForm.text)

    # Закриваємо очікування натискання кнопки.
    await callback.answer()

    if callback.message:
        # Прибираємо старі кнопки підтвердження.
        await callback.message.edit_reply_markup(reply_markup=None)

        # Просимо користувача ввести новий текст.
        await callback.message.answer(
            "✏️ Напиши новий текст нагадування: ♟️",
            reply_markup=ReplyKeyboardRemove(),
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


@dp.message(Command("admin_reminders"))
async def admin_reminders_handler(message: Message):
    

    
    if not message.from_user or message.from_user.id != ADMIN_ID:
        return

    reminders = await get_all_reminders()

    if not reminders:
        await message.answer(".")
        return

    message_text = "<b>📜 :</b>"

    for reminder in reminders:
        (
            reminder_id,
            telegram_id,
            reminder_text,
            remind_at,
            status,
        ) = reminder

        reminder_datetime = datetime.fromisoformat(remind_at)
        formatted_datetime = reminder_datetime.strftime(
            "%d.%m.%Y о %H:%M"
        )

        status_text = (
            "⏳ Очікує"
            if status == "pending"
            else "✅ Надіслано"
        )

        reminder_block = (
            f"<b>№{reminder_id}. 🐇 {escape(reminder_text)}</b>\n"
            f'👤 Telegram ID: <a href="tg://user?id={telegram_id}">{telegram_id}</a>\n'
            f"⏱️ {formatted_datetime}\n"
            f"Статус: {status_text}"
        )

        # Telegram дозволяє приблизно 4096 символів в одному повідомленні.
        if len(message_text) + len(reminder_block) > 3900:
            await message.answer(
                message_text,
                parse_mode=ParseMode.HTML,
            )
            message_text = reminder_block
        else:
            message_text += f"\n\n{reminder_block}"

    await message.answer(
        message_text,
        parse_mode=ParseMode.HTML,
    )


async def reminder_scheduler():
    """Перевіряє та надсилає готові нагадування."""

    while True:
        current_time = datetime.now(KYIV_TIMEZONE).isoformat()

        reminders = await get_due_reminders(current_time)

        for reminder in reminders:
            reminder_id, telegram_id, reminder_text = reminder

            try:
                await bot.send_message(
                    chat_id=telegram_id,
                    text=f"⏱️ <b>{escape(reminder_text)}</b>",
                    parse_mode=ParseMode.HTML,
                )

                await mark_reminder_as_sent(reminder_id)

            except Exception as error:
                print(f"Не вдалося надіслати нагадування: {error}")

        # Чекаємо 10 секунд перед наступною перевіркою.
        await asyncio.sleep(10)


# коли бот працює в терміналі пишеться "Start...",
# python -m watchfiles --filter python ".venv\Scripts\python.exe main.py" . - для запуску із перезавантаженням після змін
async def main():
    # Створюємо таблиці перед запуском бота.
    await create_tables()

    # Запускаємо перевірку нагадувань у фоновому режимі.
    asyncio.create_task(reminder_scheduler())

    print("Start...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())


