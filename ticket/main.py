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
from ticket.models.models import Base
from ticket.schemas.query import Query

logger = logging.getLogger(__name__)
logger.propagate = False

class GraphQlContext(GraphQL):
    async def get_context(self, request: Union[Request, WebSocket], response: Optional[Response] = None):
        return {"db": request.app.state.db, "db_session": request.scope.get("db_session")}

schema = strawberry.Schema(Query)
graphql_app = GraphQlContext(schema=schema)
app = Starlette()
engine = get_pg_engine(host="0.0.0.0", port=5432, user="admin", password="admin", database="ticket")

@app.on_event("startup")
async def db_load():
    async with engine.connect() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.commit()

app.add_middleware(TimingMiddleware, log_type=LogType.INFO)
DbLoader(app=app, key="db", engine=engine)
app.add_middleware(CORSMiddleware, allow_origins=['*'])

app.add_route("/graphql", graphql_app) # type: ignore
