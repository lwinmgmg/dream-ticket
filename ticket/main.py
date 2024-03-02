import contextlib
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
from ticket.extensions.db_session import DbSessionExtension
from ticket.models.models import Base
from ticket.schemas.query import Query
from ticket.schemas.mutation import Mutation

logger = logging.getLogger(__name__)
logger.propagate = False

DB_KEY = "db"


class GraphQlContext(GraphQL):
    async def get_context(self, request: Request | WebSocket, response: Response):
        res = await super().get_context(request=request, response=response)
        res["db"] = request.app.state.db
        res["ro_db"] = request.app.state.ro_db
        res["user_code"] = "A0000001"
        return res


schema = strawberry.Schema(
    Query,
    mutation=Mutation,
    extensions=[
        DbSessionExtension,
    ],
)
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
    db_loader = DbLoader(app=router, key="db", engine=engine)
    await db_loader.startup()
    ro_db_loader = DbLoader(app=router, key="ro_db", engine=engine)
    await ro_db_loader.startup()
    yield
    # On Shutdown functions
    await db_loader.shutdown()
    await ro_db_loader.shutdown()


app = Starlette(lifespan=lifespan)
app.add_middleware(TimingMiddleware, log_type=LogType.INFO)
app.add_middleware(CORSMiddleware, allow_origins=["*"])
app.add_route("/graphql", graphql_app)  # type: ignore
