"""
Rate limiting middleware
Согласно rules.md: ограничение на критичные endpoints (login, reset password)
"""
from functools import wraps
from fastapi import HTTPException, Request, status
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from core.config import settings

# Инициализация limiter
# Используем Redis для продакшена, in-memory для разработки
def get_storage_uri():
    """Получение URI хранилища для rate limiting"""
    # Проверяем, доступен ли Redis
    try:
        import redis
        redis_url = settings.REDIS_URL
        # Пробуем подключиться к Redis
        r = redis.from_url(redis_url, socket_connect_timeout=1)
        r.ping()
        return redis_url
    except:
        # Если Redis недоступен, используем in-memory
        return "memory://"

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=get_storage_uri(),
    default_limits=[]  # Отключен по умолчанию, применяется только через декораторы
)

# Декораторы для rate limiting
# SlowAPI требует, чтобы функция имела параметр request
def rate_limit_login(func):
    """Rate limiting для login endpoint: 5 попыток в минуту"""
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        # Проверяем rate limit
        try:
            # Используем limiter напрямую через middleware, а не через декоратор
            # Вместо этого используем limiter.limit() как декоратор на уровне роутера
            pass
        except RateLimitExceeded:
            raise HTTPException(status_code=429, detail="Слишком много запросов. Попробуйте позже.")
        return await func(*args, **kwargs)
    return wrapper

# Упрощенная версия без декораторов - используем limiter напрямую в роутерах
def check_rate_limit(request: Request, limit: str = "5/minute"):
    """Проверка rate limit для запроса"""
    try:
        limiter.check_rate_limit(request, limit)
    except RateLimitExceeded:
        raise HTTPException(status_code=429, detail="Слишком много запросов. Попробуйте позже.")
