from flask import jsonify
from concurrent.futures import ThreadPoolExecutor, as_completed

import json

from app.core.extensions import docker
from app.modules.user.models import Permissions
from app.modules.settings.models import DockerHost
from app.core.decorators import permission
from app.lib.common import bytes_to_human_readable
from app.lib.hosts import find_on_host

from . import api


@api.route('/<id>/delete', methods=['DELETE'])
@permission(Permissions.IMAGE_INFO)
def delete(id):
    host, _ = find_on_host(docker.inspect_image, id)
    if host is None:
        return 'Image not found', 404
    response, status_code = docker.delete_image(id, host=host)
    return str(response), status_code


@api.route('/prune', methods=['POST'])
@permission(Permissions.IMAGE_DELETE)
def prune():
    docker_hosts = DockerHost.query.filter_by(enabled=True).all()
    filters = {"dangling": ["false"]}
    params = {"filters": json.dumps(filters)}

    total_deleted = 0
    total_space_reclaimed = 0

    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(docker.prune_images, params=params, host=host): host for host in docker_hosts}
        for future in as_completed(futures):
            response, status_code = future.result()
            if status_code in range(200, 300):
                images_deleted_list = response.json().get('ImagesDeleted')
                total_deleted += len(images_deleted_list) if images_deleted_list else 0
                total_space_reclaimed += response.json().get('SpaceReclaimed', 0)

    if total_deleted == 0:
        return jsonify({"message": "Nothing to prune"}), 200

    message = f"Deleted {total_deleted} images, reclaimed {bytes_to_human_readable(total_space_reclaimed)}"
    return jsonify({"message": message}), 200
