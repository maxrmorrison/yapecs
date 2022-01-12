import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from typing import Optional


###############################################################################
# Configuration
###############################################################################


def configure(config_module: ModuleType, config: Optional[Path] = None):
    """Update the configuration values

    Args:
        config_module: The submodule containing configuration values
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
    updated_module = importlib.util.module_from_spec(config_spec)
    config_spec.loader.exec_module(updated_module)

    # Merge config module and default config module
    for parameter in dir(updated_module):
        if hasattr(config_module, parameter):
            setattr(config_module, parameter, getattr(updated_module, parameter))
