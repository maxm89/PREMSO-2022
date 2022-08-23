# -*- coding: utf-8 -*-

"""Tests for `coffe gmx` command line interface."""

from __future__ import absolute_import, division, print_function
import pytest
import os
from click.testing import CliRunner
from coffe import cli
from coffe.core import pkgdata, thirdparty
from . import box_fixture
from .box_fixture import boxes_environment


# skip all if gromacs is not installed
pytestmark = pytest.mark.skipif(not thirdparty.GROMACS.exists,
                                reason="The tests in this module require a functioning gromacs installation")


def test_gmx_mkbox_help():
    runner = CliRunner()
    help_result = runner.invoke(cli.main, ['gmx', 'mkbox', '--help'])
    assert help_result.exit_code == 0
    assert 'Show this message and exit.' in help_result.output


def test_gmx_mkbox_invalid_path():
    runner = CliRunner()
    invalid = 'lkjsdlf.cfg'
    result = runner.invoke(cli.main, ['gmx', 'mkbox', invalid, 'section'])
    assert result.exit_code != 0
    assert 'Path "{}" does not exist.'.format(invalid) in result.output


def test_gmx_mkbox_invalid_section():
    runner = CliRunner()
    cfg_file = pkgdata.abspath("data/boxes/boxes.cfg")
    section = "thisisdefinitelynovalidsectionname"
    result = runner.invoke(cli.main, ['gmx', 'mkbox', cfg_file, section])
    assert result.exit_code != 0


# ==========================================================
# ========= Test all boxes in data/boxes/boxes.cfg =========
# ==========================================================


@pytest.mark.parametrize("section", box_fixture.all_sections_in_boxes_cfg())
def test_all_gmx_boxes(boxes_environment, section):
    os.chdir(boxes_environment)
    runner = CliRunner()
    result = runner.invoke(cli.main, ['gmx', 'mkbox', "boxes.cfg", section])
    print (result.output)
    assert result.exit_code == 0


