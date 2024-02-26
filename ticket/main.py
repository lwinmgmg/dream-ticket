import contextlib
from typing import Union, Optional
import logging
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.websockets import WebSocket
from starlette.responses import Response
from starlette.middleware.cors import CORSMiddleware
import strawberry
from strawberry.asgi import GraphQL

from ticket.services.engine import get_pg_engine
from ticket.services.db_loader import DbLoader
from ticket.middlewares.timing import TimingMiddleware, LogType
from ticket.middlewares.db_session import DbSessionMiddleware
from ticket.models.models import Base
from ticket.schemas.query import Query
from ticket.schemas.mutation import Mutation

logger = logging.getLogger(__name__)
logger.propagate = False

DB_KEY = "db"


class GraphQlContext(GraphQL):
    async def get_context(
        self, request: Union[Request, WebSocket], response: Optional[Response] = None
    ):
        return {
            "db": request.app.state.db,
            "db_session": request.scope.get("db_session"),
        }


schema = strawberry.Schema(Query, mutation=Mutation)
graphql_app = GraphQlContext(schema=schema)
engine = get_pg_engine(
    host="localhost", port=5432, user="lwinmgmg", password="frontiir", database="ticket"
)


async def db_load():
    async with engine.connect() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.commit()


@contextlib.asynccontextmanager
async def lifespan(router: Starlette):
    # On startup functions
    await db_load()
    db_loader = DbLoader(app=router, key=DB_KEY, engine=engine)
    await db_loader.startup()
    yield
    # On Shutdown functions
    await db_loader.shutdown()


app = Starlette(lifespan=lifespan)
app.add_middleware(TimingMiddleware, log_type=LogType.INFO)
app.add_middleware(DbSessionMiddleware, key=DB_KEY)
app.add_middleware(CORSMiddleware, allow_origins=["*"])

app.add_route("/graphql", graphql_app)  # type: ignore
