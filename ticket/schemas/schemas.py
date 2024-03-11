from datetime import datetime
from typing import Generic, Tuple, List, Dict, Optional, Self, TypeVar
from pydantic import BaseModel
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
    _data_type: type[BaseModel] = BaseModel
    _model_enums: Dict[str, E] = {}

    id: strawberry.ID
    create_date: datetime
    wriet_date: datetime

    @classmethod
    def get_user(cls, info: Info) -> str:
        user_code: str = info.context.get("user_code")
        if not user_code:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
            )
        return user_code

    @classmethod
    def get_odoo_user(cls, info: Info) -> str:
        odoo_user: str = info.context.get("odoo_user")
        if not odoo_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
            )
        return odoo_user

    @classmethod
    def parse_obj(cls, model: M) -> Self:
        return cls(**model)

    @classmethod
    async def get_records(cls, info: Info) -> List[Self]:
        cls.get_odoo_user(info=info)
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
    async def add_record(cls, info: Info, data: JSON) -> Self:
        cls.get_odoo_user(info=info)
        session: AsyncSession = info.context.get("db_session")
        new_record = cls._model_type(
            **cls._data_type.model_validate(data).model_dump(exclude_unset=True)
        )
        await new_record.add_record(engine=session)
        return cls.parse_obj(new_record)

    @classmethod
    async def update_record(cls, info: Info, data_list: List[JSON]) -> List[Self]:
        cls.get_odoo_user(info=info)
        session: AsyncSession = info.context.get("db_session")
        return [
            cls.parse_obj(tkt)
            for tkt in await cls._model_type.update_records(
                engine=session,
                data_list=[
                    cls._data_type.model_validate(data).model_dump(exclude_unset=True)
                    for data in data_list
                    if data.get("id")
                ],
            )
        ]

    @classmethod
    async def delete_record(cls, info: Info, ids: List[int]) -> bool:
        cls.get_odoo_user(info=info)
        session: AsyncSession = info.context.get("db_session")
        return await cls._model_type.delete_records(engine=session, ids=ids)
