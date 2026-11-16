from PySide6 import QtCore
from pydantic import Field
from json_config.api import LayeredConfig, ConfigValues, ConfigLayer

from ..core.constants import (
    CONFIG_FILE_PATH,
    CHECK_HISTORY_SIZE_MINIMUM,
    TRACKER_CHECK_FREQUENCY_MINIMUM,
)


class PushoverConfigValues(ConfigValues):
    """Pushover notification settings."""

    enabled: bool = Field(default=False)
    user_key: str = Field(default_factory=str)
    app_key: str = Field(default_factory=str)


class CardsTrackerConfigValues(ConfigValues):
    """Cards tracker settings."""

    frequency_min: int = Field(default=60, ge=TRACKER_CHECK_FREQUENCY_MINIMUM)
    history_size: int = Field(default=20, ge=CHECK_HISTORY_SIZE_MINIMUM)


class HazbinAppConfigValues(ConfigValues):
    """All application settings."""

    pushover: PushoverConfigValues = Field(
        default_factory=PushoverConfigValues, alias="pushover"
    )
    cards_tracker: CardsTrackerConfigValues = Field(
        default_factory=CardsTrackerConfigValues, alias="cards_tracker"
    )


class HazbinAppConfig(LayeredConfig[HazbinAppConfigValues]):
    """Application config stored in the user config file."""

    NAME = "general"
    VALUES_CLASS = HazbinAppConfigValues
    ROOT_CONFIG_LAYER = ConfigLayer(name="root", file_path=CONFIG_FILE_PATH)

    def __init__(self):
        """Initialize config object, registering the root config layer."""
        super().__init__(layer_filter=self.ROOT_CONFIG_LAYER.name)
        self._register_root_layer()

    def _register_root_layer(self):
        """Register the root config layer unless already registered."""
        if self.ROOT_CONFIG_LAYER.name not in self.layer_manager.root_layers:
            self.layer_manager.register(self.ROOT_CONFIG_LAYER)


def get_app_config() -> HazbinAppConfig:
    """Get the config of the running application.

    Returns:
        HazbinAppConfig: config the application loaded at startup, so it has the
            values of the user's config file. Without an application a new config is
            created and resolved.
    """
    config = getattr(QtCore.QCoreApplication.instance(), "config", None)
    if config is None:
        config = HazbinAppConfig()
        config.resolve()
    return config
