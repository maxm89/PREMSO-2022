# -*- coding: utf-8 -*-

"""Utility and helper functions for Amber"""

from __future__ import absolute_import, division, print_function

from coffe.core import filesys
import os
import f90nml
import fileinput


def amb_parse_fatal_error(filename):
    """Extract error message from sander output.
    Arguments:
        file  --  a file containing sander's stderr output
    """
    errmsg = ""
    in_msg = False
    with open(filename, "r") as f:
        for line in f:
            if line.strip().lower().startswith("fatal"):
                in_msg = True
            if in_msg:
                errmsg += line
    return errmsg


class AmberError(Exception):
    def __init__(self, exception, stderr_file):
        try:
            amb_msg = amb_parse_fatal_error(stderr_file)
            assert amb_msg != ""
            msg = amb_msg + ("Details in {}\n\n\n".format(stderr_file))
            super(AmberError, self).__init__(msg)
        except Exception as e:
            super(AmberError, self).__init__(str(exception))


# TODO (MS): def amb_make_top


# ======================================================== #
# ========== READING AND MANIPULATING MDIN FILES ==========#
# ======================================================== #


def set_mdin_options(mdin, options, new_file=None):
    """Set options in an mdin file (sander configuration file).
    Note that options are case sensitive.
    Arguments:
        mdin        --  the file
        options     --  a dictionary {"nml.key": value}
        new_file    --  (optional) if specified, a copy is created and the
                        original file is not touched
    """
    assert isinstance(mdin, str) and os.path.isfile(mdin)
    assert isinstance(options, dict)
    if new_file is not None:
        assert filesys.is_writable(os.path.dirname(new_file))

    # read header
    with open(mdin) as f:
        header = f.readline()

    # read mdin
    mdin_nml = f90nml.read(mdin)
    # manipulate
    for option in options:
        nml, key = option.split(".")
        mdin_nml[nml][key] = [options[option]]

    # write
    mdin_nml.write(new_file)

    # write header
    for line in fileinput.input(new_file, inplace=True):
        if fileinput.isfirstline():
            print(header)
        print(line.strip())


def read_mdin_option(mdin, option):
    """Read options from an mdin file (sander configuration).
    Arguments:
        mdin         --  the file
        option        --  the option to be read {"nml.key"}
    Returns:            the option's value as a string
    """
    assert os.path.isfile(mdin)
    nml, key = option.split(".")
    assert isinstance(nml, str)
    assert isinstance(key, str)
    result = None

    mdin_nml = f90nml.read(mdin)
    val = mdin_nml[nml][key]
    if val is not None:
        result = val

    assert result is not None, "No option {} in namelist block {} mdin file {}"\
        .format(key, nml, mdin)
    return result
