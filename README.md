# 🐇 The White Rabbit

Telegram-бот для створення нагадувань, натхнений атмосферою «Аліси в Країні чудес».

Користувач указує текст, дату та час, а бот надсилає повідомлення у потрібний момент.

 Можливості

- створення нагадувань;
- вибір дати: сьогодні, завтра або вручну;
- введення точного часу;
- підтвердження та редагування перед збереженням;
- автоматичне надсилання нагадувань;
- перегляд активних нагадувань;
- видалення непотрібних нагадувань;
- підтримка київського часового поясу;

 Технології

- Python 3
- aiogram 3
- SQLite
- aiosqlite
- python-dotenv
- FSM
- Git та GitHub

📁 Структура проєкту

```text
The-White-Rabbit/
├── database/
│   ├── connection.py
│   └── queries.py
├── keyboards/
│   ├── main.py
│   └── reminders.py
├── states/
│   └── reminder.py
├── main.py
├── requirements.txt
└── .env.example
```

 Запуск проєкту

Клонувати репозиторій:

```bash
git clone https://github.com/freecript/The-White-Rabbit.git
cd The-White-Rabbit
```

Створити віртуальне середовище:

```bash
python -m venv .venv
```

Активувати його у Windows:

```powershell
.venv\Scripts\activate
```

Встановити залежності:

```bash
python -m pip install -r requirements.txt
```

Створити файл `.env`:

```env
BOT_TOKEN=your_bot_token_here

Запустити бота:

```bash
python main.py
```


🔐 Безпека

Файли `.env` і `reminders.db` не завантажуються на GitHub.

 Статус

Проєкт перебуває в активній розробці.