from typing import List, Optional
import strawberry
from strawberry.types import Info

from sqlalchemy.ext.asyncio import AsyncSession

from ticket.models.ticket import TicketLine
from ticket.models.order import OrderState, Order, OrderLine

from .schemas import CommonSchema
from .ticket import TicketLineGql


async def get_order_lines_for_order(
    info: Info, root: "OrderGql"
) -> List["OrderLineGql"]:
    session: AsyncSession = info.context.get("db_session")
    return [
        OrderLineGql.parse_obj(ol)
        for ol in await OrderLine.get_order_lines_by_order_id(root.id, engine=session)
    ]


@strawberry.type
class OrderGql(CommonSchema):
    _model_type = Order
    _model_enums = {"state": OrderState}

    id: strawberry.ID
    name: str
    state: OrderState
    user_code: Optional[str]
    lines: List["OrderLineGql"] = strawberry.field(resolver=get_order_lines_for_order)

    @classmethod
    def parse_obj(cls, model: Order) -> "OrderGql":
        return OrderGql(
            id=model.id,  # type: ignore
            name=model.name,
            state=model.state,
            user_code=model.user_code,
        )


async def get_order_for_order_line(info: Info, root: "OrderLineGql") -> OrderGql:
    session: AsyncSession = info.context.get("db_session")
    return OrderGql.parse_obj(
        await Order.get_record_by_id(id=root.order_id, engine=session)
    )


async def get_ticket_line_for_order_line(
    info: Info, root: "OrderLineGql"
) -> TicketLineGql:
    session: AsyncSession = info.context.get("db_session")
    return TicketLineGql.parse_obj(
        await TicketLine.get_record_by_id(id=root.ticket_line_id, engine=session)
    )


@strawberry.type
class OrderLineGql(CommonSchema):
    _model_type = OrderLine
    _model_enums = {}

    id: strawberry.ID
    order_id: int
    order: OrderGql = strawberry.field(resolver=get_order_for_order_line)
    ticket_line_id: int
    ticket_line: TicketLineGql = strawberry.field(
        resolver=get_ticket_line_for_order_line
    )

    @classmethod
    def parse_obj(cls, model: OrderLine) -> "OrderLineGql":
        return OrderLineGql(
            id=model.id,  # type: ignore
            order_id=model.order_id,
            ticket_line_id=model.ticket_line_id,
        )
