from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.ext.asyncio import async_sessionmaker

class DbSessionMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, key: str):
        super().__init__(app)
        self.key = key

    async def dispatch(self, request, call_next):
        session = None
        print("**********************************************************************")
        async with async_sessionmaker(getattr(request.app.state, self.key), expire_on_commit=False)() as session:
            request.scope.update([(f"{self.key}_session", session)])
            response = await call_next(request)
            print("NEXT**********************************************************************", session, session.is_active)
            await session.commit()
            print("COMMIT**********************************************************************")
        print(session, session and session.is_active, "*****************************")
        return response
