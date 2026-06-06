CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(64) NOT NULL,
    role VARCHAR(16) NOT NULL DEFAULT 'user',
    is_blocked BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS news (
    id SERIAL PRIMARY KEY,
    title VARCHAR(250) NOT NULL,
    content TEXT NOT NULL,
    author_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    is_published BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS comments (
    id SERIAL PRIMARY KEY,
    body TEXT NOT NULL,
    news_id INTEGER NOT NULL REFERENCES news(id) ON DELETE CASCADE,
    author_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS likes (
    id SERIAL PRIMARY KEY,
    news_id INTEGER NOT NULL REFERENCES news(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    value INTEGER NOT NULL,
    CONSTRAINT uniq_news_user_reaction UNIQUE (news_id, user_id)
);

CREATE TABLE IF NOT EXISTS comment_likes (
    id SERIAL PRIMARY KEY,
    comment_id INTEGER NOT NULL REFERENCES comments(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    value INTEGER NOT NULL,
    CONSTRAINT uniq_comment_user_reaction UNIQUE (comment_id, user_id)
);

CREATE INDEX IF NOT EXISTS ix_users_email ON users(email);
CREATE INDEX IF NOT EXISTS ix_news_title ON news(title);

INSERT INTO users (name, email, password_hash, role, is_blocked, created_at) VALUES
    ('admin', 'admin@lentadnya.local', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', 'admin', FALSE, '2026-05-01 09:00:00'),
    ('editor', 'editor@lentadnya.local', 'ef5e5a1fb95055e0e56cccf98a41e784a132c14e7f6e1ba244302f0e72b29baf', 'editor', FALSE, '2026-05-01 09:05:00'),
    ('anna', 'anna@example.local', 'd785d63511a645a24875a109e0ef1da6560dd94d149b6734949a96556cb3449f', 'user', FALSE, '2026-05-01 09:10:00'),
    ('igor', 'igor@example.local', 'd785d63511a645a24875a109e0ef1da6560dd94d149b6734949a96556cb3449f', 'user', FALSE, '2026-05-01 09:15:00'),
    ('maria', 'maria@example.local', 'd785d63511a645a24875a109e0ef1da6560dd94d149b6734949a96556cb3449f', 'user', FALSE, '2026-05-01 09:20:00'),
    ('pavel', 'pavel@example.local', 'd785d63511a645a24875a109e0ef1da6560dd94d149b6734949a96556cb3449f', 'user', FALSE, '2026-05-01 09:25:00'),
    ('olga', 'olga@example.local', 'd785d63511a645a24875a109e0ef1da6560dd94d149b6734949a96556cb3449f', 'user', FALSE, '2026-05-01 09:30:00'),
    ('denis', 'denis@example.local', 'd785d63511a645a24875a109e0ef1da6560dd94d149b6734949a96556cb3449f', 'user', FALSE, '2026-05-01 09:35:00'),
    ('elena', 'elena@example.local', 'd785d63511a645a24875a109e0ef1da6560dd94d149b6734949a96556cb3449f', 'user', FALSE, '2026-05-01 09:40:00'),
    ('nikita', 'nikita@example.local', 'd785d63511a645a24875a109e0ef1da6560dd94d149b6734949a96556cb3449f', 'user', FALSE, '2026-05-01 09:45:00')
ON CONFLICT (email) DO UPDATE SET
    name = EXCLUDED.name,
    password_hash = EXCLUDED.password_hash,
    role = EXCLUDED.role,
    is_blocked = EXCLUDED.is_blocked;

WITH editor AS (
    SELECT id AS author_id FROM users WHERE email = 'editor@lentadnya.local'
), seed_news(title, content, created_at) AS (
    VALUES
        ('Город обновил расписание общественного транспорта', 'С понедельника на популярных маршрутах увеличат количество рейсов в часы пик. Изменения должны сократить время ожидания автобусов и трамваев.', TIMESTAMP '2026-05-02 10:00:00'),
        ('В регионе открыли новый центр цифровых сервисов', 'Жители смогут получить консультации по государственным услугам, электронным документам и безопасной работе с личными кабинетами.', TIMESTAMP '2026-05-03 11:30:00'),
        ('Школьники представили проекты по экологии', 'На городском конкурсе участники показали решения для сортировки отходов, мониторинга воздуха и экономии воды в учебных учреждениях.', TIMESTAMP '2026-05-04 13:15:00'),
        ('Медики напомнили о сезонной профилактике', 'Специалисты рекомендуют соблюдать режим сна, чаще проветривать помещения и обращаться к врачу при первых признаках заболевания.', TIMESTAMP '2026-05-05 09:45:00'),
        ('В парке начались работы по благоустройству', 'Подрядчики обновят освещение, пешеходные дорожки и установят дополнительные скамейки. Основные работы планируется завершить к началу лета.', TIMESTAMP '2026-05-06 15:20:00'),
        ('Университет объявил набор на летние курсы', 'Программы посвящены программированию, анализу данных и основам информационной безопасности. Запись открыта до конца месяца.', TIMESTAMP '2026-05-07 12:10:00'),
        ('В библиотеке пройдет неделя научной литературы', 'Посетителей ждут тематические выставки, встречи с преподавателями и подборки новых изданий для студентов технических направлений.', TIMESTAMP '2026-05-08 16:40:00'),
        ('Спортсмены региона выиграли межвузовский турнир', 'Команда показала сильные результаты в финальных матчах и заняла первое место в общем зачете соревнований.', TIMESTAMP '2026-05-09 18:00:00'),
        ('Эксперты обсудили защиту персональных данных', 'На круглом столе участники разобрали актуальные угрозы, требования к организациям и практики обучения сотрудников.', TIMESTAMP '2026-05-10 14:25:00'),
        ('На набережной запланировали праздничную программу', 'Организаторы подготовили концерты, интерактивные площадки и вечернюю подсветку. В день мероприятия будет усилена работа транспорта.', TIMESTAMP '2026-05-11 19:30:00')
)
INSERT INTO news (title, content, author_id, is_published, created_at, updated_at)
SELECT seed_news.title, seed_news.content, editor.author_id, TRUE, seed_news.created_at, seed_news.created_at
FROM seed_news
CROSS JOIN editor
WHERE NOT EXISTS (
    SELECT 1 FROM news WHERE news.title = seed_news.title
);

SELECT setval(pg_get_serial_sequence('users', 'id'), GREATEST((SELECT MAX(id) FROM users), 1), TRUE);
SELECT setval(pg_get_serial_sequence('news', 'id'), GREATEST((SELECT MAX(id) FROM news), 1), TRUE);
