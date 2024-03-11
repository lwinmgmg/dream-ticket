from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
import strawberry
from strawberry.types import Info

from sqlalchemy.ext.asyncio import AsyncSession

from ticket.models.models import Filter
from ticket.models.ticket import TicketLine
from ticket.models.order import OrderState, Order, OrderLine

from .schemas import CommonSchema
from .ticket import TicketLineGql


async def get_order_lines_for_order(
    info: Info, root: "OrderGql"
) -> List["OrderLineGql"]:
    session: AsyncSession = info.context.get("ro_db_session")
    return [
        OrderLineGql.parse_obj(ol)
        for ol in await OrderLine.get_order_lines_by_order_id(root.id, engine=session)
    ]


class OrderData(BaseModel):
    id: Optional[int] = 0
    name: Optional[str] = ""
    state: Optional[OrderState] = None
    user_code: Optional[str] = ""


@strawberry.type
class OrderGql(CommonSchema):
    _model_type = Order
    _data_type = OrderData
    _model_enums = {"state": OrderState}

    id: strawberry.ID
    name: str
    state: OrderState
    user_code: Optional[str]
    lines: List["OrderLineGql"] = strawberry.field(resolver=get_order_lines_for_order)
    create_date: datetime
    write_date: datetime

    @classmethod
    def parse_obj(cls, model: Order) -> "OrderGql":
        return OrderGql(
            id=model.id,  # type: ignore
            name=model.name,
            state=model.state,
            user_code=model.user_code,
            create_date=model.create_date,
            write_date=model.write_date,
        )

    @classmethod
    async def my_orders(cls, info: Info) -> List["OrderGql"]:
        user_code = cls.get_user(info=info)
        session: AsyncSession = info.context.get("ro_db_session")
        return [
            OrderGql.parse_obj(odr)
            for odr in await Order.get_records_query(
                session,
                Filter(domain=[("user_code", "=", user_code)], limit=0, offset=0),
            )
        ]


async def get_order_for_order_line(info: Info, root: "OrderLineGql") -> OrderGql:
    session: AsyncSession = info.context.get("ro_db_session")
    return OrderGql.parse_obj(
        await Order.get_record_by_id(id=root.order_id, engine=session)
    )


async def get_ticket_line_for_order_line(
    info: Info, root: "OrderLineGql"
) -> TicketLineGql:
    session: AsyncSession = info.context.get("ro_db_session")
    return TicketLineGql.parse_obj(
        await TicketLine.get_record_by_id(id=root.ticket_line_id, engine=session)
    )


class OrderLineData(BaseModel):
    id: Optional[int] = 0
    order_id: Optional[int] = 0
    ticket_line_id: Optional[int] = 0


@strawberry.type
class OrderLineGql(CommonSchema):
    _model_type = OrderLine
    _data_type = OrderLineData
    _model_enums = {}

    id: strawberry.ID
    order_id: int
    order: OrderGql = strawberry.field(resolver=get_order_for_order_line)
    ticket_line_id: int
    ticket_line: TicketLineGql = strawberry.field(
        resolver=get_ticket_line_for_order_line
    )
    create_date: datetime
    write_date: datetime

    @classmethod
    def parse_obj(cls, model: OrderLine) -> "OrderLineGql":
        return OrderLineGql(
            id=model.id,  # type: ignore
            order_id=model.order_id,
            ticket_line_id=model.ticket_line_id,
            create_date=model.create_date,
            write_date=model.write_date,
        )
