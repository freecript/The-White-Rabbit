"""Стани створення нагадування."""

from aiogram.fsm.state import State, StatesGroup


class ReminderForm(StatesGroup):
    """Етапи створення нового нагадування."""

    text = State()
    date = State()
    time = State()
    confirmation = State()