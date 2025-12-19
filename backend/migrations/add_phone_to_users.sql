-- Миграция: добавление поля phone в таблицу users
-- Выполнить: psql -d your_database -f add_phone_to_users.sql

-- Добавляем поле phone (опциональное, уникальное)
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS phone VARCHAR UNIQUE;

-- Создаем индекс для быстрого поиска по телефону
CREATE INDEX IF NOT EXISTS ix_users_phone ON users(phone);

-- Делаем email опциональным (если еще не опционально)
-- Внимание: это может вызвать проблемы, если в БД уже есть данные
-- ALTER TABLE users ALTER COLUMN email DROP NOT NULL;

