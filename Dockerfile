# syntax=docker/dockerfile:1.7
# Segmenta MCP Server — multi-stage build (x86_64 / arm64)
# Hosting canonico v1.5: Google Cloud Run (us-central1, linux/amd64)
# Portabile: stesso Dockerfile gira anche su Hetzner/Oracle/VPS Linux arm64

# ---- Stage 1: build dependencies con uv ----
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1

COPY --from=ghcr.io/astral-sh/uv:0.5 /uv /uvx /usr/local/bin/

WORKDIR /app

COPY pyproject.toml uv.lock* README.md ./

# Senza --mount=type=cache per compatibilità con Cloud Build (Docker classic, no BuildKit)
RUN uv sync --frozen --no-install-project --no-dev || \
    uv sync --no-install-project --no-dev

COPY src/ ./src/
COPY data/ ./data/

RUN uv sync --frozen --no-dev || uv sync --no-dev

# ---- Stage 2: runtime minimal ----
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

RUN groupadd -r segmenta && useradd -r -g segmenta -u 1001 segmenta

WORKDIR /app

COPY --from=builder --chown=segmenta:segmenta /app/.venv /app/.venv
COPY --from=builder --chown=segmenta:segmenta /app/src /app/src
COPY --from=builder --chown=segmenta:segmenta /app/data /app/data

USER segmenta

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:8000/health',timeout=5).status==200 else 1)"

CMD ["python", "-m", "uvicorn", "segmenta_mcp.main:app", \
     "--host", "0.0.0.0", "--port", "8000", \
     "--no-access-log", "--proxy-headers"]
