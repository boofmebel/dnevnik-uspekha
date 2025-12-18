-- Создание администратора для 79059510009@mail.ru
-- Пароль: Admin123!

INSERT INTO users (email, password_hash, role, created_at)
VALUES (
  '79059510009@mail.ru',
  '$2b$12$qwla5dyJsTFjjTxUm3dwSObs.OV5jTIw/oLfNSDBFbAFG3p7rlJBW',
  'admin',
  NOW()
)
ON CONFLICT (email) DO UPDATE
SET role = 'admin',
    password_hash = EXCLUDED.password_hash,
    updated_at = NOW();

-- Проверка результата
SELECT id, email, role, created_at FROM users WHERE email = '79059510009@mail.ru';

