from database import get_async_session
import models
from sqlalchemy import insert, select
from managers.Logger import AsyncLogger


logger = AsyncLogger()


async def init_entities():
    async for session in get_async_session():
        db_response = await session.execute(select(models.RepeatEntity))
        if len(db_response.scalars().all()) != 0:
            await logger.info("Entities already initialized. Skiping.")
            return

        await logger.info("Entities not initialized... Initializaing...")
        try:
            new_data = [
                {"id": 1, "name": "words"},
                {"id": 2, "name": "clips"},
                {"id": -2, "name": "debug"},
            ]
            await session.execute(insert(models.RepeatEntity).values(new_data))
            await session.commit()
            await logger.info("Entities initialized")
        except Exception as ex:
            await logger.error(f"Error while entities initializing\n{ex}")
