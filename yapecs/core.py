import argparse
import importlib.util
import itertools
import os
import sys
from pathlib import Path
from types import ModuleType
from typing import Optional, Tuple, Union


###############################################################################
# Configuration
###############################################################################


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
                setattr(
                    config_module,
                    parameter,
                    getattr(updated_module, parameter))


###############################################################################
# Argument parsing
###############################################################################


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


###############################################################################
# Hyperparameter search
###############################################################################


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
    # Get current progress
    progress_file = Path(progress_file)
    if not progress_file.exists():
        progress = 0
    else:
        with open(progress_file) as f:
            progress = int(f.read())

    # Raise if finished
    combinations = list(itertools.product(*args))
    if progress >= len(combinations):
        raise IndexError('Finished grid search')

    # Write updated progress
    with open(progress_file, 'w+') as file:
        file.write(str(progress + 1))

    # Get corresponding argument combination
    return combinations[progress]
