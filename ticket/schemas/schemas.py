from typing import List, Dict, Optional, Self, TypeVar
from sqlalchemy.ext.asyncio import AsyncSession
import strawberry
from strawberry.scalars import JSON
from strawberry.types import Info

from ticket.models.models import Filter

MODEL_TYPE = TypeVar("MODEL_TYPE")
ENUM_TYPE = TypeVar("ENUM_TYPE")

class CommonSchema:
    _model_type: type[MODEL_TYPE] = MODEL_TYPE

    _model_enums: Dict[str, ENUM_TYPE] = None

    @classmethod
    def parse_obj(cls, input: MODEL_TYPE) -> Self:
        ...

    @classmethod
    async def get_records(cls, info: Info) -> List[Self]:
        session: AsyncSession = info.context.get("db_session")
        return [
            cls.parse_obj(tkt) for tkt in await cls._model_type.get_records(engine=session)
        ]

    @classmethod
    async def get_record(cls, info: Info, id: strawberry.ID) -> Self:
        session: AsyncSession = info.context.get("db_session")
        return cls.parse_obj(
            await cls._model_type.get_record_by_id(id=int(id), engine=session)
        )

    @classmethod
    async def get_records_query(
        cls,
        info: Info,
        domain: Optional[JSON],
        order: Optional[JSON],
        limit: Optional[int] = 10,
        offset: Optional[int] = 0,
    ) -> List[Self]:
        session: AsyncSession = info.context.get("db_session")
        return [
            cls.parse_obj(tkt)  # type: ignore
            for tkt in await cls._model_type.get_records_query(
                engine=session,
                query=Filter(
                    domain=domain, order=order, limit=limit, offset=offset
                ),  # type: ignore
            )
        ]

    @classmethod
    async def add_record(cls, info: Info, data: JSON) -> Self:
        session: AsyncSession = info.context.get("db_session")
        new_record = cls._model_type(**data)
        await new_record.add_record(engine=session)
        for enum_field in (cls._model_enums or []):
            if enum_field in data:
                setattr(new_record, enum_field, getattr(cls._model_enums[enum_field], data[enum_field]))
        return cls.parse_obj(new_record)
