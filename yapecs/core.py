import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from typing import Optional
import argparse


###############################################################################
# Configuration
###############################################################################


def configure(
    module_name: str,
    config_module: ModuleType,
    config: Optional[Path] = None):
    """Update the configuration values

    Args:
        module_name: The name of the module to configure
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

        configs = []
        i = index + 1
        while i < len(sys.argv) and not sys.argv[i].startswith('--'):
            path = Path(sys.argv[i])

            # Raise if config file doesn't exist
            if not path.is_file():
                raise FileNotFoundError(
                    f'Configuration file {path} does not exist')

            configs.append(path)
            i += 1

    else:

        configs  = [config]

    # Find the configuration with the matching module name
    for config in configs:

        # Load config file as a module
        config_spec = importlib.util.spec_from_file_location('config', config)
        updated_module = importlib.util.module_from_spec(config_spec)
        config_spec.loader.exec_module(updated_module)

        # Only update when the module name matches
        if updated_module.MODULE != module_name:
            continue

        # Merge config module and default config module
        for parameter in dir(updated_module):
            if hasattr(config_module, parameter):
                setattr(config_module, parameter, getattr(updated_module, parameter))

class ArgumentParser(argparse.ArgumentParser):
    
    def parse_args(self, args=None, namespace=None):
        args, argv = self.parse_known_args(args, namespace)
        if len(argv) == 2 and argv[0] == '--config':
            return args
        if argv:
            msg = 'unrecognized arguments: %s'
            self.error(msg % ' '.join(argv))
        return args