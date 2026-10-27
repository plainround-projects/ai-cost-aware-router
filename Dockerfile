# The command-line program as an image. Nothing here serves traffic; the health command is the image's check.
#   docker run --rm cost-router:dev cost-router all     (replays the recorded fixtures)
FROM python:3.13.1-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PROJECT_ROOT=/app

WORKDIR /app
COPY requirements.lock ./
RUN pip install --require-hashes -r requirements.lock

COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-deps .
COPY data ./data
COPY prompts ./prompts
COPY config ./config
COPY tests/fixtures ./tests/fixtures

RUN useradd --system --uid 10001 --home-dir /app app && mkdir -p /app/reports && chown app /app/reports
USER app

HEALTHCHECK --interval=60s --timeout=20s --retries=3 CMD ["cost-router", "health"]
CMD ["cost-router", "health"]
