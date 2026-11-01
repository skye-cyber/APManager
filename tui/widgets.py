"""Small reusable presentation widgets."""
from __future__ import annotations

from textual.widgets import Static


class SectionTitle(Static):
    DEFAULT_CLASSES = "section-title"


class MetricRow(Static):
    DEFAULT_CLASSES = "metric-row"


class StatusPill(Static):
    DEFAULT_CLASSES = "status-pill"


class EmptyState(Static):
    DEFAULT_CLASSES = "empty-state"
