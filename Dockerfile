FROM python:3.12-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl && \
    rm -rf /var/lib/apt/lists/*

RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

WORKDIR /app

COPY pyproject.toml uv.lock .python-version ./

RUN uv sync --frozen --no-dev

COPY app/ app/
COPY data/ data/
COPY scripts/ scripts/
COPY static/ static/

ARG OPENROUTER_API_KEY
ENV OPENROUTER_API_KEY=${OPENROUTER_API_KEY}

RUN mkdir -p app/data && \
    uv run python -m app.db.init_db && \
    uv run python -m app.rag.ingest

# ---- runtime ----
FROM python:3.12-slim

RUN groupadd -r app && useradd -r -g app -d /app app

WORKDIR /app

COPY --from=builder /app/.venv .venv
COPY --from=builder /root/.local /root/.local
ENV PATH="/app/.venv/bin:/root/.local/bin:${PATH}" \
    VIRTUAL_ENV="/app/.venv"

COPY --from=builder /app/app /app/app
COPY --from=builder /app/static /app/static
COPY --from=builder /app/data /app/data
COPY --from=builder /app/scripts /app/scripts

RUN chown -R app:app /app

USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"]

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
