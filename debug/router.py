from fastapi import APIRouter
from words.initializer import WordsInitializer

router = APIRouter(prefix="/debug")


@router.post("/clear_words")
async def clear_words():
    await WordsInitializer().delete()
    return 0


@router.post("/re_init_words")
async def clear_words():
    return await WordsInitializer().re_init()
