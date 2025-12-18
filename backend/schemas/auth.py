"""
Pydantic схемы для аутентификации
Согласно rules.md: schemas для request/response
"""
from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    """Запрос на вход"""
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    """Ответ на вход"""
    access_token: str
    token_type: str = "bearer"
    user: dict


class RefreshRequest(BaseModel):
    """Запрос на обновление токена"""
    refresh_token: str

