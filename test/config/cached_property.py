MODULE = 'weather'
import weather
import yapecs

# Whether to use today's temperature as a feature
TODAYS_TEMP_FEATURE = False

# Here we use a computed property.
# Computed properties can depend on other properties.
# yapecs will automatically run this function when you
#  access `weather.AVERAGE_TEMP_FEATURE`
# this is similar to the @property decorator for classes!
# In this example, we set `compute_once=True` which means
#  that the value will be cached after the first run
@yapecs.ComputedProperty(compute_once=True)
def AVERAGE_TEMP_FEATURE():
    return weather.TODAYS_TEMP_FEATURE
