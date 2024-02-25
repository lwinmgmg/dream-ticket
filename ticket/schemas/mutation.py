import strawberry
from .ticket import TicketGql


@strawberry.type
class Mutation:
    add_ticket: TicketGql = strawberry.mutation(resolver=TicketGql.add_ticket)
