"""
Репозиторий для работы с правилами семьи
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.family_rules import FamilyRules
import json


class FamilyRulesRepository:
    """Репозиторий для работы с правилами семьи"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_user_id(self, user_id: int) -> Optional[FamilyRules]:
        """Получение правил семьи для родителя"""
        result = await self.session.execute(
            select(FamilyRules).where(FamilyRules.user_id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_or_create(self, user_id: int) -> FamilyRules:
        """Получение или создание правил семьи"""
        rules = await self.get_by_user_id(user_id)
        if not rules:
            rules = FamilyRules(user_id=user_id, rules="[]")
            self.session.add(rules)
            await self.session.flush()
            await self.session.refresh(rules)
        return rules
    
    async def update(self, rules: FamilyRules, rules_list: list[str]) -> FamilyRules:
        """Обновление правил семьи"""
        rules.rules = json.dumps(rules_list, ensure_ascii=False)
        await self.session.flush()
        await self.session.refresh(rules)
        return rules
    
    def parse_rules(self, rules: FamilyRules) -> list[str]:
        """Парсинг правил из JSON"""
        try:
            return json.loads(rules.rules) if rules.rules else []
        except (json.JSONDecodeError, TypeError):
            return []



