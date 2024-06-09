FROM python:3.12-slim as base

ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN pip install poetry && \
    poetry config virtualenvs.create false

WORKDIR /app
COPY src ./src/
COPY poetry.lock pyproject.toml ./

EXPOSE 8000

# Develop
FROM base as development

COPY --from=base / /
ENV PYTHONASYNCIODEBUG 1

RUN poetry install --extras production --no-root --no-interaction --no-ansi

ENTRYPOINT ["uvicorn"]
CMD ["--host", "0.0.0.0", "--port", "8000", "--reload", "src.entrypoints.api:app"]

# Production
FROM base as production
COPY --from=base / /

RUN poetry install --extras production --no-dev --no-root --no-interaction --no-ansi

ENTRYPOINT ["uvicorn"]
CMD ["--host", "0.0.0.0", "--port", "8000", "--log-level", "warning", "--workers", "1", "--proxy-headers", "src.entrypoints.api:app"]
