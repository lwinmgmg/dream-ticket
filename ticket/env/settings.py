import os
from yaml import load, Loader
from pydantic import BaseModel

DEFAULT_SETTING_PATH = "settings.yaml"


class Server(BaseModel):
    host: str
    port: int


class Credential(BaseModel):
    user: str
    password: str


class Postgres(Server, Credential):
    database: str


class Odoo(Credential):
    url: str


class PgDbs(BaseModel):
    db: Postgres
    ro_db: Postgres


class UserHttp(BaseModel):
    url: str
    redirect_url: str


class Scopes(BaseModel):
    user_read: str
    order_read: str
    order_all: str


class UserService(BaseModel):
    http: UserHttp
    grpc: Server
    client_id: str
    client_secret: str
    scopes: Scopes


class Services(BaseModel):
    odoo: Odoo
    user: UserService
    postgres: PgDbs


class Settings(BaseModel):
    version: str
    services: Services


def load_setting(path: str) -> Settings:
    with open(path, "r", encoding="utf-8") as file:
        data = load(file, Loader=Loader)
        return Settings.model_validate(data)


def load_setting_from_env():
    path = os.getenv("TICKET_SETTING_PATH", DEFAULT_SETTING_PATH)
    return load_setting(path=path)
