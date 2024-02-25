from urllib.parse import quote
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncEngine
# pylint: disable=too-many-arguments

def get_pg_engine(host: str, port: int, user: str, password: str, database: str, pool_size: int = 2)->AsyncEngine:
    password = quote(password)
    return create_async_engine(f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}", pool_size=pool_size, echo=True, pool_pre_ping=True)

async def get_session(async_engine: AsyncEngine):
    async with async_sessionmaker(async_engine, expire_on_commit=False)() as session:
        try:
            yield session
        except Exception as err:
            await session.rollback()
            raise err
        finally:
            await session.commit()
