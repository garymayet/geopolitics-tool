"""
Feed definitions for Geopolítica Monitor.
v1.2 — All feeds tested and patched 2026-03-23.

Changelog v1.2:
  - CSIS: RSS 404 → scraper on /analysis
  - GZERO Media: RSS 404 → scraper on /news
  - Geopolitical Monitor: RSS malformed → scraper
  - Carnegie: RSS returning 0 items → scraper
  - WION: 403 on both RSS and scrape → scraper with stealth flag
  - IRNA: scraper returning 0 → better selectors + fallback
  - Tehran Times: maintained as scraper (infrastructure unreliable)
"""

FEEDS = [
    # =========================================================================
    # USA — News & Analysis (12 feeds)
    # =========================================================================
    {
        "name": "CNN World",
        "country": "usa",
        "type": "news",
        "site": "cnn.com",
        "method": "rss",
        "url": "http://rss.cnn.com/rss/edition_world.rss",
    },
    {
        "name": "Foreign Policy",
        "country": "usa",
        "type": "analysis",
        "site": "foreignpolicy.com",
        "method": "rss",
        "url": "https://foreignpolicy.com/feed/",
    },
    {
        "name": "Foreign Affairs",
        "country": "usa",
        "type": "analysis",
        "site": "foreignaffairs.com",
        # /latest ya no existe (404); el sitio publica RSS oficial vigente.
        "method": "rss",
        "url": "https://www.foreignaffairs.com/rss.xml",
    },
    {
        "name": "The National Interest",
        "country": "usa",
        "type": "analysis",
        "site": "nationalinterest.org",
        # nationalinterest.org/feed responde 403 (Cloudflare JS challenge, no superable sin navegador)
        # → syndication oficial de Google News limitada al dominio del sitio.
        "method": "rss",
        "url": "https://news.google.com/rss/search?q=site:nationalinterest.org&hl=en-US&gl=US&ceid=US:en",
        "strip_title_suffix": " - The National Interest",
        "include_description": False,
    },
    {
        "name": "War on the Rocks",
        "country": "usa",
        "type": "analysis",
        "site": "warontherocks.com",
        "method": "rss",
        "url": "https://warontherocks.com/feed/",
    },
    {
        "name": "Brookings",
        "country": "usa",
        "type": "thinktank",
        "site": "brookings.edu",
        # Brookings deshabilitó su RSS (todo /feed/ redirige a HTML) → scrapeo de la portada,
        # que lista las tarjetas de artículos con enlace overlay al post.
        "method": "scrape",
        "scrape_url": "https://www.brookings.edu/",
        "scrape_config": {
            "article_selector": "article",
            "title_selector": ".article-title",
            "link_attr": "href",
            "link_prefix": "https://www.brookings.edu",
            "desc_selector": "",
        },
    },
    {
        "name": "CFR",
        "country": "usa",
        "type": "thinktank",
        "site": "cfr.org",
        "method": "scrape",
        "scrape_url": "https://www.cfr.org/latest",
        "scrape_config": {
            "article_selector": ".card, .media-object, article",
            "title_selector": "h3 a, h2 a, .card-title a, .title a",
            "link_attr": "href",
            "link_prefix": "https://www.cfr.org",
            "desc_selector": ".body p, .dek, .summary",
        },
    },
    # FIX v1.2: CSIS RSS 404 → scraper
    {
        "name": "CSIS",
        "country": "usa",
        "type": "thinktank",
        "site": "csis.org",
        "method": "scrape",
        "scrape_url": "https://www.csis.org/analysis",
        "scrape_config": {
            "article_selector": "article, .views-row, .node, .teaser, div[class*='card']",
            "title_selector": "h3 a, h2 a, .field--name-title a, a",
            "link_attr": "href",
            "link_prefix": "https://www.csis.org",
            "desc_selector": ".field--name-body p, .teaser__text, p, .dek",
        },
    },
    # FIX v1.2: Carnegie RSS returning 0 → scraper
    {
        "name": "Carnegie",
        "country": "usa",
        "type": "thinktank",
        "site": "carnegieendowment.org",
        "method": "scrape",
        "scrape_url": "https://carnegieendowment.org/research",
        "scrape_config": {
            "article_selector": "article, .card, .result-item, div[class*='card'], .listing-item",
            "title_selector": "h3 a, h2 a, .title a, a",
            "link_attr": "href",
            "link_prefix": "https://carnegieendowment.org",
            "desc_selector": "p, .dek, .summary, .description",
        },
    },
    # FIX v1.2: GZERO RSS 404 → scraper
    {
        "name": "GZERO Media",
        "country": "usa",
        "type": "analysis",
        "site": "gzeromedia.com",
        "method": "scrape",
        "scrape_url": "https://www.gzeromedia.com/news",
        "scrape_config": {
            "article_selector": "article, .post-item, .card, div[class*='post'], div[class*='article']",
            "title_selector": "h2 a, h3 a, .title a, a",
            "link_attr": "href",
            "link_prefix": "https://www.gzeromedia.com",
            "desc_selector": "p, .excerpt, .summary, .dek",
        },
    },
    # FIX v1.2: Geopolitical Monitor RSS malformed → scraper
    {
        "name": "Geopolitical Monitor",
        "country": "usa",
        "type": "analysis",
        "site": "geopoliticalmonitor.com",
        "method": "scrape",
        "scrape_url": "https://www.geopoliticalmonitor.com/",
        "scrape_config": {
            "article_selector": "article, .post, .entry, div[class*='post']",
            "title_selector": "h2 a, h3 a, .entry-title a, a",
            "link_attr": "href",
            "link_prefix": "",
            "desc_selector": "p, .entry-content p, .excerpt",
        },
    },
    {
        "name": "The Diplomat",
        "country": "usa",
        "type": "analysis",
        "site": "thediplomat.com",
        "method": "rss",
        "url": "https://thediplomat.com/feed/",
    },
    # =========================================================================
    # CHINA — State Media (5 feeds)
    # =========================================================================
    {
        "name": "CGTN",
        "country": "china",
        "type": "state",
        "site": "cgtn.com",
        "method": "rss",
        "url": "https://www.cgtn.com/subscribe/rss/section/world.xml",
    },
    {
        "name": "Xinhua",
        "country": "china",
        "type": "state",
        "site": "english.news.cn",
        "method": "scrape",
        "scrape_url": "https://english.news.cn/world/index.htm",
        "scrape_config": {
            "article_selector": ".tit, .item, .news-item, li",
            "title_selector": "a",
            "link_attr": "href",
            "link_prefix": "https://english.news.cn",
            "desc_selector": ".des, .desc, p",
        },
    },
    {
        "name": "China Daily",
        "country": "china",
        "type": "state",
        "site": "chinadaily.com.cn",
        "method": "rss",
        "url": "https://www.chinadaily.com.cn/rss/world_rss.xml",
    },
    {
        "name": "Global Times",
        "country": "china",
        "type": "state",
        "site": "globaltimes.cn",
        "method": "rss",
        "url": "https://www.globaltimes.cn/rss/outbrain.xml",
    },
    {
        "name": "People's Daily",
        "country": "china",
        "type": "state",
        "site": "en.people.cn",
        "method": "rss",
        "url": "http://en.people.cn/rss/World.xml",
    },
    # =========================================================================
    # RUSSIA — State Media (4 feeds)
    # =========================================================================
    {
        "name": "RT",
        "country": "russia",
        "type": "state",
        "site": "rt.com",
        "method": "rss",
        "url": "https://www.rt.com/rss/news/",
    },
    {
        "name": "TASS",
        "country": "russia",
        "type": "state",
        "site": "tass.com",
        "method": "rss",
        "url": "https://tass.com/rss/v2.xml",
    },
    {
        "name": "Sputnik",
        "country": "russia",
        "type": "state",
        "site": "sputnikglobe.com",
        "method": "rss",
        "url": "https://sputnikglobe.com/export/rss2/archive/index.xml",
    },
    {
        "name": "Interfax",
        "country": "russia",
        "type": "news",
        "site": "interfax.com",
        "method": "scrape",
        "ssl_verify": False,
        "scrape_url": "https://interfax.com/newsroom/top-stories/",
        "scrape_config": {
            "article_selector": "article, .an-item, .story, div.item, .io-article-list__item",
            "title_selector": "a h3, h3 a, a.title, a, h2 a",
            "link_attr": "href",
            "link_prefix": "https://interfax.com",
            "desc_selector": "p, .description, .lead",
        },
    },
    # =========================================================================
    # INDIA (6 feeds)
    # =========================================================================
    # FIX v1.2: WION 403 everywhere → stealth scraper
    {
        "name": "WION",
        "country": "india",
        "type": "news",
        "site": "wionews.com",
        "method": "scrape",
        "stealth": True,
        "scrape_url": "https://www.wionews.com/world",
        "scrape_config": {
            "article_selector": ".news-card, article, .story-card, .card-lg, div[class*='card']",
            "title_selector": "h2 a, h3 a, .title a, a.headline, a",
            "link_attr": "href",
            "link_prefix": "https://www.wionews.com",
            "desc_selector": "p, .summary, .excerpt",
        },
    },
    {
        "name": "The Hindu – Intl",
        "country": "india",
        "type": "news",
        "site": "thehindu.com",
        "method": "rss",
        "url": "https://www.thehindu.com/news/international/feeder/default.rss",
    },
    {
        "name": "NDTV World",
        "country": "india",
        "type": "news",
        "site": "ndtv.com",
        "method": "rss",
        "url": "https://feeds.feedburner.com/ndtvnews-world-news",
    },
    {
        "name": "Hindustan Times",
        "country": "india",
        "type": "news",
        "site": "hindustantimes.com",
        "method": "rss",
        "url": "https://www.hindustantimes.com/feeds/rss/world-news/rssfeed.xml",
    },
    {
        "name": "ThePrint",
        "country": "india",
        "type": "news",
        "site": "theprint.in",
        "method": "scrape",
        "scrape_url": "https://theprint.in/world/",
        "scrape_config": {
            "article_selector": "article, .td-module-container, .entry-title, .post-item",
            "title_selector": "h3 a, h2 a, .entry-title a, a",
            "link_attr": "href",
            "link_prefix": "",
            "desc_selector": ".td-excerpt, .entry-summary p, p",
        },
    },
    {
        "name": "ORF",
        "country": "india",
        "type": "thinktank",
        "site": "orfonline.org",
        "method": "scrape",
        "scrape_url": "https://www.orfonline.org/expert-speak",
        "scrape_config": {
            "article_selector": "article, .card, .post-item, div[class*='card']",
            "title_selector": "h3 a, h2 a, .title a, a",
            "link_attr": "href",
            "link_prefix": "https://www.orfonline.org",
            "desc_selector": "p, .excerpt, .summary",
        },
    },
    # =========================================================================
    # IRAN — State Media (4 feeds)
    # =========================================================================
    {
        "name": "Press TV",
        "country": "iran",
        "type": "state",
        "site": "presstv.co.uk",
        # presstv.ir redirige hoy a presstv.co.uk (dominio vigente) y presenta TLS roto;
        # la portada de co.uk usa <a href="/Detail/..."> que envuelve div[class*=title].
        "method": "scrape",
        "scrape_url": "https://www.presstv.co.uk/",
        "scrape_config": {
            "article_selector": "a[href*='/Detail/']",
            "title_selector": "div[class*='title']",
            "link_attr": "href",
            "link_prefix": "https://www.presstv.co.uk",
            "desc_selector": "",
        },
    },
    {
        "name": "Tehran Times",
        "country": "iran",
        "type": "state",
        "site": "tehrantimes.com",
        "method": "scrape",
        "scrape_url": "https://www.tehrantimes.com/",
        "scrape_config": {
            "article_selector": "article, .news-item, .item, .card, li",
            "title_selector": "h2 a, h3 a, h4 a, a.title, a",
            "link_attr": "href",
            "link_prefix": "https://www.tehrantimes.com",
            "desc_selector": "p, .lead, .summary, .desc",
        },
    },
    # FIX v1.2: IRNA better selectors + wider net
    {
        "name": "IRNA",
        "country": "iran",
        "type": "state",
        "site": "en.irna.ir",
        "method": "scrape",
        "scrape_url": "https://en.irna.ir/",
        "scrape_config": {
            "article_selector": "article, .news, .item, li, div[class*='news'], div[class*='item'], div[class*='story']",
            "title_selector": "h2 a, h3 a, h4 a, a.title, .title a, a",
            "link_attr": "href",
            "link_prefix": "https://en.irna.ir",
            "desc_selector": "p, .lead, .summary, .desc, .excerpt",
        },
    },
    {
        "name": "Iran Press",
        "country": "iran",
        "type": "state",
        "site": "iranpress.com",
        "method": "rss",
        "url": "https://iranpress.com/rss",
    },
]
