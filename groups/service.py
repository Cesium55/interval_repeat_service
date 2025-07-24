from models import Group
from sqlalchemy import insert, select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from .schemas import GroupCreate, GroupsCreate


class GroupService:

    async def get_all(self, session: AsyncSession):
        query = select(Group)
        db_result = await session.execute(query)
        result = db_result.scalars().all()
        return result

    async def create(self, session: AsyncSession, group: GroupCreate) -> Group:
        stmt = insert(Group).values(**group.model_dump()).returning(Group)
        db_result = await session.execute(stmt)
        new_group = db_result.scalar_one_or_none()
        return new_group

    async def create_many(self, session: AsyncSession, groups: GroupsCreate):
        stmt = (
            insert(Group).values([i.model_dump() for i in groups.data]).returning(Group)
        )
        db_result = await session.execute(stmt)
        new_groups = db_result.scalars().all()
        return new_groups
