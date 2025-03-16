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

# TODO(AS): Windows test runner in github, fix various OSError: [WinError 1314] A required privilege is not held by the client

import locale
import os
import sys
if sys.platform != "win32":
    import pty
import shutil
from io import StringIO
from pathlib import Path

import pytest

from tests.common import RunContext, build_temp_workspace, temp_workspace
from yamllint import cli, config


# Check system's UTF-8 availability
def utf8_available():
    try:
        locale.setlocale(locale.LC_ALL, 'C.UTF-8')
        locale.setlocale(locale.LC_ALL, (None, None))
    except locale.Error:  # pragma: no cover
        return False
    else:
        return True


@pytest.fixture(autouse=True)
def clean_env():
    """Remove env vars that could interfere with tests."""
    env_vars = (
        'YAMLLINT_CONFIG_FILE',
        'XDG_CONFIG_HOME',
        'HOME',
        'USERPROFILE', 
        'HOMEPATH',
        'HOMEDRIVE'
    )
    for name in env_vars:
        try:
            del os.environ[name]
        except KeyError:
            pass


@pytest.fixture
def workspace(tmp_path):
    """Create test workspace with yaml files."""
    files = {
        'a.yaml': '---\n- 1   \n- 2',
        'warn.yaml': 'key: value\n',
        'empty.yml': '',
        'sub/ok.yaml': '---\nkey: value\n',
        'sub/directory.yaml/not-yaml.txt': '',
        'sub/directory.yaml/empty.yml': '',
        's/s/s/s/s/s/s/s/s/s/s/s/s/s/s/file.yaml': '---\nkey: value\n'
                                                    'key: other value\n',
        'empty-dir': [],
        'symlinks/file-without-yaml-extension': '42\n', 
        'symlinks/link.yaml': 'symlink://file-without-yaml-extension',
        'no-yaml.json': '---\nkey: value\n',
        'non-ascii/éçäγλνπ¥/utf-8': (
            '---\n'
            '- hétérogénéité\n'
            '# 19.99 €\n'
            '- お早う御座います。\n'
            '# الأَبْجَدِيَّة العَرَبِيَّة\n').encode(),
        'dos.yml': '---\r\ndos: true',
        'c.yaml': '---\nA: true\na: true',
        'en.yaml': '---\na: true\nA: true'
    }
    workspace = build_temp_workspace(files)
    workspace_path = Path(workspace)
    yield workspace_path
    shutil.rmtree(workspace)

@pytest.fixture
def run_cli():
    """Fixture to run the CLI with given arguments."""
    def _run_cli(*args):
        with RunContext() as ctx:
            cli.run(args)
        return ctx
    return _run_cli


def test_find_files_recursively(workspace):
    conf = config.YamlLintConfig('extends: default')
    
    result = sorted(cli.find_files_recursively([str(workspace)], conf))
    expected = [
        str(workspace / 'a.yaml'),
        str(workspace / 'c.yaml'),
        str(workspace / 'dos.yml'),
        str(workspace / 'empty.yml'),
        str(workspace / 'en.yaml'),
        str(workspace / 's/s/s/s/s/s/s/s/s/s/s/s/s/s/s/file.yaml'),
        str(workspace / 'sub/directory.yaml/empty.yml'),
        str(workspace / 'sub/ok.yaml'),
        str(workspace / 'symlinks/link.yaml'),
        str(workspace / 'warn.yaml')
    ]
    assert result == expected

    # Test with subset of files
    items = [str(workspace / 'sub/ok.yaml'),
             str(workspace / 'empty-dir')]
    assert sorted(cli.find_files_recursively(items, conf)) == [
        str(workspace / 'sub/ok.yaml')
    ]

    items = [str(workspace / 'empty.yml'),
             str(workspace / 's')]
    assert sorted(cli.find_files_recursively(items, conf)) == [
        str(workspace / 'empty.yml'),
        str(workspace / 's/s/s/s/s/s/s/s/s/s/s/s/s/s/s/file.yaml')
    ]

    items = [str(workspace / 'sub'),
             str(workspace / '/etc/another/file')]
    assert sorted(cli.find_files_recursively(items, conf)) == [
        str(workspace / '/etc/another/file'),
        str(workspace / 'sub/directory.yaml/empty.yml'),
        str(workspace / 'sub/ok.yaml')
    ]

    conf = config.YamlLintConfig('extends: default\n'
                                 'yaml-files:\n'
                                 '  - \'*.yaml\' \n')
    assert sorted(cli.find_files_recursively([str(workspace)], conf)) == [
        str(workspace / 'a.yaml'),
        str(workspace / 'c.yaml'),
        str(workspace / 'en.yaml'),
        str(workspace / 's/s/s/s/s/s/s/s/s/s/s/s/s/s/s/file.yaml'),
        str(workspace / 'sub/ok.yaml'),
        str(workspace / 'symlinks/link.yaml'),
        str(workspace / 'warn.yaml')
    ]

    conf = config.YamlLintConfig('extends: default\n'
                                 'yaml-files:\n'
                                 '  - \'*.yml\'\n')
    assert sorted(cli.find_files_recursively([str(workspace)], conf)) == [
        str(workspace / 'dos.yml'),
        str(workspace / 'empty.yml'),
        str(workspace / 'sub/directory.yaml/empty.yml')
    ]

    conf = config.YamlLintConfig('extends: default\n'
                                 'yaml-files:\n'
                                 '  - \'*.json\'\n')
    assert sorted(cli.find_files_recursively([str(workspace)], conf)) == [
        str(workspace / 'no-yaml.json')
    ]

    conf = config.YamlLintConfig('extends: default\n'
                                 'yaml-files:\n'
                                 '  - \'*\'\n')
    assert sorted(cli.find_files_recursively([str(workspace)], conf)) == [
        str(workspace / 'a.yaml'),
        str(workspace / 'c.yaml'),
        str(workspace / 'dos.yml'),
        str(workspace / 'empty.yml'),
        str(workspace / 'en.yaml'),
        str(workspace / 'no-yaml.json'),
        str(workspace / 'non-ascii/éçäγλνπ¥/utf-8'),
        str(workspace / 's/s/s/s/s/s/s/s/s/s/s/s/s/s/s/file.yaml'),
        str(workspace / 'sub/directory.yaml/empty.yml'),
        str(workspace / 'sub/directory.yaml/not-yaml.txt'),
        str(workspace / 'sub/ok.yaml'),
        str(workspace / 'symlinks/file-without-yaml-extension'),
        str(workspace / 'symlinks/link.yaml'),
        str(workspace / 'warn.yaml')
    ]

    conf = config.YamlLintConfig('extends: default\n'
                                 'yaml-files:\n'
                                 '  - \'*.yaml\'\n'
                                 '  - \'*\'\n'
                                 '  - \'**\'\n')
    assert sorted(cli.find_files_recursively([str(workspace)], conf)) == [
        str(workspace / 'a.yaml'),
        str(workspace / 'c.yaml'),
        str(workspace / 'dos.yml'),
        str(workspace / 'empty.yml'),
        str(workspace / 'en.yaml'),
        str(workspace / 'no-yaml.json'),
        str(workspace / 'non-ascii/éçäγλνπ¥/utf-8'),
        str(workspace / 's/s/s/s/s/s/s/s/s/s/s/s/s/s/s/file.yaml'),
        str(workspace / 'sub/directory.yaml/empty.yml'),
        str(workspace / 'sub/directory.yaml/not-yaml.txt'),
        str(workspace / 'sub/ok.yaml'),
        str(workspace / 'symlinks/file-without-yaml-extension'),
        str(workspace / 'symlinks/link.yaml'),
        str(workspace / 'warn.yaml')
    ]

    conf = config.YamlLintConfig('extends: default\n'
                                 'yaml-files:\n'
                                 '  - \'s/**\'\n'
                                 '  - \'**/utf-8\'\n')
    assert sorted(cli.find_files_recursively([str(workspace)], conf)) == [
        str(workspace / 'non-ascii/éçäγλνπ¥/utf-8')
    ]


def test_run_with_bad_arguments(run_cli):
    """Test yamllint with bad arguments."""
    ctx = run_cli()
    assert ctx.returncode != 0
    assert ctx.stdout == ''
    assert ctx.stderr.startswith('usage')

    ctx = run_cli('--unknown-arg')
    assert ctx.returncode != 0
    assert ctx.stdout == ''
    assert ctx.stderr.startswith('usage')

    ctx = run_cli('-c', './conf.yaml', '-d', 'relaxed', 'file')
    assert ctx.returncode != 0
    assert ctx.stdout == ''
    assert ctx.stderr.splitlines()[-1].startswith(
        'yamllint: error: argument -d/--config-data: '
        'not allowed with argument -c/--config-file'
    )

    # checks if reading from stdin and files are mutually exclusive
    ctx = run_cli('-', 'file')
    assert ctx.returncode != 0
    assert ctx.stdout == ''
    assert ctx.stderr.startswith('usage')


def test_run_with_bad_config(run_cli):
    """Test yamllint with a bad configuration."""
    ctx = run_cli('-d', 'rules: {a: b}', 'file')
    assert ctx.returncode == -1
    assert ctx.stdout == ''
    assert ctx.stderr.startswith('invalid config: no such rule')


def test_run_with_empty_config(run_cli):
    """Test yamllint with an empty configuration."""
    ctx = run_cli('-d', '', 'file')
    assert ctx.returncode == -1
    assert ctx.stdout == ''
    assert ctx.stderr.startswith('invalid config: not a dict')


def test_run_with_implicit_extends_config(workspace, run_cli):
    """Test yamllint with implicit extends configuration."""
    path = workspace / 'warn.yaml'

    ctx = run_cli('-d', 'default', '-f', 'parsable', str(path))
    expected_out = (f'{path}:1:1: [warning] missing document start "---" '
                    f'(document-start)\n')
    assert (ctx.returncode, ctx.stdout, ctx.stderr) == (0, expected_out, '')


def test_run_with_config_file(workspace, run_cli):
    """Test yamllint with a specified config file."""
    config_path = workspace / 'config'
    
    config_path.write_text('rules: {trailing-spaces: disable}')
    ctx = run_cli('-c', str(config_path), str(workspace / 'a.yaml'))
    assert ctx.returncode == 0

    config_path.write_text('rules: {trailing-spaces: enable}') 
    ctx = run_cli('-c', str(config_path), str(workspace / 'a.yaml'))
    assert ctx.returncode == 1


def test_run_with_user_global_config_file(workspace, run_cli):
    """Test yamllint with a global config file."""
    home = workspace / 'fake-home'
    dir = home / '.config' / 'yamllint'
    os.makedirs(dir)
    config = dir / 'config'

    os.environ['HOME'] = str(home)

    config.write_text('rules: {trailing-spaces: disable}')
    ctx = run_cli(str(workspace / 'a.yaml'))
    assert ctx.returncode == 0

    config.write_text('rules: {trailing-spaces: enable}')
    ctx = run_cli(str(workspace / 'a.yaml'))
    assert ctx.returncode == 1


def test_run_with_user_xdg_config_home_in_env(workspace, run_cli, tmp_path):
    """Test yamllint config in XDG_CONFIG_HOME."""
    os.environ['XDG_CONFIG_HOME'] = str(tmp_path)
    yamllint_dir = tmp_path / 'yamllint'
    yamllint_dir.mkdir()
    config_path = yamllint_dir / 'config'
    config_path.write_text('extends: relaxed')

    ctx = run_cli('-f', 'parsable', str(workspace / 'warn.yaml'))
    assert (ctx.returncode, ctx.stdout, ctx.stderr) == (0, '', '')


def test_run_with_user_yamllint_config_file_in_env(workspace, tmp_path, run_cli):
    """Test yamllint config file from env var."""
    config_path = tmp_path / 'config'
    config_path.write_text('rules: {trailing-spaces: disable}')
    os.environ['YAMLLINT_CONFIG_FILE'] = str(config_path)
    
    ctx = run_cli(str(workspace / 'a.yaml'))
    assert ctx.returncode == 0

    config_path.write_text('rules: {trailing-spaces: enable}')
    ctx = run_cli(str(workspace / 'a.yaml'))
    assert ctx.returncode == 1

def test_run_with_locale(workspace, run_cli):
    """Test yamllint with different locales."""
    try:
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    except locale.Error:  # pragma: no cover
        pytest.skip('locale en_US.UTF-8 not available')
    locale.setlocale(locale.LC_ALL, (None, None))

    ctx = run_cli('-d', 'rules: { key-ordering: enable }', str(workspace / 'en.yaml'))
    assert ctx.returncode == 1

    ctx = run_cli('-d', 'rules: { key-ordering: enable }', str(workspace / 'c.yaml'))
    assert ctx.returncode == 0

    locale.setlocale(locale.LC_ALL, (None, None))

    ctx = run_cli('-d', 'locale: en_US.UTF-8\nrules: { key-ordering: enable }', str(workspace / 'en.yaml'))
    assert ctx.returncode == 0

    ctx = run_cli('-d', 'locale: en_US.UTF-8\nrules: { key-ordering: enable }', str(workspace / 'c.yaml'))
    assert ctx.returncode == 1


def test_run_version(run_cli):
    """Test yamllint version output."""
    ctx = run_cli('--version')
    assert ctx.returncode == 0
    assert 'yamllint' in ctx.stdout + ctx.stderr


def test_run_non_existing_file(workspace, run_cli):
    """Test yamllint with a non-existing file."""
    path = workspace / 'i-do-not-exist.yaml'

    ctx = run_cli('-f', 'parsable', str(path))
    assert ctx.returncode == -1
    assert ctx.stdout == ''
    assert 'No such file or directory' in ctx.stderr


def test_run_one_problem_file(workspace, run_cli):
    """Test yamllint with a file that has problems."""
    path = workspace / 'a.yaml'

    ctx = run_cli('-f', 'parsable', str(path))
    assert ctx.returncode == 1
    assert ctx.stdout == (
        f'{path}:2:4: [error] trailing spaces (trailing-spaces)\n'
        f'{path}:3:4: [error] no new line character at the end of file '
        f'(new-line-at-end-of-file)\n')
    assert ctx.stderr == ''


def test_run_one_warning(workspace, run_cli):
    """Test yamllint with a file that has a warning."""
    path = workspace / 'warn.yaml'

    ctx = run_cli('-f', 'parsable', str(path))
    assert ctx.returncode == 0


def test_run_warning_in_strict_mode(workspace, run_cli):
    """Test yamllint with a warning in strict mode."""
    path = workspace / 'warn.yaml'

    ctx = run_cli('-f', 'parsable', '--strict', str(path))
    assert ctx.returncode == 2


def test_run_one_ok_file(workspace, run_cli):
    """Test yamllint with a valid YAML file."""
    path = workspace / 'sub' / 'ok.yaml'

    ctx = run_cli('-f', 'parsable', str(path))
    assert (ctx.returncode, ctx.stdout, ctx.stderr) == (0, '', '')


def test_run_empty_file(workspace, run_cli):
    """Test yamllint with an empty YAML file."""
    path = workspace / 'empty.yml'

    ctx = run_cli('-f', 'parsable', str(path))
    assert (ctx.returncode, ctx.stdout, ctx.stderr) == (0, '', '')


@pytest.mark.skipif(not utf8_available(), reason='C.UTF-8 not available')
def test_run_non_ascii_file(workspace, run_cli):
    """Test yamllint with a non-ASCII file."""
    locale.setlocale(locale.LC_ALL, 'C.UTF-8')
    locale.setlocale(locale.LC_ALL, (None, None))

    path = workspace / 'non-ascii' / 'éçäγλνπ¥' / 'utf-8'
    ctx = run_cli('-f', 'parsable', str(path))
    assert (ctx.returncode, ctx.stdout, ctx.stderr) == (0, '', '')


def test_run_multiple_files(workspace, run_cli):
    """Test yamllint with multiple files."""
    items = [str(workspace / 'empty.yml'),
             str(workspace / 's')]
    path = items[1] + '/s/s/s/s/s/s/s/s/s/s/s/s/s/s/file.yaml'

    ctx = run_cli('-f', 'parsable', *items)
    assert (ctx.returncode, ctx.stderr) == (1, '')
    assert ctx.stdout == (
        f'{path}:3:1: [error] duplication of key "key" in mapping '
        f'(key-duplicates)\n')


def test_run_piped_output_nocolor(workspace, run_cli):
    """Test yamllint piped output without color."""
    path = workspace / 'a.yaml'

    ctx = run_cli(str(path))
    expected_out = (
        f'{path}\n'
        f'  2:4       error    trailing spaces  (trailing-spaces)\n'
        f'  3:4       error    no new line character at the end of file  '
        f'(new-line-at-end-of-file)\n'
        f'\n')
    assert (ctx.returncode, ctx.stdout, ctx.stderr) == (1, expected_out, '')


@pytest.mark.skipif(sys.platform == "win32", reason="requires pty")
def test_run_default_format_output_in_tty(workspace):
    path = workspace / 'a.yaml'

    # Create a pseudo-TTY and redirect stdout to it
    master, slave = pty.openpty()  # type: ignore
    sys.stdout = os.fdopen(slave, 'w')

    with pytest.raises(SystemExit) as ctx:
        cli.run((str(path), ))
    sys.stdout.flush()

    assert ctx.value.code == 1

    # Read output from TTY
    output = os.fdopen(master, 'r')
    os.set_blocking(master, False)

    out = output.read().replace('\r\n', '\n')

    sys.stdout.close()
    output.close()

    assert out == (
        f'\033[4m{path}\033[0m\n'
        f'  \033[2m2:4\033[0m       \033[31merror\033[0m    '
        f'trailing spaces  \033[2m(trailing-spaces)\033[0m\n'
        f'  \033[2m3:4\033[0m       \033[31merror\033[0m    '
        f'no new line character at the end of file  '
        f'\033[2m(new-line-at-end-of-file)\033[0m\n'
        f'\n')


def test_run_default_format_output_without_tty(workspace, run_cli):
    """Test yamllint default format output without TTY."""
    path = workspace / 'a.yaml'

    ctx = run_cli(str(path))
    expected_out = (
        f'{path}\n'
        f'  2:4       error    trailing spaces  (trailing-spaces)\n'
        f'  3:4       error    no new line character at the end of file  '
        f'(new-line-at-end-of-file)\n'
        f'\n')
    assert (ctx.returncode, ctx.stdout, ctx.stderr) == (1, expected_out, '')


def test_run_auto_output_without_tty_output(workspace, run_cli):
    """Test yamllint auto format output without TTY."""
    path = workspace / 'a.yaml'

    ctx = run_cli(str(path), '--format', 'auto')
    expected_out = (
        f'{path}\n'
        f'  2:4       error    trailing spaces  (trailing-spaces)\n'
        f'  3:4       error    no new line character at the end of file  '
        f'(new-line-at-end-of-file)\n'
        f'\n')
    assert (ctx.returncode, ctx.stdout, ctx.stderr) == (1, expected_out, '')


def test_run_format_colored(workspace, run_cli):
    """Test yamllint colored format output."""
    path = workspace / 'a.yaml'

    ctx = run_cli(str(path), '--format', 'colored')
    expected_out = (
        f'\033[4m{path}\033[0m\n'
        f'  \033[2m2:4\033[0m       \033[31merror\033[0m    '
        f'trailing spaces  \033[2m(trailing-spaces)\033[0m\n'
        f'  \033[2m3:4\033[0m       \033[31merror\033[0m    '
        f'no new line character at the end of file  '
        f'\033[2m(new-line-at-end-of-file)\033[0m\n'
        f'\n')
    assert (ctx.returncode, ctx.stdout, ctx.stderr) == (1, expected_out, '')


def test_run_format_colored_warning(workspace, run_cli):
    """Test yamllint colored format output with a warning."""
    path = workspace / 'warn.yaml'

    ctx = run_cli(str(path), '--format', 'colored')
    expected_out = (
        f'\033[4m{path}\033[0m\n'
        f'  \033[2m1:1\033[0m       \033[33mwarning\033[0m  '
        f'missing document start "---"  \033[2m(document-start)\033[0m\n'
        f'\n')
    assert (ctx.returncode, ctx.stdout, ctx.stderr) == (0, expected_out, '')


def test_run_format_github(workspace, run_cli):
    """Test yamllint GitHub Actions format output."""
    path = workspace / 'a.yaml'

    ctx = run_cli(str(path), '--format', 'github')
    expected_out = (
        f'::group::{path}\n'
        f'::error file={path},line=2,col=4::2:4 [trailing-spaces] trailing'
        f' spaces\n'
        f'::error file={path},line=3,col=4::3:4 [new-line-at-end-of-file]'
        f' no new line character at the end of file\n'
        f'::endgroup::\n\n')
    assert (ctx.returncode, ctx.stdout, ctx.stderr) == (1, expected_out, '')


def test_github_actions_detection(workspace, run_cli):
    """Test GitHub Actions detection."""
    path = workspace / 'a.yaml'
    os.environ['GITHUB_ACTIONS'] = 'something'
    os.environ['GITHUB_WORKFLOW'] = 'something'

    ctx = run_cli(str(path))
    expected_out = (
        f'::group::{path}\n'
        f'::error file={path},line=2,col=4::2:4 [trailing-spaces] trailing'
        f' spaces\n'
        f'::error file={path},line=3,col=4::3:4 [new-line-at-end-of-file]'
        f' no new line character at the end of file\n'
        f'::endgroup::\n\n')
    assert (ctx.returncode, ctx.stdout, ctx.stderr) == (1, expected_out, '')


def test_run_read_from_stdin(run_cli):
    """Test reading from stdin."""
    sys.stdin = StringIO(
        'I am a string\n'
        'therefore: I am an error\n')

    ctx = run_cli('-', '-f', 'parsable')
    expected_out = (
        'stdin:2:10: [error] syntax error: '
        'mapping values are not allowed here (syntax)\n')
    assert (ctx.returncode, ctx.stdout, ctx.stderr) == (1, expected_out, '')


def test_run_no_warnings(workspace, run_cli):
    """Test yamllint with no warnings."""
    path = workspace / 'a.yaml'

    ctx = run_cli(str(path), '--no-warnings', '-f', 'auto')
    expected_out = (
        f'{path}\n'
        f'  2:4       error    trailing spaces  (trailing-spaces)\n'
        f'  3:4       error    no new line character at the end of file  '
        f'(new-line-at-end-of-file)\n'
        f'\n')
    assert (ctx.returncode, ctx.stdout, ctx.stderr) == (1, expected_out, '')

    path = workspace / 'warn.yaml'

    ctx = run_cli(str(path), '--no-warnings', '-f', 'auto')
    assert ctx.returncode == 0

def test_run_no_warnings_and_strict(workspace, run_cli):
    """Test yamllint with no warnings and strict mode."""
    path = workspace / 'warn.yaml'

    ctx = run_cli(str(path), '--no-warnings', '-s')
    assert ctx.returncode == 2


def test_run_non_universal_newline(workspace, run_cli):
    """Test yamllint with non-universal newline."""
    path = workspace / 'dos.yml'

    ctx = run_cli('-d', 'rules:\n  new-lines:\n    type: dos', str(path))
    assert (ctx.returncode, ctx.stdout, ctx.stderr) == (0, '', '')

    ctx = run_cli('-d', 'rules:\n  new-lines:\n    type: unix', str(path))
    expected_out = (
        f'{path}\n'
        f'  1:4       error    wrong new line character: expected \\n'
        f'  (new-lines)\n'
        f'\n')
    assert (ctx.returncode, ctx.stdout, ctx.stderr) == (1, expected_out, '')


def test_run_list_files(workspace, run_cli):
    """Test yamllint --list-files option."""
    ctx = run_cli('--list-files', str(workspace))
    assert ctx.returncode == 0
    assert sorted(ctx.stdout.splitlines()) == [
        str(workspace / 'a.yaml'),
        str(workspace / 'c.yaml'),
        str(workspace / 'dos.yml'),
        str(workspace / 'empty.yml'),
        str(workspace / 'en.yaml'),
        str(workspace / 's/s/s/s/s/s/s/s/s/s/s/s/s/s/s/file.yaml'),
        str(workspace / 'sub/directory.yaml/empty.yml'),
        str(workspace / 'sub/ok.yaml'),
        str(workspace / 'symlinks/link.yaml'),
        str(workspace / 'warn.yaml')
    ]

    config = '{ignore: "*.yml", yaml-files: ["*.*"]}'
    ctx = run_cli('--list-files', '-d', config, str(workspace))
    assert ctx.returncode == 0
    assert sorted(ctx.stdout.splitlines()) == [
        str(workspace / 'a.yaml'),
        str(workspace / 'c.yaml'),
        str(workspace / 'en.yaml'),
        str(workspace / 'no-yaml.json'),
        str(workspace / 's/s/s/s/s/s/s/s/s/s/s/s/s/s/s/file.yaml'),
        str(workspace / 'sub/directory.yaml/not-yaml.txt'),
        str(workspace / 'sub/ok.yaml'),
        str(workspace / 'symlinks/link.yaml'),
        str(workspace / 'warn.yaml')
    ]

    config = 'ignore: ["*.yaml", "*.yml", "!a.yaml"]'
    ctx = run_cli('--list-files', '-d', config, str(workspace))
    assert ctx.returncode == 0
    assert sorted(ctx.stdout.splitlines()) == [
        str(workspace / 'a.yaml')
    ]
    ctx = run_cli('--list-files', '-d', config,
                  str(workspace / 'a.yaml'),
                  str(workspace / 'en.yaml'),
                  str(workspace / 'c.yaml'))
    assert ctx.returncode == 0
    assert sorted(ctx.stdout.splitlines()) == [
        str(workspace / 'a.yaml')
    ]


def test_config_file(run_cli):
    """Test yamllint with a specified config file."""
    conf = ('---\n'
            'extends: relaxed\n')

    for conf_file in ('.yamllint', '.yamllint.yml', '.yamllint.yaml'):
        with temp_workspace({'a.yml': 'hello: world\n'}):
            ctx = run_cli('-f', 'parsable', '.')
            assert (ctx.returncode, ctx.stdout, ctx.stderr) == (
                0, './a.yml:1:1: [warning] missing document '
                'start "---" (document-start)\n', '')

            with temp_workspace({'a.yml': 'hello: world\n', conf_file: conf}):
                ctx = run_cli('-f', 'parsable', '.')
                assert (ctx.returncode, ctx.stdout, ctx.stderr) == (0, '', '')


def test_parent_config_file(workspace, run_cli):
    """Test yamllint with a parent config file."""
    workspace = {'a/b/c/d/e/f/g/a.yml': 'hello: world\n'}
    conf = ('---\n'
            'extends: relaxed\n')

    for conf_file in ('.yamllint', '.yamllint.yml', '.yamllint.yaml'):
        with temp_workspace(workspace):
            os.chdir('a/b/c/d/e/f')
            ctx = run_cli('-f', 'parsable', '.')

            assert (ctx.returncode, ctx.stdout, ctx.stderr) == (
                0, './g/a.yml:1:1: [warning] missing '
                'document start "---" (document-start)\n', '')

            with temp_workspace({**workspace, conf_file: conf}):
                os.chdir('a/b/c/d/e/f')
                ctx = run_cli('-f', 'parsable', '.')

            assert (ctx.returncode, ctx.stdout, ctx.stderr) == (0, '', '')


def test_multiple_parent_config_file(workspace, run_cli):
    """Test yamllint with multiple parent config files."""
    workspace = {
        'a/b/c/3spaces.yml': 'array:\n   - item\n',
        'a/b/c/4spaces.yml': 'array:\n    - item\n',
        'a/.yamllint': '---\nextends: relaxed\nrules:\n  indentation:\n    spaces: 4\n',
    }

    conf3 = ('---\nextends: relaxed\nrules:\n  indentation:\n    spaces: 3\n')

    with temp_workspace(workspace):
        os.chdir('a/b/c')
        ctx = run_cli('-f', 'parsable', '.')
        assert (ctx.returncode, ctx.stdout, ctx.stderr) == (
            0, './3spaces.yml:2:4: [warning] wrong indentation: '
            'expected 4 but found 3 (indentation)\n', '')

    with temp_workspace({**workspace, 'a/b/.yamllint.yml': conf3}):
        os.chdir('a/b/c')
        ctx = run_cli('-f', 'parsable', '.')
        assert (ctx.returncode, ctx.stdout, ctx.stderr) == (
            0, './4spaces.yml:2:5: [warning] wrong indentation: '
            'expected 3 but found 4 (indentation)\n', '')
