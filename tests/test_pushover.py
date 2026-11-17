import pytest
import requests

from hazbin_tracker.core import pushover
from hazbin_tracker.core.pushover import PushoverError, send_notification, validate_keys


class FakeResponse:
    """Minimal stand-in for a requests response."""

    def __init__(self, status_code=200, text=""):
        """Store the fake status and body."""
        self.status_code = status_code
        self.text = text

    def raise_for_status(self):
        """Raise like requests does for error statuses."""
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code}")


@pytest.fixture
def post(mocker):
    """Patch requests.post so nothing leaves the machine."""
    return mocker.patch.object(pushover.requests, "post", return_value=FakeResponse())


def test_send_notification_posts_the_message(post):
    """The keys, title and message are sent to the messages endpoint."""
    send_notification("app", "user", "Title", "Body")
    args, kwargs = post.call_args
    assert args == (pushover.MESSAGES_URL,)
    assert kwargs["data"] == {
        "token": "app",
        "user": "user",
        "title": "Title",
        "message": "Body",
    }


def test_send_notification_wraps_http_errors(post):
    """A rejected request is reported as PushoverError."""
    post.return_value = FakeResponse(500)
    with pytest.raises(PushoverError):
        send_notification("app", "user", "Title", "Body")


def test_send_notification_wraps_network_errors(post):
    """A network failure is reported as PushoverError."""
    post.side_effect = requests.ConnectionError("down")
    with pytest.raises(PushoverError):
        send_notification("app", "user", "Title", "Body")


def test_validate_keys_never_hits_the_messages_endpoint(post):
    """Validation uses its own endpoint, so no notification is sent."""
    assert validate_keys("app", "user") is True
    assert post.call_args.args == (pushover.VALIDATE_URL,)
    assert "message" not in post.call_args.kwargs["data"]


def test_validate_keys_rejected(post):
    """Pushover answering 400 means the keys are wrong."""
    post.return_value = FakeResponse(400, '{"errors":["user identifier is invalid"]}')
    assert validate_keys("app", "user") is False


def test_validate_keys_server_error(post):
    """Other failures are errors, not an answer about the keys."""
    post.return_value = FakeResponse(503)
    with pytest.raises(PushoverError):
        validate_keys("app", "user")
