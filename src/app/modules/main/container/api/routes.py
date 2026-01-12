from flask import jsonify, request

from app.core.extensions import docker
from app.modules.user.models import Permissions
from app.modules.settings.models import DockerHost
from app.core.decorators import permission
from app.lib.common import bytes_to_human_readable

from . import api

@api.route('/<id>/restart', methods=['POST'])
@permission(Permissions.CONTAINER_RESTART)
def restart(id):
    respone, status_code = docker.restart_container(id)
    return str(respone), status_code

@api.route('/<id>/start', methods=['POST'])
@permission(Permissions.CONTAINER_START)
def start(id):
    response, status_code = docker.start_container(id)
    return str(response), status_code

@api.route('/<id>/stop', methods=['POST'])
@permission(Permissions.CONTAINER_STOP)
def stop(id):
    response, status_code = docker.stop_container(id)
    return str(response), status_code

@api.route('/<id>/delete', methods=['DELETE'])
@permission(Permissions.CONTAINER_DELETE)
def delete(id):
    response, status_code = docker.delete_container(id)
    return str(response), status_code

@api.route('/prune', methods=['POST'])
@permission(Permissions.CONTAINER_DELETE)
def prune():
    selected_docker_hosts_ids = [int(d.strip()) for d in request.args.get('docker_host', '').split(',')] if request.args.get('docker_host') else []

    docker_hosts = DockerHost.query.filter_by(enabled=True).all()
    filtered_hosts = []
    if selected_docker_hosts_ids:
        filtered_hosts = [h for h in docker_hosts if h.id in selected_docker_hosts_ids]
    else:
        filtered_hosts = docker_hosts

    total_deleted_count = 0
    total_space_reclaimed = 0

    for host in filtered_hosts:
        response, status_code = docker.prune_containers(host=host)
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
