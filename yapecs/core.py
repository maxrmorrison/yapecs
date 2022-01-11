import contextlib
import copy
import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from typing import Optional


###############################################################################
# Configuration
###############################################################################


def configure(defaults: ModuleType, config: Optional[Path] = None):
    """Update the default configuration values

    Args:
        defaults: The submodule containing default configuration values
        config: The Python file containing the updated configuration values.
            If not provided and the ``--config`` parameter is a command-line
            argument, the corresponding argument is used as the configuration
            file.
    """
    # Get config file
    if config is None:

        try:
            index = sys.argv.index('--config')
        except:
            return
        if index == -1 or index + 1 == len(sys.argv):
            return
        config = Path(sys.argv[index + 1])

    # Load config file as a module
    config_spec = importlib.util.spec_from_file_location('config', config)
    config_module = importlib.util.module_from_spec(config_spec)
    config_spec.loader.exec_module(config_module)

    # Merge config module and default config module
    for parameter in dir(config_module):
        if hasattr(defaults, parameter):
            setattr(defaults, parameter, getattr(config_module, parameter))


@contextlib.contextmanager
def context(
    module: ModuleType,
    config_module: ModuleType,
    current: Path,
    updated: Path):
    """Temporarily update configuration values

    Args:
        module: The module that we are configuring
        config_module: The submodule containing configuration values
        current: The Python file containing the current configuration values
        updated: The Python file containing the updated configuration values
    """
    try:

        # Modify configuration
        configure(config_module, updated)

        # Reload
        importlib.reload(module)

        yield

    finally:

        # Restore configuration
        configure(config_module, current)

        # Reload
        importlib.reload(module)
