# -*- coding: utf-8 -*-

"""Validate the current working directory."""

from __future__ import absolute_import, division, print_function
import os


def validate_cwd(calc_type=None):
    """This function validates that the CWD is correct for the calculation type
    that is running. If not, then exit."""

    cwd = os.path.basename(os.getcwd())
    dirtest = 'False'

    if calc_type == 'quantum_opt':
        dirlist = ['00_Gamess_Opt', '00_Psi4_Opt']
    if calc_type == 'quantum_copt':
        dirlist = ['00_Gamess_cOpt', '00_Psi4_cOpt']

    for directory in dirlist:
        if directory in cwd:
            dirtest = 'True'

    if dirtest == "False":
        raise TypeError(cwd, "{} is not an appropriate directory for running "
                             "this.".format(cwd))
