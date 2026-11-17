import logging

import requests

LOGGER = logging.getLogger(__name__)

MESSAGES_URL = "https://api.pushover.net/1/messages.json"
VALIDATE_URL = "https://api.pushover.net/1/users/validate.json"
REQUEST_TIMEOUT = 10
REJECTED_STATUS = 400


class PushoverError(Exception):
    """Raised when Pushover can't be reached or refuses a request."""


def send_notification(app_key: str, user_key: str, title: str, message: str) -> None:
    """Send a push notification.

    Args:
        app_key (str): API token of the Pushover application.
        user_key (str): Pushover user key to notify.
        title (str): Notification title.
        message (str): Notification text.

    Raises:
        PushoverError: If the request fails or Pushover rejects it.
    """
    try:
        response = requests.post(
            MESSAGES_URL,
            data={
                "token": app_key,
                "user": user_key,
                "title": title,
                "message": message,
            },
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise PushoverError(f"Failed to send Pushover notification: {exc}") from exc


def validate_keys(app_key: str, user_key: str) -> bool:
    """Check the keys with Pushover without sending a notification.

    Args:
        app_key (str): API token of the Pushover application.
        user_key (str): Pushover user key.

    Returns:
        bool: True if the keys are valid and the user has an active device,
            False if Pushover rejected them.

    Raises:
        PushoverError: If Pushover can't be reached or fails.
    """
    try:
        response = requests.post(
            VALIDATE_URL,
            data={"token": app_key, "user": user_key},
            timeout=REQUEST_TIMEOUT,
        )
    except requests.RequestException as exc:
        raise PushoverError(f"Failed to reach Pushover: {exc}") from exc
    if response.status_code == REJECTED_STATUS:
        LOGGER.warning(f"Pushover rejected the keys: {response.text}")
        return False
    try:
        response.raise_for_status()
    except requests.RequestException as exc:
        raise PushoverError(f"Pushover validation failed: {exc}") from exc
    return True
