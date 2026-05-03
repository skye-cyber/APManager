import subprocess
from .VPN import vpnAuthentictaor


class StopCaptive:
    def __init__(self): ...

    def stop(self, novpn: bool = False) -> bool:
        """
        Stop captive portal
        """
        # Stop device detection

        self.stop_services()
        self.clear_iptables()
        if not novpn:
            vpnAuthentictaor.vpn_bypass(unset=True)
        print("Captive portal stopped")
        return True

    def stop_services(self):
        # Stop dnsmaq
        subprocess.run(["service", "dnsmasq", "stop"], check=True)

    def clear_iptables_contextual(self):
        # Don't flush everything blindly — only remove captive-specific rules
        # Remove custom chains if they exist
        subprocess.run(["iptables", "-F", "CAPTIVE_PORTAL"], check=False)
        subprocess.run(["iptables", "-t", "nat", "-F", "AUTH_REDIRECT"], check=False)
        subprocess.run(
            ["iptables", "-D", "FORWARD", "-j", "CAPTIVE_PORTAL"], check=False
        )
        subprocess.run(
            ["iptables", "-t", "nat", "-D", "PREROUTING", "-j", "AUTH_REDIRECT"],
            check=False,
        )
        subprocess.run(["iptables", "-X", "CAPTIVE_PORTAL"], check=False)
        subprocess.run(["iptables", "-t", "nat", "-X", "AUTH_REDIRECT"], check=False)

        # CRITICAL: Reset FORWARD policy to ACCEPT (or restore previous state)
        subprocess.run(["iptables", "-P", "FORWARD", "ACCEPT"], check=False)

    def clear_iptables(self):
        subprocess.run(["iptables", "-F"], check=False)
        subprocess.run(["iptables", "-t", "nat", "-F"], check=False)
        subprocess.run(["iptables", "-X"], check=False)
        subprocess.run(["iptables", "-t", "nat", "-X"], check=False)

        # Restore default policies so internet works
        subprocess.run(["iptables", "-P", "INPUT", "ACCEPT"], check=False)
        subprocess.run(["iptables", "-P", "FORWARD", "ACCEPT"], check=False)
        subprocess.run(["iptables", "-P", "OUTPUT", "ACCEPT"], check=False)
        # subprocess.run(["systemctl", "stop", "dnsmaq"])


stopcaptive = StopCaptive()
