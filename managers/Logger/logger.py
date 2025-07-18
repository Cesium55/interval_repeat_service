import asyncio
import aiofiles
from datetime import datetime, timezone
from typing import Literal
import logging


class AsyncLogger:
    def __init__(self, filename: str = "app.log"):
        self.filename = filename
        self.lock = asyncio.Lock()

    async def log(
        self, message: str, level: Literal["INFO", "WARNING", "ERROR"] = "INFO"
    ):
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S %Z")
        log_message = f"[{timestamp}] [{level}] {message}\n"

        async with self.lock:
            async with aiofiles.open(self.filename, mode="a") as f:
                await f.write(log_message)

    async def info(self, message: str):
        await self.log(message, "INFO")

    async def warning(self, message: str):
        await self.log(message, "WARNING")

    async def error(self, message: str):
        await self.log(message, "ERROR")


class Logger:
    def __init__(self, name: str = "app", level: int = logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # Проверяем, чтобы обработчики не добавлялись повторно
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("[%(asctime)s] %(levelname)s - %(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def info(self, message: str):
        self.logger.info(message)

    def warning(self, message: str):
        self.logger.warning(message)

    def error(self, message: str):
        self.logger.error(message)

    def debug(self, message: str):
        self.logger.debug(message)

    def critical(self, message: str):
        self.logger.critical(message)
