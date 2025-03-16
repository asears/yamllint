"""
Module to load yamllint configuration from pyproject.toml.

Provides functionality to extract the [tool.yamllint] section as a configuration.
References:
    - TOML format: https://toml.io/en/
    - PEP 518: https://www.python.org/dev/peps/pep-0518/
    - PEP 621: https://www.python.org/dev/peps/pep-0621/
"""

import sys

try:
    import tomllib
except ImportError:
    try:
        import tomli
    except ImportError:
        sys.exit('Either tomllib or tomli must be installed')

from pathlib import Path

import yaml


def load_pyproject_config(pyproject_path='pyproject.toml'):
    """
    Load yamllint configuration from the specified pyproject.toml file.

    :param pyproject_path: Path to the pyproject.toml file.
    :type pyproject_path: str
    :return: YAML configuration string derived from the [tool.yamllint] section.
    :rtype: str
    :raises FileNotFoundError: if pyproject.toml file does not exist.
    :raises KeyError: if [tool.yamllint] section is missing.
    """
    pyproject_config_path = Path(pyproject_path)
    if not pyproject_config_path.is_file():
        raise FileNotFoundError(f'{pyproject_path} not found')

    with pyproject_config_path.open('rb') as f:
        if 'tomllib' in sys.modules:
            config_dict = tomllib.load(f)
        else:
            config_dict = tomli.load(f)
    try:
        tool_config = config_dict['tool']['yamllint']
    except KeyError:
        raise KeyError('Missing [tool.yamllint] section in pyproject.toml')

    return yaml.dump(tool_config)


class TomlConfigLoader:
    @staticmethod
    def load(file):
        if not str(file).endswith('pyproject.toml'):
            raise ValueError('File is not a pyproject.toml')

        config_dict = (
            tomllib.load(file) if 'tomllib' in sys.modules else tomli.load(file)
        )
        try:
            tool_config = config_dict['tool']['yamllint']
        except KeyError:
            raise ValueError('pyproject.toml missing [tool.yamllint] section')

        return yaml.dump(tool_config)
