# -*- coding: utf-8 -*-

"""Tests for coffe.core.shell functions"""

from __future__ import absolute_import, division, print_function

from coffe.core import shell
import pytest
import os


@pytest.fixture
def mktmp(tmpdir):
    tmp = str(tmpdir)
    return (tmp, os.path.join(tmp, "stdout.txt"),
            os.path.join(tmp, "stderr.txt"),
            os.path.join(tmp, "test.txt"),
            os.path.join(tmp, "test2.txt")
            )


def test_touch(mktmp):
    tmp, stdo, stde, f, f2 = mktmp
    shell.touch(f)
    assert os.path.isfile(f)


def test_shell(mktmp):
    tmp, stdo, stde,f,f2 = mktmp
    shell.touch(f)
    shell.call_cmd("cp {} {}".format(f,f2), stdo, work_dir=tmp)
    assert os.path.isfile(f2)
    assert os.path.isfile(stdo)


def test_shell_failure(mktmp):
    tmp, stdo, stde, f, f2 = mktmp
    with pytest.raises(shell.ShellError) as e_info:
        shell.call_cmd("cp {} {}".format(f,f2), stdo, stderr_file=stde, work_dir=tmp)
        # assert "No such file or directory" in e_info
    assert os.path.isfile(stdo)
    assert os.path.isfile(stde)
    #with open(stde,"r") as f:
    #    assert "No such file or directory" in f.read()
    assert not os.path.isfile(f2)

