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

WITH seed_comments(news_title, user_email, body, created_at) AS (
    VALUES
        ('Город обновил расписание общественного транспорта', 'anna@example.local', 'Удобно, если интервалы действительно станут меньше утром.', TIMESTAMP '2026-05-02 10:25:00'),
        ('Город обновил расписание общественного транспорта', 'igor@example.local', 'Хотелось бы увидеть подробную схему изменений по маршрутам.', TIMESTAMP '2026-05-02 10:42:00'),
        ('В регионе открыли новый центр цифровых сервисов', 'maria@example.local', 'Такие консультации особенно полезны пожилым людям.', TIMESTAMP '2026-05-03 12:05:00'),
        ('В регионе открыли новый центр цифровых сервисов', 'pavel@example.local', 'Главное, чтобы специалисты помогали не только по записи.', TIMESTAMP '2026-05-03 12:18:00'),
        ('Школьники представили проекты по экологии', 'olga@example.local', 'Интересно было бы внедрить лучшие проекты в школах города.', TIMESTAMP '2026-05-04 14:00:00'),
        ('Медики напомнили о сезонной профилактике', 'denis@example.local', 'Полезное напоминание, особенно в период перепадов погоды.', TIMESTAMP '2026-05-05 10:20:00'),
        ('В парке начались работы по благоустройству', 'elena@example.local', 'Надеюсь, новые дорожки сделают удобными для колясок.', TIMESTAMP '2026-05-06 16:05:00'),
        ('В парке начались работы по благоустройству', 'nikita@example.local', 'Освещение в парке давно требовало обновления.', TIMESTAMP '2026-05-06 16:27:00'),
        ('Университет объявил набор на летние курсы', 'anna@example.local', 'Курсы по анализу данных звучат очень актуально.', TIMESTAMP '2026-05-07 12:45:00'),
        ('В библиотеке пройдет неделя научной литературы', 'igor@example.local', 'Хороший формат для студентов перед летней практикой.', TIMESTAMP '2026-05-08 17:05:00'),
        ('Спортсмены региона выиграли межвузовский турнир', 'maria@example.local', 'Поздравления команде, отличный результат.', TIMESTAMP '2026-05-09 18:30:00'),
        ('Эксперты обсудили защиту персональных данных', 'pavel@example.local', 'Тему безопасности стоит чаще объяснять простым языком.', TIMESTAMP '2026-05-10 15:10:00'),
        ('Эксперты обсудили защиту персональных данных', 'olga@example.local', 'Было бы полезно опубликовать краткие рекомендации после круглого стола.', TIMESTAMP '2026-05-10 15:45:00'),
        ('На набережной запланировали праздничную программу', 'denis@example.local', 'Если транспорт усилят, будет намного проще добраться вечером.', TIMESTAMP '2026-05-11 20:00:00'),
        ('На набережной запланировали праздничную программу', 'elena@example.local', 'Ждем программу мероприятий по времени.', TIMESTAMP '2026-05-11 20:22:00')
)
INSERT INTO comments (body, news_id, author_id, created_at)
SELECT seed_comments.body, news.id, users.id, seed_comments.created_at
FROM seed_comments
JOIN news ON news.title = seed_comments.news_title
JOIN users ON users.email = seed_comments.user_email
WHERE NOT EXISTS (
    SELECT 1
    FROM comments
    WHERE comments.body = seed_comments.body
      AND comments.news_id = news.id
      AND comments.author_id = users.id
);

WITH seed_reactions(news_title, user_email, value) AS (
    VALUES
        ('Город обновил расписание общественного транспорта', 'anna@example.local', 1),
        ('Город обновил расписание общественного транспорта', 'igor@example.local', 1),
        ('Город обновил расписание общественного транспорта', 'pavel@example.local', -1),
        ('В регионе открыли новый центр цифровых сервисов', 'maria@example.local', 1),
        ('В регионе открыли новый центр цифровых сервисов', 'olga@example.local', 1),
        ('В регионе открыли новый центр цифровых сервисов', 'denis@example.local', 1),
        ('Школьники представили проекты по экологии', 'anna@example.local', 1),
        ('Школьники представили проекты по экологии', 'elena@example.local', 1),
        ('Медики напомнили о сезонной профилактике', 'igor@example.local', 1),
        ('Медики напомнили о сезонной профилактике', 'nikita@example.local', -1),
        ('В парке начались работы по благоустройству', 'maria@example.local', 1),
        ('В парке начались работы по благоустройству', 'pavel@example.local', 1),
        ('Университет объявил набор на летние курсы', 'olga@example.local', 1),
        ('Университет объявил набор на летние курсы', 'denis@example.local', 1),
        ('В библиотеке пройдет неделя научной литературы', 'elena@example.local', 1),
        ('В библиотеке пройдет неделя научной литературы', 'nikita@example.local', 1),
        ('Спортсмены региона выиграли межвузовский турнир', 'anna@example.local', 1),
        ('Спортсмены региона выиграли межвузовский турнир', 'igor@example.local', 1),
        ('Эксперты обсудили защиту персональных данных', 'maria@example.local', 1),
        ('Эксперты обсудили защиту персональных данных', 'pavel@example.local', -1),
        ('На набережной запланировали праздничную программу', 'olga@example.local', 1),
        ('На набережной запланировали праздничную программу', 'denis@example.local', 1),
        ('На набережной запланировали праздничную программу', 'elena@example.local', 1)
)
INSERT INTO likes (news_id, user_id, value)
SELECT news.id, users.id, seed_reactions.value
FROM seed_reactions
JOIN news ON news.title = seed_reactions.news_title
JOIN users ON users.email = seed_reactions.user_email
ON CONFLICT (news_id, user_id) DO UPDATE SET
    value = EXCLUDED.value;

WITH seed_comment_reactions(comment_body, user_email, value) AS (
    VALUES
        ('Удобно, если интервалы действительно станут меньше утром.', 'igor@example.local', 1),
        ('Удобно, если интервалы действительно станут меньше утром.', 'maria@example.local', 1),
        ('Хотелось бы увидеть подробную схему изменений по маршрутам.', 'anna@example.local', 1),
        ('Такие консультации особенно полезны пожилым людям.', 'pavel@example.local', 1),
        ('Главное, чтобы специалисты помогали не только по записи.', 'olga@example.local', -1),
        ('Интересно было бы внедрить лучшие проекты в школах города.', 'denis@example.local', 1),
        ('Полезное напоминание, особенно в период перепадов погоды.', 'elena@example.local', 1),
        ('Надеюсь, новые дорожки сделают удобными для колясок.', 'nikita@example.local', 1),
        ('Освещение в парке давно требовало обновления.', 'anna@example.local', 1),
        ('Курсы по анализу данных звучат очень актуально.', 'igor@example.local', 1),
        ('Хороший формат для студентов перед летней практикой.', 'maria@example.local', 1),
        ('Поздравления команде, отличный результат.', 'pavel@example.local', 1),
        ('Тему безопасности стоит чаще объяснять простым языком.', 'olga@example.local', 1),
        ('Было бы полезно опубликовать краткие рекомендации после круглого стола.', 'denis@example.local', 1),
        ('Если транспорт усилят, будет намного проще добраться вечером.', 'elena@example.local', 1),
        ('Ждем программу мероприятий по времени.', 'nikita@example.local', 1),
        ('Ждем программу мероприятий по времени.', 'anna@example.local', -1)
)
INSERT INTO comment_likes (comment_id, user_id, value)
SELECT comments.id, users.id, seed_comment_reactions.value
FROM seed_comment_reactions
JOIN comments ON comments.body = seed_comment_reactions.comment_body
JOIN users ON users.email = seed_comment_reactions.user_email
ON CONFLICT (comment_id, user_id) DO UPDATE SET
    value = EXCLUDED.value;

SELECT setval(pg_get_serial_sequence('users', 'id'), GREATEST((SELECT MAX(id) FROM users), 1), TRUE);
SELECT setval(pg_get_serial_sequence('news', 'id'), GREATEST((SELECT MAX(id) FROM news), 1), TRUE);
SELECT setval(pg_get_serial_sequence('comments', 'id'), GREATEST(COALESCE((SELECT MAX(id) FROM comments), 1), 1), TRUE);
SELECT setval(pg_get_serial_sequence('likes', 'id'), GREATEST(COALESCE((SELECT MAX(id) FROM likes), 1), 1), TRUE);
SELECT setval(pg_get_serial_sequence('comment_likes', 'id'), GREATEST(COALESCE((SELECT MAX(id) FROM comment_likes), 1), 1), TRUE);
