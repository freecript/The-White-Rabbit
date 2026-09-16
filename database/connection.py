"""Підключення до бази даних і створення таблиць."""

import aiosqlite


DATABASE_NAME = "reminders.db"


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
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
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

        # Зберігаємо зміни після створення обох таблиць.
        await database.commit()