from enum import Enum
from typing import List, Dict
from sqlalchemy import String, ForeignKey, select
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.ext.asyncio import AsyncSession
import strawberry

from .models import Base, CommonModel
from .ticket import Ticket, TicketLine, TicketLineState, TicketLineNotAvailable


@strawberry.enum
class OrderState(Enum):
    DRAFT = "draft"
    CANCEL = "cancel"
    SUCCESSFUL = "successful"
    VARIFIED = "varified"


class Order(Base, CommonModel):
    __tablename__ = "order"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(15), index=True)
    state: Mapped[OrderState] = mapped_column(default=OrderState.DRAFT, index=True)
    user_code: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    # payment_id: Mapped[int] = mapped_column(ForeignKey("payment.id"))
    line_ids: Mapped[List["OrderLine"]] = relationship(
        back_populates="order",
    )

    @classmethod
    async def order_now(
        cls, tkt_line_ids: List[int], user_code: str, session: AsyncSession
    ) -> "Order":
        res = await session.execute(
            select(TicketLine).where(TicketLine.id.in_(tkt_line_ids)).with_for_update()
        )
        tkt_lines = res.scalars().all()
        order = cls(name="order", state=OrderState.DRAFT, user_code=user_code)
        session.add(order)
        await session.flush()
        order_lines: List[OrderLine] = []
        ticket_id_map: Dict[int, int] = {}
        for tkt_line in tkt_lines:
            if tkt_line.state != TicketLineState.AVAILABLE:
                raise TicketLineNotAvailable(f"Ticket Line ID - {tkt_line.id}")
            ticket_id_map[tkt_line.ticket_id] = 0
            tkt_line.state = TicketLineState.RESERVED
            tkt_line.user_code = user_code
            order_lines.append(OrderLine(order_id=order.id, ticket_line_id=tkt_line.id))
        res = await session.execute(
            select(Ticket).where(Ticket.id.in_(ticket_id_map.keys())).with_for_update()
        )
        tkts = res.scalars().all()
        for tkt in tkts:
            tkt.available_count -= ticket_id_map[tkt.id]
            tkt.reserved_count += ticket_id_map[tkt.id]
        session.add_all(order_lines)
        await session.flush()
        return order


class OrderLine(Base, CommonModel):
    __tablename__ = "order_line"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("order.id"), index=True)
    order: Mapped[Order] = relationship(back_populates="line_ids")
    ticket_line_id: Mapped[int] = mapped_column(
        ForeignKey("ticket_line.id"), index=True
    )
    ticket_line: Mapped[TicketLine] = relationship()

    @classmethod
    async def get_order_lines_by_order_id(
        cls, order_id: int, engine: AsyncSession
    ) -> List["OrderLine"]:
        stmt = select(cls).where(cls.order_id == order_id)
        res = await engine.execute(stmt)
        return res.scalars().all()
