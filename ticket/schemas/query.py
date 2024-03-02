from typing import List
import strawberry

from .order import OrderGql, OrderLineGql
from .ticket import TicketGql, TicketLineGql


@strawberry.type
class Query:
    tickets: List[TicketGql] = strawberry.field(resolver=TicketGql.get_records)
    ticket: TicketGql = strawberry.field(resolver=TicketGql.get_record)
    ticket_query: List[TicketGql] = strawberry.field(
        resolver=TicketGql.get_records_query
    )
    ticket_lines: List[TicketLineGql] = strawberry.field(
        resolver=TicketLineGql.get_records
    )
    ticket_line_query: List[TicketLineGql] = strawberry.field(
        resolver=TicketLineGql.get_records_query
    )

    # ORDER
    orders: List[OrderGql] = strawberry.field(resolver=OrderGql.get_records)
    order: OrderGql = strawberry.field(resolver=OrderGql.get_record)
    order_query: List[OrderGql] = strawberry.field(resolver=OrderGql.get_records_query)

    order_lines: List[OrderLineGql] = strawberry.field(
        resolver=OrderLineGql.get_records
    )
    order_line: OrderLineGql = strawberry.field(resolver=OrderLineGql.get_record)
    order_line_query: List[OrderLineGql] = strawberry.field(
        resolver=OrderLineGql.get_records_query
    )
