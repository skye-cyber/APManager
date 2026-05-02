#!/usr/bin/env python3
import subprocess
import re
import logging
import time
from datetime import datetime
from ..core.config import configmanager
from .authmanager import authenticator


class DeviceScanner:
    def __init__(self):
        self.config = configmanager
        self.auth_file = configmanager.mac_file
        self.subnet = self.config.SUBNET
        self.subnet_parts = self.subnet.split(".")
        self.interface = self.config.CLIENT_INTERFACE
        self.setup_logging()

    def setup_logging(self):
        (configmanager.BASE_DIR / "logs/captive").mkdir(parents=True, exist_ok=True)
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(configmanager.BASE_DIR / "logs/device_scanner.log"),
                logging.StreamHandler(),
            ],
        )
        self.logger = logging.getLogger(__name__)

    def get_connected_devices(self):
        """Get all connected devices using multiple methods"""
        devices = []

        try:
            # Method 1: Use arp command
            result = subprocess.run(
                ["arp", "-a", "-i", self.interface],
                capture_output=True,
                text=True,
                check=True,
            )

            for line in result.stdout.split("\n"):
                if self.interface in line and self.subnet.rsplit(".", 1)[0] in line:
                    # Parse: ? eg (192.168.12.100) at ab:cd:ef:12:34:56 [ether] on wlan0
                    ip_match = re.search(
                        rf"\(({self.subnet_parts[0]}\.{self.subnet_parts[1]}\.{
                            self.subnet_parts[2]
                        }\.\d+)\)",
                        line,
                    )
                    mac_match = re.search(r"at\s+([0-9a-fA-F:]{17})", line)

                    if ip_match and mac_match:
                        devices.append(
                            {
                                "ip": ip_match.group(1),
                                "mac": mac_match.group(1).lower(),
                                "timestamp": datetime.now().isoformat(),
                            }
                        )

            # Method 2: Use ip neigh (more reliable)
            result = subprocess.run(
                ["ip", "neigh", "show", "dev", self.interface],
                capture_output=True,
                text=True,
                check=True,
            )

            for line in result.stdout.split("\n"):
                if self.subnet.rsplit(".", 1)[0] in line and "REACHABLE" in line:
                    parts = line.split()
                    if len(parts) >= 5:
                        devices.append(
                            {
                                "ip": parts[0],
                                "mac": parts[4].lower(),
                                "timestamp": datetime.now().isoformat(),
                            }
                        )

        except Exception as e:
            self.logger.error(f"Error scanning devices: {e}")

        return devices

    def scan_and_log(self):
        """Main scanning function"""
        self.logger.info("Starting device scan")

        devices = self.get_connected_devices()
        new_devices = []

        for device in devices:
            if not authenticator.is_authenticated(device["mac"]):
                new_devices.append(device)
                self.logger.info(
                    f"New unauthenticated device: {device['ip']} - {device['mac']}"
                )
            else:
                self.logger.debug(
                    f"Authenticated device: {device['ip']} - {device['mac']}"
                )

        self.logger.info(
            f"Scan completed. Found {len(devices)} total devices, {
                len(new_devices)
            } new unauthenticated devices"
        )
        return new_devices


def main():
    scanner = DeviceScanner()

    # Run continuous scanning
    while True:
        try:
            scanner.scan_and_log()
            time.sleep(3)  # Scan every 30 seconds
        except KeyboardInterrupt:
            break
        except Exception as e:
            logging.error(f"Scanner error: {e}")
            time.sleep(60)


if __name__ == "__main__":
    main()
