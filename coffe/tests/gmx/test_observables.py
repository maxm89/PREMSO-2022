# -*- coding: utf-8 -*-

"""Utility and helper functions for Gromacs"""

from __future__ import absolute_import, division, print_function

from coffe.gmx import observables
from coffe.core import pkgdata, thirdparty
from coffe.gmx.sim import GmxCalculation
import pytest
import os
import tempfile
import shutil
import pandas as pd

# skip all if gromacs is not installed
pytestmark = pytest.mark.skipif(not thirdparty.GROMACS.exists,
                                reason="The tests in this module require a "
                                       "functioning gromacs installation")


@pytest.yield_fixture(scope="module")
def simulation():
    """Simulation fixture."""
    tmp = tempfile.mkdtemp()
    s = pkgdata.abspath("data/test_structure.pdb")
    t = pkgdata.abspath("data/test_topology.top")
    mdp = pkgdata.abspath("data/test_mdp.mdp")
    wd = os.path.join(tmp, "test_sim")
    gmx = GmxCalculation(s, t, mdp, wd)
    gmx()
    yield gmx
    shutil.rmtree(tmp)


def test_calc_energy(simulation):
    res = observables.gmx_calc_energy(simulation.work_dir)
    assert res is not None


def test_get_densities(tmpdir):
    traj = pkgdata.abspath("data/test_traj.gro")
    topol = pkgdata.abspath("data/test_topol.tpr")
    rho_l, rho_v, i_w, z_l, z_r, df, left_fit, right_fit = observables.get_densities(
        traj, topol, n_substances=2, first_frame=-1, last_frame=-1,
        dens="number", show_plot=False, work_dir=str(tmpdir))
    assert isinstance(rho_l, float), "Liquid Density not available!"
    assert isinstance(rho_v, float), "Vapor Density not available!"
    assert isinstance(i_w, float), "Interface Width not available!"
    assert isinstance(z_l, float), "Left-hand Interface position not available!"
    assert isinstance(z_r, float), "Right-hand Interface position not " \
                                   "available!"
    assert isinstance(df, pd.DataFrame), "Dataframe could not be created!"
    assert len(left_fit) == 4, "Left-hand fit is not a list!"
    assert len(right_fit) == 4, "Right-hand fit is not a list!"
