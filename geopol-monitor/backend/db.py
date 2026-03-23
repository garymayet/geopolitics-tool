"""
SQLite storage for articles and feed status.
Uses WAL mode for concurrent read/write.
"""

import sqlite3
import json
import os
import threading
from datetime import datetime, timedelta
from contextlib import contextmanager

DB_PATH = os.environ.get("GEOPOL_DB", "/data/geopol.db")

_local = threading.local()


def _get_conn():
    if not hasattr(_local, "conn") or _local.conn is None:
        os.makedirs(os.path.dirname(DB_PATH) or ".", exist_ok=True)
        _local.conn = sqlite3.connect(DB_PATH, timeout=15)
        _local.conn.execute("PRAGMA journal_mode=WAL")
        _local.conn.execute("PRAGMA foreign_keys=ON")
        _local.conn.row_factory = sqlite3.Row
    return _local.conn


@contextmanager
def get_db():
    conn = _get_conn()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise


def init_db():
    with get_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hash TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                link TEXT,
                description TEXT,
                pub_date TEXT,
                source_name TEXT NOT NULL,
                country TEXT NOT NULL,
                source_type TEXT NOT NULL,
                site TEXT,
                fetched_at TEXT NOT NULL,
                method TEXT DEFAULT 'rss'
            );

            CREATE INDEX IF NOT EXISTS idx_articles_country ON articles(country);
            CREATE INDEX IF NOT EXISTS idx_articles_pub_date ON articles(pub_date DESC);
            CREATE INDEX IF NOT EXISTS idx_articles_source ON articles(source_name);
            CREATE INDEX IF NOT EXISTS idx_articles_hash ON articles(hash);

            CREATE TABLE IF NOT EXISTS feed_status (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                feed_name TEXT UNIQUE NOT NULL,
                country TEXT NOT NULL,
                method TEXT NOT NULL,
                last_fetch TEXT,
                last_status TEXT DEFAULT 'pending',
                article_count INTEGER DEFAULT 0,
                error_message TEXT
            );

            CREATE TABLE IF NOT EXISTS fetch_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                feeds_total INTEGER,
                feeds_ok INTEGER,
                feeds_error INTEGER,
                articles_new INTEGER,
                duration_sec REAL
            );
        """)


def upsert_article(article: dict) -> bool:
    """Insert article if not exists. Returns True if new."""
    import hashlib
    raw = f"{article['title']}|{article.get('link', '')}|{article['source_name']}"
    h = hashlib.sha256(raw.encode()).hexdigest()[:16]

    with get_db() as conn:
        try:
            conn.execute(
                """INSERT INTO articles (hash, title, link, description, pub_date,
                   source_name, country, source_type, site, fetched_at, method)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    h,
                    article["title"],
                    article.get("link", ""),
                    article.get("description", ""),
                    article.get("pub_date", ""),
                    article["source_name"],
                    article["country"],
                    article["source_type"],
                    article.get("site", ""),
                    datetime.utcnow().isoformat(),
                    article.get("method", "rss"),
                ),
            )
            return True
        except sqlite3.IntegrityError:
            return False


def update_feed_status(feed_name: str, country: str, method: str,
                       status: str, count: int = 0, error: str = None):
    with get_db() as conn:
        conn.execute(
            """INSERT INTO feed_status (feed_name, country, method, last_fetch,
               last_status, article_count, error_message)
               VALUES (?, ?, ?, ?, ?, ?, ?)
               ON CONFLICT(feed_name) DO UPDATE SET
               last_fetch=excluded.last_fetch,
               last_status=excluded.last_status,
               article_count=excluded.article_count,
               error_message=excluded.error_message""",
            (feed_name, country, method, datetime.utcnow().isoformat(),
             status, count, error),
        )


def log_fetch(total, ok, error, new_articles, duration):
    with get_db() as conn:
        conn.execute(
            """INSERT INTO fetch_log (timestamp, feeds_total, feeds_ok,
               feeds_error, articles_new, duration_sec)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (datetime.utcnow().isoformat(), total, ok, error,
             new_articles, round(duration, 2)),
        )


def get_articles(country=None, source_type=None, source_name=None,
                 search=None, limit=200, offset=0, hours=None):
    conditions = []
    params = []

    if country and country != "all":
        conditions.append("country = ?")
        params.append(country)
    if source_type and source_type != "all":
        conditions.append("source_type = ?")
        params.append(source_type)
    if source_name:
        conditions.append("source_name = ?")
        params.append(source_name)
    if search:
        conditions.append("(title LIKE ? OR description LIKE ? OR source_name LIKE ?)")
        q = f"%{search}%"
        params.extend([q, q, q])
    if hours:
        cutoff = (datetime.utcnow() - timedelta(hours=hours)).isoformat()
        conditions.append("fetched_at >= ?")
        params.append(cutoff)

    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    with get_db() as conn:
        rows = conn.execute(
            f"""SELECT id, title, link, description, pub_date, source_name,
                country, source_type, site, fetched_at, method
                FROM articles {where}
                ORDER BY
                    CASE WHEN pub_date IS NOT NULL AND pub_date != '' THEN pub_date ELSE fetched_at END DESC
                LIMIT ? OFFSET ?""",
            params + [limit, offset],
        ).fetchall()

        count_row = conn.execute(
            f"SELECT COUNT(*) as cnt FROM articles {where}", params
        ).fetchone()

    return {
        "articles": [dict(r) for r in rows],
        "total": count_row["cnt"],
        "limit": limit,
        "offset": offset,
    }


def get_feed_statuses():
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM feed_status ORDER BY country, feed_name"
        ).fetchall()
    return [dict(r) for r in rows]


def get_stats():
    with get_db() as conn:
        total = conn.execute("SELECT COUNT(*) as c FROM articles").fetchone()["c"]
        by_country = conn.execute(
            "SELECT country, COUNT(*) as c FROM articles GROUP BY country"
        ).fetchall()
        by_type = conn.execute(
            "SELECT source_type, COUNT(*) as c FROM articles GROUP BY source_type"
        ).fetchall()
        last_log = conn.execute(
            "SELECT * FROM fetch_log ORDER BY timestamp DESC LIMIT 1"
        ).fetchone()

    return {
        "total_articles": total,
        "by_country": {r["country"]: r["c"] for r in by_country},
        "by_type": {r["source_type"]: r["c"] for r in by_type},
        "last_fetch": dict(last_log) if last_log else None,
    }


def cleanup_old(days=7):
    cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
    with get_db() as conn:
        result = conn.execute("DELETE FROM articles WHERE fetched_at < ?", (cutoff,))
        return result.rowcount
