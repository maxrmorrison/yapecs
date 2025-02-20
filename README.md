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


## Table of contents

- [Usage](#usage)
  * [Configuration](#configuration)
  * [Composition](#composition)
  * [Hyperparameter search](#hyperparameter-search)
  * [Computed properties](#computed-properties)
- [Application programming interface (API)](#application-programming-interface-api)
  * [`yapecs.configure`](#yapecsconfigure)
  * [`yapecs.compose`](#yapecscompose)
  * [`yapecs.grid_search`](#yapecsgrid_search)
  * [`yapecs.ArgumentParser`](#yapecsargumentparser)
  * [`yapecs.ComputedProperty`](#yapecscomputedproperty)
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
del defaults
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

from .config.defaults import *
from .config.static import *  # Import dependent parameters last


###############################################################################
# Module imports
###############################################################################

...
```

The second change we make is to add `--config` as a command-line option. We created a lightweight replacement for `argparse.ArgumentParser`, called `yapecs.ArgumentParser`, which does this.


### Composing configured modules

When working with multiple configurations of the same module, you can load the module multiple times with different configs by using `yapecs.compose`.

```python
import yapecs
import weather

# Compose base module with configuration file
weather_compose = yapecs.compose('weather', ['config.py'])

# Test that the modules are now different
assert weather.TODAYS_TEMP_FEATURE and not weather_compose.TODAYS_TEMP_FEATURE
```


### Hyperparameter search

To perform a hyperparameter grid search, write a config file containing the lists of values to search. Below is an example. Note that we check if weather as the `defaults` attribute as a lock on whether or not it is currently being configured. This prevents the progress file from being updated multiple times erroneously.

```python
MODULE = 'weather'

import yapecs
from pathlib import Path


# Import module, but delay updating search params until after configuration
import weather
if hasattr(weather, 'defaults'):

    # Lock file to track search progress
    progress_file = Path(__file__).parent / 'grid_search.progress'

    # Values that we want to search over
    learning_rate = [1e-5, 1e-4, 1e-3]
    batch_size = [64, 128, 256]
    average_temp_feature = [True, False]

    # Get grid search parameters for this run
    LEARNING_RATE, BATCH_SIZE, AVERAGE_TEMP_FEATURE = yapecs.grid_search(
        progress_file,
        learning_rate,
        batch_size,
        average_temp_feature)


###############################################################################
# Additional configuration
###############################################################################


# Whether to use today's temperature as a feature
TODAYS_TEMP_FEATURE = False
```

You can perform the search by running, e.g.,

```bash
while python -m weather --config causal_transformer_search.py; do :; done
```

This runs training repeatedly, incrementing the progress index and choosing the appropriate config values each time until the search is complete. Running a hyperparameter search in parallel is not (yet) supported.

### Computed properties

By default, config properties are static and cannot depend on config changes made later, nor can they depend on objects created later in the initialization of the module such as a Model class.

You can use the `@ComputedProperty` decorator to mark a function as a computed property. `yapecs` will then automatically execute this function and pass the return value whenever the property is accessed, similar to `@property` decorated class functions. Here is an example config file:

```python
MODULE = 'weather'
import weather
import yapecs

# Whether to use today's temperature as a feature
TODAYS_TEMP_FEATURE = False

# Here we use a computed property.
# Computed properties can depend on other properties
#  of the module, or anything really.
# `yapecs` will automatically run this function when you
#  access `weather.AVERAGE_TEMP_FEATURE`
@yapecs.ComputedProperty(compute_once=False)
def AVERAGE_TEMP_FEATURE():
    return weather.TODAYS_TEMP_FEATURE
```

Now `weather.AVERAGE_TEMP_FEATURE` will always have the same value as `weather.TODAYS_TEMP_FEATURE`, even if the latter is changed.

Note that since `compute_once` is `False` in this example, this property will be recomputed every time it is accessed via `weather.AVERAGE_TEMP_FEATURE`. For convenience, we include an option to cache the function
output directly in the ComputedProperty instance by setting `compute_once=True` as below

```python
# This property will be cached after the first access to `weather.AVERAGE_TEMP_FEATURE`
@yapecs.ComputedProperty(compute_once=True)
def AVERAGE_TEMP_FEATURE():
    return weather.TODAYS_TEMP_FEATURE
```

Now `weather.AVERAGE_TEMP_FEATURE` will have the same value that `weather.TODAYS_TEMP_FEATURE` had whenever `weather.AVERAGE_TEMP_FEATURE` was first accessed. If `weather.TODAYS_TEMP_FEATURE` changes, `weather.AVERAGE_TEMP_FEATURE` will not change in this example.

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


### `yapecs.compose`

```python
def compose(
    module: ModuleType,
    config_paths: List[Union[str, Path]]
) -> ModuleType:
    """Compose a configured module from a base module and list of configs

    Arguments
        module
            The base module to configure
        config_paths
            A list of paths to yapecs config files

    Returns
        composed
            A new module made from the base module and configurations
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

This is a lightweight wrapper around [`argparse.ArgumentParser`](https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser) that defines and manages a `--config` parameter.

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

### `yapecs.ComputedProperty`

This class acts as a decorator which, when applied to a function, creates a new `ComputedProperty` instance wrapping the function. `yapecs` checks for `ComputedProperty` instances and separates them out from normal attributes so that they can be executed when accessed so that you get the return value instead of the function. 

The `compute_once` argument allows you to decide whether or not the property should be cached the first time it is computed, or recomputed every time. It is required (has no default value) to ensure the user is never surprised by caching behavior.

```python
class ComputedProperty():
    """A decorator for functions representing computed properties"""
    def __init__(self, compute_once: bool):
        """Mark a function as a computed property

        Arguments
            compute_once
                should the property be computed only once and then cached (True), or recomputed every time (False)
        """
```

## Community examples

The following are code repositories that utilize `yapecs` for configuration. If you would like to see your repo included, please open a pull request.

- [`emphases`](https://github.com/interactiveaudiolab/emphases) - Crowdsourced and automatic speech prominence estimation
- [`penn`](https://github.com/interactiveaudiolab/penn) - Pitch-estimating neural networks
- [`ppgs`](https://github.com/interactiveaudiolab/ppgs) - High-fidelity neural phonetic posteriorgrams
- [`pyfoal`](https://github.com/maxrmorrison/pyfoal) - Python forced alignment
