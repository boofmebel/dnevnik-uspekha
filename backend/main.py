"""
Главный файл FastAPI приложения
Согласно rules.md: async-first, security, production-ready
"""
import logging
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from sqlalchemy.exc import OperationalError, DisconnectionError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import asyncpg

from core.config import settings
from core.database import get_db
from core.exceptions import setup_exception_handlers
from routers import auth, users, children, tasks, stars, piggy, settings as settings_router, weekly_stats, diary, wishlist, legal, subscription, support, admin, parent, staff

# Настройка логирования (согласно rules.md: JSON логи)
from core.logging_config import setup_logging
setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Дневник успеха API",
    description="Backend API для приложения Дневник успеха",
    version="1.0.0",
    docs_url="/api/docs" if settings.DEBUG else None,
    redoc_url="/api/redoc" if settings.DEBUG else None,
)

# Настройка CORS (согласно rules.md: не использовать * в проде)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["Content-Type", "Authorization", "X-CSRF-Token", "X-Requested-With"],
)

# Trusted Host Middleware (защита от Host header attacks)
if not settings.DEBUG:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS
    )

# Настройка обработчиков исключений
setup_exception_handlers(app)

# Обработчик для HTTPException - всегда возвращает JSON
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Обработчик HTTPException - всегда возвращает JSON"""
    # Если detail - это список (для валидации), преобразуем в строку
    detail = exc.detail
    if isinstance(detail, list):
        detail = "; ".join([str(d) for d in detail])
    elif not isinstance(detail, str):
        detail = str(detail) if detail else "Произошла ошибка"
    
    logger.error(f"HTTPException [{exc.status_code}]: {detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": detail,
            "status_code": exc.status_code
        }
    )

# Настройка rate limiting (согласно rules.md)
from core.middleware.rate_limit import limiter, RateLimitExceeded, _rate_limit_exceeded_handler
from slowapi.middleware import SlowAPIMiddleware
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Настройка CSRF защиты (согласно rules.md)
from core.middleware.csrf_middleware import CSRFMiddleware
app.add_middleware(CSRFMiddleware)

# Обработка всех необработанных исключений
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Глобальный обработчик исключений - всегда возвращает JSON"""
    # Если это HTTPException, пробрасываем его дальше (он обработается отдельным обработчиком)
    if isinstance(exc, HTTPException):
        raise exc
    
    error_str = str(exc)
    error_type = type(exc).__name__
    
    # Логируем ошибку
    logger.error(f"Необработанное исключение: {error_type}: {error_str}", exc_info=True)
    
    # Проверяем, является ли это ошибкой подключения к БД
    is_db_error = (
        "Connection refused" in error_str or
        "ConnectionRefusedError" in error_type or
        "OperationalError" in error_type or
        "DisconnectionError" in error_type or
        "asyncpg" in error_str.lower() or
        "database" in error_str.lower()
    )
    
    # Для админки при ошибке БД возвращаем пустой массив
    if is_db_error and "/api/admin" in str(request.url):
        logger.error(f"Ошибка подключения к БД в админке: {exc}", exc_info=True)
        return JSONResponse(
            status_code=200,  # Возвращаем 200 с пустым массивом
            content=[]
        )
    
    # Для всех остальных ошибок возвращаем JSON с деталями
    # В проде не показываем детали ошибки, только в DEBUG режиме
    if settings.DEBUG:
        detail = f"{error_type}: {error_str}"
    else:
        detail = "Внутренняя ошибка сервера"
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": detail,
            "error": error_type,
            "message": error_str if settings.DEBUG else "Произошла внутренняя ошибка сервера"
        }
    )

# Подключение роутеров
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(children.router, prefix="/api/children", tags=["children"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])
app.include_router(stars.router, prefix="/api/stars", tags=["stars"])
app.include_router(piggy.router, prefix="/api/piggy", tags=["piggy"])
app.include_router(settings_router.router, prefix="/api/settings", tags=["settings"])
app.include_router(weekly_stats.router, prefix="/api/stats", tags=["stats"])
app.include_router(diary.router, prefix="/api/diary", tags=["diary"])
app.include_router(wishlist.router, prefix="/api/wishlist", tags=["wishlist"])
app.include_router(legal.router, prefix="/api/legal", tags=["legal"])
app.include_router(subscription.router, prefix="/api/subscription", tags=["subscription"])
app.include_router(support.router, prefix="/api/support", tags=["support"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(parent.router, prefix="/api/parent", tags=["parent"])
app.include_router(staff.router, prefix="/api/staff", tags=["staff"])


@app.get("/health")
async def health_check():
    """Health check endpoint для мониторинга"""
    return {"status": "ok", "version": "1.0.0"}


@app.get("/ready")
async def ready_check(db: AsyncSession = Depends(get_db)):
    """
    Readiness check endpoint для мониторинга
    Согласно rules.md: проверка готовности БД
    """
    try:
        # Проверяем подключение к БД
        from sqlalchemy import text
        await db.execute(text("SELECT 1"))
        return {"status": "ready", "database": "connected"}
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise HTTPException(status_code=503, detail="Database not ready")


# Обслуживание статических файлов
frontend_path = Path(__file__).parent.parent / "frontend"
static_path = frontend_path / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Обслуживание статических файлов из src (JS, CSS)
src_path = frontend_path / "src"
if src_path.exists():
    app.mount("/src", StaticFiles(directory=str(src_path)), name="src")

# Обслуживание index.html для SPA маршрутов
@app.get("/")
async def root():
    """Корневой endpoint - возвращает index.html для SPA"""
    index_file = frontend_path / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return {"message": "Дневник успеха API", "version": "1.0.0"}

# Catch-all для SPA маршрутов (должен быть последним)
@app.get("/{path:path}")
async def serve_spa(path: str, request: Request):
    """Catch-all для SPA маршрутов - возвращает index.html для всех не-API запросов"""
    # Пропускаем API запросы
    if path.startswith("api/") or path.startswith("health") or path.startswith("ready"):
        raise HTTPException(status_code=404, detail="Not Found")
    
    # Пропускаем статические файлы
    if path.startswith("static/") or path.startswith("src/"):
        raise HTTPException(status_code=404, detail="Not Found")
    
    # Возвращаем index.html для всех остальных маршрутов
    index_file = frontend_path / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    
    raise HTTPException(status_code=404, detail="Not Found")


@app.get("/api/debug/token")
async def debug_token(request: Request):
    """Временный эндпоинт для диагностики токена (только для отладки!)"""
    # Согласно rules.md: защита debug endpoint
    if not settings.DEBUG:
        raise HTTPException(status_code=404, detail="Not found")
    from fastapi import Header
    from core.security.jwt import verify_token
    
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return {"error": "No token provided", "header": auth_header[:50]}
    
    token = auth_header.replace("Bearer ", "").strip()
    
    try:
        # Пробуем декодировать без проверки подписи
        from jose import jwt
        from core.config import settings
        unverified = jwt.decode(token, options={"verify_signature": False})
        
        # Пробуем с проверкой
        verified = verify_token(token)
        
        return {
            "token_length": len(token),
            "token_preview": token[:50] + "...",
            "unverified_payload": unverified,
            "verified_payload": verified,
            "secret_key_length": len(settings.SECRET_KEY) if settings.SECRET_KEY else 0,
            "algorithm": settings.ALGORITHM
        }
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}

