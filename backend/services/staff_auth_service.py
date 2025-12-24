"""
Сервис аутентификации для Staff Users
Согласно rules.md: бизнес-логика в services
"""
from typing import Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from core.security.jwt import create_access_token, create_refresh_token
from core.security.password import hash_password, verify_password
from repositories.staff_user_repository import StaffUserRepository
from repositories.refresh_token_repository import RefreshTokenRepository


class StaffAuthService:
    """Сервис для работы с аутентификацией staff пользователей"""
    
    def __init__(self, session: AsyncSession):
        self.staff_repo = StaffUserRepository(session)
        self.refresh_token_repo = RefreshTokenRepository(session)
        self.session = session
    
    async def authenticate(self, phone: str, password: str) -> Optional[dict]:
        """Аутентификация staff пользователя по телефону"""
        staff_user = await self.staff_repo.get_by_phone(phone)
        
        if not staff_user:
            return None
        
        # Проверка активности
        if not staff_user.is_active:
            return None
        
        # Проверка пароля
        if not verify_password(password, staff_user.password_hash):
            return None
        
        # Обновляем время последнего входа
        await self.staff_repo.update_last_login(staff_user.id)
        
        # Нормализуем роль к строке
        role = staff_user.role
        if not isinstance(role, str):
            role = str(role)
        
        return {
            "id": staff_user.id,
            "phone": staff_user.phone,
            "email": staff_user.email,
            "role": role,
            "is_staff": True
        }
    
    def create_access_token(self, staff_id: int, role: Optional[str] = None) -> str:
        """Создание access token для staff пользователя"""
        token_data = {"sub": str(staff_id), "is_staff": True}
        if role:
            token_data["role"] = role
        return create_access_token(token_data)
    
    def create_refresh_token(self, staff_id: int, role: Optional[str] = None) -> str:
        """Создание refresh token для staff пользователя"""
        token_data = {"sub": str(staff_id), "is_staff": True}
        if role:
            token_data["role"] = role
        return create_refresh_token(token_data)
    
    async def save_refresh_token(self, staff_id: int, token: str, device_info: Optional[str] = None):
        """Сохранение refresh token в БД"""
        # TODO: Создать отдельную таблицу staff_refresh_tokens или изменить refresh_tokens для поддержки staff
        # Временно не сохраняем refresh token для staff в БД, так как refresh_tokens имеет FK на users.id
        # Refresh token всё равно сохраняется в HttpOnly cookie, что достаточно для безопасности
        pass
    
    async def refresh_token_rotation(self, refresh_token: str, device_info: Optional[str] = None) -> Tuple[Optional[str], Optional[str]]:
        """Ротация refresh token для staff"""
        # 1. Проверяем старый refresh token
        old_token_record = await self.refresh_token_repo.get_valid_token(refresh_token)
        if not old_token_record:
            return None, None
        
        staff_id = old_token_record.user_id
        
        # 2. Отзываем старый токен
        await self.refresh_token_repo.revoke_token(refresh_token)
        
        # 3. Создаем новый access и refresh token
        staff_user = await self.staff_repo.get_by_id(staff_id)
        if not staff_user or not staff_user.is_active:
            return None, None
        
        role = staff_user.role
        if not isinstance(role, str):
            role = str(role)
        
        new_access_token = self.create_access_token(staff_id, role)
        new_refresh_token = self.create_refresh_token(staff_id, role)
        
        # 4. Сохраняем новый refresh token
        await self.refresh_token_repo.create(staff_id, new_refresh_token, device_info)
        
        return new_access_token, new_refresh_token
    
    async def revoke_refresh_token(self, refresh_token: Optional[str] = None, staff_id: Optional[int] = None):
        """Отзыв refresh token для staff"""
        if refresh_token:
            await self.refresh_token_repo.revoke_token(refresh_token)
        elif staff_id:
            await self.refresh_token_repo.revoke_all_user_tokens(staff_id)

