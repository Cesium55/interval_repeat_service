from fastapi import APIRouter, Depends
from database import AsyncSession, get_async_session
from .manager import RepeatEntityManager

re_manager = RepeatEntityManager()

router = APIRouter(prefix="/repeat-entities")


@router.get("/")
async def all_entities(session: AsyncSession = Depends(get_async_session)):
    data = await re_manager.get_all(session)
    return {"data": data}


@router.get("/mapping")
async def all_entities(session: AsyncSession = Depends(get_async_session)):
    data = await re_manager.get_mapping(session)
    return {"data": data}
