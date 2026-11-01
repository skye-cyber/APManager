"""All application/backend integration lives here.

Replace the explicit integration points with calls into core/, Captive/core/
and Captive/monitoring/. Never import these backend modules from a screen.
"""
from __future__ import annotations

from .models import DashboardSnapshot, Device


def get_dashboard_snapshot() -> DashboardSnapshot:
    """Return one coherent UI snapshot from the existing backend."""
    raise NotImplementedError(
        "INTEGRATION POINT: assemble status from core and Captive monitoring"
    )


def get_devices() -> list[Device]:
    """Return the current device snapshot (wire this to the existing snapshot API)."""
    raise NotImplementedError(
        "INTEGRATION POINT: wire to the existing device snapshot implementation"
    )


def set_hotspot_enabled(enabled: bool) -> None:
    """Start/stop hotspot through the process-aware service manager."""
    raise NotImplementedError("INTEGRATION POINT: wire to core hotspot lifecycle")


def restart_captive_portal() -> None:
    """Restart the captive portal without coupling dnsmasq to the TUI process."""
    raise NotImplementedError("INTEGRATION POINT: wire to Captive/core portal lifecycle")


def set_device_blocked(mac: str, blocked: bool, reason: str = "") -> None:
    raise NotImplementedError("INTEGRATION POINT: wire to AuthBackend")


def get_interfaces() -> list[dict[str, str]]:
    raise NotImplementedError("INTEGRATION POINT: wire to core interface discovery")


def get_logs(limit: int = 200) -> list[str]:
    raise NotImplementedError("INTEGRATION POINT: wire to Captive/monitoring log source")


def shutdown_cleanup() -> None:
    """Clean up parent-bound hostapd resources on normal TUI exit.

    Do not indiscriminately stop independent dnsmasq processes here.
    """
    raise NotImplementedError("INTEGRATION POINT: implement hostapd parent-process cleanup")
