"""
Geopolítica Monitor — Backend API

Endpoints:
  GET  /api/articles         — List articles (filterable)
  GET  /api/feeds            — Feed status list
  GET  /api/stats            — Dashboard statistics
  POST /api/fetch            — Trigger manual fetch
  POST /api/fetch/<name>     — Fetch a single feed
  GET  /api/health           — Health check

Environment:
  GEOPOL_DB            — SQLite path (default: /data/geopol.db)
  FETCH_INTERVAL_MIN   — Auto-fetch interval (default: 15)
  CLEANUP_DAYS         — Article retention days (default: 7)
  FLASK_PORT           — Server port (default: 5000)
  FETCH_ON_START       — If "1", fetch immediately on startup
"""

import logging
import os
import threading

from flask import Flask, jsonify, request
from flask_cors import CORS

from db import init_db, get_articles, get_feed_statuses, get_stats
from feeds import FEEDS
from fetcher import fetch_all, fetch_single
from scheduler import start_scheduler, scheduled_fetch

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("api")

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})


# ── Articles ─────────────────────────────────────────────────────────────────

@app.route("/api/articles")
def api_articles():
    """
    Query params:
      country     — usa, china, russia, india, iran, all
      type        — news, state, analysis, thinktank, all
      source      — exact source name
      q           — search query (title, description, source)
      limit       — max results (default 200, max 500)
      offset      — pagination offset
      hours       — only articles fetched within N hours
    """
    country = request.args.get("country", "all")
    source_type = request.args.get("type", "all")
    source_name = request.args.get("source")
    search = request.args.get("q")
    limit = min(int(request.args.get("limit", 200)), 500)
    offset = int(request.args.get("offset", 0))
    hours = request.args.get("hours")
    if hours:
        hours = int(hours)

    data = get_articles(
        country=country,
        source_type=source_type,
        source_name=source_name,
        search=search,
        limit=limit,
        offset=offset,
        hours=hours,
    )
    return jsonify(data)


# ── Feed Status ──────────────────────────────────────────────────────────────

@app.route("/api/feeds")
def api_feeds():
    statuses = get_feed_statuses()
    return jsonify({
        "feeds": statuses,
        "total": len(statuses),
        "definitions": [
            {
                "name": f["name"],
                "country": f["country"],
                "type": f["type"],
                "site": f["site"],
                "method": f["method"],
            }
            for f in FEEDS
        ],
    })


# ── Stats ────────────────────────────────────────────────────────────────────

@app.route("/api/stats")
def api_stats():
    return jsonify(get_stats())


# ── Manual Fetch ─────────────────────────────────────────────────────────────

@app.route("/api/fetch", methods=["POST"])
def api_fetch_all():
    """Trigger a full fetch of all feeds. Runs in background."""
    country = request.json.get("country") if request.is_json else None

    feeds = FEEDS
    if country and country != "all":
        feeds = [f for f in FEEDS if f["country"] == country]

    def _run():
        fetch_all(feeds)

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()

    return jsonify({
        "status": "started",
        "feeds_count": len(feeds),
        "message": f"Fetching {len(feeds)} feeds in background",
    })


@app.route("/api/fetch/<feed_name>", methods=["POST"])
def api_fetch_single(feed_name):
    """Fetch a single feed by name."""
    feed = next((f for f in FEEDS if f["name"] == feed_name), None)
    if not feed:
        return jsonify({"error": f"Feed '{feed_name}' not found"}), 404

    result = fetch_single(feed)
    return jsonify(result)


# ── Health ───────────────────────────────────────────────────────────────────

@app.route("/api/health")
def api_health():
    stats = get_stats()
    return jsonify({
        "status": "ok",
        "total_articles": stats["total_articles"],
        "feeds_configured": len(FEEDS),
    })


# ── Startup ──────────────────────────────────────────────────────────────────

def startup():
    init_db()
    logger.info(f"Database initialized at {os.environ.get('GEOPOL_DB', '/data/geopol.db')}")

    start_scheduler()

    if os.environ.get("FETCH_ON_START", "1") == "1":
        logger.info("Running initial fetch...")
        thread = threading.Thread(target=scheduled_fetch, daemon=True)
        thread.start()


if __name__ == "__main__":
    startup()
    port = int(os.environ.get("FLASK_PORT", 5000))
    logger.info(f"Starting API on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False)
