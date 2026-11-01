"""APManager Textual application."""
from __future__ import annotations

import argparse
import logging
from pathlib import Path
from datetime import datetime, timedelta

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.command import Hit, Hits, Provider
from textual.widgets import Footer, Header, Static, ContentSwitcher, Button

from . import adapters
from .config_store import ConfigStore
from .models import DashboardSnapshot, ServiceState, SystemMetrics, ThroughputSample, Event, Device
from .screens.dashboard import DashboardScreen
from .screens.devices import DevicesScreen
from .screens.placeholder import PlaceholderScreen
from .screens.operations import HotspotScreen, CaptiveScreen, InterfacesScreen, LogsScreen

log = logging.getLogger(__name__)

SCREENS = (
    ("dashboard", "DASHBOARD", "1"),
    ("devices", "DEVICES", "2"),
    ("hotspot", "HOTSPOT", "3"),
    ("captive", "CAPTIVE", "4"),
    ("interfaces", "INTERFACES", "5"),
    ("logs", "LOGS", "6"),
)


class APManagerScreen(Screen):
    HORIZONTAL_BREAKPOINTS = [(0, '-narrow'), (80, '-medium'), (110, '-wide')]
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("ctrl+p", "command_palette", "Command palette", show=False),
        Binding("1", "show_dashboard", "Dashboard", show=False),
        Binding("2", "show_devices", "Devices", show=False),
        Binding("3", "show_hotspot", "Hotspot", show=False),
        Binding("4", "show_captive", "Captive", show=False),
        Binding("5", "show_interfaces", "Interfaces", show=False),
        Binding("6", "show_logs", "Logs", show=False),
        Binding("r", "refresh_data", "Refresh"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        with Horizontal(id="topline"):
            yield Static("◆ AP MANAGER", id="brand")
            yield Static("hotspot  ?   captive  ?   clients  ?   uptime  —", id="service-summary")
        with Horizontal(id="attention-strip"):
            yield Static("ATTENTION", classes="attention-label")
            yield Static("Backend status not connected", id="attention-content")
            yield Button("COMMAND PALETTE  Ctrl+P", id="command-palette-button", variant="default")
        with Horizontal(id="navigation"):
            for sid, label, key in SCREENS:
                yield Button(f"{key}  {label.title()}", id=f"nav-{sid}", classes="nav-item", variant="default")
            yield Button("PANEL  ▾", id="panel-toggle", variant="default")
        with ContentSwitcher(initial="screen-dashboard", id="screen-switcher"):
            yield DashboardScreen(id="screen-dashboard")
            yield DevicesScreen(id="screen-devices")
            yield HotspotScreen(id="screen-hotspot")
            yield CaptiveScreen(id="screen-captive")
            yield InterfacesScreen(id="screen-interfaces")
            yield LogsScreen(id="screen-logs")
        with Horizontal(id="throughput-footer"):
            yield Static("RX  —", id="footer-rx")
            yield Static("TX  —", id="footer-tx")
            yield Static("WLAN  —", id="footer-interface")
        yield Footer()

    def on_mount(self) -> None:
        self.app.set_interval(3.0, self.refresh_data)
        self.refresh_data()

    def _show(self, screen_id: str) -> None:
        self.query_one("#screen-switcher", ContentSwitcher).current = f"screen-{screen_id}"
        for sid, _, _ in SCREENS:
            self.query_one(f"#nav-{sid}", Button).variant = "primary" if sid == screen_id else "default"
        if screen_id == "devices":
            self.refresh_data()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id or ""
        if button_id.startswith("nav-"):
            self._show(button_id.removeprefix("nav-"))
        elif button_id == "panel-toggle":
            self.action_toggle_panels()
        elif button_id == "command-palette-button":
            self.app.action_command_palette()

    def action_toggle_panels(self) -> None:
        panels = self.query(".optional-panel")
        visible = any(panel.display for panel in panels)
        for panel in panels:
            panel.display = not visible
        self.notify("Secondary panels shown" if not visible else "Secondary panels hidden")

    def action_show_dashboard(self): self._show("dashboard")
    def action_show_devices(self): self._show("devices")
    def action_show_hotspot(self): self._show("hotspot")
    def action_show_captive(self): self._show("captive")
    def action_show_interfaces(self): self._show("interfaces")
    def action_show_logs(self): self._show("logs")

    def action_refresh_data(self) -> None:
        self.refresh_data()

    def refresh_data(self) -> None:
        try:
            snapshot = adapters.get_dashboard_snapshot()
        except NotImplementedError:
            snapshot = self._preview_snapshot()
            self.query_one("#attention-content", Static).update(
                "PREVIEW DATA · backend adapters are not connected"
            )
            self.query_one("#service-summary", Static).update(
                "PREVIEW  ·  hotspot UP  ·  captive UP  ·  clients 12/64"
            )
        except Exception:
            log.exception("Dashboard refresh failed")
            self.query_one("#attention-content", Static).update("Unable to refresh backend status")
            return

        self.query_one("#screen-dashboard", DashboardScreen).show_snapshot(snapshot)
        self._render_summary(snapshot)

        if self.query_one("#screen-switcher", ContentSwitcher).current == "screen-devices":
            try:
                devices = adapters.get_devices()
            except NotImplementedError:
                devices = [
                    Device("8A:21:4F:90:2C:11", "Pixel 8", "192.168.50.102", "wlan0", "authenticated", "now"),
                    Device("D4:6A:6A:31:7B:02", "ThinkPad T14", "192.168.50.108", "wlan0", "authenticated", "1m ago"),
                    Device("3C:52:82:AA:09:EF", "Unknown device", "192.168.50.114", "wlan0", "pending", "3m ago"),
                    Device("B8:27:EB:44:10:6D", "Raspberry Pi", "192.168.50.120", "wlan0", "blocked", "8m ago"),
                ]
            except Exception:
                log.exception("Device refresh failed")
                devices = []
            self.query_one("#screen-devices", DevicesScreen).show_devices(devices)

    @staticmethod
    def _preview_snapshot() -> DashboardSnapshot:
        now = datetime.now()
        return DashboardSnapshot(
            hotspot=ServiceState("hotspot", True, "running · pid 1842"),
            captive=ServiceState("captive", True, "listening · :8080"),
            interface="wlan0", hotspot_pid=1842, captive_port=8080,
            clients=12, max_clients=64, uptime="04h 38m",
            vpn_state="connected",
            metrics=SystemMetrics(
                cpu_load=(0.18, 0.24, 0.21), memory_used_mb=842,
                memory_total_mb=2048, temperature_c=47.2,
                rx_errors=2, tx_drops=0, active_connections=12,
            ),
            throughput=[
                ThroughputSample(2.1 + (i % 5) * 0.35, 0.7 + (i % 4) * 0.22)
                for i in range(30)
            ],
            events=[
                Event(now - timedelta(minutes=1), "AUTH", "Pixel 8 authenticated", "success"),
                Event(now - timedelta(minutes=3), "CLIENT", "New device detected · 3C:52:82:…", "info"),
                Event(now - timedelta(minutes=8), "POLICY", "Raspberry Pi blocked by operator", "warning"),
            ],
            alerts=[],
        )

    def _render_summary(self, snapshot: DashboardSnapshot) -> None:
        hotspot = "UP" if snapshot.hotspot.running is True else "DOWN" if snapshot.hotspot.running is False else "?"
        captive = "UP" if snapshot.captive.running is True else "DOWN" if snapshot.captive.running is False else "?"
        clients = "?" if snapshot.clients is None else str(snapshot.clients)
        maximum = "?" if snapshot.max_clients is None else str(snapshot.max_clients)
        prefix = "PREVIEW  ·  " if snapshot.hotspot_pid == 1842 else ""
        self.query_one("#service-summary", Static).update(
            f"{prefix}hotspot  {hotspot}   captive  {captive}   clients  {clients}/{maximum}   uptime  {snapshot.uptime}"
        )
        attention = " · ".join(snapshot.alerts[:3]) if snapshot.alerts else "No active alerts"
        if prefix:
            attention = "PREVIEW DATA · backend adapters are not connected"
        self.query_one("#attention-content", Static).update(attention)
        self.query_one("#footer-interface", Static).update(f"{snapshot.interface}  status")
        if snapshot.throughput:
            latest = snapshot.throughput[-1]
            self.query_one("#footer-rx", Static).update(f"RX  {latest.rx_mbps:.1f} Mb/s")
            self.query_one("#footer-tx", Static).update(f"TX  {latest.tx_mbps:.1f} Mb/s")


class APManagerCommands(Provider):
    async def search(self, query: str) -> Hits:
        app = self.app
        actions = [
            ("Refresh dashboard", app.action_refresh),
            ("Restart captive portal", app.action_restart_portal),
            ("Open dashboard", lambda: app.action_show_view("dashboard")),
            ("Open devices", lambda: app.action_show_view("devices")),
            ("Open hotspot", lambda: app.action_show_view("hotspot")),
            ("Open captive portal", lambda: app.action_show_view("captive")),
            ("Open interfaces", lambda: app.action_show_view("interfaces")),
            ("Open logs", lambda: app.action_show_view("logs")),
        ]
        for label, callback in actions:
            if query.casefold() in label.casefold():
                yield Hit(1.0, label, callback, help="APManager action")


class APManagerApp(App):
    TITLE = "AP MANAGER"
    SUB_TITLE = "Network operations console"
    CSS_PATH = None
    COMMANDS = App.COMMANDS | {APManagerCommands}
    BINDINGS = [Binding("ctrl+p", "command_palette", "Command palette", show=True)]

    def __init__(self, theme: str = "vim-dark", **kwargs):
        theme_path = Path(__file__).parent / "themes" / f"{theme}.tcss"
        if not theme_path.is_file():
            raise ValueError(f"Unknown theme: {theme}")
        super().__init__(css_path=theme_path, **kwargs)
        self.theme_name = theme
        self.config = ConfigStore()

    def on_mount(self) -> None:
        self.push_screen(APManagerScreen())

    def action_refresh(self) -> None:
        if isinstance(self.screen, APManagerScreen):
            self.screen.action_refresh_data()

    def action_show_view(self, view_id: str) -> None:
        if isinstance(self.screen, APManagerScreen):
            self.screen._show(view_id)

    def action_restart_portal(self) -> None:
        try:
            adapters.restart_captive_portal()
            self.notify("Captive portal restart requested")
        except NotImplementedError as exc:
            self.notify(str(exc), severity="warning")
        except Exception as exc:
            self.notify(f"Portal restart failed: {exc}", severity="error")

    def on_unmount(self) -> None:
        try:
            adapters.shutdown_cleanup()
        except NotImplementedError as exc:
            log.warning("Shutdown integration not configured: %s", exc)
        except Exception:
            log.exception("Shutdown cleanup failed")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ap_manager tui")
    parser.add_argument("--theme", default="vim-dark", choices=("default-dark", "slate-flat", "vim-dark", "nord-night", "monokai-pro", "dracula"))
    args = parser.parse_args(argv)
    APManagerApp(theme=args.theme).run()
    return 0
