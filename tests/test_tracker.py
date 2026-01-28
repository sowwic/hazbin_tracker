import pytest
import datetime
from datetime import timedelta

from src.hazbin_tracker.core.cards_tracker import CardsTracker


TIME_ONE_HOUR_AGO = datetime.datetime.now(datetime.UTC) - timedelta(hours=1)
TIME_ONE_HOUR_LATER = datetime.datetime.now(datetime.UTC) + timedelta(hours=1)
GET_ALL_CARDS_FUNC_SIGNATURE = "src.hazbin_tracker.core.cards_tracker.get_all_cards"


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
def mock_get_all_cards(
    mocker,
    request,
    fake_no_new_cards_data,
    fake_new_cards_data,
):
    """Mock get_all_cards to return predefined data."""
    if request.param == "no_new":
        data = fake_no_new_cards_data
    elif request.param == "new":
        data = fake_new_cards_data
    else:
        raise ValueError(request.param)

    mocker.patch(
        GET_ALL_CARDS_FUNC_SIGNATURE,
        return_value=data,
    )

    return request.param


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


@pytest.mark.parametrize(
    "mock_get_all_cards",
    ["no_new", "new"],
    indirect=True,
)
def test_run_check(
    tracker_instance,
    mock_get_all_cards,
    fake_no_new_cards_data,
    fake_new_cards_data,
):
    """Test run_check method with fake cards data."""
    if mock_get_all_cards == "no_new":
        new_cards = tracker_instance.run_check()
        assert tracker_instance._cards_data == fake_no_new_cards_data
        assert len(new_cards) == 0

    elif mock_get_all_cards == "new":
        new_cards = tracker_instance.run_check()
        assert tracker_instance._cards_data == fake_new_cards_data
        assert len(new_cards) == len(fake_new_cards_data)
