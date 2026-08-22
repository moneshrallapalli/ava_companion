FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    build-essential \
    g++ \
    && rm -rf /var/lib/apt/lists/*

COPY uv.lock pyproject.toml README.md /app/
RUN uv sync --frozen --no-cache

COPY src/ /app/

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

RUN uv pip install -e .

VOLUME ["/app/data"]

EXPOSE 8080

CMD ["/app/.venv/bin/fastapi", "run", "ai_companion/interfaces/whatsapp/webhook_endpoint.py", "--port", "8080", "--host", "0.0.0.0"]
