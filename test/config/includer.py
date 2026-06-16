MODULE = 'weather'
import weather
import yapecs
from pathlib import Path

# Whether to use today's temperature as a feature
TODAYS_TEMP_FEATURE = False

yapecs.include(Path(__file__).parent / 'included.py')
