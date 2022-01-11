"""Yet Another Python Experiment Configuration System (YAPECS)

``yapecs`` is a Python library for experiment configuration. It is an
alternative to performing experiment configuration using JSON, YAML, or more
specialized solutions such as hydra. Relative to other configuration systems,
I prefer ``yapecs`` for the following reasons:

* Configuration files are written in Python. You do not need to learn new
  syntax, and your configurations can be as expressive as desired. Unlike JSON,
  comments are supported within configuration files.

* Integration is simple, requiring only four or five lines of code (including
  imports).

* The entire yapecs library is only one function and 25 lines (excluding
  comments).


Installation
============

::

    pip install yapecs


Configuration files
===================


Say we are creating a system that predicts tomorrow's temperature given two features

1. Today's temperature

2. The average temperature of previous years

Our default configuration file (e.g., ``defaults.py``) might look like the
following ::

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

Using ``yapecs``, we pass our new file using the ``--config`` parameter ::

    python -m <module>.<entrypoint> <args> --config config.py


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

    import <module>

    # Total number of features
    NUM_FEATURES = (
        int(<module>.TODAYS_TEMP_FEATURE) +
        int(<module>.AVERAGE_TEMP_FEATURE))


You can also use ``yapecs`` within a Jupyter Notebook by passing the
configuration file as a second argument. ::

    # Default configuration parameters to be modified
    import <module>.config.defaults

    # Modify configuration
    import yapecs
    yapecs.configure(<module>.config.defaults, 'config.py')

    # Import configuration parameters
    import <module>


Running tests
=====

::

    pip install pytest
    pytest


Considerations
==============


``yapecs`` imports the configuration file. This means the contents of the
configuration file are executed. Only use configuration files you trust.


Submodules
==========

.. autosummary::
    :toctree: _autosummary

    core
"""

from .core import *
