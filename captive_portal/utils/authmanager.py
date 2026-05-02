import json
from dataclasses import dataclass, asdict
from datetime import datetime
from ..core.config import configmanager


class Device:
    IP: str
    MAC: str
    AT: str  # Authentication time

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2)

    @classmethod
    def from_json(cls, data: str) -> "Device":
        return cls(**json.loads(data))


class Devices:
    DEVICES: list(Device)

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2)

    @classmethod
    def from_json(cls, data: str) -> "Devices":
        return cls(**json.loads(data))


@dataclass
class Schema:
    AUTHENTICATION: Devices
    MAC_HIST: list(str)  # Contains all macs of device ever connected

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2)

    @classmethod
    def from_json(cls, data: str) -> "Schema":
        return cls(**json.loads(data))


class AuthManager:
    """
    Manages devices authentication via json file\n
    Allows:\n
    - Reading
    - Writing into
    - Clearing
    - Initializing empty schema on file
    - Generating schema
    """

    def __init__(self):
        self.config = configmanager
        self.AUTH_FILE = configmanager.mac_file
        self.auth_data: Schema = self.readFile()
        self.autoSave: bool = True

    def __enter__(self):
        self.auth_data: Schema = self.readFile()

    @property
    def schema(self) -> Schema:
        SCHEMA: Schema = {"AUTHENTICATION": {"DEVICES": {}}, "MAC_HIST": []}
        return Schema.from_json(json.dumps(SCHEMA))

    def readFile(self):
        if not self.AUTH_FILE:
            return self.schema

        data = None

        try:
            with open(self.AUTH_FILE, "r") as f:
                data = json.load(f)
        except Exception:
            pass

        if data:
            return Schema.from_json(json.dumps(data))
        # Initialize file
        self.writeFile(self.schema)
        return self.schema

    def writeFile(self, data: Schema) -> bool:
        with open(self.AUTH_FILE, "w") as f:
            f.write(data.to_json())

        return True

    def addDevice(self, mac: str, ip: str = None) -> bool:
        device: Device = {
            "IP": ip,
            "MAC": mac,
            "AT": datetime.now().strftime("%d:%m:%y-%H:%M:%S"),
        }
        self.auth_data.AUTHENTICATION.DEVICES.push(device)
        self.auth_data.MAC_HIST.push(mac)
        if self.autoSave:
            self.writeFile(self.auth_data)
        return True

    def removeDevice(self, mac: str):
        self.auth_data.AUTHENTICATION.DEVICES.push(mac)
        if self.autoSave:
            self.writeFile(self.auth_data)

    def clearAuth(self):
        self.writFile(self.schema)
        if self.autoSave:
            self.writeFile(self.auth_data)

    def is_authenticated(self, mac: str):
        devices: list(Device) = self.auth_data.AUTHENTICATION.DEVICES
        if not devices or len(devices) == 0:
            return
        for dev in devices:
            if dev.MAC.lower() == mac.lower():
                return True
        return False

    @property
    def authenticated(self) -> Devices:
        return self.auth_data.AUTHENTICATION.DEVICES

    @property
    def history(self) -> Devices:
        return self.auth_data.MAC_HIST


authenticator = AuthManager()
