import os
import sqlite3
import tempfile
import pytest

# IMPORTANT: os.environ must be set BEFORE importing main.
# main.py reads DB_PATH at module load time. Keep this as the
# very first statement before any 'from main import ...' call.
TEST_DB = os.path.join(tempfile.gettempdir(), "taskkeeper_test.db")
os.environ["DB_PATH"] = TEST_DB

from fastapi.testclient import TestClient
from main import app, init_db


@pytest.fixture(autouse=True)
def fresh_db():
    """Create schema before each test; wipe all rows after.

    Why a temp file instead of :memory:?
    sqlite3.connect(':memory:') creates a NEW database per connection.
    get_db() opens a new connection per request, so POST and GET would
    each see a different (empty) database. A shared file path fixes this.
    The temp directory is outside the project root — no .gitignore needed.
    """
    init_db()
    yield
    with sqlite3.connect(TEST_DB) as conn:
        conn.execute("DELETE FROM tasks")
        conn.commit()


@pytest.fixture
def client():
    return TestClient(app)
