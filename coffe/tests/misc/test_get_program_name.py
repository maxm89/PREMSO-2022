# -*- coding: utf-8 -*-

"""Test for getting lowercase program name and 3-letter abbreviation."""

from __future__ import absolute_import, division, print_function


import os

from coffe.core import pkgdata
from coffe.misc import get_program_name


target_prog_1 = 'gamess'
target_abbrev_1 = 'gam'
target_prog_2 = 'psi4'
target_abbrev_2 = 'psi'


def test_get_abbreviation():
    prog = 'gamess'
    prog_abbrev = get_program_name.abbreviate(prog)
    assert target_abbrev_1 == prog_abbrev

    prog = 'psi4'
    prog_abbrev = get_program_name.abbreviate(prog)
    assert target_abbrev_2 == prog_abbrev


def test_get_program_name_user(tmpdir):
    prog, prog_abbrev = get_program_name.set_program_abbrev_user('Gamess', work_dir=str(tmpdir))
    assert target_prog_1 == prog
    assert target_abbrev_1 == prog_abbrev

    prog, prog_abbrev = get_program_name.set_program_abbrev_user('Psi4', work_dir=str(tmpdir))
    assert target_prog_2 == prog
    assert target_abbrev_2 == prog_abbrev


def test_get_program_name_guess_via_file(tmpdir):
    gamesslog = pkgdata.abspath('data/molecule-1-gam.inp.log')
    prog, prog_abbrev = get_program_name.set_program_abbrev_guess(gamesslog, work_dir=str(tmpdir))
    assert target_prog_1 == prog
    assert target_abbrev_1 == prog_abbrev

    psi4log = pkgdata.abspath('data/molecule-1-psi.inp.log')
    prog, prog_abbrev = get_program_name.set_program_abbrev_guess(psi4log, work_dir=str(tmpdir))
    assert target_prog_2 == prog
    assert target_abbrev_2 == prog_abbrev


def test_get_program_name_based_via_dirname(tmpdir):
    gamessdir = os.path.join(str(tmpdir), '00_GAMESS_Opt_QM10-10')
    psi4dir = os.path.join(str(tmpdir), '00_PSI4_Opt_QM10-10')
    os.mkdir(gamessdir)
    os.mkdir(psi4dir)
    prog, prog_abbrev = get_program_name.set_program_abbrev_guess(work_dir=gamessdir)
    assert target_prog_1 == prog

    prog, prog_abbrev = get_program_name.set_program_abbrev_guess(work_dir=psi4dir)
    assert target_prog_2 == prog
