from flask import render_template, url_for, request, jsonify
from flask_login import current_user

from app.modules.user.models import Permissions, PersonalSettings
from app.core.decorators import permission
from app.modules.settings.models import DockerHost
from app.core.extensions import docker
from app.lib.common import format_unix_timestamp
from app.modules.main.container import container
from app.modules.main.container.helpers import container_info, container_name, get_container_host

@container.route('/list', methods=['GET'])
@permission(Permissions.CONTAINER_VIEW_LIST)
def get_list():
    selected_composes = [c.strip() for c in request.args.get('compose', '').split(',')] if request.args.get('compose') else []
    selected_docker_hosts_ids = [int(d.strip()) for d in request.args.get('docker_host', '').split(',')] if request.args.get('docker_host') else []

    docker_hosts = DockerHost.query.filter_by(enabled=True).all()
    hosts_to_query = [h for h in docker_hosts if not selected_docker_hosts_ids or h.id in selected_docker_hosts_ids]
    containers = []
    successful_hosts = []

    from concurrent.futures import ThreadPoolExecutor, as_completed
    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(docker.get_containers, host=host): host for host in hosts_to_query}
        for future in as_completed(futures):
            host = futures[future]
            response, status_code = future.result()
            if status_code in range(200, 300):
                data = response.json()
                for c in data:
                    c['Host'] = host.id
                containers.extend(data)
                successful_hosts.append(host)

    docker_hosts = successful_hosts

    container_columns_setting = PersonalSettings.get_setting(current_user.id, 'container_list_columns', json_format=True)
    container_quick_actions_setting = PersonalSettings.get_setting(current_user.id, 'container_list_quick_actions', json_format=True)

    rows = []
    composes = set()
    if containers is not None:
        for container in containers:
            labels = container["Labels"]
            # Collect compose projects
            if "com.docker.compose.project" in labels:
                composes.add(labels["com.docker.compose.project"])
            
            is_part_of_compose = "com.docker.compose.project" in labels
            container_compose = labels.get("com.docker.compose.project")
            
            # Filter by compose project
            if selected_composes:
                matches = False
                
                if "none" in selected_composes and not is_part_of_compose:
                    # Container is standalone and "none" is selected
                    matches = True
                
                if is_part_of_compose and container_compose in selected_composes:
                    # Container belongs to a selected compose project
                    matches = True
                
                if not matches:
                    docker_hosts = [h for h in docker_hosts if h.id != container.get('Host')]
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
                        selected_composes=selected_composes,
                        docker_hosts=docker_hosts,
                        selected_docker_hosts_ids=selected_docker_hosts_ids,
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
