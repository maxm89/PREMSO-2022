# -*- coding: utf-8 -*-

"""Tests for coffe.misc.misccli functions

This module provides tests for the module coffe.misc.misccli

"""

from __future__ import absolute_import, division, print_function
from click.testing import CliRunner
from coffe import cli
from coffe.core import pkgdata

import os
import shutil

def test_compute_distance_help():
    runner = CliRunner()
    help_result = runner.invoke(cli.main, ['analysis', 'compute-distance',
                                           '--help'])
    assert help_result.exit_code == 0
    assert 'Show this message and exit.' in help_result.output


def test_compute_distance(tmpdir):
    src = pkgdata.abspath("data/test.pdb")
    dest = os.path.join(str(tmpdir), os.path.basename(src))
    shutil.copyfile(src, dest)
    runner = CliRunner()
    result = runner.invoke(cli.main, ['analysis', 'compute-distance',
                                      dest,
                                      '-a', 'C1-C5',
                                      '-n', 'test-distance'])
    assert result.exit_code == 0
    assert '1.52' in result.output
    assert 'test-distance' in result.output


def test_compute_angle_help():
    runner = CliRunner()
    help_result = runner.invoke(cli.main, ['analysis', 'compute-angle',
                                           '--help'])
    assert help_result.exit_code == 0
    assert 'Show this message and exit.' in help_result.output


def test_compute_angle(tmpdir):
    src = pkgdata.abspath("data/test.pdb")
    dest = os.path.join(str(tmpdir), os.path.basename(src))
    shutil.copyfile(src, dest)
    runner = CliRunner()
    result = runner.invoke(cli.main, ['analysis', 'compute-angle',
                                      dest,
                                      '-a', 'C1-C5-C8',
                                      '-n', 'test-angle'])
    assert result.exit_code == 0
    assert '113' in result.output
    assert 'test-angle' in result.output


def test_compute_dihedral_help():
    runner = CliRunner()
    help_result = runner.invoke(cli.main, ['analysis', 'compute-dihedral',
                                           '--help'])
    assert help_result.exit_code == 0
    assert 'Show this message and exit.' in help_result.output


def test_compute_dihedral(tmpdir):
    src = pkgdata.abspath("data/test.pdb")
    dest = os.path.join(str(tmpdir), os.path.basename(src))
    shutil.copyfile(src, dest)
    runner = CliRunner()
    result = runner.invoke(cli.main, ['analysis', 'compute-dihedral',
                                      dest,
                                      '-a', 'C1-C5-C8-C11',
                                      '-n', 'test-dihedral'])
    assert result.exit_code == 0
    assert '180' in result.output
    assert 'test-dihedral' in result.output


def test_compute_conformation_help():
    runner = CliRunner()
    help_result = runner.invoke(cli.main, ['analysis', 'compute-conformation',
                                           '--help'])
    assert help_result.exit_code == 0
    assert 'Show this message and exit.' in help_result.output
