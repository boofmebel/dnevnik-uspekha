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
    SECRET_KEY: str  # Обязательно из переменных окружения
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15  # Согласно rules.md: 5-15 минут
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    
    # CORS (согласно rules.md: не использовать * в проде)
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "https://yourdomain.com"  # Заменить на реальный домен
    ]
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1", "yourdomain.com"]
    
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
        case_sensitive = True


settings = Settings()

