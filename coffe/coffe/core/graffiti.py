# -*- coding: utf-8 -*-

"""Colored printing on the console.
This module supports colored printing using the `plumbum`_ package.
It provides a conditional formatter :class:`logging.ColorFormatter`
that can be used by instances of :class:`logging.Logger` to
write formatted text to the console, while writing plain text to the logfile.

Supported styles (may be updated):
    - Colors
        - RED, GREEN, BLUE, YELLOW, CYAN, MAGENTA,
        - ORCHID, LIGHTGRAY, DARKGRAY, DARKGOLDENROD
    - BOLD
    - UNDERLINE
You can also use arbitrary styles of type :class:`plumbum.colorlib.styles.ANSIStyle`, see `plumbum`_ documentation.

Examples:
    Example 1 (preferred use inside coffe functions)::

        with CoffeWorkDir('.') as cwd:
            cwd.print("Welcome", 1, graffiti.CYAN, graffiti.UNDERLINE, indent=2)
            # implicit use in cwd.logger
            cwd.logger.info("Welcome", graffiti.CYAN)
                # does not support indent
                # supports only single-message string

    Example 2 (mainly for command line interface)::

        graffiti.echo("Welcome", 1, graffiti.CYAN, graffiti.UNDERLINE, indent=2)

.. _plumbum:
   http://plumbum.readthedocs.io
"""

from __future__ import absolute_import, division, print_function

import plumbum
from plumbum import colors
from plumbum.colorlib.styles import ANSIStyle
import logging
import copy
from coffe.core import compat

# SUPPORTED STYLES

WARN = colors.warn

RED = colors.red
GREEN = colors.green
DARKORANGE = colors.DarkOrange3A
BLUE = colors.blue
YELLOW = colors.yellow
CYAN = colors.cyan
MAGENTA = colors.magenta
ORCHID = colors.orchid
LIGHTGRAY = colors.LightGray
DARKGRAY = colors.DarkGray
DARKGOLDENROD = colors.DarkGoldenrod            # see http://plumbum.readthedocs.io/en/latest/colors.html#color-support
                                                # for more colors
CUSTOM_COLOR = colors.rgb(18, 146, 64)          # TODO(KNK): Rename and change to whatever you like
CUSTOM_COLOR2 = colors.from_ansi("\033[92m")    # TODO(KNK): Rename and change to whatever you like

BOLD = colors.bold
UNDERLINE = colors.underline


def default_style(level):
    """Default styles for logging."""
    if level == logging.CRITICAL:
        return [RED, BOLD, UNDERLINE]
    elif level == logging.ERROR:
        return [RED, BOLD]
    elif level == logging.WARNING:
        return [DARKORANGE, BOLD]
    elif level == logging.INFO:
        return []
    elif level == logging.DEBUG:
        return [LIGHTGRAY]
    else:
        return []


def apply_indent(msg, indent=0):
    """Indent text message.

    Args:
        msg (str): Message.
        indent (int): Number of spaces.

    Returns:
        str: Indented text
    """
    assert indent >= 0
    return compat.indent(msg, " " * indent)


def set_global_use_color(use_color):
    """Set global color level.

    Args:
        use_color (int): (0: no color,  1: 8 colors,  2: 16 colors,  3: 256 colors,   4: 24-bit colors)

    """
    ANSIStyle.use_color = use_color


def get_global_use_color():
    """Get global color level.

    Returns:
         int: (0: no color,  1: 8 colors,  2: 16 colors,  3: 256 colors,   4: 24-bit colors)

    """
    return ANSIStyle.use_color


def spray(msg, *styleargs, **kwargs):
    """Format message with styles.

    Args:
        msg (str): The message.
        *styleargs: Any styles in graffiti, such as :code:`graffiti.GREEN`, :code:`graffiti.BOLD`, ...
        use_color (bool): If true, use the global color level, otherwise use no color.

    Returns:
        str: Formatted message.
    """
    use_color = kwargs.get("use_color", True)
    if styleargs:
        if use_color:
            with UseColor(get_global_use_color()):
                for a in styleargs:
                    msg = (msg | a)
        else:
            with UseColor(False):
                for a in styleargs:
                    msg = (msg | a)
    return msg


class UseColor(object):
    """An environment in which a color level other than the global color level can be used.
    """
    def __init__(self, level=3):
        """
        Args:
            level(int): See :func:`~set_global_use_color` for a description of levels (default: 3)
        """
        self._level = level
        self._color_outside = get_global_use_color()

    def __enter__(self):
        """Enter context manager (:code:`with` statement)"""
        set_global_use_color(self._level)
        return self

    def __exit__(self, *args, **kwargs):
        """Exit context manager"""
        set_global_use_color(self._color_outside)


def echo(*args, **kwargs):
    """Acts like a print function in that it writes arbitrary arguments to the console.
    Only prints output if the global log level is :obj:`logging.INFO` or :obj:`logging.DEBUG`.
    Supports styles from graffiti as arguments. Those styles are applied to all printed information.
    This function is mainly used by the command-line interface. Other functions in coffe
    should usually use :class:`~coffe.core.coffedir.CoffeWorkDir` environments and its
    :meth:`~coffe.core.coffedir.CoffeWorkDir.print` function.
    See module-level documentation of :mod:`~coffe.core.graffiti` for example of usage.

    Args:
        *args:  Any arguments that can be converted to strings & ANSIStyles, such as :obj:`grafitti.RED`.
                Multiple ANSIStyles can be combined
                e.g. :code:`graffiti.echo("Number", 12, graffiti.RED, graffiti.BOLD, graffiti.UNDERLINE)`.
        indent(int): A parameter to indent the printed message by the given number of spaces (default: 0).
        sep (str): The separator for the printed statements (default: ' ').
    """
    indent = kwargs.get("indent", 0)
    sep = kwargs.get("sep", ' ')
    styleargs = (a for a in args if isinstance(a, ANSIStyle))
    otherargs = (str(a) for a in args if not isinstance(a, ANSIStyle))
    msg = apply_indent(sep.join(otherargs), indent)
    if logging.getLogger().getEffectiveLevel() <= logging.INFO:
        print(spray(msg, *styleargs, use_color=True))


class ColorFormatter(logging.Formatter):
    """A formatter class to write colored output to the command line through a logging.Logger instance.
    This formatter is used by the logger in :class:`~coffe.core.coffedir.CoffeWorkDir`.
    """
    def __init__(self, *args, **kwargs):
        """
        Args:
            *args: Any positional arguments for :class:`logging.Formatter`.
            use_color (bool): If True [default], use color, otherwise print black (the latter is used for logfiles).
            **kwargs: Any keyword arguments for :class:`logging.Formatter`.
        """
        use_color = kwargs.get("use_color", True)
        try:
            del kwargs["use_color"]
        except KeyError:
            pass
        self._use_color = use_color
        super(ColorFormatter, self).__init__(*args, **kwargs)

    def format(self, record):
        """Overrides :meth:`logging.Formatter.format`.
        Applies :func:`~spray` to the message before invoking :meth:`logging.Formatter.format`.
        If no styleargs are given, a default style is applied, see source of :func:`~default_style`.
        """
        r = copy.copy(record)
        styleargs = [a for a in r.args if isinstance(a, ANSIStyle)]
        if not styleargs:
            styleargs = default_style(r.levelno)
        otherargs = [a for a in r.args if not isinstance(a, ANSIStyle)]
        r.msg = spray(str(r.msg), *styleargs, use_color=self._use_color)
        r.args = otherargs
        return super(ColorFormatter, self).format(r)


