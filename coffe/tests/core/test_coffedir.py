# -*- coding: utf-8 -*-

"""Tests for coffe.core.coffedir"""

from __future__ import absolute_import, division, print_function


from coffe.core import coffedir
import logging
import pytest
import shutil
import os


def test_prepare_coffe_work_dir(tmpdir):
    d = os.path.join(str(tmpdir), "test")
    _work_dir, coffe_dir, logger = coffedir.prepare_coffe_work_dir(d)
    assert os.path.isdir(d)
    assert os.path.isdir(coffe_dir)
    assert os.path.isdir(_work_dir)
    assert coffe_dir == os.path.join(d,".coffe")

    logger.info("Test log.")
    logfile = os.path.join(coffe_dir, "log.txt")
    assert os.path.isfile(logfile)
    with open(logfile,"r") as f:
        log = f.read()
        assert "Test log." in log


def test_invalid_decorator():
    with pytest.raises(AssertionError):
        def tmp():
            pass
        coffedir.log_exceptions(tmp)


def test_valid_decorator():
    class T:
        def tmp(self):
            pass
    coffedir.log_exceptions(T().tmp)


class CustomException(Exception): pass


def test_catch_exception():
    class Logger:
        def __init__(self):
            self.out = ""
        def exception(self, str):
            self.out = str

    class T:
        def __init__(self):
            self.logger = Logger()
        @coffedir.log_exceptions
        def tmp(self):
            raise CustomException("Nooo")
    t = T()
    with pytest.raises(CustomException):
        t.tmp()
    assert str(t.logger.out) == "Nooo"



def test_workdir_create(tmpdir):
    coffedir.CoffeWorkDir(str(tmpdir))


def test_workdir_dirs(tmpdir):
    tmp = str(tmpdir)
    cwd = coffedir.CoffeWorkDir(tmp)
    assert os.path.normpath(tmp) == os.path.normpath(cwd.work_dir)
    assert os.path.normpath(os.path.join(tmp, ".coffe")) == os.path.normpath(cwd.coffe_dir)


def test_workdir_logger(tmpdir):
    cwd = coffedir.CoffeWorkDir(str(tmpdir))
    cwd.logger.info("Hi, I am here")
    log = os.path.join(str(tmpdir), ".coffe/log.txt")
    assert os.path.isfile(log)
    with open(log, "r") as f:
        a = f.readlines()
        assert any("Hi, I am here" in l for l in a)


class Cls(coffedir.CoffeWorkDir):
    def __init__(self, work_dir):
        super(Cls, self).__init__(work_dir)

    @coffedir.log_exceptions
    def a(self):
        raise CustomException("Heyy")


def test_workdir_subclass_logexception(tmpdir):
    inst = Cls(str(tmpdir))
    with pytest.raises(CustomException):
        inst.a()

    with open(inst.logfile, "r") as f:
        lines = f.readlines()
        assert any("Heyy" in l for l in lines)


def test_workdir_log_exception(tmpdir):
    with pytest.raises(CustomException):
        with coffedir.CoffeWorkDir(str(tmpdir)) as cwd:
            raise CustomException("Testexception")
    with open(cwd.logfile, "r") as f:
        a = f.readlines()
        assert any("Testexception" in l for l in a)


def test_logging():
    pass


def test_save(tmpdir):
    with coffedir.CoffeWorkDir(str(tmpdir)) as cwd:
        cwd.save()
        assert os.path.isfile(cwd.dumpfilename)


def test_load(tmpdir):
    with coffedir.CoffeWorkDir(os.path.join(str(tmpdir), "a")) as cwd:
        cwd.save()
    newinst = coffedir.CoffeWorkDir.load(cwd.dumpfilename)
    assert cwd.__dict__ == newinst.__dict__


def test_load_from_dirname(tmpdir):
    with coffedir.CoffeWorkDir(os.path.join(str(tmpdir), "a")) as cwd:
        cwd.save()
    newinst = coffedir.CoffeWorkDir.load(os.path.join(str(tmpdir), "a"))
    assert cwd.__dict__ == newinst.__dict__


def test_move_and_load(tmpdir):
    with coffedir.CoffeWorkDir(os.path.join(str(tmpdir), "a")) as cwd:
        cwd.save()
    newfile = os.path.join(str(tmpdir), "some_object")
    shutil.copyfile(cwd.dumpfilename, newfile)
    newinst = coffedir.CoffeWorkDir.load(newfile)
    assert cwd.__dict__ != newinst.__dict__


def test_move_and_load(tmpdir):
    with coffedir.CoffeWorkDir(os.path.join(str(tmpdir), "a")) as cwd:
        cwd.save()
    newfile = os.path.join(str(tmpdir), "some_object")
    shutil.copyfile(cwd.dumpfilename, newfile)
    newinst = coffedir.CoffeWorkDir.load(newfile)
    assert newinst.work_dir == os.path.dirname(os.path.dirname(newfile))


def test_load_moved_memberpath(tmpdir):
    dir_a = os.path.join(str(tmpdir), "a")
    with coffedir.CoffeWorkDir(dir_a) as cwd:
        cwd.a = str(tmpdir)
        cwd.save()
    os.mkdir(os.path.join(str(tmpdir), ".coffe"))
    newfile = os.path.join(str(tmpdir), ".coffe", "some_object")
    shutil.copyfile(cwd.dumpfilename, newfile)
    newinst = coffedir.CoffeWorkDir.load(newfile)
    assert cwd.a != newinst.a
    assert newinst.a == os.path.dirname(str(tmpdir))
