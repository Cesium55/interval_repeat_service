from fastapi import APIRouter, Depends
from typing import List
from . import schemas
from database import AsyncSession, get_async_session
from .service import GroupService
from managers.AuthManager.AuthManager import admin_required


router = APIRouter(prefix="/groups")
service = GroupService()


@router.post("/", dependencies=[Depends(admin_required)])
async def groups_create(
    groups: schemas.GroupsCreate, session: AsyncSession = Depends(get_async_session)
):
    new_groups = await service.create_many(session, groups)
    await session.commit()
    return new_groups


@router.get("/", dependencies=[])
async def get_all(session: AsyncSession = Depends(get_async_session)):
    groups = await service.get_all(session)

    return {"data": groups}


@router.get("", dependencies=[])
async def get_all_by_entity_type(entity_type: str = None, session: AsyncSession = Depends(get_async_session), ):
    if not entity_type:
        groups = await service.get_all(session)
    else:
        groups = await service.get_all_by_entity(session, entity_type)

    return {"data": groups}