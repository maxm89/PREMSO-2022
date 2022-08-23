# -*- coding: utf-8 -*-

"""Decorators for coffe functions."""

from __future__ import absolute_import, division, print_function
from coffe.core import compat
from six.moves import configparser
import os
import functools
import logging


class ConfigError(Exception):
    pass


def _extract_args(*args, **kwargs):
    """Helper function for args_from_configfile to prevent code duplication."""

    # open config file
    cfg_file = kwargs["cfg_file"]
    assert "section" in kwargs, \
        "Keyword 'cfg_file'=... cannot be used without keyword 'section'=.... " \
        "cfg_file was {}".format(cfg_file)
    section = kwargs["section"]
    assert os.path.isfile(cfg_file), "Config file {} does not exist".format(cfg_file)
    cfg = configparser.ConfigParser()
    cfg.read(cfg_file)
    assert cfg.has_section(section), "Config file {} has no section {}".format(cfg_file, section)

    options_dict = {}
    # read config options
    XXX = "XXX"
    for opt in cfg.options(section):
        try:
            options_dict[opt] = eval(cfg.get(section, opt))
        except SyntaxError:
            raise ConfigError("Config file options must obey Python syntax. "
                              "Config file: {} "
                              "Section: {} "
                              "Option: {} ",
                              "Value {} could not be interpreted.".format(
                                  cfg_file, section, opt, cfg.get(section,opt)
                              ))
    # read keyword arguments
    for arg in kwargs:
        if (arg not in ["cfg_file", "section"]) and (kwargs[arg] is not None):
            options_dict[arg] = kwargs[arg]
    # assert that all XXX were overwritten by keyword arguments
    for x in options_dict:
        if options_dict[x] == XXX:
            raise ConfigError("{} was not passed as a keyword argument, "
                              "although {} = XXX in the config file.".
                              format(x, x))
    return options_dict



def args_from_configfile(func):
    """A decorator that enables retrieving function arguments from config files.
    Instead of passing all arguments, you can also pass a keyword 'cfg_file'
    and a keyword 'section'.
    The function is then called with the parameters specified in the section of
    a config file.

    When using this decorator on constructors, the class is created from cfg_file.

    Note:
    - You can combine config file arguments with keyword arguments.
    - Specifying an option as XXX in the config file indicates
        that the option must be given as a keyword argument
    - Keyword arguments override config file arguments (exception: value None does not override).
    - Non-keyword arguments are ignored, if a cfg_file is specified.
    - All arguments specified in the config file's section are passed as function parameters.
    - The arguments are evaluated, i.e. when defining a string use quotation marks in
        the configuration file.
    """
    arguments = compat.get_function_args(func)
    if len(arguments) > 0 and arguments[0] == "self":
        @functools.wraps(func)  # makes sure the decorator does not break the sphinx documentation ( + more)
        def method_wrapper(*args, **kwargs):
            if "cfg_file" in kwargs:
                try:
                    options_dict = _extract_args(*args, **kwargs)
                except Exception as e:
                    raise e
                try:
                    return func(args[0], **options_dict)
                except Exception as e:
                    print (os.linesep + "Function could not be called from cfg_file."
                                        "Arguments were: {}".format(kwargs))
                    raise e
            else:
                return func(*args, **kwargs)
        wrapper = method_wrapper
    else:
        @functools.wraps(func)  # makes sure the decorator does not break the sphinx documentation
        def function_wrapper(*args, **kwargs):
            if "cfg_file" in kwargs:
                try:
                    options_dict = _extract_args(*args, **kwargs)
                except Exception as e:
                    print (os.linesep + "Function could not be called from cfg_file."
                                        "Arguments were: {}".format(kwargs))
                    raise e
                try:
                    return func(**options_dict)
                except Exception as e:
                    raise e
            else:
                return func(*args, **kwargs)
        wrapper = function_wrapper
    wrapper.__wrapped__ = func   # required for python 2
    return wrapper


