from typing import Optional, Dict, Tuple, List, Any, Self
from enum import Enum
from pydantic import BaseModel
from sqlalchemy import select, Select, update
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs, AsyncSession


class Base(AsyncAttrs, DeclarativeBase):
    pass


class WhereOptr(Enum):
    IS = "is"
    IS_NOT = "is not"
    EQ = "="
    NE = "!="
    GT = ">"
    GE = ">="
    LT = "<"
    LE = "<="
    IN = "in"
    NOT_IN = "not in"
    ILIKE = "ilike"
    NOT_ILIKE = "not ilike"
    LIKE = "like"
    NOT_LIKE = "not like"


class Filter(BaseModel):
    domain: Optional[List[Tuple[str, str, Any]]] = []
    limit: Optional[int] = 10
    offset: Optional[int] = 0
    order: Optional[Dict[str, str]] = {}

    def prepare_where(self, stmt: Select, model: type[Base]) -> Select:
        for k, optr, v in self.domain:
            if not hasattr(model, k):
                continue
            match optr.lower():
                case WhereOptr.IS.value:
                    stmt = stmt.where(getattr(model, k).is_(v))
                case WhereOptr.IS_NOT.value:
                    stmt = stmt.where(getattr(model, k).is_not(v))
                case WhereOptr.EQ.value:
                    stmt = stmt.where(getattr(model, k) == v)
                case WhereOptr.NE.value:
                    stmt = stmt.where(getattr(model, k) != v)
                case WhereOptr.GT.value:
                    stmt = stmt.where(getattr(model, k) > v)
                case WhereOptr.GE.value:
                    stmt = stmt.where(getattr(model, k) >= v)
                case WhereOptr.LT.value:
                    stmt = stmt.where(getattr(model, k) < v)
                case WhereOptr.LE.value:
                    stmt = stmt.where(getattr(model, k) <= v)
                case WhereOptr.IN.value:
                    stmt = stmt.where(getattr(model, k).in_(v))
                case WhereOptr.NOT_IN.value:
                    stmt = stmt.where(getattr(model, k).not_in(v))
                case WhereOptr.ILIKE.value:
                    stmt = stmt.where(getattr(model, k).ilike(v))
                case WhereOptr.NOT_ILIKE.value:
                    stmt = stmt.where(getattr(model, k).not_ilike(v))
                case WhereOptr.LIKE.value:
                    stmt = stmt.where(getattr(model, k).like(v))
                case WhereOptr.NOT_LIKE.value:
                    stmt = stmt.where(getattr(model, k).not_like(v))
        return stmt

    def prepare_order(self, model: type[Base]):
        output = []
        for k, v in self.order.items():
            if not hasattr(model, k):
                continue
            match v.lower():
                case "desc":
                    output.append(getattr(model, k).desc())
                case "asc":
                    output.append(getattr(model, k).asc())
        return output


class CommonModel:
    id: int = None

    @classmethod
    async def get_record_by_id(cls, id: int, engine: AsyncSession) -> Self:
        stmt = select(cls).where(cls.id == id)
        res = await engine.execute(stmt)
        return res.scalar_one()

    @classmethod
    async def get_records(cls, engine: AsyncSession) -> List[Self]:
        stmt = select(cls).order_by(cls.id)
        res = await engine.execute(stmt)
        return res.scalars().all()

    @classmethod
    async def get_records_query(cls, engine: AsyncSession, query: Filter) -> List[Self]:
        stmt = query.prepare_where(stmt=select(cls), model=cls)
        stmt = (
            stmt.order_by(*query.prepare_order(cls))
            .limit(query.limit)
            .offset(query.offset)
        )
        res = await engine.execute(stmt)
        return res.scalars().all()

    async def add_record(self, engine: AsyncSession):
        engine.add(self)
        if hasattr(self, "create_lines"):
            await self.create_lines(engine=engine)
        await engine.flush()

    @classmethod
    async def update_records(
        cls, engine: AsyncSession, data_list: List[Dict[str, str]]
    ) -> List[Self]:
        await engine.execute(update(cls), data_list)
        return await cls.get_records_query(
            engine=engine,
            query=Filter(
                domain=[
                    ("id", WhereOptr.IN.value, [data.get("id") for data in data_list])
                ],
                limit=len(data_list),
            ),
        )
