import json
import socket
import requests_unixsocket
import requests
from urllib.parse import quote_plus

class Docker:
    def __init__(self):
        self.exec_sessions = {}

    # GENERAL

    def perform_request(self, path: str, method='GET', payload=None, params=None, host=None, timeout=10) -> tuple:
        if not host:
            return "Host not provided", 500

        if 'unix' == host.scheme:
            session = requests_unixsocket.Session()
            socket_path = host.url.replace('unix://', '')
            url = f"http+unix://{quote_plus(socket_path)}{path}"
        else:
            session = requests.Session()
            url = host.url + path
        try:
            if method == 'GET':
                response = session.get(url, params=params, timeout=timeout)
            elif method == 'DELETE':
                response = session.delete(url, params=params, timeout=timeout)
            elif method == 'POST':
                response = session.post(url, json=payload, params=params, timeout=timeout)
            else:
                return f"Unsupported HTTP method: {method}", 400
            return response, response.status_code
        except Exception as e:
            return str(e), 500
    
    # EXEC

    def create_exec(self, endpoint, payload, host=None):
        """Create an exec instance and return its ID."""
        response, status_code = self.perform_request(endpoint, method='POST', payload=payload, host=host)
        if status_code in range(200, 300):
            exec_instance_json = response.json()
            return exec_instance_json.get("Id")
        return None

    def start_exec_session(self, exec_id, sid, socketio, host, console_size=None):
        """Start an exec session and handle IO"""
        try:
            if not host or not host.enabled:
                socketio.emit('output', {'data': f"Error: host not available"}, to=sid)
                return

            if host.scheme != 'unix':
                socketio.emit('output', {'data': "Exec over TCP/HTTPS not implemented"}, to=sid)
                return

            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.connect(host.address)
            
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

    def info(self, host=None):
        return self.perform_request('/info', host=host)
    
    def df(self, host=None):
        return self.perform_request('/system/df', host=host)

    # CONTAINER

    def get_containers(self, host=None):
        return self.perform_request('/containers/json?all=true', host=host)

    def inspect_container(self, container_id, host=None):
        return self.perform_request(f'/containers/{container_id}/json', host=host)

    def get_processes(self, container_id, host=None):
        return self.perform_request(f'/containers/{container_id}/top', host=host)

    def get_logs(self, container_id, stdout=True, stderr=True, tail='all', host=None):
        path = f'/containers/{container_id}/logs?stdout={str(stdout).lower()}&stderr={str(stderr).lower()}&tail={tail}'
        response, status_code = self.perform_request(path, host=host)
        if hasattr(response, 'content'):
            return self._parse_multiplexed_logs(response.content), status_code
        return response, status_code

    def _parse_multiplexed_logs(self, data: bytes):
        messages = []
        offset = 0
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
            messages.append({'type': message_type, 'message': message_bytes})
            offset = message_end
        return messages

    def restart_container(self, container_id, host=None):
        return self.perform_request(f'/containers/{container_id}/restart', method='POST', host=host)

    def start_container(self, container_id, host=None):
        return self.perform_request(f'/containers/{container_id}/start', method='POST', host=host)

    def stop_container(self, container_id, host=None):
        return self.perform_request(f'/containers/{container_id}/stop', method='POST', host=host)

    def delete_container(self, container_id, host=None):
        return self.perform_request(f'/containers/{container_id}', method='DELETE', host=host)

    def prune_containers(self, filters=None, host=None):
        params = None
        if filters:
            params = {'filters': json.dumps(filters)}
        return self.perform_request('/containers/prune', method='POST', params=params, host=host)

    # IMAGE

    def get_images(self, host=None):
        return self.perform_request('/images/json', host=host)

    def inspect_image(self, image_id, host=None):
        return self.perform_request(f'/images/{image_id}/json', host=host)

    def delete_image(self, image_id, host=None):
        return self.perform_request(f'/images/{image_id}', method='DELETE', host=host)

    def prune_images(self, params=None, host=None):
        return self.perform_request('/images/prune', method='POST', params=params, host=host)
    
    def prune_build_cache(self, host=None):
        return self.perform_request('/build/prune', method='POST', host=host)

    # VOLUME

    def get_volumes(self, host=None):
        return self.perform_request('/volumes', host=host)

    def inspect_volume(self, volume_id, host=None):
        return self.perform_request(f'/volumes/{volume_id}', host=host)
    
    def delete_volume(self, volume_id, host=None):
        return self.perform_request(f'/volumes/{volume_id}', method='DELETE', host=host)

    def prune_volumes(self, host=None):
        return self.perform_request('/volumes/prune', method='POST', host=host)

    # NETWORK

    def get_networks(self, host=None):
        return self.perform_request('/networks', host=host)

    def inspect_network(self, network_id, host=None):
        return self.perform_request(f'/networks/{network_id}', host=host)

    def delete_network(self, network_id, host=None):
        return self.perform_request(f'/networks/{network_id}', method='DELETE', host=host)

    def prune_networks(self, host=None):
        return self.perform_request('/networks/prune', method='POST', host=host)

