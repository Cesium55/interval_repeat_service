from fastapi import FastAPI
from brokers.rabbit_broker import broker as rabbit_broker
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):


    await rabbit_broker.safe_start()

    print("APP STARTED")

    yield

    await rabbit_broker.stop()



app = FastAPI(lifespan=lifespan)

@app.get("/")
def index():
    return {"message": "interval repeat service"}
