from typing import List
import strawberry

from .ticket import TicketGql, TicketLineGql
from .order import OrderGql, OrderLineGql


@strawberry.type
class Mutation:
    add_ticket: TicketGql = strawberry.mutation(resolver=TicketGql.add_record)
    update_ticket: List[TicketGql] = strawberry.mutation(
        resolver=TicketGql.update_record
    )

    add_ticket_line: TicketLineGql = strawberry.mutation(
        resolver=TicketLineGql.add_record
    )
    update_ticket_line: List[TicketLineGql] = strawberry.mutation(
        resolver=TicketLineGql.update_record
    )

    add_order: OrderGql = strawberry.mutation(resolver=OrderGql.add_record)
    update_order: List[OrderGql] = strawberry.mutation(resolver=OrderGql.update_record)

    add_order_line: OrderLineGql = strawberry.mutation(resolver=OrderGql.add_record)
    update_order_line: List[OrderLineGql] = strawberry.mutation(
        resolver=OrderLineGql.update_record
    )

    # ORDER AUTH
    order_now: OrderGql = strawberry.field(resolver=OrderGql.order_now)
