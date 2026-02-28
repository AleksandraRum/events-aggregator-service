FROM python:3.11-slim

RUN addgroup --system --gid 1000 appuser && \
    adduser --system --uid 1000 --ingroup appuser --home /home/appuser appuser && \
    mkdir -p /home/appuser/.cache/uv && chown -R appuser:appuser /home/appuser
    
ENV HOME=/home/appuser

ENV UV_NO_CACHE=1

WORKDIR /app

RUN apt-get update && apt-get install gcc libpq-dev bash -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY requirements.txt /app/

RUN uv pip install --system -r requirements.txt

COPY --chown=appuser:appuser . /app

USER appuser

CMD ["bash", "./run.sh"]