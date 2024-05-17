import importlib
from pathlib import Path

import yapecs


###############################################################################
# Test yapecs
###############################################################################


def test_compose():
    """Test yapecs configuration composition"""
    # Import module
    import weather

    # Check that value is as expected
    assert weather.TODAYS_TEMP_FEATURE

    # Modify configuration
    weather_compose = yapecs.compose(
        weather,
        [Path(__file__).parent / 'config' / 'config.py'])

    # Check that value was updated
    assert weather.TODAYS_TEMP_FEATURE
    assert not weather_compose.TODAYS_TEMP_FEATURE


def test_configuration():
    """Test yapecs configuration"""
    # NOTE - This is just for testing purposes and is not a valid way to
    #        swap configuration files. Specifically, this will not properly
    #        reload dependent static variables.

    # Import module
    import weather

    # Check that value is as expected
    assert weather.TODAYS_TEMP_FEATURE

    # Modify configuration
    yapecs.configure(
        'weather',
        weather.config.defaults,
        Path(__file__).parent / 'config' / 'config.py')

    # Reload
    importlib.reload(weather)

    # Check that value was updated
    assert not weather.TODAYS_TEMP_FEATURE
