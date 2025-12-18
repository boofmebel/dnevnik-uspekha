"""
Сервис аутентификации
Согласно rules.md: бизнес-логика в services
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from core.security.jwt import create_access_token, create_refresh_token
from core.security.password import hash_password, verify_password
from repositories.user_repository import UserRepository
from models.user import UserRole


class AuthService:
    """Сервис для работы с аутентификацией"""
    
    def __init__(self, session: AsyncSession):
        self.user_repo = UserRepository(session)
        self.session = session
    
    async def register(self, email: str, password: str, role: str = "parent") -> dict:
        """Регистрация нового пользователя"""
        # Проверка существования пользователя
        existing_user = await self.user_repo.get_by_email(email)
        if existing_user:
            raise ValueError("Пользователь с таким email уже существует")
        
        # Хеширование пароля
        password_hash = hash_password(password)
        
        # Создание пользователя
        user = await self.user_repo.create({
            "email": email,
            "password_hash": password_hash,
            "role": UserRole(role)
        })
        
        return {
            "id": user.id,
            "email": user.email,
            "role": user.role
        }
    
    async def authenticate(self, email: str, password: str) -> Optional[dict]:
        """Аутентификация пользователя"""
        user = await self.user_repo.get_by_email(email)
        if not user:
            return None
        
        # Проверка пароля
        if not verify_password(password, user.password_hash):
            return None
        
        return {
            "id": user.id,
            "email": user.email,
            "role": user.role
        }
    
    def create_access_token(self, user_id: int) -> str:
        """Создание access token"""
        return create_access_token({"sub": str(user_id)})
    
    def create_refresh_token(self, user_id: int) -> str:
        """Создание refresh token"""
        return create_refresh_token({"sub": str(user_id)})
    
    async def save_refresh_token(self, user_id: int, token: str):
        """Сохранение refresh token в БД (согласно rules.md)"""
        # В реальной реализации сохранить в таблицу refresh_tokens
        pass
    
    async def refresh_token_rotation(self) -> tuple[Optional[str], Optional[str]]:
        """Ротация refresh token (согласно rules.md)"""
        # В реальной реализации:
        # 1. Проверить старый refresh token
        # 2. Отозвать его
        # 3. Создать новый access и refresh token
        return None, None
    
    async def revoke_refresh_token(self):
        """Отзыв refresh token"""
        # В реальной реализации пометить токен как отозванный в БД
        pass

