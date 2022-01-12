import importlib
import sys
from pathlib import Path

import yapecs


###############################################################################
# Test yapecs
###############################################################################


def test_context():
    """Test yapecs context manager"""
    # Import module
    import weather
    importlib.reload(weather)

    # Check that value is as expected
    assert weather.TODAYS_TEMP_FEATURE

    # Modify configuration
    with yapecs.context(
        weather,
        weather.config.defaults,
        weather.DEFAULT_CONFIGURATION,
        Path(__file__).parent / 'config' / 'config.py'):

        # Check that value was updated
        assert not weather.TODAYS_TEMP_FEATURE

    # Check that the value was restored
    assert weather.TODAYS_TEMP_FEATURE


def test_configuration():
    """Test yapecs configuration"""
    # Import module
    import weather

    # Check that value is as expected
    assert weather.TODAYS_TEMP_FEATURE

    # Modify configuration
    yapecs.configure(
        weather.config.defaults,
        Path(__file__).parent / 'config' / 'config.py')

    # Reload
    importlib.reload(weather)

    # Check that value was updated
    assert not weather.TODAYS_TEMP_FEATURE
