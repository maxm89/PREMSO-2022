# -*- coding: utf-8 -*-

"""Tests for coffe.misc.gamlog_reader functions

This module provides tests for the module coffe.quantum.gamlog_reader

"""

from __future__ import absolute_import, division, print_function

import os
import pytest

from coffe.quantum import extract_qm_structure
from coffe.core import pkgdata


def test_read_gam_output_structure():
    """Test for read_gam_output_structure. Compares equilibrium structure
    read from a Gamess output file with a given target structure.

    """
    gamlogfile = pkgdata.abspath("data/gamout.log")
    print('KNK0: ', gamlogfile)
    source = extract_qm_structure.read_quantum_output_structure(gamlogfile)
    targetlogfile = open(pkgdata.abspath("data/gamout.log.target"),"r")
    target=[]
    for line in targetlogfile:
        target.append(line.split())
    assert source == target


def test_read_psi_output_structure():
    """Test for read_gam_output_structure. Compares equilibrium structure
    read from a Gamess output file with a given target structure.

    """
    psilogfile = pkgdata.abspath("data/psiout.log")
    source = extract_qm_structure.read_quantum_output_structure(psilogfile)
    targetlogfile = open(pkgdata.abspath("data/psiout.log.target"),"r")
    target=[]
    for line in targetlogfile:
        target.append(line.split())
    assert source == target


def test_check_gam_equilibrium():
    """Test for check_quantum_equilibrium. The given Gamess log file contains
    an equilibrated structure that has to be found.

    """
    gamlogfile = pkgdata.abspath("data/gamout.log")
    equilibrated = extract_qm_structure.check_quantum_equilibrium(gamlogfile)
    assert equilibrated


def test_check_psi_equilibrium():
    """Test for check_quantum_equilibrium. The given Psi4 log file contains
    an equilibrated structure that has to be found.

    """
    psilogfile = pkgdata.abspath("data/psiout.log")
    equilibrated = extract_qm_structure.check_quantum_equilibrium(psilogfile)
    assert equilibrated


def test_check_quantum_gam_failure():
    """Test for check_quantum_equilibrium. The given file does not
    contain an Gamess-equilibrated structure, so we expect an error.

    """
    with pytest.raises(ValueError):
        gamlogfile = pkgdata.abspath("data/gamout.log.target")
        extract_qm_structure.check_quantum_equilibrium(gamlogfile,
                                                       program="gamess")


def test_check_psi_equilibrium_failure():
    """Test for check_quantum_equilibrium. The given file does not
    contain an Gamess-equilibrated structure, so we expect an error.

    """
    with pytest.raises(ValueError):
        psilogfile = pkgdata.abspath("data/psiout.log.target")
        extract_qm_structure.check_quantum_equilibrium(psilogfile,
                                                       program="psi4")


def test_qm2xyz_gam(tmpdir):
    """Test for qm2xyz for a gamess log file. An output file is expected to
    exist.

    """
    gamlogfile = pkgdata.abspath("data/gamout.log")
    xyz = os.path.join(str(tmpdir), "out.xyz")
    print('\n KNK1: ', xyz)
    xyz = extract_qm_structure.qm2xyz(gamlogfile, xyz, work_dir=str(tmpdir))
    assert os.path.isfile(xyz)


def test_qm2xyz_psi(tmpdir):
    """Test for qm2xyz for a psi4 log file. An output file is expected to exist.

    """
    psilogfile = pkgdata.abspath("data/psiout.log")
    print(psilogfile)
    xyz = os.path.join(str(tmpdir), "out.xyz")
    xyz = extract_qm_structure.qm2xyz(psilogfile, xyz, work_dir=str(tmpdir))
    assert os.path.isfile(xyz)


def test_qm2pdb_gam(tmpdir):
    """Test for qm2pdb for a gamess log file. An output file is expected to exist.

    """
    gamlogfile = pkgdata.abspath("data/gamout.log")
    pdb = os.path.join(str(tmpdir), "out.pdb")
    pdb = extract_qm_structure.qm2pdb(gamlogfile, pdb, work_dir=str(tmpdir))
    assert os.path.isfile(pdb)


def test_qm2pdb_psi(tmpdir):
    """Test for qm2pdb for a psi4 log file. An output file is expected to exist.

    """
    psilogfile = pkgdata.abspath("data/psiout.log")
    pdb = os.path.join(str(tmpdir), "out.pdb")
    pdb = extract_qm_structure.qm2pdb(psilogfile, pdb, work_dir=str(tmpdir))
    assert os.path.isfile(pdb)
