from typing import List
import strawberry
from strawberry.types import Info
from sqlalchemy.ext.asyncio import AsyncSession

from ticket.models.order import Order
from .order import OrderGql


@strawberry.type
class OrderFuncGql(OrderGql):
    @classmethod
    async def order_now(cls, info: Info, ticket_line_ids: List[int]) -> "OrderGql":
        user_code = cls.get_user(info=info)
        session: AsyncSession = info.context.get("db_session")
        return cls.parse_obj(
            await Order.order_now(
                tkt_line_ids=ticket_line_ids, user_code=user_code, session=session
            )
        )

    @classmethod
    async def confirm_order(cls, info: Info, record_id: int) -> bool:
        user_code = cls.get_user(info=info)
        session: AsyncSession = info.context.get("db_session")
        return await Order.confirm_order(
            record_id=record_id, user_code=user_code, session=session
        )
