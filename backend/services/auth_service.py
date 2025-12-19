"""
Сервис аутентификации
Согласно rules.md: бизнес-логика в services
"""
from typing import Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from core.security.jwt import create_access_token, create_refresh_token, verify_token
from core.security.password import hash_password, verify_password
from repositories.user_repository import UserRepository
from repositories.refresh_token_repository import RefreshTokenRepository
from models.user import UserRole
from fastapi import Request


class AuthService:
    """Сервис для работы с аутентификацией"""
    
    def __init__(self, session: AsyncSession):
        self.user_repo = UserRepository(session)
        self.refresh_token_repo = RefreshTokenRepository(session)
        self.session = session
    
    async def register(self, phone: str, password: str, name: str, role: str = "parent", email: Optional[str] = None) -> dict:
        """Регистрация нового пользователя по номеру телефона"""
        from core.utils.phone_validator import normalize_phone, validate_phone
        
        # Нормализуем и валидируем номер телефона
        normalized_phone = normalize_phone(phone)
        if not validate_phone(normalized_phone):
            raise ValueError("Неверный формат номера телефона. Используйте формат +7XXXXXXXXXX")
        
        # Валидация имени
        if not name or len(name.strip()) < 2:
            raise ValueError("Имя должно содержать минимум 2 символа")
        
        # Проверка существования пользователя по телефону
        existing_user = await self.user_repo.get_by_phone(normalized_phone)
        if existing_user:
            raise ValueError("Пользователь с таким номером телефона уже существует")
        
        # Если указан email, проверяем его уникальность
        if email and email.strip():
            existing_email_user = await self.user_repo.get_by_email(email.strip())
            if existing_email_user:
                raise ValueError("Пользователь с таким email уже существует")
        
        # Хеширование пароля
        password_hash = hash_password(password)
        
        # Создание пользователя
        user_data = {
            "phone": normalized_phone,
            "name": name.strip(),
            "password_hash": password_hash,
            "role": role
        }
        if email:
            user_data["email"] = email.strip() if email else None
        
        try:
            user = await self.user_repo.create(user_data)
        except IntegrityError as e:
            # Обработка дубликатов на уровне БД (race condition protection)
            error_str = str(e.orig) if hasattr(e, 'orig') else str(e)
            if "phone" in error_str.lower() or "ix_users_phone" in error_str.lower():
                raise ValueError("Пользователь с таким номером телефона уже существует")
            elif "email" in error_str.lower() or "ix_users_email" in error_str.lower():
                raise ValueError("Пользователь с таким email уже существует")
            else:
                # Пробрасываем другие IntegrityError
                raise ValueError(f"Ошибка создания пользователя: {error_str}")
        
        # Нормализуем роль к строке
        role = user.role
        if hasattr(role, 'value'):
            role = role.value
        elif not isinstance(role, str):
            role = str(role)
        
        return {
            "id": user.id,
            "phone": user.phone,
            "name": user.name,
            "email": user.email,
            "role": role
        }
    
    async def authenticate(self, email: Optional[str] = None, phone: Optional[str] = None, password: str = "") -> Optional[dict]:
        """Аутентификация пользователя по email или телефону"""
        user = None
        
        if phone:
            from core.utils.phone_validator import normalize_phone
            normalized_phone = normalize_phone(phone)
            user = await self.user_repo.get_by_phone(normalized_phone)
        elif email:
            user = await self.user_repo.get_by_email(email)
        
        if not user:
            return None
        
        # Проверка пароля
        if not verify_password(password, user.password_hash):
            return None
        
        # Нормализуем роль к строке
        role = user.role
        if hasattr(role, 'value'):
            role = role.value
        elif not isinstance(role, str):
            role = str(role)
        
        return {
            "id": user.id,
            "email": user.email,
            "phone": user.phone,
            "role": role
        }
    
    def create_access_token(self, user_id: int, role: Optional[str] = None) -> str:
        """Создание access token с ролью пользователя"""
        token_data = {"sub": str(user_id)}
        if role:
            token_data["role"] = role
        return create_access_token(token_data)
    
    def create_refresh_token(self, user_id: int, role: Optional[str] = None) -> str:
        """Создание refresh token с ролью пользователя"""
        token_data = {"sub": str(user_id)}
        if role:
            token_data["role"] = role
        return create_refresh_token(token_data)
    
    async def save_refresh_token(self, user_id: int, token: str, device_info: Optional[str] = None):
        """Сохранение refresh token в БД (согласно rules.md)"""
        await self.refresh_token_repo.create(user_id, token, device_info=device_info)
    
    async def refresh_token_rotation(self, refresh_token: str, device_info: Optional[str] = None) -> Tuple[Optional[str], Optional[str]]:
        """Ротация refresh token (согласно rules.md)"""
        # 1. Проверяем старый refresh token
        old_token_record = await self.refresh_token_repo.get_valid_token(refresh_token)
        if not old_token_record:
            return None, None
        
        user_id = old_token_record.user_id
        
        # 2. Отзываем старый токен
        await self.refresh_token_repo.revoke_token(refresh_token)
        
        # 3. Создаем новый access и refresh token
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            return None, None
        
        # Нормализуем роль
        role = user.role
        if hasattr(role, 'value'):
            role = role.value
        elif not isinstance(role, str):
            role = str(role)
        
        new_access_token = self.create_access_token(user_id, role)
        new_refresh_token = self.create_refresh_token(user_id, role)
        
        # 4. Сохраняем новый refresh token
        await self.refresh_token_repo.create(user_id, new_refresh_token, device_info)
        
        return new_access_token, new_refresh_token
    
    async def revoke_refresh_token(self, refresh_token: Optional[str] = None, user_id: Optional[int] = None):
        """Отзыв refresh token"""
        if refresh_token:
            await self.refresh_token_repo.revoke_token(refresh_token)
        elif user_id:
            await self.refresh_token_repo.revoke_all_user_tokens(user_id)

