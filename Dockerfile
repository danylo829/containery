FROM python:3.12-alpine AS builder

WORKDIR /build

RUN apk add --no-cache \
    build-base \
    linux-headers

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.12-alpine

WORKDIR /containery

RUN apk add --no-cache sqlite

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

EXPOSE $PORT

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HOST=0.0.0.0 \
    PORT=5000 \
    CONTAINERY_VERSION=v0.1.0-dev

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://${HOST}:${PORT}/ping || exit 1

ENTRYPOINT ["./entrypoint.sh"]