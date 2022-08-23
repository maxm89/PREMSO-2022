# -*- coding: utf-8 -*-

"""Tests for coffe.core.cluster.Cluster"""

from __future__ import absolute_import, division, print_function

from coffe.core import decorators, pkgdata

import pytest


class A:
    @decorators.args_from_configfile
    def __init__(self, arg1, arg2, arg3, arg4=None, arg5=None):
        self.args = [arg1, arg2, arg3, arg4, arg5]


@decorators.args_from_configfile
def some_function(arg1, arg2, arg3):
    return [arg1, arg2, arg3]


def test_args_from_configfile():

    # test on method
    a = A(1, 2, 3)
    assert a.args == [1, 2, 3, None, None]
    b = A(cfg_file=pkgdata.abspath("data/config.cfg"), section="test2")
    assert b.args == [100,101,102,None,None]
    c = A(1, 2, 3, 4, cfg_file=pkgdata.abspath("data/config.cfg"), section="test1")
    assert c.args == [10,11,12,13,14]

    # test on function
    result = some_function(cfg_file=pkgdata.abspath("data/config.cfg"), section="test2")
    assert result == [100,101,102]


def test_override_cfg_args():

    result = some_function(cfg_file=pkgdata.abspath("data/config.cfg"), section="test2", arg1=1000)
    assert result == [1000, 101, 102]


def test_xxx_failure():
    with pytest.raises(decorators.ConfigError):
        some_function(cfg_file=pkgdata.abspath("data/config.cfg"), section="test3")


def test_xxx_ok():
    result = some_function(cfg_file=pkgdata.abspath("data/config.cfg"), section="test3", arg3=1000)
    assert result == [100, 101, 1000]


def test_none_not_overrides():
    result = some_function(cfg_file=pkgdata.abspath("data/config.cfg"), section="test2", arg3=None)
    assert result == [100, 101, 102]


def test_failure():
    pass
