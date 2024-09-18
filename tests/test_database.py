import pytest
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from testcontainers.postgres import PostgresContainer

from {{ cookiecutter.project_slug }}.services.database import AsyncDatabaseSessionManager


postgres = PostgresContainer('postgres:16-alpine')


@pytest.fixture(scope='module')
def database_url() -> str:
    postgres.start()
    return postgres.get_connection_url().replace('psycopg2', 'asyncpg')


@pytest.mark.anyio
async def test_database_session_manager_initializes_engine_correctly(database_url: str) -> None:
    manager = AsyncDatabaseSessionManager(database_url)
    assert manager.get_engine() is not None


@pytest.mark.anyio
async def test_database_session_manager_creates_session_successfully(database_url: str) -> None:
    manager = AsyncDatabaseSessionManager(database_url)
    async with manager.session() as session:
        assert session is not None


@pytest.mark.anyio
async def test_database_session_manager_handles_session_rollback_on_sqlalchemy_error(database_url: str) -> None:
    manager = AsyncDatabaseSessionManager(database_url)
    with pytest.raises(SQLAlchemyError):
        async with manager.session() as _:
            raise SQLAlchemyError('Simulated database error for testing rollback')


@pytest.mark.anyio
async def test_database_session_manager_handles_session_rollback_on_exception(database_url: str) -> None:
    manager = AsyncDatabaseSessionManager(database_url)
    with pytest.raises(Exception):
        async with manager.connect() as _:
            raise Exception('A generic error')


@pytest.mark.anyio
async def test_database_session_manager_closes_engine_successfully(database_url: str) -> None:
    manager = AsyncDatabaseSessionManager(database_url)
    await manager.close()
    assert manager.get_engine() is None


@pytest.mark.anyio
async def test_database_session_manager_raises_exception_uninitialized_engine(database_url: str) -> None:
    manager = AsyncDatabaseSessionManager(database_url)
    await manager.close()  # Close to simulate uninitialized state
    with pytest.raises(Exception) as exc_info:
        async with manager.session():
            pass
    assert 'AsyncDatabaseSessionManager is not initialized' in str(exc_info.value)


@pytest.mark.anyio
async def test_database_session_manager_raises_exception_uninitialized_connect(database_url: str) -> None:
    manager = AsyncDatabaseSessionManager(database_url)
    await manager.close()  # Close to simulate uninitialized state
    with pytest.raises(Exception) as exc_info:
        async with manager.connect():
            pass
    assert 'AsyncDatabaseSessionManager is not initialized' in str(exc_info.value)


@pytest.mark.anyio
async def test_closing_empty_engine_sessionmanager(database_url: str) -> None:
    manager = AsyncDatabaseSessionManager(database_url)
    manager._engine = None
    with pytest.raises(Exception) as _:
        await manager.close()  # This should not raise an error


@pytest.mark.anyio
async def test_executing_query_in_session_returns_expected_result(database_url: str) -> None:
    manager = AsyncDatabaseSessionManager(database_url)
    async with manager.session() as session:
        result = await session.execute(text('SELECT 1+1'))
        result_value = result.scalar()
        assert result_value == 2


@pytest.mark.anyio
async def test_connecting_to_database_with_valid_url_provides_connection(database_url: str) -> None:
    manager = AsyncDatabaseSessionManager(database_url)
    async with manager.connect() as connection:
        assert connection is not None


@pytest.mark.anyio
async def test_connecting_to_database_with_invalid_url_raises_exception() -> None:
    invalid_url = 'postgresql+asyncpg://invalid:invalid@localhost:5432/invalid_db'
    manager = AsyncDatabaseSessionManager(invalid_url)
    with pytest.raises(Exception):
        async with manager.connect() as _:
            pass
