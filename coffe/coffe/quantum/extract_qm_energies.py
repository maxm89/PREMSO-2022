# -*- coding: utf-8 -*-

"""Extract raw final energies and save them to files."""

from __future__ import absolute_import, division, print_function

import collections
import csv
import glob
import os

from coffe.misc import get_program_name
import coffe.misc.util as miscutil


def grab_last_line_item(line):
    """Take a line (e.g. sentence), convert to a list, and returns the last item (i.e. the last word)."""

    line_as_list = line.split()
    last_item = line_as_list[-1]
    return last_item


def extract_amber_energies(amberlog):
    """Extract raw final energies from AMBER constraint minimizations"""

    start = 'FINAL RESULTS'
    end = 'BOND'
    lines = []
    amber_energies = []
    with open(amberlog) as input_data:
        for line in input_data:
            if line.strip() == start:
                break
        # Reads text until the end of the block:
        for line in input_data:
            if line.strip() == end:
                break
            lines.append(line.split())
    lines = [x for x in lines if x]  # remove empty lists
    amber_energies.append(lines[1][1])

    return amber_energies


def extract_gromacs_energies(gromacslog):
    """Extract raw final energies from GROMACS constraint minimizations"""

    start = 'Potential Energy  ='
    end = 'Maximum force'
    lines = []
    gromacs_energies = []
    with open(gromacslog) as input_data:
        for line in input_data:
            if line.strip() == start:
                break
        # Reads text until the end of the block:
        for line in input_data:
            if line.strip() == end:
                break
            lines.append(line.split('='))
    lines = [x for x in lines if x]
    gromacs_energies.append(lines)

    return gromacs_energies


def extract_gamess_energies(gamesslog):
    """ Extract energies from GAMESS log file.

    Requires: a list of gamess geometry optimized log files (non-errorred log files)

    Returns: a list of dictionary that contain file, energy_type and energies
        e.g., [('File', 'molecule-2-psi.inp.log'), ('HF', '-157.2968813194237043')]

    Notes:
        Currently, only coded for HF and MP2 calculations.
    """

    hftest_1 = 'TOTAL ENERGY ='
    hftest_2 = 'E(SCF)='  # needed for MP2 calculations
    mp2test_1 = 'E(MP2)='

    hf_collected_energies = collections.OrderedDict()
    mp2_1_collected_energies = collections.OrderedDict()

    file = collections.OrderedDict()

    keywords = {'HF_1': hftest_1,
                'HF_2': hftest_2,
                'MP2': mp2test_1}

    with open(gamesslog) as input_data:
        for line in input_data:
            for key, val in keywords.items():
                if val in line:
                    if key == 'MP2':
                        energy = grab_last_line_item(line)
                        mp2_1_collected_energies[key] = energy
                    if (key == 'HF_1') or (key == 'HF_2'):
                        key = 'HF'
                        energy = grab_last_line_item(line)
                        hf_collected_energies[key] = energy

    all_energies = miscutil.merge_two_ordered_dictionaries(hf_collected_energies, mp2_1_collected_energies)

    file['File'] = os.path.basename(gamesslog)
    final_dictionary = miscutil.merge_two_ordered_dictionaries(file, all_energies)

    return final_dictionary


def extract_psi4_energies(psi4log):
    """ Extract energies from Psi4 log file.

    Requires: a list of psi4 geometry optimized log files (non-errorred log files)

    Returns: a list of dictionary that contain file, energy_type and energies
        e.g., [('File', 'molecule-2-psi.inp.log'), ('HF', '-157.2968813194237043')]

    Notes:
        For MP2/CBS calculations, reported energies are
            a) HF/largest_basis_set energy
            b) MP2/largest_basis_set energy
            c) MP2/CBS energy
            (i.e. energies using the smaller basis set are not reported)"""

    hftest = 'Total Energy ='
    cbstest = 'total                  CBS'
    ccsdtest = 'CCSD total energy'
    ccsdttest = 'CCSD(T) total energy'
    mp25test = 'MP2.5 Total Energy'
    mp3test = 'MP3 Total Energy'
    dfmp2test = 'DF-MP2 Total Energy'
    oomp2test = 'DF-OMP2 Total Energy'
    mp2test_1 = '==================> DF-MP2 Energies <===================='  # Needed for runs that are ony MP2
    mp2test_2 = 'MP2 total energy:'  # Needed for CCSD(T) runs

    hf_collected_energies = collections.OrderedDict()
    mp2_1_collected_energies = collections.OrderedDict()
    mp2_2_collected_energies = collections.OrderedDict()
    mp25_collected_energies = collections.OrderedDict()
    mp3_collected_energies = collections.OrderedDict()
    dfmp2_collected_energies = collections.OrderedDict()
    ccsd_collected_energies = collections.OrderedDict()
    ccsdt_collected_energies = collections.OrderedDict()
    cbs_collected_energies = collections.OrderedDict()

    file = collections.OrderedDict()
    all_energies = collections.OrderedDict()
    final_dictionary = collections.OrderedDict()

    keywords = {'HF': hftest,
                'CBS': cbstest,
                'CCSD': ccsdtest,
                'CCSDT': ccsdttest,
                'MP25': mp25test,
                'DFMP2': dfmp2test,
                'OOMP2': oomp2test,
                'MP2': mp2test_1,
                'MP2_2': mp2test_2,
                'MP3': mp3test}

    with open(psi4log) as input_data:
        for line in input_data:
            for key, val in keywords.items():
                if val in line:
                    if key == 'CBS':
                        energy = grab_last_line_item(line)
                        cbs_collected_energies[key] = energy
                    if key == 'CCSDT':
                        energy = grab_last_line_item(line)
                        ccsdt_collected_energies[key] = energy
                    if key == 'CCSD':
                        energy = grab_last_line_item(line)
                        ccsd_collected_energies[key] = energy
                    if key == 'MP3':
                        energy = grab_last_line_item(line)
                        mp3_collected_energies[key] = energy
                    if key == 'MP25':
                        energy = grab_last_line_item(line)
                        mp25_collected_energies[key] = energy
                    if key == 'DFMP2':
                        energy = grab_last_line_item(line)
                        dfmp2_collected_energies[key] = energy
                    if key == 'MP2':
                        # Need to skip lines to get to MP2's Total Energy
                        next(input_data)
                        next(input_data)
                        next(input_data)
                        next(input_data)
                        next(input_data)
                        next(input_data)
                        target_line = next(input_data).split()
                        energy = target_line[3]
                        mp2_1_collected_energies[key] = energy
                        # collected_energies.append(energy)  # use if collecting all energies from a opt.
                    if key == 'HF':
                        energy = grab_last_line_item(line)
                        hf_collected_energies[key] = energy
                    if key == 'MP2_2':
                        key = 'MP2'
                        energy = grab_last_line_item(line)
                        mp2_2_collected_energies[key] = energy

    all_energies = miscutil.merge_two_ordered_dictionaries(hf_collected_energies, mp2_1_collected_energies)
    all_energies = miscutil.merge_two_ordered_dictionaries(all_energies, mp2_2_collected_energies)
    all_energies = miscutil.merge_two_ordered_dictionaries(all_energies, dfmp2_collected_energies)
    all_energies = miscutil.merge_two_ordered_dictionaries(all_energies, mp25_collected_energies)
    all_energies = miscutil.merge_two_ordered_dictionaries(all_energies, mp3_collected_energies)
    all_energies = miscutil.merge_two_ordered_dictionaries(all_energies, ccsd_collected_energies)
    all_energies = miscutil.merge_two_ordered_dictionaries(all_energies, ccsdt_collected_energies)
    all_energies = miscutil.merge_two_ordered_dictionaries(all_energies, cbs_collected_energies)

    file['File'] = os.path.basename(psi4log)
    final_dictionary = miscutil.merge_two_ordered_dictionaries(file, all_energies)

    return final_dictionary


def extract_energies_and_write(source_dir=None, write_dir=None, filename=None, program=None):
    """This is the main program for extracting the final energy of
    optimization runs. Note that this uses "Human Sorting" of the
    log files, via the natsort library.

    Currently, this can call the following function:
    1) extract_psi4_energies
    2) extract_gamess_energies

    Requires:
    1) a directory_target for where the log files exist (default = cwd)
    2) a write_directory for where the output csv file should be written (default = cwd)
    3) an output_file for the name of the output csv file (default = guessing from log file)
    4) the program name that created the energy (default = Energies_raw.csv)

    Returns: csv formatted output_file that contains the file names and raw energies
    """
    if source_dir is None:
        source_dir = os.getcwd()
    if write_dir is None:
        write_dir = os.getcwd()
    if filename is None:
        filename = str(write_dir) + '/Energies_raw.csv'

    qm_logs = glob.glob(source_dir + "/*.inp.log")

    try:
        qm_logs[0]
    except IndexError:
        raise Exception("There are no log files present here. Exiting")

    if program is None:
        program, progabbrev = get_program_name.set_program_abbrev_guess(qm_logs[0])
    else:
        program, progabbrev = get_program_name.set_program_abbrev_user(program)

    qm_logs_natural_sorted = miscutil.natural_sort(qm_logs)
    qm_logs = qm_logs_natural_sorted
    keynames = []

    for log in qm_logs:
        if program == 'psi4':
            energies_dict = extract_psi4_energies(log)
        elif program == 'gamess':
            energies_dict = extract_gamess_energies(log)
        energies = [energies_dict]

        with open(str(filename), 'a') as f:
            writer = csv.DictWriter(f, energies[0].keys())
            for e in energies:
                writer.writerow(e)

    for key, value in energies_dict.items():
        keynames.append(key)

    # Reverse ordering in order to properly add column headers
    with open(str(filename)) as fi, open(str(write_dir) + '/Energies_raw_2.txt', 'w') as fo:
        fo.writelines(reversed(fi.readlines()))

    # Add column headers (i.e. keys)
    with open(str(write_dir) + '/Energies_raw_2.txt', 'a') as f:
        writer = csv.writer(f)
        writer.writerow(keynames)

    # Undo the above reverse to re-obtain proper sequence.
    with open(str(write_dir) + '/Energies_raw_2.txt') as fi, open(str(filename), 'w') as fo:
        fo.writelines(reversed(fi.readlines()))

    os.remove(str(write_dir) + '/Energies_raw_2.txt')
