"""Підключення до бази даних і створення таблиць."""

import os

import aiosqlite

DATABASE_NAME = os.getenv("DATABASE_PATH", "reminders.db")

async def create_tables():
    """Створює необхідні таблиці, якщо їх ще немає."""

    # Відкриваємо підключення до бази даних.
    async with aiosqlite.connect(DATABASE_NAME) as database:
        # Створюємо таблицю користувачів.
        await database.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE NOT NULL,
                username TEXT,
                full_name TEXT,
                reminder_hint_shown INTEGER NOT NULL DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        # Отримуємо список колонок таблиці users.
        cursor = await database.execute("PRAGMA table_info(users)")
        user_columns = await cursor.fetchall()

        column_names = [
            column[1]
            for column in user_columns
        ]

        # Додаємо нову колонку до вже наявної таблиці users.
        if "reminder_hint_shown" not in column_names:
            await database.execute(
                """
                ALTER TABLE users
                ADD COLUMN reminder_hint_shown INTEGER NOT NULL DEFAULT 0
                """
            )

        # Створюємо таблицю нагадувань.
        await database.execute(
            """
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER NOT NULL,
                text TEXT NOT NULL,
                remind_at TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        # Зберігаємо всі зміни в базі даних.
        await database.commit()