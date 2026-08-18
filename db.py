import os
import sqlite3
import threading

# Absolute path, so the db is found regardless of the process working directory.
DATABASE_NAME = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tidal.db")

# Indexes the query paths in controller.py depend on. Kept here (rather than
# only in the .db file) because tidal.db is replaced wholesale by
# pull_db_from_wasabi.sh, which would otherwise drop them.
#
# idx_predictions_station_utc is the important one: without it every
# /tide/predictions request SCANs all ~5.1M rows of tide_predictions and then
# sorts them in a temp B-tree. The composite (station_no, utc) index turns that
# into a range seek that also satisfies the ORDER BY.
INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_predictions_station_utc "
    "ON tide_predictions(station_no, utc);",
    "CREATE INDEX IF NOT EXISTS idx_tide_station_date "
    "ON tide(station_id, date_local);",
]

# One connection per thread, reused across requests. A fresh connection per
# request throws away SQLite's page cache every time, so each request re-reads
# from disk.
_local = threading.local()
_indexes_ready = False
_indexes_lock = threading.Lock()


def _ensure_indexes(conn):
    """Create the required indexes once per process. Idempotent."""
    global _indexes_ready
    if _indexes_ready:
        return
    with _indexes_lock:
        if _indexes_ready:
            return
        for statement in INDEXES:
            conn.execute(statement)
        conn.commit()
        _indexes_ready = True


def _connect():
    conn = sqlite3.connect(DATABASE_NAME, timeout=30.0)
    # WAL lets readers run while a writer holds the db, instead of blocking.
    #
    # Off by default: docker-compose bind-mounts tidal.db as a *single file*, so
    # the -wal/-shm sidecars would land in the container layer instead of next to
    # the db on the host. A hard `docker compose down` would then discard
    # committed writes, and pull_db_from_wasabi.sh swapping the host file out
    # from under a live -wal risks corruption. Bind-mount the containing
    # directory instead, then set SQLITE_WAL=1.
    if os.getenv("SQLITE_WAL") == "1":
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
    # Wait rather than immediately raising "database is locked" under contention.
    conn.execute("PRAGMA busy_timeout=30000;")
    # ~16MB of page cache per connection (negative = KiB, not pages).
    # Kept modest because there is one connection per worker thread.
    conn.execute("PRAGMA cache_size=-16384;")
    _ensure_indexes(conn)
    return conn


def get_db():
    conn = getattr(_local, "conn", None)
    if conn is None:
        conn = _connect()
        _local.conn = conn
    return conn
