import pytest
from tests.common import RuleTestCase

@pytest.fixture
def tester():
    return RuleTestCase()

def test_disable_directive(tester):
    conf = ('commas: disable\n'
            'trailing-spaces: {}\n'
            'colons: {max-spaces-before: 1}\n')
    tester.check('---\n'
                 '- [valid , YAML]\n'
                 '- trailing spaces    \n'
                 '- bad   : colon\n'
                 '- [valid , YAML]\n'
                 '- bad  : colon and spaces   \n'
                 '- [valid , YAML]\n',
                 conf,
                 problem1=(3, 18, 'trailing-spaces'),
                 problem2=(4, 8, 'colons'),
                 problem3=(6, 7, 'colons'),
                 problem4=(6, 26, 'trailing-spaces'))
    tester.check('---\n'
                 '- [valid , YAML]\n'
                 '- trailing spaces    \n'
                 '# yamllint disable\n'
                 '- bad   : colon\n'
                 '- [valid , YAML]\n'
                 '- bad  : colon and spaces   \n'
                 '- [valid , YAML]\n',
                 conf,
                 problem=(3, 18, 'trailing-spaces'))
    tester.check('---\n'
                 '- [valid , YAML]\n'
                 '# yamllint disable\n'
                 '- trailing spaces    \n'
                 '- bad   : colon\n'
                 '- [valid , YAML]\n'
                 '# yamllint enable\n'
                 '- bad  : colon and spaces   \n'
                 '- [valid , YAML]\n',
                 conf,
                 problem1=(8, 7, 'colons'),
                 problem2=(8, 26, 'trailing-spaces'))

def test_disable_directive_with_rules(tester):
    conf = ('commas: disable\n'
            'trailing-spaces: {}\n'
            'colons: {max-spaces-before: 1}\n')
    tester.check('---\n'
                 '- [valid , YAML]\n'
                 '- trailing spaces    \n'
                 '# yamllint disable rule:trailing-spaces\n'
                 '- bad   : colon\n'
                 '- [valid , YAML]\n'
                 '- bad  : colon and spaces   \n'
                 '- [valid , YAML]\n',
                 conf,
                 problem1=(3, 18, 'trailing-spaces'),
                 problem2=(5, 8, 'colons'),
                 problem3=(7, 7, 'colons'))
    tester.check('---\n'
                 '- [valid , YAML]\n'
                 '# yamllint disable rule:trailing-spaces\n'
                 '- trailing spaces    \n'
                 '- bad   : colon\n'
                 '- [valid , YAML]\n'
                 '# yamllint enable rule:trailing-spaces\n'
                 '- bad  : colon and spaces   \n'
                 '- [valid , YAML]\n',
                 conf,
                 problem1=(5, 8, 'colons'),
                 problem2=(8, 7, 'colons'),
                 problem3=(8, 26, 'trailing-spaces'))
    tester.check('---\n'
                 '- [valid , YAML]\n'
                 '# yamllint disable rule:trailing-spaces\n'
                 '- trailing spaces    \n'
                 '- bad   : colon\n'
                 '- [valid , YAML]\n'
                 '# yamllint enable\n'
                 '- bad  : colon and spaces   \n'
                 '- [valid , YAML]\n',
                 conf,
                 problem1=(5, 8, 'colons'),
                 problem2=(8, 7, 'colons'),
                 problem3=(8, 26, 'trailing-spaces'))
    tester.check('---\n'
                 '- [valid , YAML]\n'
                 '# yamllint disable\n'
                 '- trailing spaces    \n'
                 '- bad   : colon\n'
                 '- [valid , YAML]\n'
                 '# yamllint enable rule:trailing-spaces\n'
                 '- bad  : colon and spaces   \n'
                 '- [valid , YAML]\n',
                 conf,
                 problem=(8, 26, 'trailing-spaces'))
    tester.check('---\n'
                 '- [valid , YAML]\n'
                 '# yamllint disable rule:colons\n'
                 '- trailing spaces    \n'
                 '# yamllint disable rule:trailing-spaces\n'
                 '- bad   : colon\n'
                 '- [valid , YAML]\n'
                 '# yamllint enable rule:colons\n'
                 '- bad  : colon and spaces   \n'
                 '- [valid , YAML]\n',
                 conf,
                 problem1=(4, 18, 'trailing-spaces'),
                 problem2=(9, 7, 'colons'))

def test_disable_line_directive(tester):
    conf = ('commas: disable\n'
            'trailing-spaces: {}\n'
            'colons: {max-spaces-before: 1}\n')
    tester.check('---\n'
                 '- [valid , YAML]\n'
                 '- trailing spaces    \n'
                 '# yamllint disable-line\n'
                 '- bad   : colon\n'
                 '- [valid , YAML]\n'
                 '- bad  : colon and spaces   \n'
                 '- [valid , YAML]\n',
                 conf,
                 problem1=(3, 18, 'trailing-spaces'),
                 problem2=(7, 7, 'colons'),
                 problem3=(7, 26, 'trailing-spaces'))
    tester.check('---\n'
                 '- [valid , YAML]\n'
                 '- trailing spaces    \n'
                 '- bad   : colon  # yamllint disable-line\n'
                 '- [valid , YAML]\n'
                 '- bad  : colon and spaces   \n'
                 '- [valid , YAML]\n',
                 conf,
                 problem1=(3, 18, 'trailing-spaces'),
                 problem2=(6, 7, 'colons'),
                 problem3=(6, 26, 'trailing-spaces'))
    tester.check('---\n'
                 '- [valid , YAML]\n'
                 '- trailing spaces    \n'
                 '- bad   : colon\n'
                 '- [valid , YAML]  # yamllint disable-line\n'
                 '- bad  : colon and spaces   \n'
                 '- [valid , YAML]\n',
                 conf,
                 problem1=(3, 18, 'trailing-spaces'),
                 problem2=(4, 8, 'colons'),
                 problem3=(6, 7, 'colons'),
                 problem4=(6, 26, 'trailing-spaces'))

def test_disable_line_directive_with_rules(tester):
    conf = ('commas: disable\n'
            'trailing-spaces: {}\n'
            'colons: {max-spaces-before: 1}\n')
    tester.check('---\n'
                 '- [valid , YAML]\n'
                 '# yamllint disable-line rule:colons\n'
                 '- trailing spaces    \n'
                 '- bad   : colon\n'
                 '- [valid , YAML]\n'
                 '- bad  : colon and spaces   \n'
                 '- [valid , YAML]\n',
                 conf,
                 problem1=(4, 18, 'trailing-spaces'),
                 problem2=(5, 8, 'colons'),
                 problem3=(7, 7, 'colons'),
                 problem4=(7, 26, 'trailing-spaces'))
    tester.check('---\n'
                 '- [valid , YAML]\n'
                 '- trailing spaces  # yamllint disable-line rule:colons  \n'
                 '- bad   : colon\n'
                 '- [valid , YAML]\n'
                 '- bad  : colon and spaces   \n'
                 '- [valid , YAML]\n',
                 conf,
                 problem1=(3, 55, 'trailing-spaces'),
                 problem2=(4, 8, 'colons'),
                 problem3=(6, 7, 'colons'),
                 problem4=(6, 26, 'trailing-spaces'))
    tester.check('---\n'
                 '- [valid , YAML]\n'
                 '- trailing spaces    \n'
                 '# yamllint disable-line rule:colons\n'
                 '- bad   : colon\n'
                 '- [valid , YAML]\n'
                 '- bad  : colon and spaces   \n'
                 '- [valid , YAML]\n',
                 conf,
                 problem1=(3, 18, 'trailing-spaces'),
                 problem2=(7, 7, 'colons'),
                 problem3=(7, 26, 'trailing-spaces'))
    tester.check('---\n'
                 '- [valid , YAML]\n'
                 '- trailing spaces    \n'
                 '- bad   : colon  # yamllint disable-line rule:colons\n'
                 '- [valid , YAML]\n'
                 '- bad  : colon and spaces   \n'
                 '- [valid , YAML]\n',
                 conf,
                 problem1=(3, 18, 'trailing-spaces'),
                 problem2=(6, 7, 'colons'),
                 problem3=(6, 26, 'trailing-spaces'))
    tester.check('---\n'
                 '- [valid , YAML]\n'
                 '- trailing spaces    \n'
                 '- bad   : colon\n'
                 '- [valid , YAML]\n'
                 '# yamllint disable-line rule:colons\n'
                 '- bad  : colon and spaces   \n'
                 '- [valid , YAML]\n',
                 conf,
                 problem1=(3, 18, 'trailing-spaces'),
                 problem2=(4, 8, 'colons'),
                 problem3=(7, 26, 'trailing-spaces'))
    tester.check('---\n'
                 '- [valid , YAML]\n'
                 '- trailing spaces    \n'
                 '- bad   : colon\n'
                 '- [valid , YAML]\n'
                 '# yamllint disable-line rule:colons rule:trailing-spaces\n'
                 '- bad  : colon and spaces   \n'
                 '- [valid , YAML]\n',
                 conf,
                 problem1=(3, 18, 'trailing-spaces'),
                 problem2=(4, 8, 'colons'))

def test_disable_directive_with_rules_and_dos_lines(tester):
    conf = ('commas: disable\n'
            'trailing-spaces: {}\n'
            'colons: {max-spaces-before: 1}\n'
            'new-lines: {type: dos}\n')
    tester.check('---\r\n'
                 '- [valid , YAML]\r\n'
                 '# yamllint disable rule:trailing-spaces\r\n'
                 '- trailing spaces    \r\n'
                 '- bad   : colon\r\n'
                 '- [valid , YAML]\r\n'
                 '# yamllint enable rule:trailing-spaces\r\n'
                 '- bad  : colon and spaces   \r\n'
                 '- [valid , YAML]\r\n',
                 conf,
                 problem1=(5, 8, 'colons'),
                 problem2=(8, 7, 'colons'),
                 problem3=(8, 26, 'trailing-spaces'))
    tester.check('---\r\n'
                 '- [valid , YAML]\r\n'
                 '- trailing spaces    \r\n'
                 '- bad   : colon\r\n'
                 '- [valid , YAML]\r\n'
                 '# yamllint disable-line rule:colons\r\n'
                 '- bad  : colon and spaces   \r\n'
                 '- [valid , YAML]\r\n',
                 conf,
                 problem1=(3, 18, 'trailing-spaces'),
                 problem2=(4, 8, 'colons'),
                 problem3=(7, 26, 'trailing-spaces'))

def test_directive_on_last_line(tester):
    conf = 'new-line-at-end-of-file: {}'
    tester.check('---\n'
                 'no new line',
                 conf,
                 problem=(2, 12, 'new-line-at-end-of-file'))
    tester.check('---\n'
                 '# yamllint disable\n'
                 'no new line',
                 conf)
    tester.check('---\n'
                 'no new line  # yamllint disable',
                 conf)

def test_indented_directive(tester):
    conf = 'brackets: {min-spaces-inside: 0, max-spaces-inside: 0}'
    tester.check('---\n'
                 '- a: 1\n'
                 '  b:\n'
                 '    c: [    x]\n',
                 conf,
                 problem=(4, 12, 'brackets'))
    tester.check('---\n'
                 '- a: 1\n'
                 '  b:\n'
                 '    # yamllint disable-line rule:brackets\n'
                 '    c: [    x]\n',
                 conf)

def test_directive_on_itself(tester):
    conf = ('comments: {min-spaces-from-content: 2}\n'
            'comments-indentation: {}\n')
    tester.check('---\n'
                 '- a: 1 # comment too close\n'
                 '  b:\n'
                 ' # wrong indentation\n'
                 '    c: [x]\n',
                 conf,
                 problem1=(2, 8, 'comments'),
                 problem2=(4, 2, 'comments-indentation'))
    tester.check('---\n'
                 '# yamllint disable\n'
                 '- a: 1 # comment too close\n'
                 '  b:\n'
                 ' # wrong indentation\n'
                 '    c: [x]\n',
                 conf)
    tester.check('---\n'
                 '- a: 1 # yamllint disable-line\n'
                 '  b:\n'
                 '    # yamllint disable-line\n'
                 ' # wrong indentation\n'
                 '    c: [x]\n',
                 conf)
    tester.check('---\n'
                 '- a: 1 # yamllint disable-line rule:comments\n'
                 '  b:\n'
                 '    # yamllint disable-line rule:comments-indentation\n'
                 ' # wrong indentation\n'
                 '    c: [x]\n',
                 conf)
    tester.check('---\n'
                 '# yamllint disable\n'
                 '- a: 1 # comment too close\n'
                 '  # yamllint enable rule:comments-indentation\n'
                 '  b:\n'
                 ' # wrong indentation\n'
                 '    c: [x]\n',
                 conf,
                 problem=(6, 2, 'comments-indentation'))

def test_disable_file_directive(tester):
    conf = ('comments: {min-spaces-from-content: 2}\n'
            'comments-indentation: {}\n')
    tester.check('# yamllint disable-file\n'
                 '---\n'
                 '- a: 1 # comment too close\n'
                 '  b:\n'
                 ' # wrong indentation\n'
                 '    c: [x]\n',
                 conf)
    tester.check('#    yamllint disable-file\n'
                 '---\n'
                 '- a: 1 # comment too close\n'
                 '  b:\n'
                 ' # wrong indentation\n'
                 '    c: [x]\n',
                 conf)
    tester.check('#yamllint disable-file\n'
                 '---\n'
                 '- a: 1 # comment too close\n'
                 '  b:\n'
                 ' # wrong indentation\n'
                 '    c: [x]\n',
                 conf)
    tester.check('#yamllint disable-file    \n'
                 '---\n'
                 '- a: 1 # comment too close\n'
                 '  b:\n'
                 ' # wrong indentation\n'
                 '    c: [x]\n',
                 conf)
    tester.check('---\n'
                 '# yamllint disable-file\n'
                 '- a: 1 # comment too close\n'
                 '  b:\n'
                 ' # wrong indentation\n'
                 '    c: [x]\n',
                 conf,
                 problem1=(3, 8, 'comments'),
                 problem2=(5, 2, 'comments-indentation'))
    tester.check('# yamllint disable-file: rules cannot be specified\n'
                 '---\n'
                 '- a: 1 # comment too close\n'
                 '  b:\n'
                 ' # wrong indentation\n'
                 '    c: [x]\n',
                 conf,
                 problem1=(3, 8, 'comments'),
                 problem2=(5, 2, 'comments-indentation'))
    tester.check('AAAA yamllint disable-file\n'
                 '---\n'
                 '- a: 1 # comment too close\n'
                 '  b:\n'
                 ' # wrong indentation\n'
                 '    c: [x]\n',
                 conf,
                 problem1=(1, 1, 'document-start'),
                 problem2=(3, 8, 'comments'),
                 problem3=(5, 2, 'comments-indentation'))

def test_disable_file_directive_not_at_first_position(tester):
    conf = ('commas: disable\n'
            'trailing-spaces: {}\n'
            'colons: {max-spaces-before: 1}\n')
    tester.check('# yamllint disable-file\n'
                 '---\n'
                 '- bad  : colon and spaces   \n',
                 conf)
    tester.check('---\n'
                 '# yamllint disable-file\n'
                 '- bad  : colon and spaces   \n',
                 conf,
                 problem1=(3, 7, 'colons'),
                 problem2=(3, 26, 'trailing-spaces'))

def test_disable_file_directive_with_syntax_error(tester):
    conf = ('commas: disable\n'
            'trailing-spaces: {}\n'
            'colons: {max-spaces-before: 1}\n')
    tester.check('# This file is not valid YAML (it is a Jinja template)\n'
                 '{% if extra_info %}\n'
                 'key1: value1\n'
                 '{% endif %}\n'
                 'key2: value2\n',
                 conf,
                 problem=(2, 2, 'syntax'))
    tester.check('# yamllint disable-file\n'
                 '# This file is not valid YAML (it is a Jinja template)\n'
                 '{% if extra_info %}\n'
                 'key1: value1\n'
                 '{% endif %}\n'
                 'key2: value2\n',
                 conf)

def test_disable_file_directive_with_dos_lines(tester):
    conf = ('commas: disable\n'
            'trailing-spaces: {}\n'
            'colons: {max-spaces-before: 1}\n')
    tester.check('# yamllint disable-file\r\n'
                 '---\r\n'
                 '- bad  : colon and spaces   \r\n',
                 conf)
    tester.check('# yamllint disable-file\r\n'
                 '# This file is not valid YAML (it is a Jinja template)\r\n'
                 '{% if extra_info %}\r\n'
                 'key1: value1\r\n'
                 '{% endif %}\r\n'
                 'key2: value2\r\n',
                 conf)
