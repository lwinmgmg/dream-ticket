from typing import List
import strawberry
from .ticket import TicketGql, get_tickets

@strawberry.type
class Query:
    tickets: List[TicketGql] = strawberry.field(resolver=get_tickets)
