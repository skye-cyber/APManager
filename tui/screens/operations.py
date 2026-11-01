"""Operational screens for APManager. Presentation only; integrations stay in adapters."""
from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Static, DataTable, Input, Select, TextArea, Switch

from ..widgets import SectionTitle


class HotspotScreen(Container):
    def compose(self) -> ComposeResult:
        with Horizontal(classes="screen-heading"):
            yield Static("HOTSPOT", classes="eyebrow")
            yield Static("RADIO & SERVICE CONFIGURATION", classes="muted")
            yield Static("LOCAL DRAFT", classes="state-chip", id="hotspot-draft-state")
        with Horizontal(id="hotspot-layout"):
            with Vertical(classes="form-column"):
                yield Static("01  RADIO", classes="section-title")
                yield Static("Wireless interface", classes="field-label")
                yield Input(value="wlan0", disabled=True, id="hotspot-interface")
                yield Static("Network name · SSID", classes="field-label")
                yield Input(value="APManager-Guest", id="hotspot-ssid")
                yield Static("Radio channel", classes="field-label")
                yield Select([("Auto", "auto"), ("1 · 2.4 GHz", "1"), ("6 · 2.4 GHz", "6"), ("11 · 2.4 GHz", "11"), ("36 · 5 GHz", "36")], value="auto", id="hotspot-channel")
                yield Static("02  SECURITY", classes="section-title")
                yield Static("Security mode", classes="field-label")
                yield Select([("WPA2-Personal", "wpa2"), ("WPA3-Personal", "wpa3"), ("Open network", "open")], value="wpa2", id="hotspot-security")
                yield Static("Passphrase", classes="field-label")
                yield Input(value="••••••••••••", password=True, id="hotspot-passphrase")
                with Horizontal(classes="action-row"):
                    yield Static("[S] SAVE DRAFT", classes="key-hint")
                    yield Static("[A] APPLY  ·  [R] REVERT", classes="key-hint")
            with Vertical(classes="preview-column optional-panel"):
                yield Static("CONFIGURATION PREVIEW", classes="section-title")
                yield Static("hostapd · rendered configuration", classes="muted")
                yield Static("interface=wlan0\nssid=APManager-Guest\nchannel=auto\nwpa=2\nwpa_key_mgmt=WPA-PSK\nrsn_pairwise=CCMP", id="hotspot-preview", classes="code-preview")
                yield Static("SERVICE STATUS", classes="section-title")
                yield Static("●  hostapd     STATUS UNAVAILABLE", classes="status-line warning")
                yield Static("●  dnsmasq     STATUS UNAVAILABLE", classes="status-line muted")
                yield Static("Changes remain local until the backend apply integration is connected.", classes="helper-note")


class CaptiveScreen(Container):
    def on_mount(self) -> None:
        self.query_one("#vpn-policy-table", DataTable).add_columns("INTERFACE", "TYPE", "POLICY", "STATE")

    def compose(self) -> ComposeResult:
        with Horizontal(classes="screen-heading"):
            yield Static("CAPTIVE PORTAL", classes="eyebrow")
            yield Static("AUTHENTICATION & ACCESS POLICY", classes="muted")
        with Horizontal(id="captive-overview"):
            with Vertical(classes="stat-card"):
                yield Static("PORTAL SERVICE", classes="card-label")
                yield Static("UNKNOWN", classes="big-status warning")
                yield Static("No live adapter connected", classes="muted")
            with Vertical(classes="stat-card"):
                yield Static("AUTHENTICATED", classes="card-label")
                yield Static("—", classes="big-number")
                yield Static("Current active sessions", classes="muted")
            with Vertical(classes="stat-card"):
                yield Static("PENDING", classes="card-label")
                yield Static("—", classes="big-number")
                yield Static("Awaiting authorization", classes="muted")
        with Horizontal(id="captive-content"):
            with Vertical(classes="policy-column"):
                yield Static("VPN INTERFACE POLICY", classes="section-title")
                yield Static("Choose the policy applied to new flows. Existing connections are not retroactively changed.", classes="helper-note")
                table = DataTable(id="vpn-policy-table", zebra_stripes=True)
                yield table
            with Vertical(classes="auth-column optional-panel"):
                yield Static("RECENT AUTHENTICATION", classes="section-title")
                yield Static("No authentication events available", classes="empty-state")
                yield Static("Adapter integration required for live sessions and policy changes.", classes="helper-note")


class InterfacesScreen(Container):
    def on_mount(self) -> None:
        self.query_one("#interfaces-table", DataTable).add_columns("NAME", "TYPE", "STATE", "ADDRESS")

    def compose(self) -> ComposeResult:
        with Horizontal(classes="screen-heading"):
            yield Static("INTERFACES", classes="eyebrow")
            yield Static("LINK STATE · ADDRESSING · RADIO", classes="muted")
        with Horizontal(id="interfaces-layout"):
            with Vertical(classes="interfaces-list"):
                yield Static("DISCOVERED INTERFACES", classes="section-title")
                table = DataTable(id="interfaces-table", zebra_stripes=True)
                yield table
            with Vertical(classes="interface-inspector optional-panel"):
                yield Static("INTERFACE INSPECTOR", classes="section-title")
                yield Static("wlan0", classes="inspector-title")
                yield Static("WIRELESS · PRIMARY", classes="eyebrow")
                yield Static("Link state       UNKNOWN\nIPv4 address     —\nMAC address      —\nDriver           —\nPHY              —\nChannel          —", id="interface-details", classes="detail-block")
                yield Static("TRAFFIC COUNTERS", classes="section-title")
                yield Static("RX packets       —\nTX packets       —\nRX errors        —\nTX dropped       —", classes="detail-block")


class LogsScreen(Container):
    def compose(self) -> ComposeResult:
        with Horizontal(classes="screen-heading"):
            yield Static("SYSTEM LOGS", classes="eyebrow")
            yield Static("SERVICE EVENTS & DIAGNOSTICS", classes="muted")
        with Horizontal(id="log-toolbar"):
            yield Input(placeholder="Filter messages…", id="log-search")
            yield Select([("All severity", "all"), ("Errors", "error"), ("Warnings", "warning"), ("Info", "info")], value="all", id="log-severity")
            yield Select([("All sources", "all"), ("hostapd", "hostapd"), ("dnsmasq", "dnsmasq"), ("captive", "captive"), ("kernel", "kernel"), ("auth", "auth")], value="all", id="log-source")
            yield Static("FOLLOW  ●", classes="state-chip")
        with Horizontal(id="log-stream-heading"):
            yield Static("TIME", classes="log-time")
            yield Static("SOURCE", classes="log-source")
            yield Static("SEVERITY", classes="log-level")
            yield Static("MESSAGE", classes="log-message")
        yield Vertical(id="log-stream", classes="log-stream")
        yield Static("Live stream unavailable · connect the log adapter to populate this view.", classes="helper-note")
