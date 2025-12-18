# 📋 Весь код проекта - для копирования

## 🔧 Backend - Модели

### models/user.py
```python
"""
SQLAlchemy модель пользователя
Согласно rules.md: SQLAlchemy 2.0 async style
"""
from sqlalchemy import Column, Integer, String, Enum, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
import enum

# Base для всех моделей
Base = declarative_base()


class UserRole(str, enum.Enum):
    """Роли пользователей"""
    ADMIN = "admin"
    PARENT = "parent"
    CHILD = "child"


class User(Base):
    """Модель пользователя"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    parent_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Для детей
    
    # Связи
    children = relationship("Child", back_populates="user", cascade="all, delete-orphan")
    parent = relationship("User", remote_side=[id], backref="children_users")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

### models/__init__.py
```python
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
]
```

### models/child.py
```python
"""
Модель ребёнка
Согласно rules.md: SQLAlchemy 2.0 async style
"""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from models.user import Base


class Gender(str, enum.Enum):
    """Пол ребёнка"""
    GIRL = "girl"
    BOY = "boy"
    NONE = "none"


class Child(Base):
    """Модель ребёнка"""
    __tablename__ = "children"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String, nullable=False, default="Ребёнок")
    gender = Column(Enum(Gender), nullable=False, default=Gender.NONE)
    avatar = Column(Text, nullable=True)  # Base64 или URL
    
    # Связи
    user = relationship("User", back_populates="children")
    tasks = relationship("Task", back_populates="child", cascade="all, delete-orphan")
    stars = relationship("Star", back_populates="child", uselist=False, cascade="all, delete-orphan")
    piggy = relationship("Piggy", back_populates="child", uselist=False, cascade="all, delete-orphan")
    diary_entries = relationship("DiaryEntry", back_populates="child", cascade="all, delete-orphan")
    wishlist_items = relationship("WishlistItem", back_populates="child", cascade="all, delete-orphan")
    settings = relationship("Settings", back_populates="child", uselist=False, cascade="all, delete-orphan")
    weekly_stats = relationship("WeeklyStat", back_populates="child", cascade="all, delete-orphan")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

### models/task.py
```python
"""
Модель задачи
Согласно rules.md: SQLAlchemy 2.0 async style
"""
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from models.user import Base


class TaskType(str, enum.Enum):
    """Тип задачи"""
    CHECKLIST = "checklist"
    KANBAN = "kanban"


class TaskStatus(str, enum.Enum):
    """Статус задачи в канбане"""
    TODO = "todo"
    DOING = "doing"
    DONE = "done"


class Task(Base):
    """Модель задачи"""
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("children.id"), nullable=False, index=True)
    text = Column(String, nullable=False)
    task_type = Column(Enum(TaskType), nullable=False)
    status = Column(Enum(TaskStatus), nullable=True)  # Для канбана
    completed = Column(Boolean, default=False, nullable=False)
    stars = Column(Integer, default=0, nullable=False)
    position = Column(Integer, default=0)  # Для сортировки
    
    # Связи
    child = relationship("Child", back_populates="tasks")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

### models/star.py
```python
"""
Модели для работы со звёздами
Согласно rules.md: SQLAlchemy 2.0 async style
"""
from sqlalchemy import Column, Integer, ForeignKey, DateTime, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models.user import Base


class Star(Base):
    """Модель звёзд ребёнка"""
    __tablename__ = "stars"
    
    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("children.id"), nullable=False, unique=True, index=True)
    today = Column(Integer, default=0, nullable=False)
    total = Column(Integer, default=0, nullable=False)
    
    # Связи
    child = relationship("Child", back_populates="stars")
    history = relationship("StarHistory", back_populates="star", cascade="all, delete-orphan")
    streak = relationship("StarStreak", back_populates="star", uselist=False, cascade="all, delete-orphan")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class StarHistory(Base):
    """История получения звёзд"""
    __tablename__ = "star_history"
    
    id = Column(Integer, primary_key=True, index=True)
    star_id = Column(Integer, ForeignKey("stars.id"), nullable=False, index=True)
    description = Column(String, nullable=False)
    stars = Column(Integer, nullable=False)
    
    # Связи
    star = relationship("Star", back_populates="history")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class StarStreak(Base):
    """Серия дней выполнения задач"""
    __tablename__ = "star_streaks"
    
    id = Column(Integer, primary_key=True, index=True)
    star_id = Column(Integer, ForeignKey("stars.id"), nullable=False, unique=True, index=True)
    current = Column(Integer, default=0, nullable=False)
    last_date = Column(String, nullable=True)  # YYYY-MM-DD
    best = Column(Integer, default=0, nullable=False)
    claimed_rewards = Column(Text, nullable=True)  # JSON массив
    
    # Связи
    star = relationship("Star", back_populates="streak")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

### models/piggy.py
```python
"""
Модели для работы с копилкой
Согласно rules.md: SQLAlchemy 2.0 async style
"""
from sqlalchemy import Column, Integer, ForeignKey, DateTime, String, Numeric, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models.user import Base


class Piggy(Base):
    """Модель копилки ребёнка"""
    __tablename__ = "piggies"
    
    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("children.id"), nullable=False, unique=True, index=True)
    amount = Column(Numeric(10, 2), default=0, nullable=False)
    
    # Связи
    child = relationship("Child", back_populates="piggy")
    goal = relationship("PiggyGoal", back_populates="piggy", uselist=False, cascade="all, delete-orphan")
    history = relationship("PiggyHistory", back_populates="piggy", cascade="all, delete-orphan")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class PiggyGoal(Base):
    """Цель копилки"""
    __tablename__ = "piggy_goals"
    
    id = Column(Integer, primary_key=True, index=True)
    piggy_id = Column(Integer, ForeignKey("piggies.id"), nullable=False, unique=True, index=True)
    name = Column(String, nullable=False, default="")
    amount = Column(Numeric(10, 2), default=0, nullable=False)
    
    # Связи
    piggy = relationship("Piggy", back_populates="goal")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class PiggyHistory(Base):
    """История операций с копилкой"""
    __tablename__ = "piggy_history"
    
    id = Column(Integer, primary_key=True, index=True)
    piggy_id = Column(Integer, ForeignKey("piggies.id"), nullable=False, index=True)
    type = Column(String, nullable=False)  # 'add', 'withdraw', 'streak', 'exchange'
    amount = Column(Numeric(10, 2), nullable=False)
    description = Column(String, nullable=True)
    
    # Связи
    piggy = relationship("Piggy", back_populates="history")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

### models/settings.py
```python
"""
Модель настроек
Согласно rules.md: SQLAlchemy 2.0 async style
"""
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models.user import Base


class Settings(Base):
    """Настройки ребёнка"""
    __tablename__ = "settings"
    
    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("children.id"), nullable=False, unique=True, index=True)
    stars_to_money = Column(Integer, default=15, nullable=False)
    money_per_stars = Column(Numeric(10, 2), default=200, nullable=False)
    
    # Связи
    child = relationship("Child", back_populates="settings")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

### models/diary.py
```python
"""
Модель дневника
Согласно rules.md: SQLAlchemy 2.0 async style
"""
from sqlalchemy import Column, Integer, ForeignKey, DateTime, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models.user import Base


class DiaryEntry(Base):
    """Запись в дневнике"""
    __tablename__ = "diary_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("children.id"), nullable=False, index=True)
    title = Column(String, nullable=True)
    content = Column(Text, nullable=False)
    
    # Связи
    child = relationship("Child", back_populates="diary_entries")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

### models/wishlist.py
```python
"""
Модель списка желаний
Согласно rules.md: SQLAlchemy 2.0 async style
"""
from sqlalchemy import Column, Integer, ForeignKey, DateTime, String, Numeric, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models.user import Base


class WishlistItem(Base):
    """Элемент списка желаний"""
    __tablename__ = "wishlist_items"
    
    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("children.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    price = Column(Numeric(10, 2), nullable=True)
    achieved = Column(Boolean, default=False, nullable=False)
    position = Column(Integer, default=0)  # Для сортировки
    
    # Связи
    child = relationship("Child", back_populates="wishlist_items")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

### models/weekly_stats.py
```python
"""
Модель статистики недели
Согласно rules.md: SQLAlchemy 2.0 async style
"""
from sqlalchemy import Column, Integer, ForeignKey, DateTime, String, Integer as SQLInteger
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models.user import Base


class WeeklyStat(Base):
    """Статистика за день"""
    __tablename__ = "weekly_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("children.id"), nullable=False, index=True)
    date = Column(String, nullable=False, index=True)  # YYYY-MM-DD
    stars = Column(SQLInteger, default=0, nullable=False)
    tasks_completed = Column(SQLInteger, default=0, nullable=False)
    
    # Связи
    child = relationship("Child", back_populates="weekly_stats")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

---

## 📝 Примечание

Все остальные файлы (schemas, repositories, services, routers) находятся в соответствующих директориях проекта. Полный список файлов:

- `backend/schemas/*.py` - Pydantic схемы
- `backend/repositories/*.py` - Репозитории
- `backend/services/*.py` - Сервисы
- `backend/routers/*.py` - Роутеры
- `backend/core/*.py` - Ядро приложения

Для просмотра всех файлов используйте IDE или команду `find backend -name "*.py"`.

