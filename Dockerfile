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

EXPOSE 5000

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

ENTRYPOINT ["./entrypoint.sh"]