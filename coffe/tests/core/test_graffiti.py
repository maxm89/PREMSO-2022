# -*- coding: utf-8 -*-

"""Tests for the graffiti module (colored console output).
When debugging these tests for the first time, there were
some really awkward errors, because the loggers got in the way
with the pytest.logger.
Concretely, the global logger would keep complaining that
the color args were not resolved in msg % args.
The usage of the log record arguments as color styles
is of course a slight abuse of record.args, but anyway, t
hey should not be redirected to the pytest logger.

To prevent these issues in the future,
I required pytest >= 3.4 and set log_level=100 as default in
tox.ini (this setting applies also to running pytest outside tox).
"""

from __future__ import absolute_import, division, print_function

from coffe.core import graffiti, coffedir

import logging


def test_color():
    with graffiti.UseColor(3):
        assert "red" | graffiti.RED == graffiti.RED.ansi_sequence + "red" + graffiti.colors._reset
        print("darkgoldenrod" | graffiti.DARKGOLDENROD | graffiti.BOLD)


def test_omit_color():
    with graffiti.UseColor(False):
        assert graffiti.GREEN | "green" == "green"


def test_logging(tmpdir, capsys):
    coffedir.set_global_log_level(logging.INFO)
    with graffiti.UseColor(3):
        expected = ("test" | graffiti.RED) + "\n"
        with coffedir.CoffeWorkDir(str(tmpdir)) as cwd:
            cwd.logger.info("test", graffiti.RED)
            out, err = capsys.readouterr()
    with open(cwd.logfile, "r") as f:
        assert f.readlines()[-1].strip().split(" - ")[2] == "test"
    assert err == expected


def test_logging_twoargs(tmpdir, capsys):
    coffedir.set_global_log_level(logging.INFO)
    with graffiti.UseColor(3):
        expected = ("test" | graffiti.RED | graffiti.BOLD) + "\n"
        with coffedir.CoffeWorkDir(str(tmpdir)) as cwd:
            cwd.logger.info("test", graffiti.RED, graffiti.BOLD)
            out, err = capsys.readouterr()
    with open(cwd.logfile, "r") as f:
        assert f.readlines()[-1].strip().split(" - ")[2] == "test"
    assert err == expected


def test_logging_debug(tmpdir, capsys):
    coffedir.set_global_log_level(logging.DEBUG)
    with graffiti.UseColor(3):
        expected  = "test" | graffiti.DARKGOLDENROD | graffiti.UNDERLINE
        with coffedir.CoffeWorkDir(str(tmpdir)) as cwd:
            cwd.logger.debug("test", graffiti.DARKGOLDENROD, graffiti.UNDERLINE)
            out, err = capsys.readouterr()
    with open(cwd.logfile, "r") as f:
        assert f.readlines()[-1].strip().split(" - ")[2] == "test"
    assert err.split("\n")[-2] == expected


def test_default_styles(tmpdir, capsys):
    coffedir.set_global_log_level(logging.WARNING)
    with graffiti.UseColor(3):
        expected = "test" | graffiti.DARKORANGE | graffiti.BOLD
        with coffedir.CoffeWorkDir(str(tmpdir)) as cwd:
            cwd.logger.warning("test")
            out, err = capsys.readouterr()
    with open(cwd.logfile, "r") as f:
        assert f.readlines()[-1].strip().split(" - ")[2] == "test"
    assert err.split("\n")[-2] == expected


def test_logging_print(tmpdir, capsys):
    coffedir.set_global_log_level(logging.INFO)
    with graffiti.UseColor(3):
        expected = "  test 1" | graffiti.RED | graffiti.BOLD
        with coffedir.CoffeWorkDir(str(tmpdir)) as cwd:
            cwd.prnt("test", 1, graffiti.RED, graffiti.BOLD, indent=2)
            out, err = capsys.readouterr()
    with open(cwd.logfile, "r") as f:
        assert f.readlines()[-1].strip().split(" - ")[2] == "  " + "test 1"
    assert err.split("\n")[-2] == expected

