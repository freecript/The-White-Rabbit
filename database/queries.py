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


async def get_due_reminders(current_time: str):
    """Повертає нагадування, час яких уже настав."""

    async with aiosqlite.connect(DATABASE_NAME) as database:
        cursor = await database.execute(
            """
            SELECT id, telegram_id, text
            FROM reminders
            WHERE status = 'pending'
              AND remind_at <= ?
            ORDER BY remind_at
            """,
            (current_time,),
        )

        reminders = await cursor.fetchall()
        return reminders


async def mark_reminder_as_sent(reminder_id: int):
    """Позначає нагадування як надіслане."""

    async with aiosqlite.connect(DATABASE_NAME) as database:
        await database.execute(
            """
            UPDATE reminders
            SET status = 'sent'
            WHERE id = ?
            """,
            (reminder_id,),
        )

        await database.commit()


async def get_user_reminders(telegram_id: int):
    """Повертає активні нагадування користувача."""

    async with aiosqlite.connect(DATABASE_NAME) as database:
        cursor = await database.execute(
            """
            SELECT id, text, remind_at
            FROM reminders
            WHERE telegram_id = ?
              AND status = 'pending'
            ORDER BY remind_at
            """,
            (telegram_id,),
        )

        reminders = await cursor.fetchall()
        return reminders


async def delete_reminder(
    reminder_id: int,
    telegram_id: int,
):
    """Видаляє нагадування конкретного користувача."""

    async with aiosqlite.connect(DATABASE_NAME) as database:
        await database.execute(
            """
            DELETE FROM reminders
            WHERE id = ?
              AND telegram_id = ?
              AND status = 'pending'
            """,
            (
                reminder_id,
                telegram_id,
            ),
        )

        await database.commit()


async def should_show_reminder_hint(telegram_id: int) -> bool:
    """Перевіряє, чи потрібно показати підказку користувачу."""

    async with aiosqlite.connect(DATABASE_NAME) as database:
        cursor = await database.execute(
            """
            SELECT reminder_hint_shown
            FROM users
            WHERE telegram_id = ?
            """,
            (telegram_id,),
        )

        user = await cursor.fetchone()

        # Якщо користувача немає або підказку вже показували.
        if not user or user[0] == 1:
            return False

        # Запам’ятовуємо, що користувач уже побачив підказку.
        await database.execute(
            """
            UPDATE users
            SET reminder_hint_shown = 1
            WHERE telegram_id = ?
            """,
            (telegram_id,),
        )

        await database.commit()
        return True


async def get_all_reminders():

    async with aiosqlite.connect(DATABASE_NAME) as database:
        cursor = await database.execute(
            """
            SELECT id, telegram_id, text, remind_at, status
            FROM reminders
            ORDER BY remind_at
            """
        )

        reminders = await cursor.fetchall()
        return reminders