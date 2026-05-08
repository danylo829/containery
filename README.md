<div align="center">

  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="src/app/static/images/Containery-white.png">
    <img alt="Containery Logo" src="src/app/static/images/Containery-black.png" height="120">
  </picture>

  ![Version](https://img.shields.io/github/v/tag/danylo829/containery?label=version)
  ![Image Size](https://img.shields.io/badge/image%20size-170MB-blue)
  ![Python](https://img.shields.io/badge/python-3.12-blue)
  ![Last Commit](https://img.shields.io/github/last-commit/danylo829/containery)
  ![Contributions Welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)
  ![License](https://img.shields.io/github/license/danylo829/containery)

</div>

**Containery** is a web-based container management tool that provides a fast, lightweight, and intuitive interface for managing Docker containers. Whether you're a software engineer, DevOps, QA, or anyone who needs to interact with containers, Containery makes it easy to monitor status, view logs, and access terminals for quick insights and control.

## Features
- **Docker Management**: Manage containers, images, networks, and volumes within a unified interface.
- **Terminal and Logs**: View container logs and interact with container terminals directly in the UI.
- **Responsive Web Interface**: Access and manage Docker resources from any device.
- **User Management**: Authentication, user profiles, and roles. Ensure that each member has the right level of access to perform their tasks efficiently.

## Deployment
To deploy Containery, use the following `docker-compose.yml` configuration. Please note that the `docker-compose.yml` in the repository is set up for development purposes.

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

Once the application starts, you can access it by navigating to **[http://localhost:5000](http://localhost:5000)** in your browser. Feel free to change host port (e.g. 80:5000, 8080:5000)

### NGINX Reverse Proxy (Optional)
If you need to expose the application over a domain, add HTTPS or improve page loads by caching static content, you can use NGINX as a reverse proxy. Below is a sample NGINX configuration:

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

**Note**:  
1. If you're using NGINX as a reverse proxy, remove the `ports` section from the `docker-compose.yml` file for the `app` service.  
2. To enable static content caching, ensure that the `containery_static` volume is mounted to `/var/www/containery/static/dist` in the NGINX configuration. 
3. If you do not wish to enable static content caching, you can omit the `containery_static` volume mount and remove the `/static/dist/` location block from the NGINX configuration.

### Adding a Docker Host

Containery supports managing multiple Docker hosts. To register one, go to **Settings → Docker Hosts → Add** and provide a name and URL.

#### Remote host via socket proxy (recommended)

For remote machines, we recommend running [lscr.io/linuxserver/socket-proxy](https://github.com/linuxserver/docker-socket-proxy) on the remote host. It exposes the Docker socket over HTTP and lets you enable only the capabilities you actually need. For example, if you only want to browse images on a remote host, you can enable `IMAGES` and `INFO` alone and leave everything else off for security reasons.

See the [socket proxy documentation](https://github.com/linuxserver/docker-socket-proxy) for setup instructions and the full list of available capabilities.

Once the proxy is running on the remote machine, register it in Containery with:
- **URL**: `http://<remote-host>:<proxy-port>`

#### Local Unix socket

If you need to connect to a Docker daemon accessible via a Unix socket (e.g. a socket shared through a volume), use:
- **URL**: `unix:///path/to/docker.sock`

### Environment variables

#### Docker Configuration
- **`DOCKER_SOCKET_PATH`**: The path to the Docker socket. Defaults to `/var/run/docker.sock`.

#### Development
- **`SECRET_KEY`**: A secret key used for cryptographic operations. If not provided, a random 32-byte hexadecimal string will be generated.
- **`CSRF_SECRET_KEY`**: A secret key specifically for CSRF protection. If not provided, a random 32-byte hexadecimal string will be generated.
- **`SQLALCHEMY_DATABASE_URI`**: The database connection URI. Defaults to `sqlite:////containery_data/containery.db` for local development.
- **`SQLALCHEMY_TRACK_MODIFICATIONS`**: A flag to enable or disable SQLAlchemy's event system. Defaults to `False`.
- **`DEBUG`**: Enables or disables debug mode. Defaults to `False`.

## Screenshots

<p align="center">
  <img src="docs/images/dashboard.png" alt="Dashboard" width="600" />
  <br><em>Dashboard view</em>
</p>

<p align="center">
  <img src="docs/images/container_list.png" alt="Container List" width="600" />
  <br><em>Container list</em>
</p>

<p align="center">
  <img src="docs/images/terminal.png" alt="Terminal" width="600" />
  <br><em>Container terminal</em>
</p>

<p align="center">
  <img src="docs/images/role_add.png" alt="Role Add" width="600" />
  <br><em>Role management</em>
</p>

## Roadmap
- **OIDC Authentication**
- **Remote Docker host support**

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
