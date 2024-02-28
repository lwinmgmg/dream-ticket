from typing import List
import strawberry

from .order import OrderGql, OrderLineGql
from .ticket import TicketGql, TicketLineGql


@strawberry.type
class Query:
    tickets: List[TicketGql] = strawberry.field(resolver=TicketGql.get_tickets)
    ticket: TicketGql = strawberry.field(resolver=TicketGql.get_ticket)
    ticket_query: List[TicketGql] = strawberry.field(
        resolver=TicketGql.get_tickets_query
    )
    ticket_lines: List[TicketLineGql] = strawberry.field(
        resolver=TicketLineGql.get_ticket_lines
    )
    ticket_line_query: List[TicketLineGql] = strawberry.field(
        resolver=TicketLineGql.get_ticket_lines_query
    )

    orders: List[OrderGql] = strawberry.field(resolver=OrderGql.get_orders)

    order_lines: List[OrderLineGql] = strawberry.field(
        resolver=OrderLineGql.get_order_lines
    )
