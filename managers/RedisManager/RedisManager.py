import aiohttp
from redis.asyncio import Redis
from config import REDIS_HOST, REDIS_PASSWORD
from managers.Logger import AsyncLogger

if 1:
    import datetime
    import hashlib
    import warnings
    from enum import Enum
    from typing import (
        TYPE_CHECKING,
        Any,
        AsyncIterator,
        Awaitable,
        Callable,
        Dict,
        Iterable,
        Iterator,
        List,
        Literal,
        Mapping,
        Optional,
        Sequence,
        Set,
        Tuple,
        Union,
    )

    from redis.exceptions import ConnectionError, DataError, NoScriptError, RedisError
    from redis.typing import (
        AbsExpiryT,
        AnyKeyT,
        BitfieldOffsetT,
        ChannelT,
        CommandsProtocol,
        ConsumerT,
        EncodableT,
        ExpiryT,
        FieldT,
        GroupT,
        KeysT,
        KeyT,
        Number,
        PatternT,
        ResponseT,
        ScriptTextT,
        StreamIdT,
        TimeoutSecT,
        ZScoreBoundT,
    )

logger = AsyncLogger()


class RedisManager:
    r: Redis

    def __init__(self, redis_host=REDIS_HOST, redis_password=REDIS_PASSWORD):
        self.r = Redis(host=redis_host, decode_responses=True)

    async def get(self, name: str):
        try:
            result = await self.r.get(name)
            return result
        except Exception as ex:
            await logger.info(ex)

    async def set(
        self,
        name: "KeyT",
        value: "EncodableT",
        ex: "Optional[ExpiryT]" = None,
        px: "Optional[ExpiryT]" = None,
        nx: bool = False,
        xx: bool = False,
        keepttl: bool = False,
        get: bool = False,
        exat: "Optional[AbsExpiryT]" = None,
        pxat: "Optional[AbsExpiryT]" = None,
    ) -> "ResponseT":
        try:
            result = await self.r.set(
                name, value, ex, px, nx, xx, keepttl, get, exat, pxat
            )
            return result
        except Exception as _ex:
            await logger.info(_ex)
