# -*- coding: utf-8 -*-

"""Tests for coffe.core.saver functions"""

from __future__ import absolute_import, division, print_function

import coffe.core.coffedir
from coffe.gmx.sim import GmxCalculation
from coffe.core import shell, saver, filesys
import os
import logging
from click.testing import CliRunner
from coffe import cli


class SomeClass(object):
    def __init__(self, tmppath):
        self.tmppath = tmppath
        self.testfile = os.path.join(self.tmppath,"test.txt")

    def __call__(self):
        shell.touch(self.testfile)


class SomeClassThatHasALogger(coffe.core.coffedir.CoffeWorkDir):
    """Logging instances are not pickleable"""
    def __init__(self, tmppath):
        super(SomeClassThatHasALogger, self).__init__(str(tmppath))
        self.testfile = os.path.join(self.work_dir,"test.txt")

    def __call__(self):
        shell.touch(self.testfile)
        assert isinstance(self.logger, logging.Logger)


def test_save(tmpdir):
    test = SomeClass(str(tmpdir))
    filename = os.path.join(str(tmpdir), "test.obj")
    saver.save(test, filename)
    assert os.path.isfile(filename)


def test_load(tmpdir):
    test = SomeClass(str(tmpdir))
    filename = os.path.join(str(tmpdir), "test.obj")
    saver.save(test, filename)
    test2 = saver.load(filename)
    test2()
    assert os.path.isfile(test2.testfile)


def test_load_run(tmpdir):
    test = SomeClass(str(tmpdir))
    filename = os.path.join(str(tmpdir), "test.obj")
    saver.save(test, filename)
    test2 = saver.load_and_run(filename)
    assert os.path.isfile(test2.testfile)


def test_run_cli(tmpdir):
    test = SomeClass(str(tmpdir))
    filename = os.path.join(str(tmpdir), "test.obj")
    saver.save(test, filename)

    runner = CliRunner()
    result = runner.invoke(cli.main, ['run-class', filename])
    assert result.exit_code == 0
    assert os.path.isfile(test.testfile)


def test_save_with_logger(tmpdir):
    test = SomeClassThatHasALogger(str(tmpdir))
    filename = os.path.join(str(tmpdir), "test.obj")
    saver.save(test, filename)


def test_load_with_logger(tmpdir):
    test = SomeClassThatHasALogger(str(tmpdir))
    filename = os.path.join(str(tmpdir), "test.obj")
    saver.save(test, filename)
    test2 = saver.load_and_run(filename)
    test2.logger.info("checking if logging works")
    assert os.path.isfile(test2.testfile)
