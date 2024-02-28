from enum import Enum
from typing import Dict, List
from sqlalchemy import String, Integer, Float, Text, Boolean, ForeignKey, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
import strawberry

from .models import Base
from .filter import Filter, WhereOptr


@strawberry.enum
class TicketState(Enum):
    DRAFT = "draft"
    POSTED = "posted"
    DONE = "done"


class Ticket(Base):
    __tablename__ = "ticket"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    state: Mapped[TicketState] = mapped_column(index=True, default=TicketState.DRAFT)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    start_num: Mapped[int] = mapped_column(Integer, default=0)
    end_num: Mapped[int] = mapped_column(Integer)
    win_num: Mapped[int] = mapped_column(Integer, nullable=True)
    available_count: Mapped[int] = mapped_column(Integer)
    reserved_count: Mapped[int] = mapped_column(Integer, default=0)
    sold_count: Mapped[int] = mapped_column(Integer, default=0)

    line_ids: Mapped[List["TicketLine"]] = relationship(
        back_populates="ticket",
    )

    def __repr__(self) -> str:
        return f"Ticket(id={self.id!r}, name={self.name!r})"

    @classmethod
    async def get_ticket_by_id(cls, id: int, engine: AsyncSession) -> "Ticket":
        stmt = select(cls).where(cls.id == id)
        res = await engine.execute(stmt)
        return res.scalar_one()

    @classmethod
    async def get_tickets(cls, engine: AsyncSession) -> List["Ticket"]:
        stmt = select(cls).order_by(cls.id)
        res = await engine.execute(stmt)
        return res.scalars().all()

    @classmethod
    async def get_tickets_query(
        cls, engine: AsyncSession, query: Filter
    ) -> List["Ticket"]:
        stmt = query.prepare_where(stmt=select(cls), model=Ticket)
        stmt = (
            stmt.order_by(*query.prepare_order(Ticket))
            .limit(query.limit)
            .offset(query.offset)
        )
        res = await engine.execute(stmt)
        return res.scalars().all()

    async def add_ticket(self, engine: AsyncSession):
        engine.add(self)
        await self.create_lines(engine=engine)
        await engine.flush()

    async def create_lines(self, engine: AsyncSession) -> List["TicketLine"]:
        stmt = select(TicketLine)
        res = await engine.execute(stmt)
        records = res.scalars().all()
        if records:
            return records
        records = []
        for idx in range(self.start_num, self.end_num + 1):
            records.append(TicketLine(number=idx, ticket_id=self.id))
        engine.add_all(records)
        return records

    @classmethod
    async def update_ticket(
        cls, engine: AsyncSession, data_list: List[Dict[str, str]]
    ) -> List["Ticket"]:
        await engine.execute(update(Ticket), data_list)
        return await cls.get_tickets_query(
            engine=engine,
            query=Filter(
                domain=[
                    ("id", WhereOptr.IN.value, [data.get("id") for data in data_list])
                ],
                limit=len(data_list),
            ),
        )


@strawberry.enum
class TicketLineState(Enum):
    AVAILABLE = "available"
    RESERVED = "reserved"
    SOLD = "sold"


class TicketLine(Base):
    __tablename__ = "ticket_line"

    id: Mapped[int] = mapped_column(primary_key=True)
    number: Mapped[int] = mapped_column(nullable=False)
    ticket_id: Mapped[int] = mapped_column(ForeignKey("ticket.id"), index=True)
    ticket: Mapped[Ticket] = relationship(back_populates="line_ids")
    user_code: Mapped[str] = mapped_column(String(length=30), nullable=True)
    is_special_price: Mapped[bool] = mapped_column(Boolean, default=False)
    special_price: Mapped[float] = mapped_column(Float, default=0.0)
    state: Mapped[TicketLineState] = mapped_column(
        index=True, default=TicketLineState.AVAILABLE
    )

    def __repr__(self) -> str:
        return f"TicketLine(id={self.id!r}, name={self.number})"

    @classmethod
    async def get_ticket_line_by_id(cls, id: int, engine: AsyncSession) -> "TicketLine":
        stmt = select(cls).where(cls.id == id)
        res = await engine.execute(stmt)
        return res.scalar_one()

    @classmethod
    async def get_ticket_line_by_tid(
        cls, ticket_id: int, engine: AsyncSession
    ) -> List["TicketLine"]:
        stmt = select(cls).where(cls.ticket_id == ticket_id)
        res = await engine.execute(stmt)
        return res.scalars().all()

    @classmethod
    async def get_ticket_lines(cls, engine: AsyncSession) -> List["TicketLine"]:
        stmt = select(cls).order_by(cls.id)
        res = await engine.execute(stmt)
        return res.scalars().all()

    @classmethod
    async def get_ticket_lines_query(
        cls, engine: AsyncSession, query: Filter
    ) -> List["TicketLine"]:
        stmt = query.prepare_where(stmt=select(cls), model=TicketLine)
        stmt = (
            stmt.order_by(*query.prepare_order(TicketLine))
            .limit(query.limit)
            .offset(query.offset)
        )
        res = await engine.execute(stmt)
        return res.scalars().all()

    async def add_ticket_line(self, engine: AsyncSession):
        engine.add(self)
        await engine.flush()

    @classmethod
    async def update_ticket_line(
        cls, engine: AsyncSession, data_list: List[Dict[str, str]]
    ) -> List["TicketLine"]:
        await engine.execute(update(TicketLine), data_list)
        return await cls.get_ticket_lines_query(
            engine=engine,
            query=Filter(
                domain=[
                    ("id", WhereOptr.IN.value, [data.get("id") for data in data_list])
                ],
                limit=len(data_list),
            ),
        )
