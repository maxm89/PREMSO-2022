# -*- coding: utf-8 -*-

"""This module computes the relative energies."""

from __future__ import absolute_import, division, print_function


import os
import pandas

from coffe.core import coffedir, constants


def relative_energies(raw_energies=[], convert='no', work_dir=os.getcwd()):
    """Compute the relative energies from a list of raw values.

    Args:
        raw_energies (:obj:list of :obj:float): Raw energies.
        convert (str): Conversion mode ('No' [default], 'hartree2kcal').

    Returns:
        (:obj:list of :obj:float): a list of relative energies, with the minimum set to zero.

    Raises:
        TypeError: if raw_energies is not a list
        TypeError: if convert is not a string
        TypeError: if work_dir is not a string
        IOError: If the provided list is empty.
        IOError: If convert argument is not valid.
    """
    local_variables = locals()
    work_dir, coffe_dir, logger = coffedir.prepare_coffe_work_dir(work_dir)
    logger.info(relative_energies.__name__ + ": Calculating relative energies.\n"
                "  Input parameters: {}.\n".format(local_variables))

    if not isinstance(raw_energies, list):
        raise TypeError('The provided argument is not a list.')
    if not isinstance(convert, str):
        raise TypeError('The value for convert is not a string.')
    if not isinstance(work_dir, str):
        raise TypeError('The value for work_dir is not a string.')

    convert = convert.lower()

    assert len(raw_energies) != 0, "The supplied raw energy list is empty."
    assert convert in ['no', 'hartree2kcal']

    float_list = [float(i) for i in raw_energies]
    minimum_e = min(float_list)

    if convert in ["no"]:
        relative_e = [e - minimum_e for e in float_list]
    elif convert in ['hartree2kcal']:
        relative_e = [(e - minimum_e) * constants.hartree2kcalmol for e in float_list]
    else:
        raise IOError("Desired energy conversion is not coded, or what you "
                      "typed is not understood.")

    return relative_e


def relative_energies_csv(inputfile='Energies_raw.csv', convert='no', outputfile='Energies_rel.csv',
                          work_dir=os.getcwd()):
    """Compute the relative energies from a file of raw values and store them to an outputfile.

    Args:
        inputfile (str): Input CSV file must have a header and the rest of the files should be
                         string,float or string,float,float.
        convert (str): Convert mode, as in :func:`~relative_energies`.
        outputfile (str): Output CSV file containing relative energies [default: work_dir/Energies_rel.csv].
        work_dir (str): Path of the coffe working directory [default: current working directory].

    Returns:
        output file: a csv formatted file.

    Raises:
        TypeError: if inputfile is not a string
        TypeError: if convert is not a string
        TypeError: if outputfile is not a string
        TypeError: if work_dir is not a string
        IOError: if convert argument is not valid.
        IOError: if inputfile is not found.
    """
    local_variables = locals()
    work_dir, coffe_dir, logger = coffedir.prepare_coffe_work_dir(work_dir)
    logger.info(relative_energies_csv.__name__ + ": Calculating relative energies and saving them to a csv file.\n"
                "   Input parameters: {}.\n".format(local_variables))

    if not isinstance(inputfile, str):
        raise TypeError('The value for inputfile is not a string.')
    if not isinstance(convert, str):
        raise TypeError('The value for convert is not a string.')
    if not isinstance(outputfile, str):
        raise TypeError('The value for outputfile is not a string.')
    if not isinstance(work_dir, str):
        raise TypeError('The value for work_dir is not a string.')

    outputfile = os.path.join(work_dir, outputfile)
    inputfile = os.path.join(work_dir, inputfile)
    assert os.path.isfile(inputfile)

    convert = convert.lower()
    assert convert in ['no', 'hartree2kcal']

    energies = pandas.read_csv(inputfile, index_col=0)
    energies -= energies.min()
    if convert == 'hartree2kcal':
        energies *= constants.hartree2kcalmol

    energies.to_csv(outputfile)
