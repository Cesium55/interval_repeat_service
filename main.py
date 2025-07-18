import asyncio
from fastapi import FastAPI
from brokers.rabbit_broker import broker as rabbit_broker
from contextlib import asynccontextmanager
from groups.router import router as groups_router
from repeat_entities import broker
import initializer
import config
from debug.router import router as debug_router

from groups import broker


@asynccontextmanager
async def lifespan(app: FastAPI):

    await rabbit_broker.safe_start()

    await initializer.init_entities()

    print("APP STARTED")

    yield

    await rabbit_broker.stop()


app = FastAPI(lifespan=lifespan)

app.include_router(groups_router)

if config.APP_DEBUG:
    app.include_router(debug_router)


@app.get("/")
def index():
    return {"message": "interval repeat service"}
