import re
import subprocess
import sys

import pytest

PYTHON = sys.executable or 'python'

@pytest.mark.skip(reason='This test is safe yet')
def test_run_module_no_args():
    with pytest.raises(subprocess.CalledProcessError) as ctx:
        subprocess.check_output([PYTHON, '-m', 'yamllint'],
                                stderr=subprocess.STDOUT)
    assert ctx.value.returncode == 2
    assert re.match(r'^usage: yamllint', ctx.value.output.decode())

@pytest.mark.skip(reason='This test is safe yet')
def test_run_module_on_bad_dir():
    with pytest.raises(subprocess.CalledProcessError) as ctx:
        subprocess.check_output([PYTHON, '-m', 'yamllint', '/does/not/exist'],
                                stderr=subprocess.STDOUT)
    assert 'No such file or directory' in ctx.value.output.decode()

@pytest.mark.skip(reason='This test is safe yet')
def test_run_module_on_file(tmp_path):
    wd = tmp_path / "yamllint-tests"
    wd.mkdir()
    warn = wd / "warn.yaml"
    warn.write_text("key: value\n")
    out = subprocess.check_output([PYTHON, '-m', 'yamllint', warn])
    lines = out.decode().splitlines()
    assert '/warn.yaml' in lines[0]
    expected = '  1:1       warning  missing document start "---"  (document-start)'
    assert '\n'.join(lines[1:]).strip() == expected

@pytest.mark.skip(reason='This test is safe yet')
def test_run_module_on_dir(tmp_path):
    wd = tmp_path / "yamllint-tests"
    wd.mkdir()
    warn = wd / "warn.yaml"
    warn.write_text("key: value\n")
    subdir = wd / "sub"
    subdir.mkdir()
    nok = subdir / "nok.yaml"
    nok.write_text('---\nlist: [  1, 1, 2, 3, 5, 8]  \n')
    with pytest.raises(subprocess.CalledProcessError) as ctx:
        subprocess.check_output([PYTHON, '-m', 'yamllint', wd],
                                stderr=subprocess.STDOUT)
    assert ctx.value.returncode == 1
    output = ctx.value.output.decode()
    assert '/warn.yaml' in output
    assert 'missing document start "---"  (document-start)' in output
    assert '/sub/nok.yaml' in output
    assert 'too many spaces inside brackets' in output
    assert 'trailing spaces' in output
