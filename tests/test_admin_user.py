from typing import Optional

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from {{ cookiecutter.project_slug }}.models.admin_user import AdminUser
from {{ cookiecutter.project_slug }}.repositories import DatabaseRepository
from init_db import predefined_value


@pytest.mark.anyio
async def test_create_admin_user(db: AsyncSession, client: AsyncClient) -> None:
    data = {'username': 'admin', 'password': 'encrypted_password'}
    response = await client.post('/admin/api/v1/admin_users', json=data)
    assert response.status_code == 200
    created = response.json()
    assert 'id' in created
    assert created['username'] == data['username']
    assert 'password' not in created

    repo = DatabaseRepository(AdminUser, db)
    user: Optional[AdminUser] = await repo.get(created['id'])
    assert user is not None
    assert user.id == created['id']
    assert user.password == data['password']
    assert user.username == data['username']


@pytest.mark.anyio
async def test_admin_user_detail(
    db: AsyncSession, client: AsyncClient, current_admin_user: AdminUser, admin_user_token: str
) -> None:
    response = await client.get(
        f'/admin/api/v1/admin_users/{current_admin_user.id}', headers={'Authorization': f'Bearer {admin_user_token}'}
    )
    assert response.status_code == 200
    user = response.json()
    assert user['id'] == current_admin_user.id
    assert user['username'] == current_admin_user.username
    assert 'password' not in user


@pytest.mark.anyio
async def test_admin_user_detail_not_found(db: AsyncSession, client: AsyncClient, admin_user_token: str) -> None:
    response = await client.get(
        '/admin/api/v1/admin_users/999999999', headers={'Authorization': f'Bearer {admin_user_token}'}
    )
    assert response.status_code == 404


@pytest.mark.anyio
async def test_admin_user_detail_bad_token(db: AsyncSession, client: AsyncClient) -> None:
    response = await client.get('/admin/api/v1/admin_users/10001', headers={'Authorization': 'Bearer BAD_TOKEN'})
    assert response.status_code == 401


@pytest.mark.anyio
async def test_admin_user_detail_no_auth(db: AsyncSession, client: AsyncClient) -> None:
    response = await client.get('/admin/api/v1/admin_users/10001')
    assert response.status_code == 422


@pytest.mark.anyio
async def test_admin_user_login_with_password(db: AsyncSession, client: AsyncClient) -> None:
    user = predefined_value.admin_users[0]
    data = {
        'username': user['username'],
        'password': user['password'],
    }
    response = await client.post('/admin/api/v1/admin_users/login', json=data)
    assert response.status_code == 200
    token = response.json()
    assert 'access_token' in token
    assert isinstance(token['access_token'], str)
    assert len(token['access_token']) > 0


@pytest.mark.anyio
async def test_admin_user_login_with_wrong_password(db: AsyncSession, client: AsyncClient) -> None:
    user = predefined_value.admin_users[0]
    data = {
        'username': user['username'],
        'password': 'wrong_password',
    }
    response = await client.post('/admin/api/v1/admin_users/login', json=data)
    assert response.status_code == 401
