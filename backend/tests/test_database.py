from threading import Event, Thread

from app.database import get_db


def test_get_db_serializes_sessions():
    first_session = get_db()
    next(first_session)

    second_started = Event()
    second_acquired = Event()

    def acquire_second_session():
        second_started.set()
        second_session = get_db()
        next(second_session)
        second_acquired.set()
        second_session.close()

    thread = Thread(target=acquire_second_session)
    thread.start()
    try:
        assert second_started.wait(timeout=1)
        assert not second_acquired.wait(timeout=0.1)
    finally:
        first_session.close()

    assert second_acquired.wait(timeout=1)
    thread.join(timeout=1)
    assert not thread.is_alive()
