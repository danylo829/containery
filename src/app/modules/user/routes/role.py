from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import current_user

from app.modules.user.forms import *
from app.modules.user.models import User, Role, Permissions

from app.core.decorators import permission

from app.modules.user import user

@user.route('/role/list', methods=['GET'])
@permission(Permissions.ROLE_VIEW_LIST)
def get_role_list():
    """
    Render the role list page.
    """
    roles = Role.get_roles()
    breadcrumbs = [
        {"name": "Dashboard", "url": url_for('main.dashboard.index')},
        {"name": "Users", "url": url_for('user.get_list')},
        {"name": "Roles", "url": None},
    ]
    page_title = 'Roles'
    
    return render_template('user/table_role.html', 
                           breadcrumbs=breadcrumbs, 
                           page_title=page_title, 
                           roles=roles)

@user.route('/role', methods=['GET', 'POST'])
@permission(Permissions.ROLE_VIEW)
def view_role():
    form = RoleForm()

    role_id = request.args.get('id', type=int)

    try:
        role = Role.get_role(id=role_id)
    except ValueError as ve:
        flash(str(ve), 'error')
        return redirect(url_for('user.get_list'))
    except LookupError as le:
        flash(str(le), 'error')
        return redirect(url_for('user.get_list'))

    if form.validate_on_submit():
        if role_id == 1:
            flash('Can\'t edit super admin role.', 'error')
            return redirect(url_for('user.get_list'))
        if not current_user.has_permission(Permissions.ROLE_EDIT):
            flash('You don\'t have permission to edit roles', 'error')
            return redirect(url_for('user.view_role', id=role_id))

        name = str(form.name.data).strip()
        selected_permissions = [
            int(entry['permission_value'])
            for entry in form.permissions.data if entry['enabled']
        ]

        try:
            role.rename(name)

            for permission in selected_permissions:
                if permission not in role.get_permissions():
                    role.add_permission(permission=permission)

            for permission in role.get_permissions():
                if permission not in selected_permissions:
                    role.remove_permission(permission=permission)

            flash(f"Role '{name}' updated successfully", 'success')

        except ValueError as ve:
            flash(str(ve), 'error')
        except Exception as e:
            flash(f"An unexpected error occurred: {str(e)}", 'error')
        
        return redirect(url_for('user.view_role', id=role_id))
    
    if not form.permissions.entries:
        for permission in Permissions:
            is_enabled = permission.value in role.get_permissions_values()
            form.permissions.append_entry({
                'enabled': is_enabled,
                'permission_value': permission.value
            })

    form.name.data = role.name

    category_order = ['CONTAINER', 'IMAGE', 'NETWORK', 'VOLUME', 'USER', 'ROLE', 'GLOBAL']

    categories = {}
    for permission_form, permission in zip(form.permissions, Permissions):
        category = permission.name.split('_')[0]
        if category not in categories:
            categories[category] = []
        categories[category].append((permission_form, permission))

    ordered_categories = {cat: categories[cat] for cat in category_order if cat in categories}

    breadcrumbs = [
        {"name": "Dashboard", "url": url_for('main.dashboard.index')},
        {"name": "Users", "url": url_for('user.get_list')},
        {"name": "Roles", "url": url_for('user.get_list')},
        {"name": role.name, "url": None},
    ]
    
    page_title = "View Role"
    
    return render_template('user/role.html',
                           breadcrumbs=breadcrumbs,
                           page_title=page_title,
                           role=role,
                           form=form,
                           categories=ordered_categories)

@user.route('/role/add', methods=['GET', 'POST'])
@permission(Permissions.ROLE_ADD)
def add_role():
    """
    Render and handle the add role page.
    """
    form = RoleForm()

    if not form.permissions.entries:
        for permission in Permissions:
            form.permissions.append_entry({
                'enabled': False,
                'permission_value': permission.value
            })

    if form.validate_on_submit():
        name = str(form.name.data).strip()
        selected_permissions = [
            int(entry['permission_value'])
            for entry in form.permissions.data if entry['enabled']
        ]

        try:
            role = Role.create_role(name)
            flash(f"Role '{name}' created successfully", 'success')

            for permission in selected_permissions:
                role.add_permission(permission=permission)

            return redirect(url_for('user.get_role_list'))

        except ValueError as ve:
            flash(str(ve), 'error')
        except Exception as e:
            flash(f"An unexpected error occurred: {str(e)}", 'error')
    elif request.method == 'POST':
        flash('Form validation failed.', 'error')

    category_order = ['CONTAINER', 'IMAGE', 'NETWORK', 'VOLUME', 'USER', 'ROLE', 'GLOBAL']

    categories = {}
    for permission_form, permission in zip(form.permissions, Permissions):
        category = permission.name.split('_')[0]
        if category not in categories:
            categories[category] = []
        categories[category].append((permission_form, permission))

    ordered_categories = {cat: categories[cat] for cat in category_order if cat in categories}

    breadcrumbs = [
        {"name": "Dashboard", "url": url_for('main.dashboard.index')},
        {"name": "Users", "url": url_for('user.get_list')},
        {"name": "Roles", "url": url_for('user.get_list')},
        {"name": "Add", "url": None},
    ]
    
    page_title = "Add role"

    return render_template('user/role.html',
                           breadcrumbs=breadcrumbs,
                           page_title=page_title,
                           form=form,
                           categories=ordered_categories)

@user.route('/role/remove', methods=['DELETE'])
@permission(Permissions.ROLE_EDIT)
def remove_role():
    """
    Remove a role from a user.
    """
    user_id = request.form.get('user_id')
    role_id = request.form.get('role_id')

    try:
        user = User.query.get(user_id)
        role = Role.get_role(int(role_id))

        user.remove_role(role)

        return jsonify({'success': True}), 200
    
    except PermissionError as pe:
        return jsonify({'message': str(pe)}), 403

    except ValueError as ve:
        return jsonify({'message': str(ve)}), 400

    except LookupError as le:
        return jsonify({'message': str(le)}), 404

    except RuntimeError as re:
        return jsonify({'message': 'Failed to remove role.'}), 500
    
@user.route('/role/delete', methods=['DELETE'])
@permission(Permissions.ROLE_EDIT)
def delete_role():
    """
    Delete a role.
    """
    role_id = request.args.get('id', type=int)

    if not role_id:
        return jsonify({'message': 'Role ID is required.'}), 400

    try:
        Role.delete_role(role_id)

        return jsonify({'success': True}), 200

    except PermissionError as pe:
        return jsonify({'message': str(pe)}), 403

    except ValueError as ve:
        return jsonify({'message': str(ve)}), 400

    except LookupError as le:
        return jsonify({'message': str(le)}), 404

    except RuntimeError as re:
        return jsonify({'message': 'Failed to delete role.'}), 500