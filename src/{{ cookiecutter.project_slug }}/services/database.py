import contextlib
from typing import Any, AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncConnection, AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class AsyncDatabaseSessionManager:
    """
    inspired by https://praciano.com.br/fastapi-and-async-sqlalchemy-20-with-pytest-done-right.html
    """

    _engine: Optional[AsyncEngine]
    _session_maker: Optional[async_sessionmaker[AsyncSession]]

    def __init__(self, host: str, engine_kwargs: Optional[dict[str, Any]] = None):
        if engine_kwargs is None:
            engine_kwargs = {}
        self._engine = create_async_engine(host, **engine_kwargs)
        self._session_maker = async_sessionmaker(autocommit=False, bind=self._engine)

    def get_engine(self) -> Optional[AsyncEngine]:
        return self._engine

    async def close(self) -> None:
        if self._engine is None:
            raise Exception('AsyncDatabaseSessionManager is not initialized')
        await self._engine.dispose()

        self._engine = None
        self._session_maker = None

    @contextlib.asynccontextmanager
    async def connect(self) -> AsyncGenerator[AsyncConnection, None]:
        if self._engine is None:
            raise Exception('AsyncDatabaseSessionManager is not initialized')

        async with self._engine.begin() as connection:
            try:
                yield connection
            except Exception:
                await connection.rollback()
                raise

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        if self._session_maker is None:
            raise Exception('AsyncDatabaseSessionManager is not initialized')

        session = self._session_maker()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
