# -*- coding: utf-8 -*-

"""Tests for coffe.core.compat functions"""

from __future__ import absolute_import, division, print_function
import coffe.core.compat as compat


def test_get_function_args():
    def f(arg1,arg2):
        pass
    assert compat.get_function_args(f) == ['arg1', 'arg2']
