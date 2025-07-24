import asyncio
from fastapi import FastAPI
from brokers.rabbit_broker import broker as rabbit_broker
from contextlib import asynccontextmanager
from groups.router import router as groups_router
from interval_repeat.routes import router as ir_router
from repeat_entities import broker
from repeat_entities.routes import router as re_router
import initializer
import config
from debug.router import router as debug_router
from middleware import ExceptionsSQLAlchemyToHTTP
from fastapi.middleware.cors import CORSMiddleware

from groups import broker


@asynccontextmanager
async def lifespan(app: FastAPI):

    await rabbit_broker.safe_start()

    await initializer.init_entities()

    print("APP STARTED")

    yield

    await rabbit_broker.stop()


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.add_middleware(ExceptionsSQLAlchemyToHTTP)

app.include_router(groups_router)
app.include_router(ir_router)
app.include_router(re_router)

if config.APP_DEBUG:
    app.include_router(debug_router)


@app.get("/")
def index():
    return {"message": "interval repeat service"}
