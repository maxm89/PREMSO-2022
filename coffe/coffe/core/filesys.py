# -*- coding: utf-8 -*-

"""Filesystem-related functions."""

from __future__ import absolute_import, division, print_function

import os
import time


def make_abspath(path, work_dir, check_exists=True):
    assert isinstance(path, str), "Path {} must be string.".format(path)
    assert isinstance(work_dir, str), "Directory {} must be string".format(work_dir)
    result = os.path.abspath(os.path.expandvars(os.path.expanduser(os.path.join(work_dir, path))))
    if check_exists:
        assert os.path.exists(result), "Path {} does not exist".format(result)
    return result


def parent_dir(directory):
    assert os.path.isdir(directory)
    return os.path.abspath(os.path.join(directory, os.pardir))


def is_writable(directory):
    assert os.path.isdir(directory)
    f = os.path.join(directory, "test.txt")
    try:
        with open(f, 'a'):
            os.utime(f, None)
        os.remove(f)
        return True
    except IOError:
        return False


def stdout_filename(directory, cmd):
    t = time.strftime("%Y_%m_%d_%H%M%S")
    return os.path.abspath(
        os.path.join(directory, "{}-{}.out".format(t, cmd.replace(' ', '')))
    )


def stderr_filename(dir, cmd):
    t = time.strftime("%Y_%m_%d_%H%M%S")
    return os.path.abspath(
        os.path.join(dir, "{}-{}.err".format(t,cmd.replace(' ','')))
    )


def batch_filename(dir, jobname=None):
    t = time.strftime("%Y_%m_%d_%H%M%S")
    if jobname is not None:
        return os.path.abspath(
            os.path.join(dir, "batch-{}-{}.sh".format(t, jobname.replace(' ','')))
        )
    else:
        return os.path.abspath(
            os.path.join(dir, "batch-{}.sh".format(t))
        )


def grep_line(filename, string):
    """
    get first line that matches a given string
    """
    with open(filename,"r") as fh:
        for line in fh:
            if string in line:
                return line


def basename(path):
    assert isinstance(path, str), "Path {} must be string.".format(path)
    result = os.path.basename(path)
    return result

