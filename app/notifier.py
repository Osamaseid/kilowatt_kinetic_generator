import requests

from app.config import WEBHOOK_URL


def send_notification(payload: dict) -> None:
    """Forward a critical alert payload to the configured notification endpoint.

    Performs an HTTP POST to NOTIFICATION_WEBHOOK_URL with the alert data as
    JSON. Raises ValueError if the URL is not configured, and propagates any
    HTTP error returned by the downstream service.

    Args:
        payload: Serialisable dict containing the alert fields to forward.

    Raises:
        ValueError: NOTIFICATION_WEBHOOK_URL environment variable is not set.
        requests.HTTPError: The notification endpoint returned a non-2xx status.
    """
    if not WEBHOOK_URL:
        raise ValueError("NOTIFICATION_WEBHOOK_URL is not configured.")

    response = requests.post(WEBHOOK_URL, json=payload, timeout=5)
    response.raise_for_status()