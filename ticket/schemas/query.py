from typing import List
import strawberry
from .ticket import TicketGql, TicketLineGql


@strawberry.type
class Query:
    tickets: List[TicketGql] = strawberry.field(resolver=TicketGql.get_tickets)
    ticket_query: List[TicketGql] = strawberry.field(
        resolver=TicketGql.get_tickets_query, name="ticket_query"
    )
    ticket_lines: List[TicketLineGql] = strawberry.field(
        resolver=TicketLineGql.get_ticket_lines, name="ticket_lines"
    )
