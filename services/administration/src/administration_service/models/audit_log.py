"""Audit Log model - placeholder for demo."""

from dataclasses import dataclass
from datetime import datetime

@dataclass
class AuditLog:
    """Placeholder audit log model."""
    id: str = "placeholder"
    action: str = "demo_action"
    created_at: datetime = None