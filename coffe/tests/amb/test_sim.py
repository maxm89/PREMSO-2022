# -*- coding: utf-8 -*-

"""Tests for coffe.amb.sim"""

from __future__ import absolute_import, division, print_function

from coffe.core import pkgdata, thirdparty
from coffe.amb import sim as ambsim
# from coffe_fixtures import absrel_tmpdir


import os
import shutil
import pytest

# skip all if Amber (sander) is not installed
pytestmark = pytest.mark.skipif(not thirdparty.AMBER.exists,
                                reason="The tests in this module require a "
                                       "functioning Amber installation")


@pytest.fixture
def asim(tmpdir):
    """Simulation fixture. Returns a function that creates a AmbCalculation,
    as well as the work_dir."""
    s = pkgdata.abspath("data/test_inpcrd")
    t = pkgdata.abspath("data/test_prmtop")
    infile = pkgdata.abspath("data/test_mdin")
    wd = os.path.join(str(tmpdir), "test_sim")

    def wrapper(structure=s, topology=t, mdin=infile, work_dir=wd, **kwargs):
        return ambsim.AmbCalculation(structure, topology, mdin, work_dir,
                                     **kwargs)

    return wrapper, wd


@pytest.fixture
def asim_restart(tmpdir):
    """Simulation fixture. Returns a function that creates a AmbCalculation,
    as well as the work_dir."""
    s = pkgdata.abspath("data/test_restrt")
    t = pkgdata.abspath("data/test_prmtop")
    infile = pkgdata.abspath("data/test_mdin")
    wd = os.path.join(str(tmpdir), "test_sim_restart")

    def wrapper(structure=s, topology=t, mdin=infile, work_dir=wd, **kwargs):
        return ambsim.AmbCalculation(structure, topology, mdin, work_dir,
                                     restart=True, **kwargs)

    return wrapper, wd


def test_amb_simulation_init(asim):
    """Test initialization."""
    ambs, wd = asim
    sim = ambs()
    assert os.path.isdir(wd)
    assert os.path.isdir(sim.coffe_dir)


# def test_amb_simulation_init_from_cfg(tmpdir):
#     """Test initialization from config file."""
#     d = str(tmpdir)
#     shutil.copy(pkgdata.abspath("data/test_structure.pdb"), d)
#     shutil.copy(pkgdata.abspath("data/test_topology.top"), d)
#     shutil.copy(pkgdata.abspath("data/test_mdp.mdp"), d)
#     # create temporary config file
#     cfg_file = os.path.join(d,"test.cfg")
#     wd = os.path.join(d, "test_sim")
#     with open(cfg_file,"w") as f:
#         f.writelines(
#             [
#                 "[test_sim]\n",
#                 "structure:     '{}'\n".format(os.path.join(d,"test_structure.pdb")),
#                 "topology:      '{}'\n".format(os.path.join(d, "test_topology.top")),
#                 "mdp_file:      '{}'\n".format(os.path.join(d, "test_mdp.mdp")),
#                 "work_dir:      '{}'\n".format(wd),
#
#             ]
#         )
#     sim = ambsim.AmbCalculation(cfg_file=cfg_file, section="test_sim")
#     assert os.path.isdir(wd)
#     assert os.path.isdir(sim.coffe_dir)
#
#
def test_amb_simulation_failure(asim):
    """Test failure with no valid mdin file."""
    ambs, wd = asim
    with pytest.raises(Exception) as e_info:
        sim = ambs(mdin=pkgdata.abspath("data/foo_mdin"))
        assert "does not exist" in e_info
    with open(os.path.join(wd, ".coffe/log.txt"), 'r') as log:
        assert "does not exist" in log.read()


def test_amb_simulation_run(asim):
    """Test a normal simulation run."""
    ambs, wd = asim
    sim = ambs()
    assert os.path.isdir(wd)
    sim()
    assert os.path.exists(wd + "/mdout")


def test_amb_simulation_restart_init(asim_restart):
    """Test initialization."""
    ambs, wd = asim_restart
    sim = ambs()
    assert os.path.isdir(wd)
    assert os.path.isdir(sim.coffe_dir)
    assert sim.mdin_options["cntrl.irest"] == 1
    assert sim.mdin_options["cntrl.ntx"] == 5


def test_amb_simulation_run_restart(asim_restart):
    """Test a normal simulation run with restart file."""
    ambs, wd = asim_restart
    sim = ambs()
    assert os.path.isdir(wd)
    assert os.path.exists(wd + "/steering_mdin")
    sim()
    assert os.path.exists(wd + "/mdout")


def test_amb_simulation_warn_no_initial_conf(asim):
    """Test a simulation initialization where the structure file is only created
    after initialization."""
    ambs, wd = asim
    sim = ambs(structure=os.path.join(wd, ".coffe/blablacrd"))
    with open(os.path.join(wd, ".coffe/log.txt"), 'r') as log:
        assert "The indicated structure file" in log.read()


def test_amb_simulation_nowarn_no_initial_conf(asim):
    """Test a simulation initialization where the structure file is only created
    after initialization."""
    ambs, wd = asim
    sim = ambs(structure=os.path.join(wd, ".coffe/inpcrd"))
    with open(os.path.join(wd, ".coffe/log.txt"), 'r') as log:
        assert "The indicated structure file" not in log.read()


def test_amb_simulation_run_no_initial_conf(asim):
    """Test a simulation run where the structure file is only created after
    initialization."""
    ambs, wd = asim
    s = os.path.join(wd, ".coffe/inpcrd")
    sim = ambs(structure=s)
    shutil.copy(pkgdata.abspath("data/test_inpcrd"), s)
    sim()
    assert os.path.exists(wd + "/mdout")

# TODO check logging (as in test_util.py)
