# -*- coding: utf-8 -*-

"""Test for checking existence, versions, ... of third party software"""

from __future__ import absolute_import, division, print_function

from coffe.core import thirdparty
from coffe.core.thirdparty import *
import pytest


def test_program_exists():
    assert thirdparty.program_exists("cp")


def test_program_not_exists():
    assert not thirdparty.program_exists("lkasjdofkja")


@pytest.fixture(
    params=(GROMACS, AMBER, TORQUE, SLURM, PYMOL, BABEL)
)
def each_program(request):
    return request.param


def test_existing_programs(each_program):
    if each_program.exists:
        assert each_program.version != ""
        each_program.require()


def test_not_existing_programs(each_program):
    if not each_program.exists:
        with pytest.raises(RequirementMissingError):
            each_program.require()


def test_version_requirement_ok():
    py_bin = Requirement("python", "python",
                         version_parser=lambda x: x.strip().split()[1])
    py_bin.require(version="0.0.5")


def test_version_requirement_not_ok():
    py_bin = Requirement("python", "python",
                         version_parser=lambda x: x.strip().split()[1])
    with pytest.raises(RequirementMissingError):
        py_bin.require(version="10000000000000.0.5")


def test_deco_version_requirement_ok():
    some_valid_program = Requirement(
        "python", "python", version_flag="--invalid_version_flag")
    assert some_valid_program.version == some_valid_program.VERSION_NOT_PARSED

    @some_valid_program
    def test():
        pass

    test()


def test_deco_version_requirement_not_ok():
    some_invalid_program = Requirement(
        "Fischifischifisch", "fischifischifisch")

    @some_invalid_program
    def test():
        pass

    with pytest.raises(RequirementMissingError):
        test()


def test_print_function():
    thirdparty.print_version_list()


def test_pymol_program_opt():
    assert PYMOL.options == "-c"
