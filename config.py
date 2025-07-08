import os

APP_DEBUG = os.environ.get("APP_DEBUG") or True

DB_SYNC_DRIVER = os.environ.get("DB_SYNC_DRIVER")
DB_ASYNC_DRIVER = os.environ.get("DB_ASYNC_DRIVER")
DB_HOST = os.environ.get("DB_HOST")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")

AUTH_SERVICE_URL = os.environ.get("AUTH_SERVICE_URL")
AUTH_GET_PUBLIC_KEY_URL = (AUTH_SERVICE_URL or "") + "/api/v1/public-key"

REDIS_HOST = os.environ.get("REDIS_HOST")
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD")

RABBIT_HOST = os.environ.get("RABBIT_HOST")
