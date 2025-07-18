from brokers.rabbit_broker import broker, decoder, RabbitMessage
from groups import schemas as groups_schemas
from groups.service import GroupService
from managers.Logger import AsyncLogger
from database import get_async_session
from repeat_entities.manager import RepeatEntityManager


logger = AsyncLogger()
entity_manager = RepeatEntityManager()
service = GroupService()


@broker.subscriber("new_group_queue", decoder=decoder)
async def new_group(msg: RabbitMessage):

    await logger.info("creating new group")
    await logger.info(f"type: {type(msg.body)} data: {msg.body}")

    data = groups_schemas.BrokerGroupCreate(**msg.body)

    async for session in get_async_session():
        entity = await entity_manager.find_by_name(session, data.entity_name)

        if not entity:
            logger.error(f"Unknown entity: '{data.entity_name}'")
            return

        new_data = groups_schemas.GroupCreate(**msg.body, entity_id=entity.id)

        new_group = await service.create(session, new_data)
        await session.commit()

    await logger.info(
        f"new group was created {entity.name}-[{new_group.entity_id}], {new_group.id}, {new_group.name}"
    )
