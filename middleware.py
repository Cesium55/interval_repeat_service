from fastapi import Request
from database import get_async_session


class SessionInsertMiddleware:
    async def __call__(self, request: Request, call_next):
        async for session in get_async_session():
            request.state.session = session
            return await call_next(request)