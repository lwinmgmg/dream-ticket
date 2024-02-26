from typing import List, Optional
import strawberry

from ticket.models.order import OrderState

from .ticket import TicketLineGql

@strawberry.type
class OrderGql:
    id: strawberry.ID
    name: str
    state: OrderState
    user_code: Optional[str]
    line_ids: List["OrderLineGql"]

@strawberry.type
class OrderLineGql:
    id: strawberry.ID
    order_id: int
    order: OrderGql
    ticket_line_id: int
    ticket_line: TicketLineGql
