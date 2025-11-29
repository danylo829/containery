import click
from faker import Faker
import random
from werkzeug.security import generate_password_hash

from app import ApplicationFactory
from app.core.extensions import db
from app.modules.user.models.user import User, PersonalSettings
from app.modules.user.models.role import Role, RolePermission, UserRole
from app.modules.user.models.permissions import Permissions, permission_names
from app.modules.settings.models import GlobalSettings

# Helper to escape single quotes for raw SQL generation
_def_escape = lambda s: s.replace("'", "''") if isinstance(s, str) else s

@click.command('seed')
@click.option('--users', default=25, show_default=True, help='Number of non-admin users to create')
@click.option('--roles', default=5, show_default=True, help='Number of additional roles to create (excluding admin)')
@click.option('--permissions-per-role', default=8, show_default=True, help='Approx permissions per role (sampled)')
@click.option('--personal-settings/--no-personal-settings', default=True, show_default=True, help='Populate PersonalSettings for each user')
@click.option('--sql-file', type=click.Path(dir_okay=False), default=None, help='If provided, also emit a raw SQL file with INSERT statements')
def seed_command(users, roles, permissions_per_role, personal_settings, sql_file):
    """Populate the database with synthetic test data.

    Creates:
      - Ensures admin role & user exist (id=1 semantics if fresh DB)
      - Extra roles with random permission subsets
      - Users with hashed passwords (password = 'Password123!')
      - Role assignments (each user 1-2 roles)
      - Optional personal settings per user
      - Optional raw SQL file mirroring inserts
    """
    app_factory = ApplicationFactory()
    app = app_factory.create_app()
    fake = Faker()

    sql_statements = []

    with app.app_context():
        # Ensure GlobalSettings defaults exist
        for k, v in GlobalSettings.defaults.items():
            existing = GlobalSettings.query.filter_by(key=k).first()
            if not existing:
                gs = GlobalSettings(key=k, value=str(v))
                db.session.add(gs)
                sql_statements.append(
                    f"INSERT INTO stg_global_settings (key, value) VALUES ('{_def_escape(k)}', '{_def_escape(v)}');"
                )

        # Admin role
        admin_role = Role.query.filter_by(name='admin').first()
        if not admin_role:
            admin_role = Role(name='admin')
            db.session.add(admin_role)
            db.session.flush()  # get id
            sql_statements.append(
                f"INSERT INTO usr_role (name, created_at) VALUES ('admin', strftime('%s','now'));"  # sqlite epoch
            )

        # Grant all permissions to admin role
        existing_admin_perms = {p.permission for p in admin_role.permissions}
        for perm_name in permission_names:
            perm_value = getattr(Permissions, perm_name)
            if perm_value not in existing_admin_perms:
                rp = RolePermission(role_id=admin_role.id, permission=perm_value)
                db.session.add(rp)
                sql_statements.append(
                    f"INSERT INTO usr_role_permission (role_id, permission) VALUES ({admin_role.id}, {perm_value});"
                )

        generated_roles = []
        # Generate additional roles
        for i in range(roles):
            name = fake.unique.job().lower().replace(' ', '_')[:20]
            if Role.query.filter_by(name=name).first():
                continue
            r = Role(name=name)
            db.session.add(r)
            db.session.flush()
            generated_roles.append(r)
            sql_statements.append(
                f"INSERT INTO usr_role (name, created_at) VALUES ('{_def_escape(name)}', strftime('%s','now'));"
            )
            # Assign random subset of permissions
            chosen_perm_names = fake.random_sample(elements=permission_names, length=min(permissions_per_role, len(permission_names)))
            for pn in chosen_perm_names:
                pv = getattr(Permissions, pn)
                rp = RolePermission(role_id=r.id, permission=pv)
                db.session.add(rp)
                sql_statements.append(
                    f"INSERT INTO usr_role_permission (role_id, permission) VALUES ({r.id}, {pv});"
                )

        # Ensure admin user
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(username='admin', password_hash=generate_password_hash('Admin123!'))
            db.session.add(admin_user)
            db.session.flush()
            sql_statements.append(
                f"INSERT INTO usr_user (username, password_hash, created_at) VALUES ('admin', '{_def_escape(admin_user.password_hash)}', strftime('%s','now'));"
            )
            ur = UserRole(user_id=admin_user.id, role_id=admin_role.id)
            db.session.add(ur)
            sql_statements.append(
                f"INSERT INTO usr_user_role (user_id, role_id) VALUES ({admin_user.id}, {admin_role.id});"
            )

        # Generate users
        all_role_ids = [r.id for r in generated_roles]
        password_plain = 'Password123!'
        for _ in range(users):
            username = fake.unique.user_name()[:150]
            if User.query.filter_by(username=username).first():
                continue
            pw_hash = generate_password_hash(password_plain)
            u = User(username=username, password_hash=pw_hash)
            db.session.add(u)
            db.session.flush()
            sql_statements.append(
                f"INSERT INTO usr_user (username, password_hash, created_at) VALUES ('{_def_escape(username)}', '{_def_escape(pw_hash)}', strftime('%s','now'));"
            )
            # Assign 1-2 random roles
            if all_role_ids:
                assign_ids = random.sample(all_role_ids, k=min(len(all_role_ids), random.choice([1, 2])))
                for rid in assign_ids:
                    ur = UserRole(user_id=u.id, role_id=rid)
                    db.session.add(ur)
                    sql_statements.append(
                        f"INSERT INTO usr_user_role (user_id, role_id) VALUES ({u.id}, {rid});"
                    )
            # Personal settings
            if personal_settings:
                for key, meta in PersonalSettings.defaults.items():
                    value = meta['default']
                    is_json = isinstance(value, (list, dict))
                    ps = PersonalSettings(user_id=u.id, key=key, value=(json_dumps(value) if is_json else str(value)))
                    db.session.add(ps)
                    escaped_val = _def_escape(ps.value)
                    sql_statements.append(
                        f"INSERT INTO usr_personal_settings (user_id, key, value) VALUES ({u.id}, '{_def_escape(key)}', '{escaped_val}');"
                    )

        db.session.commit()

    if sql_file:
        with open(sql_file, 'w', encoding='utf-8') as f:
            f.write('-- Seed data generated by seed_command\n')
            for stmt in sql_statements:
                f.write(stmt + '\n')
        click.echo(f"Raw SQL written to {sql_file}")

    click.echo("Seeding complete:")
    click.echo(f"  Roles created: {len(generated_roles)} (+ admin)")
    click.echo(f"  Users created: {users} (+ admin if created)")
    click.echo("  Personal settings: " + ("yes" if personal_settings else "no"))

# Compatibility helper for dumps without importing json globally in command context
import json as _json
json_dumps = _json.dumps

if __name__ == '__main__':
    # Direct run behaves like: python -m app.cli.seed --users 10 --sql-file seed.sql
    seed_command.main(standalone_mode=True)
