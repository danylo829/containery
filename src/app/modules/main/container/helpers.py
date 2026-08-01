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

    if host is None or response is None:
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
        info = response.get('general_info')
        if isinstance(info, dict):
            return info.get('name', "Unknown Container")
    return "Unknown Container"


def get_container_host(container_id):
    host, _ = _find_container(container_id)
    return host


def is_self_container(container_id):
    import os
    import socket

    if not container_id:
        return False

    cid_str = str(container_id).strip().lower().lstrip('/')

    self_ids = set()
    try:
        hn = socket.gethostname().strip().lower()
        if hn:
            self_ids.add(hn)
    except Exception:
        pass

    env_hn = os.getenv('HOSTNAME', '').strip().lower()
    if env_hn:
        self_ids.add(env_hn)

    try:
        if os.path.exists('/etc/hostname'):
            with open('/etc/hostname', 'r') as f:
                h = f.read().strip().lower()
                if h:
                    self_ids.add(h)
    except Exception:
        pass

    try:
        if os.path.exists('/proc/self/mountinfo'):
            with open('/proc/self/mountinfo', 'r') as f:
                for line in f:
                    if '/docker/containers/' in line:
                        parts = line.split('/docker/containers/')
                        if len(parts) > 1:
                            c_full = parts[1].split('/')[0].strip().lower()
                            if c_full:
                                self_ids.add(c_full)
    except Exception:
        pass

    self_ids.add('containery')

    if cid_str in self_ids:
        return True

    for sid in self_ids:
        if len(sid) >= 12 and (cid_str.startswith(sid) or sid.startswith(cid_str)):
            return True

    host, response = _find_container(container_id)
    if host and response and getattr(response, 'status_code', None) == 200:
        try:
            details = response.json()
            full_id = details.get('Id', '').lower()
            name = details.get('Name', '').lstrip('/').lower()
            hostname = details.get('Config', {}).get('Hostname', '').lower()

            if name in self_ids or hostname in self_ids or full_id in self_ids:
                return True

            for sid in self_ids:
                if len(sid) >= 12 and (full_id.startswith(sid) or sid.startswith(full_id)):
                    return True
        except Exception:
            pass

    return False

