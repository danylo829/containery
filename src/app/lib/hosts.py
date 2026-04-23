from concurrent.futures import ThreadPoolExecutor, as_completed

from app.modules.settings.models import DockerHost


def find_on_host(inspect_fn, resource_id):
    """Fan out inspect_fn(resource_id, host=host) across all enabled hosts.

    Returns (host, response) for the first host that responds with HTTP 200,
    or (None, None) if no host has the resource.
    """
    docker_hosts = DockerHost.query.filter_by(enabled=True).all()
    found_host = None
    found_response = None

    executor = ThreadPoolExecutor()
    futures = {executor.submit(inspect_fn, resource_id, host=host): host for host in docker_hosts}
    try:
        for future in as_completed(futures):
            resp, code = future.result()
            if code == 200:
                found_host = futures[future]
                found_response = resp
                break
    finally:
        executor.shutdown(wait=False)

    return found_host, found_response
