from typing import List
from brokers.rabbit_broker import broker, decoder, RabbitMessage
from pydantic import BaseModel
from database import get_async_session
from .manager import RepeatEntityManager
from managers.Logger import AsyncLogger
from models import RepeatEntityInstance, GroupInstanceRelation
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

entities_manager = RepeatEntityManager()
logger = AsyncLogger()


class NewInstanceModel(BaseModel):
    entity_type: str
    id: int
    groups: List[int]


async def link_group_instances(
    session: AsyncSession, entity_id: int, instance_id: int, groups_ids: List[int]
):
    """func for creating 'GroupInstanceRelation' objects"""
    new_data = [
        {"group_id": group_id, "entity_id": entity_id, "instance_id": instance_id}
        for group_id in groups_ids
    ]

    stmt = (
        insert(GroupInstanceRelation).values(new_data).returning(GroupInstanceRelation)
    )
    db_result = await session.execute(stmt)

    return db_result.scalars().all()


@broker.subscriber("new_instances_queue", decoder=decoder)
async def new_instance_handler(msg: RabbitMessage):
    data = NewInstanceModel(**msg.body)

    async for session in get_async_session():
        entity = await entities_manager.find_by_name(session, data.entity_type)
        if not entity:
            await logger.error(f"Broker: Unknown entity type: '{data.entity_type}'")
            return

        new_instance = (
            await session.execute(
                insert(RepeatEntityInstance)
                .values({"entity_type": data.entity_type, "instance_id": data.id})
                .returning(RepeatEntityInstance)
            )
        ).scalar_one()

        await link_group_instances(session, entity.id, data.id, data.groups)

        await session.commit()

        await logger.info(f"New instance created {data.entity_type}[{data.id}]")
