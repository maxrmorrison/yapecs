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
@yapecs.ComputedProperty(compute_once=False)
def AVERAGE_TEMP_FEATURE():
    return weather.TODAYS_TEMP_FEATURE
