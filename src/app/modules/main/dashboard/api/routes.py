from flask import jsonify, session
from concurrent.futures import ThreadPoolExecutor, as_completed

from app.core.extensions import docker
from app.modules.settings.models import DockerHost
from app.lib.common import bytes_to_human_readable

import psutil
import json

from . import api


@api.route('/usage', methods=['GET'])
def get_usage():
    cpu_usage = psutil.cpu_percent(interval=1)

    ram_usage_percent = psutil.virtual_memory().percent
    ram_usage_absolute = round((psutil.virtual_memory().used / 1024 / 1024 / 1024), 2)
    ram_total = round((psutil.virtual_memory().total / 1024 / 1024 / 1024), 2)

    # Load average
    load_average = psutil.getloadavg()  # Returns a tuple (1min, 5min, 15min)

    return jsonify(
        cpu=cpu_usage,
        ram_percent=ram_usage_percent,
        ram_absolute=ram_usage_absolute,
        ram_total=ram_total,
        load_average=load_average
    )


@api.route('/dismiss-update-notification', methods=['POST'])
def dismiss_update_notification():
    session['dismiss_update_notification'] = True
    return jsonify({'success': True}), 200


@api.route('/prune', methods=['POST'])
def prune():
    docker_hosts = DockerHost.query.filter_by(enabled=True).all()
    filters = {"dangling": ["false"]}
    params = {"filters": json.dumps(filters)}

    prune_ops = [
        ('containers', lambda host: docker.prune_containers(host=host), 'SpaceReclaimed'),
        ('images', lambda host: docker.prune_images(params=params, host=host), 'SpaceReclaimed'),
        ('volumes', lambda host: docker.prune_volumes(host=host), 'SpaceReclaimed'),
        ('networks', lambda host: docker.prune_networks(host=host), None),
        ('build_cache', lambda host: docker.prune_build_cache(host=host), 'SpaceReclaimed'),
    ]

    reclaimed_space = 0

    for label, op, space_key in prune_ops:
        with ThreadPoolExecutor() as executor:
            futures = {executor.submit(op, host): host for host in docker_hosts}
            for future in as_completed(futures):
                response, status_code = future.result()
                if status_code not in range(200, 300):
                    return jsonify({'message': f'Failed to prune {label}'}), status_code
                if space_key:
                    reclaimed_space += response.json().get(space_key, 0)

    message = f"Reclaimed {bytes_to_human_readable(reclaimed_space)} of disk space."
    return jsonify({'message': message}), 200