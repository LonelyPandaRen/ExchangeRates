FROM python:3.11-slim as requirements-stage

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=0 \
    POETRY_VERSION=1.7.1 \
    PATH="${PATH}:/root/.local/bin"

WORKDIR /tmp

RUN apt-get update && apt-get install -y curl && curl -sSL https://install.python-poetry.org | python3 -
COPY ./pyproject.toml ./poetry.lock* /tmp/
RUN set -xe \
    && poetry export  \
    -f requirements.txt  \
    --output requirements.txt \
    --only=main \
    --without-hashes  \
    --no-ansi  \
    --with-credentials

FROM python:3.11-slim as build-stage
ENV PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/code

WORKDIR /code

COPY --from=requirements-stage /tmp/requirements.txt /code/requirements.txt

RUN set -xe \
    && pip install --no-cache-dir -r requirements.txt \
    && rm -f requirements.txt

COPY ./exchange_rates /code/exchange_rates
COPY ./alembic.ini gunicorn.conf.py /code/

FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/code

WORKDIR /code

COPY --from=build-stage /usr/local /usr/local
COPY --from=build-stage /code /code

RUN set -xe \
    && useradd --uid 1000 --home-dir /code user \
    && chown -R 1000 /code

USER 1000
CMD ["gunicorn", "-c", "gunicorn.conf.py", "--bind=0.0.0.0:8000", "--workers=4", "--chdir=/code"]
