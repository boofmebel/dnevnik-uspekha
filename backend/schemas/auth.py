"""
Pydantic схемы для аутентификации
Согласно rules.md: schemas для request/response
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class LoginRequest(BaseModel):
    """Запрос на вход"""
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    """Запрос на регистрацию"""
    email: EmailStr
    password: str = Field(..., min_length=8, description="Пароль минимум 8 символов")
    role: str = "parent"  # По умолчанию родитель


class LoginResponse(BaseModel):
    """Ответ на вход"""
    access_token: str
    token_type: str = "bearer"
    user: dict


class RefreshRequest(BaseModel):
    """Запрос на обновление токена"""
    refresh_token: str


class ChildPinRequest(BaseModel):
    """Запрос на вход ребёнка по PIN"""
    child_id: int
    pin: str = Field(..., min_length=4, max_length=6, description="PIN-код (4-6 цифр)")


class ChildQrRequest(BaseModel):
    """Запрос на вход ребёнка по QR-коду"""
    qr_token: str


class ChildAccessResponse(BaseModel):
    """Ответ с данными доступа для ребёнка"""
    child_id: int
    qr_code: str  # Base64 изображение QR-кода
    qr_token: str  # Токен для сканирования
    pin: str  # PIN-код (показывается только один раз)
    pin_set: bool  # Установлен ли PIN
    expires_at: Optional[str] = None  # Срок действия QR-токена

