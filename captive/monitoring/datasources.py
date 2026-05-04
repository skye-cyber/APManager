"""Backend Data Sources"""

from typing import List, Optional
from .writer import writer
from ..core.config import configmanager
from ..utils.authmanager import authenticator

# Try to import requests for API calls, fallback to file
try:
    import requests

    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


class AbstractAPI:
    """Abstract base class for data sources"""

    def get_authenticated_macs(self) -> List[str]:
        raise NotImplementedError

    def authenticate_device(self, mac: str) -> bool:
        raise NotImplementedError

    def block_device(self, mac: str) -> bool:
        raise NotImplementedError


class FileApi(AbstractAPI):
    """File-based data source (current implementation)"""

    def __init__(self):
        self.api = SystemApi()
        pass

    def get_authenticated_macs(self) -> List[str]:
        """Read authenticated MACs from file"""
        writer.write("Auth devices")
        try:
            devices = authenticator.authenticated
            writer.write(f"Devices:\n{devices}")
            return devices
        except Exception:
            return []

    def authenticate_device(self, mac: str) -> bool:
        """Add MAC to authenticated file"""
        mac = mac.lower()
        if configmanager.USE_API and HAS_REQUESTS:
            self.api.authenticate_device(mac)
        return authenticator.addDevice(mac=mac)

    def block_device(self, mac: str) -> bool:
        """Remove MAC from authenticated file"""
        mac = mac.lower()
        if configmanager.USE_API and HAS_REQUESTS:
            self.api.block_device(mac)
        return authenticator.removeDevice(mac=mac)


class SystemApi(AbstractAPI):
    """API-based data source (for future Django integration)"""

    def __init__(
        self,
        api_endpoint: str = configmanager.API_ENDPOINT,
        api_key: Optional[str] = None,
    ):
        self.api_endpoint = api_endpoint.rstrip("/")
        self.api_key = api_key
        self.session = requests.Session() if HAS_REQUESTS else None

    def get_authenticated_macs(self) -> List[str]:
        """Fetch authenticated MACs from API"""
        if not self.session:
            return []

        try:
            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

            response = self.session.get(
                f"{self.api_endpoint}/authenticated/", headers=headers, timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                return [device["mac"].lower() for device in data.get("devices", [])]
        except Exception:
            pass

        return []

    def authenticate_device(self, mac: str) -> bool:
        """Authenticate device via API"""
        if not self.session:
            return False

        try:
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

            response = self.session.post(
                f"{self.api_endpoint}/authenticate/",
                json={"mac": mac.lower()},
                headers=headers,
                timeout=5,
            )
            return response.status_code == 200
        except Exception:
            return False

    def block_device(self, mac: str) -> bool:
        """Block device via API"""
        if not self.session:
            return False

        try:
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

            response = self.session.post(
                f"{self.api_endpoint}/block/",
                json={"mac": mac.lower()},
                headers=headers,
                timeout=5,
            )
            return response.status_code == 200
        except Exception:
            return False
