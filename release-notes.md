# Containery 1.3.4 is out!

This release includes critical security hardening across Socket.IO and management API endpoints, CSRF protection fixes, Docker build refactorings, and documentation updates.

### Bug Fixes

- **container:** Require authentication and permission checks for container exec Socket.IO sessions
- **core:** Enforce delete and edit permissions on management API endpoints
- **settings:** Enable CSRF validation on global settings update endpoint

### Features

- **docs:** Expand documentation with dedicated feature guides and setup Zensical docs workflow

### Improvements

- **core:** Combine production and development Dockerfiles and clean up Gunicorn configuration

Feedback, issues, and contributions are welcome.