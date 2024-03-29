import contextlib
import logging
from typing import Tuple
import grpc
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.websockets import WebSocket
from starlette.responses import Response
from starlette.middleware.cors import CORSMiddleware
import strawberry
from strawberry.asgi import GraphQL
from user_go import user_go_pb2, user_go_pb2_grpc

from ticket.env.settings import load_setting_from_env
from ticket.services.odoo import Odoo
from ticket.services.engine import get_pg_engine
from ticket.services.db_loader import DbLoader
from ticket.middlewares.timing import TimingMiddleware, LogType
from ticket.extensions.db_session import DbSessionExtension
from ticket.schemas.query import Query
from ticket.schemas.mutation import Mutation

logger = logging.getLogger(__name__)
logger.propagate = False

DB_KEY = "db"

settings = load_setting_from_env()

odoo = Odoo(
    settings.services.odoo.url,
    settings.services.odoo.user,
    settings.services.odoo.password,
)


class GraphQlContext(GraphQL):
    @classmethod
    def custom_get_auth(cls, request: Request | WebSocket) -> Tuple[str, str]:
        auth_values = request.headers.get("Authorization")
        if not auth_values:
            return "", ""
        values = auth_values.split(" ")
        if len(values) != 2:
            return "", ""
        return values[0], values[1]

    @classmethod
    def get_token(cls, token: str):
        with grpc.insecure_channel(
            f"{settings.services.user.grpc.host}:{settings.services.user.grpc.port}"
        ) as channel:
            stub = user_go_pb2_grpc.UserServiceStub(channel=channel)
            # pylint: disable = no-member
            response = stub.CheckThirdpartyToken(user_go_pb2.Token(token=token))
        return response

    async def get_context(self, request: Request | WebSocket, response: Response):
        res = await super().get_context(request=request, response=response)
        res["db"] = request.app.state.db
        res["ro_db"] = request.app.state.ro_db
        token_type, access_token = self.custom_get_auth(request=request)
        match token_type.lower():
            case "bearer":
                tkn = self.get_token(access_token)
                res["user_code"] = tkn.uid
                res["cid"] = tkn.cid
                res["scopes"] = tkn.scp
            case "odoo":
                res["odoo_user"] = await odoo.get_odoo_user(access_token)
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
    host=settings.services.postgres.db.host,
    port=settings.services.postgres.db.port,
    user=settings.services.postgres.db.user,
    password=settings.services.postgres.db.password,
    database=settings.services.postgres.db.database,
)
ro_engine = get_pg_engine(
    host=settings.services.postgres.ro_db.host,
    port=settings.services.postgres.ro_db.port,
    user=settings.services.postgres.ro_db.user,
    password=settings.services.postgres.ro_db.password,
    database=settings.services.postgres.ro_db.database,
)


@contextlib.asynccontextmanager
async def lifespan(router: Starlette):
    # On startup functions
    # await db_load()
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
