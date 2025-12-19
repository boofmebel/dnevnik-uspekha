"""
CSRF защита middleware
Согласно rules.md: double-submit CSRF или Anti-CSRF header
"""
import secrets
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from typing import Callable


class CSRFMiddleware(BaseHTTPMiddleware):
    """
    CSRF защита через double-submit token
    Токен генерируется и отправляется в cookie и header
    """
    
    def __init__(self, app, exempt_paths: list = None):
        super().__init__(app)
        self.exempt_paths = exempt_paths or [
            "/health",
            "/ready",
            "/api/docs",
            "/api/redoc",
            "/api/openapi.json"
        ]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Пропускаем exempt paths
        if any(request.url.path.startswith(path) for path in self.exempt_paths):
            return await call_next(request)
        
        # Пропускаем GET, HEAD, OPTIONS запросы (безопасные методы)
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return await call_next(request)
        
        # Для POST, PUT, DELETE, PATCH проверяем CSRF токен
        if request.method in ["POST", "PUT", "DELETE", "PATCH"]:
            # Получаем токен из cookie
            csrf_token_cookie = request.cookies.get("csrf_token")
            
            # Получаем токен из header
            csrf_token_header = request.headers.get("X-CSRF-Token")
            
            # Если токена нет в cookie, генерируем новый
            if not csrf_token_cookie:
                csrf_token_cookie = secrets.token_urlsafe(32)
            
            # Проверяем совпадение токенов
            if csrf_token_cookie != csrf_token_header:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="CSRF token mismatch"
                )
        
        # Выполняем запрос
        response = await call_next(request)
        
        # Устанавливаем CSRF токен в cookie, если его нет
        if "csrf_token" not in request.cookies:
            response.set_cookie(
                key="csrf_token",
                value=csrf_token_cookie,
                httponly=False,  # Должен быть доступен для JavaScript
                secure=True,  # Только HTTPS
                samesite="strict",
                max_age=3600  # 1 час
            )
        
        return response
