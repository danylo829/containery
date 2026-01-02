from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import current_user

from app.modules.settings.models import DockerHost
from app.modules.settings.forms import DockerHostForm
from app.core.db import db
from app.core.extensions import docker

from app.modules.user.models import Permissions
from app.core.decorators import permission

from app.modules.settings import settings

@settings.route('/docker-hosts', methods=['GET'])
@permission(Permissions.GLOBAL_SETTINGS_VIEW)
def list_docker_hosts():
    hosts = DockerHost.query.order_by(DockerHost.name.asc()).all()

    breadcrumbs = [
        {"name": "Dashboard", "url": url_for('main.dashboard.index')},
        {"name": "Settings", "url": url_for('settings.get_list')},
        {"name": "Docker Hosts", "url": None},
    ]
    page_title = 'Docker hosts'

    return render_template('settings/docker_hosts/list.html',
                           breadcrumbs=breadcrumbs,
                           page_title=page_title,
                           hosts=hosts)

@settings.route('/docker-hosts/add', methods=['GET', 'POST'])
@permission(Permissions.GLOBAL_SETTINGS_VIEW)
def add_docker_host():
    form = DockerHostForm()

    if request.method == 'POST' and not current_user.has_permission(Permissions.GLOBAL_SETTINGS_EDIT):
        message = f'You do not have the necessary permission.'
        code = 403
        return render_template('error.html', message=message, code=code), code

    if form.validate_on_submit():
        # Simple uniqueness check for name before attempting to insert
        existing = DockerHost.query.filter_by(name=form.name.data.strip()).first()
        if existing:
            flash('A host with this name already exists.', 'error')
        else:
            try:
                DockerHost.add(
                    name=form.name.data.strip(),
                    url=form.url.data.strip(),
                )
                flash('Docker host added successfully!', 'success')
                return redirect(url_for('settings.list_docker_hosts'))
            except Exception as e:
                db.session.rollback()
                flash(f'Error adding docker host: {str(e)}', 'error')

    breadcrumbs = [
        {"name": "Dashboard", "url": url_for('main.dashboard.index')},
        {"name": "Settings", "url": url_for('settings.get_list')},
        {"name": "Docker Hosts", "url": url_for('settings.list_docker_hosts')},
        {"name": "Add", "url": None},
    ]
    page_title = 'Add docker host'

    return render_template('settings/docker_hosts/add.html',
                           breadcrumbs=breadcrumbs,
                           page_title=page_title,
                           form=form)

@settings.route('/docker-hosts/delete/<int:host_id>', methods=['POST'])
@permission(Permissions.GLOBAL_SETTINGS_EDIT)
def delete_docker_host(host_id):
    host = DockerHost.query.get_or_404(host_id)
    try:
        host.delete()
        return jsonify({'message': 'User deleted successfully.'}), 200
    except Exception as e:
        return jsonify({'message': 'Failed to delete user.'}), 500
    
@settings.route('/docker-hosts/edit/<int:host_id>', methods=['POST'])
@permission(Permissions.GLOBAL_SETTINGS_EDIT)
def edit_docker_host(host_id):
    host = DockerHost.query.get_or_404(host_id)
    data = request.json
    
    try:
        host.edit(
            name=data.get('name'),
            url=data.get('url'),
            enabled=data.get('enabled')
        )
        return jsonify({'message': 'Docker host updated successfully.'}), 200
    except Exception as e:
        return jsonify({'message': 'Failed to update docker host.'}), 500
    
@settings.route('/docker-hosts/check/<int:host_id>', methods=['GET'])
@permission(Permissions.GLOBAL_SETTINGS_VIEW)
def check_docker_host(host_id):
    host = DockerHost.query.get_or_404(host_id)
    try:
        response, status = docker.info(host)

        if status == 200:
            return jsonify({'message': 'Docker host is reachable.', 'version': response.json().get('ServerVersion')}), 200
        else:
            return jsonify({'message': 'Docker host is not reachable.'}), 500
    except Exception as e:
        return jsonify({'message': f'Error checking docker host connection.'}), 500