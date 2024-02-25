from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker

class DbSessionMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, key: str):
        super().__init__(app)
        self.key = key

    async def dispatch(self, request, call_next):
        db : AsyncEngine = getattr(request.app.state, self.key)
        async with async_sessionmaker(db)() as session:
            request.scope.update([(f"{self.key}_session", session)])
            try:
                response = await call_next(request)
                await session.commit()
            except Exception as err:
                await session.rollback()
                raise err
        return response
