from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Static, Sparkline

from ..models import DashboardSnapshot
from ..widgets import EmptyState, MetricRow, SectionTitle, StatusPill


def _value(value, suffix=""):
    return "—" if value is None else f"{value}{suffix}"


class DashboardScreen(Container):
    """Dashboard composition matching the supplied APManager reference."""

    def compose(self) -> ComposeResult:
        with Horizontal(id="dashboard-grid"):
            with Vertical(classes="dashboard-column metrics-column"):
                yield SectionTitle("SYSTEM METRICS")
                yield MetricRow("CPU load                         —", id="metric-cpu")
                yield MetricRow("Memory                           —", id="metric-memory")
                yield MetricRow("Temperature                      —", id="metric-temp")
                yield MetricRow("RX errors                        —", id="metric-rx-errors")
                yield MetricRow("TX drops                         —", id="metric-tx-drops")
                yield MetricRow("Active connections               —", id="metric-connections")
            with Vertical(classes="dashboard-column traffic-column"):
                yield SectionTitle("THROUGHPUT · LAST 30s")
                yield Static("RX", classes="chart-label")
                yield Sparkline([], id="rx-sparkline")
                yield Static("TX", classes="chart-label")
                yield Sparkline([], id="tx-sparkline")
                yield Static("No throughput samples yet", id="traffic-empty", classes="empty-state")
            with Vertical(classes="dashboard-column events-column optional-panel"):
                yield SectionTitle("RECENT EVENTS")
                yield Static("No events available", id="events-empty", classes="empty-state")
                yield Vertical(id="event-list")

    def show_snapshot(self, snapshot: DashboardSnapshot) -> None:
        metrics = snapshot.metrics
        cpu = "—" if metrics.cpu_load is None else ", ".join(f"{v:.2f}" for v in metrics.cpu_load)
        memory = "—"
        if metrics.memory_used_mb is not None and metrics.memory_total_mb is not None:
            pct = metrics.memory_used_mb / max(metrics.memory_total_mb, 1) * 100
            memory = f"{metrics.memory_used_mb} MB / {metrics.memory_total_mb} MB ({pct:.0f}%)"
        self.query_one("#metric-cpu", MetricRow).update(f"CPU load                         {cpu}")
        self.query_one("#metric-memory", MetricRow).update(f"Memory                           {memory}")
        self.query_one("#metric-temp", MetricRow).update(f"Temperature                      {_value(metrics.temperature_c, ' °C')}")
        self.query_one("#metric-rx-errors", MetricRow).update(f"RX errors                        {_value(metrics.rx_errors)}")
        self.query_one("#metric-tx-drops", MetricRow).update(f"TX drops                         {_value(metrics.tx_drops)}")
        self.query_one("#metric-connections", MetricRow).update(f"Active connections               {_value(metrics.active_connections)}")

        rx = [s.rx_mbps for s in snapshot.throughput]
        tx = [s.tx_mbps for s in snapshot.throughput]
        self.query_one("#rx-sparkline", Sparkline).data = rx
        self.query_one("#tx-sparkline", Sparkline).data = tx
        self.query_one("#traffic-empty", Static).display = not (rx or tx)

        event_list = self.query_one("#event-list", Vertical)
        event_list.remove_children()
        self.query_one("#events-empty", Static).display = bool(snapshot.events)
        for event in snapshot.events[:8]:
            stamp = event.timestamp.strftime("%H:%M:%S")
            event_list.mount(Static(f"{stamp}  {event.kind.upper():<8} {event.message}", classes=f"event event-{event.severity}"))
