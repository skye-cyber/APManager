from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import DataTable, Static

from ..models import Device


class DevicesScreen(Container):
    def compose(self) -> ComposeResult:
        yield Static("CONNECTED DEVICES", classes="section-title")
        yield Static("Device data is supplied by the backend adapter.", classes="muted")
        yield DataTable(id="devices-table", zebra_stripes=True)

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns("DEVICE", "MAC ADDRESS", "IP ADDRESS", "INTERFACE", "STATE", "LAST SEEN")
        table.cursor_type = "row"

    def show_devices(self, devices: list[Device]) -> None:
        table = self.query_one(DataTable)
        table.clear()
        for device in devices:
            table.add_row(device.name, device.mac, device.ip_address, device.interface,
                          device.state.upper(), device.last_seen, key=device.mac)
