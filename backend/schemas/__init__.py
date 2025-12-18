"""
Инициализация схем
"""
from schemas.auth import LoginRequest, LoginResponse, RefreshRequest
from schemas.task import TaskCreate, TaskUpdate, TaskResponse, TaskListResponse
from schemas.star import StarResponse, StarAddRequest, StarExchangeRequest, StarHistoryResponse, StarStreakResponse
from schemas.piggy import PiggyResponse, PiggyGoalUpdate, PiggyAddRequest, PiggyGoalResponse, PiggyHistoryResponse
from schemas.child import ChildCreate, ChildUpdate, ChildResponse
from schemas.settings import SettingsUpdate, SettingsResponse
from schemas.diary import DiaryEntryCreate, DiaryEntryUpdate, DiaryEntryResponse
from schemas.wishlist import WishlistItemCreate, WishlistItemUpdate, WishlistItemResponse
from schemas.weekly_stats import WeeklyStatResponse, WeeklyStatsResponse
from schemas.subscription import SubscriptionResponse, SubscriptionCancelRequest, SubscriptionRefundRequest, ParentConsentRequest, ParentConsentResponse
from schemas.notification import NotificationResponse, ComplaintRequest, NotificationCreate
from schemas.legal import LegalTextResponse
from schemas.admin import AdminUserResponse, AdminChildResponse, AdminSubscriptionResponse, AdminNotificationResponse, AdminStatsResponse, AdminUserUpdate, AdminChildUpdate

__all__ = [
    "LoginRequest",
    "LoginResponse",
    "RefreshRequest",
    "TaskCreate",
    "TaskUpdate",
    "TaskResponse",
    "TaskListResponse",
    "StarResponse",
    "StarAddRequest",
    "StarExchangeRequest",
    "StarHistoryResponse",
    "StarStreakResponse",
    "PiggyResponse",
    "PiggyGoalUpdate",
    "PiggyAddRequest",
    "PiggyGoalResponse",
    "PiggyHistoryResponse",
    "ChildCreate",
    "ChildUpdate",
    "ChildResponse",
    "SettingsUpdate",
    "SettingsResponse",
    "DiaryEntryCreate",
    "DiaryEntryUpdate",
    "DiaryEntryResponse",
    "WishlistItemCreate",
    "WishlistItemUpdate",
    "WishlistItemResponse",
    "WeeklyStatResponse",
    "WeeklyStatsResponse",
    "SubscriptionResponse",
    "SubscriptionCancelRequest",
    "SubscriptionRefundRequest",
    "ParentConsentRequest",
    "ParentConsentResponse",
    "NotificationResponse",
    "ComplaintRequest",
    "NotificationCreate",
    "LegalTextResponse",
    "AdminUserResponse",
    "AdminChildResponse",
    "AdminSubscriptionResponse",
    "AdminNotificationResponse",
    "AdminStatsResponse",
    "AdminUserUpdate",
    "AdminChildUpdate",
]
