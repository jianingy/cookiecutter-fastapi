from typing import Any, AsyncGenerator

import pytest
from _pytest.fixtures import FixtureRequest
from celery.worker import WorkController
from httpx import ASGITransport, AsyncClient
from pydantic import PostgresDsn, RedisDsn
from sqlalchemy.ext.asyncio import AsyncSession
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer

from {{ cookiecutter.project_slug }}.app.settings import settings
from {{ cookiecutter.project_slug }}.models.admin_user import AdminUser
from {{ cookiecutter.project_slug }}.services.database import AsyncDatabaseSessionManager
from init_db import init_db

postgres = PostgresContainer('postgres:16-alpine')
redis = RedisContainer('redis:7.2-alpine')


@pytest.fixture(scope='session')
def anyio_backend() -> str:
    return 'asyncio'


@pytest.fixture(scope='session', autouse=True)
def setup(request: FixtureRequest, celery_session_worker: WorkController) -> None:
    postgres.start()
    redis.start()

    def remove_container() -> None:
        celery_session_worker.stop()  # type: ignore
        redis.stop()
        postgres.stop()

    request.addfinalizer(remove_container)
    database_url = postgres.get_connection_url().replace('psycopg2', 'asyncpg')
    redis_url = f'redis://{redis.get_container_host_ip()}:{redis.get_exposed_port(redis.port)}'
    settings.database_url = PostgresDsn(database_url)
    settings.celery_broker_url = RedisDsn(f'{redis_url}/0')
    settings.celery_backend_url = RedisDsn(f'{redis_url}/1')
    assert settings.database_url.unicode_string() == database_url
    init_db(postgres)

    @pytest.fixture(scope='session')
    def celery_config() -> dict[str, Any]:
        return {
            'broker_url': settings.celery_broker_url.unicode_string(),
            'result_backend': settings.celery_backend_url.unicode_string(),
            'worker_hijack_root_logger': False,
            'worker_log_color': False,
            'accept_content': {'json'},
            'enable_utc': False,
            'timezone': 'Asia/Shanghai',
            'broker_heartbeat': 0,
        }


@pytest.fixture(scope='session')
async def client() -> AsyncGenerator[AsyncClient, None]:
    # Import the FastAPI app after the environment has been set up
    from {{ cookiecutter.project_slug }}.app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://test') as client:
        yield client


@pytest.fixture(scope='session')
def sessionmanager() -> AsyncDatabaseSessionManager:
    database_url = postgres.get_connection_url().replace('psycopg2', 'asyncpg')
    return AsyncDatabaseSessionManager(database_url, {'echo': settings.echo_sql})


@pytest.fixture(scope='session')
async def db(sessionmanager: AsyncDatabaseSessionManager) -> AsyncGenerator[AsyncSession, None]:
    async with sessionmanager.session() as session:
        yield session

    await sessionmanager.close()


@pytest.fixture
async def current_admin_user(db: AsyncSession) -> AdminUser:
    from {{ cookiecutter.project_slug }}.repositories import DatabaseRepository

    user: AdminUser | None = await DatabaseRepository(AdminUser, db).get(10001)
    assert user is not None
    return user


@pytest.fixture
async def admin_user_token(current_admin_user: AdminUser) -> str:
    from {{ cookiecutter.project_slug }}.app.auth import create_admin_user_access_token

    return create_admin_user_access_token(
        current_admin_user,
        settings.admin_token_expire_seconds,
        settings.admin_token_secret_key,
        settings.admin_token_algorithm,
    )


@pytest.fixture(scope='session')
def celery_enable_logging() -> bool:
    return True


@pytest.fixture(scope='session')
def celery_worker_pool() -> str:
    # must use solo since we patch the openapi requests
    return 'solo'


@pytest.fixture(scope='session')
def celery_worker_parameters() -> dict[str, Any]:
    return {
        'queues':  ('default',),
        'perform_ping_check': False,
    }

@pytest.fixture(scope='session')
def celery_includes() -> list[str]:
    return [
        '{{ cookiecutter.project_slug }}.app.tasks',
    ]
