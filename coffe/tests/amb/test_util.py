# -*- coding: utf-8 -*-

"""Tests for coffe.amb.util functions"""

from __future__ import absolute_import, division, print_function
import os
import shutil
import coffe.amb.util as ambutil
from coffe.core import pkgdata, thirdparty
import pytest

# skip all if amber is not installed
pytestmark = pytest.mark.skipif(not thirdparty.AMBER.exists,
                                reason="The tests in this module require a "
                                       "functioning amber (sander) installation"
                                )


def test_read_mdin_option():
    # test for option at the beginning of a line in mdin
    mdp = pkgdata.abspath("data/test_mdin")
    option = "cntrl.nstlim"
    val = 100
    assert ambutil.read_mdin_option(mdp, option) == val


def test_read_mdin_option2():
    # test for option at the beginning of a line in mdin
    mdp = pkgdata.abspath("data/test_mdin")
    option = "cntrl.dt"
    val = 0.002
    assert ambutil.read_mdin_option(mdp, option) == val


def test_read_mdin_option3():
    # test for option at the beginning of a line in mdin
    mdp = pkgdata.abspath("data/test_mdin")
    option = "ewald.skinnb"
    val = 2.0
    assert ambutil.read_mdin_option(mdp, option) == val


def test_set_mdin_options(tmpdir):
    mdin = os.path.join(str(tmpdir), "test_mdin")
    mdin_edited = os.path.join(str(tmpdir), "test_mdin_edited")
    shutil.copy(pkgdata.abspath("data/test_mdin"), mdin)
    options = {"cntrl.nstlim": 99,
               "cntrl.hey": "jude",
               "ewald.skinnb": 3.1415926}
    ambutil.set_mdin_options(mdin, options, new_file=mdin_edited)
    for key in options:
        assert ambutil.read_mdin_option(mdin_edited, key) == options[key]


def test_read_not_exists():
    mdp = pkgdata.abspath("data/test_mdddddin")  # This doesn't exist
    option = "cntrl.nstlim"
    with pytest.raises(AssertionError):
        ambutil.read_mdin_option(mdp, option)


def test_read_no_such_namelist():
    mdp = pkgdata.abspath("data/test_mddin")
    option = "wegrrewf.nstlim"  # This doesn't exist.
    with pytest.raises(AssertionError):
        ambutil.read_mdin_option(mdp, option)


def test_read_no_such_option():
    mdp = pkgdata.abspath("data/test_mdin")
    option = "cntrl.foaeghrers"  # This doesn't exist
    with pytest.raises(KeyError):
        ambutil.read_mdin_option(mdp, option)


def test_type_failure(tmpdir):
    mdin = os.path.join(str(tmpdir), "test_mdin")
    shutil.copy(pkgdata.abspath("data/test_mdin"), mdin)
    with pytest.raises(AssertionError):
        ambutil.set_mdin_options(mdin, [], [])
    with pytest.raises(AssertionError):
        ambutil.set_mdin_options(1, {}, {})


def test_set_and_read_mdin_option_newfile(tmpdir):
    mdin = os.path.join(str(tmpdir), "test_mdin")
    options = {"cntrl.nstlim": 99,
               "cntrl.hey": "jude",
               "ewald.skinnb": 3.1415926}
    ambutil.set_mdin_options(pkgdata.abspath("data/test_mdin"), options,
                             new_file=mdin)
    for key in options:
        assert ambutil.read_mdin_option(mdin, key) == options[key]
