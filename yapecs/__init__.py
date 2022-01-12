"""Yet Another Python Experiment Configuration System (YAPECS)

``yapecs`` is a Python library for experiment configuration. It is an
alternative to using JSON or YAML files, or more complex solutions such as
`hydra <https://hydra.cc/docs/intro/>`_. With ``yapecs``,

* Configuration files are written in Python. You do not need to learn new
  syntax, and your configurations can be as expressive as desired, using, e.g.,
  classes, functions, or built-in types.

* Configuration parameters are bound to the user's module. This reduces code
  bloat by eliminating the need to pass a configuration dictionary or many
  individual values through functions.

* Integration is simple, requiring only four or five lines of code (including
  imports).


Installation
============

::

    pip install yapecs


Configuration files
===================


Say we are creating a ``weather`` module to predict tomorrow's temperature
given two features: 1) today's temperature and 2) the average temperature
during previous years. Our default configuration file
(e.g., ``weather/config/defaults.py``) might look like the following ::

    # Number of items in a batch
    BATCH_SIZE = 64

    # Optimizer learning rate
    LEARNING_RATE = 1e-4

    # Whether to use today's temperature as a feature
    TODAYS_TEMP_FEATURE = True

    # Whether to use the average temperature as a feature
    AVERAGE_TEMP_FEATURE = True


Say we want to run an experiment without using today's temperature as
a feature. We can create a new configuration file (e.g., ``config.py``) with
just the changed parameters. ::

    TODAYS_TEMP_FEATURE = False

Using ``yapecs``, we pass our new file using the ``--config`` parameter. For
example, if our ``weather`` module has a training entrypoint ``train``, we can
use the following ::

    python -m weather.train <args> --config config.py


Usage
=====

``yapecs`` can be integrated into an entire module by adding the following to the
top of ``<module>/__init__.py`` ::

    ###############################################################################
    # Configuration
    ###############################################################################


    # Default configuration parameters to be modified
    from .config import defaults

    # Modify configuration
    import yapecs
    yapecs.configure(defaults)

    # Import configuration parameters
    from .config.defaults import *
    from .config.static import *


    ###############################################################################
    # Module imports
    ###############################################################################


    # Your imports go here
    pass


This assumes that default configuration values are saved in
``<module>/config/defaults.py``. You can also define configuration values that
depend on other configuration values. In the above script, these are assumed to
be defined in ``<module>/config/static.py``. For example, in the previous example
of temperature prediction, we may want to keep track of the total number of
features being provided to the learning model. ::

    import weather

    # Total number of features
    NUM_FEATURES = (
        int(weather.TODAYS_TEMP_FEATURE) +
        int(weather.AVERAGE_TEMP_FEATURE))


Running tests
=============

::

    pip install pytest
    pytest


Considerations
==============


* ``yapecs`` cannot swap between configuration files, as this would require the
  module to be reloaded. This prevents usage in, e.g., a Jupyter Notebook.


Submodules
==========

.. autosummary::
    :toctree: _autosummary

    core
"""

from .core import *
