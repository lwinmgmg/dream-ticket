from typing import List
import strawberry
from strawberry.types import Info
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

@strawberry.type
class TicketGql:
    id: strawberry.ID
    ticket_lines: List["TicketLineGql"]

async def get_tickets(info: Info):
    session : AsyncSession = info.context.get('db_session')
    await session.execute(text("SELECT 1"))
    return []

@strawberry.type
class TicketLineGql:
    id: strawberry.ID
    ticket: TicketGql
    number: int
