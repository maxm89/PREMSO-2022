# -*- coding: utf-8 -*-

"""Quantum log file parser.

This module provides functions to read equilibrium structures from quantum log
files and to create pdb and xyz files from it. Gamess and Psi4 is supported.
"""

from __future__ import absolute_import, division, print_function

from coffe.core import filesys, coffedir
from coffe.misc import get_program_name
import os


def read_quantum_output_structure(logfile, program=None):
    """Function that returns the output structure of a quantum log file;

    Args:
        logfile: Quantum log file.
        program: Quantum program that created logfile. Can be detected
            automatically

    Returns:
        output: list of the lines of the log file that define the molecular
            structure.

    """
    if program is None:
        program, progabbrev = get_program_name.set_program_abbrev_guess(logfile)
    else:
        program, progabbrev = get_program_name.set_program_abbrev_user(program)

    logfile = open(logfile, "r")
    lines = logfile.readlines()
    if progabbrev == 'gam':
        lookupline = '      ***** EQUILIBRIUM GEOMETRY LOCATED *****\n'
        lookuplineindex = len(lines) - lines[-1::-1].index(lookupline) - 1
        structurestartindex = lookuplineindex + 4
    elif progabbrev == 'psi':
        lookupline = '			 OPTKING Finished Execution \n'
        lookuplineindex = len(lines) - lines[-1::-1].index(lookupline) - 1
        structurestartindex = lookuplineindex + 9
    atomlineindex = structurestartindex
    atomline = lines[atomlineindex]

    output = []
    while atomline != '\n':
        output.append(atomline.split())
        atomlineindex = atomlineindex + 1
        atomline = lines[atomlineindex]

    # Remove atom index from gamess output
    if progabbrev == 'gam':
        for row in output:
            del row[1]
    return output


def check_quantum_equilibrium(logfile, program=None):
    """Function that checks if Quantum run found an equilibrium structure.

    Function looks for the last occurence of
    "    ***** EQUILIBRIUM GEOMETRY LOCATED *****"
    in a Gamess output file or
    "			 OPTKING Finished Execution "
    in a Psi4 output file and returns the line number if found.

    Args:
        logfile: Quantum log file.
        program: Quantum program that created logfile. Can be detected
            automatically

    Returns:
        lookupline_number: Number of the line that has been found.

    """
    if program is None:
        program, progabbrev = get_program_name.set_program_abbrev_guess(logfile)
    else:
        program, progabbrev = get_program_name.set_program_abbrev_user(program)

    logfile = open(logfile, "r")
    lines = logfile.readlines()
    if progabbrev == 'gam':
        lookupline = '      ***** EQUILIBRIUM GEOMETRY LOCATED *****\n'
        lookuplineindex = len(lines) - lines[-1::-1].index(lookupline) - 1
    elif progabbrev == 'psi':
        lookupline = '			 OPTKING Finished Execution \n'
        lookuplineindex = len(lines) - lines[-1::-1].index(lookupline) - 1
    return lookuplineindex


def qm2xyz(logfile, xyz_file, work_dir=os.getcwd(), program=None):
    """Function that creates a xyz file from the output structure in a quantum
    log file;

    Args:
        logfile: Quantum log file.
        xyz_file: (Output) xyz structure file; will be created.
        work_dir: Coffe working directory.
        program: Quantum program that created logfile. Can be detected
            automatically

    Returns:
        xyz_file: Resulting xyz structure file of the molecule.

    """
    if program is None:
        program, progabbrev = get_program_name.set_program_abbrev_guess(logfile)
    else:
        program, progabbrev = get_program_name.set_program_abbrev_user(program)

    local_variables = locals()
    _work_dir, coffe_dir, logger = coffedir.prepare_coffe_work_dir(work_dir)
    logger.info(
        "Creating xyz structure file (.xyz) from quantum output file (.log).")
    logger.debug("Arguments: {}".format(local_variables))
    stdout_file = filesys.stdout_filename(coffe_dir, "qm2xyz")
    stderr_file = filesys.stdout_filename(coffe_dir, "qm2xyz")

    # ISSUE when path is not given with xyz_file - so I changed it
    # check input
    try:
        assert filesys.is_writable(os.path.dirname(_work_dir)), \
            "directory for output .xyz file is not writable (i.e. {}).".format(_work_dir)
    except Exception as e:
        logger.exception(e)
        raise e

    structure = read_quantum_output_structure(logfile)
    natoms = structure.__len__()

    with open(xyz_file, 'wt') as out:
        # first line is number of atoms
        out.write('{}\n'.format(natoms))
        # second line is a comment
        out.write("Converted from {} by coffe\n".format(logfile))
        for line in structure:
            # atom_name x_coord y_coord z_coord
            out.write("{:>3}    {:15.12f}    {:15.12f}    {:15.12f}\n"
                      .format(line[0], float(line[1]), float(line[2]),
                              float(line[3])))
    return xyz_file


def qm2pdb(logfile, pdb_file, work_dir=os.getcwd(), program=None):
    """Function that creates a pdb file from the output structure in a
    quantum log
    file;

    Args:
        logfile: Quantum log file.
        pdb_file: (Output) pdb structure file; will be created.
        work_dir: Coffe working directory.
        program: Quantum program that created logfile. Can be detected
            automatically

    Returns:
        pdb_file: Resulting pdb structure file of the molecule.

    """
    if program is None:
        program, progabbrev = get_program_name.set_program_abbrev_guess(logfile)
    else:
        program, progabbrev = get_program_name.set_program_abbrev_user(program)

    local_variables = locals()
    _work_dir, coffe_dir, logger = coffedir.prepare_coffe_work_dir(work_dir)
    logger.info(
        "Creating pdb structure file (.pdb) from Quantum output file (.log).")
    logger.debug("Arguments: {}".format(local_variables))
    stdout_file = filesys.stdout_filename(coffe_dir, "qm2pdb")
    stderr_file = filesys.stdout_filename(coffe_dir, "qm2pdb")

    # check input
    try:
        assert filesys.is_writable(os.path.dirname(_work_dir)), \
            "directory for output .xyz file is not writable (i.e. {}).".format(_work_dir)
    except Exception as e:
        logger.exception(e)
        raise e

    structure = read_quantum_output_structure(logfile)
    natoms = structure.__len__()

    with open(pdb_file, 'wt') as out:
        out.write("TITLE " + "  " + "  " + "Converted from {} by "
                                           "coffe\n".format(logfile))
        for index, line in enumerate(structure):
            # ATOM lines in pdb format
            # format is on page 191 of
            # ftp://ftp.wwpdb.org/pub/pdb/doc/format_descriptions/Format_v33_Letter.pdf
            out.write("HETATM{:>5} {:>2}{:<2} MOL     1    {:8.3f}{:8.3f}{:8.3f}"
                      "  1.00  0.00          {:>2}  \n"
                      .format(index + 1, line[0], index + 1, float(line[1]),
                              float(line[3]), float(line[2]), line[0]))
            # out.write("ATOM  {:>5} {:>2}{:<2} LIG          {:8.3f}{:8.3f}"
            #           "{:8.3f}                            {:>2}  \n"
            #           .format(index + 1, line[0], index + 1, float(line[1]),
            #                   float(line[3]), float(line[2]), line[0]))
    return pdb_file
