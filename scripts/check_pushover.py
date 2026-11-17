"""Check the Pushover keys of the app config without sending a notification.

Usage:
    uv run python scripts/check_pushover.py

Exit codes: 0 keys accepted, 1 keys rejected or Pushover unreachable, 2 keys not set.
"""

import sys

from hazbin_tracker.core.config import get_app_config
from hazbin_tracker.core.pushover import PushoverError, validate_keys


def main() -> int:
    """Validate the saved Pushover keys.

    Returns:
        int: Process exit code.
    """
    pushover = get_app_config().values.pushover
    if not (pushover.app_key and pushover.user_key):
        print("Pushover app key or user key is not set in the config.")
        return 2
    try:
        valid = validate_keys(pushover.app_key, pushover.user_key)
    except PushoverError as exc:
        print(exc)
        return 1
    print("Pushover keys are valid." if valid else "Pushover rejected the keys.")
    return 0 if valid else 1


if __name__ == "__main__":
    sys.exit(main())
