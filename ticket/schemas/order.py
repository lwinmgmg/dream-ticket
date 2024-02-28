from typing import List, Optional
import strawberry
from strawberry.scalars import JSON
from strawberry.types import Info

from sqlalchemy.ext.asyncio import AsyncSession

from ticket.models.ticket import TicketLine
from ticket.models.order import OrderState, Order, OrderLine

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
class OrderGql:
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

    @staticmethod
    async def get_orders(info: Info) -> List["OrderGql"]:
        session: AsyncSession = info.context.get("db_session")
        return [
            OrderGql.parse_obj(odr) for odr in await Order.get_orders(engine=session)
        ]

    @staticmethod
    async def get_tickets_query(
        info: Info,
        domain: Optional[JSON],
        order: Optional[JSON],
        limit: Optional[int] = 10,
        offset: Optional[int] = 0,
    ) -> List["OrderGql"]:
        session: AsyncSession = info.context.get("db_session")
        return [
            TicketGql.parse_obj(tkt)  # type: ignore
            for tkt in await Ticket.get_tickets_query(
                engine=session,
                query=Filter(
                    domain=domain, order=order, limit=limit, offset=offset
                ),  # type: ignore
            )
        ]


async def get_order_for_order_line(info: Info, root: "OrderLineGql") -> OrderGql:
    session: AsyncSession = info.context.get("db_session")
    return OrderGql.parse_obj(
        await Order.get_order_by_id(id=root.order_id, engine=session)
    )


async def get_ticket_line_for_order_line(
    info: Info, root: "OrderLineGql"
) -> TicketLineGql:
    session: AsyncSession = info.context.get("db_session")
    return TicketLineGql.parse_obj(
        await TicketLine.get_ticket_line_by_id(id=root.ticket_line_id, engine=session)
    )


@strawberry.type
class OrderLineGql:
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

    @staticmethod
    async def get_order_lines(info: Info) -> List["OrderLineGql"]:
        session: AsyncSession = info.context.get("db_session")
        return [
            OrderLineGql.parse_obj(odr)
            for odr in await OrderLine.get_order_lines(engine=session)
        ]
