# Installation & Deployment

This page details how to deploy, configure, and maintain Containery across different environments.

---

## 1. Quick One-Line Script Installation

For a quick automated deployment on Linux servers with Docker installed:

```bash
curl -fsSL https://raw.githubusercontent.com/danylo829/containery/master/install.sh | sh
```

This script automatically pulls the latest `ghcr.io/danylo829/containery:latest` Docker image, mounts the local Docker Unix socket (`/var/run/docker.sock`), creates persistent data volumes, and starts Containery on **`http://localhost:5000`**.

---

## 2. Deployment with Docker Compose (Recommended)

To deploy Containery using Docker Compose, create a `docker-compose.yml` file:

```yaml
services:
  app:
    image: ghcr.io/danylo829/containery:latest
    container_name: containery
    restart: "unless-stopped"
    ports:
      - "5000:5000"
    environment:
      - SECRET_KEY=change_this_to_a_secure_random_hex_string
      - CSRF_SECRET_KEY=change_this_to_another_secure_random_hex_string
    volumes:
      - containery_data:/containery_data
      - containery_static:/containery/app/static/dist
      - /var/run/docker.sock:/var/run/docker.sock:ro

volumes:
  containery_data:
    name: containery_data
  containery_static:
    name: containery_static
```

Start the application container in detached mode:

```bash
docker compose up -d
```

Once running, access the web interface at **`http://localhost:5000`**.

---

## 3. Remote Docker Daemon Security & Socket Proxy

To manage remote Docker hosts safely, we recommend installing a secure socket proxy on remote machines (such as [`Tecnativa/docker-socket-proxy`](https://github.com/Tecnativa/docker-socket-proxy) or [`linuxserver/docker-socket-proxy`](https://github.com/linuxserver/docker-socket-proxy)).

The socket proxy exposes Docker daemon endpoints over HTTP/HTTPS while enabling fine-grained read/write permission controls.

Example `docker-compose.yml` for remote socket proxy:

```yaml
services:
  socket-proxy:
    image: linuxserver/socket-proxy:latest
    container_name: docker_socket_proxy
    restart: unless-stopped
    ports:
      - "2375:2375"
    environment:
      - CONTAINERS=1
      - IMAGES=1
      - NETWORKS=1
      - VOLUMES=1
      - INFO=1
      - POST=1
      - DELETE=1
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
```

After deploying the socket proxy on the remote server:

1. Navigate to **Settings** > **Docker Hosts** > **Add Host**.
2. Set the **URL** to `http://<remote-server-ip>:2375`.

---

## 4. NGINX Reverse Proxy & WebSocket Configuration

If exposing Containery behind NGINX with SSL/HTTPS or domain routing, ensure WebSocket upgrade headers are passed for the interactive web terminal (`/socket.io`).

Here is a complete NGINX configuration block:

```nginx
server {
    listen 80;
    server_name containery.example.com;

    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
    gzip_vary on;
    gzip_min_length 1024;

    # Serve static assets directly from container volume for performance
    location ^~ /static/dist/ {
        root /var/www/containery;
        autoindex off;
        access_log off;
        expires max;
        add_header Cache-Control "public, max-age=31536000, immutable";
    }

    # WebSocket proxying for real-time container terminals
    location /socket.io {
        proxy_pass http://app:5000/socket.io;
        proxy_http_version 1.1;
        proxy_buffering off;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";

        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Main application proxy
    location / {
        proxy_pass http://app:5000;

        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 5. Environment Variables

### Deployment & Production Environment Variables

Primary configuration variable used to set the Docker host socket location for deployment.

| Variable Name | Description | Default Value |
| :--- | :--- | :--- |
| `DOCKER_SOCKET_PATH` | Path to the target Docker daemon Unix socket. | `/var/run/docker.sock` |

### Development & Application Configuration Environment Variables

Application security keys, database storage paths, and debugging flags.

| Variable Name | Description | Default Value |
| :--- | :--- | :--- |
| `SECRET_KEY` | Secret key used for session cryptographic operations. | Auto-generated 32-byte hex string |
| `CSRF_SECRET_KEY` | Secret key specifically for CSRF token protection. | Auto-generated 32-byte hex string |
| `SQLALCHEMY_DATABASE_URI` | SQLite database URI connection path. | `sqlite:////containery_data/containery.db` |
| `DEBUG` | Enable Flask debug mode and interactive reloader. | `False` |
| `SQLALCHEMY_TRACK_MODIFICATIONS` | Flag for SQLAlchemy event tracking. | `False` |
| `CONTAINERY_VERSION` | Override application release version string. | `0.1.0-dev` |
