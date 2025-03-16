import io

import pytest

from yamllint import linter
from yamllint.config import YamlLintConfig


def fake_config():
    """Return a default fake configuration for linting.

    :return: YamlLintConfig instance
    """
    return YamlLintConfig('extends: default')

def test_run_on_string():
    """Test run on a string input."""
    linter.run('test: document', fake_config())

def test_run_on_bytes():
    """Test run on bytes input."""
    linter.run(b'test: document', fake_config())

def test_run_on_unicode():
    """Test run on unicode input."""
    linter.run('test: document', fake_config())

def test_run_on_stream():
    """Test run on a stream input."""
    linter.run(io.StringIO('hello'), fake_config())

def test_run_on_int():
    """Test that passing an int raises a TypeError."""
    with pytest.raises(TypeError):
        linter.run(42, fake_config())

def test_run_on_list():
    """Test that passing a list raises a TypeError."""
    with pytest.raises(TypeError):
        linter.run(['h', 'e', 'l', 'l', 'o'], fake_config())

def test_run_on_non_ascii_chars():
    """Test run on strings containing non-ASCII characters."""
    s = ('- hétérogénéité\n'
         '# 19.99 €\n')
    linter.run(s, fake_config())
    linter.run(s.encode('utf-8'), fake_config())
    linter.run(s.encode('iso-8859-15'), fake_config())

    s = ('- お早う御座います。\n'
         '# الأَبْجَدِيَّة العَرَبِيَّة\n')
    linter.run(s, fake_config())
    linter.run(s.encode('utf-8'), fake_config())

def test_linter_problem_repr_without_rule():
    """Test the string representation of a LintProblem without a rule id."""
    problem = linter.LintProblem(1, 2, 'problem')
    assert str(problem) == '1:2: problem'

def test_linter_problem_repr_with_rule():
    """Test the string representation of a LintProblem with a rule id."""
    problem = linter.LintProblem(1, 2, 'problem', 'rule-id')
    assert str(problem) == '1:2: problem (rule-id)'
