# -*- coding: utf-8 -*-

"""Fixture for a temporary box environment."""

from __future__ import absolute_import, division, print_function
import pytest
from coffe.core import pkgdata
from six.moves import configparser
import shutil
import os


def all_sections_in_boxes_cfg():
    """Read all sections from config file."""
    cfg_file = pkgdata.abspath("data/boxes/boxes.cfg")
    assert os.path.isfile(cfg_file)
    cfg = configparser.ConfigParser()
    cfg.read(cfg_file)
    sections = cfg.sections()
    assert len(sections) != 0
    return sections


@pytest.fixture(scope="session")
def boxes_environment(tmpdir_factory):
    """A fixture to create a temporary copy of the directory data/boxes"""
    tmp = tmpdir_factory.mktemp("boxes_environment")
    boxdir = os.path.join(str(tmp), "boxes")
    shutil.copytree(pkgdata.abspath("data/boxes"), boxdir)
    return boxdir
