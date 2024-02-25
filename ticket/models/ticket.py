from typing import List
from sqlalchemy import String, ForeignKey
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

class Base(AsyncAttrs, DeclarativeBase):
    pass

class Ticket(Base):
    __tablename__ = "ticket"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))

    line_ids: Mapped[List["TicketLine"]] = relationship(
        back_populates="ticket",
    )

    def __repr__(self) -> str:
        return f"Ticket(id={self.id!r}, name={self.name!r})"

class TicketLine(Base):
    __tablename__ = "ticket_line"

    id: Mapped[int] = mapped_column(primary_key=True)
    number: Mapped[int] = mapped_column(nullable=False)
    ticket_id: Mapped[int] = mapped_column(ForeignKey("ticket.id"), index=True)
    ticket: Mapped[Ticket] = relationship(back_populates="line_ids")

    def __repr__(self) -> str:
        return f"TicketLine(id={self.id!r}, name={self.number})"
