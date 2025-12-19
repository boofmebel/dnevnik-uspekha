"""
Настройка логирования
Согласно rules.md: JSON логи для продакшена
"""
import logging
import sys
from core.config import settings

try:
    from pythonjsonlogger import jsonlogger
    JSON_LOGGER_AVAILABLE = True
except ImportError:
    JSON_LOGGER_AVAILABLE = False


def setup_logging():
    """Настройка логирования в зависимости от окружения"""
    root_logger = logging.getLogger()
    
    # Удаляем существующие обработчики
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Создаем обработчик
    handler = logging.StreamHandler(sys.stdout)
    
    # Настраиваем формат в зависимости от настроек
    if settings.LOG_FORMAT == "json" and JSON_LOGGER_AVAILABLE:
        # JSON формат для продакшена
        formatter = jsonlogger.JsonFormatter(
            '%(asctime)s %(name)s %(levelname)s %(message)s %(pathname)s %(lineno)d',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    else:
        # Обычный формат для разработки
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
    
    # Настраиваем логирование для сторонних библиотек
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
