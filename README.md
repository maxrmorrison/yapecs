<h1 align="center">Yet Another Python Experiment Configuration System (yapecs)</h1>
<div align="center">

[![PyPI](https://img.shields.io/pypi/v/yapecs.svg)](https://pypi.python.org/pypi/yapecs)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://static.pepy.tech/badge/yapecs)](https://pepy.tech/project/yapecs)

`pip install yapecs`

</div>

`yapecs` is a Python library for experiment configuration. It is an
alternative to using JSON or YAML files, or more complex solutions such as
[`hydra`](https://hydra.cc/docs/intro/). With `yapecs`,

- Configuration files are written in Python. You do not need to learn new syntax, and your configurations can be as expressive as desired, using, e.g., classes, functions, or built-in types.
- Configuration parameters are bound to the user's module. This reduces code bloat by eliminating the need to pass a configuration dictionary or many individual values through functions.
- Integration is simple, requiring only four or five lines of code (including imports).
- `yapecs` is concise; the documentation for `yapecs` (this README) is longer than the code.


## Table of contents

- [Usage](#usage)
  * [Configuration](#configuration)
  * [Hyperparameter search](#hyperparameter-search)
  * [Importing with different configs](#importing-with-different-configs)
- [Application programming interface (API)](#application-programming-interface-api)
  * [`yapecs.configure`](#yapecsconfigure)
  * [`yapecs.grid_search`](#yapecsgrid_search)
  * [`yapecs.ArgumentParser`](#yapecsargumentparser)
- [Community examples](#community-examples)


## Usage

### Configuration

Say we are creating a `weather` module to predict tomorrow's temperature
given two features: 1) today's temperature and 2) the average temperature
during previous years. Our default configuration file
(e.g., `weather/config/defaults.py`) might look like the following.

```python
# Number of items in a batch
BATCH_SIZE = 64

# Optimizer learning rate
LEARNING_RATE = 1e-4

# Whether to use today's temperature as a feature
TODAYS_TEMP_FEATURE = True

# Whether to use the average temperature as a feature
AVERAGE_TEMP_FEATURE = True
```

Say we want to run an experiment without using today's temperature as
a feature. We can create a new configuration file (e.g., `config.py`) with
just the module name and the changed parameters.

```python
MODULE = 'weather'

# Whether to use today's temperature as a feature
TODAYS_TEMP_FEATURE = False
```

Using `yapecs`, we pass our new file using the `--config` parameter. For
example, if our `weather` module has a training entrypoint `train`, we can
use the following.

```bash
python -m weather.train --config config.py
```

You can also pass a list of configuration files. This will apply all
configuration files with a matching `MODULE` name, in order.

```bash
python -m weather.train --config config-00.py config-01.py ...
```

Within the `weather` module, we make two changes. First, we add the following to module root initialization file `weather/__init__.py`.

```python
###############################################################################
# Configuration
###############################################################################


# Default configuration parameters to be modified
from .config import defaults

# Modify configuration
import yapecs
yapecs.configure('weather', defaults)

# Import configuration parameters
from .config.defaults import *


###############################################################################
# Module imports
###############################################################################


# Your module root imports go here
pass
```

This assumes that default configuration values are saved in
`weather/config/defaults.py`. You can also define configuration values that
depend on other configuration values, and control the import order relative to configuration. Using our `weather` module example, we may want to keep track of the total number of features (e.g., to initialize a machine learning model). To do this, we create a file `weather/config/static.py` containing the following.

```python
import weather

# Total number of features
NUM_FEATURES = (
    int(weather.TODAYS_TEMP_FEATURE) +
    int(weather.AVERAGE_TEMP_FEATURE))
```

We update the module root initialization as follows.

```python
...

# Import configuration parameters
from .config.defaults import *
from .config.static import *  # Import dependent parameters after configuration

###############################################################################
# Module imports
###############################################################################

...
```

The second change we make is to add `--config` as a command-line option. We created a lightweight replacement for `argparse.ArgumentParser`, called `yapecs.ArgumentParser`, which does this.

### Hyperparameter search

To perform a hyperparamter search, you can write a single config file containing values over which to perform a grid search.

Here is a commented example config which performs a grid search over the values for `HIDDEN_CHANNELS`, `NUM_HIDDEN_LAYERS`, and `KERNEL_SIZE`:

```py
MODULE = 'ppgs'

from pathlib import Path
from itertools import product
import torch

import ppgs
import yapecs

# Make sure this code only runs once, when ppgs is being configured.
#  Otherwise, the progress value might be incremented multiple times.
if hasattr(ppgs, "defaults"):

    progress_file = Path(__file__).parent / 'causal_transformer_search.progress'

    # Values that we want to search over
    hidden_channels = [64, 128, 256, 512]
    num_hidden_layers = [3, 4, 5]
    kernel_size = [3, 5, 7]

    # Here we use `yapecs.grid_search` which handles loading and saving the progress file and computing the current combination of config values.
    HIDDEN_CHANNELS, NUM_HIDDEN_LAYERS, KERNEL_SIZE = yapecs.grid_search(
        progress_file,
        hidden_channels,
        num_hidden_layers,
        kernel_size
    )

    # Name the config using the specific values for this run.
    CONFIG = f"causal_transformer_search/{HIDDEN_CHANNELS}-{NUM_HIDDEN_LAYERS}-{KERNEL_SIZE}".replace('.', '_')
    print(CONFIG)


# Additional config values

# Dimensionality of input representation
INPUT_CHANNELS = 80

# Input representation
REPRESENTATION = 'mel'

# Number of training steps
STEPS = 50_000

IS_CAUSAL = True
CHECKPOINT_INTERVAL = 25_000  # steps
```

Then you can perform the search by running a command similar to

```sh
while python -m ppgs.train --config causal_transformer_search.py; do :; done
```

which will run the training repeatedly, incrementing the progress index and choosing the appropriate config values each time until the search is complete.

## Importing with different configs

When working with and comparing multiple configs, you can load the same module multiple times with different configs by using `yapecs.import_with_configs`.

```py
import yapecs
import weather

weather_no_humidity = yapecs.import_with_configs(weather, ['no-humidity.py'])
weather_no_windspeed = yapecs.import_with_configs(weather, ['no-humidity.py'])

```

## Application programming interface (API)

### `yapecs.configure`

```python
def configure(
    module_name: str,
    config_module: ModuleType,
    config: Optional[Path] = None
) -> None:
    """Update the configuration values

    Arguments
        module_name
            The name of the module to configure
        config_module
            The submodule containing configuration values
        config
            The Python file containing the updated configuration values.
            If not provided and the ``--config`` parameter is a command-line
            argument, the corresponding argument is used as the configuration
    """
```


### `yapecs.grid_search`

```python
def grid_search(progress_file: Union[str, os.PathLike], *args: Tuple) -> Tuple:
    """Perform a grid search over configuration arguments

    Arguments
        progress_file
            File to store current search progress
        args
            Lists of argument values to perform grid search over

    Returns
        current_args
            The arguments that should be used by the current process
    """
```

### `yapecs.ArgumentParser`

This is a lightweight wrapper around [`argparse.ArgumentParser`](https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser). The only changes are in the `__init__` and `parse_args` functions.

```python
class ArgumentParser(argparse.ArgumentParser):

    def parse_args(
        self,
        args: Optional[List[str]] = None,
        namespace: Optional[argparse.Namespace] = None
    ) -> argparse.Namespace:
        """Parse arguments while allowing unregistered config argument

        Arguments
            args
                Arguments to parse. Default is taken from sys.argv.
            namespace
                Object to hold the attributes. Default is an empty Namespace.

        Returns
            Namespace containing program arguments
        """
```


## Community examples

The following are code repositories that utilize `yapecs` for configuration. If you would like to see your repo included, please open a pull request.

- [`emphases`](https://github.com/interactiveaudiolab/emphases)
- [`penn`](https://github.com/interactiveaudiolab/penn)
- [`ppgs`](https://github.com/interactiveaudiolab/ppgs)
- [`pyfoal`](https://github.com/maxrmorrison/pyfoal)
