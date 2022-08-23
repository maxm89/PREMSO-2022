# -*- coding: utf-8 -*-

""" This module calculates the RMSD between structures.
    Requires pytraj (python) from AMBER
"""

from __future__ import absolute_import, division, print_function

import os
import pandas
import pytraj

from coffe.core import coffedir


def rmsd_individual_csv(structures=[], outputfile='rmsd.csv',
                        work_dir=os.getcwd()):
    """
    Compute the RMSD between individual structures (i.e. not an MD trajectory)
    Returns: a list of RMSD values, with the first being 0.0 (i.e. reference
    structure to itself).

    Requires good structure files (e.g. a PDB or MOL2 made using babel) -- please see
    http://amber-md.github.io/pytraj/latest/read_and_write.html

    Args:
        structures (list): A list of [pdb|mol2] structures.
        outputfile (str): Output file name (default: rmsd.csv).
        work_dir (str): working directory (default: current working directory)

    Returns:
        A csv file.

    Examples: rmsd.rmsd_individual_csv(structures, outputfile)


    Raises:
        TypeError: structure arg is not a list.
        TypeError: outputfile arg is not a string.
        TypeError: work_dir arg is not a string.
        ValueError: not enough structures provided (i.e. len(structure) < 2).
        AssertionError: if one of the input molecules does not exist.
    """
    local_variables = locals()
    work_dir, coffe_dir, logger = coffedir.prepare_coffe_work_dir(work_dir)
    logger.info("Calculating RMSD and saving them to a csv file.\n"
                "   Input parameters: {}.\n".format(local_variables))

    if not isinstance(structures, list):
        raise TypeError('The provided structure argument is not a list.')
    for individual in structures:
        if not individual.lower().endswith(('.pdb', '.mol2')):
            raise TypeError('The provided structure type ( {} )is not allowed.'.format(individual))
    if not isinstance(outputfile, str):
        raise TypeError('The output file name is not a string.')
    if not isinstance(work_dir, str):
        raise TypeError('The working directory is not a string.')
    if len(structures) < 2:
        raise ValueError('You need to provide at least two input structure '
                         'files.')

    for input_molecule in structures:
        assert os.path.isfile(input_molecule), "{0} molecule doesn't exist.".format(str(input_molecule))

    outputfile = os.path.join(work_dir, outputfile)

    molecules_pytraj = pytraj.iterload(structures, structures[0])
    data_rmsd = pytraj.rmsd(molecules_pytraj, ref=molecules_pytraj[0], nofit=False)
    data_rmsd_noh = pytraj.rmsd(molecules_pytraj, ref=molecules_pytraj[0], mask='!@H=', nofit=False)

    precision = 3
    rmsd_values = pandas.DataFrame(
        {"rmsd_all": data_rmsd.round(decimals=precision), "rmsd_noH": data_rmsd_noh.round(decimals=precision)})
    rmsd_values.insert(loc=0, column='entity', value=structures)
    rmsd_values.to_csv(outputfile, header=True, index=False, index_label=structures, float_format='%.3f')
    return outputfile
