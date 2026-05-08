from flask import render_template, url_for
from concurrent.futures import ThreadPoolExecutor, as_completed

import json

from app.core.extensions import docker
from app.lib.common import format_docker_timestamp
from app.lib.hosts import find_on_host
from app.modules.settings.models import DockerHost

from app.core.decorators import permission
from app.modules.user.models import Permissions

from . import volume


@volume.route('/list', methods=['GET'])
@permission(Permissions.VOLUME_VIEW_LIST)
def get_list():
    docker_hosts = DockerHost.query.filter_by(enabled=True).all()
    volumes = []

    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(docker.get_volumes, host=host): host for host in docker_hosts}
        for future in as_completed(futures):
            host = futures[future]
            response, status_code = future.result()
            if status_code in range(200, 300):
                data = response.json().get('Volumes', [])
                for v in data:
                    v['Host'] = host.id
                volumes.extend(data)

    rows = []
    for vol in volumes:
        rows.append({
            'name': vol['Name'],
            'mountpoint': vol['Mountpoint'],
        })

    rows = sorted(rows, key=lambda x: x['name'], reverse=True)

    breadcrumbs = [
        {"name": "Dashboard", "url": url_for('main.dashboard.index')},
        {"name": "Volumes", "url": None},
    ]
    page_title = "Volumes List"
    return render_template('volume/table.html', rows=rows, breadcrumbs=breadcrumbs, page_title=page_title)


@volume.route('/<name>', methods=['GET'])
@permission(Permissions.VOLUME_INFO)
def info(name):
    host, response = find_on_host(docker.inspect_volume, name)

    if host is None:
        return render_template('error.html', message='Volume not found', code=404), 404

    vol = response.json()

    breadcrumbs = [
        {"name": "Dashboard", "url": url_for('main.dashboard.index')},
        {"name": "Volumes", "url": url_for('main.volume.get_list')},
        {"name": vol['Name'], "url": None},
    ]
    page_title = 'Volume Details'

    return render_template('volume/info.html', volume=vol, breadcrumbs=breadcrumbs, page_title=page_title, format_docker_timestamp=format_docker_timestamp)