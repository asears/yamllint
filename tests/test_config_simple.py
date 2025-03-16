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

import pytest

from yamllint import config


def test_parse_config():
    """
    Test parsing of a valid config.
    
    :return: None
    """
    new = config.YamlLintConfig('rules:\n'
                                '  colons:\n'
                                '    max-spaces-before: 0\n'
                                '    max-spaces-after: 1\n')
    assert list(new.rules.keys()) == ['colons']
    assert new.rules['colons']['max-spaces-before'] == 0
    assert new.rules['colons']['max-spaces-after'] == 1
    assert len(new.enabled_rules(None)) == 1

def test_invalid_conf():
    """
    Test that an invalid YAML config raises YamlLintConfigError.
    
    :return: None
    """
    with pytest.raises(config.YamlLintConfigError):
        config.YamlLintConfig('not: valid: yaml')

def test_unknown_rule():
    """
    Test that a config with an unknown rule raises YamlLintConfigError.
    
    :return: None
    """
    with pytest.raises(config.YamlLintConfigError, match='invalid config: no such rule: "this-one-does-not-exist"'):
        config.YamlLintConfig('rules:\n'
                              '  this-one-does-not-exist: enable\n')

def test_missing_option():
    """
    Test that missing options are defaulted properly.
    
    :return: None
    """
    c = config.YamlLintConfig('rules:\n'
                              '  colons: enable\n')
    assert c.rules['colons']['max-spaces-before'] == 0
    assert c.rules['colons']['max-spaces-after'] == 1

    c = config.YamlLintConfig('rules:\n'
                              '  colons:\n'
                              '    max-spaces-before: 9\n')
    assert c.rules['colons']['max-spaces-before'] == 9
    assert c.rules['colons']['max-spaces-after'] == 1

def test_unknown_option():
    """
    Test that an unknown option in a rule raises YamlLintConfigError.
    
    :return: None
    """
    with pytest.raises(config.YamlLintConfigError, match='invalid config: unknown option "abcdef" for rule "colons"'):
        config.YamlLintConfig('rules:\n'
                              '  colons:\n'
                              '    max-spaces-before: 0\n'
                              '    max-spaces-after: 1\n'
                              '    abcdef: yes\n')

def test_yes_no_for_booleans():
    """
    Test that boolean values are handled correctly.
    
    :return: None
    """
    c = config.YamlLintConfig('rules:\n'
                              '  indentation:\n'
                              '    spaces: 2\n'
                              '    indent-sequences: true\n'
                              '    check-multi-line-strings: false\n')
    assert c.rules['indentation']['indent-sequences']
    assert c.rules['indentation']['check-multi-line-strings'] is False

    c = config.YamlLintConfig('rules:\n'
                              '  indentation:\n'
                              '    spaces: 2\n'
                              '    indent-sequences: yes\n'
                              '    check-multi-line-strings: false\n')
    assert c.rules['indentation']['indent-sequences']
    assert c.rules['indentation']['check-multi-line-strings'] is False

    c = config.YamlLintConfig('rules:\n'
                              '  indentation:\n'
                              '    spaces: 2\n'
                              '    indent-sequences: whatever\n'
                              '    check-multi-line-strings: false\n')
    assert c.rules['indentation']['indent-sequences'] == 'whatever'
    assert c.rules['indentation']['check-multi-line-strings'] is False

    with pytest.raises(config.YamlLintConfigError, match='invalid config: option "indent-sequences" of "indentation" '):
        config.YamlLintConfig('rules:\n'
                              '  indentation:\n'
                              '    spaces: 2\n'
                              '    indent-sequences: YES!\n'
                              '    check-multi-line-strings: false\n')

def test_enable_disable_keywords():
    """
    Test that enable/disable keywords are processed correctly.
    
    :return: None
    """
    c = config.YamlLintConfig('rules:\n'
                              '  colons: enable\n'
                              '  hyphens: disable\n')
    assert c.rules['colons'] == {'level': 'error',
                                 'max-spaces-after': 1,
                                 'max-spaces-before': 0}
    assert c.rules['hyphens'] is False

def test_validate_rule_conf():
    """
    Test the validate_rule_conf function with various configurations.
    
    :return: None
    """
    class Rule:
        ID = 'fake'

    assert config.validate_rule_conf(Rule, False) is False
    assert config.validate_rule_conf(Rule, {}) == {'level': 'error'}

    config.validate_rule_conf(Rule, {'level': 'error'})
    config.validate_rule_conf(Rule, {'level': 'warning'})
    with pytest.raises(config.YamlLintConfigError):
        config.validate_rule_conf(Rule, {'level': 'warn'})

    Rule.CONF = {'length': int}
    Rule.DEFAULT = {'length': 80}
    config.validate_rule_conf(Rule, {'length': 8})
    config.validate_rule_conf(Rule, {})
    with pytest.raises(config.YamlLintConfigError):
        config.validate_rule_conf(Rule, {'height': 8})

    Rule.CONF = {'a': bool, 'b': int}
    Rule.DEFAULT = {'a': True, 'b': -42}
    config.validate_rule_conf(Rule, {'a': True, 'b': 0})
    config.validate_rule_conf(Rule, {'a': True})
    config.validate_rule_conf(Rule, {'b': 0})
    with pytest.raises(config.YamlLintConfigError):
        config.validate_rule_conf(Rule, {'a': 1, 'b': 0})

    Rule.CONF = {'choice': (True, 88, 'str')}
    Rule.DEFAULT = {'choice': 88}
    config.validate_rule_conf(Rule, {'choice': True})
    config.validate_rule_conf(Rule, {'choice': 88})
    config.validate_rule_conf(Rule, {'choice': 'str'})
    with pytest.raises(config.YamlLintConfigError):
        config.validate_rule_conf(Rule, {'choice': False})
    with pytest.raises(config.YamlLintConfigError):
        config.validate_rule_conf(Rule, {'choice': 99})
    with pytest.raises(config.YamlLintConfigError):
        config.validate_rule_conf(Rule, {'choice': 'abc'})

    Rule.CONF = {'choice': (int, 'hardcoded')}
    Rule.DEFAULT = {'choice': 1337}
    config.validate_rule_conf(Rule, {'choice': 42})
    config.validate_rule_conf(Rule, {'choice': 'hardcoded'})
    config.validate_rule_conf(Rule, {})
    with pytest.raises(config.YamlLintConfigError):
        config.validate_rule_conf(Rule, {'choice': False})
    with pytest.raises(config.YamlLintConfigError):
        config.validate_rule_conf(Rule, {'choice': 'abc'})

    Rule.CONF = {'multiple': ['item1', 'item2', 'item3']}
    Rule.DEFAULT = {'multiple': ['item1']}
    config.validate_rule_conf(Rule, {'multiple': []})
    config.validate_rule_conf(Rule, {'multiple': ['item2']})
    config.validate_rule_conf(Rule, {'multiple': ['item2', 'item3']})
    config.validate_rule_conf(Rule, {})
    with pytest.raises(config.YamlLintConfigError):
        config.validate_rule_conf(Rule, {'multiple': 'item1'})
    with pytest.raises(config.YamlLintConfigError):
        config.validate_rule_conf(Rule, {'multiple': ['']})
    with pytest.raises(config.YamlLintConfigError):
        config.validate_rule_conf(Rule, {'multiple': ['item1', 4]})
    with pytest.raises(config.YamlLintConfigError):
        config.validate_rule_conf(Rule, {'multiple': ['item4']})

def test_invalid_rule():
    """
    Test that an invalid rule value raises YamlLintConfigError.
    
    :return: None
    """
    with pytest.raises(config.YamlLintConfigError, match='invalid config: rule "colons": should be either "enable", "disable" or a dict'):
        config.YamlLintConfig('rules:\n'
                              '  colons: invalid\n')

def test_invalid_ignore():
    """
    Test that an invalid ignore configuration raises YamlLintConfigError.
    
    :return: None
    """
    with pytest.raises(config.YamlLintConfigError, match='invalid config: ignore should contain file patterns'):
        config.YamlLintConfig('ignore: yes\n')

def test_invalid_rule_ignore():
    """
    Test that an invalid rule ignore configuration raises YamlLintConfigError.
    
    :return: None
    """
    with pytest.raises(config.YamlLintConfigError, match='invalid config: ignore should contain file patterns'):
        config.YamlLintConfig('rules:\n'
                              '  colons:\n'
                              '    ignore: yes\n')

def test_invalid_rule_ignore_from_file():
    """
    Test that an invalid rule ignore-from-file configuration raises YamlLintConfigError.
    
    :return: None
    """
    with pytest.raises(config.YamlLintConfigError):
        config.YamlLintConfig('rules:\n'
                              '  colons:\n'
                              '    ignore-from-file: 1337\n')

def test_invalid_locale():
    """
    Test that an invalid locale configuration raises YamlLintConfigError.
    
    :return: None
    """
    with pytest.raises(config.YamlLintConfigError, match='invalid config: locale should be a string'):
        config.YamlLintConfig('locale: yes\n')

def test_invalid_yaml_files():
    """
    Test that an invalid yaml-files configuration raises YamlLintConfigError.
    
    :return: None
    """
    with pytest.raises(config.YamlLintConfigError, match='invalid config: yaml-files should be a list of file patterns'):
        config.YamlLintConfig('yaml-files: yes\n')

