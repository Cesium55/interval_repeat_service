from sqlalchemy import select, insert, delete
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_async_session
from models import (
    UserGroupRelation,
    RepeatRelation,
    GroupInstanceRelation,
    Group,
    RepeatEntityInstance,
    RepeatEntity,
)
import config
import httpx


class BaseInitializer:
    """
    Base class for instances initializators with implemented functionality (inspired by words initializer)

    terms may meet:
        groups = cats (categories)
        instances = words
    """

    entity_name: str
    get_groups_url: str
    get_all_instances_url: str
    get_instances_by_group_id_url: str
    group_name_descriptor: str

    def __init__(
        self,
        entity_name: str,
        get_groups_url: str,
        get_all_instances_url: str,
        get_instances_by_group_id_url: str,
        group_name_descriptor: str
    ):
        """
        group_name_descriptor:
            examples:
                category: {"name": "Anatomy", ...} <- group_name_descriptor = 'name'
                movie: {"title": "Anatomy", ...} <- group_name_descriptor = 'title'
        """
        self.entity_name = entity_name
        self.get_groups_url = get_groups_url
        self.get_all_instances_url = get_all_instances_url
        self.get_instances_by_group_id_url = get_instances_by_group_id_url
        self.group_name_descriptor = group_name_descriptor

    async def delete(self):
        queries = [
            delete(UserGroupRelation).where(
                UserGroupRelation.group_id.in_(
                    select(Group.id).where(
                        Group.entity_id
                        == select(RepeatEntity.id)
                        .where(RepeatEntity.name == self.entity_name)
                        .scalar_subquery()
                    )
                )
            ),
            delete(GroupInstanceRelation).where(
                GroupInstanceRelation.entity_id
                == select(RepeatEntity.id)
                .where(RepeatEntity.name == self.entity_name)
                .scalar_subquery()
            ),
            delete(RepeatRelation).where(
                RepeatRelation.entity_type
                == select(RepeatEntity.id)
                .where(RepeatEntity.name == self.entity_name)
                .scalar_subquery()
            ),
            delete(Group).where(
                Group.entity_id
                == select(RepeatEntity.id)
                .where(RepeatEntity.name == self.entity_name)
                .scalar_subquery()
            ),
            delete(RepeatEntityInstance).where(
                RepeatEntityInstance.entity_type
                == select(RepeatEntity.id)
                .where(RepeatEntity.name == self.entity_name)
                .scalar_subquery()
            ),
            delete(RepeatEntity).where(RepeatEntity.name == self.entity_name),
        ]

        async for session in get_async_session():
            for query in queries:
                await session.execute(query)

            await session.commit()

    async def get_groups(self):
        http_async_client = httpx.AsyncClient()
        response = await http_async_client.get(
            # config.WORDS_SERVICE_URL + "/categories/"
            self.get_groups_url
        )
        response_json = response.json()
        data = response_json.get("data")
        return data

    async def init_cats(self, session: AsyncSession, entity: RepeatEntity):
        
        data = await self.get_groups()

        for cat in data:
            cat_values = {
                "entity_id": entity.id,
                "name": cat.get(self.group_name_descriptor),
                "owner_id": cat.get("owner_id"),
                "id": cat.get("id"),
            }

            stmt = insert(Group).values(cat_values)
            await session.execute(stmt)


    async def get_instances(self, entity: RepeatEntity):
        http_async_client = httpx.AsyncClient()
        response = await http_async_client.get(
            # config.WORDS_SERVICE_URL + "/words/"
            self.get_all_instances_url
        )
        response_json = response.json()
        data = response_json.get("data")
        return data


    async def init_instances(self, session: AsyncSession, entity: RepeatEntity):
        data = await self.get_instances(entity)

        for word in data:
            word_values = {
                "entity_type": entity.id,
                "instance_id": word.get("id"),
            }

            stmt = insert(RepeatEntityInstance).values(word_values)
            await session.execute(stmt)


    async def get_group_and_instances(self, group_id):
        http_async_client = httpx.AsyncClient()
        response = await http_async_client.get(
            # config.WORDS_SERVICE_URL + f"/categories/{category_id}/words/",
            self.get_instances_by_group_id_url.format(group_id),
            follow_redirects=True,
        )
        response_json = response.json()
        data = response_json.get("data")

        return data

    async def link_category_words(
        self, session: AsyncSession, category_id: int, entity: RepeatEntity
    ):
        
        
        data = await self.get_group_and_instances(category_id)

        for word in data.get(self.entity_name):
            stmt = insert(GroupInstanceRelation).values(
                {
                    "group_id": category_id,
                    "entity_id": entity.id,
                    "instance_id": word.get("id"),
                }
            )

            await session.execute(stmt)

    async def link_categories_words(self, session: AsyncSession, entity: RepeatEntity):
        http_async_client = httpx.AsyncClient()
        response = await http_async_client.get(
            # config.WORDS_SERVICE_URL + "/categories/"
            self.get_groups_url
        )
        response_json = response.json()
        data = response_json.get("data")

        for cat in data:
            await self.link_category_words(session, cat.get("id"), entity)

    async def initialize(self):
        async for session in get_async_session():
            query = (
                insert(RepeatEntity)
                .values({"name": self.entity_name})
                .returning(RepeatEntity)
            )
            entity = (await session.execute(query)).scalar_one()

            await self.init_cats(session, entity)
            await self.init_instances(session, entity)
            await self.link_categories_words(session, entity)

            await session.commit()

            return 1

    async def re_init(self):
        await self.delete()
        return await self.initialize()
