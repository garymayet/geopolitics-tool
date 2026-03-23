import { useState, useEffect, useCallback, useRef } from "react";

/* ── Config ─────────────────────────────────────────────────────────────── */

const API =
  import.meta.env.VITE_API_URL ||
  (window.location.port === "3000" ? "http://localhost:5000" : "");

const COUNTRIES = [
  { id: "all",     label: "Global Feed",  icon: "🌐", color: "#94A3B8" },
  { id: "usa",     label: "USA",          icon: "🇺🇸", color: "#60A5FA" },
  { id: "china",   label: "China",        icon: "🇨🇳", color: "#F87171" },
  { id: "russia",  label: "Rusia",        icon: "🇷🇺", color: "#FBBF24" },
  { id: "india",   label: "India",        icon: "🇮🇳", color: "#FB923C" },
  { id: "iran",    label: "Irán",         icon: "🇮🇷", color: "#34D399" },
];

const TYPES = [
  { id: "all",       label: "Todo" },
  { id: "news",      label: "Noticias" },
  { id: "state",     label: "Estatal" },
  { id: "analysis",  label: "Análisis" },
  { id: "thinktank", label: "Think Tank" },
];

/* ── Helpers ─────────────────────────────────────────────────────────────── */

function timeAgo(dateStr) {
  if (!dateStr) return "";
  const d = new Date(dateStr);
  if (isNaN(d.getTime())) return "";
  const sec = (Date.now() - d.getTime()) / 1000;
  if (sec < 0) return "ahora";
  if (sec < 3600) return `${Math.max(1, Math.floor(sec / 60))}m`;
  if (sec < 86400) return `${Math.floor(sec / 3600)}h`;
  if (sec < 604800) return `${Math.floor(sec / 86400)}d`;
  return d.toLocaleDateString("es-MX", { day: "numeric", month: "short" });
}

async function api(path, opts = {}) {
  const res = await fetch(`${API}${path}`, opts);
  if (!res.ok) throw new Error(`API ${res.status}`);
  return res.json();
}

/* ── Styles (CSS-in-JS object) ───────────────────────────────────────────── */

const S = {
  root: {
    minHeight: "100vh",
    background: "#0B0F1A",
    color: "#E2E8F0",
    fontFamily: "'IBM Plex Sans', -apple-system, sans-serif",
  },
  header: {
    borderBottom: "1px solid rgba(255,255,255,0.06)",
    padding: "14px 24px",
    background: "rgba(11,15,26,0.97)",
    backdropFilter: "blur(16px)",
    position: "sticky",
    top: 0,
    zIndex: 100,
  },
  mono: { fontFamily: "'IBM Plex Mono', monospace" },
  serif: { fontFamily: "'Crimson Pro', Georgia, serif" },
};

/* ── Components ──────────────────────────────────────────────────────────── */

function TypeBadge({ type }) {
  const map = {
    state:     { l: "Estatal",    bg: "rgba(239,68,68,0.15)",  c: "#FCA5A5" },
    news:      { l: "Noticias",   bg: "rgba(96,165,250,0.15)", c: "#93C5FD" },
    analysis:  { l: "Análisis",   bg: "rgba(167,139,250,0.15)",c: "#C4B5FD" },
    thinktank: { l: "Think Tank", bg: "rgba(52,211,153,0.15)", c: "#6EE7B7" },
  };
  const s = map[type] || map.news;
  return (
    <span
      style={{
        fontSize: 10, padding: "2px 8px", borderRadius: 4,
        background: s.bg, color: s.c, fontWeight: 600,
        letterSpacing: "0.04em", textTransform: "uppercase",
        whiteSpace: "nowrap",
      }}
    >
      {s.l}
    </span>
  );
}

function MethodBadge({ method }) {
  if (method === "rss") return null;
  return (
    <span
      style={{
        fontSize: 9, padding: "1px 5px", borderRadius: 3,
        background: "rgba(251,191,36,0.12)", color: "#FCD34D",
        fontWeight: 600, letterSpacing: "0.05em", textTransform: "uppercase",
        ...S.mono,
      }}
    >
      SCRAPE
    </span>
  );
}

function ArticleCard({ article }) {
  const cc = COUNTRIES.find((c) => c.id === article.country)?.color || "#94A3B8";
  const [hovered, setHovered] = useState(false);

  return (
    <a
      href={article.link}
      target="_blank"
      rel="noopener noreferrer"
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      style={{
        display: "block",
        background: hovered ? "rgba(255,255,255,0.05)" : "rgba(255,255,255,0.02)",
        border: `1px solid ${hovered ? "rgba(255,255,255,0.1)" : "rgba(255,255,255,0.04)"}`,
        borderLeft: `3px solid ${cc}`,
        borderRadius: 8,
        padding: "14px 18px",
        textDecoration: "none",
        transition: "all 0.15s ease",
        transform: hovered ? "translateX(2px)" : "none",
      }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 7, flexWrap: "wrap" }}>
        <span style={{ fontSize: 11, color: cc, fontWeight: 700, ...S.mono }}>
          {article.source_name}
        </span>
        <TypeBadge type={article.source_type} />
        <MethodBadge method={article.method} />
        <span style={{ fontSize: 11, color: "#475569", marginLeft: "auto", ...S.mono }}>
          {timeAgo(article.pub_date)}
        </span>
      </div>
      <h3 style={{ fontSize: 15, fontWeight: 600, color: "#E2E8F0", lineHeight: 1.4, margin: "0 0 5px", ...S.serif }}>
        {article.title}
      </h3>
      {article.description && (
        <p style={{ fontSize: 13, color: "#94A3B8", lineHeight: 1.5, margin: 0 }}>
          {article.description.length > 220
            ? article.description.slice(0, 220) + "…"
            : article.description}
        </p>
      )}
    </a>
  );
}

function FeedStatusPanel({ feeds, onRefreshFeed }) {
  if (!feeds.length)
    return <p style={{ color: "#475569", fontSize: 13, padding: 20 }}>Cargando estado de feeds…</p>;

  const grouped = {};
  for (const f of feeds) {
    if (!grouped[f.country]) grouped[f.country] = [];
    grouped[f.country].push(f);
  }

  return (
    <div
      style={{
        background: "rgba(15,23,42,0.97)",
        borderBottom: "1px solid rgba(255,255,255,0.06)",
        padding: "20px 24px",
        maxHeight: 420,
        overflowY: "auto",
      }}
    >
      <h3 style={{ fontSize: 13, fontWeight: 600, marginBottom: 16, color: "#64748B", ...S.mono }}>
        ESTADO DE FUENTES — RSS + SCRAPERS
      </h3>
      {Object.entries(grouped).map(([country, list]) => {
        const cc = COUNTRIES.find((c) => c.id === country);
        return (
          <div key={country} style={{ marginBottom: 16 }}>
            <div style={{ fontSize: 12, fontWeight: 600, color: cc?.color || "#94A3B8", marginBottom: 6 }}>
              {cc?.icon} {cc?.label || country}
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))", gap: 6 }}>
              {list.map((fs) => (
                <div
                  key={fs.feed_name}
                  style={{
                    display: "flex", alignItems: "center", gap: 8,
                    padding: "6px 10px", borderRadius: 6,
                    background: "rgba(255,255,255,0.02)",
                    border: "1px solid rgba(255,255,255,0.04)",
                    fontSize: 12,
                  }}
                >
                  <span
                    style={{
                      width: 7, height: 7, borderRadius: "50%", flexShrink: 0,
                      background:
                        fs.last_status === "ok" ? "#34D399" :
                        fs.last_status === "error" ? "#F87171" : "#FBBF24",
                    }}
                  />
                  <span style={{ color: "#CBD5E1", flex: 1 }}>{fs.feed_name}</span>
                  <span
                    style={{
                      fontSize: 9, padding: "1px 5px", borderRadius: 3,
                      background: fs.method === "scrape"
                        ? "rgba(251,191,36,0.1)" : "rgba(99,102,241,0.1)",
                      color: fs.method === "scrape" ? "#FCD34D" : "#A5B4FC",
                      fontWeight: 600, textTransform: "uppercase", ...S.mono,
                    }}
                  >
                    {fs.method}
                  </span>
                  <span style={{ color: "#475569", ...S.mono, fontSize: 11 }}>
                    {fs.last_status === "ok" ? fs.article_count : fs.last_status === "error" ? "✕" : "…"}
                  </span>
                  <button
                    onClick={(e) => { e.stopPropagation(); onRefreshFeed(fs.feed_name); }}
                    style={{
                      background: "rgba(255,255,255,0.05)", border: "none",
                      color: "#64748B", cursor: "pointer", borderRadius: 4,
                      padding: "2px 6px", fontSize: 11,
                    }}
                    title={`Refrescar ${fs.feed_name}`}
                  >
                    ↻
                  </button>
                </div>
              ))}
            </div>
          </div>
        );
      })}
      <p style={{ fontSize: 11, color: "#475569", marginTop: 12, fontStyle: "italic" }}>
        ⚠ Los feeds con error pueden deberse a geobloqueo, CORS, o caídas temporales del sitio.
        Los scrapers (SCRAPE) se usan para sitios sin RSS funcional.
      </p>
    </div>
  );
}

function StatsBar({ stats }) {
  if (!stats) return null;
  return (
    <div
      style={{
        display: "flex", gap: 16, alignItems: "center",
        padding: "10px 24px",
        borderBottom: "1px solid rgba(255,255,255,0.04)",
        overflowX: "auto",
      }}
    >
      {COUNTRIES.filter((c) => c.id !== "all").map((c) => (
        <div key={c.id} style={{ display: "flex", alignItems: "center", gap: 5, whiteSpace: "nowrap" }}>
          <span style={{ fontSize: 13 }}>{c.icon}</span>
          <span style={{ fontSize: 20, fontWeight: 700, color: c.color, ...S.serif }}>
            {stats.by_country?.[c.id] || 0}
          </span>
        </div>
      ))}
      <div style={{ marginLeft: "auto", ...S.mono, fontSize: 11, color: "#475569" }}>
        {stats.last_fetch
          ? `Último ciclo: ${stats.last_fetch.feeds_ok}/${stats.last_fetch.feeds_total} OK · ${stats.last_fetch.articles_new} nuevos · ${stats.last_fetch.duration_sec}s`
          : "Sin datos de ciclo"}
      </div>
    </div>
  );
}

function Spinner() {
  return (
    <div style={{ textAlign: "center", padding: 60 }}>
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
      <div
        style={{
          width: 40, height: 40, margin: "0 auto 14px",
          border: "3px solid rgba(99,102,241,0.15)",
          borderTopColor: "#6366F1", borderRadius: "50%",
          animation: "spin 0.8s linear infinite",
        }}
      />
      <p style={{ color: "#64748B", fontSize: 14 }}>Cargando artículos…</p>
    </div>
  );
}

/* ── App ─────────────────────────────────────────────────────────────────── */

export default function App() {
  const [country, setCountry] = useState("all");
  const [type, setType] = useState("all");
  const [search, setSearch] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [articles, setArticles] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [feedStatuses, setFeedStatuses] = useState([]);
  const [stats, setStats] = useState(null);
  const [showSources, setShowSources] = useState(false);
  const [fetchingAll, setFetchingAll] = useState(false);
  const [page, setPage] = useState(0);

  const LIMIT = 60;
  const searchTimer = useRef(null);

  // Debounce search
  useEffect(() => {
    clearTimeout(searchTimer.current);
    searchTimer.current = setTimeout(() => setDebouncedSearch(search), 350);
    return () => clearTimeout(searchTimer.current);
  }, [search]);

  // Fetch articles
  const loadArticles = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        country,
        type,
        limit: String(LIMIT),
        offset: String(page * LIMIT),
      });
      if (debouncedSearch) params.set("q", debouncedSearch);

      const data = await api(`/api/articles?${params}`);
      setArticles(data.articles || []);
      setTotal(data.total || 0);
    } catch (e) {
      console.error("Failed to load articles:", e);
    }
    setLoading(false);
  }, [country, type, debouncedSearch, page]);

  useEffect(() => { loadArticles(); }, [loadArticles]);

  // Periodic refresh
  useEffect(() => {
    const interval = setInterval(loadArticles, 60_000);
    return () => clearInterval(interval);
  }, [loadArticles]);

  // Load feed statuses & stats
  useEffect(() => {
    const load = async () => {
      try {
        const [feedData, statsData] = await Promise.all([
          api("/api/feeds"),
          api("/api/stats"),
        ]);
        setFeedStatuses(feedData.feeds || []);
        setStats(statsData);
      } catch (e) {
        console.error("Failed to load metadata:", e);
      }
    };
    load();
    const interval = setInterval(load, 30_000);
    return () => clearInterval(interval);
  }, []);

  // Manual fetch all
  const triggerFetchAll = async () => {
    setFetchingAll(true);
    try {
      await api("/api/fetch", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ country }),
      });
      setTimeout(loadArticles, 5000);
    } catch (e) {
      console.error("Fetch trigger failed:", e);
    }
    setTimeout(() => setFetchingAll(false), 8000);
  };

  // Refresh single feed
  const refreshFeed = async (feedName) => {
    try {
      await api(`/api/fetch/${encodeURIComponent(feedName)}`, { method: "POST" });
      setTimeout(loadArticles, 2000);
    } catch (e) {
      console.error(`Refresh ${feedName} failed:`, e);
    }
  };

  // Reset page on filter change
  useEffect(() => { setPage(0); }, [country, type, debouncedSearch]);

  const totalPages = Math.ceil(total / LIMIT);

  return (
    <div style={S.root}>
      {/* ── Header ──────────────────────────────────────────────────────── */}
      <header style={S.header}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: 12 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <div
              style={{
                width: 38, height: 38, borderRadius: 8,
                background: "linear-gradient(135deg, #3B82F6 0%, #8B5CF6 100%)",
                display: "flex", alignItems: "center", justifyContent: "center",
                fontSize: 20, boxShadow: "0 0 20px rgba(99,102,241,0.3)",
              }}
            >
              🌍
            </div>
            <div>
              <h1 style={{ fontSize: 19, fontWeight: 800, margin: 0, letterSpacing: "-0.03em", ...S.serif }}>
                GEOPOLÍTICA MONITOR
              </h1>
              <p style={{ fontSize: 11, color: "#4B5563", margin: 0, ...S.mono }}>
                RSS + Scrapers · {stats?.total_articles ?? "…"} artículos
              </p>
            </div>
          </div>

          <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
            <button
              onClick={triggerFetchAll}
              disabled={fetchingAll}
              style={{
                background: fetchingAll ? "rgba(99,102,241,0.15)" : "rgba(99,102,241,0.1)",
                border: "1px solid rgba(99,102,241,0.2)",
                color: fetchingAll ? "#818CF8" : "#A5B4FC",
                padding: "7px 14px", borderRadius: 6, fontSize: 12,
                cursor: fetchingAll ? "wait" : "pointer", ...S.mono,
              }}
            >
              {fetchingAll ? "⟳ Descargando…" : "⟳ Actualizar"}
            </button>
            <button
              onClick={() => setShowSources(!showSources)}
              style={{
                background: showSources ? "rgba(99,102,241,0.2)" : "rgba(255,255,255,0.04)",
                border: "1px solid rgba(255,255,255,0.08)",
                color: showSources ? "#A5B4FC" : "#94A3B8",
                padding: "7px 14px", borderRadius: 6, fontSize: 12,
                cursor: "pointer", ...S.mono,
              }}
            >
              {showSources ? "✕ Cerrar" : "◉ Fuentes"}
            </button>
          </div>
        </div>

        {/* Country Tabs */}
        <div style={{ display: "flex", gap: 3, marginTop: 14, overflowX: "auto", paddingBottom: 2 }}>
          {COUNTRIES.map((c) => {
            const cnt = c.id === "all" ? total : (stats?.by_country?.[c.id] ?? "");
            return (
              <button
                key={c.id}
                onClick={() => setCountry(c.id)}
                style={{
                  display: "flex", alignItems: "center", gap: 6,
                  padding: "7px 14px", borderRadius: 6, border: "none",
                  fontSize: 13, cursor: "pointer", whiteSpace: "nowrap",
                  fontWeight: country === c.id ? 600 : 400,
                  background: country === c.id ? `${c.color}22` : "transparent",
                  color: country === c.id ? c.color : "#4B5563",
                  transition: "all 0.15s",
                }}
              >
                <span>{c.icon}</span> {c.label}
                {cnt !== "" && <span style={{ fontSize: 11, opacity: 0.6 }}>{cnt}</span>}
              </button>
            );
          })}
        </div>

        {/* Search + Type Filter */}
        <div style={{ display: "flex", gap: 8, marginTop: 10, flexWrap: "wrap" }}>
          <div style={{ position: "relative", flex: 1, minWidth: 200 }}>
            <span style={{ position: "absolute", left: 10, top: "50%", transform: "translateY(-50%)", color: "#475569", fontSize: 14 }}>⌕</span>
            <input
              type="text"
              placeholder="Buscar artículos, fuentes…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              style={{
                width: "100%", padding: "8px 12px 8px 30px",
                background: "rgba(255,255,255,0.04)",
                border: "1px solid rgba(255,255,255,0.08)",
                borderRadius: 6, color: "#E2E8F0", fontSize: 13,
                outline: "none", boxSizing: "border-box",
              }}
            />
          </div>
          <div style={{ display: "flex", gap: 4 }}>
            {TYPES.map((t) => (
              <button
                key={t.id}
                onClick={() => setType(t.id)}
                style={{
                  padding: "6px 12px", borderRadius: 6, border: "none",
                  fontSize: 12, cursor: "pointer",
                  background: type === t.id ? "rgba(99,102,241,0.2)" : "rgba(255,255,255,0.04)",
                  color: type === t.id ? "#A5B4FC" : "#64748B",
                  fontWeight: type === t.id ? 600 : 400,
                }}
              >
                {t.label}
              </button>
            ))}
          </div>
        </div>
      </header>

      {/* ── Sources Panel ───────────────────────────────────────────────── */}
      {showSources && (
        <FeedStatusPanel feeds={feedStatuses} onRefreshFeed={refreshFeed} />
      )}

      {/* ── Stats Bar ───────────────────────────────────────────────────── */}
      <StatsBar stats={stats} />

      {/* ── Articles ────────────────────────────────────────────────────── */}
      <main style={{ padding: "20px 24px", maxWidth: 1200, margin: "0 auto" }}>
        {loading ? (
          <Spinner />
        ) : articles.length === 0 ? (
          <div style={{ textAlign: "center", padding: 60, color: "#475569" }}>
            <p style={{ fontSize: 40, marginBottom: 8 }}>∅</p>
            <p style={{ fontSize: 14 }}>
              {total === 0
                ? "No hay artículos aún. Presiona ⟳ Actualizar para descargar feeds."
                : "Sin resultados para esta búsqueda/filtro."}
            </p>
          </div>
        ) : (
          <>
            <div
              style={{
                display: "flex", justifyContent: "space-between", alignItems: "center",
                marginBottom: 14, paddingBottom: 10,
                borderBottom: "1px solid rgba(255,255,255,0.04)",
              }}
            >
              <span style={{ fontSize: 12, color: "#475569", ...S.mono }}>
                {total} artículos · página {page + 1}/{totalPages || 1}
              </span>
              <div style={{ display: "flex", gap: 6 }}>
                <button
                  onClick={() => setPage(Math.max(0, page - 1))}
                  disabled={page === 0}
                  style={{
                    padding: "4px 10px", borderRadius: 4, border: "none",
                    background: "rgba(255,255,255,0.04)", color: page === 0 ? "#333" : "#94A3B8",
                    cursor: page === 0 ? "default" : "pointer", fontSize: 12,
                  }}
                >
                  ← Anterior
                </button>
                <button
                  onClick={() => setPage(page + 1)}
                  disabled={page + 1 >= totalPages}
                  style={{
                    padding: "4px 10px", borderRadius: 4, border: "none",
                    background: "rgba(255,255,255,0.04)",
                    color: page + 1 >= totalPages ? "#333" : "#94A3B8",
                    cursor: page + 1 >= totalPages ? "default" : "pointer", fontSize: 12,
                  }}
                >
                  Siguiente →
                </button>
              </div>
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
              {articles.map((a, i) => (
                <ArticleCard key={`${a.source_name}-${a.id || i}`} article={a} />
              ))}
            </div>
          </>
        )}
      </main>

      {/* ── Footer ──────────────────────────────────────────────────────── */}
      <footer
        style={{
          borderTop: "1px solid rgba(255,255,255,0.04)",
          padding: "18px 24px", textAlign: "center",
          color: "#1E293B", fontSize: 11, lineHeight: 1.6, ...S.mono,
        }}
      >
        GEOPOLÍTICA MONITOR v1.0 · Open-source RSS + Scraping aggregator
        <br />
        Los medios estatales (China, Rusia, Irán) representan posiciones oficiales · Lectura crítica recomendada
      </footer>
    </div>
  );
}
