MODULE = 'weather'

import yapecs
import weather
from pathlib import Path

if hasattr(weather, 'defaults'):

    progress_file = Path(__file__).parent / 'grid_search.progress'

    # Values that we want to search over
    learning_rate = [1e-5, 1e-4, 1e-3]
    batch_size = [64, 128, 256]
    average_temp_feature = [True, False]

    # yapecs.grid_search handles loading and saving the progress file as well
    # as computing the current combination of config values
    LEARNING_RATE, BATCH_SIZE, AVERAGE_TEMP_FEATURE = yapecs.grid_search(
        progress_file,
        learning_rate,
        batch_size,
        average_temp_feature)