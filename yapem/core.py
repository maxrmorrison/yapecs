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

    The configuration values are updated by loading the Python file specified
    by the --config flag. Default configuration values are overwritten by
    values of the same name defined in the configuration file specified by
    --config.

    Args:
        defaults: The submodule containing default configuration values
        config: The Python file containing the updated configuration values
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
