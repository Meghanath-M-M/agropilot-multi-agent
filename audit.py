"""
AgroPilot Audit Logger
Structured JSONL audit logging for advisory lifecycle events.
Provides a compliance-ready trail of all advisory generation,
approval, and delivery actions.
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# Log file lives next to the application
_LOG_DIR = Path(__file__).resolve().parent / "logs"
_LOG_FILE = _LOG_DIR / "audit.jsonl"


class AuditLogger:
    """Appends structured JSON events to an audit log file.

    Each line in audit.jsonl is a self-contained JSON object with:
    - event: the action type
    - timestamp: ISO-8601 UTC timestamp
    - payload: event-specific data
    """

    def __init__(self) -> None:
        _LOG_DIR.mkdir(exist_ok=True)

    def _write(self, event: str, payload: Dict) -> None:
        """Write a single audit entry."""
        entry = {
            "event": event,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **payload,
        }
        try:
            with open(_LOG_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception as e:
            logger.error(f"Audit log write failed: {e}")

    # ── Advisory Lifecycle Events ──

    def log_advisory_generated(self, advisory: Dict) -> None:
        """Log when a new advisory is generated."""
        self._write("advisory_generated", {
            "location": advisory.get("farmer_location"),
            "crop": advisory.get("crop", {}).get("crop_name"),
            "confidence": advisory.get("advisory_confidence"),
            "agent_sources": advisory.get("agent_sources"),
            "errors": advisory.get("errors", []),
        })

    def log_advisory_approved(self, advisory: Dict, phone: str) -> None:
        """Log when an expert approves an advisory."""
        self._write("advisory_approved", {
            "location": advisory.get("farmer_location"),
            "crop": advisory.get("crop", {}).get("crop_name"),
            "farmer_phone_last4": phone[-4:] if phone else "N/A",
        })

    def log_advisory_rejected(self, advisory: Dict) -> None:
        """Log when an expert rejects an advisory."""
        self._write("advisory_rejected", {
            "location": advisory.get("farmer_location"),
            "crop": advisory.get("crop", {}).get("crop_name"),
        })

    def log_whatsapp_sent(self, phone: str, success: bool, message: str) -> None:
        """Log WhatsApp delivery attempt."""
        self._write("whatsapp_delivery", {
            "farmer_phone_last4": phone[-4:] if phone else "N/A",
            "success": success,
            "status_message": message[:200],
        })

    def log_whatsapp_resend(self, phone: str, success: bool) -> None:
        """Log when the Resend WhatsApp button is pressed."""
        self._write("whatsapp_resend", {
            "farmer_phone_last4": phone[-4:] if phone else "N/A",
            "success": success,
        })
