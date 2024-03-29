from typing import Callable, Any, List
from strawberry.types import Info
from strawberry.extensions import FieldExtension

from ticket.env.settings import load_setting_from_env

settings = load_setting_from_env()


class UnauthorizeError(Exception):
    pass


class AuthExtension(FieldExtension):
    def __init__(self, scopes: List[str]) -> None:
        self.scopes = scopes
        super().__init__()

    async def resolve_async(
        self, next_: Callable[..., Any], source: Any, info: Info, **kwargs
    ):
        user_scopes: List[str] = info.context.get("scopes")
        if user_scopes:
            for scope in self.scopes:
                if scope in user_scopes:
                    return await next_(source, info, **kwargs)
        raise UnauthorizeError("Unauthorized")


OrderReadExt = AuthExtension(
    scopes=[
        settings.services.user.scopes.user_read,
        settings.services.user.scopes.order_read,
        settings.services.user.scopes.order_all,
    ]
)

OrderAllExt = AuthExtension(scopes=[settings.services.user.scopes.order_all])
