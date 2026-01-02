from app.core.db import db
from urllib.parse import urlparse

class DockerHost(db.Model):
    __tablename__ = 'stg_docker_hosts'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    url = db.Column(db.String(255), nullable=False)
    enabled = db.Column(db.Boolean, default=True)

    @property
    def scheme(self):
        if self.url.startswith('unix://'):
            return 'unix'
        return urlparse(self.url).scheme

    @property
    def address(self):
        if self.scheme == 'unix':
            return self.url.replace('unix://', '')
        parsed = urlparse(self.url)
        return (parsed.hostname, parsed.port or 80)

    def as_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'url': self.url,
            'enabled': self.enabled,
        }
    
    @classmethod
    def add(cls, name, url, enabled=True):
        host = cls(name=name, url=url, enabled=enabled)
        db.session.add(host)
        db.session.commit()
        return host
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def edit(self, name=None, url=None, enabled=None):
        if name is not None:
            self.name = name
        if url is not None:
            self.url = url
        if enabled is not None:
            self.enabled = enabled
        db.session.commit()

class GlobalSettings(db.Model):
    __tablename__ = 'stg_global_settings'
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(150), unique=True, nullable=False)
    value = db.Column(db.String(150), nullable=False)

    defaults = {
        'dashboard_refresh_interval': 5,
        'session_timeout': 1800,
        'password_min_length': 8,
        'latest_version': '',
        'latest_version_checked_at': '',
    }

    @classmethod
    def get_setting(cls, key):
        if key not in cls.defaults:
            raise KeyError(f"The setting '{key}' is not defined in defaults.")

        try:
            setting = cls.query.filter_by(key=key).first()
            return setting.value if setting else cls.defaults[key]
        except Exception as e:
            raise RuntimeError(f"Database error while retrieving setting '{key}': {str(e)}")

    @classmethod
    def set_setting(cls, key, value):
        if key not in cls.defaults:
            raise KeyError(f"The setting '{key}' is not defined in defaults.")

        try:
            setting = cls.query.filter_by(key=key).first()
            if setting:
                setting.value = str(value)
            else:
                setting = cls(key=key, value=str(value))
                db.session.add(setting)

            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Database error while setting '{key}': {str(e)}")

    @classmethod
    def delete_setting(cls, key):
        if key not in cls.defaults:
            raise KeyError(f"The setting '{key}' is not defined in defaults.")
        
        try:
            setting = cls.query.filter_by(key=key).first()
            if setting:
                db.session.delete(setting)
                db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Database error while deleting setting '{key}': {str(e)}")