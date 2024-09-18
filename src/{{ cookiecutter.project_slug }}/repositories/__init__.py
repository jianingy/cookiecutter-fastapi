# inspired by https://chaoticengineer.hashnode.dev/fastapi-sqlalchemy#heading-repository

from typing import Any, Generic, Optional, TypeVar

from sqlalchemy import BinaryExpression, select
from sqlalchemy.ext.asyncio import AsyncSession

from .. import models

Model = TypeVar('Model', bound=models.Base)


class DatabaseRepository(Generic[Model]):
    """Repository for performing database queries."""

    def __init__(self, model: type[Model], session: AsyncSession) -> None:
        self.model = model
        self.session = session

    async def create(self, data: dict[str, Any]) -> Model:
        instance = self.model(**data)
        self.session.add(instance)
        await self.session.commit()
        await self.session.refresh(instance)
        return instance

    async def update(self, pk: int, data: dict[str, Any]) -> Optional[Model]:
        match await self.get(pk):
            case instance if instance is not None:
                for key, value in data.items():
                    setattr(instance, key, value)
                self.session.add(instance)
                await self.session.commit()
                await self.session.refresh(instance)
                return instance
            case _:
                return None

    async def get(self, pk: int) -> Optional[Model]:
        return await self.session.get(self.model, pk)

    async def delete(self, instance: object) -> None:
        await self.session.delete(instance)
        await self.session.commit()

    async def filter(
        self,
        offset: int,
        limit: int,
        *expressions: BinaryExpression[Any],
    ) -> list[Model]:
        query = select(self.model).offset(offset).limit(limit)
        if expressions:
            query = query.where(*expressions)
        return list(await self.session.scalars(query))

    async def filter_one(self, *expressions: BinaryExpression[Any]) -> Optional[Model]:
        query = select(self.model).where(*expressions)
        return await self.session.scalar(query)
