from typing import List, Optional
import strawberry
from strawberry.types import Info
from strawberry.scalars import JSON
from sqlalchemy.ext.asyncio import AsyncSession

from ticket.models.ticket import Ticket, TicketState, TicketLine, TicketLineState
from ticket.models.filter import Filter


class NoIdForUpdate(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


async def get_lines_for_ticket(info: Info, root: "TicketGql") -> List["TicketLineGql"]:
    session: AsyncSession = info.context.get("db_session")
    return [
        TicketLineGql.parse_obj(tl)
        for tl in await TicketLine.get_ticket_line_by_tid(
            ticket_id=root.id, engine=session  # type: ignore
        )
    ]


@strawberry.type
class TicketGql:
    id: strawberry.ID
    name: str
    state: TicketState
    description: str
    start_num: int
    end_num: int
    win_num: int
    available_count: int
    reserved_count: int
    sold_count: int
    lines: List["TicketLineGql"] = strawberry.field(resolver=get_lines_for_ticket)

    @classmethod
    def parse_obj(cls, model: Ticket) -> "TicketGql":
        return TicketGql(
            id=model.id,
            name=model.name,
            state=model.state,
            description=model.description,
            start_num=model.start_num,
            end_num=model.end_num,
            win_num=model.win_num,
            available_count=model.available_count,
            reserved_count=model.reserved_count,
            sold_count=model.sold_count,
        )

    @staticmethod
    async def get_tickets(info: Info) -> List["TicketGql"]:
        session: AsyncSession = info.context.get("db_session")
        return [
            TicketGql.parse_obj(tkt) for tkt in await Ticket.get_tickets(engine=session)
        ]

    @staticmethod
    async def get_ticket(info: Info, id: strawberry.ID) -> "TicketGql":
        session: AsyncSession = info.context.get("db_session")
        return TicketGql.parse_obj(
            await Ticket.get_ticket_by_id(id=int(id), engine=session)
        )

    @staticmethod
    async def get_tickets_query(
        info: Info,
        domain: Optional[JSON],
        order: Optional[JSON],
        limit: Optional[int] = 10,
        offset: Optional[int] = 0,
    ) -> List["TicketGql"]:
        session: AsyncSession = info.context.get("db_session")
        return [
            TicketGql.parse_obj(tkt)  # type: ignore
            for tkt in await Ticket.get_tickets_query(
                engine=session,
                query=Filter(
                    domain=domain, order=order, limit=limit, offset=offset
                ),  # type: ignore
            )
        ]

    @staticmethod
    async def add_ticket(info: Info, data: JSON) -> "TicketGql":
        session: AsyncSession = info.context.get("db_session")
        if "state" in data:
            data["state"] = getattr(TicketState, data["state"])
        new_record = Ticket(**data)
        await new_record.add_ticket(engine=session)
        return TicketGql.parse_obj(new_record)

    @staticmethod
    async def update_ticket(info: Info, data_list: JSON) -> List["TicketGql"]:
        session: AsyncSession = info.context.get("db_session")
        for data in data_list:
            if not data.get("id"):
                raise NoIdForUpdate("No id found for update ticket")
        return [
            TicketGql.parse_obj(tkt)
            for tkt in await Ticket.update_ticket(engine=session, data_list=data_list)
        ]


async def get_ticket_for_line(info: Info, root: "TicketLineGql") -> TicketGql:
    session: AsyncSession = info.context.get("db_session")
    tkt = await Ticket.get_ticket_by_id(id=root.ticket_id, engine=session)
    return TicketGql.parse_obj(tkt)


@strawberry.type
class TicketLineGql:
    id: strawberry.ID
    number: int
    ticket_id: int
    ticket: TicketGql = strawberry.field(resolver=get_ticket_for_line)
    user_code: Optional[str]
    is_special_price: bool
    special_price: float
    state: TicketLineState

    @staticmethod
    async def get_ticket_lines(info: Info):
        session: AsyncSession = info.context.get("db_session")
        return [
            TicketLineGql.parse_obj(tl)
            for tl in await TicketLine.get_ticket_lines(engine=session)
        ]

    @classmethod
    def parse_obj(cls, model: TicketLine) -> "TicketLineGql":
        return TicketLineGql(
            id=model.id,
            number=model.number,
            ticket_id=model.ticket_id,
            user_code=model.user_code,
            is_special_price=model.is_special_price,
            special_price=model.special_price,
            state=model.state,
        )

    @staticmethod
    async def get_ticket_lines_query(
        info: Info,
        domain: Optional[JSON],
        order: Optional[JSON],
        limit: Optional[int] = 10,
        offset: Optional[int] = 0,
    ) -> List["TicketLineGql"]:
        session: AsyncSession = info.context.get("db_session")
        return [
            TicketLineGql.parse_obj(tkt)
            for tkt in await TicketLine.get_ticket_lines_query(
                engine=session,
                query=Filter(domain=domain, order=order, limit=limit, offset=offset),
            )
        ]
