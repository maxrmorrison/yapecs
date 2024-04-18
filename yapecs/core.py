import argparse
import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from typing import Optional
from copy import copy


###############################################################################
# Configuration
###############################################################################

def import_from_path(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def configure(
    module_name: str,
    config_module: ModuleType,
    config: Optional[Path] = None
):
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
        updated_module = import_from_path('config', config)

        # Only update when the module name matches
        if updated_module.MODULE != module_name:
            continue

        # Merge config module and default config module
        for parameter in dir(updated_module):
            if hasattr(config_module, parameter):
                setattr(config_module, parameter, getattr(updated_module, parameter))


def import_with_configs(module, config_paths):
    #TODO create a lock to prevent potential issues when using multithreading issues

    # handle sys.argv changes
    original_argv = copy(sys.argv)
    if '--config' in sys.argv:
        raise ValueError('cannot replace --config, --config must not be set in sys.argv')
    sys.argv.append('--config')
    assert len(config_paths) >= 1
    for config_path in config_paths:
        sys.argv.append(config_path)

    # temporarily clear sys.modules to ensure that other modules are configured properly
    original_modules = copy(sys.modules)
    config_module_names = [] # names of corresponding modules for all config files
    for config_path in config_paths:
        config_module = import_from_path('config', config_path)
        config_module_names.append(config_module.MODULE)
    to_delete = []
    for module_name in sys.modules.keys():
        if module_name.split('.')[0] in config_module_names:
            to_delete.append(module_name)
    for module_name in to_delete:
        del sys.modules[module_name]

    # import the module
    name = module.__name__
    path = module.__path__
    if isinstance(path, list):
        path = path[0] #TODO investigate remifications
    if not path.endswith('.py'):
        path = path + '/__init__.py' #TODO make better
    module = import_from_path(name, path)

    # revert sys.modules
    sys.modules = original_modules

    # revert sys.argv
    sys.argv = original_argv

    return module

class ArgumentParser(argparse.ArgumentParser):

    def parse_args(self, args=None, namespace=None):
        """Parse arguments while allowing unregistered config argument"""
        # Parse
        args, argv = self.parse_known_args(args, namespace)

        # Get unregistered arguments
        unknown = [arg for arg in argv if arg.startswith('--')]

        # Allow unregistered config argument
        if len(unknown) == 1 and unknown[0] == '--config':
            return args

        # Disallow other unregistered arguments
        if len(unknown) > 0:
            unknown = [arg for arg in unknown if arg != '--config']
            self.error(f'Unrecognized arguments: {unknown}')

        return args
