from pydantic import BaseModel
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, delete, update
from sqlalchemy import func

from typing import TypeVar, Generic, List

Model = TypeVar("Model", bound=DeclarativeBase)


class BaseServiceSchema(BaseModel):
    model: BaseModel
    create_schema: BaseModel
    delete_schema: BaseModel
    read_schema: BaseModel


class BaseService(Generic(Model)):

    _schemas: BaseServiceSchema

    def __init__(self, schemas: BaseServiceSchema):
        self._schemas = schemas

    async def get(self, session: AsyncSession, id):
        query = select(Model).where(Model.id == id)
        db_result = await session.execute(query)
        result = db_result.scalar_one_or_none()
        return result

    async def get_all(self, session: AsyncSession):
        query = select(Model)
        db_result = await session.execute(query)
        result = db_result.scalars().all()
        return result

    async def create(self, session: AsyncSession, data: List) -> List[Model]:
        stmt = insert(Model).values([i.model_dump() for i in data]).returning(Model)
        db_result = await session.execute(stmt)
        new_instances = db_result.scalars().all()
        return new_instances

    async def delete(self, session: AsyncSession, data: List) -> List[Model]:
        stmt = (
            delete(Model)
            .where(Model.id.in_((i.model_dump().id for i in data)))
            .returning(Model)
        )
        db_result = await session.execute(stmt)
        new_instances = db_result.scalars().all()
        return new_instances
