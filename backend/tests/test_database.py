from app.database import engine


def test_concurrent_connection_checkouts_are_independent():
    with engine.connect() as first, engine.connect() as second:
        assert first.connection.driver_connection is not second.connection.driver_connection
