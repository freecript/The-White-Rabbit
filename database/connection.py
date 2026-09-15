"""Підключення до бази даних і створення таблиць."""

import aiosqlite


DATABASE_NAME = "reminders.db"


async def create_tables():
    """Створює необхідні таблиці, якщо їх ще немає."""

    # Відкриваємо підключення до бази даних.
    async with aiosqlite.connect(DATABASE_NAME) as database:
        # Виконуємо SQL-команду створення таблиці users.
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

        # Зберігаємо зміни в базі даних.
        await database.commit()