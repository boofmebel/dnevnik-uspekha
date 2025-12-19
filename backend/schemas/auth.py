"""
Pydantic схемы для аутентификации
Согласно rules.md: schemas для request/response
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class LoginRequest(BaseModel):
    """Запрос на вход (по email или телефону)"""
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    password: str
    
    @classmethod
    def model_validate(cls, obj, *, strict=None, from_attributes=None, context=None):
        """Валидация: должен быть указан либо email, либо phone"""
        instance = super().model_validate(obj, strict=strict, from_attributes=from_attributes, context=context)
        if not instance.email and not instance.phone:
            raise ValueError("Необходимо указать email или номер телефона")
        return instance


class RegisterRequest(BaseModel):
    """Запрос на регистрацию по номеру телефона"""
    phone: str = Field(..., description="Номер телефона в формате +7XXXXXXXXXX")
    name: str = Field(..., min_length=2, description="Имя пользователя (минимум 2 символа)")
    password: str = Field(..., min_length=8, description="Пароль минимум 8 символов")
    role: str = Field(default="parent", pattern="^(parent|admin|child)$", description="Роль пользователя")


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


class AdminLoginRequest(BaseModel):
    """Запрос на вход админа по телефону"""
    phone: str = Field(..., description="Номер телефона (79059510009)")
    password: str = Field(..., description="Пароль администратора")

