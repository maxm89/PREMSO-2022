# -*- coding: utf-8 -*-

"""Extracts program name and its 3-letter abbreviation from
    a) user input that is passed to here,
    b) the log files within the directory,
    c) the name of the current working directory.

    Returns: the lowercase name and 3-letter abbreviation.

    ** Currently support Gamess and Psi4. **
    e.g. psi4 and psi for 00_Psi4_QM10-10 directory name
    e.g. gamess and gam for 00_Gamess_QM10-10 directory name."""

from __future__ import absolute_import, division, print_function

import os

from coffe.core import coffedir


def abbreviate(program=None):
    """Attempts to abbreviate the program that was provided as user input."""

    progabbrev = None
    program_options = ['psi4', 'gamess']

    if program in program_options:
        if program == 'psi4':
            progabbrev = 'psi'
        elif program == 'gamess':
            progabbrev = 'gam'
    else:
        raise TypeError("Specified program ({0}) is not psi4 or gamess. Exiting".format(program))
    return progabbrev


def test_program_progabbrev(program=None, progabbrev=None):
    """Test if the variables program and progabbrev have been set. If valid,
    it will return the program and its 3-letter abbreviation. If not valid,
    then it exists."""

    program_options = ['psi4', 'gamess']

    if program is None:
        raise TypeError("Program could not be detected. Please rerun and "
                        "specify program using the -p {0} option.".format(program_options))
    if progabbrev is None:
        raise TypeError("Program's abbreviation could not be set.")

    return program, progabbrev


def set_program_abbrev_guess(logfile=None, work_dir=os.getcwd()):
    """Attempts to guess the program by 1) searching the output file (i.e.
    a Gamess or Psi4 log file) if one is available, or 2) by the cwd
    name. If valid, it will return the lowercase program and its 3-letter
    abbreviation. If not valid, then it exists."""

    local_variables = locals()
    with coffedir.CoffeWorkDir(work_dir, set_program_abbrev_guess.__name__ + ": Guessing program abbreviation based on "
        "1) log file content, or 2) directory name. Input parameters: {0}\n".format(local_variables),
        locals()) as cwd:

        program = None

        if logfile is not None:
            with open(logfile) as file:
                for line in file:
                    line = line.lower()
                    if 'psi4' in line:
                        program = 'psi4'
                    if 'gamess' in line:
                        program = 'gamess'
        else:
            if 'psi' in work_dir.lower():
                program = 'psi4'
            elif 'gamess' in work_dir.lower():
                program = 'gamess'

        progabbrev = abbreviate(program)

        test_program_progabbrev(program, progabbrev)
        return program, progabbrev


def set_program_abbrev_user(userinput=None, work_dir=os.getcwd()):
    """Checks to see if the program provided by the user is valid. If valid,
    it will return the lowercase program and its 3-letter abbreviation. If
    not valid, then it exists."""

    local_variables = locals()
    with coffedir.CoffeWorkDir(work_dir, set_program_abbrev_user.__name__ + ": Determining program abbreviation based "
        "on user input. Input parameters: {0}\n".format(local_variables),
        locals()) as cwd:

        program = None

        program_options = ['psi4', 'gamess']

        if userinput:
            program = userinput.lower()
            if program in program_options:
                pass
            else:
                raise TypeError("Specified program ({0}) is not {1}. Exiting".format(program, program_options))

        progabbrev = abbreviate(program)

        test_program_progabbrev(program, progabbrev)
        return program, progabbrev
