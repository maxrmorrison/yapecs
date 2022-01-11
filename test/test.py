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
    import testmodule
    importlib.reload(testmodule)

    # Check that value is as expected
    assert testmodule.TODAYS_TEMP_FEATURE

    # Modify configuration
    with yapecs.context(
        testmodule,
        testmodule.config.defaults,
        testmodule.DEFAULT_CONFIGURATION,
        Path(__file__).parent / 'config' / 'config.py'):

        # Check that value was updated
        assert not testmodule.TODAYS_TEMP_FEATURE

    # Check that the value was restored
    assert testmodule.TODAYS_TEMP_FEATURE


def test_configuration():
    """Test yapecs configuration"""
    # Import module
    import testmodule

    # Check that value is as expected
    assert testmodule.TODAYS_TEMP_FEATURE

    # Modify configuration
    yapecs.configure(
        testmodule.config.defaults,
        Path(__file__).parent / 'config' / 'config.py')

    # Reload
    importlib.reload(testmodule)

    # Check that value was updated
    assert not testmodule.TODAYS_TEMP_FEATURE
