# -*- coding: utf-8 -*-

"""Global configuration for coffe.

If you want to customize coffe's behavior, you can overwrite
the default configuration in local files named .coffe.conf .

These .coffe.conf files
reside either in your home directory or in any parent directory
of the current working directory. Each option has to be defined
inside the [coffe] section. You must not define other sections
and options than those specified in the default file
:data:`~DEFAULTS_FILE`.

The priority goes from special to general:

 - Options in a directory's .coffe.conf overwrite options in any
   parent directory's .coffe.conf
 - Options in any parent directory's .coffe.conf overwrite options
   in your home directory's .coffe.conf
 - Options in your home directory's .coffe.conf overwrite the
   defaults from the :data:`~DEFAULTS_FILE`.

To view all settings that coffe uses in a specific directory, type::

    coffe config --defaults

to the command line.

Note to developers:

To make new options available to coffe, just add them to the defaults file
(coffe/core/data/coffe.defaults). Nothing more to do.

In the code, global options are accessed as follows::

    from coffe.core.globconf import CONFIG
    CONFIG.whatever_option

To check the options provided by the user, or convert options
into other formats (integer, list, ...), take a look at
:meth:`~Config.check_and_convert`.

Note:
    Please use the globconf module only for settings that are
    truly global. Local settings should be passed as function
    arguments.

"""

from __future__ import absolute_import, division, print_function

import os

from six.moves import configparser
from collections import OrderedDict
import pandas

from coffe.core import pkgdata

DEFAULTS_FILE = pkgdata.abspath(
    "data/coffe.defaults")  #: location of the defaults file
LOCAL_CONFIG_NAME = ".coffe.conf"  #: name of a local configuration file
USER_FILE = os.path.join(
    os.path.expanduser("~"),
    LOCAL_CONFIG_NAME
)  #: name of the user's configuration file


class ConfigFileError(Exception):
    """Error class for invalid formatting of a config file.
    """
    def __init__(self, filename):
        self.filename = filename

    def __str__(self):
        return ("Coffe configuration files "
                "may only have one section [coffe]. "
                "The configuration read from "
                "{} was invalid. To see a list of all "
                "options available to coffe, take a look at "
                "{}.".format(self.filename, DEFAULTS_FILE))


class ConfigOptionError(Exception):
    """Error class for invalid options in a config file.
    """
    def __init__(self, filename, option):
        self.filename = filename
        self.option = option

    def __str__(self):
        return ("The option {} is not a valid coffe option, "
                "but it was found in the configuration file {}."
                "Please remove the option from the configuration "
                "file (or resolve typos). To see a list of all "
                "options available to coffe, take a look at "
                "{}.".format(self.option, self.filename,
                             DEFAULTS_FILE))


class ConfigOptionValueError(Exception):
    """Error class for invalid option format in a config file.
    """
    def __init__(self, filename, option, other_exception):
        self.filename = filename
        self.option = option
        self.other = other_exception

    def __str__(self):
        return ("The option {} could not be interpreted correctly."
                "It was found in the configuration file {}."
                "The error message from Config.check_and_convert "
                "was :\n{}".format(self.option, self.filename, self.other)
                )


class Config(object):
    """
    Configuration class.
    The options are stored internally as a :class:`collections.OrderedDict`,
    but made accessible as attributes of this class.

    Upon construction, a config option holds the defaults that are specified
    in the :data:`~DEFAULTS_FILE`
    """

    def __init__(self):
        self._options = OrderedDict()
        self._sources = OrderedDict()
        self.update_from_file(DEFAULTS_FILE)

    def __getattr__(self, item):
        if item in self._options:
            return self._options[str(item)]
        else:
            raise AttributeError(
                "{} is not a valid coffe option. "
                "Valid options are listed in {}".format(
                    item, DEFAULTS_FILE))

    # Iterable
    def __iter__(self):
        return self._options.__iter__()

    def __next__(self):
        return self._options.__next__()

    next = __next__  # python2.x compatibility.


    def update_from_file(self, config_file):
        """
        Update a dictionary with values from a configuration file.
        Values from the file overwrite presently stored values.

        Args:
            config_file (str): Path of a configuration file.

        Raises:
            ConfigFileError: If the :attr:`~config_file` has invalid format.
            ConfigOptionError: If some option set in :attr:`~config_file` is
                not a valid coffe option.
            ConfigOptionValueError: If some value set in :attr:`~config_file`
                does not pass :meth:`~check_and_convert`.
        """
        if not os.path.isfile(config_file):
            return
        file_cfg = configparser.ConfigParser(dict_type=OrderedDict)
        file_cfg.read(config_file)
        try:
            assert len(file_cfg._sections) == 1
            coffe_dict = file_cfg._sections["coffe"]
        except:
            raise ConfigFileError(config_file)
        if os.path.abspath(config_file) != os.path.abspath(DEFAULTS_FILE):
            for key in coffe_dict:
                if key not in self._options:
                    raise ConfigOptionError(config_file, key)
                try:
                    coffe_dict[key] = self.check_and_convert(key,
                                                             coffe_dict[key]
                                                             )
                except Exception as e:
                    raise ConfigOptionValueError(config_file, key, e)
        src_dict = {key: config_file for key in coffe_dict}
        self._options.update(coffe_dict)
        self._sources.update(src_dict)

    @staticmethod
    def check_and_convert(option, value):
        """
        This function provides checking and converting values read from
        config files.

        Example code::

            if option == "number_of_apples":
                value = int(value)
                assert value >= 0
                return value  # use as an integer in other modules
            if option == "etc.":
                pass

        Args:
            option(str): The option that should be checked.
            value(str): The value that was read for the option.

        Returns:
            The converted value.

        Raises:
            ConfigOptionError: If some option set in :attr:`~config_file`
                in invalid.
        """
        # ! add your checks and conversions here

        # ! default behavior:
        return value

    def get_sources(self, omit_defaults=True):
        """
        Get a list of source files for all settings.

        Args:
            omit_defaults (bool): Do not list default values.

        Returns:
            An instance of :class:`pandas.DataFrame` with the options as
            indices and columns
                :code:`["Value", "Source"]`

        """
        df_src = pandas.DataFrame.from_dict(self._sources, orient='index')
        df_src.columns = ["Source"]
        df = pandas.DataFrame.from_dict(self._options, orient='index')
        df.columns = ["Value"]
        df["Source"] = df_src["Source"]
        if omit_defaults:
            return df[df["Source"] != DEFAULTS_FILE]
        else:
            return df


def load_config(path=os.getcwd()):
    """
    Load a configuration from a given path.
    All config files files in parent directories of :attr:`~path` are read.
    See module-level documentation for more information.

    Args:
        path (str): A directory. By default, the current working directory.

    Returns:
        An instance of :class:`~Config`

    """
    config = Config()

    # ==== update defaults with $HOME/.coffe.config ====
    config.update_from_file(USER_FILE)

    # ==== walk from / to current working directory and ====
    # ==== update options with .coffe.config            ====
    parent_dirs = os.path.abspath(path).split(os.sep)
    directory = os.path.abspath("/")
    for d in parent_dirs:
        directory = os.path.join(directory, d)
        config.update_from_file(os.path.join(directory, LOCAL_CONFIG_NAME))
    return config


CONFIG = load_config()  #: The global configuration object that is used from other coffe modules.
