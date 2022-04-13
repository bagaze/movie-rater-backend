FROM python:3.10-alpine

EXPOSE 9090

ARG YOUR_ENV=production

ENV YOUR_ENV=${YOUR_ENV} \
  PYTHONFAULTHANDLER=1 \
  PYTHONDONTWRITEBYTECODE=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_VERSION=1.1.13

RUN apk update \
  && apk add --no-cache build-base g++ postgresql postgresql-dev libc-dev linux-headers libffi-dev

# System deps:
RUN pip install "poetry==$POETRY_VERSION"

# Copy only requirements to cache them in docker layer
WORKDIR /app
COPY poetry.lock pyproject.toml /app/

# Copy environment information
COPY ./local-env ./.env
COPY ./alembic.ini ./alembic.ini

# Creating folders, and files for a project:
COPY ./app /app/app
COPY ./alembic /app/alembic

# Project initialization:
RUN poetry config virtualenvs.create false \
  && poetry install $(test "$YOUR_ENV" == production && echo "--no-dev") --no-interaction --no-ansi

# Launch the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "9090"]
