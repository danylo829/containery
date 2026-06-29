from flask import render_template, flash, redirect, url_for, session, request
from flask_login import login_user, logout_user, login_required, current_user

from app.modules.user.models import User, Role
from app.modules.settings.models import GlobalSettings
from app.lib.common import is_safe_url

from .helpers import create_admin_role
from .forms import LoginForm, AdminSetupForm

from . import auth

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard.index'))
    if not User.query.first():
        return redirect(url_for('auth.install'))

    form = LoginForm()

    next_page = request.args.get('next')
    
    if form.validate_on_submit():
        username = str(form.username.data).strip()
        password = form.password.data
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            session.permanent = True

            if next_page and is_safe_url(next_page, request.host_url):
                return redirect(next_page)
            
            return redirect(url_for('index.root'))
        else:
            flash('Invalid username or password', 'error')

    return render_template('login.html', form=form, next=next_page)

@auth.route('/install', methods=['GET', 'POST'])
def install():
    if User.query.first():
        return redirect(url_for('index.root'))

    password_min_length = int(GlobalSettings.get_setting('password_min_length'))

    form = AdminSetupForm(min_length=password_min_length)
    
    if form.validate_on_submit():
        username = str(form.username.data).strip()
        password = str(form.password.data)

        if len(password) < password_min_length:
            return redirect(url_for('auth.install'))

        try:
            user = User.create_user(
                username=username,
                password=password,
                name=str(form.name.data).strip() if form.name.data else None,
                email=str(form.email.data).strip() if form.email.data else None
            )
            if not user or not isinstance(user, User):
                flash("User creation failed. Please try again.", 'error')
                return redirect(url_for('auth.install'))
            
            admin_role = create_admin_role()
            if not admin_role or not isinstance(admin_role, Role):
                flash("Failed to create admin role. Please try again.", 'error')
                return redirect(url_for('auth.install'))

            user.assign_role(admin_role)

            flash("Admin user created successfully.", 'success')
            return redirect(url_for('index.root'))

        except Exception as e:
            flash(str(e), 'error')

    return render_template('install.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index.root'))