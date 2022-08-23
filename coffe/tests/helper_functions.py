# -*- coding: utf-8 -*-

"""
Helper functions for tests
"""

from __future__ import absolute_import, division, print_function

import pandas


def are_csv_files_equal(file_a, file_b):
    """Check if two csv files are equal.
     Floats are considered equal within a threshold of 1e-7.
    """
    a = pandas.read_csv(file_a)
    b = pandas.read_csv(file_b)
    if any(a.keys() != b.keys()):
        return False
    if len(a) != len(b):
        return False
    if not (a.round(7) == b.round(7)).all().all():
        return False
    return True
