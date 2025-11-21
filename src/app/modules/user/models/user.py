from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from time import time
import json

from app.core.extensions import db
from .role import Role, UserRole
from .helpers import merge_named_list

class User(UserMixin, db.Model):
    __tablename__ = 'usr_user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)
    created_at = db.Column(db.Integer, default=lambda: int(time()), nullable=False)

    personal_settings = db.relationship('PersonalSettings', backref='user', cascade="all, delete-orphan")
    user_roles = db.relationship('UserRole', back_populates='user', cascade='all, delete-orphan')

    def update_password(self, new_password):
        self.password_hash = generate_password_hash(new_password)
        db.session.commit()

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @classmethod
    def create_user(cls, username, password):
        if cls.query.filter_by(username=username).first():
            return "Username already exists"

        user = cls(username=username, password_hash=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        
        return user

    def has_permission(self, permission):
        if not isinstance(permission, int):
            raise ValueError("Permission must be an integer value from Permissions.")
        for user_role in self.user_roles:
            if user_role.role_id == 1:
                return True
            for role_permission in user_role.role.permissions:
                if role_permission.permission == permission:
                    return True
        return False

    def get_roles(self):
        return [user_role.role for user_role in self.user_roles]

    def get_roles_str(self):
        return ', '.join([role.role.name for role in self.user_roles])

    def assign_role(self, role):
        if not isinstance(role, Role):
            raise ValueError("Role must be an instance of the Role model.")
        if not role:
            raise LookupError("The role provided does not exist.")
        if any(user_role.role_id == role.id for user_role in self.user_roles):
            raise ValueError(f"Role '{role.name}' is already assigned to the user.")
        new_user_role = UserRole(user_id=self.id, role_id=role.id)
        db.session.add(new_user_role)
        db.session.commit()

    def remove_role(self, role):
        if not isinstance(role, Role):
            raise ValueError(f"Expected a Role instance, got {type(role)}")
        if self.id == 1 and role.id == 1:
            raise PermissionError("Cannot remove the 'admin' role from the main admin.")
        user_role = UserRole.query.filter_by(user_id=self.id, role_id=role.id).first()
        if not user_role:
            raise LookupError(f"Role '{role.name}' not assigned to the user.")
        try:
            db.session.delete(user_role)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Failed to remove role: {str(e)}")

    @classmethod
    def delete_user(cls, id):    
        if not isinstance(id, int) or id <= 0:
            raise ValueError("Invalid user ID provided.")
        if id == 1:
            raise PermissionError("The admin user cannot be deleted.")
        user = cls.query.filter_by(id=id).first()
        if not user:
            raise LookupError(f"User with ID '{id}' not found.")
        try:
            db.session.delete(user)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Failed to delete user: {str(e)}")

class PersonalSettings(db.Model):
    __tablename__ = 'usr_personal_settings'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('usr_user.id'), nullable=False)
    key = db.Column(db.String(150), nullable=False)
    value = db.Column(db.String(150), nullable=False)

    defaults = {
        'theme': {
            'options': ['light', 'dark', 'dark_mixed', 'system'],
            'default': 'system',
        },
        'container_list_columns': {
            'default': [
                {'name': 'Name',           'enabled': True},
                {'name': 'Status',         'enabled': True},
                {'name': 'Image',          'enabled': True},
                {'name': 'Quick actions',  'enabled': True},
                {'name': 'Ports',          'enabled': False},
                {'name': 'Created',        'enabled': False},
                {'name': 'State',          'enabled': False}
            ]
        },
        'container_list_quick_actions': {
            'default': [
                {'name': 'Start',     'enabled': False},
                {'name': 'Stop',      'enabled': False},
                {'name': 'Restart',   'enabled': False},
                {'name': 'Delete',    'enabled': False},
                {'name': 'Processes', 'enabled': True},
                {'name': 'Logs',      'enabled': True},
                {'name': 'Terminal',  'enabled': True},
            ]
        },
    }

    @classmethod
    def get_setting(cls, user_id, key, json_format=False):
        setting = cls.query.filter_by(user_id=user_id, key=key).first()
        if not setting:
            default_config = cls.defaults.get(key)
            if default_config:
                return default_config['default']
            return None
        if json_format:
            return json.loads(setting.value)
        return setting.value

    @classmethod
    def set_setting(cls, user_id, key, value, json_format=False):
        if json_format:
            value = json.dumps(value)
        setting = cls.query.filter_by(user_id=user_id, key=key).first()
        if setting:
            setting.value = value
        else:
            setting = cls(user_id=user_id, key=key, value=value)
            db.session.add(setting)
        db.session.commit()

    @classmethod
    def migrate_all(cls):
        """Normalize list-type settings for all users against current defaults.

        Generic merge: preserves user 'enabled' flags, removes
        obsolete entries, appends new defaults, and fills missing keys inside
        existing items without repeated list scans or in-loop removals.
        """
        list_setting_keys = [
            'container_list_columns',
            'container_list_quick_actions',
        ]
        default_cache = {
            key: cls.defaults[key]['default'] for key in list_setting_keys
        }
        user_ids = [row[0] for row in db.session.query(User.id).all()]
        for uid in user_ids:
            for key in list_setting_keys:
                default_list = default_cache[key]
                current_list = cls.get_setting(uid, key, json_format=True)
                if not isinstance(current_list, list):
                    continue
                merged = merge_named_list(current_list, default_list)
                cls.set_setting(uid, key, merged, json_format=True)