from typing import List
import strawberry
from .ticket import TicketGql


@strawberry.type
class Mutation:
    add_ticket: TicketGql = strawberry.mutation(resolver=TicketGql.add_ticket)
    update_ticket: List[TicketGql] = strawberry.mutation(
        resolver=TicketGql.update_ticket
    )
