from sqlalchemy import and_, select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from models import Group, RepeatEntity, UserGroupRelation
from . import schemas


class GroupsService:

    async def get_group(self, session: AsyncSession, group: schemas.GroupGet):

        target_group = (
            await session.execute(
                select(Group)
                .where(Group.id == group.id)
                .where(Group.entity_id == group.entity_id)
            )
        ).scalar_one()
        return target_group

    async def find_group(self, session: AsyncSession, group: schemas.GroupFind):
        target_group = (
            await session.execute(
                select(Group)
                .where(Group.id == group.id)
                .where(
                    Group.entity_id
                    == select(RepeatEntity.id)
                    .where(RepeatEntity.name == group.entity_type)
                    .subquery()
                )
            )
        ).scalar_one()
        return target_group

    async def get_subscribtion_or_none(
        self, session: AsyncSession, user_id: int, group: schemas.GroupGet
    ):
        query = select(UserGroupRelation).where(
            and_(
                UserGroupRelation.entity_id == group.entity_id,
                UserGroupRelation.group_id == group.id,
                UserGroupRelation.user_id == user_id,
            )
        )

        result = (await session.execute(query)).scalar_one_or_none()

        return result

    async def get_subscribtion_or_none_by_entity_name(
        self, session: AsyncSession, user_id: int, group: schemas.GroupFind
    ):
        query = select(UserGroupRelation).where(
            and_(
                UserGroupRelation.entity_id
                == select(RepeatEntity.id)
                .where(RepeatEntity.name == group.entity_type)
                .subquery(),
                UserGroupRelation.group_id == group.id,
                UserGroupRelation.user_id == user_id,
            )
        )

        result = (await session.execute(query)).scalar_one_or_none()

        return result

    async def subscribe(
        self, session: AsyncSession, user_id: int, group: schemas.GroupGet
    ):
        stmt = (
            insert(UserGroupRelation)
            .values(
                {"user_id": user_id, "group_id": group.id, "entity_id": group.entity_id}
            )
            .returning(UserGroupRelation)
        )

        result = (await session.execute(stmt)).scalar_one()
        return result

    async def subscribe_by_entity_name(
        self, session: AsyncSession, user_id: int, group: schemas.GroupFind
    ):

        stmt = (
            insert(UserGroupRelation)
            .values(
                {
                    "user_id": user_id,
                    "group_id": group.id,
                    "entity_id": select(RepeatEntity.id)
                    .where(RepeatEntity.name == group.entity_type)
                    .subquery(),
                }
            )
            .returning(UserGroupRelation)
        )

        result = (await session.execute(stmt)).scalar_one()
        return result

    async def unsubscribe(
        self, session: AsyncSession, user_id: int, group: schemas.GroupGet
    ):
        stmt = delete(UserGroupRelation).where(
            and_(
                UserGroupRelation.entity_id == group.entity_id,
                UserGroupRelation.group_id == group.id,
                UserGroupRelation.user_id == user_id,
            )
        )

        await session.execute(stmt)

    async def unsubscribe_by_entity_name(
        self, session: AsyncSession, user_id: int, group: schemas.GroupFind
    ):
        stmt = delete(UserGroupRelation).where(
            and_(
                UserGroupRelation.entity_id
                == select(RepeatEntity.id)
                .where(RepeatEntity.name == group.entity_type)
                .subquery(),
                UserGroupRelation.group_id == group.id,
                UserGroupRelation.user_id == user_id,
            )
        )

        await session.execute(stmt)

    async def get_user_subscribed_groups(self, session: AsyncSession, user_id: int):
        query = (
            select(Group)
            .join(
                UserGroupRelation,
                and_(
                    Group.id == UserGroupRelation.group_id,
                    Group.entity_id == UserGroupRelation.entity_id,
                ),
            )
            .where(UserGroupRelation.user_id == user_id)
        )

        result = (await session.execute(query)).scalars().all()
        return result
