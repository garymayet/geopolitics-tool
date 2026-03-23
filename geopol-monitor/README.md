# 🌍 Geopolítica Monitor

Agregador open-source de noticias geopolíticas con motor dual: **RSS parser + HTML scraper** para sitios sin feeds funcionales.

Consolida en un solo dashboard los medios de comunicación principales de **USA, China, Rusia, India e Irán**, con enfoque en cobertura geopolítica y relaciones internacionales.

---

## Arquitectura

```
┌─────────────────────────────────────────────────────┐
│                    USUARIO :8080                     │
│              React SPA + Nginx reverse proxy         │
└──────────────────────┬──────────────────────────────┘
                       │ /api/*
┌──────────────────────▼──────────────────────────────┐
│                 BACKEND :5000                        │
│    Flask API + APScheduler (cada 15 min)             │
│                                                      │
│  ┌─────────────┐   ┌──────────────────┐              │
│  │  RSS Parser  │   │   HTML Scraper   │              │
│  │ (feedparser) │   │ (BeautifulSoup)  │              │
│  └──────┬──────┘   └───────┬──────────┘              │
│         │                  │                          │
│         └───────┬──────────┘                          │
│                 ▼                                     │
│          ┌────────────┐                               │
│          │   SQLite    │ ← /data/geopol.db            │
│          │  (WAL mode) │                               │
│          └────────────┘                               │
└─────────────────────────────────────────────────────┘
```

### Motor dual de ingesta

| Motor | Cuándo se usa | Tecnología |
|-------|--------------|------------|
| **RSS Parser** | El sitio tiene feed RSS/Atom funcional y actualizado | `feedparser` + `requests` |
| **HTML Scraper** | El sitio NO tiene RSS, o su feed está abandonado/roto | `BeautifulSoup` + selectores CSS configurables |

El scraper tiene dos estrategias:
1. **Selectores específicos**: usa `article_selector` + `title_selector` del config del feed
2. **Fallback heurístico**: si los selectores no encuentran nada, extrae todos los `<a>` con texto > 20 chars, excluyendo nav/footer

---

## Fuentes configuradas (31 feeds)

### 🇺🇸 USA (12)
| Fuente | Tipo | Motor |
|--------|------|-------|
| CNN World | Noticias | RSS |
| Foreign Policy | Análisis | RSS |
| Foreign Affairs | Análisis | **Scraper** |
| The National Interest | Análisis | RSS |
| War on the Rocks | Análisis | RSS |
| Brookings | Think Tank | RSS |
| CFR | Think Tank | **Scraper** |
| CSIS | Think Tank | RSS |
| Carnegie | Think Tank | RSS |
| GZERO Media | Análisis | RSS |
| Geopolitical Monitor | Análisis | RSS |
| The Diplomat | Análisis | RSS |

### 🇨🇳 China (5)
| Fuente | Tipo | Motor |
|--------|------|-------|
| CGTN | Estatal | RSS |
| Xinhua | Estatal | **Scraper** |
| China Daily | Estatal | RSS |
| Global Times | Estatal | RSS |
| People's Daily | Estatal | RSS |

### 🇷🇺 Rusia (4)
| Fuente | Tipo | Motor |
|--------|------|-------|
| RT | Estatal | RSS |
| TASS | Estatal | RSS |
| Sputnik | Estatal | RSS |
| Interfax | Noticias | **Scraper** |

### 🇮🇳 India (6)
| Fuente | Tipo | Motor |
|--------|------|-------|
| WION | Noticias | RSS |
| The Hindu – Intl | Noticias | RSS |
| NDTV World | Noticias | RSS |
| Hindustan Times | Noticias | RSS |
| ThePrint | Noticias | RSS |
| ORF | Think Tank | RSS |

### 🇮🇷 Irán (4)
| Fuente | Tipo | Motor |
|--------|------|-------|
| Press TV | Estatal | RSS |
| Tehran Times | Estatal | RSS |
| IRNA | Estatal | RSS |
| Iran Press | Estatal | RSS |

---

## Despliegue rápido (Docker)

### Prerrequisitos
- Docker Engine ≥ 20.10
- Docker Compose ≥ 2.0

### Levantar todo

```bash
git clone https://github.com/tu-usuario/geopol-monitor.git
cd geopol-monitor
cp .env.example .env   # ajustar si es necesario

docker compose up -d --build
```

El dashboard estará en **http://localhost:8080**
La API estará en **http://localhost:5000/api/**

### Verificar estado

```bash
# Health check
curl http://localhost:5000/api/health

# Ver estadísticas
curl http://localhost:5000/api/stats

# Ver artículos de China
curl "http://localhost:5000/api/articles?country=china&limit=10"
```

### Detener

```bash
docker compose down          # detener
docker compose down -v       # detener y borrar datos
```

---

## Desarrollo local (sin Docker)

### Backend

```bash
cd backend

# Crear virtualenv
python3 -m venv .venv
source .venv/bin/activate

# Instalar deps
pip install -r requirements.txt

# Configurar
export GEOPOL_DB=./geopol.db
export FETCH_INTERVAL_MIN=15
export FETCH_ON_START=1

# Ejecutar
python app.py
```

### Frontend

```bash
cd frontend
npm install
npm run dev    # → http://localhost:3000  (proxy a :5000)
```

---

## API Reference

### `GET /api/articles`

| Param | Tipo | Default | Descripción |
|-------|------|---------|-------------|
| `country` | string | `all` | `usa`, `china`, `russia`, `india`, `iran`, `all` |
| `type` | string | `all` | `news`, `state`, `analysis`, `thinktank`, `all` |
| `source` | string | — | Nombre exacto de la fuente |
| `q` | string | — | Búsqueda en título, descripción, fuente |
| `limit` | int | 200 | Máximo 500 |
| `offset` | int | 0 | Para paginación |
| `hours` | int | — | Solo artículos de las últimas N horas |

**Response:**
```json
{
  "articles": [...],
  "total": 1234,
  "limit": 200,
  "offset": 0
}
```

### `GET /api/feeds`

Devuelve el estado de todos los feeds configurados (último fetch, status, conteo, errores).

### `GET /api/stats`

Estadísticas generales: total de artículos, por país, por tipo, último ciclo de fetch.

### `POST /api/fetch`

Dispara un fetch manual de todos los feeds (o filtrado por país). Body opcional:
```json
{ "country": "china" }
```

### `POST /api/fetch/<feed_name>`

Refresca un solo feed por nombre.

### `GET /api/health`

Health check para Docker/monitoreo.

---

## Configuración

### Variables de entorno

| Variable | Default | Descripción |
|----------|---------|-------------|
| `GEOPOL_DB` | `/data/geopol.db` | Ruta de la base SQLite |
| `FETCH_INTERVAL_MIN` | `15` | Intervalo de fetch automático (minutos) |
| `CLEANUP_DAYS` | `7` | Días de retención de artículos |
| `FETCH_ON_START` | `1` | Si `1`, fetch inmediato al arrancar |
| `FLASK_PORT` | `5000` | Puerto del backend |
| `VITE_API_URL` | — | Override de URL de API para el frontend |

---

## Agregar un nuevo feed

### Feed RSS

Editar `backend/feeds.py` y agregar:

```python
{
    "name": "Al Jazeera English",
    "country": "qatar",  # agregar país a COUNTRIES del frontend
    "type": "news",
    "site": "aljazeera.com",
    "method": "rss",
    "url": "https://www.aljazeera.com/xml/rss/all.xml",
},
```

### Feed por Scraper (sin RSS)

```python
{
    "name": "Chatham House",
    "country": "uk",
    "type": "thinktank",
    "site": "chathamhouse.org",
    "method": "scrape",
    "scrape_url": "https://www.chathamhouse.org/publications",
    "scrape_config": {
        "article_selector": "article, .node--type-publication",
        "title_selector": "h3 a, h2 a, .field--name-title a",
        "link_attr": "href",
        "link_prefix": "https://www.chathamhouse.org",
        "desc_selector": ".field--name-body p, .teaser__text",
    },
},
```

### Cómo encontrar los selectores CSS

1. Abrir el sitio en el navegador
2. Click derecho → Inspeccionar en un titular
3. Identificar el patrón:
   - ¿Qué elemento contiene cada artículo? → `article_selector`
   - ¿Dónde está el `<a>` con el título? → `title_selector`
   - ¿Los links son absolutos o relativos? → `link_prefix`
   - ¿Hay un elemento con resumen? → `desc_selector`
4. Probar con: `POST /api/fetch/NombreDelFeed`

---

## Notas sobre los medios

> ⚠ **Descargo de responsabilidad epistémico**

Los medios estatales de China (CGTN, Xinhua, Global Times, People's Daily, China Daily),
Rusia (RT, TASS, Sputnik) e Irán (Press TV, Tehran Times, IRNA, Iran Press) representan
directamente las posiciones de sus respectivos gobiernos. Su inclusión en este agregador
tiene como propósito entender las narrativas geopolíticas desde múltiples polos, **no**
validar su contenido como periodismo independiente.

Los medios estadounidenses, aunque más diversos e independientes del gobierno, también
operan dentro de marcos interpretativos particulares (establishment liberal, neoconservador,
realista, etc.).

Los medios indios incluyen tanto prensa relativamente independiente como medios con
alineamientos políticos más marcados.

**Recomendación**: Triangular siempre entre fuentes de múltiples países y tipos antes
de formar conclusiones sobre cualquier evento geopolítico.

---

## Troubleshooting

### Feeds que fallan constantemente

| Causa | Síntoma | Solución |
|-------|---------|----------|
| Geobloqueo | HTTP 403/451 desde ciertos países | Usar VPN o proxy en el servidor |
| SSL/TLS | `SSLError` | Actualizar `certifi`: `pip install --upgrade certifi` |
| Scraper roto | 0 artículos pero sin error HTTP | Actualizar `scrape_config` selectores CSS |
| Rate limiting | HTTP 429 | Aumentar `FETCH_INTERVAL_MIN` |
| Feed muerto | Feed parsea OK pero 0 items | Cambiar a `method: "scrape"` |

### Base de datos

```bash
# Acceder a la DB
docker compose exec backend sqlite3 /data/geopol.db

# Ver artículos recientes
SELECT source_name, title, pub_date FROM articles ORDER BY pub_date DESC LIMIT 20;

# Conteo por fuente
SELECT source_name, COUNT(*) FROM articles GROUP BY source_name ORDER BY COUNT(*) DESC;

# Limpiar todo
DELETE FROM articles;
DELETE FROM feed_status;
DELETE FROM fetch_log;
```

---

## Stack técnico

| Componente | Tecnología |
|------------|------------|
| Backend | Python 3.12, Flask, feedparser, BeautifulSoup4, APScheduler |
| Frontend | React 18, Vite 5 |
| Base de datos | SQLite (WAL mode) |
| Servidor web | Nginx (frontend) + Gunicorn (backend) |
| Contenedores | Docker + Docker Compose |

---

## Licencia

MIT — Uso libre, incluyendo comercial. Sin garantías.
