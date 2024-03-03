from typing import List
import strawberry

from .ticket import TicketGql, TicketLineGql
from .order import OrderGql, OrderLineGql
from .order_func import OrderFuncGql


@strawberry.type
class Mutation:
    # Ticket
    add_ticket: TicketGql = strawberry.mutation(resolver=TicketGql.add_record)
    update_ticket: List[TicketGql] = strawberry.mutation(
        resolver=TicketGql.update_record
    )
    delete_ticket: bool = strawberry.mutation(resolver=TicketGql.delete_record)

    # TicketLine
    add_ticket_line: TicketLineGql = strawberry.mutation(
        resolver=TicketLineGql.add_record
    )
    update_ticket_line: List[TicketLineGql] = strawberry.mutation(
        resolver=TicketLineGql.update_record
    )
    delete_ticket_line: bool = strawberry.mutation(resolver=TicketLineGql.delete_record)

    # Order
    add_order: OrderGql = strawberry.mutation(resolver=OrderGql.add_record)
    update_order: List[OrderGql] = strawberry.mutation(resolver=OrderGql.update_record)
    delete_order: bool = strawberry.mutation(resolver=OrderGql.delete_record)

    # OrderLine
    add_order_line: OrderLineGql = strawberry.mutation(resolver=OrderGql.add_record)
    update_order_line: List[OrderLineGql] = strawberry.mutation(
        resolver=OrderLineGql.update_record
    )
    delete_order_line: bool = strawberry.mutation(resolver=OrderLineGql.delete_record)

    # ORDER AUTH Functions
    order_now: OrderGql = strawberry.field(resolver=OrderFuncGql.order_now)
    confirm_order: bool = strawberry.field(resolver=OrderFuncGql.confirm_order)
    cancel_order: bool = strawberry.field(resolver=OrderFuncGql.cancel_order)
