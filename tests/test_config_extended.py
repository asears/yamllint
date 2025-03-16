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

from yamllint import config


def test_extend_on_object():
    """Test extending configuration on object.
    
    :return: None
    """
    old = config.YamlLintConfig('rules:\n'
                                '  colons:\n'
                                '    max-spaces-before: 0\n'
                                '    max-spaces-after: 1\n')
    new = config.YamlLintConfig('rules:\n'
                                '  hyphens:\n'
                                '    max-spaces-after: 2\n')
    new.extend(old)

    assert sorted(new.rules.keys()) == ['colons', 'hyphens']
    assert new.rules['colons']['max-spaces-before'] == 0
    assert new.rules['colons']['max-spaces-after'] == 1
    assert new.rules['hyphens']['max-spaces-after'] == 2
    assert len(new.enabled_rules(None)) == 2

def test_extend_on_file(tmp_path):
    """Test extending configuration on file.
    
    :param tmp_path: pytest tmp_path fixture.
    :return: None
    """
    base = tmp_path / "base.yml"
    base.write_text('rules:\n'
                    '  colons:\n'
                    '    max-spaces-before: 0\n'
                    '    max-spaces-after: 1\n')
    c = config.YamlLintConfig('extends: ' + str(base) + '\n'
                              'rules:\n'
                              '  hyphens:\n'
                              '    max-spaces-after: 2\n')

    assert sorted(c.rules.keys()) == ['colons', 'hyphens']
    assert c.rules['colons']['max-spaces-before'] == 0
    assert c.rules['colons']['max-spaces-after'] == 1
    assert c.rules['hyphens']['max-spaces-after'] == 2
    assert len(c.enabled_rules(None)) == 2

def test_extend_remove_rule(tmp_path):
    """Test that a rule can be disabled via extension.
    
    :param tmp_path: pytest tmp_path fixture.
    :return: None
    """
    base = tmp_path / "base.yml"
    base.write_text('rules:\n'
                    '  colons:\n'
                    '    max-spaces-before: 0\n'
                    '    max-spaces-after: 1\n'
                    '  hyphens:\n'
                    '    max-spaces-after: 2\n')
    c = config.YamlLintConfig('extends: ' + str(base) + '\n'
                              'rules:\n'
                              '  colons: disable\n')

    assert sorted(c.rules.keys()) == ['colons', 'hyphens']
    assert not c.rules['colons']
    assert c.rules['hyphens']['max-spaces-after'] == 2
    assert len(c.enabled_rules(None)) == 1

def test_extend_edit_rule(tmp_path):
    """Test editing rule parameters in an extended config.
    
    :param tmp_path: pytest tmp_path fixture.
    :return: None
    """
    base = tmp_path / "base.yml"
    base.write_text('rules:\n'
                    '  colons:\n'
                    '    max-spaces-before: 0\n'
                    '    max-spaces-after: 1\n'
                    '  hyphens:\n'
                    '    max-spaces-after: 2\n')
    c = config.YamlLintConfig('extends: ' + str(base) + '\n'
                              'rules:\n'
                              '  colons:\n'
                              '    max-spaces-before: 3\n'
                              '    max-spaces-after: 4\n')

    assert sorted(c.rules.keys()) == ['colons', 'hyphens']
    assert c.rules['colons']['max-spaces-before'] == 3
    assert c.rules['colons']['max-spaces-after'] == 4
    assert c.rules['hyphens']['max-spaces-after'] == 2
    assert len(c.enabled_rules(None)) == 2

def test_extend_reenable_rule(tmp_path):
    """Test re-enabling a previously disabled rule.
    
    :param tmp_path: pytest tmp_path fixture.
    :return: None
    """
    base = tmp_path / "base.yml"
    base.write_text('rules:\n'
                    '  colons:\n'
                    '    max-spaces-before: 0\n'
                    '    max-spaces-after: 1\n'
                    '  hyphens: disable\n')
    c = config.YamlLintConfig('extends: ' + str(base) + '\n'
                              'rules:\n'
                              '  hyphens:\n'
                              '    max-spaces-after: 2\n')

    assert sorted(c.rules.keys()) == ['colons', 'hyphens']
    assert c.rules['colons']['max-spaces-before'] == 0
    assert c.rules['colons']['max-spaces-after'] == 1
    assert c.rules['hyphens']['max-spaces-after'] == 2
    assert len(c.enabled_rules(None)) == 2

def test_extend_recursive_default_values(tmp_path):
    """Test extended configuration merging with recursive default values.
    
    :param tmp_path: pytest tmp_path fixture.
    :return: None
    """
    # Part one: Update for braces rule.
    base_braces = tmp_path / "braces.yml"
    base_braces.write_text('rules:\n'
                           '  braces:\n'
                           '    max-spaces-inside: 1248\n')
    c = config.YamlLintConfig('extends: ' + str(base_braces) + '\n'
                              'rules:\n'
                              '  braces:\n'
                              '    min-spaces-inside-empty: 2357\n')

    assert c.rules['braces']['min-spaces-inside'] == 0
    assert c.rules['braces']['max-spaces-inside'] == 1248
    assert c.rules['braces']['min-spaces-inside-empty'] == 2357
    assert c.rules['braces']['max-spaces-inside-empty'] == -1

    # Part two: Update for colons rule.
    base_colons = tmp_path / "colons.yml"
    base_colons.write_text('rules:\n'
                           '  colons:\n'
                           '    max-spaces-before: 1337\n')
    c = config.YamlLintConfig('extends: ' + str(base_colons) + '\n'
                              'rules:\n'
                              '  colons: enable\n')

    assert c.rules['colons']['max-spaces-before'] == 1337
    assert c.rules['colons']['max-spaces-after'] == 1

    # Part three: Recursive disable then re-enable.
    base3 = tmp_path / "base3.yml"
    base3.write_text('rules:\n'
                     '  colons:\n'
                     '    max-spaces-before: 1337\n')
    intermediate = tmp_path / "intermediate.yml"
    intermediate.write_text('extends: ' + str(base3) + '\n'
                            'rules:\n'
                            '  colons: disable\n')
    c = config.YamlLintConfig('extends: ' + str(intermediate) + '\n'
                              'rules:\n'
                              '  colons: enable\n')

    assert c.rules['colons']['max-spaces-before'] == 0
    assert c.rules['colons']['max-spaces-after'] == 1

def test_extended_ignore_str(tmp_path):
    """Test extended configuration using ignore defined as string.
    
    :param tmp_path: pytest tmp_path fixture.
    :return: None
    """
    ignore_file = tmp_path / "ignore.yml"
    ignore_file.write_text('ignore: |\n  *.template.yaml\n')
    c = config.YamlLintConfig('extends: ' + str(ignore_file) + '\n')

    assert c.ignore.match_file('test.template.yaml') is True
    assert c.ignore.match_file('test.yaml') is False

def test_extended_ignore_list(tmp_path):
    """Test extended configuration using ignore defined as list.
    
    :param tmp_path: pytest tmp_path fixture.
    :return: None
    """
    ignore_file = tmp_path / "ignore.yml"
    ignore_file.write_text('ignore:\n  - "*.template.yaml"\n')
    c = config.YamlLintConfig('extends: ' + str(ignore_file) + '\n')

    assert c.ignore.match_file('test.template.yaml') is True
    assert c.ignore.match_file('test.yaml') is False
