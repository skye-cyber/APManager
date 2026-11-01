"""UI-facing data contracts. Keep backend-specific objects out of the UI."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal


@dataclass(slots=True)
class ServiceState:
    name: str
    running: bool | None = None
    detail: str = "status unavailable"


@dataclass(slots=True)
class SystemMetrics:
    cpu_load: tuple[float, float, float] | None = None
    memory_used_mb: int | None = None
    memory_total_mb: int | None = None
    temperature_c: float | None = None
    rx_errors: int | None = None
    tx_drops: int | None = None
    active_connections: int | None = None


@dataclass(slots=True)
class ThroughputSample:
    rx_mbps: float = 0.0
    tx_mbps: float = 0.0


@dataclass(slots=True)
class Event:
    timestamp: datetime
    kind: str
    message: str
    severity: Literal["info", "success", "warning", "error"] = "info"


@dataclass(slots=True)
class Device:
    mac: str
    name: str = "Unknown device"
    ip_address: str = "—"
    interface: str = "—"
    state: str = "unknown"
    last_seen: str = "—"


@dataclass(slots=True)
class DashboardSnapshot:
    hotspot: ServiceState = field(default_factory=lambda: ServiceState("hotspot"))
    captive: ServiceState = field(default_factory=lambda: ServiceState("captive"))
    interface: str = "—"
    hotspot_pid: int | None = None
    captive_port: int | None = None
    clients: int | None = None
    max_clients: int | None = None
    uptime: str = "—"
    vpn_state: str = "unknown"
    metrics: SystemMetrics = field(default_factory=SystemMetrics)
    throughput: list[ThroughputSample] = field(default_factory=list)
    events: list[Event] = field(default_factory=list)
    alerts: list[str] = field(default_factory=list)
