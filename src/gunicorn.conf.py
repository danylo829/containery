from os import getenv

DEBUG = getenv('DEBUG', 'False') == 'True'

wsgi_app = 'wsgi:app'
bind = '0.0.0.0:5000'
workers = 1  # Only one worker is used to ensure WebSocket support with Gevent
worker_class = 'gevent'
reload = DEBUG
loglevel = 'debug' if DEBUG else 'info'