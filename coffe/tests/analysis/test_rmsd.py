# -*- coding: utf-8 -*-

"""Tests for coffe.analysis.rmsd functions"""

from __future__ import absolute_import, division, print_function

import pandas

from coffe.core import pkgdata
from coffe.analysis import rmsd


def test_rmsd_pdb_csv(tmpdir):
    """
    Tests for computing rmsd on individual pdb files and create an rmsd.csv
    output file.
    """
    structures = ['data/molecule-1.pdb', 'data/molecule-2.pdb', 'data/molecule-3.pdb', 'data/molecule-4.pdb']
    structures = [pkgdata.abspath(s) for s in structures]

    file_target = pkgdata.abspath("data/rmsd.csv.target")
    file_generated = "{0}/rmsd.csv".format(str(tmpdir))

    csv_out = rmsd.rmsd_individual_csv(structures, file_generated, str(tmpdir))

    generated = pandas.read_csv(csv_out)
    expected = pandas.read_csv(file_target)

    assert (generated["rmsd_all"].round(3) == expected["rmsd_all"].round(3)).all()
    assert (generated["rmsd_noH"].round(3) == expected["rmsd_noH"].round(3)).all()


def test_rmsd_mol2_csv(tmpdir):
    """
    Tests for computing rmsd on individual pdb files and create an rmsd.csv
    output file.
    """
    structures = ['data/molecule-1.mol2', 'data/molecule-2.mol2', 'data/molecule-3.mol2', 'data/molecule-4.mol2']
    structures = [pkgdata.abspath(s) for s in structures]

    file_target = pkgdata.abspath("data/rmsd.csv.target")
    file_generated = "{0}/rmsd.csv".format(str(tmpdir))

    csv_out = rmsd.rmsd_individual_csv(structures, file_generated, str(tmpdir))

    generated = pandas.read_csv(csv_out)
    expected = pandas.read_csv(file_target)

    assert (generated["rmsd_all"].round(3) == expected["rmsd_all"].round(3)).all()
    assert (generated["rmsd_noH"].round(3) == expected["rmsd_noH"].round(3)).all()


