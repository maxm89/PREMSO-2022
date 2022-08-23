# -*- coding: utf-8 -*-

"""Saving and loading classes"""

from __future__ import absolute_import, division, print_function
from coffe.core import filesys
import pickle
import logging
import os


def save(instance, filename):
    assert os.path.isdir(os.path.dirname(filename))
    with open(filename,"wb") as f:
        pickle.dump(instance, f)
    return filename


def load(filename):
    assert os.path.isfile(filename), "File of simulation instance does not exist: {}".format(filename)
    with open(filename,"rb") as f:
        obj = pickle.load(f)
    return obj


def load_and_run(filename):
    obj = load(filename)
    obj()
    return obj


