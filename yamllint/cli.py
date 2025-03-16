# Copyright (C) 2016 Adrien Vergé
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""A linter for YAML files."""
import argparse
import locale
import os
import platform
import sys
from pathlib import Path
from typing import Any

from yamllint import APP_DESCRIPTION, APP_NAME, APP_VERSION, linter
from yamllint.config import YamlLintConfig, YamlLintConfigError
from yamllint.linter import PROBLEM_LEVELS


def find_files_recursively(items: list, conf: Any) -> Any:
    """Find files recursively in the given items.
    
    :param items: The items to search for files
    :type items: list
    :param conf: The YamlLint configuration
    :type conf: YamlLintConfig
    
    :return: The found files
    :rtype: str
    """
    for item in items:
        item_path = Path(item)
        if item_path.is_dir():
            for filepath in item_path.rglob('*'):
                if (
                    filepath.is_file()
                    and conf.is_yaml_file(filepath)
                    and not conf.is_file_ignored(filepath)
                ):
                    yield str(filepath)
        else:
            yield str(item_path)


def supports_color():
    supported_platform = not (
        platform.system() == 'Windows'
        and not (
            'ANSICON' in os.environ
            or ('TERM' in os.environ and os.environ['TERM'] == 'ANSI')
        )
    )
    return supported_platform and hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()


class Format:
    """
    Provides various static methods to generate formatted strings for linter problems.

    These methods support different formats including parsable, standard, colored, and GitHub Actions annotations.

    Methods
    -------
    parsable(problem: linter.Problem, filename: str) -> str
        Generates a parsable formatted string for a given linter problem.
    standard(problem: linter.Problem) -> str
        Generates a standard formatted string for a given linter problem.
    standard_color(problem: linter.Problem) -> str
        Generates a colored formatted string for a given linter problem.
    github(problem: linter.Problem, filename: str) -> str
        Generates a GitHub Actions formatted annotation string for a given linter problem.
    """
    @staticmethod
    def parsable(problem: Any, filename: str) -> str:
        """
        Generates a parsable formatted string for a given linter problem.

        :param linter.Problem problem: The linter problem instance containing details about the issue.
        :param str filename: The name of the file where the problem was found.
        :return: A formatted string representing the problem in a parsable format.
        :rtype: str
        """
        return (
            f'{filename}:{problem.line}:{problem.column}: '
            f'[{problem.level}] {problem.message}'
        )

    @staticmethod
    def standard(problem: Any) -> str:
        """
        Generates a standard formatted string for a given linter problem.

        :param problem: The linter problem instance containing details about the issue.
        :type problem: linter.Problem
        :return: A formatted string representing the problem.
        :rtype: str
        """
        line = f'  {problem.line}:{problem.column}'
        line += max(12 - len(line), 0) * ' '
        line += problem.level
        line += max(21 - len(line), 0) * ' '
        line += problem.desc
        if problem.rule:
            line += f'  ({problem.rule})'
        return line

    @staticmethod
    def standard_color(problem: Any) -> str:
        """
        Generates a colored formatted string for a given linter problem.

        :param problem: The linter problem instance containing details about the issue.
        :type problem: linter.Problem
        :return: A colored formatted string representing the problem.
        :rtype: str
        """
        line = f'  \033[2m{problem.line}:{problem.column}\033[0m'
        line += max(20 - len(line), 0) * ' '
        if problem.level == 'warning':
            line += f'\033[33m{problem.level}\033[0m'
        else:
            line += f'\033[31m{problem.level}\033[0m'
        line += max(38 - len(line), 0) * ' '
        line += problem.desc
        if problem.rule:
            line += f'  \033[2m({problem.rule})\033[0m'
        return line
    @staticmethod
    def github(problem: Any, filename: str) -> str:
        """
        Generates a GitHub Actions formatted annotation string for a given linter problem.

        :param problem: The linter problem instance containing details about the issue.
        :type problem: linter.Problem
        :param filename: The name of the file where the problem was found.
        :type filename: str
        :return: A formatted string suitable for GitHub Actions annotations.
        :rtype: str
        """
        line = (
            f'::{problem.level} file={filename},'
            f'line={problem.line},col={problem.column}'
            f'::{problem.line}:{problem.column} '
        )
        if problem.rule:
            line += f'[{problem.rule}] '
        line += problem.desc
        return line


def show_problems(
    problems: list,
    file: str,
    args_format: str,
    no_warn: bool
) -> int:
    """Show linting problems in the specified format.

    :param problems: List of linting problems
    :type problems: list
    :param file: The file being linted
    :type file: str
    :param args_format: The format to display the problems
    :type args_format: str
    :param no_warn: Whether to suppress warnings
    :type no_warn: bool

    :return: The highest level of problems found
    :rtype: int
    """
    max_level = 0
    first = True

    if args_format == 'auto':
        if 'GITHUB_ACTIONS' in os.environ and 'GITHUB_WORKFLOW' in os.environ:
            args_format = 'github'
        elif supports_color():
            args_format = 'colored'

    for problem in problems:
        max_level = max(max_level, PROBLEM_LEVELS[problem.level])
        if no_warn and (problem.level != 'error'):
            continue
        if args_format == 'parsable':
            print(Format.parsable(problem, file))
        elif args_format == 'github':
            if first:
                print(f'::group::{file}')
                first = False
            print(Format.github(problem, file))
        elif args_format == 'colored':
            if first:
                print(f'\033[4m{file}\033[0m')
                first = False
            print(Format.standard_color(problem))
        else:
            if first:
                print(file)
                first = False
            print(Format.standard(problem))

    if not first and args_format == 'github':
        print('::endgroup::')

    if not first and args_format != 'parsable':
        print('')

    return max_level


def find_project_config_filepath(path: Path = Path()) -> str:
    """Find the project configuration file path.

    :param path: The starting path to search for the configuration file, defaults to Path()
    :type path: Path, optional

    :return: The path to the project configuration file if found, otherwise None
    :rtype: str
    """
    for filename in ('.yamllint', '.yamllint.yaml', '.yamllint.yml'):
        filepath = path / filename
        if filepath.is_file():
            return str(filepath)
    try:
        if path.resolve() == Path.home().resolve():
            return None
    except RuntimeError:
        # In case of a RuntimeError, the user is likely running in a restricted environment
        pass
    if path.resolve() == path.parent.resolve():
        return None
    return find_project_config_filepath(path=path.parent)

def get_user_global_config() -> Path:
    """Get the path to the user global configuration file.

    :return: Path to the user global configuration file
    :rtype: Path
    """
    if 'YAMLLINT_CONFIG_FILE' in os.environ:
        user_global_config = Path(os.environ['YAMLLINT_CONFIG_FILE']).expanduser()
    # User-global config is supposed to be in ~/.config/yamllint/config
    elif 'XDG_CONFIG_HOME' in os.environ:
        user_global_config = Path(os.environ['XDG_CONFIG_HOME']) / 'yamllint' / 'config'
    else:
        try:
            user_global_config = Path(os.path.expanduser('~/.config/yamllint/config'))
        except RuntimeError:
            # In case of a RuntimeError, the user is likely running in a restricted environment
            user_global_config = None
    return user_global_config

def load_yaml_config(
    args: Any,
    user_global_config: Path,
    project_config_filepath: str,
) -> YamlLintConfig:
    """Load the YAML configuration for yamllint.

    :param args: Parsed command line arguments
    :type args: argparse.Namespace
    :param user_global_config: Path to the user global configuration file
    :type user_global_config: Path
    :param project_config_filepath: Path to the project configuration file
    :type project_config_filepath: str

    :return: The loaded YAML configuration
    :rtype: YamlLintConfig
    """
    try:
        if args.config_data is not None:
            if args.config_data and ':' not in args.config_data:
                args.config_data = f'extends: {args.config_data}'
            conf = YamlLintConfig(content=args.config_data)
        elif args.config_file is not None:
            conf = YamlLintConfig(file=args.config_file)
        elif project_config_filepath:
            conf = YamlLintConfig(file=project_config_filepath)
        elif user_global_config.is_file():
            conf = YamlLintConfig(file=user_global_config)
        else:
            conf = YamlLintConfig('extends: default')
    except YamlLintConfigError as e:
        print(e, file=sys.stderr)
        sys.exit(-1)
    return conf

def lint_stdin(conf: YamlLintConfig) -> list:
    """Lint YAML content from standard input.

    :param conf: YamlLint configuration
    :type conf: YamlLintConfig

    :return: List of linting problems
    :rtype: list
    """
    try:
        problems = linter.run(sys.stdin, conf, '')
    except OSError as e:
        print(e, file=sys.stderr)
        sys.exit(-1)
    return problems


def get_linter_exit_status(args: Any, max_level: int) -> int:
    """Determine the exit status for the linter based on the highest problem level.

    :param args: Parsed command line arguments
    :type args: argparse.Namespace
    :param max_level: The highest level of problems found
    :type max_level: int

    :return: The exit status code
    :rtype: int
    """
    if max_level == PROBLEM_LEVELS['error']:
        return_code = 1
    elif max_level == PROBLEM_LEVELS['warning']:
        return_code = 2 if args.strict else 0
    else:
        return_code = 0
    return return_code

def list_files_only(args: Any, conf: YamlLintConfig) -> None:
    """List files to lint and exit.

    :param args: Parsed command line arguments
    :type args: argparse.Namespace
    :param conf: YamlLint configuration
    :type conf: YamlLintConfig

    :return: None
    """
    for file in find_files_recursively(args.files, conf):
        if not conf.is_file_ignored(file):
            print(file)
    sys.exit(0)

def run(argv: list[str] | None = None) -> None:
    """Run the linter with the given arguments.

    :param argv: Arguments to parse, defaults to None
    :type argv: List[str], optional

    :return: None
    """
    parser = argparse.ArgumentParser(prog=APP_NAME, description=APP_DESCRIPTION)
    files_group = parser.add_mutually_exclusive_group(required=True)
    # fmt: off
    files_group.add_argument(
        'files',
        metavar='FILE_OR_DIR',
        nargs='*',
        default=(),
        help='files to check',
    )
    files_group.add_argument(
        '-',
        action='store_true',
        dest='stdin',
        help='read from standard input',
    )
    config_group = parser.add_mutually_exclusive_group()
    config_group.add_argument(
        '-c',
        '--config-file',
        dest='config_file',
        action='store',
        help='path to a custom configuration',
    )
    config_group.add_argument(
        '-d',
        '--config-data',
        dest='config_data',
        action='store',
        help='custom configuration (as YAML source)',
    )
    parser.add_argument(
        '--list-files',
        action='store_true',
        dest='list_files',
        help='list files to lint and exit',
    )
    parser.add_argument(
        '-f',
        '--format',
        choices=('parsable', 'standard', 'colored', 'github', 'auto'),
        default='auto',
        help='format for parsing output',
    )
    parser.add_argument(
        '-s',
        '--strict',
        action='store_true',
        help='return non-zero exit code on warnings as well as errors',
    )
    parser.add_argument(
        '--no-warnings',
        action='store_true',
        help='output only error level problems',
    )
    parser.add_argument(
        '-v',
        '--version',
        action='version',
        version=f'{APP_NAME} {APP_VERSION}',
    )
    # fmt: on

    args = parser.parse_args(argv)

    user_global_config = get_user_global_config()

    project_config_filepath = find_project_config_filepath()
    conf = load_yaml_config(args, user_global_config, project_config_filepath)

    if conf.locale is not None:
        locale.setlocale(locale.LC_ALL, conf.locale)

    if args.list_files:
        list_files_only(args, conf)

    max_level = 0

    for file in find_files_recursively(args.files, conf):
        filepath = Path(file).relative_to(Path.cwd())
        # fmt: off
        try:
            with filepath.open(newline='') as f:
                problems = linter.run(f, conf, str(filepath))
        except OSError as e:
            print(e, file=sys.stderr)
            sys.exit(-1)
        prob_level = show_problems(
            problems,
            str(filepath),
            args_format=args.format,
            no_warn=args.no_warnings,
        )
        max_level = max(max_level, prob_level)
        # fmt: on

    # read yaml from stdin
    if args.stdin:
        problems = lint_stdin(conf)
        # fmt: off
        prob_level = show_problems(
            problems,
            'stdin',
            args_format=args.format,
            no_warn=args.no_warnings,
        )
        # fmt: on
        max_level = max(max_level, prob_level)

    return_code = get_linter_exit_status(args, max_level)

    sys.exit(return_code)
