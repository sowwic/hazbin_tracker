import datetime

from pydantic import BaseModel, ConfigDict, Field


class CardVariant(BaseModel):
    """A purchasable variant of a card."""

    model_config = ConfigDict(extra="ignore")

    available: bool = False


class HazbinCard(BaseModel):
    """A trading card of the Hazbin Hotel store.

    Only the fields the app uses are kept, the rest of the store's product is ignored.
    """

    model_config = ConfigDict(extra="ignore")

    id: int | None = None
    title: str = ""
    published_at: datetime.datetime
    variants: list[CardVariant] = Field(default_factory=list)

    @property
    def is_available(self) -> bool:
        """Whether any variant of the card can be purchased.

        Returns:
            bool: True if at least one variant is available.
        """
        return any(variant.available for variant in self.variants)
