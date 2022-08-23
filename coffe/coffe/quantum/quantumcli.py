# -*- coding: utf-8 -*-

"""Console script for coffe's quantum specific commands. cli = command line interface."""

from __future__ import absolute_import, division, print_function

import click

from coffe.quantum import extract_qm_structure
from coffe.quantum import extract_qm_energies


@click.command()
@click.option('--inputpdb', '-i',
              help='[filename.pdb | all] Name of the single input PDB file, or'
                   'use all PDB files within the working directory.',
              type=str,
              default=None)
@click.option('--charge', '-c',
              help='[-3 | -2 | -1 | 0 | 1 | 2 | 3] The molecular charge.',
              type=int,
              default=None)
@click.option('--multiplicity', '-mu',
              help='[1 | 2 | 3] The molecules multiplicity.',
              type=int,
              default=None)
@click.option('--qmtheory', '-qm1',
              help='The QM theory (defaults to QMOPT10 = HF).',
              type=str,
              default='QMOPT10')
@click.option('--basisset', '-bs',
              help='The basis set (defaults to BS10 = 6-31G(d)).',
              type=str,
              default='BS10')
@click.option('--program', '-p',
              help='[gamess | psi4] The target program (default is to guess,'
                   'which may fail).',
              type=str,
              default=None)
def create_qm_opt(inputpdb, charge, multiplicity, qmtheory, basisset, program):
    """Create quantum full optimization input files from PDB files."""
    #print(inputpdb, charge, multiplicity, qmtheory, basisset, program)
    #mk_qm_opt.create_qm_opt(inputpdb, charge, multiplicity, qmtheory, basisset, program)
    raise NotImplementedError("Functionality is not merged into master, yet.")

@click.command()
@click.option('--inputlog', '-i',
              help='Name of a fully optimized QM (gamess or psi4) logfile (e.g. molecule-1-psi.inp.log)',
              type=str,
              default='')
@click.option('--charge', '-c',
              help='[-3 | -2 | -1 | 0 | 1 | 2 | 3] The molecular charge.',
              type=int,
              default='')
@click.option('--multiplicity', '-mu',
              help='[1 | 2 | 3] The molecules multiplicity.',
              type=int,
              default='')
@click.option('--qmtheory', '-qm1',
              help='The QM theory (defaults to QMOPT10 = HF).',
              type=str,
              default='QMOPT10')
@click.option('--basisset', '-bs',
              help='The basis set (defaults to BS10 = 6-31G(d)).',
              type=str,
              default='BS10')
@click.option('--program_target', '-pt',
              help='[gamess | psi4] The target program (default is to guess, which may fail).',
              type=str,
              default='')
@click.option('--int_coord_1', '-int1',
              help='The internal coordinate (ID numbers) that will be stretch, bent or rotated (e.g. 4,6,7,10).',
              type=str,
              default='')
@click.option('--value_1', '-v1',
              help='The starting degree (e.g. 0) of internal_coord_1.',
              type=str,
              default='')
@click.option('--number_conf', '-n',
              help='The number of conformations (e.g. 3, 7 or 12) that will be made by 30 degree rotation about'
                   'internal_coord_1.',
              type=str,
              default='')
@click.option('--int_coord_2', '-int2',
              help='An internal coordinate (ID numbers) that will be constrained (e.g. 4,6,7).',
              type=str,
              default='')
@click.option('--value_2', '-v2',
              help='The value (e.g. 35.6, 123.1, 1.567) of the constrained internal_coord_2.',
              type=str,
              default='')
@click.option('--int_coord_3', '-int3',
              help='An internal coordinate (ID numbers) that will be constrained (e.g. 1,4,6).',
              type=str,
              default='')
@click.option('--value_3', '-v3',
              help='The value (e.g. 35.6, 123.1, 1.567) of the constrained internal_coord_2.',
              type=str,
              default='')
def create_qm_copt(inputlog, charge, multiplicity, qmtheory, basisset, program_source, program_target,
                   int_coord_1, value_1, number_conf_1, int_coord_2, value_2, int_coord_3, value_3):
    """Create quantum constraint optimization input files from a fully optimized QM logfile."""
    #mk_qm_copt.create_qm_copt(inputlog, charge, multiplicity, qmtheory, basisset, program_source, program_target,
    #               int_coord_1, value_1, number_conf_1, int_coord_2, value_2, int_coord_3, value_3)
    raise NotImplementedError("Functionality is not merged into master, yet.")

@click.command()
@click.option('--inputlog', '-i',
              help='[filename.log] Gamess or Psi4 log file',
              type=str,
              default='')
def log2pdb(inputlog):
    outputpdb = inputlog + ".pdb"
    extract_qm_structure.qm2pdb(inputlog, outputpdb)


@click.command()
@click.option('--inputlog', '-i',
              help='[filename.log] Gamess or Psi4 log file',
              type=str,
              default='')
def log2xyz(inputlog):
    outputxyz = inputlog + ".xyz"
    extract_qm_structure.qm2xyz(inputlog, outputxyz)


@click.command()
@click.option('--source_dir', '-sd',
              help='Directory that contains the QM log files.',
              type=str,
              default=None)
@click.option('--write_dir', '-wd',
              help='Directory that will have the energies written into.',
              type=str,
              default=None)
@click.option('--filename', '-fn',
              help='The filename for which the energies will be written to.',
              type=str,
              default=None)
@click.option('--program', '-p',
              help='[gamess | psi4] The target program (default is to guess,'
                   'which may fail).',
              type=str,
              default=None)
def get_qm_energies(source_dir, write_dir, filename, program):
    """Extract all QM raw final energies from logfiles"""
    extract_qm_energies.extract_energies_and_write(source_dir, write_dir, filename, program)
