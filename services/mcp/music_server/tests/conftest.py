import pytest
from podforge_music_mcp import config


@pytest.fixture(autouse=True)
def clear_settings_cache() -> None:
    config.get_settings.cache_clear()
    yield  # type: ignore[misc]
    config.get_settings.cache_clear()
