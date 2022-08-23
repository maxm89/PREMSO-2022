# -*- coding: utf-8 -*-

"""Test functions for high-level simulation plan generator."""

from __future__ import absolute_import, division, print_function

from coffe.core import pkgdata, thirdparty
from coffe.gmx import simgen, sim, util
# from ..coffe_fixtures import absrel_tmpdir
import pytest
import os

# skip all if gromacs is not installed
pytestmark = pytest.mark.skipif(not thirdparty.GROMACS.exists,
                                reason="The tests in this module require a functioning gromacs installation")


def test_empty_construction():
    simgen.GmxChainGenerator()


# TODO(AK) use absrel_tmpdir fixture
@pytest.fixture
def make_emin_chain(tmpdir):
    def makegen(mdp):
        return simgen.GmxChainGenerator(names=["emin1", "emin2", "emin3"],
                                        mdp_files=[mdp, mdp, mdp],
                                        mdp_options=[{}, {}, {}],
                                        types=[sim.GmxCalculation, sim.GmxCalculation, sim.GmxCalculation]
                                        ), str(tmpdir)
    return makegen


# TODO(AK) use absrel_tmpdir fixture
def test_default_types_construction(tmpdir):
    mdp = pkgdata.abspath("data/test_mdp.mdp")
    gen = simgen.GmxChainGenerator(names=["emin1", "emin2", "emin3"],
                                 mdp_files=[mdp, mdp, mdp],
                                 mdp_options=[{}, {}, {}])
    for t in gen.types:
        assert t == sim.GmxCalculation


def test_mdp_construction(make_emin_chain):
    mdp = pkgdata.abspath("data/test_mdp.mdp")
    make_emin_chain(mdp)


def test_failure_construction(make_emin_chain):
    with pytest.raises(AssertionError):
        make_emin_chain("sdflksdj")


@pytest.fixture
def generated_emin_cc(make_emin_chain):
    mdp = pkgdata.abspath("data/test_mdp.mdp")
    s = pkgdata.abspath("data/test_structure.pdb")
    top = pkgdata.abspath("data/test_topology.top")
    gen, tmp = make_emin_chain(mdp)
    return gen.generate(work_dir=tmp, structure=s, topology=top), tmp


def test_mdp_generate(generated_emin_cc):
    cc, tmp = generated_emin_cc
    assert len(cc) == 3


def test_mdp_generate_structure_not_exists(generated_emin_cc):
    cc, tmp = generated_emin_cc
    for i in range(len(cc)):
        if i == 0:
            continue
        assert not os.path.isfile(cc[i].structure)


def test_mdp_commandchain(generated_emin_cc):
    cc, tmp = generated_emin_cc
    cc()


def test_start_from_checkpoint(tmpdir):
    """Check if intermediate simulations start from checkpoints"""
    # make sd chain
    tmp = str(tmpdir)
    mdp = pkgdata.abspath("data/test_mdp.mdp")
    gen = simgen.GmxChainGenerator(names=["sd1", "sd2", "sd3"],
                                   mdp_files=[mdp, mdp, mdp],
                                   mdp_options=[{"integrator": "sd", "nsteps": 10}] * 3,
                                   types=[sim.GmxCalculation, sim.GmxCalculation, sim.GmxCalculation]
                                   )
    s = pkgdata.abspath("data/test_structure.pdb")
    top = pkgdata.abspath("data/test_topology.top")
    cc = gen.generate(work_dir=tmp, structure=s, topology=top)
    assert cc[1].checkpoint is not None
    cc()
    assert os.path.isfile(cc[1].checkpoint)


def test_no_start_from_checkpoint(generated_emin_cc):
    """check that checkpoints are not used for minimization"""
    cc, tmp = generated_emin_cc
    assert cc[1].checkpoint is None



# TODO(AK) test for relative paths  ---> this applies for pretty much everything else as well :-/
# TODO(AK) Write a tmppath fixture that tests relative and absolute paths
