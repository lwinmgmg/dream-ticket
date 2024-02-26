import logging
from starlette.applications import Starlette
from sqlalchemy.ext.asyncio import AsyncEngine

_logger = logging.getLogger(__name__)


class DbLoader:
    def __init__(self, app: Starlette, key: str, engine: AsyncEngine) -> None:
        self.app = app
        self.key = key
        self.engine = engine

    async def startup(self):
        async with self.engine.connect() as connection:
            await connection.exec_driver_sql("SELECT 1")
        setattr(self.app.state, self.key, self.engine)
        _logger.info("Successfully attached the engine[%s]", self.key)

    async def shutdown(self):
        await self.engine.dispose()
        _logger.info("Successfully closed the engine[%s]", self.key)
