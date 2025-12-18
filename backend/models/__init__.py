"""
Инициализация моделей
Согласно rules.md: SQLAlchemy 2.0 async style
"""
from sqlalchemy.ext.declarative import declarative_base
from models.user import User, UserRole, Base

# Импортируем все модели для регистрации
from models.child import Child
from models.task import Task
from models.star import Star, StarHistory, StarStreak
from models.piggy import Piggy, PiggyGoal, PiggyHistory
from models.diary import DiaryEntry
from models.wishlist import WishlistItem
from models.settings import Settings
from models.weekly_stats import WeeklyStat
from models.subscription import Subscription
from models.parent_consent import ParentConsent
from models.notification import Notification, NotificationType, NotificationStatus

__all__ = [
    "Base",
    "User",
    "UserRole",
    "Child",
    "Task",
    "Star",
    "StarHistory",
    "StarStreak",
    "Piggy",
    "PiggyGoal",
    "PiggyHistory",
    "DiaryEntry",
    "WishlistItem",
    "Settings",
    "WeeklyStat",
    "Subscription",
    "Notification",
    "NotificationType",
    "NotificationStatus",
    "ParentConsent",
]
