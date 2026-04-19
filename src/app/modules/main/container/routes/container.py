from flask import render_template, url_for, request

from app.modules.user.models import Permissions
from app.core.decorators import permission
from app.core.extensions import docker
from app.modules.main.container import container
from app.modules.main.container.helpers import container_info, container_name, get_container_host

import json

@container.route('/<id>', methods=['GET'])
@permission(Permissions.CONTAINER_INFO)
def info(id):
    response, status_code = container_info(id)
    container = []
    if status_code not in range(200, 300):
        message = response.text if hasattr(response, 'text') else str(response)
        try:
            message = json.loads(message).get('message', message)
        except json.JSONDecodeError:
            pass
        return render_template('error.html', message=message, code=status_code), status_code
    else:
        container = response

    breadcrumbs = [
        {"name": "Dashboard", "url": url_for('main.dashboard.index')},
        {"name": "Containers", "url": url_for('main.container.get_list')},
        {"name": container_name(id), "url": None},
    ]
    page_title = 'Container Details'

    return render_template('container/info.html', container=container, breadcrumbs=breadcrumbs, page_title=page_title)


@container.route('/<id>/logs', methods=['GET'])
@permission(Permissions.CONTAINER_INFO)
def logs(id):
    tail = request.args.get('tail', '100')
    if int(tail) < 0:
        tail = '100'

    host = get_container_host(id)
    if host is None:
        return render_template('error.html', message='Container not found', code=404), 404

    response, status_code = docker.get_logs(id, tail=tail, host=host)
    if status_code not in range(200, 300):
        message = response.text if hasattr(response, 'text') else str(response)
        try:
            message = json.loads(message).get('message', message)
        except json.JSONDecodeError:
            pass
        return render_template('error.html', message=message, code=status_code), status_code

    log_text = ''.join(log['message'] for log in response)

    breadcrumbs = [
        {"name": "Dashboard", "url": url_for('main.dashboard.index')},
        {"name": "Containers", "url": url_for('main.container.get_list')},
        {"name": container_name(id), "url": url_for('main.container.info', id=id)},
        {"name": "Logs", "url": None},
    ]
    page_title = 'Container Logs'

    return render_template('container/logs.html', tail=tail, log_text=log_text, breadcrumbs=breadcrumbs, page_title=page_title)


@container.route('/<id>/processes', methods=['GET'])
@permission(Permissions.CONTAINER_INFO)
def processes(id):
    host = get_container_host(id)
    if host is None:
        return render_template('error.html', message='Container not found', code=404), 404

    response, status_code = docker.get_processes(id, host=host)
    if status_code not in range(200, 300):
        # Custom error messages
        if status_code == 409:
            id = response.json()['message'].split(' ')[1]
            name = container_name(id)
            message = f'Container {name} is not running'
        # Default error message
        else:
            message = response.text if hasattr(response, 'text') else str(response)
        try:
            message = json.loads(message).get('message', message)
        except json.JSONDecodeError:
            pass
        return render_template('error.html', message=message, code=status_code), status_code

    processes = response.json()

    breadcrumbs = [
        {"name": "Dashboard", "url": url_for('main.dashboard.index')},
        {"name": "Containers", "url": url_for('main.container.get_list')},
        {"name": container_name(id), "url": url_for('main.container.info', id=id)},
        {"name": "Processes", "url": None},
    ]
    page_title = f'{container_name(id)} processes'

    return render_template('container/processes.html', processes=processes, breadcrumbs=breadcrumbs, page_title=page_title)


@container.route('/<id>/terminal', methods=['GET'])
@permission(Permissions.CONTAINER_EXEC)
def terminal(id):
    breadcrumbs = [
        {"name": "Dashboard", "url": url_for('main.dashboard.index')},
        {"name": "Containers", "url": url_for('main.container.get_list')},
        {"name": container_name(id), "url": url_for('main.container.info', id=id)},
        {"name": "Terminal", "url": None},
    ]
    page_title = 'Container terminal'

    return render_template('container/terminal.html', container_id=id, breadcrumbs=breadcrumbs, page_title=page_title)
