import json
import socket
import requests_unixsocket

class Docker:
    def __init__(self):
        self.exec_sessions = {}

    def init_app(self, app):
        self.socket_path = app.config.get("DOCKER_SOCKET_PATH")
        self.encoded_socket_path = app.config.get("DOCKER_SOCKET_PATH").replace('/', '%2F')

    # GENERAL
    def perform_request(self, path, method='GET', payload=None, params=None) -> tuple:
        url = f'http+unix://{self.encoded_socket_path}{path}'
        session = requests_unixsocket.Session()

        try:
            if method == 'GET':
                response = session.get(url, params=params)
            elif method == 'DELETE':
                response = session.delete(url, params=params)
            elif method == 'POST':
                response = session.post(url, json=payload, params=params)
            else:
                return f"Unsupported HTTP method: {method}", 400

            return response, response.status_code

        except Exception as e:
            return str(e), 500

    
    # EXEC

    def create_exec(self, endpoint, payload):
        """Create an exec instance and return its ID."""
        response, status_code = self.perform_request(endpoint, method='POST', payload=payload)
        if status_code in range(200, 300):
            exec_instance_json = response.json()
            return exec_instance_json.get("Id")
        return None

    def start_exec_session(self, exec_id, sid, socketio, console_size=None):
        """Start an exec session and handle IO"""
        try:
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.connect(self.socket_path)
            
            start_payload = {
                "Detach": False,
                "Tty": True
            }
            if console_size:
                start_payload["ConsoleSize"] = console_size

            http_request = (
                f"POST /exec/{exec_id}/start HTTP/1.1\r\n"
                f"Host: localhost\r\n"
                f"Content-Type: application/json\r\n"
                f"Content-Length: {len(json.dumps(start_payload))}\r\n"
                f"\r\n"
                f"{json.dumps(start_payload)}"
            )

            sock.send(http_request.encode('utf-8'))

            self.exec_sessions[sid] = {
                'socket': sock,
                'exec_id': exec_id
            }

            try:
                # Read the HTTP response headers
                response_data = b""
                while b"\r\n\r\n" not in response_data:
                    chunk = sock.recv(1024)
                    if not chunk:
                        break
                    response_data += chunk

                # Split headers and start of body
                headers, body = response_data.split(b"\r\n\r\n", 1)
                
                # If we have any body data from the split, send it
                if body:
                    socketio.emit('output', {'data': body.decode('utf-8', errors='replace')}, to=sid)

                # Continue reading the stream
                buffer = b""
                while True:
                    if sid not in self.exec_sessions:
                        break

                    chunk = sock.recv(1024)
                    if not chunk:
                        break

                    buffer += chunk
                    
                    # Try to process as much of the buffer as possible
                    while buffer:
                        try:
                            # Try to decode the buffer
                            data = buffer.decode('utf-8', errors='replace')
                            socketio.emit('output', {'data': data}, to=sid)
                            buffer = b""
                        except UnicodeDecodeError:
                            # If we can't decode, we might have a partial character
                            # Keep the last byte in the buffer and try again
                            buffer = buffer[-1:]
                            data = buffer[:-1].decode('utf-8', errors='replace')
                            if data:
                                socketio.emit('output', {'data': data}, to=sid)

            except Exception as e:
                socketio.emit('output', {'data': f"Error: {str(e)}"}, to=sid)
            finally:
                self.cleanup_session(sid)
            
        except Exception as e:
            socketio.emit('output', {'data': f"Error starting exec session: {str(e)}"}, to=sid)
            self.cleanup_session(sid)

    def handle_command(self, command, sid):
        """Handle input from client"""
        try:
            if sid in self.exec_sessions:
                sock = self.exec_sessions[sid]['socket']
                sock.send(command.encode())
            else:
                return "No active session\r\n"
        except Exception as e:
            return f"Error sending command: {str(e)}"

    def cleanup_session(self, sid):
        """Clean up session resources"""
        if sid in self.exec_sessions:
            try:
                self.exec_sessions[sid]['socket'].close()
            except:
                pass
            del self.exec_sessions[sid]
    
    # SYSTEM

    def info(self):
        return self.perform_request('/info')
    
    def df(self):
        return self.perform_request('/system/df')

    # CONTAINER

    def get_containers(self):
        return self.perform_request('/containers/json?all=true')

    def inspect_container(self, container_id):
        return self.perform_request(f'/containers/{container_id}/json')

    def get_processes(self, container_id):
        return self.perform_request(f'/containers/{container_id}/top')

    def get_logs(self, container_id, stdout=True, stderr=True, tail='all'):
        path = f'/containers/{container_id}/logs?stdout={str(stdout).lower()}&stderr={str(stderr).lower()}&tail={tail}'
        response, status_code = self.perform_request(path)
        messages = []
        offset = 0

        if status_code not in range(200, 300):
            return response, status_code

        data = response.content

        while offset < len(data):
            stream_type = data[offset]

            if stream_type == 1:
                message_type = 'stdout'
            elif stream_type == 2:
                message_type = 'stderr'
            else:
                message_type = 'unknown'

            length_bytes = data[offset + 4:offset + 8]
            message_length = (length_bytes[0] << 24) + (length_bytes[1] << 16) + (length_bytes[2] << 8) + length_bytes[3]

            message_start = offset + 8
            message_end = message_start + message_length
            message_bytes = data[message_start:message_end].decode('utf-8', errors='ignore')

            messages.append({
                'type': message_type,
                'message': message_bytes
            })

            offset = message_end

        return messages, 200

    def restart_container(self, container_id):
        return self.perform_request(f'/containers/{container_id}/restart', method='POST')

    def start_container(self, container_id):
        return self.perform_request(f'/containers/{container_id}/start', method='POST')

    def stop_container(self, container_id):
        return self.perform_request(f'/containers/{container_id}/stop', method='POST')

    def delete_container(self, container_id):
        return self.perform_request(f'/containers/{container_id}', method='DELETE')

    def prune_containers(self):
        return self.perform_request('/containers/prune', method='POST')

    # IMAGE

    def get_images(self):
        return self.perform_request('/images/json')

    def inspect_image(self, image_id):
        return self.perform_request(f'/images/{image_id}/json')

    def delete_image(self, image_id):
        return self.perform_request(f'/images/{image_id}', method='DELETE')

    def prune_images(self, params=None):
        return self.perform_request('/images/prune', method='POST', params=params)
    
    def prune_build_cache(self):
        return self.perform_request('/build/prune', method='POST')

    # VOLUME

    def get_volumes(self):
        return self.perform_request('/volumes')

    def inspect_volume(self, volume_id):
        return self.perform_request(f'/volumes/{volume_id}')
    
    def delete_volume(self, volume_id):
        return self.perform_request(f'/volumes/{volume_id}', method='DELETE')

    def prune_volumes(self):
        return self.perform_request('/volumes/prune', method='POST')

    # NETWORK

    def get_networks(self):
        return self.perform_request('/networks')

    def inspect_network(self, network_id):
        return self.perform_request(f'/networks/{network_id}')

    def delete_network(self, network_id):
        return self.perform_request(f'/networks/{network_id}', method='DELETE')

    def prune_networks(self):
        return self.perform_request('/networks/prune', method='POST')

