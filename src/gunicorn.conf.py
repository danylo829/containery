from os import getenv

DEBUG = getenv('DEBUG', 'False') == 'True'
HOST = getenv('HOST', '0.0.0.0')
PORT = int(getenv('PORT', 5000))

wsgi_app = 'wsgi:app'
bind = f'{HOST}:{PORT}'
workers = 1
worker_class = 'gevent'
reload = DEBUG
loglevel = 'debug' if DEBUG else 'info'