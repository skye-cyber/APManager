#!/usr/bin/env python3
"""
Root daemon for AP Manager - runs with root privileges
Communicates via Unix socket or DBus
"""
import os
import sys
import json
import signal
import socket
import logging
import threading
import subprocess
from typing import Dict, Any, List

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class APManagerDaemon:
    SOCKET_PATH = "/var/run/ap_manager.sock"

    def __init__(self):
        self.running = True
        self.socket = None
        signal.signal(signal.SIGTERM, self.handle_signal)
        signal.signal(signal.SIGINT, self.handle_signal)

    def handle_signal(self, signum, frame):
        logger.info("Received shutdown signal")
        self.running = False
        if self.socket:
            self.socket.close()

    def run_command(self, command: str, args: list) -> Dict[str, Any]:
        """Run a privileged command safely."""
        allowed_commands = {
            'iw': ['iw', 'dev', 'wlan0', 'interface', 'add', 'xap0', 'type', '__ap'],
            'ip_link': ['ip', 'link'],
            'ip_addr': ['ip', 'addr'],
            'hostapd': ['hostapd'],
            'dnsmasq': ['dnsmasq'],
            'mkdir': ['mkdir', '-p'],
            'chown': ['chown'],
            'systemctl': ['systemctl'],
        }

        logger.info(f"X: {command}--{args}")
        if command not in allowed_commands.keys():
            return {"success": False, "error": f"Command not allowed: {command}"}

        try:
            cmd = command + args
            logger.info(f"CMD: {command} - {args}")
            logger.info(f"Executing: {' '.join(cmd)}")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def exec(
        self,
        cmd: List[str],
        *args,
        capture_output: bool = True,
        check: bool = True,
        text: bool = True,
        **kwargs
    ) -> json:
        """
        Run command with appropriate privilege escalation.
        """

        # Prepare command
        full_cmd = cmd + list(args)

        logger.info(f"Executing: {' '.join(full_cmd)}")
        # Run the command
        try:
            result = subprocess.run(
                full_cmd,
                capture_output=capture_output,
                check=check,
                text=text,
                **kwargs
            )
            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        except subprocess.CalledProcessError as e:
            return {"success": False, "error": str(e)}

    def handle_client(self, conn, addr):
        """Handle a single client connection."""
        try:
            data = conn.recv(4096)
            if not data:
                return

            request = json.loads(data.decode('utf-8'))
            command = request.get('command')
            args = request.get('args', [])
            request_id = request.get('id', 'unknown')

            logger.info(f"Processing request {request_id}: {command}")

            # response = self.exec(command, args) if type(command) is list and type(args) is str else
            response = self.run_command(command, args)

            response['request_id'] = request_id

            conn.send(json.dumps(response).encode('utf-8'))

        except Exception as e:
            logger.error(f"Error handling client: {e}")
            conn.send(json.dumps({
                "success": False,
                "error": str(e)
            }).encode('utf-8'))
        finally:
            conn.close()

    def _start_(self):
        # Remove old socket check and cleanup
        # Systemd will handle socket creation and cleanup

        # Just bind to the existing socket
        self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.socket.bind(self.SOCKET_PATH)
        self.socket.listen(5)

        # Set permissions (though systemd already did this)
        try:
            os.chmod(self.SOCKET_PATH, 0o660)
            os.chown(self.SOCKET_PATH, 0, os.getgid())
        except OSError:
            pass  # Socket might be in use by systemd

        logger.info(f"Daemon started, listening on {self.SOCKET_PATH}")

        while self.running:
            try:
                conn, addr = self.socket.accept()
                thread = threading.Thread(
                    target=self.handle_client,
                    args=(conn, addr)
                )
                thread.daemon = True
                thread.start()
            except OSError:
                break  # Socket closed

        logger.info("Daemon stopped")

    def start(self):
        # Ensure we're root
        if os.geteuid() != 0:
            sys.exit(1)

        # Remove old socket
        try:
            if os.path.exists(self.SOCKET_PATH):
                os.unlink(self.SOCKET_PATH)
        except Exception:
            pass

        # Create socket
        self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.socket.bind(self.SOCKET_PATH)
        self.socket.listen(5)

        # Set permissions so user can connect
        try:
            os.chmod(self.SOCKET_PATH, 0o660)
            os.chown(self.SOCKET_PATH, 0, os.getgid())  # Owned by root, group accessible
        except OSError:
            pass

        logger.info(f"Daemon started, listening on {self.SOCKET_PATH}")

        while self.running:
            try:
                conn, addr = self.socket.accept()
                thread = threading.Thread(
                    target=self.handle_client,
                    args=(conn, addr)
                )
                thread.daemon = True
                thread.start()
            except OSError:
                break  # Socket closed

        logger.info("Daemon stopped")


def main():
    daemon = APManagerDaemon()
    daemon.start()


if __name__ == "__main__":
    main()
