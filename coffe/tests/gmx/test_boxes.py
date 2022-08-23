# -*- coding: utf-8 -*-

"""Tests for coffe.gmx.boxes functions"""

from __future__ import absolute_import, division, print_function
import os
import pytest
import coffe.gmx.boxes as gmxboxes
import coffe.gmx.sim as gmxsim
from coffe.core import pkgdata, thirdparty
from coffe.misc import util
from .box_fixture import boxes_environment

# skip all if gromacs is not installed
pytestmark = pytest.mark.skipif(not thirdparty.GROMACS.exists,
    reason="The tests in this module require a functioning gromacs installation")


def test_gmx_mkbox_homogeneous_pure(tmpdir):
    substance = pkgdata.abspath("data/boxes/c16.pdb")
    ff_dir = pkgdata.abspath("data/boxes/charmm36-andi/charmm36-andi.ff")
    box_size = 5
    n_mols = 10
    structure, topology = gmxboxes.gmx_mkbox_homogeneous(substance,
                                                         n_mols=n_mols,
                                                         box_size=box_size,
                                                         ff_dir=ff_dir,
                                                         work_dir=str(tmpdir))
    assert os.path.isfile(structure)
    assert os.path.isfile(topology)
    # check grompp
    mdp_file = pkgdata.abspath("data/test_mdp.mdp")
    gmxsim.GmxCalculation(structure, topology, mdp_file, str(tmpdir))


def test_gmx_mkbox_homogeneous_pure_densnmol(tmpdir):
    substance = pkgdata.abspath("data/boxes/c16.pdb")
    ff_dir = pkgdata.abspath("data/boxes/charmm36-andi/charmm36-andi.ff")
    density = 770
    m_mol = 226.41
    n_mols = 30
    structure, topology = gmxboxes.gmx_mkbox_homogeneous(substance,
                                                         n_mols=n_mols,
                                                         density=density,
                                                         m_mol=m_mol,
                                                         ff_dir=ff_dir,
                                                         work_dir=str(tmpdir))
    assert os.path.isfile(structure)
    assert os.path.isfile(topology)
    with open(structure, "r") as structure_file:
        struc = structure_file.readlines()
    n_mols_test = int(struc[-2][0:5].replace(" ", ""))
    box_size_test = (float(struc[-1].split()[0]), float(struc[-1].split()[1]), float(struc[-1].split()[2]))
    density_test = util.compute_density(box_size_test, n_mols_test, m_mol)
    density_sum = 0
    for dens in density_test:
        density_sum += dens
    assert abs((density-density_sum)/density) < 1e-4
    # check grompp
    mdp_file = pkgdata.abspath("data/test_mdp.mdp")
    gmxsim.GmxCalculation(structure, topology, mdp_file, str(tmpdir))


def test_gmx_mkbox_homogeneous_pure_densboxsize(tmpdir):
    substance = pkgdata.abspath("data/boxes/c16.pdb")
    ff_dir = pkgdata.abspath("data/boxes/charmm36-andi/charmm36-andi.ff")
    density = 770
    m_mol = 226.41
    box_size = 3
    structure, topology = gmxboxes.gmx_mkbox_homogeneous(substance,
                                                         box_size=box_size,
                                                         density=density,
                                                         m_mol=m_mol,
                                                         ff_dir=ff_dir,
                                                         work_dir=str(tmpdir))
    assert os.path.isfile(structure)
    assert os.path.isfile(topology)
    with open(structure, "r") as structure_file:
        struc = structure_file.readlines()
    n_mols_test = int(struc[-2][0:5].replace(" ", ""))
    box_size_test = (float(struc[-1].split()[0]), float(struc[-1].split()[1]), float(struc[-1].split()[2]))
    density_test = util.compute_density(box_size_test, n_mols_test, m_mol)
    density_sum = 0
    for dens in density_test:
        density_sum += dens
    assert abs((density-density_sum)/density) < 1e-2
    # check grompp
    mdp_file = pkgdata.abspath("data/test_mdp.mdp")
    gmxsim.GmxCalculation(structure, topology, mdp_file, str(tmpdir))


def test_gmx_mkbox_homogeneous_mix3(tmpdir):
    substance = [pkgdata.abspath("data/boxes/c16.pdb"),
                 pkgdata.abspath("data/boxes/c2.pdb"),
                 pkgdata.abspath("data/boxes/c4.pdb")]
    ff_dir = pkgdata.abspath("data/boxes/charmm36-andi/charmm36-andi.ff")
    box_size = 5
    n = [10, 10, 10]
    structure, topology = gmxboxes.gmx_mkbox_homogeneous(substance, n_mols=n,
                                                         box_size=box_size,
                                                         ff_dir=ff_dir,
                                                         work_dir=str(tmpdir))
    assert os.path.isfile(structure)
    assert os.path.isfile(topology)
    # check grompp
    mdp_file = pkgdata.abspath("data/test_mdp.mdp")
    gmxsim.GmxCalculation(structure, topology, mdp_file, str(tmpdir))


# TODO: Alle Partialdichten und n_mols vorgeben, box_size berechnen.
#  Funktioniert das?
# def test_gmx_mkbox_homogeneous_mix3_densnmol(tmpdir):
#     substance = [pkgdata.abspath("data/boxes/c16.pdb"),
#                  pkgdata.abspath("data/boxes/c4.pdb"),
#                  pkgdata.abspath("data/boxes/c2.pdb")]
#     ff_dir = pkgdata.abspath("data/boxes/charmm36-andi/charmm36-andi.ff")
#     density = [1.5,]
#     m_mol = [226.41,]
#     n_mols = [30,]
#     structure, topology = gmxboxes.gmx_mkbox_homogeneous(substance,
#                                                          n_mols=n_mols,
#                                                          density=density,
#                                                          m_mol=m_mol,
#                                                          ff_dir=ff_dir,
#                                                          work_dir=str(tmpdir))
#     # check grompp
#     mdp_file = pkgdata.abspath("data/test_mdp.mdp")
#     gmxsim.GmxCalculation(structure, topology, mdp_file, str(tmpdir))


def test_gmx_mkbox_homogeneous_mix3_densboxsize(tmpdir):
    substance = [pkgdata.abspath("data/boxes/c16.pdb"),
                 pkgdata.abspath("data/boxes/c4.pdb"),
                 pkgdata.abspath("data/boxes/c2.pdb")]
    ff_dir = pkgdata.abspath("data/boxes/charmm36-andi/charmm36-andi.ff")
    density = [500, 170, 100]
    m_mol = [226.41, 58.12, 30.07]
    box_size = 3
    structure, topology = gmxboxes.gmx_mkbox_homogeneous(substance,
                                                         box_size=box_size,
                                                         density=density,
                                                         m_mol=m_mol,
                                                         ff_dir=ff_dir,
                                                         work_dir=str(tmpdir))
    # check grompp
    mdp_file = pkgdata.abspath("data/test_mdp.mdp")
    gmxsim.GmxCalculation(structure, topology, mdp_file, str(tmpdir))


def test_gmx_mkbox_homogeneous_nmols_wrong(tmpdir):
    with pytest.raises(ValueError):
        substance = [pkgdata.abspath("data/boxes/c16.pdb"),
                     pkgdata.abspath("data/boxes/c2.pdb")]
        ff_dir = pkgdata.abspath("data/boxes/charmm36-andi/charmm36-andi.ff")
        box_size = 5
        n = 10
        gmxboxes.gmx_mkbox_homogeneous(substance, n_mols=n, box_size=box_size,
                                       ff_dir=ff_dir, work_dir=str(tmpdir))


def test_gmx_mkbox_homogeneous_density_wrong(tmpdir):
    with pytest.raises(ValueError):
        substance = [pkgdata.abspath("data/boxes/c16.pdb"),
                     pkgdata.abspath("data/boxes/c2.pdb")]
        ff_dir = pkgdata.abspath("data/boxes/charmm36-andi/charmm36-andi.ff")
        box_size = 5
        density = 1.5
        m_mol = [226.41, 30.07]
        gmxboxes.gmx_mkbox_homogeneous(substance, density=density, m_mol=m_mol,
                                       box_size=box_size, ff_dir=ff_dir,
                                       work_dir=str(tmpdir))


def test_gmx_mkbox_homogeneous_mmol_wrong(tmpdir):
    with pytest.raises(ValueError):
        substance = [pkgdata.abspath("data/boxes/c16.pdb"),
                     pkgdata.abspath("data/boxes/c2.pdb")]
        ff_dir = pkgdata.abspath("data/boxes/charmm36-andi/charmm36-andi.ff")
        box_size = 5
        density = [1.5, 2.5]
        m_mol = 226.41
        gmxboxes.gmx_mkbox_homogeneous(substance, density=density, m_mol=m_mol,
                                       box_size=box_size, ff_dir=ff_dir,
                                       work_dir=str(tmpdir))


def test_gmx_mkbox_homogeneous_mmol_wrong(tmpdir):
    with pytest.raises(ValueError):
        substance = [pkgdata.abspath("data/boxes/c16.pdb"),
                     pkgdata.abspath("data/boxes/c2.pdb")]
        ff_dir = pkgdata.abspath("data/boxes/charmm36-andi/charmm36-andi.ff")
        box_size = 5
        substance_name = "Hexadecane"
        gmxboxes.gmx_mkbox_homogeneous(substance, substance_name=substance_name,
                                       box_size=box_size, ff_dir=ff_dir,
                                       work_dir=str(tmpdir))


def test_gmx_mkbox_twophase_pure(tmpdir):
    substance = pkgdata.abspath("data/boxes/c16.pdb")
    ff_dir = pkgdata.abspath("data/boxes/charmm36-andi/charmm36-andi.ff")
    box_size = 5
    n_mols_v = 5
    n_mols_l = 50
    structure, topology = gmxboxes.gmx_mkbox_twophase(substance,
                                                      n_mols_v=n_mols_v,
                                                      n_mols_l=n_mols_l,
                                                      box_size=box_size,
                                                      ff_dir=ff_dir,
                                                      work_dir=str(tmpdir))
    assert os.path.isfile(structure)
    assert os.path.isfile(topology)
    mdp_file = pkgdata.abspath("data/test_mdp.mdp")
    gmxsim.GmxCalculation(structure, topology, mdp_file, str(tmpdir))


def test_gmx_mkbox_twophase_pure_densboxsize(tmpdir):
    substance = pkgdata.abspath("data/boxes/c16.pdb")
    ff_dir = pkgdata.abspath("data/boxes/charmm36-andi/charmm36-andi.ff")
    box_size = 3
    density_v = 15.0
    density_l = 770.0
    m_mol = 226.41
    structure, topology = gmxboxes.gmx_mkbox_twophase(substance,
                                                      density_v=density_v,
                                                      density_l=density_l,
                                                      m_mol=m_mol,
                                                      box_size=box_size,
                                                      ff_dir=ff_dir,
                                                      work_dir=str(tmpdir))
    assert os.path.isfile(structure)
    assert os.path.isfile(topology)
    mdp_file = pkgdata.abspath("data/test_mdp.mdp")
    gmxsim.GmxCalculation(structure, topology, mdp_file, str(tmpdir))

def test_gmx_mkbox_twophase_mix3(tmpdir):
    substance = [pkgdata.abspath("data/boxes/c16.pdb"),
                 pkgdata.abspath("data/boxes/c4.pdb"),
                 pkgdata.abspath("data/boxes/c2.pdb")]
    ff_dir = pkgdata.abspath("data/boxes/charmm36-andi/charmm36-andi.ff")
    box_size = 5
    n_mols_v = [5, 5, 5]
    n_mols_l = [50, 50, 50]
    structure, topology = gmxboxes.gmx_mkbox_twophase(substance,
                                                      n_mols_v=n_mols_v,
                                                      n_mols_l=n_mols_l,
                                                      box_size=box_size,
                                                      ff_dir=ff_dir,
                                                      work_dir=str(tmpdir))
    assert os.path.isfile(structure)
    assert os.path.isfile(topology)
    mdp_file = pkgdata.abspath("data/test_mdp.mdp")
    gmxsim.GmxCalculation(structure, topology, mdp_file, str(tmpdir))


def test_gmx_mkbox_twophase_mix3_densboxsize(tmpdir):
    substance = [pkgdata.abspath("data/boxes/c16.pdb"),
                 pkgdata.abspath("data/boxes/c4.pdb"),
                 pkgdata.abspath("data/boxes/c2.pdb")]
    ff_dir = pkgdata.abspath("data/boxes/charmm36-andi/charmm36-andi.ff")
    box_size = 3
    density_v = [15.0, 15.0, 15.0]
    density_l = [300.0, 300.0, 300.0]
    m_mol = [226.41, 58.12, 30.07]
    structure, topology = gmxboxes.gmx_mkbox_twophase(substance,
                                                      density_v=density_v,
                                                      density_l=density_l,
                                                      m_mol=m_mol,
                                                      box_size=box_size,
                                                      ff_dir=ff_dir,
                                                      work_dir=str(tmpdir))
    assert os.path.isfile(structure)
    assert os.path.isfile(topology)
    mdp_file = pkgdata.abspath("data/test_mdp.mdp")
    gmxsim.GmxCalculation(structure, topology, mdp_file, str(tmpdir))


def test_mkbox_no_boxtype(boxes_environment):
    with pytest.raises(AssertionError):
        os.chdir(boxes_environment)
        gmxboxes.gmx_mkbox(
            cfg_file=os.path.join(boxes_environment, "box_validity.cfg"),
            section="withouttype")


def test_mkbox_cfg_boxtype(boxes_environment):
    os.chdir(boxes_environment)
    result = gmxboxes.gmx_mkbox(
        cfg_file=os.path.join(boxes_environment, "box_validity.cfg"),
        section="withtype")
    assert len(result) == 2
    assert os.path.isfile(result[0])
    assert os.path.isfile(result[0])


def test_mkbox_override_none_boxtype(boxes_environment):
    os.chdir(boxes_environment)
    result = gmxboxes.gmx_mkbox(boxtype=None, cfg_file=os.path.join(boxes_environment,
                                                           "box_validity.cfg"),
                       section="withtype")
    assert len(result) == 2
    assert os.path.isfile(result[0])
    assert os.path.isfile(result[0])



def test_mkbox_args_boxtype(boxes_environment):
    os.chdir(boxes_environment)
    result = gmxboxes.gmx_mkbox(boxtype="homogeneous",
                       cfg_file=os.path.join(boxes_environment,
                                             "box_validity.cfg"),
                       section="withouttype")
    assert len(result) == 2
    assert os.path.isfile(result[0])
    assert os.path.isfile(result[0])



def test_gmx_mkbox_solvation(tmpdir):
    # TODO(AK) implement test
    pass
