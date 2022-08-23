# -*- coding: utf-8 -*-

"""Test functions for high-level simulation plan generator."""

from __future__ import absolute_import, division, print_function

from coffe.core import pkgdata, thirdparty
from coffe.amb import simgen, sim, util
# from ..coffe_fixtures import absrel_tmpdir
import pytest
import os

# skip all if amber is not installed
pytestmark = pytest.mark.skipif(not thirdparty.AMBER.exists,
                                reason="The tests in this module require a "
                                       "functioning amber installation")


def test_empty_construction():
    simgen.AmbChainGenerator()


# TODO(AK) use absrel_tmpdir fixture
@pytest.fixture
def make_emin_chain(tmpdir):
    def makegen(mdin):
        return simgen.AmbChainGenerator(names=["emin1", "emin2", "emin3"],
                                        mdin_files=[mdin, mdin, mdin],
                                        mdin_options=[{}, {}, {}],
                                        types=[sim.AmbCalculation,
                                               sim.AmbCalculation,
                                               sim.AmbCalculation]), str(tmpdir)
    return makegen


# TODO(AK) use absrel_tmpdir fixture
def test_default_types_construction(tmpdir):
    mdin = pkgdata.abspath("data/test_mdin")
    gen = simgen.AmbChainGenerator(names=["emin1", "emin2", "emin3"],
                                   mdin_files=[mdin, mdin, mdin],
                                   mdin_options=[{}, {}, {}])
    for t in gen.types:
        assert t == sim.AmbCalculation


def test_mdin_construction(make_emin_chain):
    mdin = pkgdata.abspath("data/test_mdin")
    make_emin_chain(mdin)


def test_failure_construction(make_emin_chain):
    with pytest.raises(AssertionError):
        make_emin_chain("sdflksdj")


@pytest.fixture
def generated_emin_cc(make_emin_chain):
    mdin = pkgdata.abspath("data/test_mdin")
    s = pkgdata.abspath("data/test_inpcrd")
    top = pkgdata.abspath("data/test_prmtop")
    gen, tmp = make_emin_chain(mdin)
    return gen.generate(work_dir=tmp, structure=s, topology=top), tmp


def test_mdin_generate(generated_emin_cc):
    cc, tmp = generated_emin_cc
    assert len(cc) == 3


def test_mdin_generate_structure_not_exists(generated_emin_cc):
    cc, tmp = generated_emin_cc
    for i in range(len(cc)):
        if i == 0:
            continue
        assert not os.path.isfile(cc[i].structure)


def test_mdin_commandchain(generated_emin_cc):
    cc, tmp = generated_emin_cc
    cc()


def test_start_from_restart(tmpdir):
    """Check if intermediate simulations use restart settings"""
    tmp = str(tmpdir)
    mdin = pkgdata.abspath("data/test_mdin")
    gen = simgen.AmbChainGenerator(names=["sim1", "sim2", "sim3"],
                                   mdin_files=[mdin, mdin, mdin],
                                   mdin_options=[{}] * 3,
                                   types=[sim.AmbCalculation, 
                                          sim.AmbCalculation,
                                          sim.AmbCalculation])
    s = pkgdata.abspath("data/test_inpcrd")
    top = pkgdata.abspath("data/test_prmtop")
    cc = gen.generate(work_dir=tmp, structure=s, topology=top)
    assert util.read_mdin_option(cc[0].mdin_file, "cntrl.irest") is 0
    assert util.read_mdin_option(cc[1].mdin_file, "cntrl.irest") is 1
    assert util.read_mdin_option(cc[1].mdin_file, "cntrl.ntx") is 5
    assert util.read_mdin_option(cc[2].mdin_file, "cntrl.irest") is 1
    assert util.read_mdin_option(cc[1].mdin_file, "cntrl.ntx") is 5
    cc()

# TODO(AK) test for relative paths  ---> this applies for pretty much everything
# else as well :-/
# TODO(AK) Write a tmppath fixture that tests relative and absolute paths
