import json
from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import List, Optional
from ..core.config import configmanager


@dataclass
class Device:
    IP: Optional[str] = None
    MAC: Optional[str] = None
    AT: Optional[str] = None  # Authentication time

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2)

    @classmethod
    def from_json(cls, data: str) -> "Device":
        return cls(**json.loads(data))


@dataclass
class Devices:
    DEVICES: List[Device] = field(default_factory=list)

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2)

    @classmethod
    def from_json(cls, data: str) -> "Devices":
        parsed = json.loads(data)
        # Handle case where DEVICES is a list of dicts
        if isinstance(parsed, dict) and "DEVICES" in parsed:
            devices = [
                Device(**d) if isinstance(d, dict) else d for d in parsed["DEVICES"]
            ]
            return cls(DEVICES=devices)
        return cls(**parsed)


@dataclass
class Schema:
    AUTHENTICATION: Devices = field(default_factory=lambda: Devices(DEVICES=[]))
    MAC_HIST: List[str] = field(default_factory=list)

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2)

    @classmethod
    def from_json(cls, data: str) -> "Schema":
        parsed = json.loads(data)
        # Handle nested deserialization
        auth = parsed.get("AUTHENTICATION", {})
        if isinstance(auth, dict):
            auth = Devices.from_json(json.dumps(auth))
        mac_hist = parsed.get("MAC_HIST", [])
        return cls(AUTHENTICATION=auth, MAC_HIST=mac_hist)


class AuthManager:
    """
    Manages devices authentication via json file
    Allows:
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
        self.auth_data = self.readFile()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.autoSave:
            self.writeFile(self.auth_data)

    @property
    def schema(self) -> Schema:
        return Schema(AUTHENTICATION=Devices(DEVICES=[]), MAC_HIST=[])

    def readFile(self) -> Schema:
        if not self.AUTH_FILE:
            return self.schema

        try:
            with open(self.AUTH_FILE, "r") as f:
                data = json.load(f)
                return Schema.from_json(json.dumps(data))
        except (FileNotFoundError, json.JSONDecodeError):
            schema = self.schema
            self.writeFile(schema)
            return schema
        except Exception as e:
            print(f"Error reading auth file: {e}")
            return self.schema

    def writeFile(self, data: Schema) -> bool:
        with open(self.AUTH_FILE, "w") as f:
            f.write(data.to_json())
        return True

    def addDevice(self, mac: str, ip: str = None) -> bool:
        device = Device(
            IP=ip,
            MAC=mac,
            AT=datetime.now().strftime("%d:%m:%y-%H:%M:%S"),
        )
        self.auth_data.AUTHENTICATION.DEVICES.append(device)
        if mac not in self.auth_data.MAC_HIST:
            self.auth_data.MAC_HIST.append(mac)
        if self.autoSave:
            self.writeFile(self.auth_data)
        return True

    def removeDevice(self, mac: str) -> bool:
        devices = self.auth_data.AUTHENTICATION.DEVICES
        self.auth_data.AUTHENTICATION.DEVICES = [
            d for d in devices if d.MAC.lower() != mac.lower()
        ]
        if self.autoSave:
            self.writeFile(self.auth_data)
        return True

    def clearAuth(self) -> bool:
        self.auth_data = self.schema
        self.writeFile(self.auth_data)
        return True

    def is_authenticated(self, mac: str) -> bool:
        devices = self.auth_data.AUTHENTICATION.DEVICES
        if not devices:
            return False
        mac_lower = mac.lower()
        for dev in devices:
            if dev.MAC and dev.MAC.lower() == mac_lower:
                return True
        return False

    @property
    def authenticated(self) -> List[Device]:
        return self.auth_data.AUTHENTICATION.DEVICES

    @property
    def history(self) -> List[str]:
        return self.auth_data.MAC_HIST


authenticator = AuthManager()
