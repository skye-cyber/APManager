import subprocess
from .config import configmanager


class VPNAthentictaor:
    def __init__(self):
        self.config = configmanager

    def vpn_bypass(self, unset=False):
        """Allow forwarding for VPN/tunnel interfaces"""
        # Get all interfaces
        result = subprocess.run(
            ["ip", "-o", "link", "show"], capture_output=True, text=True
        )

        for line in result.stdout.splitlines():
            # Extract interface name
            iface = line.split(":")[1].strip()

            # Skip local/hotspot interfaces
            if iface in [
                "lo",
                self.config.CLIENT_INTERFACE,
                self.config.INTERNET_INTERFACE,
            ]:
                continue

            # Check if interface has an IP (is active)
            ip_check = subprocess.run(
                ["ip", "addr", "show", iface], capture_output=True, text=True
            )
            if "inet " in ip_check.stdout:
                # Not in our subnet range → likely VPN
                if self.config.GATEWAY not in ip_check.stdout:
                    if unset:
                        self.resetVPNInterface(iface=iface)
                    else:
                        self.allowVPNInterface(iface)

    def allowVPNInterface(self, iface: str):
        """Allows traffic t and from a given interface"""
        if not iface:
            return
        print(f"Adding VPN bypass for interface: {iface}")

        # Allow forwarding both directions
        subprocess.run(
            [
                "iptables",
                "-I",
                "FORWARD",
                "1",
                "-i",
                iface,
                "-o",
                self.config.CLIENT_INTERFACE,
                "-j",
                "ACCEPT",
            ],
            check=False,
        )

        subprocess.run(
            [
                "iptables",
                "-I",
                "FORWARD",
                "1",
                "-i",
                self.config.INTERNET_INTERFACE,
                "-o",
                iface,
                "-j",
                "ACCEPT",
            ],
            check=False,
        )

    def blockVPNInterface(self, iface: str):
        """Explicitly blocks given interface"""
        if not iface:
            return
        print(f"Remove VPN bypass for interface: {iface}")

        # Allow forwarding both directions
        subprocess.run(
            [
                "iptables",
                "-I",
                "FORWARD",
                "1",
                "-i",
                iface,
                "-o",
                self.config.CLIENT_INTERFACE,
                "-j",
                "DROP",
            ],
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            check=False,
        )

        subprocess.run(
            [
                "iptables",
                "-I",
                "FORWARD",
                "1",
                "-i",
                self.config.INTERNET_INTERFACE,
                "-o",
                iface,
                "-j",
                "DROP",
            ],
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            check=False,
        )

    def resetVPNInterface(self, iface: str):
        """Clears rules for given interface"""
        if not iface:
            return
        print(f"Reset VPN bypass for interface: {iface}")

        # Allow forwarding both directions
        subprocess.run(
            [
                "iptables",
                "-D",
                "FORWARD",
                "-i",
                iface,
                "-o",
                self.config.CLIENT_INTERFACE,
                "-j",
                "ACCEPT",
            ],
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            check=False,
        )

        subprocess.run(
            [
                "iptables",
                "-D",
                "FORWARD",
                "-i",
                self.config.INTERNET_INTERFACE,
                "-o",
                iface,
                "-j",
                "ACCEPT",
            ],
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            check=False,
        )


vpnAuthentictaor = VPNAthentictaor()
