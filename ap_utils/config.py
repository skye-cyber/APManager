import json
from pathlib import Path
import sys

# BASE_DIR = Path(__file__).resolve().parent.parent


class ConfigManager:
    def __init__(self, config_file: Path = Path("/etc/ap_manager/conf/config.json")):
        self.config_file = config_file
        self.config = self.load_config()
        self.config_dir = config_file.parent or self.config.get("conf_dir", "")
        self.proc_dir = self.config.get("proc_dir", self.config_dir.parent / "proc")

    def __enter__(self):
        # Ensure we are using update config
        self.config = self.load_config()

    @property
    def get_config(self):
        return self.config

    @property
    def dnsmasq_pidfile(self):
        return Path(self.proc_dir) / "dnsmasq.pid"

    @property
    def hostapd_pidfile(self):
        return Path(self.proc_dir) / "hostapd.pid"

    @property
    def dnsmasq_leasesfile(self):
        return Path(self.proc_dir) / "dnsmasq.leases"

    @property
    def hostapd_logfile(self):
        return (
            self.config.get("hostapd_logfile", None)
            or Path(self.proc_dir).parent / "hostapd.log"
        )

    @property
    def dnsmasq_logfile(self):
        return (
            self.config.get("dnsmasq_logfile", None)
            or Path(self.proc_dir).parent / "dnsmasq.log"
        )

    def load_config(self):
        """Load configuration from file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, "r") as f:
                    self.config = json.load(f)
                    # self.config = {**self.default_config, **user_config}
            else:
                raise Exception(f"Config file not found {self.config_file}")
            return self.config
        except IOError:
            sys.exit(f"Error: Unable to read config file {self.config_file}")

    def set(self, key, value):
        """Save configuration to file"""
        if key not in self.config:
            return None
        self.config[key] = value
        self.save_config()
        return value

    def save_config(self):
        """Save configuration to file"""
        with open(self.config_file, "w") as f:
            json.dump(self.config, f, indent=2)

    @property
    def __str__(self):
        return (
            "\n".join(f"{k}={v}" for k, v in self.config.items()).strip()
            if self.config
            else None
        )

    def _dict_update(self, d1: dict | None, d2: dict):
        """
        Args:
            d1: dictionary to update - target dict
            d2: dictionary to update from - source dict
        """
        target = d1 if d1 is not None else self.config
        known = config_manager.config  # or .keys(), hoisted
        if not d2:
            return self.config

        target.update(
            {
                k.lower(): v
                for k, v in d2.items()
                if v is not None and k.lower() in known
            }
        )

        return target

    @property
    def __bdir__(self):
        return self.config.get("BASE_DIR")

    @property
    def __bconfdir__(self):
        return self.config_dir

    def is_config_opt(self, opt: str) -> bool:
        """Check if an option is a valid configuration option."""
        return opt in self.config.keys()


config_manager = ConfigManager()
