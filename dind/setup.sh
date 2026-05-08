#!/bin/sh

echo "Starting setup..."

echo "Pulling images..."
docker pull alpine:latest
docker pull nginx:alpine
docker pull busybox:latest

echo "Removing existing containers..."
docker rm -f $(docker ps -a -q) || true

echo "Creating containers..."

echo "Starting web-server..."
docker run -d --name web-server-$(hostname) --restart unless-stopped -p 80:80 nginx:alpine

echo "Starting worker-loop..."
docker run -d --name worker-loop-$(hostname) --restart unless-stopped alpine:latest sh -c "while true; do echo hello world; sleep 5; done"

echo "Running one-shot-task..."
docker run --name one-shot-task-$(hostname) busybox:latest echo "I am done"

echo "Setup complete."
