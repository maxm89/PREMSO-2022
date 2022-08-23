# -*- coding: utf-8 -*-

"""Tests for coffe.core.relpath functions"""

from __future__ import absolute_import, division, print_function
import os
from coffe.core import pkgdata


def test_abspath():
    filename = pkgdata.abspath("data/foo.txt")
    assert os.path.isfile(filename)


def test_isdir():
    assert pkgdata.isdir("data")
    assert not pkgdata.isdir("data/foo.txt")


def test_isfile():
    assert not pkgdata.isfile("data")
    assert pkgdata.isfile("data/foo.txt")


def test_exists():
    assert pkgdata.exists("data")
    assert pkgdata.exists("data/foo.txt")
    assert not pkgdata.exists("foo")


def test_listdir():
    ls = pkgdata.listdir("data")
    assert "foo.txt" in ls


def test_string():
    ls = pkgdata.read("data/foo.txt").strip()
    assert ls == "foo"


def test_openfile():
    with pkgdata.openfile("data/foo.txt") as f:
        assert f.read().strip().decode("utf-8") == "foo"
    # decode is used for python 2/3 compatibility
    # python 3 returns a byte string b'foo' here
