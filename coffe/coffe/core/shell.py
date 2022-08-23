# -*- coding: utf-8 -*-

"""Console-related functions."""

from __future__ import absolute_import, division, print_function

import subprocess
import os


class ShellError(Exception):
    pass


def touch(fname, times=None):
    """Touch file."""
    with open(fname, 'a'):
        os.utime(fname, times)


def call_cmd(cmd, stdout_file, stdin_string=None, stderr_file=None, work_dir=None):
    """Calls a shell command.
    """
    # assertions
    if os.path.dirname(stdout_file) != "":
        assert os.path.isdir(os.path.dirname(stdout_file))
    if stderr_file is not None and os.path.dirname(stdout_file) != "":
        assert os.path.isdir(os.path.dirname(stderr_file))
    if work_dir is None:
        work_dir = os.getcwd()
    assert os.path.isdir(work_dir), \
        "Error to running call_cmd in working directory {}. Working directory does not exist.".format(work_dir)

    # open files
    stdout = open(stdout_file,"w")
    stderr = subprocess.STDOUT
    if stderr_file is not None:
        stderr = open(stderr_file,"w")
    stdin = stdin_string
    if stdin is not None:
        stdin = stdin.encode("latin-1")
        # This encoding ensures compatibility between python 2 and 3
    rc = 1
    p = None
    try:
        p = subprocess.Popen(cmd.strip().split(), stdout=stdout,
                 stdin=subprocess.PIPE, stderr=stderr, cwd=work_dir)
        p.communicate(input=stdin)
        rc = p.returncode
    except Exception as e:
        p.kill()    # avoid zombies
        raise ShellError("Error in calling {}. "
                         "See {} or {} for further information.".format(cmd, stdout_file, stderr_file))
    finally:
        stdout.close()
        if stderr_file is not None:
            stderr.close()
    if rc != 0:
        raise ShellError("Error. Command {} terminated with exit code {}. Terminating. See {} or {} "
                         "for further information.".format(cmd, rc, stdout_file, stderr_file))

