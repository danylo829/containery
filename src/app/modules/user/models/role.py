from app.core.db import db

class Role(db.Model):
    __tablename__ = 'usr_role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    created_at = db.Column(db.Integer, default=lambda: int(__import__('time').time()), nullable=False)

    user_roles = db.relationship('UserRole', back_populates='role', cascade='all, delete-orphan')
    permissions = db.relationship('RolePermission', back_populates='role', cascade='all, delete-orphan')

    @classmethod
    def create_role(cls, name):
        if not name or not name.strip():
            raise ValueError("Role name cannot be empty.")
        if len(name) > 20:
            raise ValueError("Role name must be 20 characters or less.")
        existing_role = cls.query.filter_by(name=name).first()
        if existing_role:
            raise ValueError(f"Role '{name}' already exists.")
        try:
            role = cls(name=name)
            db.session.add(role)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Failed to create role: {str(e)}")
        return role
    
    @classmethod
    def delete_role(cls, id):
        if not isinstance(id, int) or id <= 0:
            raise ValueError("Invalid role ID provided.")
        if id == 1:
            raise PermissionError("The admin role cannot be deleted.")
        role = cls.query.filter_by(id=id).first()
        if not role:
            raise LookupError(f"Role with ID '{id}' not found.")
        try:
            db.session.delete(role)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Failed to delete role: {str(e)}")
        
    @classmethod
    def get_roles(cls):
        return cls.query.all()
    
    @classmethod
    def get_role(cls, id):
        if not isinstance(id, int) or id <= 0:
            raise ValueError("Invalid role ID provided.")
        
        role = cls.query.filter_by(id=id).first()

        if not role:
            raise LookupError(f"Role with ID '{id}' not found.")

        return role

    def rename(self, name):
        if not name or not isinstance(name, str):
            raise ValueError("Invalid role name")
        if len(name) > 20:
            raise ValueError("Role name must be 20 characters or less.")
        self.name = name
        db.session.commit()

    def get_user_count(self):
        if not self.id:
            raise ValueError("The role must have a valid ID.")
        user_count = UserRole.query.filter_by(role_id=self.id).count()
        return user_count

    def get_permissions(self):
        return [p.permission for p in self.permissions]

    def add_permission(self, permission):
        if not isinstance(permission, int):
            raise ValueError("Permission must be an integer value from Permissions.")
        if any(rp.permission == permission for rp in self.permissions):
            return
        new_permission = RolePermission(role_id=self.id, permission=permission)
        db.session.add(new_permission)
        db.session.commit()

    def get_permissions_values(self):
        return [rp.permission for rp in RolePermission.query.filter_by(role_id=self.id).all()]

    def remove_permission(self, permission):
        if not isinstance(permission, int):
            raise ValueError("Permission must be an integer value from Permissions.")
        role_permission = RolePermission.query.filter_by(role_id=self.id, permission=permission).first()
        if not role_permission:
            return
        db.session.delete(role_permission)
        db.session.commit()

class RolePermission(db.Model):
    __tablename__ = 'usr_role_permission'
    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('usr_role.id'), nullable=False)
    permission = db.Column(db.Integer, nullable=False)
    role = db.relationship('Role', back_populates='permissions')

class UserRole(db.Model):
    __tablename__ = 'usr_user_role'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('usr_user.id'), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('usr_role.id'), nullable=False)
    user = db.relationship('User', back_populates='user_roles')
    role = db.relationship('Role', back_populates='user_roles')
