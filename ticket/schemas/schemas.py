from typing import Generic, Tuple, List, Dict, Optional, Self, TypeVar
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.exceptions import HTTPException
from starlette import status
import strawberry
from strawberry.scalars import JSON
from strawberry.types import Info

from ticket.models.models import Filter, CommonModel

# pylint: disable = too-many-arguments

M = TypeVar("M")
E = TypeVar("E")
T = TypeVar("T")


class NoIdForUpdate(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


@strawberry.input
class QueryFilter(Generic[T]):
    domain: List[Tuple[str, str, T]]
    order: Optional[JSON]
    limit: Optional[int] = 10
    offset: Optional[int] = 0


class CommonSchema(Generic[M, E]):
    _model_type: type[CommonModel] = CommonModel

    _model_enums: Dict[str, E] = {}

    @classmethod
    def get_user(cls, info: Info) -> str:
        user_code: str = info.context.get("user_code")
        if not user_code:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
            )
        return user_code

    @classmethod
    def parse_obj(cls, model: M) -> Self:
        return cls(**model)

    @classmethod
    async def get_records(cls, info: Info) -> List[Self]:
        session: AsyncSession = info.context.get("ro_db_session")
        return [
            cls.parse_obj(tkt)
            for tkt in await cls._model_type.get_records(engine=session)
        ]

    @classmethod
    async def get_record(cls, info: Info, id: strawberry.ID) -> Self:
        session: AsyncSession = info.context.get("ro_db_session")
        return cls.parse_obj(
            await cls._model_type.get_record_by_id(id=int(id), engine=session)
        )

    @classmethod
    async def get_records_query(cls, info: Info, query: QueryFilter) -> List[Self]:
        session: AsyncSession = info.context.get("ro_db_session")
        return [
            cls.parse_obj(tkt)
            for tkt in await cls._model_type.get_records_query(
                engine=session,
                query=Filter(
                    domain=query.domain,
                    order=query.order,
                    limit=query.limit,
                    offset=query.offset,
                ),
            )
        ]

    @classmethod
    async def add_record(cls, info: Info, data: List[JSON]) -> Self:
        session: AsyncSession = info.context.get("db_session")
        new_record = cls._model_type(**data)
        await new_record.add_record(engine=session)
        for enum_field in cls._model_enums or []:
            if enum_field in data:
                setattr(
                    new_record,
                    enum_field,
                    getattr(cls._model_enums[enum_field], data[enum_field]),
                )
        return cls.parse_obj(new_record)

    @classmethod
    async def update_record(cls, info: Info, data_list: JSON) -> List[Self]:
        session: AsyncSession = info.context.get("db_session")
        for data in data_list:
            if not data.get("id"):
                raise NoIdForUpdate("No id found for update ticket")
        return [
            cls.parse_obj(tkt)
            for tkt in await cls._model_type.update_records(
                engine=session, data_list=data_list
            )
        ]
