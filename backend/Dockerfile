# syntax = docker/dockerfile:1.2
# Stage 1
FROM ghcr.io/dmfigol/base/python:3.8-slim as builder

WORKDIR /app

COPY pyproject.toml .
COPY poetry.lock .

RUN --mount=type=cache,target=/root/.cache \
    python -m venv .venv \
 && poetry install --no-dev --no-root

COPY netwarden netwarden

# Non-editable installation of the project
RUN poetry build -f wheel \
 && .venv/bin/pip install --no-deps dist/*.whl \
 && rm -rf dist/

# Stage 2
FROM python:3.8-slim

WORKDIR /app
COPY --from=builder /app/.venv /app/.venv

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

CMD ["uvicorn", "netwarden.app:app", "--host", "0.0.0.0", "--port", "5000"]
EXPOSE 5000