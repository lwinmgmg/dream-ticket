from enum import Enum
from typing import List
from sqlalchemy import String, Integer, Float, Text, Boolean, ForeignKey, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
import strawberry

from .models import Base, CommonModel

# pylint: disable=unsubscriptable-object


class TicketLineNotAvailable(Exception):
    pass


class TicketLineNotReserved(Exception):
    pass


@strawberry.enum
class TicketState(Enum):
    DRAFT = "draft"
    POSTED = "posted"
    DONE = "done"


class Ticket(Base, CommonModel):
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

    async def create_lines(self, engine: AsyncSession) -> List["TicketLine"]:
        res = await engine.execute(
            select(TicketLine).where(TicketLine.ticket_id == self.id)
        )
        records = res.scalars().all()
        if records:
            return records
        records = []
        for idx in range(self.start_num, self.end_num + 1):
            records.append(TicketLine(number=idx, ticket_id=self.id))
        engine.add_all(records)
        return records


@strawberry.enum
class TicketLineState(Enum):
    AVAILABLE = "available"
    RESERVED = "reserved"
    SOLD = "sold"


class TicketLine(Base, CommonModel):
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
    async def get_ticket_line_by_tid(
        cls, ticket_id: int, engine: AsyncSession
    ) -> List["TicketLine"]:
        stmt = select(cls).where(cls.ticket_id == ticket_id)
        res = await engine.execute(stmt)
        return res.scalars().all()
