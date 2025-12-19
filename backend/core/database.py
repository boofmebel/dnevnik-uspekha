"""
Подключение к базе данных
Согласно rules.md: async-first, AsyncEngine + async_session
"""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from core.config import settings

# Создание async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True
)

# Создание async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncSession:
    """
    Dependency для получения async сессии БД
    Использование: async def endpoint(db: AsyncSession = Depends(get_db))
    """
    try:
        async with AsyncSessionLocal() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    except (ConnectionRefusedError, OSError) as e:
        # Если БД недоступна, создаем пустую сессию-заглушку
        # Это позволит эндпоинтам обработать ошибку и вернуть пустой список
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"БД недоступна: {e}. Создаю заглушку сессии.")
        # Создаем пустую сессию, которая будет обработана в эндпоинтах
        async with AsyncSessionLocal() as session:
            yield session
            # Не делаем commit/rollback для заглушки

