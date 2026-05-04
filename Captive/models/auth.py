from ..core.config import configmanager


class Device:
    IP: str
    MAC: str
    AT: str  # Authentication time


class Devices:
    DEVICES: list(Device)


class Schema:
    AUTHENTICATION: Devices


class AuthenticationManager:
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

    @property
    def schema() -> Schema: ...

    def readFile(self) -> Schema: ...

    def writeFile(self) -> bool: ...

    def add_device(self, mac: str, ip: str) -> bool: ...

    def removeDevice(self, mac: str) -> bool: ...

    def clearAuth(self): ...
