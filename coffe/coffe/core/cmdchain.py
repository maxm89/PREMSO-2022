# -*- coding: utf-8 -*-

"""A class for storing consecutive commands"""

from __future__ import absolute_import, division, print_function

import coffe.core.coffedir
from coffe.core import filesys, compat
import copy
import os


def has_empty_call(x):
    return callable(x) and hasattr(x, "__call__") and compat.get_function_args(x.__call__) == ["self"]


class CommandChain(coffe.core.coffedir.CoffeWorkDir):
    """A chain of consecutive commands, e.g. a simulation plan
    """

    @coffe.core.coffedir.log_exceptions
    def __init__(self, commands=[], work_dir="."):
        super(CommandChain, self).__init__(work_dir, "CommandChain", locals())
        assert isinstance(commands, list)
        for x in commands:
            assert has_empty_call(x), "Cannot create CommandChain. No function __call__() in {}".format(x)
        self.commands = copy.deepcopy(commands)

    @coffe.core.coffedir.log_exceptions
    def __call__(self):
        for cmd in self.commands:
            if hasattr(cmd, "work_dir"):
                self.logger.info("NEXT CALL: Running command in directory {}".
                                 format(os.path.relpath(cmd.work_dir, self.work_dir)))
            cmd.__call__()

    def __len__(self):
        return len(self.commands)

    def __getitem__(self, key):
        return self.commands[key]

    @coffe.core.coffedir.log_exceptions
    def __iadd__(self, other):
        assert isinstance(other, list)
        for x in other:
            assert has_empty_call(x), "Cannot add to CommandChain. No function __call__() in {}".format(x)
        self.commands.__iadd__(other)
        return self


    # Iterable
    def __iter__(self):
        return self.commands.__iter__()

    def __next__(self):
        return self.commands.__next__()

    next = __next__  # python2.x compatibility.

