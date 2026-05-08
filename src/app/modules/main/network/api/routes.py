from flask import jsonify
from concurrent.futures import ThreadPoolExecutor, as_completed

from app.core.extensions import docker
from app.modules.user.models import Permissions
from app.modules.settings.models import DockerHost
from app.core.decorators import permission
from app.lib.common import bytes_to_human_readable
from app.lib.hosts import find_on_host

from . import api


@api.route('/<id>/delete', methods=['DELETE'])
@permission(Permissions.NETWORK_INFO)
def delete(id):
    host, _ = find_on_host(docker.inspect_network, id)
    if host is None:
        return 'Network not found', 404
    response, status_code = docker.delete_network(id, host=host)
    return str(response), status_code


@api.route('/prune', methods=['POST'])
@permission(Permissions.NETWORK_DELETE)
def prune():
    docker_hosts = DockerHost.query.filter_by(enabled=True).all()

    total_deleted = 0

    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(docker.prune_networks, host=host): host for host in docker_hosts}
        for future in as_completed(futures):
            response, status_code = future.result()
            if status_code in range(200, 300):
                networks_deleted_list = response.json().get('NetworksDeleted')
                total_deleted += len(networks_deleted_list) if networks_deleted_list else 0

    if total_deleted == 0:
        return jsonify({"message": "Nothing to prune"}), 200

    return jsonify({"message": f"Deleted {total_deleted} networks"}), 200
