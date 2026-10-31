from app.database import SessionLocal


def test_database_sessions_use_distinct_connections():
    first_session = SessionLocal()
    second_session = SessionLocal()
    try:
        first_connection = first_session.connection().connection.driver_connection
        second_connection = second_session.connection().connection.driver_connection

        assert first_connection is not second_connection
    finally:
        first_session.close()
        second_session.close()
