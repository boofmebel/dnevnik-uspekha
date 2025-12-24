-- SQL скрипт для создания администратора
-- Email: 79059510009@mail.ru
-- Пароль: Admin123!

-- Проверка существующего пользователя
SELECT id, email, role FROM users WHERE email = '79059510009@mail.ru';

-- Создание или обновление администратора
INSERT INTO users (email, password_hash, role, created_at)
VALUES (
  '79059510009@mail.ru',
  '$2b$12$YrMfirTKOMvr.WzkuUfVK.tJqJqJqJqJqJqJqJqJqJqJqJqJqJqJqJq',
  'admin',
  NOW()
)
ON CONFLICT (email) DO UPDATE
SET role = 'admin',
    password_hash = EXCLUDED.password_hash,
    updated_at = NOW();

-- Проверка результата
SELECT id, email, role, created_at FROM users WHERE email = '79059510009@mail.ru';





