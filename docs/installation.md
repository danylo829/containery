# Installation & Deployment

This page details how to deploy and configure Containery in different environments.

## Deployment with Docker Compose

To deploy Containery, use the following `docker-compose.yml` configuration.

```yaml
services:
  app:
    image: ghcr.io/danylo829/containery:latest
    container_name: containery
    restart: "unless-stopped"
    ports:
      - "5000:5000"
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

Start the application by running:

```bash
docker compose up -d
```

Once the application starts, access it by navigating to **[http://localhost:5000](http://localhost:5000)** in your web browser. You can customize the host port (e.g. `80:5000` or `8080:5000`) in the `ports` mapping.

---

## NGINX Reverse Proxy Configuration (Optional)

If you expose Containery over a domain, want to add SSL/HTTPS, or improve page loads by caching static assets, you can run NGINX as a reverse proxy.

Here is a sample NGINX configuration block:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
    gzip_vary on;
    gzip_min_length 1024;

    location ^~ /static/dist/ {
        root /var/www/containery;
        autoindex off;
        access_log off;
        expires max;
        add_header Cache-Control "public, max-age=31536000, immutable";
    }

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

!!! note

    1. If NGINX is reverse proxying within the same Docker network, you can remove the `ports` section from the `app` service in `docker-compose.yml` to prevent public access on port 5000.
    2. To cache static content, ensure the `containery_static` volume is mounted to `/var/www/containery/static/dist` in the NGINX container.
    3. If you do not wish to cache static content, remove the `/static/dist/` location block from the NGINX configuration.

---

## Environment Variables

### Docker Configuration
*   `DOCKER_SOCKET_PATH`: The path to the Docker socket. Defaults to `/var/run/docker.sock`.

### Development
*   `SECRET_KEY`: A secret key used for cryptographic operations. If not provided, a random 32-byte hexadecimal string will be generated automatically on startup.
*   `CSRF_SECRET_KEY`: A secret key specifically for CSRF protection. If not provided, a random 32-byte hexadecimal string will be generated.
*   `SQLALCHEMY_DATABASE_URI`: The database connection URI. Defaults to `sqlite:////containery_data/containery.db`.
*   `SQLALCHEMY_TRACK_MODIFICATIONS`: A flag to enable or disable SQLAlchemy's event system. Defaults to `False`.
*   `DEBUG`: Enables or disables debug mode. Defaults to `False`.
