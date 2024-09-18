from typing import Annotated, Any, AsyncGenerator, Callable

import jwt
from fastapi import Depends, Header, HTTPException
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from {{ cookiecutter.project_slug }} import models
from {{ cookiecutter.project_slug }}.models.admin_user import AdminUser
from {{ cookiecutter.project_slug }}.repositories import DatabaseRepository
from {{ cookiecutter.project_slug }}.services.database import AsyncDatabaseSessionManager
from .auth import decode_access_token
from .settings import settings
from ..schemas.admin_user import AdminUserAccessTokenPayload

sessionmanager = AsyncDatabaseSessionManager(
    settings.database_url.unicode_string(),
    {
        'echo': settings.echo_sql,
        'pool_size': settings.database_max_connections,
    },
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with sessionmanager.session() as session:
        yield session


def get_repository(model: type[models.Base]) -> Callable[[AsyncSession], DatabaseRepository[Any]]:
    def func(session: AsyncSession = Depends(get_db_session)) -> DatabaseRepository[models.Base]:
        return DatabaseRepository(model, session)

    return func


async def get_admin_user(
    authorization: Annotated[str, Header()],
    admin_user_repo: DatabaseRepository[AdminUser] = Depends(get_repository(AdminUser)),
) -> AdminUser:
    try:
        _, access_token = authorization.split()
        raw = decode_access_token(access_token, settings.admin_token_secret_key, settings.admin_token_algorithm)
        payload = AdminUserAccessTokenPayload.model_validate(raw)
        match await admin_user_repo.get(payload.id):
            case user if user is not None:
                return user
            case _:
                raise HTTPException(status_code=401)
    except ValidationError:
        raise HTTPException(status_code=401)
    except jwt.exceptions.InvalidTokenError:
        raise HTTPException(status_code=401)
