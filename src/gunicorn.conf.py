from os import getenv

DEBUG = getenv('DEBUG', 'False') == 'True'
PORT = int(getenv('PORT', 5000))

wsgi_app = 'wsgi:app'
bind = f'0.0.0.0:{PORT}'
workers = 1  # Only one worker is used to ensure WebSocket support with Gevent
worker_class = 'gevent'
reload = DEBUG
loglevel = 'debug' if DEBUG else 'info'