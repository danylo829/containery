#!/bin/sh
set -e

# Start dockerd in background using the original entrypoint logic
# We assume the original entrypoint is available at /usr/local/bin/dockerd-entrypoint.sh
# and that passing arguments works as expected.
/usr/local/bin/dockerd-entrypoint.sh dockerd &
DOCKERD_PID=$!

# Wait for the daemon to be ready
echo "Waiting for Docker daemon..."
timeout=60
while ! docker info >/dev/null 2>&1; do
    timeout=$(($timeout - 1))
    if [ $timeout -eq 0 ]; then
        echo "Timed out waiting for Docker daemon."
        exit 1
    fi
    sleep 1
done

echo "Docker daemon is ready."

# Run our setup script
/usr/local/bin/setup.sh

# Wait for the daemon process to exit (it shouldn't, unless we stop the container)
wait $DOCKERD_PID
