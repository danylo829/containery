from concurrent.futures import ThreadPoolExecutor, as_completed

from app.modules.settings.models import DockerHost
from app.core.extensions import docker
from app.lib.common import format_docker_timestamp

def _find_container(container_id):
    """Return (host, response) from the first host that has the given container."""

    docker_hosts = DockerHost.query.filter_by(enabled=True).all()
    found_host = None
    found_response = None

    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(docker.inspect_container, container_id, host=host): host for host in docker_hosts}
        for future in as_completed(futures):
            resp, code = future.result()
            if code == 200 and found_host is None:
                found_host = futures[future]
                found_response = resp

    return found_host, found_response


def container_info(id):
    host, response = _find_container(id)

    if host is None:
        return "Container not found", 404

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

    return {
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
    }, 200


def container_name(id):
    response, status_code = container_info(id)
    if status_code in range(200, 300) and isinstance(response, dict):
        return response.get('general_info', {}).get('name', "Unknown Container")
    return "Unknown Container"


def get_container_host(container_id):
    host, _ = _find_container(container_id)
    return host
