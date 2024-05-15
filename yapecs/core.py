import argparse
import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from typing import Optional, Union, List
from copy import copy


###############################################################################
# Configuration
###############################################################################

def import_from_path(
    name: str, 
    path: Union[Path, str]):
    """Import module from a filesystem path

    Args:
        name: the name of the module
        path: the path to import from
    """
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


def import_with_configs(
        module: ModuleType,
        config_paths: List[str]):
    """Import an instance of a module with a list of configs applied

    Args:
        module: the module to re-import with configs applied
        config_paths: a list of strings containing paths to yapecs config files
    """
    #TODO create a lock to prevent potential issues when using multithreading issues

    # handle sys.argv changes
    #  simulates adding `--config config_paths[0] config_paths[1]...` to sys.argv
    original_argv = copy(sys.argv)
    if '--config' in sys.argv:
        raise ValueError('cannot replace --config, --config must not be set in sys.argv')
    sys.argv.append('--config')
    assert len(config_paths) >= 1
    for config_path in config_paths:
        sys.argv.append(config_path)

    # temporarily remove modules for which configs are present
    #  from sys.modules to ensure that other modules are configured properly
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

    def __init__(
        self,
        prog=None,
        usage=None,
        description=None,
        epilog=None,
        parents=[],
        formatter_class=argparse.HelpFormatter,
        prefix_chars='-',
        fromfile_prefix_chars=None,
        argument_default=None,
        conflict_handler='error',
        add_help=True,
        allow_abbrev=True,
        exit_on_error=True
    ):
        """Object for parsing command-line arguments which include a yapecs '--config' option.
        If you manually define a '--config' option for use elsewhere, use argparse.ArgumentParser instead.

        Keyword Arguments:
            - prog -- The name of the program (default:
                ``os.path.basename(sys.argv[0])``)
            - usage -- A usage message (default: auto-generated from arguments)
            - description -- A description of what the program does
            - epilog -- Text following the argument descriptions
            - parents -- Parsers whose arguments should be copied into this one
            - formatter_class -- HelpFormatter class for printing help messages
            - prefix_chars -- Characters that prefix optional arguments
            - fromfile_prefix_chars -- Characters that prefix files containing
                additional arguments
            - argument_default -- The default value for all arguments
            - conflict_handler -- String indicating how to handle conflicts
            - add_help -- Add a -h/-help option
            - allow_abbrev -- Allow long options to be abbreviated unambiguously
            - exit_on_error -- Determines whether or not ArgumentParser exits with
                error info when an error occurs
        """
        result = super().__init__(
                 prog=prog,
                 usage=usage,
                 description=description,
                 epilog=epilog,
                 parents=parents,
                 formatter_class=formatter_class,
                 prefix_chars=prefix_chars,
                 fromfile_prefix_chars=fromfile_prefix_chars,
                 argument_default=argument_default,
                 conflict_handler=conflict_handler,
                 add_help=add_help,
                 allow_abbrev=allow_abbrev,
                 exit_on_error=exit_on_error
        )
        self.add_argument(
            '--config',
            help='config files to use with yapecs. This argument was added automatically by yapecs.ArgumentParser',
            nargs='*',
            required=False
        )
        return result

    def parse_args(self, args=None, namespace=None):

        arguments = super().parse_args(args, namespace)

        if 'config' in arguments:
            del arguments.__dict__['config']

        return arguments