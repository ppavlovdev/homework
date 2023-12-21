# Dockerfile for django project with python 3.12-slim-bullseye

FROM python:3.12-slim-bullseye

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set working directory
WORKDIR /usr/src/app

COPY poetry.lock pyproject.toml /usr/src/app/
# Install poetry
RUN pip install poetry

# Install project dependencies
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev --no-interaction --no-ansi

# Copy project
COPY . .
RUN chmod +x /usr/src/app/entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]