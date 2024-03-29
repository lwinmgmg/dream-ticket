from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
import strawberry
from strawberry.types import Info
from sqlalchemy.ext.asyncio import AsyncSession

from ticket.models.ticket import Ticket, TicketState, TicketLine, TicketLineState

from .schemas import CommonSchema


async def get_lines_for_ticket(info: Info, root: "TicketGql") -> List["TicketLineGql"]:
    session: AsyncSession = info.context.get("ro_db_session")
    return [
        TicketLineGql.parse_obj(tl)
        for tl in await TicketLine.get_ticket_line_by_tid(
            ticket_id=root.id, engine=session  # type: ignore
        )
    ]


class TicketData(BaseModel):
    id: Optional[int] = 0
    name: Optional[str] = ""
    state: Optional[TicketState] = None
    description: Optional[str] = ""
    price: Optional[float] = 0.0
    start_num: Optional[int] = 0
    end_num: Optional[int] = 0
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    win_num: Optional[int] = 0
    available_count: Optional[int] = 0
    reserved_count: Optional[int] = 0
    sold_count: Optional[int] = 0
    sync_user: Optional[str] = ""


@strawberry.type
class TicketGql(CommonSchema):
    _model_type = Ticket
    _data_type = TicketData
    _model_enums = {"state": TicketState}

    id: strawberry.ID
    name: str
    state: TicketState
    description: Optional[str] = strawberry.field(default="")
    price: float
    start_num: int
    end_num: int
    start_date: datetime
    end_date: datetime
    win_num: Optional[int] = strawberry.field(default=0)
    available_count: int
    reserved_count: int
    sold_count: int
    lines: List["TicketLineGql"] = strawberry.field(resolver=get_lines_for_ticket)
    sync_user: str
    create_date: datetime
    write_date: datetime

    @classmethod
    def parse_obj(cls, model: Ticket) -> "TicketGql":
        return TicketGql(
            id=model.id,
            name=model.name,
            state=model.state,
            description=model.description,
            price=model.price,
            start_num=model.start_num,
            end_num=model.end_num,
            start_date=model.start_date,
            end_date=model.end_date,
            win_num=model.win_num,
            available_count=model.available_count,
            reserved_count=model.reserved_count,
            sold_count=model.sold_count,
            sync_user=model.sync_user,
            create_date=model.create_date,
            write_date=model.write_date,
        )


async def get_ticket_for_line(info: Info, root: "TicketLineGql") -> TicketGql:
    session: AsyncSession = info.context.get("ro_db_session")
    tkt = await Ticket.get_record_by_id(id=root.ticket_id, engine=session)
    return TicketGql.parse_obj(tkt)


class TicketLineData(BaseModel):
    id: Optional[int] = 0
    number: Optional[int] = 0
    ticket_id: Optional[int] = 0
    user_code: Optional[str] = ""
    is_special_price: Optional[bool] = False
    special_price: Optional[float] = 0.0
    state: Optional[TicketLineState] = None


@strawberry.type
class TicketLineGql(CommonSchema):
    _model_type = TicketLine
    _data_type = TicketLineData
    _model_enums = {"state": TicketLineState}

    id: strawberry.ID
    number: int
    ticket_id: int
    ticket: TicketGql = strawberry.field(resolver=get_ticket_for_line)
    user_code: Optional[str]
    is_special_price: bool
    special_price: float
    state: TicketLineState
    create_date: datetime
    write_date: datetime

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
            create_date=model.create_date,
            write_date=model.write_date,
        )
