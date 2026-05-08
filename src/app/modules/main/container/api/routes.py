from flask import jsonify, request
from concurrent.futures import ThreadPoolExecutor, as_completed

from app.core.extensions import docker
from app.modules.user.models import Permissions
from app.modules.settings.models import DockerHost
from app.core.decorators import permission
from app.lib.common import bytes_to_human_readable
from app.lib.hosts import find_on_host

from . import api


@api.route('/<id>/restart', methods=['POST'])
@permission(Permissions.CONTAINER_RESTART)
def restart(id):
    host, _ = find_on_host(docker.inspect_container, id)
    if host is None:
        return 'Container not found', 404
    response, status_code = docker.restart_container(id, host=host)
    return str(response), status_code


@api.route('/<id>/start', methods=['POST'])
@permission(Permissions.CONTAINER_START)
def start(id):
    host, _ = find_on_host(docker.inspect_container, id)
    if host is None:
        return 'Container not found', 404
    response, status_code = docker.start_container(id, host=host)
    return str(response), status_code


@api.route('/<id>/stop', methods=['POST'])
@permission(Permissions.CONTAINER_STOP)
def stop(id):
    host, _ = find_on_host(docker.inspect_container, id)
    if host is None:
        return 'Container not found', 404
    response, status_code = docker.stop_container(id, host=host)
    return str(response), status_code


@api.route('/<id>/delete', methods=['DELETE'])
@permission(Permissions.CONTAINER_DELETE)
def delete(id):
    host, _ = find_on_host(docker.inspect_container, id)
    if host is None:
        return 'Container not found', 404
    response, status_code = docker.delete_container(id, host=host)
    return str(response), status_code


@api.route('/prune', methods=['POST'])
@permission(Permissions.CONTAINER_DELETE)
def prune():
    selected_docker_hosts_ids = [int(d.strip()) for d in request.args.get('docker_host', '').split(',')] if request.args.get('docker_host') else []

    docker_hosts = DockerHost.query.filter_by(enabled=True).all()
    hosts_to_prune = [h for h in docker_hosts if not selected_docker_hosts_ids or h.id in selected_docker_hosts_ids]

    total_deleted_count = 0
    total_space_reclaimed = 0

    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(docker.prune_containers, host=host): host for host in hosts_to_prune}
        for future in as_completed(futures):
            response, status_code = future.result()
            if status_code in range(200, 300):
                result = response.json()
                containers_deleted = result.get('ContainersDeleted')
                if containers_deleted:
                    total_deleted_count += len(containers_deleted)
                total_space_reclaimed += result.get('SpaceReclaimed', 0)

    if total_deleted_count == 0:
        return jsonify({"message": "Nothing to prune"}), 200

    message = f"Deleted {total_deleted_count} containers, reclaimed {bytes_to_human_readable(total_space_reclaimed)}"
    return jsonify({"message": message}), 200
