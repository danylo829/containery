from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import current_user

from app.modules.user.forms import *
from app.modules.user.models import PersonalSettings, User, Role, Permissions

from app.modules.settings.models import GlobalSettings
from app.core.decorators import permission

from app.modules.user import user

@user.route('/profile', methods=['GET', 'POST'])
def profile():
    """
    Render and handle the current user's profile page.
    """
    password_min_length = int(GlobalSettings.get_setting('password_min_length'))

    settings_form = PersonalSettingsForm()
    password_form = ChangeOwnPasswordForm(password_min_length=password_min_length)

    if settings_form.submit.data and settings_form.validate_on_submit():
        PersonalSettings.set_setting(current_user.id, 'theme', settings_form.theme.data)
        
        flash('Settings updated successfully!', 'success')
        return redirect(url_for('user.profile'))

    if password_form.submit.data and password_form.validate_on_submit():
        if User.check_password(current_user.username, password_form.current_password.data):
            User.update_password(current_user.username, password_form.new_password.data)
            flash('Password updated successfully!', 'success')
        else:
            flash('Current password is incorrect.', 'error')
        return redirect(url_for('user.profile'))
    
    # Set form data based on current settings
    settings_form.theme.data = PersonalSettings.get_setting(current_user.id, 'theme')

    breadcrumbs = [
        {"name": "Dashboard", "url": url_for('main.dashboard.index')},
        {"name": "Users", "url": url_for('user.get_list')},
        {"name": current_user.username, "url": None},
    ]
    page_title = 'Profile'
    
    return render_template('user/profile.html', 
                           breadcrumbs=breadcrumbs, 
                           page_title=page_title, 
                           settings_form=settings_form, 
                           password_form=password_form)

@user.route('/list', methods=['GET'])
@permission(Permissions.USER_VIEW_LIST)
def get_list():
    """
    Render the user list page.
    """
    users = User.query.all()

    breadcrumbs = [
        {"name": "Dashboard", "url": url_for('main.dashboard.index')},
        {"name": "Users", "url": None},
    ]
    page_title = 'Users info'
    
    return render_template('user/table.html', 
                           breadcrumbs=breadcrumbs, 
                           page_title=page_title, 
                           users=users)

@user.route('', methods=['GET', 'POST'])
@permission(Permissions.USER_VIEW_PROFILE)
def view_profile():
    """
    Render and handle viewing another user's profile page.
    """
    user_id = request.args.get('id', type=int)
    user = User.query.get(user_id)
    
    if not user_id or not user:
        message = 'No such user.'
        code = 404
        return render_template('error.html', message=message, code=code), code

    password_min_length = int(GlobalSettings.get_setting('password_min_length'))

    password_form = ChangeUserPasswordForm(password_min_length=password_min_length)
    role_form = AddUserRoleForm()

    all_roles = Role.get_roles()
    user_roles = user.get_roles()
    available_roles = [role for role in all_roles if role not in user_roles]
    role_form.set_role_choices(available_roles)

    if request.method == 'POST' and not current_user.has_permission(Permissions.USER_EDIT):
        flash('You cannot edit users', 'error')
        return redirect(url_for('user.view_profile', id=user_id))

    if password_form.submit.data and password_form.validate_on_submit():
        if len(str(password_form.new_password.data)) < password_min_length:
            flash(f'Password length must be at least {password_min_length} characters long.', 'error')
            return redirect(url_for('user.view_profile', id=user_id))
            
        user.update_password(password_form.new_password.data)
        flash('Password changed successfully!', 'success')
        return redirect(url_for('user.view_profile', id=user_id))

    if role_form.submit.data and role_form.validate_on_submit():
        role = Role.get_role(int(role_form.role.data))
        try:
            user.assign_role(role)
            flash(f"Role '{role.name}' assigned successfully.", 'success')
        except (ValueError, LookupError) as e:
            flash(str(e), 'error')

        return redirect(url_for('user.view_profile', id=user_id))

    breadcrumbs = [
        {"name": "Dashboard", "url": url_for('main.dashboard.index')},
        {"name": "Users", "url": url_for('user.get_list')},
        {"name": user.username, "url": None},
    ]
    
    page_title = "View Profile"
    
    return render_template('user/view_profile.html', 
                           breadcrumbs=breadcrumbs, 
                           page_title=page_title,
                           password_form=password_form,
                           role_form=role_form,
                           user=user)

@user.route('/add', methods=['GET', 'POST'])
@permission(Permissions.USER_ADD)
def add():
    password_min_length = int(GlobalSettings.get_setting('password_min_length'))

    add_user_form = AddUserForm(password_min_length=password_min_length)
    add_user_form.set_role_choices(Role.get_roles())

    if add_user_form.submit.data and add_user_form.validate_on_submit():
        if len(str(add_user_form.password.data)) < password_min_length:
            flash(f'Minimal password length is {password_min_length} characters', 'error')
            return redirect(url_for('user.add'))

        user = User.create_user(add_user_form.username.data, add_user_form.password.data)

        if not isinstance(user, User):
            flash(user, 'error')
            return redirect(url_for('user.add'))

        result = user.assign_role(Role.get_role(int(add_user_form.role.data)))
        if result:
            flash(result)

        flash('User added successfully!', 'success')
        return redirect(url_for('user.get_list'))
    
    breadcrumbs = [
        {"name": "Dashboard", "url": url_for('main.dashboard.index')},
        {"name": "Users", "url": url_for('user.get_list')},
        {"name": "Add", "url": None},
    ]
    
    page_title = "Add user"
    
    return render_template('user/add.html', 
                           breadcrumbs=breadcrumbs, 
                           page_title=page_title,
                           add_user_form=add_user_form)

@user.route('/delete', methods=['DELETE'])
@permission(Permissions.USER_DELETE)
def delete():
    """
    Delete a user.
    """
    user_id = request.args.get('id', type=int)

    try:
        User.delete_user(int(user_id))
        return jsonify({'message': 'User deleted successfully.'}), 200

    except PermissionError as pe:
        return jsonify({'message': str(pe)}), 403

    except ValueError as ve:
        return jsonify({'message': str(ve)}), 400

    except LookupError as le:
        return jsonify({'message': str(le)}), 404

    except RuntimeError as re:
        return jsonify({'message': 'Failed to delete user.'}), 500