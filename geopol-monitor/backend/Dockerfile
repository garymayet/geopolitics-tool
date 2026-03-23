FROM python:3.12-slim

WORKDIR /app

# System deps for lxml
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libxml2-dev libxslt-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Data volume for SQLite
RUN mkdir -p /data

ENV GEOPOL_DB=/data/geopol.db
ENV FETCH_INTERVAL_MIN=15
ENV CLEANUP_DAYS=7
ENV FETCH_ON_START=1
ENV FLASK_PORT=5000

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--threads", "4", \
     "--timeout", "120", "--preload", "wsgi:app"]
