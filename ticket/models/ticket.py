from typing import List
from sqlalchemy import String, ForeignKey, select
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from .models import Base
from .filter import Filter


class Ticket(Base):
    __tablename__ = "ticket"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))

    line_ids: Mapped[List["TicketLine"]] = relationship(
        back_populates="ticket",
    )

    def __repr__(self) -> str:
        return f"Ticket(id={self.id!r}, name={self.name!r})"

    @classmethod
    async def get_ticket_by_id(
        cls, id: int, engine: AsyncEngine | AsyncSession
    ) -> "Ticket":
        stmt = select(cls).where(cls.id == id)
        res = await engine.execute(stmt)
        return res.scalar_one()

    @classmethod
    async def get_tickets(cls, engine: AsyncEngine | AsyncSession) -> List["Ticket"]:
        stmt = select(cls).order_by(cls.id)
        res = await engine.execute(stmt)
        return res.scalars().all()

    @classmethod
    async def get_tickets_query(
        cls, engine: AsyncEngine | AsyncSession, query: Filter
    ) -> List["Ticket"]:
        stmt = query.prepare_where(stmt=select(cls), model=Ticket)
        stmt = (
            stmt
            .order_by(*query.prepare_order(Ticket))
            .limit(query.limit)
            .offset(query.offset)
        )
        res = await engine.execute(stmt)
        return res.scalars().all()


class TicketLine(Base):
    __tablename__ = "ticket_line"

    id: Mapped[int] = mapped_column(primary_key=True)
    number: Mapped[int] = mapped_column(nullable=False)
    ticket_id: Mapped[int] = mapped_column(ForeignKey("ticket.id"), index=True)
    ticket: Mapped[Ticket] = relationship(back_populates="line_ids")

    def __repr__(self) -> str:
        return f"TicketLine(id={self.id!r}, name={self.number})"

    @classmethod
    async def get_ticket_line_by_id(
        cls, id: int, engine: AsyncEngine | AsyncSession
    ) -> "Ticket":
        stmt = select(cls).where(cls.id == id)
        res = await engine.execute(stmt)
        return res.scalar_one()

    @classmethod
    async def get_ticket_line_by_tid(
        cls, ticket_id: int, engine: AsyncEngine | AsyncSession
    ) -> List["TicketLine"]:
        stmt = select(cls).where(cls.ticket_id == ticket_id)
        res = await engine.execute(stmt)
        return res.scalars().all()

    @classmethod
    async def get_ticket_lines(
        cls, engine: AsyncEngine | AsyncSession
    ) -> List["TicketLine"]:
        stmt = select(cls).order_by(cls.id)
        res = await engine.execute(stmt)
        return res.scalars().all()
