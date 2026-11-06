from app.database import _database_lock, get_db


def test_database_access_is_locked_for_session_lifetime():
    db_generator = get_db()
    next(db_generator)

    assert not _database_lock.acquire(blocking=False)

    db_generator.close()
    assert _database_lock.acquire(blocking=False)
    _database_lock.release()
