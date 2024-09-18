import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from {{ cookiecutter.project_slug }}.repositories import DatabaseRepository


@pytest.mark.anyio
async def test_app_root(client: AsyncClient) -> None:
    response = await client.get('/')
    assert response.status_code == 404


@pytest.mark.anyio
async def test_get_repository(db: AsyncSession) -> None:
    from {{ cookiecutter.project_slug }}.app.dependencies import get_repository
    from {{ cookiecutter.project_slug }}.models.admin_user import AdminUser

    repo = get_repository(AdminUser)(db)
    assert isinstance(repo, DatabaseRepository)
