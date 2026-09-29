from sqlalchemy import create_engine, inspect, text

from app.database import session as database_session


def test_legacy_sqlite_schema_receives_company_and_customer_whatsapp_columns(monkeypatch):
    legacy_engine = create_engine("sqlite:///:memory:")
    with legacy_engine.begin() as connection:
        connection.execute(text("CREATE TABLE companies (id INTEGER PRIMARY KEY, name VARCHAR)"))
        connection.execute(
            text(
                "CREATE TABLE customers "
                "(id INTEGER PRIMARY KEY, company_id INTEGER NOT NULL, name VARCHAR NOT NULL)"
            )
        )

    monkeypatch.setattr(database_session, "engine", legacy_engine)
    database_session.ensure_company_admin_columns()
    database_session.ensure_customer_whatsapp_phone_column()

    inspector = inspect(legacy_engine)
    company_columns = {column["name"] for column in inspector.get_columns("companies")}
    customer_columns = {column["name"] for column in inspector.get_columns("customers")}

    assert {
        "display_name",
        "cancellation_policy",
        "default_timezone",
        "reminder_lead_minutes",
        "average_ticket_amount",
        "bot_name",
        "whatsapp_number",
    } <= company_columns
    assert "whatsapp_phone" in customer_columns
    assert "uq_customer_company_whatsapp_phone" in {
        index["name"] for index in inspector.get_indexes("customers")
    }
    legacy_engine.dispose()