from sqlalchemy.ext.asyncio import AsyncSession
from . import schemas
from .groups_service import GroupsService as IRGroupService
from .repeat_service import RepeatService
from models import Group, UserGroupRelation
from fastapi import HTTPException
from repeat_entities.manager import RepeatEntityManager

ir_group_service = IRGroupService()
repeat_service = RepeatService()
re_manager = RepeatEntityManager()


class IntervalRepeatManager:
    async def subscribe(
        self, session: AsyncSession, user_id: int, group: schemas.GroupFind
    ):
        group_from_db: Group = await ir_group_service.find_group(session, group)

        if (group_from_db.owner_id != -1) and (user_id != group_from_db.owner_id):
            raise HTTPException(status_code=403, detail="Forbidden")

        group_get = schemas.GroupGet(
            id=group_from_db.id, entity_id=group_from_db.entity_id
        )
        if subscription := await ir_group_service.get_subscribtion_or_none(
            session,
            user_id,
            group_get,
        ):
            return subscription
        sub = await ir_group_service.subscribe(session, user_id, group_get)
        await session.commit()
        return sub

    async def unsubscribe(
        self, session: AsyncSession, user_id: int, group: schemas.GroupFind
    ):
        result = {"message": "OK"}
        group_from_db: Group = await ir_group_service.find_group(session, group)
        group_get = schemas.GroupGet(
            id=group_from_db.id, entity_id=group_from_db.entity_id
        )
        if not (
            await ir_group_service.get_subscribtion_or_none(session, user_id, group_get)
        ):
            return result

        await ir_group_service.unsubscribe(session, user_id, group_get)

        await session.commit()

        return result

    async def get_user_subscribed_groups(self, session: AsyncSession, user_id: int):
        result = await ir_group_service.get_user_subscribed_groups(session, user_id)

        return result

    async def get_instances_to_learn(
        self, session: AsyncSession, user_id: int, entity_type: str
    ):
        result = await repeat_service.get_entities_to_learn_by_entity_name(
            session, user_id, entity_type
        )
        return result

    async def get_instances_to_repeat(
        self, session: AsyncSession, user_id: int, entity_type: str
    ):
        entity_id = (await re_manager.get_mapping(session)).get(entity_type)
        result = await repeat_service.get_due_for_repeat(session, user_id, entity_id)
        return result

    async def mark_as_known(
        self, session: AsyncSession, user_id: int, entity_type: str, instance_id: int
    ):
        entity_id = (await re_manager.get_mapping(session)).get(entity_type)
        result = await repeat_service.mark_as_known(
            session, user_id, entity_id, instance_id
        )
        await session.commit()
        return result

    async def repeat(
        self, session: AsyncSession, user_id: int, entity_type: str, instance_id: int
    ):
        entity_id = (await re_manager.get_mapping(session)).get(entity_type)
        result = await repeat_service.repeat(session, user_id, entity_id, instance_id)
        await session.commit()
        return result

    async def forget(
        self, session: AsyncSession, user_id: int, entity_type: str, instance_id: int
    ):
        entity_id = (await re_manager.get_mapping(session)).get(entity_type)
        result = await repeat_service.forget(session, user_id, entity_id, instance_id)
        await session.commit()
        return result

    async def start_learning(
        self, session: AsyncSession, user_id: int, entity_type: str, instance_id: int
    ):
        entity_id = (await re_manager.get_mapping(session)).get(entity_type)
        result = await repeat_service.start_learning(
            session, user_id, entity_id, instance_id
        )
        await session.commit()
        return result

    async def get_stats(self, session: AsyncSession, user_id: int):
        return await repeat_service.get_stats(session, user_id)

    async def get_next_repeat_relation(
        self, session: AsyncSession, user_id: int, entity_type: str
    ):
        entity_id = (await re_manager.get_mapping(session)).get(entity_type)
        result = await repeat_service.get_next_repeat_relation(
            session, user_id, entity_id
        )

        return result
