# -*- coding: utf-8 -*-

"""Tests for `coffe misc` command line interface."""

from __future__ import absolute_import, division, print_function
import os
from coffe.misc import validate_cwd

def test_validate_cwd(tmpdir):
    directory_temp = tmpdir.mkdir("00_Psi4_Opt10-10")
    os.chdir(str(directory_temp))
    calc_type = 'quantum_opt'
    validate_cwd.validate_cwd(calc_type)
