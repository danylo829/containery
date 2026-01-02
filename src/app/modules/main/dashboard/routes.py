from flask import render_template

import json

from app.core.extensions import docker
from app.modules.settings.models import DockerHost
from app.config import Config

import app.modules.main.dashboard.utils as utils
from . import dashboard

@dashboard.route('/', methods=['GET'])
def index():
    docker_host = DockerHost.query.filter_by(enabled=True).first()
    response, status_code = docker.info(host=docker_host)
    info = []
    if status_code not in range(200, 300):
        message = response.text if hasattr(response, 'text') else str(response)
        try:
            message = json.loads(message).get('message', message)
        except json.JSONDecodeError:
            pass
        return render_template('error.html', message=message, code=status_code), status_code
    else:
        info = response.json()

    latest_version, show_update_notification = utils.check_for_update()

    page_title = "Dashboard"
    return render_template(
        'dashboard.html',
        info=info,
        docker_host_name=docker_host.name if docker_host else "Default",
        page_title=page_title,
        show_update_notification=show_update_notification,
        latest_version=latest_version,
        installed_version=Config.VERSION
    )

@dashboard.route('/info', methods=['GET'])
def info():
    response, status_code = docker.info()
    response_df, status_code_df = docker.df()
    info = []
    df = []
    if status_code not in range(200, 300):
        message = response.text if hasattr(response, 'text') else str(response)
        try:
            message = json.loads(message).get('message', message)
        except json.JSONDecodeError:
            pass
        return render_template('error.html', message=message, code=status_code), status_code
    else:
        info = response.json()

    if status_code_df in range(200, 300):
        df = response_df.json()

    page_title = "Dashboard"
    breadcrumbs = [
        {'name': 'Dashboard', 'url': '/'},
        {'name': 'Info', 'url': ''}
    ]
    return render_template('info.html', page_title=page_title, info=info, df=df, breadcrumbs=breadcrumbs)