"""SQL-запити для роботи з користувачами та нагадуваннями."""

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


async def get_all_users():

    async with aiosqlite.connect(DATABASE_NAME) as database:
        cursor = await database.execute(
            """
            SELECT telegram_id, username, full_name, created_at
            FROM users
            ORDER BY id
            """
        )

        users = await cursor.fetchall()
        return users


async def add_reminder(
    telegram_id: int,
    text: str,
    remind_at: str,
):
    """Зберігає нове нагадування в базі даних."""

    async with aiosqlite.connect(DATABASE_NAME) as database:
        await database.execute(
            """
            INSERT INTO reminders (
                telegram_id,
                text,
                remind_at
            )
            VALUES (?, ?, ?)
            """,
            (
                telegram_id,
                text,
                remind_at,
            ),
        )

        await database.commit()