# -*- coding: utf-8 -*-

"""Tests for `coffe` package."""

from __future__ import absolute_import, division, print_function
import pytest
import subprocess
from click.testing import CliRunner
from coffe import cli
from coffe.core import graffiti


def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()
    result = runner.invoke(cli.main)
    assert result.exit_code == 0
    assert 'Console script for coffe' in result.output


def test_help_message():
    runner = CliRunner()
    help_result = runner.invoke(cli.main, ['--help'])
    assert help_result.exit_code == 0
    assert 'Show this message and exit.' in help_result.output


def test_command_line_without_runner():
    """test coffe command"""
    p = subprocess.Popen(["coffe", "--help"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    assert p.returncode == 0
    assert 'Console script for coffe' in stdout.decode("latin-1")


def test_logging_argument(tmpdir):
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli.main, ['-c', 3, '-v', 10, "log", "Damn!", "-s", "[GREEN,BOLD,UNDERLINE]"])
        assert result.exit_code == 0
        # too lazy to write the check


