import socket
import json
import os
import logging

logger = logging.getLogger(__name__)


class APManagerClient:
    SOCKET_PATH = "/var/run/ap_manager.sock"

    def __init__(self):
        self.request_id = 0

    def __enter__(self):
        self.ensure_daemon_running()

    def _send_request(self, command: str | list, args: list | str) -> dict:
        """Send request to daemon."""
        if not os.path.exists(self.SOCKET_PATH):
            raise ConnectionError("Daemon not running")

        self.request_id += 1
        request = {
            "id": f"req_{self.request_id}",
            "command": command,
            "args": args
        }

        try:
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.settimeout(30)
            sock.connect(self.SOCKET_PATH)

            sock.send(json.dumps(request).encode('utf-8'))

            # Receive response
            response_data = b""
            while True:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                response_data += chunk

            sock.close()

            return json.loads(response_data.decode('utf-8'))

        except Exception as e:
            raise
            logger.error(f"Failed to communicate with daemon: {e}")
            return {"success": False, "error": str(e)}

    def create_virtual_interface(self, interface: str, virt_name: str) -> bool:
        """Create virtual WiFi interface."""
        response = self._send_request('iw', ['dev', interface, 'interface', 'add', virt_name, 'type', '__ap'])
        return response.get('success', False)

    def setup_interface(self, interface: str, ip: str = "192.168.4.1") -> bool:
        """Setup network interface."""
        # Bring down
        self._send_request('ip_link', ['set', interface, 'down'])

        # Set MAC
        self._send_request('ip_link', ['set', interface, 'address', '02:00:00:00:00:01'])

        # Bring up
        self._send_request('ip_link', ['set', interface, 'up'])

        # Set IP
        response = self._send_request('ip_addr', ['add', f'{ip}/24', 'dev', interface])
        return response.get('success', False)

    # Add more methods as needed...


def ensure_daemon_running():
    """Ensure the daemon is running, start it if not."""
    import subprocess

    # Check if daemon is running
    result = subprocess.run(
        ['systemctl', 'is-active', 'ap_manager_daemon'],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print("Starting AP Manager daemon...")
        subprocess.run(['sudo', 'systemctl', 'start', 'ap_manager_daemon'])
        subprocess.run(['sudo', 'systemctl', 'enable', 'ap_manager_daemon'])


if __name__ == "__main__":
    # Ensure daemon is running
    ensure_daemon_running()
    import sys
    # Create client
    client = APManagerClient()
    try:
        # Create virtual interface
        if client.create_virtual_interface('wlan0', 'xap0'):
            print("✓ Virtual interface created")
        else:
            print("✗ Failed to create interface")
            sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
