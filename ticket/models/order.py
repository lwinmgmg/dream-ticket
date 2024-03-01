from enum import Enum
from typing import List
from sqlalchemy import String, ForeignKey, select
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.ext.asyncio import AsyncSession
import strawberry

from .models import Base, CommonModel
from .ticket import TicketLine


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