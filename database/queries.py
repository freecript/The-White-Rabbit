"""SQL-запити для роботи з користувачами."""

import aiosqlite

from database.connection import DATABASE_NAME


async def add_user(
    telegram_id: int,
    username: str | None,
    full_name: str,
):
    """Додає нового користувача або оновлює його дані."""

    async with aiosqlite.connect(DATABASE_NAME) as database:
        await database.execute(
            """
            INSERT INTO users (telegram_id, username, full_name)
            VALUES (?, ?, ?)
            ON CONFLICT(telegram_id) DO UPDATE SET
                username = excluded.username,
                full_name = excluded.full_name
            """,
            (telegram_id, username, full_name),
        )

        await database.commit()