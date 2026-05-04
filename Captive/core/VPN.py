import subprocess
from .config import configmanager


class VPNAuthenticator:
    def __init__(self):
        self.config = configmanager

    def _rule_exists(self, table, chain, rule_spec):
        """Check if a rule exists in iptables. Returns True if exists."""
        cmd = ["iptables"]
        if table != "filter":
            cmd.extend(["-t", table])
        cmd.extend(["-C", chain] + rule_spec)
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0

    def _remove_rule(self, table, chain, rule_spec):
        """Remove a rule if it exists. Returns True if removed."""
        if not self._rule_exists(table, chain, rule_spec):
            return False
        cmd = ["iptables"]
        if table != "filter":
            cmd.extend(["-t", table])
        cmd.extend(["-D", chain] + rule_spec)
        subprocess.run(cmd, capture_output=True, text=True)
        return True

    def vpn_bypass(self, unset=False):
        """Allow forwarding for VPN/tunnel interfaces"""
        result = subprocess.run(
            ["ip", "-o", "link", "show"], capture_output=True, text=True
        )

        for line in result.stdout.splitlines():
            iface = line.split(":")[1].strip()

            if iface in [
                "lo",
                self.config.CLIENT_INTERFACE,
                self.config.INTERNET_INTERFACE,
            ]:
                continue

            ip_check = subprocess.run(
                ["ip", "addr", "show", iface], capture_output=True, text=True
            )
            if "inet " in ip_check.stdout:
                if self.config.GATEWAY not in ip_check.stdout:
                    if unset:
                        self.resetVPNInterface(iface=iface)
                    else:
                        self.allowVPNInterface(iface)

    def allowVPNInterface(self, iface: str):
        """Allow traffic to and from a given interface"""
        if not iface:
            return
        print(f"Adding VPN bypass for interface: {iface}")

        # Define rule specs
        rule1 = ["-i", iface, "-o", self.config.CLIENT_INTERFACE, "-j", "ACCEPT"]
        rule2 = ["-i", self.config.CLIENT_INTERFACE, "-o", iface, "-j", "ACCEPT"]
        nat_rule = ["-o", iface, "-j", "MASQUERADE"]

        # Only add if not exists (prevent duplicates)
        if not self._rule_exists("filter", "FORWARD", rule1):
            subprocess.run(["iptables", "-I", "FORWARD", "1"] + rule1, check=False)

        if not self._rule_exists("filter", "FORWARD", rule2):
            subprocess.run(["iptables", "-I", "FORWARD", "1"] + rule2, check=False)

        if not self._rule_exists("nat", "POSTROUTING", nat_rule):
            subprocess.run(
                ["iptables", "-t", "nat", "-I", "POSTROUTING", "1"] + nat_rule,
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                check=False,
            )

    def blockVPNInterface(self, iface: str):
        """Block traffic on given interface by removing allow rules"""
        if not iface:
            return
        print(f"Blocking VPN bypass for interface: {iface}")

        # Remove allow rules (not add drop rules)
        self._remove_rule(
            "filter",
            "FORWARD",
            ["-i", iface, "-o", self.config.CLIENT_INTERFACE, "-j", "ACCEPT"],
        )
        self._remove_rule(
            "filter",
            "FORWARD",
            ["-i", self.config.CLIENT_INTERFACE, "-o", iface, "-j", "ACCEPT"],
        )
        self._remove_rule("nat", "POSTROUTING", ["-o", iface, "-j", "MASQUERADE"])

    def resetVPNInterface(self, iface: str):
        """Clears all rules for given interface"""
        if not iface:
            return
        print(f"Reset VPN bypass for interface: {iface}")

        # Remove all possible rule variations (ACCEPT and any DROP if exists)
        self._remove_rule(
            "filter",
            "FORWARD",
            ["-i", iface, "-o", self.config.CLIENT_INTERFACE, "-j", "ACCEPT"],
        )
        self._remove_rule(
            "filter",
            "FORWARD",
            ["-i", self.config.CLIENT_INTERFACE, "-o", iface, "-j", "ACCEPT"],
        )
        self._remove_rule(
            "filter",
            "FORWARD",
            ["-i", iface, "-o", self.config.CLIENT_INTERFACE, "-j", "DROP"],
        )
        self._remove_rule(
            "filter",
            "FORWARD",
            ["-i", self.config.CLIENT_INTERFACE, "-o", iface, "-j", "DROP"],
        )
        self._remove_rule("nat", "POSTROUTING", ["-o", iface, "-j", "MASQUERADE"])


vpnAuthenticator = VPNAuthenticator()
