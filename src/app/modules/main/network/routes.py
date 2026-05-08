from flask import render_template, url_for
from concurrent.futures import ThreadPoolExecutor, as_completed

import json

from app.core.extensions import docker
from app.lib.common import format_docker_timestamp
from app.lib.hosts import find_on_host
from app.modules.settings.models import DockerHost

from app.core.decorators import permission
from app.modules.user.models import Permissions

from . import network


def network_info(id):
    host, response = find_on_host(docker.inspect_network, id)

    if host is None:
        return "Network not found", 404

    network_details = response.json()

    net = {
        'Name': network_details["Name"],
        'Id': network_details["Id"],
        'Created': format_docker_timestamp(network_details["Created"]),
        'Scope': network_details["Scope"],
        'Driver': network_details["Driver"],
        'EnableIPv6': network_details["EnableIPv6"],
        'Internal': network_details["Internal"],
        'Attachable': network_details["Attachable"],
        'Ingress': network_details["Ingress"],
        'Containers': network_details.get("Containers", {}),
        'Labels': network_details.get("Labels", {}),
        'IPAM': [],
    }

    subnets_gateways = []
    if 'IPAM' in network_details and network_details['IPAM']['Config']:
        for config in network_details['IPAM']['Config']:
            subnets_gateways.append((config.get('Subnet'), config.get('Gateway')))
    net['IPAM'] = subnets_gateways

    return net, 200


@network.route('/list', methods=['GET'])
@permission(Permissions.NETWORK_VIEW_LIST)
def get_list():
    docker_hosts = DockerHost.query.filter_by(enabled=True).all()
    networks = []

    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(docker.get_networks, host=host): host for host in docker_hosts}
        for future in as_completed(futures):
            host = futures[future]
            response, status_code = future.result()
            if status_code in range(200, 300):
                data = response.json()
                for n in data:
                    n['Host'] = host.id
                networks.extend(data)

    rows = []
    for net in networks:
        rows.append({
            'id': net['Id'],
            'name': net['Name'],
            'driver': net['Driver'],
            'subnet': net['IPAM']['Config'][0]['Subnet'] if net['IPAM']['Config'] else 'N/A',
            'gateway': net['IPAM']['Config'][0]['Gateway'] if net['IPAM']['Config'] else 'N/A',
        })

    rows = sorted(rows, key=lambda x: x['name'], reverse=True)

    breadcrumbs = [
        {"name": "Dashboard", "url": url_for('main.dashboard.index')},
        {"name": "Networks", "url": None},
    ]
    page_title = "Networks List"
    return render_template('network/table.html', rows=rows, breadcrumbs=breadcrumbs, page_title=page_title)


@network.route('/<id>', methods=['GET'])
@permission(Permissions.NETWORK_INFO)
def info(id):
    response, status_code = network_info(id)
    if status_code not in range(200, 300):
        message = response.text if hasattr(response, 'text') else str(response)
        try:
            message = json.loads(message).get('message', message)
        except json.JSONDecodeError:
            pass
        return render_template('error.html', message=message, code=status_code), status_code

    breadcrumbs = [
        {"name": "Dashboard", "url": url_for('main.dashboard.index')},
        {"name": "Networks", "url": url_for('main.network.get_list')},
        {"name": response['Name'], "url": None},
    ]
    page_title = 'Network Details'

    return render_template('network/info.html', network=response, breadcrumbs=breadcrumbs, page_title=page_title)


@network.route('/<id>/delete', methods=['DELETE'])
@permission(Permissions.NETWORK_DELETE)
def delete(id):
    host, _ = find_on_host(docker.inspect_network, id)
    if host is None:
        return 'Network not found', 404
    response, status_code = docker.delete_network(id, host=host)
    return str(response), status_code