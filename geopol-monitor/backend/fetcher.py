"""
Dual-engine fetcher v1.2:
  1. RSS/Atom parser via feedparser
  2. HTML scraper via requests + BeautifulSoup
  3. Stealth mode for bot-blocking sites (WION, etc.)

Includes retry logic, user-agent rotation, SSL bypass, and rate limiting.
"""

import logging
import time
import random
import re
from datetime import datetime
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed

import feedparser
import requests
from bs4 import BeautifulSoup

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from db import upsert_article, update_feed_status, log_fetch

logger = logging.getLogger("fetcher")

USER_AGENTS = [
    "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
]

# More convincing headers for sites with aggressive bot detection
STEALTH_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Cache-Control": "max-age=0",
    "sec-ch-ua": '"Chromium";v="125", "Not.A/Brand";v="24", "Google Chrome";v="125"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
}

REQUEST_TIMEOUT = 25
MAX_WORKERS = 6


def _session(stealth=False):
    s = requests.Session()
    if stealth:
        s.headers.update(STEALTH_HEADERS)
    else:
        s.headers.update({
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9,es;q=0.8",
        })
    return s


def _clean_text(text):
    if not text:
        return ""
    text = BeautifulSoup(text, "html.parser").get_text(separator=" ", strip=True)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:500]


def _parse_date(entry):
    """Extract date from feedparser entry."""
    for field in ("published_parsed", "updated_parsed", "created_parsed"):
        tp = getattr(entry, field, None)
        if tp:
            try:
                return datetime(*tp[:6]).isoformat()
            except Exception:
                pass
    for field in ("published", "updated", "created"):
        val = getattr(entry, field, None)
        if val:
            return val
    return ""


# =============================================================================
# RSS Fetcher
# =============================================================================

def fetch_rss(feed: dict) -> list:
    """Fetch and parse an RSS/Atom feed. Returns list of article dicts."""
    url = feed["url"]
    logger.info(f"[RSS] Fetching {feed['name']} — {url}")

    try:
        session = _session()
        verify = feed.get("ssl_verify", True)
        resp = session.get(url, timeout=REQUEST_TIMEOUT, verify=verify)
        resp.raise_for_status()
        parsed = feedparser.parse(resp.content)

        if parsed.bozo and not parsed.entries:
            raise ValueError(f"Feed parse error: {parsed.bozo_exception}")

        articles = []
        for entry in parsed.entries[:50]:
            title = _clean_text(getattr(entry, "title", ""))
            if not title:
                continue

            link = getattr(entry, "link", "")
            desc = _clean_text(
                getattr(entry, "summary", "")
                or getattr(entry, "description", "")
            )

            articles.append({
                "title": title,
                "link": link,
                "description": desc[:280],
                "pub_date": _parse_date(entry),
                "source_name": feed["name"],
                "country": feed["country"],
                "source_type": feed["type"],
                "site": feed["site"],
                "method": "rss",
            })

        return articles

    except Exception as e:
        logger.error(f"[RSS] Error fetching {feed['name']}: {e}")
        raise


# =============================================================================
# HTML Scraper
# =============================================================================

def fetch_scrape(feed: dict) -> list:
    """Scrape headlines from a page using CSS selectors. Returns article dicts."""
    scrape_url = feed["scrape_url"]
    config = feed["scrape_config"]
    stealth = feed.get("stealth", False)
    logger.info(f"[SCRAPE{'·STEALTH' if stealth else ''}] Fetching {feed['name']} — {scrape_url}")

    try:
        session = _session(stealth=stealth)
        verify = feed.get("ssl_verify", True)

        # For stealth mode: first hit the homepage to get cookies, then target page
        if stealth:
            base_url = f"{urlparse(scrape_url).scheme}://{urlparse(scrape_url).netloc}/"
            try:
                session.get(base_url, timeout=10, verify=verify)
                time.sleep(random.uniform(0.5, 1.5))
            except Exception:
                pass
            session.headers["Referer"] = base_url

        resp = session.get(scrape_url, timeout=REQUEST_TIMEOUT, verify=verify)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.content, "html.parser")

        articles = []
        seen_titles = set()

        # Strategy 1: Use article_selector to find containers
        containers = soup.select(config.get("article_selector", "article"))

        for container in containers[:60]:
            title_el = container.select_one(config.get("title_selector", "a"))
            if not title_el:
                continue

            title = _clean_text(title_el.get_text())
            if not title or len(title) < 10 or title.lower() in seen_titles:
                continue
            seen_titles.add(title.lower())

            # Extract link
            link = ""
            link_el = title_el if title_el.name == "a" else title_el.find_parent("a")
            if not link_el:
                link_el = container.select_one("a[href]")
            if link_el:
                raw_link = link_el.get(config.get("link_attr", "href"), "")
                if raw_link:
                    if raw_link.startswith("http"):
                        link = raw_link
                    elif raw_link.startswith("/"):
                        link = config.get("link_prefix", "") + raw_link
                    else:
                        link = urljoin(scrape_url, raw_link)

            # Extract description
            desc = ""
            desc_sel = config.get("desc_selector")
            if desc_sel:
                desc_el = container.select_one(desc_sel)
                if desc_el:
                    desc = _clean_text(desc_el.get_text())

            articles.append({
                "title": title,
                "link": link,
                "description": desc[:280],
                "pub_date": datetime.utcnow().isoformat(),
                "source_name": feed["name"],
                "country": feed["country"],
                "source_type": feed["type"],
                "site": feed["site"],
                "method": "scrape",
            })

        # Strategy 2: Fallback — broad headline extraction
        if not articles:
            logger.info(f"[SCRAPE] Fallback strategy for {feed['name']}")
            for link_el in soup.select("a[href]"):
                text = _clean_text(link_el.get_text())
                if not text or len(text) < 20 or len(text) > 300:
                    continue
                if text.lower() in seen_titles:
                    continue

                # Skip nav/footer links
                parent_tags = [p.name for p in link_el.parents]
                if "nav" in parent_tags or "footer" in parent_tags:
                    continue
                # Skip common non-article link patterns
                lower = text.lower()
                skip_words = ["subscribe", "sign in", "log in", "cookie", "privacy",
                              "terms of", "contact us", "about us", "advertise",
                              "copyright", "all rights"]
                if any(sw in lower for sw in skip_words):
                    continue

                seen_titles.add(text.lower())
                raw_link = link_el.get("href", "")
                if raw_link.startswith("http"):
                    link = raw_link
                elif raw_link.startswith("/"):
                    link = config.get("link_prefix", "") + raw_link
                else:
                    link = urljoin(scrape_url, raw_link)

                articles.append({
                    "title": text,
                    "link": link,
                    "description": "",
                    "pub_date": datetime.utcnow().isoformat(),
                    "source_name": feed["name"],
                    "country": feed["country"],
                    "source_type": feed["type"],
                    "site": feed["site"],
                    "method": "scrape",
                })

                if len(articles) >= 30:
                    break

        return articles

    except Exception as e:
        logger.error(f"[SCRAPE] Error fetching {feed['name']}: {e}")
        raise


# =============================================================================
# Orchestrator
# =============================================================================

def fetch_single(feed: dict) -> dict:
    """Fetch a single feed (RSS or scrape). Returns result dict."""
    try:
        if feed["method"] == "rss":
            articles = fetch_rss(feed)
        elif feed["method"] == "scrape":
            articles = fetch_scrape(feed)
        else:
            raise ValueError(f"Unknown method: {feed['method']}")

        new_count = 0
        for article in articles:
            if upsert_article(article):
                new_count += 1

        update_feed_status(
            feed["name"], feed["country"], feed["method"],
            "ok", len(articles)
        )

        logger.info(f"[OK] {feed['name']}: {len(articles)} articles, {new_count} new")
        return {
            "feed": feed["name"],
            "status": "ok",
            "total": len(articles),
            "new": new_count,
        }

    except Exception as e:
        update_feed_status(
            feed["name"], feed["country"], feed["method"],
            "error", 0, str(e)[:200]
        )
        logger.error(f"[FAIL] {feed['name']}: {e}")
        return {
            "feed": feed["name"],
            "status": "error",
            "error": str(e)[:200],
        }


def fetch_all(feeds: list, max_workers: int = MAX_WORKERS) -> dict:
    """Fetch all feeds concurrently. Returns summary."""
    start = time.time()
    results = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(fetch_single, f): f for f in feeds}
        for future in as_completed(futures):
            try:
                results.append(future.result())
            except Exception as e:
                feed = futures[future]
                results.append({
                    "feed": feed["name"],
                    "status": "error",
                    "error": str(e)[:200],
                })

    duration = time.time() - start
    ok = sum(1 for r in results if r["status"] == "ok")
    err = sum(1 for r in results if r["status"] == "error")
    new_articles = sum(r.get("new", 0) for r in results)

    log_fetch(len(feeds), ok, err, new_articles, duration)

    summary = {
        "feeds_total": len(feeds),
        "feeds_ok": ok,
        "feeds_error": err,
        "articles_new": new_articles,
        "duration_sec": round(duration, 2),
        "details": results,
    }

    logger.info(
        f"[DONE] {ok}/{len(feeds)} feeds OK, {new_articles} new articles "
        f"in {duration:.1f}s"
    )
    return summary
