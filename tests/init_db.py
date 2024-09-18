import asyncio
from dataclasses import dataclass
from threading import Thread

from sqlalchemy.ext.asyncio import AsyncSession
from testcontainers.postgres import PostgresContainer

from {{ cookiecutter.project_slug }}.models.admin_user import AdminUser
from {{ cookiecutter.project_slug }}.repositories import DatabaseRepository
from {{ cookiecutter.project_slug }}.services.database import AsyncDatabaseSessionManager


@dataclass
class PredefinedValue:
    admin_users = [
        {
            'id': 10001,
            'username': 'admin_user_1',
            'password': 'admin_password_1',
        }
    ]


predefined_value = PredefinedValue()


def init_db(postgres: PostgresContainer) -> None:
    database_url = postgres.get_connection_url().replace('psycopg2', 'asyncpg')

    import os
    os.environ['DATABASE_URL'] = database_url

    from alembic.config import Config
    from alembic import command

    config = Config('alembic.ini')
    command.upgrade(config, 'head')

    event_loop = asyncio.new_event_loop()
    sessionmanager = AsyncDatabaseSessionManager(database_url, {})

    async def _init() -> None:
        async with sessionmanager.session() as session:
            await create_admin_users(session)
        await sessionmanager.close()

    thread = Thread(target=event_loop.run_forever, daemon=True)
    thread.start()
    asyncio.run_coroutine_threadsafe(_init(), event_loop).result()
    event_loop.call_soon_threadsafe(lambda ev: ev.stop(), event_loop)
    thread.join()


async def create_admin_users(db: AsyncSession) -> None:
    for admin_user in predefined_value.admin_users:
        await DatabaseRepository(AdminUser, db).create(
            {
                'id': admin_user['id'],
                'username': admin_user['username'],
                'password': admin_user['password'],
            }
        )
