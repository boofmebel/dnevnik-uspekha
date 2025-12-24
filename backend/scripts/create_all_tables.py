"""
Профессиональный скрипт для создания всех таблиц БД
Создает полную структуру согласно моделям и миграциям
"""
import asyncio
import sys
import os
from pathlib import Path

# Добавляем корневую директорию в путь
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import text
from core.database import engine


async def create_all_tables():
    """Создает все таблицы БД согласно моделям"""
    async with engine.begin() as conn:
        print("🚀 Начинаю создание структуры БД...\n")
        
        # 1. Создание ENUM типов
        print("📋 Создание ENUM типов...")
        await conn.execute(text("""
            DO $$ BEGIN
                CREATE TYPE gender AS ENUM ('girl', 'boy', 'none');
            EXCEPTION
                WHEN duplicate_object THEN null;
            END $$;
        """))
        
        await conn.execute(text("""
            DO $$ BEGIN
                CREATE TYPE tasktype AS ENUM ('checklist', 'kanban');
            EXCEPTION
                WHEN duplicate_object THEN null;
            END $$;
        """))
        
        await conn.execute(text("""
            DO $$ BEGIN
                CREATE TYPE taskstatus AS ENUM ('todo', 'doing', 'done');
            EXCEPTION
                WHEN duplicate_object THEN null;
            END $$;
        """))
        print("✅ ENUM типы созданы\n")
        
        # 2. Таблица tasks
        print("📝 Создание таблицы tasks...")
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS tasks (
                id SERIAL PRIMARY KEY,
                child_id INTEGER NOT NULL REFERENCES children(id) ON DELETE CASCADE,
                text VARCHAR NOT NULL,
                task_type tasktype NOT NULL,
                status taskstatus,
                completed BOOLEAN NOT NULL DEFAULT FALSE,
                stars INTEGER NOT NULL DEFAULT 0,
                position INTEGER DEFAULT 0,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE,
                CONSTRAINT fk_tasks_child FOREIGN KEY (child_id) REFERENCES children(id) ON DELETE CASCADE
            )
        """))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_tasks_id ON tasks(id)"))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_tasks_child_id ON tasks(child_id)"))
        print("✅ Таблица tasks создана\n")
        
        # 3. Таблицы для звёзд
        print("⭐ Создание таблиц для звёзд...")
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS stars (
                id SERIAL PRIMARY KEY,
                child_id INTEGER NOT NULL REFERENCES children(id) ON DELETE CASCADE,
                today INTEGER NOT NULL DEFAULT 0,
                total INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE,
                CONSTRAINT fk_stars_child FOREIGN KEY (child_id) REFERENCES children(id) ON DELETE CASCADE,
                CONSTRAINT uq_stars_child_id UNIQUE (child_id)
            )
        """))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_stars_id ON stars(id)"))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_stars_child_id ON stars(child_id)"))
        
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS star_history (
                id SERIAL PRIMARY KEY,
                star_id INTEGER NOT NULL REFERENCES stars(id) ON DELETE CASCADE,
                description VARCHAR NOT NULL,
                stars INTEGER NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT fk_star_history_star FOREIGN KEY (star_id) REFERENCES stars(id) ON DELETE CASCADE
            )
        """))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_star_history_id ON star_history(id)"))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_star_history_star_id ON star_history(star_id)"))
        
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS star_streaks (
                id SERIAL PRIMARY KEY,
                star_id INTEGER NOT NULL REFERENCES stars(id) ON DELETE CASCADE,
                current INTEGER NOT NULL DEFAULT 0,
                last_date VARCHAR,
                best INTEGER NOT NULL DEFAULT 0,
                claimed_rewards TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE,
                CONSTRAINT fk_star_streaks_star FOREIGN KEY (star_id) REFERENCES stars(id) ON DELETE CASCADE,
                CONSTRAINT uq_star_streaks_star_id UNIQUE (star_id)
            )
        """))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_star_streaks_id ON star_streaks(id)"))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_star_streaks_star_id ON star_streaks(star_id)"))
        print("✅ Таблицы для звёзд созданы\n")
        
        # 4. Таблицы для копилки
        print("🐷 Создание таблиц для копилки...")
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS piggies (
                id SERIAL PRIMARY KEY,
                child_id INTEGER NOT NULL REFERENCES children(id) ON DELETE CASCADE,
                amount NUMERIC(10, 2) NOT NULL DEFAULT 0,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE,
                CONSTRAINT fk_piggies_child FOREIGN KEY (child_id) REFERENCES children(id) ON DELETE CASCADE,
                CONSTRAINT uq_piggies_child_id UNIQUE (child_id)
            )
        """))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_piggies_id ON piggies(id)"))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_piggies_child_id ON piggies(child_id)"))
        
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS piggy_goals (
                id SERIAL PRIMARY KEY,
                piggy_id INTEGER NOT NULL REFERENCES piggies(id) ON DELETE CASCADE,
                name VARCHAR NOT NULL DEFAULT '',
                amount NUMERIC(10, 2) NOT NULL DEFAULT 0,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE,
                CONSTRAINT fk_piggy_goals_piggy FOREIGN KEY (piggy_id) REFERENCES piggies(id) ON DELETE CASCADE,
                CONSTRAINT uq_piggy_goals_piggy_id UNIQUE (piggy_id)
            )
        """))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_piggy_goals_id ON piggy_goals(id)"))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_piggy_goals_piggy_id ON piggy_goals(piggy_id)"))
        
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS piggy_history (
                id SERIAL PRIMARY KEY,
                piggy_id INTEGER NOT NULL REFERENCES piggies(id) ON DELETE CASCADE,
                type VARCHAR NOT NULL,
                amount NUMERIC(10, 2) NOT NULL,
                description VARCHAR,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT fk_piggy_history_piggy FOREIGN KEY (piggy_id) REFERENCES piggies(id) ON DELETE CASCADE
            )
        """))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_piggy_history_id ON piggy_history(id)"))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_piggy_history_piggy_id ON piggy_history(piggy_id)"))
        print("✅ Таблицы для копилки созданы\n")
        
        # 5. Таблица diary_entries
        print("📔 Создание таблицы diary_entries...")
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS diary_entries (
                id SERIAL PRIMARY KEY,
                child_id INTEGER NOT NULL REFERENCES children(id) ON DELETE CASCADE,
                title VARCHAR,
                content TEXT NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE,
                CONSTRAINT fk_diary_entries_child FOREIGN KEY (child_id) REFERENCES children(id) ON DELETE CASCADE
            )
        """))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_diary_entries_id ON diary_entries(id)"))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_diary_entries_child_id ON diary_entries(child_id)"))
        print("✅ Таблица diary_entries создана\n")
        
        # 6. Таблица wishlist_items
        print("🎁 Создание таблицы wishlist_items...")
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS wishlist_items (
                id SERIAL PRIMARY KEY,
                child_id INTEGER NOT NULL REFERENCES children(id) ON DELETE CASCADE,
                name VARCHAR NOT NULL,
                price NUMERIC(10, 2),
                achieved BOOLEAN NOT NULL DEFAULT FALSE,
                position INTEGER DEFAULT 0,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE,
                CONSTRAINT fk_wishlist_items_child FOREIGN KEY (child_id) REFERENCES children(id) ON DELETE CASCADE
            )
        """))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_wishlist_items_id ON wishlist_items(id)"))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_wishlist_items_child_id ON wishlist_items(child_id)"))
        print("✅ Таблица wishlist_items создана\n")
        
        # 7. Таблица weekly_stats
        print("📊 Создание таблицы weekly_stats...")
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS weekly_stats (
                id SERIAL PRIMARY KEY,
                child_id INTEGER NOT NULL REFERENCES children(id) ON DELETE CASCADE,
                date VARCHAR NOT NULL,
                stars INTEGER NOT NULL DEFAULT 0,
                tasks_completed INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE,
                CONSTRAINT fk_weekly_stats_child FOREIGN KEY (child_id) REFERENCES children(id) ON DELETE CASCADE
            )
        """))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_weekly_stats_id ON weekly_stats(id)"))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_weekly_stats_child_id ON weekly_stats(child_id)"))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_weekly_stats_date ON weekly_stats(date)"))
        print("✅ Таблица weekly_stats создана\n")
        
        # 8. Обновление таблицы settings (добавление полей из миграции 002)
        print("⚙️  Обновление таблицы settings...")
        # Проверяем существование колонок
        result = await conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'settings' AND column_name = 'max_daily_tasks'
        """))
        if not result.scalar():
            await conn.execute(text("""
                ALTER TABLE settings 
                ADD COLUMN max_daily_tasks INTEGER NOT NULL DEFAULT 10
            """))
            print("  ✅ Добавлено поле max_daily_tasks")
        
        result = await conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'settings' AND column_name = 'stars_per_task'
        """))
        if not result.scalar():
            await conn.execute(text("""
                ALTER TABLE settings 
                ADD COLUMN stars_per_task INTEGER NOT NULL DEFAULT 1
            """))
            print("  ✅ Добавлено поле stars_per_task")
        print("✅ Таблица settings обновлена\n")
        
        # 9. Таблица family_rules
        print("📜 Создание таблицы family_rules...")
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS family_rules (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                rules TEXT NOT NULL DEFAULT '[]',
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE,
                CONSTRAINT fk_family_rules_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                CONSTRAINT uq_family_rules_user_id UNIQUE (user_id)
            )
        """))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_family_rules_id ON family_rules(id)"))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_family_rules_user_id ON family_rules(user_id)"))
        print("✅ Таблица family_rules создана\n")
        
        # 10. Таблица subscriptions
        print("💳 Создание таблицы subscriptions...")
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS subscriptions (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                start_date TIMESTAMP WITH TIME ZONE NOT NULL,
                end_date TIMESTAMP WITH TIME ZONE NOT NULL,
                is_active BOOLEAN NOT NULL DEFAULT TRUE,
                refund_requested BOOLEAN NOT NULL DEFAULT FALSE,
                refund_reason VARCHAR,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE,
                CONSTRAINT fk_subscriptions_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                CONSTRAINT uq_subscriptions_user_id UNIQUE (user_id)
            )
        """))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_subscriptions_id ON subscriptions(id)"))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_subscriptions_user_id ON subscriptions(user_id)"))
        print("✅ Таблица subscriptions создана\n")
        
        # 11. Создание ENUM для notifications
        print("🔔 Создание ENUM типов для notifications...")
        await conn.execute(text("""
            DO $$ BEGIN
                CREATE TYPE notificationtype AS ENUM ('subscription', 'refund', 'complaint', 'consent', 'system');
            EXCEPTION
                WHEN duplicate_object THEN null;
            END $$;
        """))
        
        await conn.execute(text("""
            DO $$ BEGIN
                CREATE TYPE notificationstatus AS ENUM ('pending', 'sent', 'read', 'failed');
            EXCEPTION
                WHEN duplicate_object THEN null;
            END $$;
        """))
        print("✅ ENUM типы для notifications созданы\n")
        
        # 12. Таблица notifications
        print("📢 Создание таблицы notifications...")
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS notifications (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                subscription_id INTEGER REFERENCES subscriptions(id) ON DELETE SET NULL,
                type notificationtype NOT NULL,
                message TEXT NOT NULL,
                status notificationstatus NOT NULL DEFAULT 'pending',
                meta_data TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE,
                CONSTRAINT fk_notifications_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                CONSTRAINT fk_notifications_subscription FOREIGN KEY (subscription_id) REFERENCES subscriptions(id) ON DELETE SET NULL
            )
        """))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_notifications_id ON notifications(id)"))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_notifications_user_id ON notifications(user_id)"))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_notifications_subscription_id ON notifications(subscription_id)"))
        print("✅ Таблица notifications создана\n")
        
        # 13. Таблица parent_consents
        print("✅ Создание таблицы parent_consents...")
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS parent_consents (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                child_id INTEGER NOT NULL REFERENCES children(id) ON DELETE CASCADE,
                consent_given BOOLEAN NOT NULL DEFAULT FALSE,
                consent_date TIMESTAMP WITH TIME ZONE,
                ip_address VARCHAR,
                user_agent TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE,
                CONSTRAINT fk_parent_consents_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                CONSTRAINT fk_parent_consents_child FOREIGN KEY (child_id) REFERENCES children(id) ON DELETE CASCADE
            )
        """))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_parent_consents_id ON parent_consents(id)"))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_parent_consents_user_id ON parent_consents(user_id)"))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_parent_consents_child_id ON parent_consents(child_id)"))
        print("✅ Таблица parent_consents создана\n")
        
        # 14. Таблица staff_users
        print("👔 Создание таблицы staff_users...")
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS staff_users (
                id SERIAL PRIMARY KEY,
                phone VARCHAR(20) NOT NULL UNIQUE,
                email VARCHAR(255) UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                role VARCHAR(50) NOT NULL,
                last_login TIMESTAMP WITH TIME ZONE,
                is_active BOOLEAN NOT NULL DEFAULT TRUE,
                two_fa_secret VARCHAR(255),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE
            )
        """))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_staff_users_id ON staff_users(id)"))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_staff_users_phone ON staff_users(phone)"))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_staff_users_email ON staff_users(email)"))
        print("✅ Таблица staff_users создана\n")
        
        print("🎉 Все таблицы успешно созданы!")
        print("\n📋 Созданные таблицы:")
        print("  ✅ tasks")
        print("  ✅ stars, star_history, star_streaks")
        print("  ✅ piggies, piggy_goals, piggy_history")
        print("  ✅ diary_entries")
        print("  ✅ wishlist_items")
        print("  ✅ weekly_stats")
        print("  ✅ settings (обновлена)")
        print("  ✅ family_rules")
        print("  ✅ subscriptions")
        print("  ✅ notifications")
        print("  ✅ parent_consents")
        print("  ✅ staff_users")


if __name__ == "__main__":
    # Загружаем DATABASE_URL из .env
    env_file = backend_dir / ".env"
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                if line.startswith('DATABASE_URL='):
                    os.environ['DATABASE_URL'] = line.split('=', 1)[1].strip()
                    break
    
    asyncio.run(create_all_tables())

