"""System Metrics model - placeholder for demo."""

from dataclasses import dataclass
from datetime import datetime

@dataclass
class SystemMetrics:
    """Placeholder system metrics model."""
    id: str = "placeholder"
    metric_name: str = "demo_metric"
    created_at: datetime = None