import pytest
from alembic.config import Config
from alembic import command


@pytest.fixture(scope="session", autouse=True)
def apply_migrations():
    alembic_cfg = Config("alembic.ini")

    command.upgrade(alembic_cfg, "head")

    yield

    command.downgrade(alembic_cfg, "base")
