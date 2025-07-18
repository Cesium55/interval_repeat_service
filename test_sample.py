from config import DB_SYNC_DRIVER, TEST_DB_URL
import asyncio
import pytest


def pytest_configure(config):
    from alembic import context
    from models import Base

    url = TEST_DB_URL
    context.configure(
        url=url,
        target_metadata=Base.metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def test_env():
    print("testing env")
    assert DB_SYNC_DRIVER == "sqlite"


@pytest.mark.asyncio
async def test_async():
    await asyncio.sleep(0.01)
