# -*- coding: utf-8 -*-

"""Tests for coffe.misc.misccli functions

This module provides tests for the module coffe.misc.misccli

"""

from __future__ import absolute_import, division, print_function
from click.testing import CliRunner
from coffe import cli


def test_create_torsion_conformations_help():
    runner = CliRunner()
    help_result = runner.invoke(cli.main, ['misc',
                                           'create-torsion-conformations',
                                           '--help'])
    assert help_result.exit_code == 0
    assert 'Show this message and exit.' in help_result.output
