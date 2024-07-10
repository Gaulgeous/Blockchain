# syntax=docker/dockerfile:1

# Comments are provided throughout this file to help you get started.
# If you need more help, visit the Dockerfile reference guide at
# https://docs.docker.com/go/dockerfile-reference/

# Want to help us make this template better? Share your feedback here: https://forms.gle/ybq9Krt8jtBL3iCk7

ARG PYTHON_VERSION=3.12.4
FROM python:${PYTHON_VERSION} AS builder

# Install poetry
RUN pip install poetry

# Prevents Python from writing pyc files.
# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
# Create a virtual environment within the container (Not strictly necessary, but is super safe)
# Prevent poetry from interacting outside environment, and create a temporary cache to delete after running 
# As per multi-stage building recommendations
ENV PYTHONDONTWRITEBYTECODE=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache \ 
    PYTHONUNBUFFERED=1

# Change to working directory
WORKDIR /app

# Copy the poetry install requirements
COPY pyproject.toml poetry.lock ./

# Install poetry dependencies, without development dependencies and requiring no root source code (to prevent additional downloads)
# Delete the temporary poetry cache after use
RUN poetry install --no-root && rm -rf $POETRY_CACHE_DIR


# I dooooooooon't think I need this below code, but we'll see

# Download dependencies as a separate step to take advantage of Docker's caching.
# Leverage a cache mount to /root/.cache/pip to speed up subsequent builds.
# Leverage a bind mount to requirements.txt to avoid having to copy them into
# into this layer.
# RUN --mount=type=cache,target=/root/.cache/pip \
#     --mount=type=bind,source=requirements.txt,target=requirements.txt \
#     python -m pip install -r requirements.txt

# Harness a multi-stage build to remove previous dependencies and reduce package size
FROM python:3.11-slim-buster AS runtime

# Enable virtual environment
ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

# Copy the source code into the container.
COPY . .

# Expose the port that the application listens on.
EXPOSE 8000

# Run the file
# ENTRYPOINT ["python", "-m", ".main"]


