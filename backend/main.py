"""
Главный файл FastAPI приложения
Согласно rules.md: async-first, security, production-ready
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from core.config import settings
from core.exceptions import setup_exception_handlers
from routers import auth, users, children, tasks, stars, piggy, settings, weekly_stats, diary, wishlist, legal, subscription, support, admin

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
    allow_headers=["*"],
)

# Trusted Host Middleware (защита от Host header attacks)
if not settings.DEBUG:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS
    )

# Настройка обработчиков исключений
setup_exception_handlers(app)

# Подключение роутеров
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(children.router, prefix="/api/children", tags=["children"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])
app.include_router(stars.router, prefix="/api/stars", tags=["stars"])
app.include_router(piggy.router, prefix="/api/piggy", tags=["piggy"])
app.include_router(settings.router, prefix="/api/settings", tags=["settings"])
app.include_router(weekly_stats.router, prefix="/api/stats", tags=["stats"])
app.include_router(diary.router, prefix="/api/diary", tags=["diary"])
app.include_router(wishlist.router, prefix="/api/wishlist", tags=["wishlist"])
app.include_router(legal.router, prefix="/api/legal", tags=["legal"])
app.include_router(subscription.router, prefix="/api/subscription", tags=["subscription"])
app.include_router(support.router, prefix="/api/support", tags=["support"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])


@app.get("/health")
async def health_check():
    """Health check endpoint для мониторинга"""
    return {"status": "ok", "version": "1.0.0"}


@app.get("/")
async def root():
    """Корневой endpoint"""
    return {"message": "Дневник успеха API", "version": "1.0.0"}

