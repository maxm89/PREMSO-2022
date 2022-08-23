# -*- coding: utf-8 -*-

"""Tests for coffe.misc.pdb_reader functions

This module provides tests for the module coffe.misc.pdb_reader

"""

from __future__ import absolute_import, division, print_function

from coffe.analysis import pdb_reader
from coffe.core import filesys, pkgdata

import pandas
import shutil
import os


def test_read_pdb_structure():
    """Test for read_gam_output_structure. Compares equilibrium structure
    read from a Gamess output file with a given target structure.

    """
    with open(pkgdata.abspath("data/test.pdb"), "r") as pdbfile:
        source = pdb_reader.read_pdb_structure(pdbfile)
        targetlogfile = open(pkgdata.abspath("data/test.pdb.target"), "r")
        target = []
        for line in targetlogfile:
            target.append(line.split())
        assert source == target


def test_are_same_pdbs_equal():
    assert pdb_reader.are_pdbs_equal(pkgdata.abspath("data/test.pdb"),
                                     pkgdata.abspath("data/test.pdb"), 1e-10
                                     )


def test_are_pdbs_equal_tolerance():
    assert not pdb_reader.are_pdbs_equal(pkgdata.abspath("data/test.pdb"),
                                         pkgdata.abspath("data/test2.pdb"),
                                         1e-1)
    assert pdb_reader.are_pdbs_equal(pkgdata.abspath("data/test.pdb"),
                                     pkgdata.abspath("data/test2.pdb"),
                                     10)


def test_compute_geometry_distance(tmpdir):
    """Test for computation of a single distance on a single file with
    compute_geometry. Compares the distance of two atoms from a pdb file with
    the manually computed value.

    """
    src = pkgdata.abspath("data/test.pdb")
    dest = os.path.join(str(tmpdir), os.path.basename(src))
    shutil.copyfile(src, dest)
    source = pdb_reader.compute_geometry(dest, "C1,H2", "CHbond",
                                         work_dir=str(tmpdir))
    target = pandas.DataFrame(
        data=[[dest, "CHbond", "C1-H2", "bond", 1.085659707274798, "-"]],
        dtype=float,
        columns=("file", "name", "atoms", "type", "value", "conf")
    )
    assert (source == target).all().all()


def test_compute_geometry_angle(tmpdir):
    """Test for computation of a single angle on a single file with
    compute_geometry. Compares the distance of two atoms from a pdb file with
    the manually computed value.

    """
    src = pkgdata.abspath("data/test.pdb")
    dest = os.path.join(str(tmpdir), os.path.basename(src))
    shutil.copyfile(src, dest)
    source = pdb_reader.compute_geometry(dest, "C1,C5,C8", "CCCangle",
                                         work_dir=str(tmpdir))
    target = pandas.DataFrame(
        data=[[dest, "CCCangle", "C1-C5-C8", "angle", 113.0464635072865, "-"]],
        dtype=float,
        columns=("file", "name", "atoms", "type", "value", "conf")
    )
    assert (source.round(10) == target.round(10)).all().all()


def test_compute_geometry_dihedral(tmpdir):
    """Test for computation of a single torsion on a single file with
    compute_geometry. Compares the distance of two atoms from a pdb file with
    the manually computed value.

    """
    src = pkgdata.abspath("data/test.pdb")
    dest = os.path.join(str(tmpdir), os.path.basename(src))
    shutil.copyfile(src, dest)
    source = pdb_reader.compute_geometry(dest, "C1,C5,C8,C11", "CCCCdihed",
                                         work_dir=str(tmpdir))
    target = pandas.DataFrame(
        data=[[dest, "CCCCdihed", "C1-C5-C8-C11", "dihedral", 180.00, "T"]],
        dtype=float,
        columns=("file", "name", "atoms", "type", "value", "conf")
    )
    assert (source == target).all().all()


def test_compute_geometry_dihedral_mult(tmpdir):
    """Test for compute_dihedral with multiple files. Compares the dihedral of
    four atoms from a pdb file with the manually computed value.

    """
    src1 = pkgdata.abspath("data/test.pdb")
    src2 = pkgdata.abspath("data/test2.pdb")
    dest1 = os.path.join(str(tmpdir), os.path.basename(src1))
    dest2 = os.path.join(str(tmpdir), os.path.basename(src2))
    shutil.copyfile(src1, dest1)
    shutil.copyfile(src2, dest2)
    source = pdb_reader.compute_geometry(dest1, "C1,C5,C8,C11", "phi",
                                         work_dir=str(tmpdir))
    target = pandas.DataFrame(
        data=[[dest1, "phi", "C1-C5-C8-C11", "dihedral", 180.00, "T"]],
        dtype=float,
        columns=("file", "name", "atoms", "type", "value", "conf")
    )
    assert (source == target).all().all()
    source = pdb_reader.compute_geometry(dest2, "C1,C5,C8,C11", "phi",
                                         work_dir=str(tmpdir))
    target = pandas.DataFrame(
        data=[[dest2, "phi", "C1-C5-C8-C11", "dihedral", 0.00, "C"]],
        dtype=float,
        columns=("file", "name", "atoms", "type", "value", "conf")
    )
    assert (source == target).all().all()


def test_compute_mult_geometry_dihedral(tmpdir):
    """Test for compute_dihedral with a single file. Compares two dihedrals
    from a pdb file with the manually computed values.

    """
    src = pkgdata.abspath("data/test.pdb")
    dest = os.path.join(str(tmpdir), os.path.basename(src))
    shutil.copyfile(src, dest)
    source = pdb_reader.compute_geometry(dest, "C1,C5,C8,C11", "phi1",
                                         work_dir=str(tmpdir))
    source2 = pdb_reader.compute_geometry(dest, "C1,C5,C8,C11", "phi2",
                                          work_dir=str(tmpdir))
    source = source.append(source2, ignore_index=True)
    target = pandas.DataFrame(
        data=[[dest, "phi1", "C1-C5-C8-C11", "dihedral", 180.00, "T"],
              [dest, "phi2", "C1-C5-C8-C11", "dihedral", 180.00, "T"]
              ],
        dtype=float,
        columns=("file", "name", "atoms", "type", "value", "conf")
    )
    assert (source.dtypes == target.dtypes).all()
    assert (source == target).all().all()


def test_compute_conformation(tmpdir):
    """Test for compute_conformation.

    """
    src = pkgdata.abspath("data/test.pdb")
    dest = os.path.join(str(tmpdir), os.path.basename(src))
    shutil.copyfile(src, dest)
    confdeffile = pkgdata.abspath("data/molconf.def")
    source = pdb_reader.compute_conformation(dest, confdeffile,
                                             work_dir=str(tmpdir))
    target = pandas.DataFrame(data=[[dest, "TG-"]], dtype=float,
                              columns=("file", "conf")
                              )
    assert (source.dtypes == target.dtypes).all()
    assert (source == target).all().all()
