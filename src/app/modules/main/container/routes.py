from flask import render_template, url_for, request, jsonify
from flask_login import current_user
from flask_socketio import emit

import json

from app.core.extensions import docker
from app.lib.common import format_docker_timestamp, format_unix_timestamp

from app.modules.user.models import Permissions, PersonalSettings
from app.core.decorators import permission

from app.core.extensions import socketio

from . import container

def container_info (id):
    response, status_code = docker.inspect_container(id)
    container_details = []
    if status_code not in range(200, 300):
        return response, status_code
    else:
        container_details = response.json()

    general_info = {
        "id": container_details["Id"],
        "name": container_details["Name"].strip("/"),
        "status": container_details["State"]["Status"],
        "created_at": format_docker_timestamp(container_details['Created']),
        "restart_policy": container_details["HostConfig"]["RestartPolicy"]["Name"]
    }

    image = {
        "id": container_details["Image"],
        "name": container_details["Config"]["Image"]
    }

    env_vars = container_details["Config"].get("Env", [])

    labels = container_details["Config"].get("Labels", {})

    container_info = {
        'general_info': general_info,
        'image': image,
        'env_vars': env_vars,
        'labels': labels,
        'volumes': [{
            'host_path': mount['Source'],
            'container_path': mount['Destination']
        } for mount in container_details['Mounts']],
        'network_info': [{
            'id': network['NetworkID'],
            'network_name': net,
            'self_ip': network['IPAddress'],
            'exposed_ports': container_details['NetworkSettings']['Ports']
        } for net, network in container_details['NetworkSettings']['Networks'].items()]
    }

    return container_info, 200

def container_name (id):
    response, status_code = container_info(id)
    return response['general_info']['name'] if status_code in range(200, 300) else "Unknown Container"

@container.route('/list', methods=['GET'])
@permission(Permissions.CONTAINER_VIEW_LIST)
def get_list():
    response, status_code = docker.get_containers()
    containers = []
    if status_code not in range(200, 300):
        message = response.text if hasattr(response, 'text') else str(response)
        try:
            message = json.loads(message).get('message', message)
        except json.JSONDecodeError:
            pass
        return render_template('error.html', message=message, code=status_code), status_code

    else:
        containers = response.json()

    container_columns_setting = PersonalSettings.get_setting(current_user.id, 'container_list_columns', json_format=True)
    container_quick_actions_setting = PersonalSettings.get_setting(current_user.id, 'container_list_quick_actions', json_format=True)

    # return containers

    rows = []
    composes = set()
    if containers is not None:
        for container in containers:
            compose_param = request.args.get('compose')
            labels = container["Labels"]
            # Collect compose projects
            if "com.docker.compose.project" in labels:
                composes.add(labels["com.docker.compose.project"])
            
            is_part_of_compose = "com.docker.compose.project" in labels
            container_compose = labels.get("com.docker.compose.project")
            
            # Filter by compose project
            if compose_param:
                compose_filters = [c.strip() for c in compose_param.split(',')]
                
                matches = False
                
                if "none" in compose_filters and not is_part_of_compose:
                    # Container is standalone and "none" is selected
                    matches = True
                
                if is_part_of_compose and container_compose in compose_filters:
                    # Container belongs to a selected compose project
                    matches = True
                
                if not matches:
                    continue
            
            row = {
                'id': container.get('Id', 'Unknown'),
                'name': container.get('Names', ['Unknown'])[0].strip('/') if container.get('Names') else 'Unknown',
                'status': container.get('Status', 'Unknown'),
                'created': format_unix_timestamp(container.get('Created', '0')),
                'state': container.get('State', 'Unknown'),
                'image': container.get('Image', 'Unknown'),
                'imageID': container.get('ImageID', 'Unknown'),
                'ports': [
                    f"{port.get('PrivatePort', 'Unknown')} -> {port.get('PublicPort', 'Unknown')}" 
                    for port in container.get('Ports', []) 
                    if all(key in port for key in ['PrivatePort', 'PublicPort', 'IP']) and port.get('IP') != '::'
                ] if container.get('Ports') else [],
            }
            rows.append(row)

    rows = sorted(rows, key=lambda x: x['name'], reverse=True)

    breadcrumbs = [
        {"name": "Dashboard", "url": url_for('main.dashboard.index')},
        {"name": "Containers", "url": None},
    ]
    page_title = "Container List"

    return render_template('container/table.html', 
                           rows=rows, 
                           composes=composes, 
                           container_columns_setting=container_columns_setting,
                           container_quick_actions_setting=container_quick_actions_setting,
                           breadcrumbs=breadcrumbs, 
                           page_title=page_title)

@container.route('/list/settings', methods=['GET', 'POST'])
def column_settings():
    if request.method == 'GET':
        container_list_columns = PersonalSettings.get_setting(current_user.id, 'container_list_columns', json_format=True)
        container_list_quick_actions = PersonalSettings.get_setting(current_user.id, 'container_list_quick_actions', json_format=True)
    
        return render_template('container/list_settings.html', container_list_columns=container_list_columns, container_list_quick_actions=container_list_quick_actions)
    
    elif request.method == 'POST':
        data = request.get_json(force=True)

        if not isinstance(data, dict):
            return jsonify({"success": False, "error": "Invalid data format"}), 400

        columns = data.get('columns')
        quick_actions = data.get('quick_actions')

        if columns is not None:
            if not isinstance(columns, list):
                return jsonify({"success": False, "error": "Invalid columns format"}), 400

        if quick_actions is not None:
            if not isinstance(quick_actions, list):
                return jsonify({"success": False, "error": "Invalid quick actions format"}), 400

        PersonalSettings.set_setting(
            current_user.id,
            'container_list_columns',
            columns if columns is not None else PersonalSettings.defaults['container_list_columns']['default'],
            json_format=True
        )
        PersonalSettings.set_setting(
            current_user.id,
            'container_list_quick_actions',
            quick_actions if quick_actions is not None else PersonalSettings.defaults['container_list_quick_actions']['default'],
            json_format=True
        )

        return jsonify({"success": True})

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
    response, status_code = docker.get_logs(id, tail=tail)
    logs = []
    if status_code not in range(200, 300):
        message = response.text if hasattr(response, 'text') else str(response)
        try:
            message = json.loads(message).get('message', message)
        except json.JSONDecodeError:
            pass
        return render_template('error.html', message=message, code=status_code), status_code
    else:
        logs = response

    log_text = ''.join(log['message'] for log in logs)
    
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
    response, status_code = docker.get_processes(id)
    processes = []
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
    else:
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

@socketio.on('start_session')
def handle_start_session(data):
    container_id = data['container_id']
    cmd = data['command'].split()
    user = data['user']
    console_size = data['consoleSize']
    sid = request.sid

    exec_create_endpoint = f"/containers/{container_id}/exec"
    payload = {"AttachStdin": True, "AttachStdout": True, "AttachStderr": True, "Tty": True, "Cmd": cmd, "User": user}

    exec_id = docker.create_exec(exec_create_endpoint, payload=payload)

    if exec_id is None:
        emit('output', {'data': 'Could not create exec session. Check if container is running.\r\n'})
        return

    emit('exec_id', {'execId': exec_id}, to=sid)

    socketio.start_background_task(target=docker.start_exec_session, 
                                    exec_id=exec_id,
                                    sid=sid,
                                    socketio=socketio,
                                    console_size=console_size)
@socketio.on('input')
def handle_command(data):
    command = data['command']
    sid = request.sid  # Using flask.request for session ID

    response = docker.handle_command(command, sid)
    if response:
        emit('output', {'data': response})

@socketio.on('resize_session')
def handle_resize_session(data):
    exec_id = data['exec_id']
    cols = data['cols']
    rows = data['rows']

    resize_exec_endpoint = f"/exec/{exec_id}/resize?h={rows}&w={cols}"

    response, status_code = docker.perform_request(path=resize_exec_endpoint, method='POST')