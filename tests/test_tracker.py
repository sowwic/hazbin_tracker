import pytest
import datetime
from datetime import timedelta

from src.hazbin_tracker.core.cards_tracker import CardsTracker
from src.hazbin_tracker.core.constants import MAX_CONSECUTIVE_FAILED_CHECKS
from src.hazbin_tracker.core.scrapper import ScraperError


TIME_ONE_HOUR_AGO = datetime.datetime.now(datetime.UTC) - timedelta(hours=1)
TIME_ONE_HOUR_LATER = datetime.datetime.now(datetime.UTC) + timedelta(hours=1)


@pytest.fixture
def fake_no_new_cards_data():
    """Mock data for card that was published one hour in the past.

    This data is expected to not trigger new card check.

    Returns:
        list[dict]: mock old card data
    """
    return [
        {
            "title": "Old Hazbin Card",
            "published_at": TIME_ONE_HOUR_AGO.isoformat(),
        }
    ]


@pytest.fixture
def fake_new_cards_data():
    """Mock data for card that was published one hour from current time.

    This data is expected to trigger new card check.

    Returns:
        list[dict]: mock new card data
    """
    return [
        {
            "title": "New Hazbin Card",
            "published_at": TIME_ONE_HOUR_LATER.isoformat(),
        }
    ]


@pytest.fixture
def tracker_instance(mocker):
    """Tracker instance with mocked properties and methods."""
    mocker.patch.object(CardsTracker, "on_new_cards_found", return_value=None)
    mocker.patch.object(CardsTracker, "start_periodic_check_timer", return_value=None)
    mocker.patch.object(CardsTracker, "create_cache", return_value=None)
    mocker.patch.object(CardsTracker, "populate_cards_data", return_value=None)
    mocker.patch.object(CardsTracker, "_create_signals", return_value=None)
    mocker.patch.object(CardsTracker, "record_time", return_value=None)
    mocker.patch.object(
        CardsTracker,
        "__repr__",
        return_value="Test Tracker",
    )

    tracker = CardsTracker()
    tracker._check_timer = None
    tracker._last_check_time = datetime.datetime.now(datetime.UTC)

    return tracker


def test_on_check_finished_no_new(tracker_instance, fake_no_new_cards_data):
    """Cards published before the last check are not reported."""
    with_signal = []
    tracker_instance.check_completed.connect(with_signal.append)

    tracker_instance._on_check_finished(fake_no_new_cards_data)

    assert tracker_instance._cards_data == fake_no_new_cards_data
    assert with_signal == [[]]


def test_on_check_finished_new(tracker_instance, fake_new_cards_data):
    """Cards published after the last check are reported."""
    found = []
    tracker_instance.new_cards_found.connect(found.append)

    tracker_instance._on_check_finished(fake_new_cards_data)

    assert tracker_instance._cards_data == fake_new_cards_data
    assert found == [fake_new_cards_data]


def test_run_check_runs_in_background(qtbot, tracker_instance, mocker):
    """run_check starts a worker and results arrive through signals."""
    mocker.patch(
        "src.hazbin_tracker.core.cards_tracker.CardsScraper.get_all_cards",
        return_value=[],
    )
    with qtbot.waitSignal(tracker_instance.check_completed, timeout=5000):
        assert tracker_instance.run_check() is True
        assert tracker_instance.is_check_running
        assert tracker_instance.run_check() is False  # overlap guard
    assert not tracker_instance.is_check_running


def test_run_check_failure_emits_check_failed(qtbot, tracker_instance, mocker):
    """A scraper failure is reported via check_failed and keeps the data."""
    mocker.patch(
        "src.hazbin_tracker.core.cards_tracker.CardsScraper.get_all_cards",
        side_effect=ScraperError("429"),
    )
    tracker_instance._cards_data = [{"title": "keep"}]
    with qtbot.waitSignal(tracker_instance.check_failed, timeout=5000) as blocker:
        tracker_instance.run_check()
    assert blocker.args == ["429"]
    assert tracker_instance._cards_data == [{"title": "keep"}]
    assert not tracker_instance.is_check_running


def test_repeated_failures_notify_once_and_reset_on_success(tracker_instance):
    """The streak signal fires at the threshold only and success resets it."""
    streaks = []
    tracker_instance.repeated_checks_failed.connect(streaks.append)

    for _ in range(MAX_CONSECUTIVE_FAILED_CHECKS + 2):
        tracker_instance._on_check_failed("429")

    assert streaks == [MAX_CONSECUTIVE_FAILED_CHECKS]
    assert tracker_instance.failed_checks_in_a_row == MAX_CONSECUTIVE_FAILED_CHECKS + 2

    tracker_instance._on_check_finished([])
    assert tracker_instance.failed_checks_in_a_row == 0

    for _ in range(MAX_CONSECUTIVE_FAILED_CHECKS):
        tracker_instance._on_check_failed("429")
    assert streaks == [MAX_CONSECUTIVE_FAILED_CHECKS] * 2


def test_fewer_failures_do_not_notify(tracker_instance):
    """No streak signal below the threshold."""
    streaks = []
    tracker_instance.repeated_checks_failed.connect(streaks.append)
    for _ in range(MAX_CONSECUTIVE_FAILED_CHECKS - 1):
        tracker_instance._on_check_failed("429")
    assert streaks == []
