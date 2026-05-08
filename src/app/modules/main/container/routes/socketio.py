from flask import request
from flask_socketio import emit
from app.core.extensions import socketio, docker
from app.modules.main.container.helpers import get_container_host

@socketio.on('start_session')
def handle_start_session(data):
    container_id = data.get('container_id')
    command = data.get('command')
    user = data.get('user', '')
    console_size = data.get('consoleSize')
    sid = request.sid

    if not container_id or not command:
        emit('output', {'data': 'Invalid session data.\r\n'})
        return

    host = get_container_host(container_id)
    if host is None:
        emit('output', {'data': 'Could not find a host for this container.\r\n'})
        return

    exec_create_endpoint = f"/containers/{container_id}/exec"
    payload = {"AttachStdin": True, "AttachStdout": True, "AttachStderr": True, "Tty": True, "Cmd": command.split(), "User": user}

    exec_id = docker.create_exec(exec_create_endpoint, payload=payload, host=host)

    if exec_id is None:
        emit('output', {'data': 'Could not create exec session. Check if container is running.\r\n'})
        return

    emit('exec_id', {'execId': exec_id}, to=sid)

    socketio.start_background_task(target=docker.start_exec_session,
                                   exec_id=exec_id,
                                   sid=sid,
                                   socketio=socketio,
                                   host=host,
                                   console_size=console_size)

@socketio.on('input')
def handle_command(data):
    command = data.get('command')
    if not command:
        return
    sid = request.sid

    response = docker.handle_command(command, sid)
    if response:
        emit('output', {'data': response})

@socketio.on('resize_session')
def handle_resize_session(data):
    exec_id = data.get('exec_id')
    cols = data.get('cols')
    rows = data.get('rows')
    sid = request.sid

    if not all([exec_id, cols, rows]):
        return

    docker.resize_exec(sid, exec_id, cols, rows)

@socketio.on('disconnect')
def handle_disconnect():
    sid = request.sid
    docker.cleanup_session(sid)
