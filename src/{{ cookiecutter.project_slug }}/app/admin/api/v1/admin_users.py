from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_

from {{ cookiecutter.project_slug }}.app.auth import create_admin_user_access_token
from {{ cookiecutter.project_slug }}.app.dependencies import get_admin_user, get_repository
from {{ cookiecutter.project_slug }}.app.settings import settings
from {{ cookiecutter.project_slug }}.models.admin_user import AdminUser
from {{ cookiecutter.project_slug }}.repositories import DatabaseRepository
from {{ cookiecutter.project_slug }}.schemas.admin_user import (
    AdminUserAccessTokenResponse,
    AdminUserCreationRequest,
    AdminUserLoginByUsernameRequest,
    AdminUserResponse,
)

router = APIRouter(tags=['Administration User Management'])

AdminUserRepository = Annotated[
    DatabaseRepository[AdminUser],
    Depends(get_repository(AdminUser)),
]


@router.post('/admin_users', response_model=AdminUserResponse, name='Create an administrator account')
async def create_admin_user_endpoint(data: AdminUserCreationRequest, repository: AdminUserRepository) -> AdminUser:
    user = await repository.create(data.model_dump())
    return user


@router.post('/admin_users/login', response_model=AdminUserAccessTokenResponse, name='Login with username & password')
async def login_with_username_endpoint(
    data: AdminUserLoginByUsernameRequest, repository: AdminUserRepository
) -> AdminUserAccessTokenResponse:
    criterion = and_(AdminUser.username == data.username, AdminUser.password == data.password)
    match await repository.filter_one(criterion.is_(True)):
        case user if user is not None:
            return AdminUserAccessTokenResponse.model_validate(
                {
                    'access_token': create_admin_user_access_token(
                        user,
                        settings.admin_token_expire_seconds,
                        settings.admin_token_secret_key,
                        settings.admin_token_algorithm,
                    )
                }
            )
        case _:
            raise HTTPException(status_code=401)


@router.get(
    '/admin_users/{user_id}',
    dependencies=[Depends(get_admin_user)],
    response_model=AdminUserResponse,
    name='Get details by user id',
)
async def get_admin_user_endpoint(user_id: int, repository: AdminUserRepository) -> AdminUser:
    match await repository.get(user_id):
        case user if user is not None:
            return user
        case _:
            raise HTTPException(status_code=404)
