from hazbin_tracker.core.models import HazbinCard


def test_card_ignores_unknown_fields_and_parses_date():
    """Extra store fields are dropped and the publish date becomes a datetime."""
    card = HazbinCard.model_validate(
        {
            "id": 1,
            "title": "Vox",
            "published_at": "2026-10-01T10:00:00-04:00",
            "body_html": "<p>ignored</p>",
        }
    )
    assert card.published_at.year == 2026
    assert "body_html" not in card.model_dump()


def test_is_available_needs_an_available_variant():
    """A card is available when any of its variants is."""
    published_at = "2026-10-01T10:00:00+00:00"
    sold_out = HazbinCard(published_at=published_at, variants=[{"available": False}])
    open_card = HazbinCard(
        published_at=published_at, variants=[{"available": False}, {"available": True}]
    )
    assert not sold_out.is_available
    assert open_card.is_available
    assert not HazbinCard(published_at=published_at).is_available
