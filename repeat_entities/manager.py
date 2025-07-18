__all__ = ["RepeatEntityManager"]

from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession
from models import RepeatEntity


class RepeatEntityManager:

    async def find_by_name(
        self, session: AsyncSession, name: str
    ) -> RepeatEntity | None:
        db_response = await session.execute(
            select(RepeatEntity).where(RepeatEntity.name == name)
        )
        entity = db_response.scalar_one_or_none()
        return entity

    async def get_all(self, session: AsyncSession):
        db_response = await session.execute(select(RepeatEntity))
        entity = db_response.scalars().all()
        return entity
