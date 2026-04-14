from os import getenv
import secrets

class Config:
    SECRET_KEY = getenv('SECRET_KEY', secrets.token_hex(32))
    CSRF_SECRET_KEY = getenv('CSRF_SECRET_KEY', secrets.token_hex(32))
    SQLALCHEMY_DATABASE_URI = getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:////containery_data/containery.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = getenv('SQLALCHEMY_TRACK_MODIFICATIONS', 'False') == 'True'
    DEBUG = getenv('DEBUG', 'False') == 'True'
    DOCKER_SOCKET_PATH = getenv('DOCKER_SOCKET_PATH', '/var/run/docker.sock')
    VERSION = getenv('CONTAINERY_VERSION', '0.1.0-dev')
    # ASSETS_DEBUG = True