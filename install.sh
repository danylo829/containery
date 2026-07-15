#!/sh
set -e

# Containery Automatic Installer & Launcher
# Installs and launches Containery inside Docker

echo "========================================="
echo "   Containery Installer & Launcher"
echo "========================================="

# 1. Check if Docker is installed
if ! command -v docker >/dev/null 2>&1; then
    echo "Error: Docker is not installed or not in PATH." >&2
    echo "Please install Docker first: https://docs.docker.com/get-docker/" >&2
    exit 1
fi

# 2. Check if Docker socket is accessible
if ! docker ps >/dev/null 2>&1; then
    echo "Error: Cannot connect to Docker daemon." >&2
    echo "Please ensure the Docker daemon is running and your user has permissions." >&2
    exit 1
fi

echo "✔ Docker detected and accessible."

# 3. Pull latest image
echo "Pulling latest Containery image..."
docker pull ghcr.io/danylo829/containery:latest

# 4. Check if a container with the same name already exists
if docker ps -a --format '{{.Names}}' | grep -Eq "^containery$"; then
    echo "An existing 'containery' container was found."
    echo "Stopping and removing the old container to upgrade..."
    docker stop containery >/dev/null 2>&1 || true
    docker rm containery >/dev/null 2>&1 || true
fi

# 5. Run the container
echo "Starting Containery in the background on port 5000..."
docker run -d \
  --name containery \
  --restart unless-stopped \
  -p 5000:5000 \
  -v /var/run/docker.sock:/var/run/docker.sock:ro \
  ghcr.io/danylo829/containery:latest

echo "========================================="
echo "✔ Containery is running!"
echo "Access the web UI at: http://localhost:5000"
echo "========================================="
