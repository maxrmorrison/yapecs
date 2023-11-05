from collections.abc import Sequence
import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from typing import Any, Optional
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

    def __init__(
        self,
        prog = None,
        usage = None,
        description = None,
        epilog = None,
        # parents: Sequence[ArgumentParser] = ...,
        # formatter_class = ...,
        prefix_chars: str = "-",
        fromfile_prefix_chars = None,
        argument_default: Any = None,
        conflict_handler: str = "error",
        add_help: bool = True,
        allow_abbrev: bool = True) -> None:

        super().__init__(
            prog=prog,
            usage=usage,
            description=description,
            epilog=epilog,
            # parents=parents,
            # formatter_class=formatter_class,
            prefix_chars=prefix_chars,
            fromfile_prefix_chars=fromfile_prefix_chars,
            argument_default=argument_default,
            conflict_handler=conflict_handler,
            add_help=add_help,
            allow_abbrev=allow_abbrev)


        self.add_argument(
            '--config',
            help='config files to use with yapecs. This argument was added automatically by yapecs.ArgumentParser',
            nargs='*',
            required=False
        )

    def parse_args(self, args=None, namespace=None):

        arguments = super().parse_args(args, namespace)

        if 'config' in arguments:
            del arguments.__dict__['config']

        return arguments