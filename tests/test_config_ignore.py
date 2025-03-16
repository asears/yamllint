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

import os
import shutil

from tests.common import RunContext, build_temp_workspace
from yamllint import cli, config
from yamllint.config import YamlLintConfigError
import pytest

@pytest.fixture
def temp_workspace_ignore():
    bad_yaml = ('---\n'
                '- key: val1\n'
                '  key: val2\n'
                '- trailing space \n'
                '-    lonely hyphen\n')
    wd = build_temp_workspace({
        'bin/file.lint-me-anyway.yaml': bad_yaml,
        'bin/file.yaml': bad_yaml,
        'file-at-root.yaml': bad_yaml,
        'file.dont-lint-me.yaml': bad_yaml,
        'ign-dup/file.yaml': bad_yaml,
        'ign-dup/sub/dir/file.yaml': bad_yaml,
        'ign-trail/file.yaml': bad_yaml,
        'include/ign-dup/sub/dir/file.yaml': bad_yaml,
        's/s/ign-trail/file.yaml': bad_yaml,
        's/s/ign-trail/s/s/file.yaml': bad_yaml,
        's/s/ign-trail/s/s/file2.lint-me-anyway.yaml': bad_yaml,
    })
    backup_wd = os.getcwd()
    os.chdir(wd)
    yield wd
    os.chdir(backup_wd)
    shutil.rmtree(wd)

def test_extend_config_disable_rule():
    old = config.YamlLintConfig('extends: default')
    new = config.YamlLintConfig('extends: default\n'
                                'rules:\n'
                                '  trailing-spaces: disable\n')
    old.rules['trailing-spaces'] = False
    assert sorted(new.rules.keys()) == sorted(old.rules.keys())
    for rule in new.rules:
        assert new.rules[rule] == old.rules[rule]

def test_extend_config_override_whole_rule():
    old = config.YamlLintConfig('extends: default')
    new = config.YamlLintConfig('extends: default\n'
                                'rules:\n'
                                '  empty-lines:\n'
                                '    max: 42\n'
                                '    max-start: 43\n'
                                '    max-end: 44\n')
    old.rules['empty-lines']['max'] = 42
    old.rules['empty-lines']['max-start'] = 43
    old.rules['empty-lines']['max-end'] = 44
    assert sorted(new.rules.keys()) == sorted(old.rules.keys())
    for rule in new.rules:
        assert new.rules[rule] == old.rules[rule]
    assert new.rules['empty-lines']['max'] == 42
    assert new.rules['empty-lines']['max-start'] == 43
    assert new.rules['empty-lines']['max-end'] == 44

def test_extend_config_override_rule_partly():
    old = config.YamlLintConfig('extends: default')
    new = config.YamlLintConfig('extends: default\n'
                                'rules:\n'
                                '  empty-lines:\n'
                                '    max-start: 42\n')
    old.rules['empty-lines']['max-start'] = 42
    assert sorted(new.rules.keys()) == sorted(old.rules.keys())
    for rule in new.rules:
        assert new.rules[rule] == old.rules[rule]
    assert new.rules['empty-lines']['max'] == 2
    assert new.rules['empty-lines']['max-start'] == 42
    assert new.rules['empty-lines']['max-end'] == 0

def test_mutually_exclusive_ignore_keys():
    with pytest.raises(YamlLintConfigError):
        config.YamlLintConfig('extends: default\n'
                              'ignore-from-file: .gitignore\n'
                              'ignore: |\n'
                              '  *.dont-lint-me.yaml\n'
                              '  /bin/\n')

def test_ignore_from_file_not_exist():
    with pytest.raises(FileNotFoundError):
        config.YamlLintConfig('extends: default\n'
                              'ignore-from-file: not_found_file\n')

def test_ignore_from_file_incorrect_type():
    with pytest.raises(YamlLintConfigError):
        config.YamlLintConfig('extends: default\n'
                              'ignore-from-file: 0\n')
    with pytest.raises(YamlLintConfigError):
        config.YamlLintConfig('extends: default\n'
                              'ignore-from-file: [0]\n')

def test_no_ignore(temp_workspace_ignore, capsys):
    with pytest.raises(SystemExit):
        cli.run(('-f', 'parsable', '.'))
    out = capsys.readouterr().out
    out = '\n'.join(sorted(out.splitlines()))
    keydup = '[error] duplication of key "key" in mapping (key-duplicates)'
    trailing = '[error] trailing spaces (trailing-spaces)'
    hyphen = '[error] too many spaces after hyphen (hyphens)'
    expected = '\n'.join((
        './bin/file.lint-me-anyway.yaml:3:3: ' + keydup,
        './bin/file.lint-me-anyway.yaml:4:17: ' + trailing,
        './bin/file.lint-me-anyway.yaml:5:5: ' + hyphen,
        './bin/file.yaml:3:3: ' + keydup,
        './bin/file.yaml:4:17: ' + trailing,
        './bin/file.yaml:5:5: ' + hyphen,
        './file-at-root.yaml:3:3: ' + keydup,
        './file-at-root.yaml:4:17: ' + trailing,
        './file-at-root.yaml:5:5: ' + hyphen,
        './file.dont-lint-me.yaml:3:3: ' + keydup,
        './file.dont-lint-me.yaml:4:17: ' + trailing,
        './file.dont-lint-me.yaml:5:5: ' + hyphen,
        './ign-dup/file.yaml:3:3: ' + keydup,
        './ign-dup/file.yaml:4:17: ' + trailing,
        './ign-dup/file.yaml:5:5: ' + hyphen,
        './ign-dup/sub/dir/file.yaml:3:3: ' + keydup,
        './ign-dup/sub/dir/file.yaml:4:17: ' + trailing,
        './ign-dup/sub/dir/file.yaml:5:5: ' + hyphen,
        './ign-trail/file.yaml:3:3: ' + keydup,
        './ign-trail/file.yaml:4:17: ' + trailing,
        './ign-trail/file.yaml:5:5: ' + hyphen,
        './include/ign-dup/sub/dir/file.yaml:3:3: ' + keydup,
        './include/ign-dup/sub/dir/file.yaml:4:17: ' + trailing,
        './include/ign-dup/sub/dir/file.yaml:5:5: ' + hyphen,
        './s/s/ign-trail/file.yaml:3:3: ' + keydup,
        './s/s/ign-trail/file.yaml:4:17: ' + trailing,
        './s/s/ign-trail/file.yaml:5:5: ' + hyphen,
        './s/s/ign-trail/s/s/file.yaml:3:3: ' + keydup,
        './s/s/ign-trail/s/s/file.yaml:4:17: ' + trailing,
        './s/s/ign-trail/s/s/file.yaml:5:5: ' + hyphen,
        './s/s/ign-trail/s/s/file2.lint-me-anyway.yaml:3:3: ' + keydup,
        './s/s/ign-trail/s/s/file2.lint-me-anyway.yaml:4:17: ' + trailing,
        './s/s/ign-trail/s/s/file2.lint-me-anyway.yaml:5:5: ' + hyphen,
    ))
    assert out == expected

def test_run_with_ignore_str(temp_workspace_ignore, capsys):
    with open(os.path.join(temp_workspace_ignore, '.yamllint'), 'w') as f:
        f.write('extends: default\n'
                'ignore: |\n'
                '  *.dont-lint-me.yaml\n'
                '  /bin/\n'
                '  !/bin/*.lint-me-anyway.yaml\n'
                'rules:\n'
                '  key-duplicates:\n'
                '    ignore: |\n'
                '      /ign-dup\n'
                '  trailing-spaces:\n'
                '    ignore: |\n'
                '      ign-trail\n'
                '      !*.lint-me-anyway.yaml\n')
    with pytest.raises(SystemExit):
        cli.run(('-f', 'parsable', '.'))
    out = capsys.readouterr().out
    out = '\n'.join(sorted(out.splitlines()))
    docstart = '[warning] missing document start "---" (document-start)'
    keydup = '[error] duplication of key "key" in mapping (key-duplicates)'
    trailing = '[error] trailing spaces (trailing-spaces)'
    hyphen = '[error] too many spaces after hyphen (hyphens)'
    expected = '\n'.join((
        './.yamllint:1:1: ' + docstart,
        './bin/file.lint-me-anyway.yaml:3:3: ' + keydup,
        './bin/file.lint-me-anyway.yaml:4:17: ' + trailing,
        './bin/file.lint-me-anyway.yaml:5:5: ' + hyphen,
        './file-at-root.yaml:3:3: ' + keydup,
        './file-at-root.yaml:4:17: ' + trailing,
        './file-at-root.yaml:5:5: ' + hyphen,
        './ign-dup/file.yaml:4:17: ' + trailing,
        './ign-dup/file.yaml:5:5: ' + hyphen,
        './ign-dup/sub/dir/file.yaml:4:17: ' + trailing,
        './ign-dup/sub/dir/file.yaml:5:5: ' + hyphen,
        './ign-trail/file.yaml:3:3: ' + keydup,
        './ign-trail/file.yaml:5:5: ' + hyphen,
        './include/ign-dup/sub/dir/file.yaml:3:3: ' + keydup,
        './include/ign-dup/sub/dir/file.yaml:4:17: ' + trailing,
        './include/ign-dup/sub/dir/file.yaml:5:5: ' + hyphen,
        './s/s/ign-trail/file.yaml:3:3: ' + keydup,
        './s/s/ign-trail/file.yaml:5:5: ' + hyphen,
        './s/s/ign-trail/s/s/file.yaml:3:3: ' + keydup,
        './s/s/ign-trail/s/s/file.yaml:5:5: ' + hyphen,
        './s/s/ign-trail/s/s/file2.lint-me-anyway.yaml:3:3: ' + keydup,
        './s/s/ign-trail/s/s/file2.lint-me-anyway.yaml:4:17: ' + trailing,
        './s/s/ign-trail/s/s/file2.lint-me-anyway.yaml:5:5: ' + hyphen,
    ))
    assert out == expected

def test_run_with_ignore_list(temp_workspace_ignore, capsys):
    with open(os.path.join(temp_workspace_ignore, '.yamllint'), 'w') as f:
        f.write('extends: default\n'
                'ignore:\n'
                '  - "*.dont-lint-me.yaml"\n'
                '  - "/bin/"\n'
                '  - "!/bin/*.lint-me-anyway.yaml"\n'
                'rules:\n'
                '  key-duplicates:\n'
                '    ignore:\n'
                '      - "/ign-dup"\n'
                '  trailing-spaces:\n'
                '    ignore:\n'
                '      - "ign-trail"\n'
                '      - "!*.lint-me-anyway.yaml"\n')
    with pytest.raises(SystemExit):
        cli.run(('-f', 'parsable', '.'))
    out = capsys.readouterr().out
    out = '\n'.join(sorted(out.splitlines()))
    docstart = '[warning] missing document start "---" (document-start)'
    keydup = '[error] duplication of key "key" in mapping (key-duplicates)'
    trailing = '[error] trailing spaces (trailing-spaces)'
    hyphen = '[error] too many spaces after hyphen (hyphens)'
    expected = '\n'.join((
        './.yamllint:1:1: ' + docstart,
        './bin/file.lint-me-anyway.yaml:3:3: ' + keydup,
        './bin/file.lint-me-anyway.yaml:4:17: ' + trailing,
        './bin/file.lint-me-anyway.yaml:5:5: ' + hyphen,
        './file-at-root.yaml:3:3: ' + keydup,
        './file-at-root.yaml:4:17: ' + trailing,
        './file-at-root.yaml:5:5: ' + hyphen,
        './ign-dup/file.yaml:4:17: ' + trailing,
        './ign-dup/file.yaml:5:5: ' + hyphen,
        './ign-dup/sub/dir/file.yaml:4:17: ' + trailing,
        './ign-dup/sub/dir/file.yaml:5:5: ' + hyphen,
        './ign-trail/file.yaml:3:3: ' + keydup,
        './ign-trail/file.yaml:5:5: ' + hyphen,
        './include/ign-dup/sub/dir/file.yaml:3:3: ' + keydup,
        './include/ign-dup/sub/dir/file.yaml:4:17: ' + trailing,
        './include/ign-dup/sub/dir/file.yaml:5:5: ' + hyphen,
        './s/s/ign-trail/file.yaml:3:3: ' + keydup,
        './s/s/ign-trail/file.yaml:5:5: ' + hyphen,
        './s/s/ign-trail/s/s/file.yaml:3:3: ' + keydup,
        './s/s/ign-trail/s/s/file.yaml:5:5: ' + hyphen,
        './s/s/ign-trail/s/s/file2.lint-me-anyway.yaml:3:3: ' + keydup,
        './s/s/ign-trail/s/s/file2.lint-me-anyway.yaml:4:17: ' + trailing,
        './s/s/ign-trail/s/s/file2.lint-me-anyway.yaml:5:5: ' + hyphen,
    ))
    assert out == expected

def test_run_with_ignore_from_file(temp_workspace_ignore, capsys):
    with open(os.path.join(temp_workspace_ignore, '.yamllint'), 'w') as f:
        f.write('extends: default\n'
                'ignore-from-file: .gitignore\n'
                'rules:\n'
                '  key-duplicates:\n'
                '    ignore-from-file: .ignore-key-duplicates\n')
    with open(os.path.join(temp_workspace_ignore, '.gitignore'), 'w') as f:
        f.write('*.dont-lint-me.yaml\n'
                '/bin/\n'
                '!/bin/*.lint-me-anyway.yaml\n')
    with open(os.path.join(temp_workspace_ignore, '.ignore-key-duplicates'), 'w') as f:
        f.write('/ign-dup\n')
    with pytest.raises(SystemExit):
        cli.run(('-f', 'parsable', '.'))
    out = capsys.readouterr().out
    out = '\n'.join(sorted(out.splitlines()))
    docstart = '[warning] missing document start "---" (document-start)'
    keydup = '[error] duplication of key "key" in mapping (key-duplicates)'
    trailing = '[error] trailing spaces (trailing-spaces)'
    hyphen = '[error] too many spaces after hyphen (hyphens)'
    expected = '\n'.join((
        './.yamllint:1:1: ' + docstart,
        './bin/file.lint-me-anyway.yaml:3:3: ' + keydup,
        './bin/file.lint-me-anyway.yaml:4:17: ' + trailing,
        './bin/file.lint-me-anyway.yaml:5:5: ' + hyphen,
        './file-at-root.yaml:3:3: ' + keydup,
        './file-at-root.yaml:4:17: ' + trailing,
        './file-at-root.yaml:5:5: ' + hyphen,
        './ign-dup/file.yaml:4:17: ' + trailing,
        './ign-dup/file.yaml:5:5: ' + hyphen,
        './ign-dup/sub/dir/file.yaml:4:17: ' + trailing,
        './ign-dup/sub/dir/file.yaml:5:5: ' + hyphen,
        './ign-trail/file.yaml:3:3: ' + keydup,
        './ign-trail/file.yaml:4:17: ' + trailing,
        './ign-trail/file.yaml:5:5: ' + hyphen,
        './include/ign-dup/sub/dir/file.yaml:3:3: ' + keydup,
        './include/ign-dup/sub/dir/file.yaml:4:17: ' + trailing,
        './include/ign-dup/sub/dir/file.yaml:5:5: ' + hyphen,
        './s/s/ign-trail/file.yaml:3:3: ' + keydup,
        './s/s/ign-trail/file.yaml:4:17: ' + trailing,
        './s/s/ign-trail/file.yaml:5:5: ' + hyphen,
        './s/s/ign-trail/s/s/file.yaml:3:3: ' + keydup,
        './s/s/ign-trail/s/s/file.yaml:4:17: ' + trailing,
        './s/s/ign-trail/s/s/file.yaml:5:5: ' + hyphen,
        './s/s/ign-trail/s/s/file2.lint-me-anyway.yaml:3:3: ' + keydup,
        './s/s/ign-trail/s/s/file2.lint-me-anyway.yaml:4:17: ' + trailing,
        './s/s/ign-trail/s/s/file2.lint-me-anyway.yaml:5:5: ' + hyphen,
    ))
    assert out == expected

def test_run_with_ignored_from_file(temp_workspace_ignore, capsys):
    with open(os.path.join(temp_workspace_ignore, '.yamllint'), 'w') as f:
        f.write('ignore-from-file: [.gitignore, .yamlignore]\n'
                'extends: default\n')
    with open(os.path.join(temp_workspace_ignore, '.gitignore'), 'w') as f:
        f.write('*.dont-lint-me.yaml\n'
                '/bin/\n')
    with open(os.path.join(temp_workspace_ignore, '.yamlignore'), 'w') as f:
        f.write('!/bin/*.lint-me-anyway.yaml\n')
    with pytest.raises(SystemExit):
        cli.run(('-f', 'parsable', '.'))
    out = capsys.readouterr().out
    out = '\n'.join(sorted(out.splitlines()))
    docstart = '[warning] missing document start "---" (document-start)'
    keydup = '[error] duplication of key "key" in mapping (key-duplicates)'
    trailing = '[error] trailing spaces (trailing-spaces)'
    hyphen = '[error] too many spaces after hyphen (hyphens)'
    expected = '\n'.join((
        './.yamllint:1:1: ' + docstart,
        './bin/file.lint-me-anyway.yaml:3:3: ' + keydup,
        './bin/file.lint-me-anyway.yaml:4:17: ' + trailing,
        './bin/file.lint-me-anyway.yaml:5:5: ' + hyphen,
        './file-at-root.yaml:3:3: ' + keydup,
        './file-at-root.yaml:4:17: ' + trailing,
        './file-at-root.yaml:5:5: ' + hyphen,
        './ign-dup/file.yaml:3:3: ' + keydup,
        './ign-dup/file.yaml:4:17: ' + trailing,
        './ign-dup/file.yaml:5:5: ' + hyphen,
        './ign-dup/sub/dir/file.yaml:3:3: ' + keydup,
        './ign-dup/sub/dir/file.yaml:4:17: ' + trailing,
        './ign-dup/sub/dir/file.yaml:5:5: ' + hyphen,
        './ign-trail/file.yaml:3:3: ' + keydup,
        './ign-trail/file.yaml:4:17: ' + trailing,
        './ign-trail/file.yaml:5:5: ' + hyphen,
        './include/ign-dup/sub/dir/file.yaml:3:3: ' + keydup,
        './include/ign-dup/sub/dir/file.yaml:4:17: ' + trailing,
        './include/ign-dup/sub/dir/file.yaml:5:5: ' + hyphen,
        './s/s/ign-trail/file.yaml:3:3: ' + keydup,
        './s/s/ign-trail/file.yaml:4:17: ' + trailing,
        './s/s/ign-trail/file.yaml:5:5: ' + hyphen,
        './s/s/ign-trail/s/s/file.yaml:3:3: ' + keydup,
        './s/s/ign-trail/s/s/file.yaml:4:17: ' + trailing,
        './s/s/ign-trail/s/s/file.yaml:5:5: ' + hyphen,
        './s/s/ign-trail/s/s/file2.lint-me-anyway.yaml:3:3: ' + keydup,
        './s/s/ign-trail/s/s/file2.lint-me-anyway.yaml:4:17: ' + trailing,
        './s/s/ign-trail/s/s/file2.lint-me-anyway.yaml:5:5: ' + hyphen,
    ))
    assert out == expected

def test_run_with_ignore_with_broken_symlink():
    wd = build_temp_workspace({
        'file-without-yaml-extension': '42\n',
        'link.yaml': 'symlink://file-without-yaml-extension',
        'link-404.yaml': 'symlink://file-that-does-not-exist',
    })
    backup_wd = os.getcwd()
    os.chdir(wd)
    with RunContext() as ctx:
        cli.run(('-f', 'parsable', '.'))
    assert ctx.returncode != 0
    with open(os.path.join(wd, '.yamllint'), 'w') as f:
        f.write('extends: default\n'
                'ignore: |\n'
                '  *404.yaml\n')
    with RunContext() as ctx:
        cli.run(('-f', 'parsable', '.'))
    assert ctx.returncode == 0
    docstart = '[warning] missing document start "---" (document-start)'
    out = '\n'.join(sorted(ctx.stdout.splitlines()))
    expected = '\n'.join((
        './.yamllint:1:1: ' + docstart,
        './link.yaml:1:1: ' + docstart,
    ))
    assert out == expected
    os.chdir(backup_wd)
    shutil.rmtree(wd)

def test_run_with_ignore_on_ignored_file(temp_workspace_ignore, capsys):
    with open(os.path.join(temp_workspace_ignore, '.yamllint'), 'w') as f:
        f.write('ignore: file.dont-lint-me.yaml\n'
                'rules:\n'
                '  trailing-spaces: enable\n'
                '  key-duplicates:\n'
                '    ignore: file-at-root.yaml\n')
    with pytest.raises(SystemExit):
        cli.run(('-f', 'parsable', 'file.dont-lint-me.yaml',
                 'file-at-root.yaml'))
    captured = capsys.readouterr().out.strip()
    assert captured == ('file-at-root.yaml:4:17: [error] trailing spaces (trailing-spaces)')
