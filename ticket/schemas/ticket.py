from typing import List
import strawberry
from strawberry.types import Info
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ticket.models.ticket import Ticket, TicketLine

async def get_lines_for_ticket(info: Info, root: "TicketGql")->List["TicketLineGql"]:
    session : AsyncSession = info.context.get('db_session')
    stmt = select(TicketLine).where(TicketLine.ticket_id==root.id)
    res = await session.execute(stmt)
    return [TicketLineGql(id=tl.id, number=tl.number, ticket=root) for tl in res.scalars()]

@strawberry.type
class TicketGql:
    id: strawberry.ID
    name: str
    lines: List["TicketLineGql"] = strawberry.field(resolver=get_lines_for_ticket, name="ticket_lines")

async def get_tickets(info: Info):
    session : AsyncSession = info.context.get('db_session')
    stmt = select(Ticket).order_by(Ticket.id)
    res = await session.execute(stmt)
    return [TicketGql(id=tkt.id, name=tkt.name) for tkt in res.scalars()]

@strawberry.type
class TicketLineGql:
    id: strawberry.ID
    ticket: TicketGql
    number: int
