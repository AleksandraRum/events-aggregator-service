FROM python:3.11-slim

RUN addgroup --system --gid 1000 appuser && \
    adduser --system --uid 1000 --ingroup appuser appuser

WORKDIR /app

RUN apt-get update && apt-get install gcc libpq-dev bash -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=appuser:appuser . /app

USER appuser

CMD ["bash", "./run.sh"]