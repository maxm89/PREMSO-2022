# -*- coding: utf-8 -*-

"""Wrapper functions for compatibility with different python versions."""

from __future__ import absolute_import, division, print_function
import six
import inspect
import textwrap


def get_function_args(func):
    """Returns arguments of a function.
    Note: at some point, six will probably have a function getfullargspec to replace this function."""
    # (getargspec is deprecated in python 3, use signature (or getfullargspec) instead)
    # unfortunately, the six module does not provide a 2/3 compatible version, yet.
    wrapped = func
    while hasattr(wrapped, "__wrapped__"):
        wrapped = wrapped.__wrapped__

    if six.PY2:
        return inspect.getargspec(wrapped)[0]
    else:  # six.PY3
        return inspect.getfullargspec(wrapped)[0]


def indent(msg, prefix):
    """Indent text message.

    Args:
        msg (str): Message.
        indent (int): Number of spaces.

    Returns:
        str: Indented text
    """
    if six.PY2:
        return " ".join(textwrap.TextWrapper(initial_indent=prefix, subsequent_indent=prefix, width=100).wrap(msg))
    else:
        return textwrap.indent(msg, prefix)



