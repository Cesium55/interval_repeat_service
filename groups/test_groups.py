from sqlalchemy import select
from database import get_async_session
import pytest
from models import Group
from sqlalchemy import text
from groups.service import GroupService
from groups.schemas import GroupCreate


@pytest.mark.asyncio
async def test_table_exists():
    async for session in get_async_session():
        db_result = await session.execute(select(Group))
        assert [] == db_result.scalars().all()


@pytest.mark.asyncio
async def test_insert_group():
    async for session in get_async_session():
        name = "test_insert_group"
        gr = await GroupService().create(session, GroupCreate(name=name))
        assert gr.name == name


@pytest.mark.asyncio
async def test_insert_group_with_commit():
    async for session in get_async_session():
        name = "test_insert_group_with_commit"
        gr = await GroupService().create(session, GroupCreate(name=name))
        await session.commit()
        assert gr.name == name


@pytest.mark.asyncio
async def test_insert_group_with_select():
    async for session in get_async_session():
        name = "test_insert_group_with_select"
        service = GroupService()
        gr = await service.create(session, GroupCreate(name=name))
        new_gr = await service.get(session, gr.id)
        assert gr == new_gr


@pytest.mark.asyncio
async def test_insert_group_with_rollback():
    async for session in get_async_session():
        name = "test_insert_group_with_rollback"
        service = GroupService()
        gr = await service.create(session, GroupCreate(name=name))
        id = gr.id
        await session.rollback()
    async for session in get_async_session():
        new_gr = await service.get(session, id)
        assert None == new_gr
