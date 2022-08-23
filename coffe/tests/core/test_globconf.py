# -*- coding: utf-8 -*-

"""Testing global configuration for coffe."""

from __future__ import absolute_import, division, print_function

import os

import pytest

from coffe.core import globconf, shell


def test_defaults():
    cfg = globconf.load_config()
    assert cfg.gmx == "gmx"


def prepare_option(dirname, line):
    loc = os.path.join(dirname, globconf.LOCAL_CONFIG_NAME)
    with open(loc, "w") as f:
        f.writelines(["[coffe]" + os.linesep,
                      line + os.linesep])


def test_local_config_file(tmpdir):
    prepare_option(str(tmpdir), "gmx = /my/gmx")
    cfg = globconf.load_config(str(tmpdir))
    assert cfg.gmx == "/my/gmx"


def test_priority(tmpdir):
    subdir = os.path.join(str(tmpdir), "subdir")
    os.mkdir(subdir)
    prepare_option(str(tmpdir), "gmx = /my/gmx")
    prepare_option(subdir, "gmx = /my/other/gmx")
    cfg = globconf.load_config(subdir)
    assert cfg.gmx == "/my/other/gmx"


def test_failure_empty_config_file(tmpdir):
    shell.touch(os.path.join(str(tmpdir), globconf.LOCAL_CONFIG_NAME))
    with pytest.raises(globconf.ConfigFileError):
        globconf.load_config(str(tmpdir))


def test_failure_invalid_option(tmpdir):
    prepare_option(str(tmpdir), "grmx = /my/gmx")
    with pytest.raises(globconf.ConfigOptionError):
        globconf.load_config(str(tmpdir))


def test_failure_invalid_attribute(tmpdir):
    with pytest.raises(AttributeError):
        cfg = globconf.load_config()
        cfg.someinvalidattribute


def test_print_globconf(tmpdir):
    prepare_option(str(tmpdir), "gmx = /my/gmx")
    cfg = globconf.load_config(str(tmpdir))
    df = cfg.get_sources()
    assert "Value" in df
    assert "Source" in df
    assert df.loc["gmx", "Value"] == "/my/gmx"
    assert df.loc["gmx", "Source"] == os.path.join(
        str(tmpdir), globconf.LOCAL_CONFIG_NAME)
    assert all(src != globconf.DEFAULTS_FILE for src in df["Source"])


def test_print_globconf_with_defaults(tmpdir):
    prepare_option(str(tmpdir), "gmx = /my/gmx")
    cfg = globconf.load_config(str(tmpdir))
    df = cfg.get_sources(omit_defaults=False)
    assert "Value" in df
    assert "Source" in df
    defaults = globconf.Config() # initialized with defaults
    # check that all valid values are written to the data frame
    assert all(x in df["Value"] for x in defaults)


def test_global_instance():
    # we cannot making any assumptions here about the content
    assert isinstance(globconf.CONFIG, globconf.Config)
    globconf.CONFIG.gmx

