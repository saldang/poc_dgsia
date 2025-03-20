FROM python:3.12-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy the project into the image
COPY . /app

# Sync the project into a new environment, using the frozen lockfile
WORKDIR /app
RUN uv sync --frozen --no-cache

# Run the project
CMD [".venv/bin/streamlit", "run", "app/main.py", "--server.port", "80", "--server.enableCORS", "true"]