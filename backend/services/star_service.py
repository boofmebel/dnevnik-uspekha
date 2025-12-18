"""
Сервис для работы со звёздами
Согласно rules.md: бизнес-логика в services
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from repositories.star_repository import StarRepository
from repositories.child_repository import ChildRepository
from repositories.settings_repository import SettingsRepository
from repositories.piggy_repository import PiggyRepository
from schemas.star import StarAddRequest, StarExchangeRequest
from models.star import Star
from core.exceptions import NotFoundError, ValidationError
from decimal import Decimal
import json
from datetime import datetime, timedelta


class StarService:
    """Сервис для работы со звёздами"""
    
    def __init__(self, session: AsyncSession):
        self.star_repo = StarRepository(session)
        self.child_repo = ChildRepository(session)
        self.settings_repo = SettingsRepository(session)
        self.piggy_repo = PiggyRepository(session)
        self.session = session
    
    async def get_stars(self, child_id: int) -> Star:
        """Получение звёзд ребёнка"""
        child = await self.child_repo.get_by_id(child_id)
        if not child:
            raise NotFoundError("Ребёнок не найден")
        
        return await self.star_repo.get_or_create(child_id)
    
    async def add_stars(self, child_id: int, request: StarAddRequest) -> Star:
        """Добавление звёзд"""
        star = await self.get_stars(child_id)
        
        # Обновляем счётчики
        star.today += request.stars
        star.total += request.stars
        
        # Добавляем в историю
        await self.star_repo.add_history(star.id, request.description, request.stars)
        
        await self.session.flush()
        await self.session.refresh(star)
        
        # Проверяем промежуточные награды
        rewards = await self._check_rewards(star)
        
        return {
            "star": star,
            "rewards": rewards
        }
    
    async def exchange_stars(self, child_id: int, request: StarExchangeRequest) -> dict:
        """Обмен звёзд на виртуальную валюту (для конвертации в подарки)"""
        star = await self.get_stars(child_id)
        settings = await self.settings_repo.get_or_create(child_id)
        
        if star.today < request.stars:
            raise ValidationError("Недостаточно звёзд")
        
        # Проверяем кратность
        if request.stars < settings.stars_to_money:
            raise ValidationError(f"Минимум {settings.stars_to_money} звёзд для обмена")
        
        # Вычисляем количество виртуальной валюты (для конвертации в подарки)
        exchanges = request.stars // settings.stars_to_money
        stars_used = exchanges * settings.stars_to_money
        virtual_currency = Decimal(exchanges) * settings.money_per_stars
        
        # Обновляем звёзды
        star.today -= stars_used
        await self.session.flush()
        
        # Добавляем виртуальную валюту в копилку (для конвертации в подарки)
        piggy = await self.piggy_repo.get_or_create(child_id)
        piggy.amount += virtual_currency
        await self.piggy_repo.add_history(
            piggy.id,
            "exchange",
            virtual_currency,
            f"Обмен {stars_used} ⭐ на виртуальную валюту"
        )
        
        await self.session.flush()
        
        return {
            "stars_used": stars_used,
            "virtual_currency": float(virtual_currency),
            "remaining_stars": star.today,
            "note": "Виртуальная валюта может быть конвертирована в подарки по усмотрению родителей"
        }
    
    async def check_streak(self, child_id: int) -> dict:
        """Проверка и обновление серии дней"""
        star = await self.get_stars(child_id)
        streak = await self.star_repo.get_or_create_streak(star.id)
        
        today = datetime.now().date()
        today_str = today.strftime("%Y-%m-%d")
        yesterday = today - timedelta(days=1)
        yesterday_str = yesterday.strftime("%Y-%m-%d")
        
        # Если уже обновляли сегодня, не обновляем
        if streak.last_date == today_str:
            return {"current": streak.current, "bonus": None}
        
        # Проверяем вчерашний день
        if streak.last_date == yesterday_str:
            # Продолжаем серию
            streak.current += 1
            streak.last_date = today_str
            if streak.current > streak.best:
                streak.best = streak.current
        elif streak.last_date and streak.last_date != yesterday_str:
            # Пропущен день, сбрасываем
            streak.current = 1
            streak.last_date = today_str
        else:
            # Первый день
            streak.current = 1
            streak.last_date = today_str
        
        await self.session.flush()
        
        # Проверяем бонусы
        bonus = await self._check_streak_bonus(star, streak)
        
        return {
            "current": streak.current,
            "bonus": bonus
        }
    
    async def _check_rewards(self, star: Star) -> list[dict]:
        """Проверка промежуточных наград"""
        # Получаем claimed_rewards
        streak = await self.star_repo.get_or_create_streak(star.id)
        claimed = json.loads(streak.claimed_rewards) if streak.claimed_rewards else []
        
        # Проверяем награды: 5, 10, 25 звёзд
        rewards_config = {
            5: {"emoji": "🎉", "message": "Можешь выбрать мультик на вечер!"},
            10: {"emoji": "🎁", "message": "Маленький сюрприз"},
            25: {"emoji": "🌟", "message": "Отличная работа!"}
        }
        
        new_rewards = []
        for reward_stars, config in rewards_config.items():
            if star.total >= reward_stars and reward_stars not in claimed:
                claimed.append(reward_stars)
                new_rewards.append({
                    "stars": reward_stars,
                    "emoji": config["emoji"],
                    "message": config["message"]
                })
        
        if new_rewards:
            streak.claimed_rewards = json.dumps(claimed)
            await self.session.flush()
        
        return new_rewards
    
    async def _check_streak_bonus(self, star: Star, streak) -> Optional[dict]:
        """Проверка виртуальных бонусов за серию дней (для конвертации в подарки)"""
        bonuses = {
            3: Decimal("10"),
            7: Decimal("50"),
            14: Decimal("150"),
            30: Decimal("500")
        }
        
        if streak.current in bonuses:
            bonus = bonuses[streak.current]
            piggy = await self.piggy_repo.get_or_create(star.child_id)
            piggy.amount += bonus
            await self.piggy_repo.add_history(
                piggy.id,
                "streak",
                bonus,
                f"🔥 Виртуальный бонус за {streak.current} дней подряд (для конвертации в подарки)"
            )
            await self.session.flush()
            return {
                "days": streak.current,
                "virtual_bonus": float(bonus),
                "note": "Виртуальный бонус может быть конвертирован в подарки по усмотрению родителей"
            }
        return None

