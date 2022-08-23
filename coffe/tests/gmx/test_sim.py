# -*- coding: utf-8 -*-

"""Tests for coffe.gmx.sim"""

from __future__ import absolute_import, division, print_function

from coffe.core import pkgdata, thirdparty, filesys
from coffe.gmx import sim as gmxsim
from coffe.gmx import util as gmxutil
# from coffe_fixtures import absrel_tmpdir


import os
import shutil
import pytest

# skip all if gromacs is not installed
pytestmark = pytest.mark.skipif(not thirdparty.GROMACS.exists,
                                reason="The tests in this module require a functioning gromacs installation")

@pytest.fixture
def gsim(tmpdir):
    """Simulation fixture. Returns a function that creates a GmxCalculation, as well as the work_dir."""
    s = pkgdata.abspath("data/test_structure.pdb")
    t = pkgdata.abspath("data/test_topology.top")
    mdp = pkgdata.abspath("data/test_mdp.mdp")
    wd = os.path.join(str(tmpdir), "test_sim")

    def wrapper(structure=s, topology=t, mdp_file=mdp, work_dir=wd, **kwargs):
        return gmxsim.GmxCalculation(structure, topology, mdp_file, work_dir, **kwargs)
    return wrapper, wd


def test_gmx_simulation_init(gsim):
    """Test initialization."""
    gs, wd = gsim
    sim = gs()
    assert os.path.isdir(wd)
    assert os.path.isdir(sim.coffe_dir)


def test_gmx_simulation_init_from_cfg(tmpdir):
    """Test initialization from config file."""
    d = str(tmpdir)
    shutil.copy(pkgdata.abspath("data/test_structure.pdb"), d)
    shutil.copy(pkgdata.abspath("data/test_topology.top"), d)
    shutil.copy(pkgdata.abspath("data/test_mdp.mdp"), d)
    # create temporary config file
    cfg_file = os.path.join(d,"test.cfg")
    wd = os.path.join(d, "test_sim")
    with open(cfg_file,"w") as f:
        f.writelines(
            [
                "[test_sim]\n",
                "structure:     '{}'\n".format(os.path.join(d,"test_structure.pdb")),
                "topology:      '{}'\n".format(os.path.join(d, "test_topology.top")),
                "mdp_file:      '{}'\n".format(os.path.join(d, "test_mdp.mdp")),
                "work_dir:      '{}'\n".format(wd),

            ]
        )
    sim = gmxsim.GmxCalculation(cfg_file=cfg_file, section="test_sim")
    assert os.path.isdir(wd)
    assert os.path.isdir(sim.coffe_dir)


def test_gmx_simulation_failure(gsim):
    """Test failure with no valid mdp file."""
    gs, wd = gsim
    with pytest.raises(Exception) as e_info:
        sim = gs(mdp_file=pkgdata.abspath("data/foo.mdp"))
        assert "does not exist" in e_info
    with open(os.path.join(wd,".coffe/log.txt"),'r') as log:
        assert "does not exist" in log.read()


def test_gmx_simulation_run(gsim):
    """Test a normal simulation run."""
    gs, wd = gsim
    sim = gs()
    assert os.path.isdir(wd)
    sim()


def test_gmx_simulation_warn_no_initial_conf(gsim):
    """Test a simulation initialization where the structure file is only created after initialization."""
    gs, wd = gsim
    sim = gs(structure=os.path.join(wd,".coffe/blabla.gro"))
    with open(os.path.join(wd, ".coffe/log.txt"), 'r') as log:
        assert "The indicated structure file" in log.read()


def test_gmx_simulation_nowarn_no_initial_conf(gsim):
    """Test a simulation initialization where the structure file is only created after initialization."""
    gs, wd = gsim
    sim = gs(structure=os.path.join(wd,".coffe/confout.gro"))
    with open(os.path.join(wd, ".coffe/log.txt"), 'r') as log:
        assert not "The indicated structure file" in log.read()


def test_gmx_simulation_run_no_initial_conf(gsim):
    """Test a simulation run where the structure file is only created after initialization."""
    gs, wd = gsim
    s = os.path.join(wd,".coffe/confout.pdb")
    sim = gs(structure=s)
    shutil.copy(pkgdata.abspath("data/test_structure.pdb"), s)
    sim()


def test_gmx_simulation_existing_mdp_option(gsim):
    """Test a simulation run with changed mdp options."""
    gs, wd = gsim
    sim = gs(mdp_options={"nsteps": 20})
    assert gmxutil.read_mdp_option(sim.mdp_file, "nsteps") == "20"


def test_gmx_simulation_new_mdp_option(gsim):
    """Test a simulation run with changed mdp options."""
    gs, wd = gsim
    s = os.path.join(wd,".coffe/confout.pdb")
    sim = gs(mdp_options={"foo": "bar"}, structure=s) # no intial config to prevent grompp
    assert gmxutil.read_mdp_option(sim.mdp_file, "foo") == "bar"


def is_restarted(simulation):
    with open(simulation.last_errfile, "r") as f:
        restarted = any("Reading checkpoint" in l for l in f)
    return restarted


def test_gmx_checkpoint_samedir(gsim):
    """Test restarting from checkpoint."""
    gs, wd = gsim
    s = os.path.join(wd,".coffe/confout.pdb")
    sim = gs(structure=s, mdp_options={"integrator": "sd"})
    shutil.copy(pkgdata.abspath("data/test_structure.pdb"), s)
    sim()
    sim2 = gs(structure=s, mdp_options={"integrator": "sd"},
              checkpoint=os.path.join(sim.work_dir, "state.cpt")
              # the checkpoint should be read implicitly
              )
    sim2()
    assert is_restarted(sim2)


def test_gmx_checkpoint_not_exist(gsim):
    """Test failure when checkpoint does not exist."""
    gs, wd = gsim
    s = os.path.join(wd,".coffe/confout.pdb")
    sim = gs(structure=s, checkpoint="blabla")
    shutil.copy(pkgdata.abspath("data/test_structure.pdb"), s)
    with pytest.raises(Exception):
        sim()


def get_start_time(simulation):
    simulation.call_cmd("gmx check -f traj.trr")
    start_frame = filesys.grep_line(simulation.last_errfile, "Reading frame")
    start_time = float(start_frame.strip().split()[4])
    return start_time


def test_gmx_checkpoint_otherdir(gsim):
    """Test restarting from checkpoint."""
    gs, wd = gsim
    s = os.path.join(wd,".coffe/confout.pdb")
    sim = gs(structure=s, mdp_options={"integrator": "sd"})
    shutil.copy(pkgdata.abspath("data/test_structure.pdb"), s)
    sim()
    sim2 = gs(structure=s, mdp_options={"integrator": "sd"},
              checkpoint=os.path.join(sim.work_dir, "state.cpt"),
              work_dir=os.path.join(wd, "next"))
    sim2()
    assert not is_restarted(sim2)
    assert all(os.path.isfile(os.path.join(sim2.work_dir, f))
               for f in ["ener.edr", "md.log", "traj.trr", "confout.gro"]
               )
    assert get_start_time(sim2) == 0.0
    assert not is_restarted(sim2)
