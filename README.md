# Лента Дня

Модульное веб-приложение новостного портала на FastAPI.

## Структура

- `app/main.py` — сборка приложения и подключение роутеров.
- `app/routes/` — роутеры (`public`, `auth`, `admin`).
- `app/models.py` — SQLAlchemy-модели.
- `app/db.py` — подключение к БД и сессии.
- `templates/`, `static/` — UI.

## Запуск в Docker

```bash
docker compose -p news up -d --build
```

Приложение: `http://127.0.0.1:8000`

PostgreSQL доступен с хоста на `localhost:5432`.

При старте выполняется SQL-скрипт `db/init/001_schema_seed.sql`: он создает таблицы и заполняет БД тестовыми пользователями и новостями.

Администратор (тест):

- `admin@lentadnya.local`
- `admin123`

Редактор (тест):

- `editor@lentadnya.local`
- `editor123`

Обычные пользователи (тест):

- `anna@example.local`
- `igor@example.local`
- `maria@example.local`
- `pavel@example.local`
- `olga@example.local`
- `denis@example.local`
- `elena@example.local`
- `nikita@example.local`

Пароль для обычных пользователей: `user12345`
