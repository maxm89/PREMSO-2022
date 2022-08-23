# -*- coding: utf-8 -*-

"""Test for extracting raw energies from qm calculations.
    Currently supports GAMESS and Psi4.
    """

from __future__ import absolute_import, division, print_function

from .. import helper_functions
from coffe.core import pkgdata
from coffe.quantum import extract_qm_energies


def test_psi4_qm10_10(tmpdir):
    source_dir = pkgdata.abspath('data/00_Psi4_Opt_QM10-10')
    file_target = str(source_dir) + '/Energies_raw.csv.target'
    file_generated = str(tmpdir) + '/Energies_raw.csv'
    program = 'psi4'
    extract_qm_energies.extract_energies_and_write(source_dir, tmpdir, file_generated, program)
    assert helper_functions.are_csv_files_equal(file_generated, file_target)


def test_psi4_qm20_21(tmpdir):
    source_dir = pkgdata.abspath('data/00_Psi4_Opt_QM20-21')
    file_target = str(source_dir) + '/Energies_raw.csv.target'
    file_generated = str(tmpdir) + '/Energies_raw.csv'
    program = 'psi4'
    extract_qm_energies.extract_energies_and_write(source_dir, tmpdir, file_generated, program)
    assert helper_functions.are_csv_files_equal(file_generated, file_target)


def test_psi4_qm2021_3521(tmpdir):
    source_dir = pkgdata.abspath('data/01_Psi4_HLSP_QM20-21_35-21')
    file_target = str(source_dir) + '/Energies_raw.csv.target'
    file_generated = str(tmpdir) + '/Energies_raw.csv'
    program = 'psi4'
    extract_qm_energies.extract_energies_and_write(source_dir, tmpdir, file_generated, program)
    assert helper_functions.are_csv_files_equal(file_generated, file_target)


def test_psi4_qm2021_6121(tmpdir):
    source_dir = pkgdata.abspath('data/01_Psi4_HLSP_QM20-21_61-21')
    file_target = str(source_dir) + '/Energies_raw.csv.target'
    file_generated = str(tmpdir) + '/Energies_raw.csv'
    program = 'psi4'
    extract_qm_energies.extract_energies_and_write(source_dir, tmpdir, file_generated, program)
    assert helper_functions.are_csv_files_equal(file_generated, file_target)


def test_psi4_qm21_20cbs34(tmpdir):
    source_dir = pkgdata.abspath('data/01_Psi4_HLSP_QM20-21_20-CBS34')
    file_target = str(source_dir) + '/Energies_raw.csv.target'
    file_generated = str(tmpdir) + '/Energies_raw.csv'
    program = 'psi4'
    extract_qm_energies.extract_energies_and_write(source_dir, tmpdir, file_generated, program)
    assert helper_functions.are_csv_files_equal(file_generated, file_target)


def test_gamess_qm10_10(tmpdir):
    source_dir = pkgdata.abspath('data/00_Gamess_Opt_QM10-10')
    file_target = str(source_dir) + '/Energies_raw.csv.target'
    file_generated = str(tmpdir) + '/Energies_raw.csv'
    program = 'gamess'
    extract_qm_energies.extract_energies_and_write(source_dir, tmpdir, file_generated, program)
    assert helper_functions.are_csv_files_equal(file_generated, file_target)


def test_gamess_qm1010_2020(tmpdir):
    source_dir = pkgdata.abspath('data/01_Gamess_HLSP_QM10-10_20-20')
    file_target = str(source_dir) + '/Energies_raw.csv.target'
    file_generated = str(tmpdir) + '/Energies_raw.csv'
    program = 'gamess'
    extract_qm_energies.extract_energies_and_write(source_dir, tmpdir, file_generated, program)
    assert helper_functions.are_csv_files_equal(file_generated, file_target)
