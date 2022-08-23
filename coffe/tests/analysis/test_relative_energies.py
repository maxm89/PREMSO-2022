# -*- coding: utf-8 -*-

"""Tests for coffe.analysis relative energy functions"""

from __future__ import absolute_import, division, print_function

import pytest

from coffe.analysis import relative_energies
from coffe.core import pkgdata
from .. import helper_functions


def test_relative_energies_list():
    """Test if relative energies are computed correctly."""

    raw = []
    raw_file = pkgdata.abspath("data/Energies_raw.txt")

    with open(raw_file) as input_data:
        for line in input_data:
            raw.append(line.strip())

    rel = relative_energies.relative_energies(raw, 'no')

    rel_target = [4.450404480757882, 2.307173008125474, 0.0, 0.8061096837899129,
                  3.0966794536319284, 4.12250573703632, 6.214660971402239,
                  7.854315324271987, 6.703124524988766, 2.646574533524614,
                  0.4968151306479385, 2.5800375975466068]

    assert rel == pytest.approx(rel_target)


def test_relative_energies_csv_two_columns(tmpdir):
    """Test if the resulting csv file is correct within round-off errors."""

    raw_file = pkgdata.abspath("data/Energies_raw.csv")

    file_generated_1 = '{0}/Energies_rel.csv'.format(str(tmpdir))
    file_target_1 = pkgdata.abspath("data/Energies_rel.csv.target")

    relative_energies.relative_energies_csv(raw_file, 'hartree2kcal', work_dir=str(tmpdir))

    assert helper_functions.are_csv_files_equal(file_generated_1, file_target_1)


def test_relative_energies_csv_three_columns(tmpdir):
    """Test if a three column input file (string, float, float) is correctly
     converted."""

    raw_file = pkgdata.abspath("data/Energies_raw_three_columns.csv")

    file_generated_1 = '{0}/Energies_rel.csv'.format(str(tmpdir))
    file_target_1 = pkgdata.abspath("data/Energies_rel_three_columns.csv.target")

    relative_energies.relative_energies_csv(raw_file, 'hartree2kcal', work_dir=str(tmpdir))

    assert helper_functions.are_csv_files_equal(file_generated_1, file_target_1)
