from typing import List, Optional
import strawberry
from strawberry.types import Info
from strawberry.scalars import JSON
from sqlalchemy.ext.asyncio import AsyncSession

from ticket.models.ticket import Ticket, TicketLine
from ticket.models.filter import Filter


async def get_lines_for_ticket(info: Info, root: "TicketGql") -> List["TicketLineGql"]:
    session: AsyncSession = info.context.get("db_session")
    return [
        TicketLineGql(id=tl.id, number=tl.number, ticket_id=root.id)
        for tl in await TicketLine.get_ticket_line_by_tid(
            ticket_id=root.id, engine=session
        )
    ]


@strawberry.type
class TicketGql:
    id: strawberry.ID
    name: str
    lines: List["TicketLineGql"] = strawberry.field(
        resolver=get_lines_for_ticket, name="ticket_lines"
    )

    @staticmethod
    async def get_tickets(info: Info):
        session: AsyncSession = info.context.get("db_session")
        return [
            TicketGql(id=tkt.id, name=tkt.name)
            for tkt in await Ticket.get_tickets(engine=session)
        ]

    @staticmethod
    async def get_tickets_query(
        info: Info,
        domain: Optional[JSON],
        order: Optional[JSON],
        limit: Optional[int] = 10,
        offset: Optional[int] = 0,
    ) -> "TicketGql":
        session: AsyncSession = info.context.get("db_session")
        return [
            TicketGql(id=tkt.id, name=tkt.name)
            for tkt in await Ticket.get_tickets_query(
                engine=session, query=Filter(domain=domain, order=order, limit=limit, offset=offset)
            )
        ]


async def get_ticket_for_line(info: Info, root: "TicketLineGql") -> TicketGql:
    session: AsyncSession = info.context.get("db_session")
    tkt = await Ticket.get_ticket_by_id(id=root.ticket_id, engine=session)
    return TicketGql(id=tkt.id, name=tkt.name)


@strawberry.type
class TicketLineGql:
    id: strawberry.ID
    number: int
    ticket_id: int = strawberry.field(name="ticket_id")
    ticket: TicketGql = strawberry.field(resolver=get_ticket_for_line)

    @staticmethod
    async def get_ticket_lines(info: Info):
        session: AsyncSession = info.context.get("db_session")
        return [
            TicketLineGql(id=tl.id, number=tl.number, ticket_id=tl.ticket_id)
            for tl in await TicketLine.get_ticket_lines(engine=session)
        ]
