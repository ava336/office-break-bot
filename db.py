import sqlite3
from datetime import datetime, timezone
from config import DB_PATH, DEFAULT_BREAK_LIMITS

def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

def conn():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c

def init_db():
    with conn() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS employees (
            telegram_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            username TEXT,
            active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER NOT NULL,
            event_type TEXT NOT NULL,
            started_at TEXT NOT NULL,
            ended_at TEXT,
            limit_minutes INTEGER,
            late_minutes INTEGER DEFAULT 0
        );
        """)
        for k, v in DEFAULT_BREAK_LIMITS.items():
            db.execute("INSERT OR IGNORE INTO settings(key,value) VALUES (?,?)",
                       (f"limit_{k}", str(v)))

def register_employee(tid, name, username):
    with conn() as db:
        db.execute("""
        INSERT INTO employees(telegram_id,name,username,active,created_at)
        VALUES(?,?,?,?,?)
        ON CONFLICT(telegram_id) DO UPDATE SET
        name=excluded.name, username=excluded.username
        """, (tid, name, username or "", 1, now()))

def active_event(tid):
    with conn() as db:
        return db.execute("""
        SELECT * FROM events WHERE telegram_id=? AND ended_at IS NULL
        ORDER BY id DESC LIMIT 1
        """, (tid,)).fetchone()

def get_limits():
    with conn() as db:
        rows = db.execute("SELECT key,value FROM settings WHERE key LIKE 'limit_%'").fetchall()
    return {r["key"].replace("limit_", ""): int(r["value"]) for r in rows}

def set_limit(kind, minutes):
    with conn() as db:
        db.execute("""
        INSERT INTO settings(key,value) VALUES(?,?)
        ON CONFLICT(key) DO UPDATE SET value=excluded.value
        """, (f"limit_{kind}", str(minutes)))

def start_active(tid, event_type):
    limit = get_limits().get(event_type) if event_type in ("eat","smoke","toilet") else None
    with conn() as db:
        cur = db.execute("""
        INSERT INTO events(telegram_id,event_type,started_at,limit_minutes)
        VALUES(?,?,?,?)
        """, (tid, event_type, now(), limit))
        return cur.lastrowid

def close_active(tid):
    ev = active_event(tid)
    if not ev:
        return None
    end = datetime.now(timezone.utc)
    start = datetime.fromisoformat(ev["started_at"])
    duration = max(0, int((end-start).total_seconds()//60))
    late = max(0, duration-ev["limit_minutes"]) if ev["limit_minutes"] else 0
    with conn() as db:
        db.execute("UPDATE events SET ended_at=?, late_minutes=? WHERE id=?",
                   (end.isoformat(timespec="seconds"), late, ev["id"]))
    return ev, duration, late

def list_employees():
    with conn() as db:
        return db.execute("SELECT * FROM employees ORDER BY name").fetchall()

def all_events(limit=500):
    with conn() as db:
        return db.execute("""
        SELECT e.*, p.name, p.username
        FROM events e JOIN employees p ON p.telegram_id=e.telegram_id
        ORDER BY e.started_at DESC LIMIT ?
        """, (limit,)).fetchall()

init_db()
