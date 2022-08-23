# -*- coding: utf-8 -*-

"""Test for creating full qm optimization input files."""

from __future__ import absolute_import, division, print_function
import pytest
from coffe.misc import create_torsion_conformers
from coffe.analysis import pdb_reader
from coffe.core import pkgdata, thirdparty

pytestmark = pytest.mark.skipif(not thirdparty.PYMOL.exists,
                                reason="All functions tested here require pymol.")


def test_create_7_1d_pdb_torsions(tmpdir):
    """Test to make 7 conformations from 0 to 180 degrees in 30 degree
    increments. Input and output are PDB files."""

    inputfile = pkgdata.abspath("data/molecule-1-gam.inp.log.pdb")
    int_coord_1 = '1,5,8,11'
    degree_inc_1 = 30
    number_conf_1 = 7
    directory_target = str(tmpdir)
    directory_compare = pkgdata.abspath("data/torsion_conf_1")

    create_torsion_conformers.create_torsion_conformers(inputfile,
                                                    int_coord_1,
                                                    number_conf_1,
                                                    degree_inc_1,
                                                    work_dir=directory_target)

    file_generated_1 = directory_target + '/1.pdb'
    file_target_1 = directory_compare + '/1.pdb.target'
    file_generated_2 = directory_target + '/2.pdb'
    file_target_2 = directory_compare + '/2.pdb.target'
    file_generated_3 = directory_target + '/3.pdb'
    file_target_3 = directory_compare + '/3.pdb.target'
    file_generated_4 = directory_target + '/4.pdb'
    file_target_4 = directory_compare + '/4.pdb.target'
    file_generated_5 = directory_target + '/5.pdb'
    file_target_5 = directory_compare + '/5.pdb.target'
    file_generated_6 = directory_target + '/6.pdb'
    file_target_6 = directory_compare + '/6.pdb.target'
    file_generated_7 = directory_target + '/7.pdb'
    file_target_7 = directory_compare + '/7.pdb.target'

    assert pdb_reader.are_pdbs_equal(file_generated_1, file_target_1)
    assert pdb_reader.are_pdbs_equal(file_generated_2, file_target_2)
    assert pdb_reader.are_pdbs_equal(file_generated_3, file_target_3)
    assert pdb_reader.are_pdbs_equal(file_generated_4, file_target_4)
    assert pdb_reader.are_pdbs_equal(file_generated_5, file_target_5)
    assert pdb_reader.are_pdbs_equal(file_generated_6, file_target_6)
    assert pdb_reader.are_pdbs_equal(file_generated_7, file_target_7)


def test_create_13_1d_pdb_torsions(tmpdir):
    """Test to make 13 conformations from 0 to 180 degrees in 15 degree
    increments. Input and output are PDB files."""

    inputfile = pkgdata.abspath("data/molecule-1-gam.inp.log.pdb")
    int_coord_1 = '1,5,8,11'
    degree_inc_1 = 15
    number_conf_1 = 13
    directory_target = str(tmpdir)
    directory_compare = pkgdata.abspath("data/torsion_conf_2")

    create_torsion_conformers.create_torsion_conformers(inputfile,
                                                    int_coord_1,
                                                    number_conf_1,
                                                    degree_inc_1,
                                                    work_dir=directory_target)

    file_generated_1 = directory_target + '/01.pdb'
    file_target_1 = directory_compare + '/01.pdb.target'
    file_generated_2 = directory_target + '/02.pdb'
    file_target_2 = directory_compare + '/02.pdb.target'
    file_generated_3 = directory_target + '/07.pdb'
    file_target_3 = directory_compare + '/07.pdb.target'
    file_generated_4 = directory_target + '/10.pdb'
    file_target_4 = directory_compare + '/10.pdb.target'
    file_generated_5 = directory_target + '/13.pdb'
    file_target_5 = directory_compare + '/13.pdb.target'

    assert pdb_reader.are_pdbs_equal(file_generated_1, file_target_1)
    assert pdb_reader.are_pdbs_equal(file_generated_2, file_target_2)
    assert pdb_reader.are_pdbs_equal(file_generated_3, file_target_3)
    assert pdb_reader.are_pdbs_equal(file_generated_4, file_target_4)
    assert pdb_reader.are_pdbs_equal(file_generated_5, file_target_5)


def test_create_144_2d_pdb_torsions(tmpdir):
    """Test to make 144 conformations from rotating two torsion angles from 0
    to 330 degrees in 30 degree increments. Input and output are PDB files."""

    inputfile = pkgdata.abspath("data/pentanol_conf1.pdb")
    int_coord_1 = '1,11,8,5'
    int_coord_2 = '11,8,5,16'
    number_conf_1 = 12
    degree_inc_1 = 30
    number_conf_2 = 12
    degree_inc_2 = 30
    directory_target = str(tmpdir)
    directory_compare = pkgdata.abspath("data/torsion_conf_3")

    create_torsion_conformers.create_torsion_conformers(inputfile,
                                                    int_coord_1,
                                                    number_conf_1,
                                                    degree_inc_1,
                                                    int_coord_2,
                                                    number_conf_2,
                                                    degree_inc_2,
                                                    work_dir=directory_target)

    file_generated_1 = directory_target + '/01-01.pdb'
    file_target_1 = directory_compare + '/01-01.pdb.target'
    file_generated_2 = directory_target + '/02-07.pdb'
    file_target_2 = directory_compare + '/02-07.pdb.target'
    file_generated_3 = directory_target + '/07-09.pdb'
    file_target_3 = directory_compare + '/07-09.pdb.target'
    file_generated_4 = directory_target + '/12-12.pdb'
    file_target_4 = directory_compare + '/12-12.pdb.target'

    assert pdb_reader.are_pdbs_equal(file_generated_1, file_target_1)
    assert pdb_reader.are_pdbs_equal(file_generated_2, file_target_2)
    assert pdb_reader.are_pdbs_equal(file_generated_3, file_target_3)
    assert pdb_reader.are_pdbs_equal(file_generated_4, file_target_4)


def test_create_156_2d_pdb_torsions(tmpdir):
    """Test to make 156 conformations from rotating two torsion angles:
    0 to 330 degrees in 30, and 0 to 180 in 15 degree increments.
    Input and output are PDB files."""

    inputfile = pkgdata.abspath("data/pentanol_conf1.pdb")
    int_coord_1 = '1,11,8,5'
    number_conf_1 = 12
    degree_inc_1 = 30
    int_coord_2 = '11,8,5,16'
    number_conf_2 = 13
    degree_inc_2 = 15
    directory_target = str(tmpdir)
    directory_compare = pkgdata.abspath("data/torsion_conf_4")

    create_torsion_conformers.create_torsion_conformers(inputfile,
                                                    int_coord_1,
                                                    number_conf_1,
                                                    degree_inc_1,
                                                    int_coord_2,
                                                    number_conf_2,
                                                    degree_inc_2,
                                                    work_dir=directory_target)

    file_generated_1 = directory_target + '/01-02.pdb'
    file_target_1 = directory_compare + '/01-02.pdb.target'
    file_generated_2 = directory_target + '/02-07.pdb'
    file_target_2 = directory_compare + '/02-07.pdb.target'
    file_generated_3 = directory_target + '/12-13.pdb'
    file_target_3 = directory_compare + '/12-13.pdb.target'

    assert pdb_reader.are_pdbs_equal(file_generated_1, file_target_1)
    assert pdb_reader.are_pdbs_equal(file_generated_2, file_target_2)
    assert pdb_reader.are_pdbs_equal(file_generated_3, file_target_3)


def test_create_1728_3d_pdb_torsions(tmpdir):
    """Test to make 156 conformations from rotating two torsion angles:
    0 to 330 degrees in 30, and 0 to 180 in 15 degree increments.
    Input and output are PDB files."""

    inputfile = pkgdata.abspath("data/pentanol_conf1.pdb")
    int_coord_1 = '1,11,8,5'
    number_conf_1 = 12
    degree_inc_1 = 30
    int_coord_2 = '11,8,5,16'
    number_conf_2 = 12
    degree_inc_2 = 30
    int_coord_3 = '8,5,16,14'
    number_conf_3 = 12
    degree_inc_3 = 30
    directory_target = str(tmpdir)
    directory_compare = pkgdata.abspath("data/torsion_conf_5")

    create_torsion_conformers.create_torsion_conformers(inputfile,
                                                    int_coord_1,
                                                    number_conf_1,
                                                    degree_inc_1,
                                                    int_coord_2,
                                                    number_conf_2,
                                                    degree_inc_2,
                                                    int_coord_3,
                                                    number_conf_3,
                                                    degree_inc_3,
                                                    work_dir=directory_target)

    file_generated_1 = directory_target + '/01-01-01.pdb'
    file_target_1 = directory_compare + '/01-01-01.pdb.target'
    file_generated_2 = directory_target + '/07-08-10.pdb'
    file_target_2 = directory_compare + '/07-08-10.pdb.target'
    file_generated_3 = directory_target + '/12-12-12.pdb'
    file_target_3 = directory_compare + '/12-12-12.pdb.target'

    assert pdb_reader.are_pdbs_equal(file_generated_1, file_target_1)
    assert pdb_reader.are_pdbs_equal(file_generated_2, file_target_2)
    assert pdb_reader.are_pdbs_equal(file_generated_3, file_target_3)
