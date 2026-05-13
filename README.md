# Лента Дня

Модульное веб-приложение новостного портала на FastAPI.

## Структура

- `app/main.py` — сборка приложения и подключение роутеров.
- `app/routes/` — роутеры (`public`, `auth`, `admin`).
- `app/models.py` — SQLAlchemy-модели.
- `app/db.py` — подключение к БД и сессии.
- `templates/`, `static/` — UI.

## Локальный запуск

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python main.py
```

## Запуск в Docker (два контейнера: app + db)

```bash
docker compose up --build
```

Приложение: `http://127.0.0.1:8000`

Администратор (тест):

- `admin@lentadnya.local`
- `admin123`

Редактор (тест):

- `editor@lentadnya.local`
- `editor123`
