from typing import List, Optional
import strawberry
from strawberry.types import Info
from strawberry.scalars import JSON
from sqlalchemy.ext.asyncio import AsyncSession

from ticket.models.ticket import Ticket, TicketState, TicketLine, TicketLineState
from ticket.models.models import Filter

from .schemas import CommonSchema


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
class TicketGql(CommonSchema):
    _model_type = Ticket
    _model_enums = {"state": TicketState}

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
    async def update_ticket(info: Info, data_list: JSON) -> List["TicketGql"]:
        session: AsyncSession = info.context.get("db_session")
        for data in data_list:
            if not data.get("id"):
                raise NoIdForUpdate("No id found for update ticket")
        return [
            TicketGql.parse_obj(tkt)
            for tkt in await Ticket.update_records(engine=session, data_list=data_list)
        ]


async def get_ticket_for_line(info: Info, root: "TicketLineGql") -> TicketGql:
    session: AsyncSession = info.context.get("db_session")
    tkt = await Ticket.get_record_by_id(id=root.ticket_id, engine=session)
    return TicketGql.parse_obj(tkt)


@strawberry.type
class TicketLineGql(CommonSchema):
    _model_type = TicketLine
    _model_enums = {"state": TicketLineState}

    id: strawberry.ID
    number: int
    ticket_id: int
    ticket: TicketGql = strawberry.field(resolver=get_ticket_for_line)
    user_code: Optional[str]
    is_special_price: bool
    special_price: float
    state: TicketLineState

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
