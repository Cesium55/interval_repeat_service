import jwt
from managers.AuthManager import AuthManager
from managers.Logger import Logger
import asyncio

logger = Logger()


class JWTManager:

    def get_data(self, token: str, public_key):
        logger.info(f"pub key: {public_key}")
        try:
            data = jwt.decode(token, public_key, algorithms=["RS256"])
            return data
        except jwt.exceptions.PyJWTError as _ex:
            logger.error(_ex)
            return None
