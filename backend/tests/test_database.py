from concurrent.futures import ThreadPoolExecutor
from threading import Barrier, Lock
import time

from app.database import get_db


def test_database_sessions_are_serialized():
    start = Barrier(3)
    state_lock = Lock()
    active_sessions = 0
    peak_sessions = 0

    def use_session():
        nonlocal active_sessions, peak_sessions
        start.wait()
        session_generator = get_db()
        next(session_generator)
        with state_lock:
            active_sessions += 1
            peak_sessions = max(peak_sessions, active_sessions)
        time.sleep(0.05)
        with state_lock:
            active_sessions -= 1
        session_generator.close()

    with ThreadPoolExecutor(max_workers=2) as executor:
        workers = [executor.submit(use_session) for _ in range(2)]
        start.wait()
        for worker in workers:
            worker.result()

    assert peak_sessions == 1
