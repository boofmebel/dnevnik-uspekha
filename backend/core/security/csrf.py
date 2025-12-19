"""
CSRF защита
Согласно rules.md: double-submit CSRF token или Anti-CSRF header
"""
import secrets
from typing import Optional
from fastapi import Request, HTTPException, status


class CSRFProtection:
    """Класс для защиты от CSRF атак"""
    
    @staticmethod
    def generate_token() -> str:
        """Генерация CSRF токена"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def validate_token(request: Request, token: Optional[str] = None) -> bool:
        """
        Валидация CSRF токена
        Использует double-submit cookie pattern
        """
        # Получаем токен из cookie
        cookie_token = request.cookies.get("csrf_token")
        
        # Получаем токен из заголовка или тела запроса
        header_token = request.headers.get("X-CSRF-Token")
        form_token = token  # Если передан напрямую
        
        submitted_token = header_token or form_token
        
        if not cookie_token or not submitted_token:
            return False
        
        # Сравниваем токены (double-submit pattern)
        return secrets.compare_digest(cookie_token, submitted_token)
    
    @staticmethod
    def require_csrf_token(request: Request, token: Optional[str] = None):
        """
        Проверка CSRF токена с выбросом исключения при ошибке
        """
        if not CSRFProtection.validate_token(request, token):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="CSRF token validation failed"
            )

