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

import sys
from io import StringIO
from pathlib import Path

import pytest
import yaml

from yamllint import linter
from yamllint.config import YamlLintConfig


class RuleTestCase:
    def build_fake_config(self, conf):
        """
        Build a fake configuration.

        :param conf: YAML configuration string or None.
        :returns: A YamlLintConfig instance.
        """
        if conf is None:
            conf = {}
        else:
            conf = yaml.safe_load(conf)
        conf = {'extends': 'default',
                'rules': conf}
        return YamlLintConfig(yaml.safe_dump(conf))

    def check(self, source, conf, **kwargs):
        """
        Check YAML lint results against expected problems.

        :param source: YAML content to lint.
        :param conf: Configuration string.
        :param kwargs: Expected problem details.
        """
        expected_problems = []
        for key in kwargs:
            assert key.startswith('problem')
            if len(kwargs[key]) > 2:
                if kwargs[key][2] == 'syntax':
                    rule_id = None
                else:
                    rule_id = kwargs[key][2]
            else:
                rule_id = self.rule_id
            expected_problems.append(linter.LintProblem(
                kwargs[key][0], kwargs[key][1], rule=rule_id))
        expected_problems.sort()

        real_problems = list(linter.run(source, self.build_fake_config(conf)))
        assert real_problems == expected_problems


class RunContext:
    """
    Context manager for cli.run() to capture exit code and streams using pytest.
    """
    def __init__(self):
        self.stdout = self.stderr = None

    def __enter__(self):
        self.old_sys_stdout = sys.stdout
        self.old_sys_stderr = sys.stderr
        sys.stdout = self.outstream = StringIO()
        sys.stderr = self.errstream = StringIO()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stdout = self.outstream.getvalue()
        self.stderr = self.errstream.getvalue()
        sys.stdout = self.old_sys_stdout
        sys.stderr = self.old_sys_stderr
        if exc_type is SystemExit:
            self.returncode = exc_val.code
            return True
        return False

    @property
    def returncode(self):
        return self._returncode
    @returncode.setter
    def returncode(self, value):
        self._returncode = value


def build_temp_workspace(files, base_path):
    """
    Build a temporary workspace within the given base directory.

    :param files: Dict mapping relative file paths to file content.
    :param base_path: The base directory (pytest tmp_path).
    :returns: The workspace path.
    """
    for rel_path, content in files.items():
        path = base_path / Path(rel_path)
        if not path.parent.exists():
            path.parent.mkdir(parents=True)
        if isinstance(content, list):
            path.mkdir()
        elif isinstance(content, str) and content.startswith('symlink://'):
            path.symlink_to(content[10:])
        else:
            mode = 'wb' if isinstance(content, bytes) else 'w'
            with path.open(mode) as f:
                f.write(content)
    return base_path


@pytest.fixture
def temp_workspace(tmp_path):
    """
    Provide a temporary workspace using the pytest tmp_path fixture.

    Yields:
        The workspace path.
    """
    backup_wd = Path.cwd()
    workspace = tmp_path
    Path(workspace).mkdir(parents=True, exist_ok=True)
    Path.chdir(workspace)
    try:
        yield workspace
    finally:
        Path.chdir(backup_wd)
