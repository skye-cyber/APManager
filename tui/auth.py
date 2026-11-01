"""Authentication boundary. UI code depends on this protocol, not FileApi."""
from __future__ import annotations

from typing import Protocol, Sequence
from .models import Device


class AuthBackend(Protocol):
    def get_authenticated_macs(self) -> set[str]: ...
    def authenticate_device(self, mac: str) -> None: ...
    def block_device(self, mac: str, reason: str = "") -> None: ...
    def snapshot(self) -> Sequence[Device]: ...


class FileAuthBackend:
    """Adapter placeholder for the current FileApi JSON implementation.

    Implement this class by delegating to the existing FileApi. Do not add
    JSON paths or HTTP requests to widgets/screens.
    """
    def get_authenticated_macs(self) -> set[str]:
        raise NotImplementedError("INTEGRATION POINT: delegate to FileApi.get_authenticated_macs")

    def authenticate_device(self, mac: str) -> None:
        raise NotImplementedError("INTEGRATION POINT: delegate to FileApi.authenticate_device")

    def block_device(self, mac: str, reason: str = "") -> None:
        raise NotImplementedError("INTEGRATION POINT: delegate to FileApi.block_device")

    def snapshot(self):
        raise NotImplementedError("INTEGRATION POINT: delegate to FileApi.snapshot")
