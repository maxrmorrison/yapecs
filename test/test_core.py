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

    # re-import with composed configuration
    weather_compose = yapecs.compose(
        'weather',
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

def test_grid_search():
    """Test yapecs grid_search"""
    import weather

    config_file = Path(__file__).parent / 'config' / 'grid_search.py'
    progress_file = Path(__file__).parent / 'config' / 'grid_search.progress'
    if progress_file.exists():
        progress_file.unlink()

    weather_first = yapecs.compose(
        'weather', [config_file])
    
    assert weather_first.LEARNING_RATE == 1e-5
    assert weather_first.BATCH_SIZE == 64
    assert weather_first.AVERAGE_TEMP_FEATURE == True

    weather_second = yapecs.compose(
        'weather', [config_file])
    
    assert weather_second.LEARNING_RATE == 1e-5
    assert weather_second.BATCH_SIZE == 64
    assert weather_second.AVERAGE_TEMP_FEATURE == False

    weather_third = yapecs.compose(
        'weather', [config_file])
    
    assert weather_third.LEARNING_RATE == 1e-5
    assert weather_third.BATCH_SIZE == 128
    assert weather_third.AVERAGE_TEMP_FEATURE == True

def test_property():
    """Test yapecs computed properties"""

    # use compose because it's the easiest way to mimic actual usage
    _weather = yapecs.compose('weather', [Path(__file__).parent / 'config' / 'property.py'])

    assert not _weather.TODAYS_TEMP_FEATURE
    assert not _weather.AVERAGE_TEMP_FEATURE

    # unrealistic use case, but demonstrates dynamic nature of properties
    _weather.TODAYS_TEMP_FEATURE = True

    assert _weather.TODAYS_TEMP_FEATURE
    assert _weather.AVERAGE_TEMP_FEATURE

def test_cached_property():
    """Test caching (compute_once) of yapecs computed properties"""

    # use compose because it's the easiest way to mimic actual usage
    _weather = yapecs.compose('weather', [Path(__file__).parent / 'config' / 'cached_property.py'])

    assert not _weather.TODAYS_TEMP_FEATURE
    assert not _weather.AVERAGE_TEMP_FEATURE

    # unrealistic use case, but demonstrates dynamic nature of properties
    _weather.TODAYS_TEMP_FEATURE = True

    assert _weather.TODAYS_TEMP_FEATURE
    assert not _weather.AVERAGE_TEMP_FEATURE