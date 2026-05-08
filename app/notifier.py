import requests

from app.config import WEBHOOK_URL

_ALERT_LABEL = {
    "CRITICAL_PHASE_LOSS": "Phase Loss Detected",
}


def send_notification(payload: dict) -> None:
    """Forward a critical alert payload to the configured notification endpoint.

    Enriches the raw telemetry dict with a human-readable alert_summary before
    posting, so the destination (webhook.site, Discord, etc.) displays a
    meaningful message without further transformation.

    Args:
        payload: Serialisable dict containing the alert fields to forward.

    Raises:
        ValueError: NOTIFICATION_WEBHOOK_URL environment variable is not set.
        requests.HTTPError: The notification endpoint returned a non-2xx status.
    """
    if not WEBHOOK_URL:
        raise ValueError("NOTIFICATION_WEBHOOK_URL is not configured.")

    status = payload.get("status_code", "UNKNOWN")
    enriched = {
        **payload,
        "alert_summary": _ALERT_LABEL.get(status, "Low Fuel Warning"),
        "source": "Kilowatt Kinetic Middleware",
    }

    response = requests.post(WEBHOOK_URL, json=enriched, timeout=5)
    response.raise_for_status()