from flask import render_template, url_for
from concurrent.futures import ThreadPoolExecutor, as_completed

import json

from app.modules.user.models import Permissions
from app.modules.settings.models import DockerHost
from app.core.decorators import permission
from app.lib.common import format_docker_timestamp, format_unix_timestamp

from app.core.extensions import docker

from . import image


def _find_image(image_id):
    """Return (host, response) from the first host that has the given image."""
    docker_hosts = DockerHost.query.filter_by(enabled=True).all()
    found_host = None
    found_response = None

    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(docker.inspect_image, image_id, host=host): host for host in docker_hosts}
        for future in as_completed(futures):
            resp, code = future.result()
            if code == 200 and found_host is None:
                found_host = futures[future]
                found_response = resp

    return found_host, found_response


def image_info(id):
    host, response = _find_image(id)

    if host is None:
        return "Image not found", 404

    image_details = response.json()

    general_info = {
        "id": id,
        "architecture": image_details["Architecture"],
        "docker_version": image_details["DockerVersion"],
        "os": image_details["Os"],
        "created_at": format_docker_timestamp(image_details["Created"]),
        "size": round(image_details["Size"] / 1024 / 1024, 2),
        "author": image_details.get("Author", ""),
        "comment": image_details.get("Comment", "")
    }

    env_vars = image_details["Config"].get("Env", [])
    labels = image_details["Config"].get("Labels", {})
    repo_tags = image_details.get("RepoTags", [])
    entrypoint = image_details["Config"].get("Entrypoint", [])
    cmd = image_details["Config"].get("Cmd", [])

    return {
        'general_info': general_info,
        'env_vars': env_vars,
        'labels': labels,
        'repo_tags': repo_tags,
        'entrypoint': entrypoint,
        'cmd': cmd
    }, 200


def image_name(id):
    response, status_code = image_info(id)
    if status_code in range(200, 300) and isinstance(response, dict) and response.get('repo_tags'):
        return response['repo_tags'][0]
    return "Unnamed Image"


@image.route('/list', methods=['GET'])
@permission(Permissions.IMAGE_VIEW_LIST)
def get_list():
    docker_hosts = DockerHost.query.filter_by(enabled=True).all()
    images = []

    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(docker.get_images, host=host): host for host in docker_hosts}
        for future in as_completed(futures):
            host = futures[future]
            response, status_code = future.result()
            if status_code in range(200, 300):
                data = response.json()
                for img in data:
                    img['Host'] = host.id
                images.extend(data)

    rows = []
    for img in images:
        row = {
            'id': img['Id'],
            'created': format_unix_timestamp(img['Created']),
            'repo_tags': ', '.join(img['RepoTags']) if img.get('RepoTags') else 'N/A',
            'size': round(img['Size'] / 1024 / 1024, 2)
        }
        rows.append(row)

    rows = sorted(rows, key=lambda x: x['repo_tags'], reverse=True)

    breadcrumbs = [
        {"name": "Dashboard", "url": url_for('main.dashboard.index')},
        {"name": "Images", "url": None},
    ]
    page_title = "Images List"
    return render_template('image/table.html', rows=rows, breadcrumbs=breadcrumbs, page_title=page_title)


@image.route('/<id>', methods=['GET'])
@permission(Permissions.IMAGE_INFO)
def info(id):
    response, status_code = image_info(id)
    if status_code not in range(200, 300):
        message = response.text if hasattr(response, 'text') else str(response)
        try:
            message = json.loads(message).get('message', message)
        except json.JSONDecodeError:
            pass
        return render_template('error.html', message=message, code=status_code), status_code

    breadcrumbs = [
        {"name": "Dashboard", "url": url_for('main.dashboard.index')},
        {"name": "Images", "url": url_for('main.image.get_list')},
        {"name": image_name(id), "url": None},
    ]
    page_title = 'Image Details'

    return render_template('image/info.html', image=response, breadcrumbs=breadcrumbs, page_title=page_title)