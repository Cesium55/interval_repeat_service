from fastapi import APIRouter, Depends
from words.initializer import WordsInitializer
from database import get_async_session
from interval_repeat.groups_service import GroupsService
from interval_repeat.schemas import GroupFind


router = APIRouter(prefix="/debug")


@router.post("/clear_words")
async def clear_words():
    await WordsInitializer().delete()
    return 0


@router.post("/re_init_words")
async def clear_words():
    return await WordsInitializer().re_init()


@router.get("/test_response")
async def test_response(group: GroupFind, session=Depends(get_async_session)):
    gs = GroupsService()
    return await gs.find_group(session, group)
