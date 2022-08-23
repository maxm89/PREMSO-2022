# -*- coding: utf-8 -*-

"""Tests for coffe.core.filesys functions"""

from __future__ import absolute_import, division, print_function
import os

import coffe.core.coffedir
from coffe.core import filesys, pkgdata, shell
import pytest


def test_grep_line():
    l = filesys.grep_line(pkgdata.abspath("data/config.cfg"), "test2")
    assert l.strip() == "[test2]"


def test_make_abspath():
    p = "data/foo.txt"
    abs = filesys.make_abspath(p, pkgdata.abspath("."))
    assert os.path.isfile(abs)
    p2 = "data/foo2.txt"
    filesys.make_abspath(p, pkgdata.abspath("."), check_exists=False)


def test_batch_filename(tmpdir):
    name = filesys.batch_filename(str(tmpdir),"hallo")
    shell.touch(name)


def test_basename(tmpdir):
    name = filesys.basename(str(tmpdir + "/test"))
    assert name == "test"
