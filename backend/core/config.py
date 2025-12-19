"""
Конфигурация приложения
Согласно rules.md: использование переменных окружения, безопасность
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Основные настройки
    DEBUG: bool = False
    PROJECT_NAME: str = "Дневник успеха"
    VERSION: str = "1.0.0"
    
    # Безопасность
    SECRET_KEY: str = ""  # Обязательно из переменных окружения, но с дефолтом для проверки
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15  # Согласно rules.md: 5-15 минут (было 60, исправлено)
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    
    # Администратор
    ADMIN_PHONE: str = ""  # Номер телефона администратора (из переменных окружения)
    
    # Окружение
    ENVIRONMENT: str = "development"  # development | production
    
    # CORS (согласно rules.md: не использовать * в проде)
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://89.104.74.123:3000",
        "http://89.104.74.123:8080",
        "https://yourdomain.com"  # Заменить на реальный домен
    ]
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1", "89.104.74.123", "yourdomain.com"]
    
    # База данных
    DATABASE_URL: str  # Обязательно из переменных окружения
    # Формат: postgresql+asyncpg://user:password@host:port/dbname
    
    # Redis (для rate limiting и refresh tokens)
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Загрузка файлов (согласно rules.md)
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_DIR: str = "/var/uploads"  # Вне /static
    
    # Логирование
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # Согласно rules.md: JSON логи
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Создаем экземпляр настроек
try:
    settings = Settings()
except Exception as e:
    import warnings
    warnings.warn(f"Ошибка загрузки настроек: {e}. Проверьте .env файл.")
    # Создаем минимальный экземпляр для предотвращения падения
    import os
    settings = Settings(
        SECRET_KEY=os.getenv("SECRET_KEY", ""),
        DATABASE_URL=os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/dnevnik_uspekha")
    )

# Проверка SECRET_KEY при загрузке
if not settings.SECRET_KEY:
    import os
    # Пробуем получить из переменных окружения напрямую
    secret_key = os.getenv("SECRET_KEY")
    if secret_key:
        settings.SECRET_KEY = secret_key
    else:
        import warnings
        import logging
        logger = logging.getLogger(__name__)
        logger.error("⚠️ SECRET_KEY is not set! JWT tokens will not work. Set SECRET_KEY in .env file or environment variables.")
        logger.error("💡 Запустите: python scripts/setup_secrets.py для автоматической настройки")
        warnings.warn("SECRET_KEY is not set! JWT tokens will not work. Set SECRET_KEY in .env file or environment variables.")

