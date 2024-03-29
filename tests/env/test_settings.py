import os
from ticket.env.settings import load_setting, load_setting_from_env


def test_load_setting():
    settings = load_setting("settings.yaml.example")
    assert settings.services.postgres.ro_db.user == "admin"
    assert settings.services.postgres.ro_db.password == "admin"


def test_load_setting_from_env():
    os.putenv("TICKET_SETTING_PATH", "setting.yaml.example")
    settings = load_setting_from_env()
    assert settings.services.postgres.ro_db.user == "admin"
    assert settings.services.postgres.ro_db.password == "admin"
