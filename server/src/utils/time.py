"""Utility functions for time-related operations."""

from datetime import datetime, timezone

def get_today_str() -> str:
    """Get current date in a human-readable format."""
    return datetime.now(timezone.utc).strftime("%a %b %-d, %Y")

