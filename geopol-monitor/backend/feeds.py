"""
Feed definitions for Geopolítica Monitor.

Each feed has:
  - name: Display name
  - country: usa | china | russia | india | iran
  - type: news | state | analysis | thinktank
  - site: Base domain for display
  - method: "rss" or "scrape"
  - url: RSS feed URL (if method=rss)
  - scrape_url: Page to scrape (if method=scrape)
  - scrape_config: CSS selectors for scraping (if method=scrape)
"""

FEEDS = [
    # =========================================================================
    # USA — News & Analysis
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
        "method": "scrape",
        "scrape_url": "https://www.foreignaffairs.com/latest",
        "scrape_config": {
            "article_selector": "article, .article-card, .media-object",
            "title_selector": "h2 a, h3 a, .title a, .headline a",
            "link_attr": "href",
            "link_prefix": "https://www.foreignaffairs.com",
            "desc_selector": ".dek, .summary, .subtitle, p",
        },
    },
    {
        "name": "The National Interest",
        "country": "usa",
        "type": "analysis",
        "site": "nationalinterest.org",
        "method": "rss",
        "url": "https://nationalinterest.org/feed",
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
        "method": "rss",
        "url": "https://www.brookings.edu/feed/",
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
    {
        "name": "CSIS",
        "country": "usa",
        "type": "thinktank",
        "site": "csis.org",
        "method": "rss",
        "url": "https://www.csis.org/analysis/feed",
    },
    {
        "name": "Carnegie",
        "country": "usa",
        "type": "thinktank",
        "site": "carnegieendowment.org",
        "method": "rss",
        "url": "https://carnegieendowment.org/feeds/posts",
    },
    {
        "name": "GZERO Media",
        "country": "usa",
        "type": "analysis",
        "site": "gzeromedia.com",
        "method": "rss",
        "url": "https://www.gzeromedia.com/feed",
    },
    {
        "name": "Geopolitical Monitor",
        "country": "usa",
        "type": "analysis",
        "site": "geopoliticalmonitor.com",
        "method": "rss",
        "url": "https://www.geopoliticalmonitor.com/feed/",
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
    # CHINA — State Media
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
    # RUSSIA — State Media
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
        "scrape_url": "https://interfax.com/newsroom/top-stories/",
        "scrape_config": {
            "article_selector": "article, .an-item, .story, div.item",
            "title_selector": "a h3, h3 a, a.title, a",
            "link_attr": "href",
            "link_prefix": "https://interfax.com",
            "desc_selector": "p, .description, .lead",
        },
    },
    # =========================================================================
    # INDIA
    # =========================================================================
    {
        "name": "WION",
        "country": "india",
        "type": "news",
        "site": "wionews.com",
        "method": "rss",
        "url": "https://www.wionews.com/feeds/world/rss.xml",
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
        "method": "rss",
        "url": "https://theprint.in/feed/",
    },
    {
        "name": "ORF",
        "country": "india",
        "type": "thinktank",
        "site": "orfonline.org",
        "method": "rss",
        "url": "https://www.orfonline.org/feed",
    },
    # =========================================================================
    # IRAN — State Media
    # =========================================================================
    {
        "name": "Press TV",
        "country": "iran",
        "type": "state",
        "site": "presstv.ir",
        "method": "rss",
        "url": "https://www.presstv.ir/RSS",
    },
    {
        "name": "Tehran Times",
        "country": "iran",
        "type": "state",
        "site": "tehrantimes.com",
        "method": "rss",
        "url": "https://www.tehrantimes.com/rss",
    },
    {
        "name": "IRNA",
        "country": "iran",
        "type": "state",
        "site": "en.irna.ir",
        "method": "rss",
        "url": "https://en.irna.ir/rss",
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
