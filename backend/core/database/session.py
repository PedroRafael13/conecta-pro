"""
Gerenciamento de sessões do banco de dados.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager, contextmanager

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker

from core.config import settings

# Engine assíncrono
engine = create_async_engine(
    settings.database_url,
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
    echo=settings.debug,
)

# Session factory
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency para obter sessão do banco de dados.

    Yields:
        AsyncSession: Sessão do banco de dados

    Example:
        @router.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Inicializa o banco de dados (cria tabelas)."""
    from core.models import Base

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """Fecha conexões do banco de dados."""
    await engine.dispose()


# Alias para Celery async tasks
get_async_db_session = asynccontextmanager(get_db)


# ============================================================================
# Sessão Síncrona para Celery Tasks
# ============================================================================

# Engine síncrono para Celery
sync_engine = create_engine(
    settings.database_url.replace("+asyncpg", ""),  # Remove asyncpg para usar psycopg2
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
    echo=settings.debug,
)

# Session factory síncrona
SyncSessionLocal = sessionmaker(
    bind=sync_engine,
    autocommit=False,
    autoflush=False,
)


def get_sync_db_dependency():
    """FastAPI dependency para sessão síncrona do banco."""
    session = SyncSessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@contextmanager
def get_sync_db():
    """Context manager para sessão síncrona do banco (para Celery tasks).

    Example:
        with get_sync_db() as db:
            items = db.query(Item).all()
    """
    session = SyncSessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
