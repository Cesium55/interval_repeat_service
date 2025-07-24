from fastapi import Request, HTTPException, Response
from database import get_async_session
from sqlalchemy.exc import NoResultFound
from starlette.middleware.base import BaseHTTPMiddleware
import json


class SessionInsertMiddleware:
    async def __call__(self, request: Request, call_next):
        async for session in get_async_session():
            request.state.session = session
            return await call_next(request)


class ExceptionsSQLAlchemyToHTTP(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except NoResultFound:
            return Response(json.dumps({"detail": "Not found"}), status_code=404)
