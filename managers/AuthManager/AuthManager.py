import aiohttp
from config import AUTH_GET_PUBLIC_KEY_URL, REDIS_HOST, REDIS_PASSWORD
from managers.RedisManager import RedisManager
from fastapi import HTTPException, Request
from managers.AuthManager.JWTManager import JWTManager
from managers.Logger import AsyncLogger


logger = AsyncLogger()


class AuthManager:

    public_key_redis_key = "auth_public_key"

    async def public_key_init(self, silent=False):
        async with aiohttp.ClientSession() as client_session:
            async with client_session.get(AUTH_GET_PUBLIC_KEY_URL) as response:
                if not response.ok:
                    raise Exception(
                        f"Error while getting public key ({response.status})"
                    )
                data = await response.json()
                key = data.get("key")
                if (not key) and (not silent):
                    raise Exception(
                        f"Error while getting public key (key not found in response)"
                    )

                redis = RedisManager()
                await redis.set(self.public_key_redis_key, key)

                return key

    async def get_auth_public_key(self, init_if_null=True):
        redis = RedisManager()

        key = await redis.get(self.public_key_redis_key)
        if key:
            return key
        if not init_if_null:
            return None

        key = await self.public_key_init(silent=True)
        return key


ex401 = HTTPException(401, "Unauthorized")
ex403 = HTTPException(403, "Forbidden")
jwt_m: JWTManager = JWTManager()


def get_bearer_token(request: Request) -> str:
    auth: str = request.headers.get("Authorization")

    if not auth or not auth.lower().startswith("bearer "):
        return None

    token = auth[7:]
    return token


async def admin_required(request: Request):
    token = get_bearer_token(request)
    if not token:
        raise ex401
    auth_manager = AuthManager()
    data = jwt_m.get_data(token, await auth_manager.get_auth_public_key())
    await logger.info(f"JWT decoded data: '{data}', token:{token}")
    if (not data) or (not data.get("is_admin")):
        raise ex403

    return data


async def user_required(request: Request):
    token = get_bearer_token(request)
    if not token:
        raise ex401
    auth_manager = AuthManager()
    data = jwt_m.get_data(token, await auth_manager.get_auth_public_key())
    await logger.info(f"JWT decoded data: '{data}', token:{token}")
    if not data:
        raise ex401

    return data
