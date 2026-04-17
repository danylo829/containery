import codecs
import json
import socket
import requests_unixsocket
import requests
from urllib.parse import quote_plus

class Docker:
    def __init__(self):
        self.exec_sessions = {}

    def _decode_chunked_data(self, state, data: bytes) -> bytes:
        """Decode HTTP chunked payload bytes from a streaming connection."""
        if not data:
            return b""

        state['buffer'] += data
        out = bytearray()

        while True:
            if state['chunk_size'] is None:
                line_end = state['buffer'].find(b"\r\n")
                if line_end == -1:
                    break

                size_line = state['buffer'][:line_end].split(b";", 1)[0].strip()
                state['buffer'] = state['buffer'][line_end + 2:]

                try:
                    state['chunk_size'] = int(size_line, 16)
                except ValueError:
                    # Fallback: return buffered bytes unmodified if framing is malformed.
                    out.extend(state['buffer'])
                    state['buffer'] = b""
                    state['chunk_size'] = None
                    break

                if state['chunk_size'] == 0:
                    state['chunk_size'] = None
                    if state['buffer'].startswith(b"\r\n"):
                        state['buffer'] = state['buffer'][2:]
                    continue

            chunk_size = state['chunk_size']
            if len(state['buffer']) < chunk_size + 2:
                break

            out.extend(state['buffer'][:chunk_size])
            state['buffer'] = state['buffer'][chunk_size:]

            if state['buffer'].startswith(b"\r\n"):
                state['buffer'] = state['buffer'][2:]

            state['chunk_size'] = None

        return bytes(out)

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
            try:
                sock.connect(host.address)
            except Exception:
                sock.close()
                raise

            start_payload = {
                "Detach": False,
                "Tty": True
            }
            if console_size:
                start_payload["ConsoleSize"] = console_size

            body = json.dumps(start_payload).encode('utf-8')
            http_request = (
                f"POST /exec/{exec_id}/start HTTP/1.1\r\n"
                f"Host: localhost\r\n"
                f"Content-Type: application/json\r\n"
                f"Connection: Upgrade\r\n"
                f"Upgrade: tcp\r\n"
                f"Content-Length: {len(body)}\r\n"
                f"\r\n"
            ).encode('utf-8') + body
            sock.sendall(http_request)

            response_data = b""
            while b"\r\n\r\n" not in response_data:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                response_data += chunk

            if b"\r\n\r\n" not in response_data:
                socketio.emit('output', {'data': "Error: invalid exec response from Docker daemon"}, to=sid)
                sock.close()
                return

            header_bytes, initial_body = response_data.split(b"\r\n\r\n", 1)
            header_text = header_bytes.decode('iso-8859-1', errors='replace')
            header_lines = header_text.split("\r\n")

            status_code = 500
            if header_lines:
                status_parts = header_lines[0].split(" ", 2)
                if len(status_parts) > 1 and status_parts[1].isdigit():
                    status_code = int(status_parts[1])

            if status_code not in (101, 200):
                socketio.emit('output', {'data': f"Error: Docker exec start failed ({status_code})"}, to=sid)
                sock.close()
                return

            is_chunked = 'transfer-encoding: chunked' in header_text.lower()
            chunked_state = {'buffer': b'', 'chunk_size': None}

            self.exec_sessions[sid] = {
                'socket': sock,
                'exec_id': exec_id,
                'host': host
            }

            try:
                decoder = codecs.getincrementaldecoder('utf-8')(errors='replace')
                sock.settimeout(30)

                # Some Docker variants send initial payload bytes with headers.
                pending = self._decode_chunked_data(chunked_state, initial_body) if is_chunked else initial_body
                if pending:
                    initial_data = decoder.decode(pending)
                    if initial_data:
                        socketio.emit('output', {'data': initial_data}, to=sid)

                while True:
                    if sid not in self.exec_sessions:
                        break

                    chunk = sock.recv(4096)
                    if not chunk:
                        break

                    if is_chunked:
                        chunk = self._decode_chunked_data(chunked_state, chunk)
                        if not chunk:
                            continue

                    data = decoder.decode(chunk)
                    if data:
                        socketio.emit('output', {'data': data}, to=sid)

                data = decoder.decode(b'', final=True)
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
                sock.sendall(command.encode())
            else:
                return "No active session\r\n"
        except Exception as e:
            return f"Error sending command: {str(e)}"

    def resize_exec(self, sid, exec_id, cols, rows):
        """Resize the TTY for an active exec session."""
        session = self.exec_sessions.get(sid)
        if not session:
            return None, 404
        host = session['host']
        return self.perform_request(f'/exec/{exec_id}/resize?h={rows}&w={cols}', method='POST', host=host)

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

