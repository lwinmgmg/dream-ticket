from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.ext.asyncio import async_sessionmaker

class DbSessionMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, key: str):
        super().__init__(app)
        self.key = key

    async def dispatch(self, request, call_next):
        async with async_sessionmaker(getattr(request.app.state, self.key), expire_on_commit=False)() as session:
            request.scope.update([(f"{self.key}_session", session)])
            response = await call_next(request)
            await session.commit()
        return response
