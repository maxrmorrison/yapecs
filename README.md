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

**TODO**


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
TODO
```


### `yapecs.ArgumentParser`

```python
TODO
```


## Community examples

The following are code repositories that utilize `yapecs` for configuration. If you would like to see your repo included, please open a pull request.

- [`emphases`](https://github.com/interactiveaudiolab/emphases)
- [`penn`](https://github.com/interactiveaudiolab/penn)
- [`ppgs`](https://github.com/interactiveaudiolab/ppgs)
- [`pyfoal`](https://github.com/maxrmorrison/pyfoal)
