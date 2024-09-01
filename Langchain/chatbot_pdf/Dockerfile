# syntax=docker/dockerfile:1

# Comments are provided throughout this file to help you get started.
# If you need more help, visit the Dockerfile reference guide at
# https://docs.docker.com/go/dockerfile-reference/

# Want to help us make this template better? Share your feedback here: https://forms.gle/ybq9Krt8jtBL3iCk7


FROM python:3.12.5-bookworm AS base
WORKDIR /app

RUN apt-get update && apt-get install -y build-essential

RUN python -m pip install poetry

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

# Copy the source code into the container.
COPY . ./

RUN poetry install --no-root && rm -rf $POETRY_CACHE_DIR

ENTRYPOINT ["poetry", "run"]

# Expose the port that the application listens on.
EXPOSE 8501

