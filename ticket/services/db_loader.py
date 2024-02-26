import logging
from starlette.applications import Starlette
from sqlalchemy.ext.asyncio import AsyncEngine
from ticket.middlewares.db_session import DbSessionMiddleware

_logger = logging.getLogger(__name__)


class DbLoader:
    def __init__(self, app: Starlette, key: str, engine: AsyncEngine) -> None:
        self.app = app
        self.key = key
        self.engine = engine
        self.app.on_event("startup")(self._startup)
        self.app.on_event("shutdown")(self._shutdown)
        self.app.add_middleware(DbSessionMiddleware, key=self.key)

    async def _startup(self):
        async with self.engine.connect() as connection:
            await connection.exec_driver_sql("SELECT 1")
        setattr(self.app.state, self.key, self.engine)
        _logger.info("Successfully attached the engine[%s]", self.key)

    async def _shutdown(self):
        await self.engine.dispose()
        _logger.info("Successfully closed the engine[%s]", self.key)
