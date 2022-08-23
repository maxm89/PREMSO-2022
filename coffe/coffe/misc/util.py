# -*- coding: utf-8 -*-

"""Short utility programs for miscellaneous things."""

from __future__ import absolute_import, division, print_function

import collections
from natsort import natsorted
import os
from scipy.constants import *
import numpy as np


def extract_basename_string(inputstring=None):
    """
    Returns basename of a string with an extension
        (e.g. 'filename.extension' will return 'filename')
    Args:
        inputstring (str): input name of the file
    Returns:
        basefilename (str): the basename of the file, minus its extension.
    Raises:
        TypeError: inputstring arg is not a string.
    """
    if not isinstance(inputstring, str):
        raise TypeError('The input is not a string.')

    base = os.path.basename(inputstring)
    basefilename = base.split('.')
    return str(basefilename[0])


def merge_two_ordered_dictionaries(dict1, dict2):
    """
    Takes two ordered dictionaries and returns a single combined ordered dictionary.
    Note that the second dictionary values will replace the first dictionary values,
    if they share the same key.

    Args:
        dict1 (OrderedDict): first dictionary
        dict2 (OrderedDict): second dictionary
    Returns:
        dict_new (OrderedDict): the combined ordered dictionary
    Raises:
        TypeError: if the either of the input dictionaries is not an ordered dictionary.
    """
    # start with dict_1's keys and values
    # modifies dict_new with dict_2's keys and values
    # returns an ORDERED dictionary
    if not isinstance(dict1, collections.OrderedDict):
        raise TypeError('The provided argument ({}) is not a dictionary.'.format(dict1))
    if not isinstance(dict2, collections.OrderedDict):
        raise TypeError('The provided argument ({}) is not a dictionary.'.format(dict2))

    dict_new = collections.OrderedDict(dict1.copy())
    dict_new.update(dict2)
    return dict_new


def natural_sort(inputlist=[]):
    """
    Perform a 'human' natural sorting of a list.
        (The goal of this function is to make other code a bit more readable.)
        e.g. 02.inp, 1.inp, 10.inp, 3.inp, 04.inp
                      is sorted into
             1.inp, 02.inp, 3.inp, 04.inp, 10.inp
    Args:
        inputlist (list): the list to be sorted
    Returns:
        naturallist (list): human sorted list
    Raises:
        TypeError: if the either of the input dictionaries is not an ordered dictionary.
    """
    if not isinstance(inputlist, list):
        raise TypeError('The provided argument ({}) is not a list.'.format(inputlist))
    naturallist = natsorted(inputlist, key=lambda x: x.replace('.', '~'))
    return naturallist


def compute_n_mols(box_size, density, m_mol):
    """
    Computes the number of molecules needed to reach a given density in a given box with molecules of a given molar mass.

    Args:
        box_size(float or list of 3 floats): Box size in nm.
        density(list of floats): Partial densities of the substances in kg/m³.
        m_mol(float or list of floats): Molar mass in g/mol.
    Returns:
        n_mols(int or list of ints): Number of Molecules.
    Raises:
        AssertionError: If input files do not exist or do not match the criteria.
    """

    if isinstance(box_size, (int, float)):
        box_size = (box_size, box_size, box_size)
    assert all(isinstance(dim, (int, float)) for dim in box_size)\
           and all(dim > 0 for dim in box_size), "box_size elements must be " \
                                                 "positive float or int"
    assert len(box_size) == 3, "box_size must contain one or three floats"
    if isinstance(density, (int, float)):
        density = [density]
    if isinstance(m_mol, (int, float)):
        m_mol = [m_mol]
    if len(density) is not len(m_mol):
        raise ValueError("density and m_mol must be of the same size.")
    assert all(isinstance(dens, (int, float)) and dens > 0 for dens in
               density), "all densities must be float > 0"
    assert all(isinstance(m, (int, float)) and m > 0 for m in
               m_mol), "all m_mol must be float > 0"
    vol = box_size[0]* nano * box_size[1] * nano * box_size[2] * nano
    n_mols = [int(dens * kilo * vol * N_A / m) for dens, m in zip(
        density,m_mol)]
    return n_mols


def compute_box_size(n_mols, density, m_mol):
    """
    Computes the box size needed do reach a given density with a given number of molecules and a given molar mass.

    Args:
        n_mols(int or list of ints): Number of Molecules.
        density(float or list of floats): Density of the substances in kg/m³.
        m_mol(float or list of floats): Molar mass in g/mol.
    Returns:
        box_size(float): Box size in nm.
        n_mols(None or list of ints): Number of molecules if a total amount of all molecules was given.

    Raises:
        AssertionError: If input files do not exist or do not match the criteria.
    """

    if isinstance(n_mols, (int)):
        n_mols = [n_mols]
    assert isinstance(n_mols, (list)), "n_mols must be int or list of int > 0"
    for item in n_mols:
        assert isinstance(item, int) and item > 0, "n_mols must be int or list of int > 0"
    if isinstance(density, (int, float)):
        density = [density]
    assert isinstance(density, (list)), "density must be float or int or list of float or int > 0"
    for item in density:
        assert isinstance(item, (int, float)) and item > 0, "density must be float or int or list of float or int > 0"
    if isinstance(m_mol, (int, float)):
        m_mol = [m_mol]
    assert isinstance(m_mol, (list)), "m_mol must be float or int or list of float or int > 0"
    for item in m_mol:
        assert isinstance(item, (int, float)) and item > 0, "m_mol must be float or int or list of float or int > 0"
    if len(density) > 1 and len(n_mols) > 1:
        raise ValueError("Too much input arguments. Only one density or one n_mols is permitted")
    if len(density) > 1:
        rho_m = np.divide(density, m_mol)
        n = np.around(n_mols * (rho_m / np.sum(rho_m)), 0)
        box_size = np.power(np.divide(np.multiply(n, m_mol) * milli, np.multiply(density, N_A)), 1/3) / nano
        return box_size[0], [int(element) for element in n]
    else:
        vol = 0
        for n, m in zip(n_mols, m_mol):
            vol += n * m * milli / (density[0] * N_A)
        box_size = vol ** (1./3.) / nano
        return box_size, None

def compute_density(box_size, n_mols, m_mol):
    """
    Computes the number of molecules needed to reach a given density in a given box with molecules of a given molar mass.

    Args:
        box_size(float or list of 3 floats): Box size in nm.
        n_mols(int or list of ints): Number of Molecules.
        m_mol(float or list of floats): Molar mass in g/mol.
    Returns:
        density(list of floats): Partial densities of the substances in kg/m³.
    Raises:
        AssertionError: If input files do not exist or do not match the criteria.
    """

    if isinstance(box_size, (int, float)):
        box_size = (box_size, box_size, box_size)
    assert all(isinstance(dim, (int, float)) for dim in box_size)\
           and all(dim > 0 for dim in box_size), "box_size elements must be " \
                                                 "positive float or int"
    assert len(box_size) == 3, "box_size must contain one or three floats"
    if isinstance(n_mols, (int)):
        n_mols = [n_mols]
    if isinstance(m_mol, (int, float)):
        m_mol = [m_mol]
    if len(n_mols) is not len(m_mol):
        raise ValueError("n_mols and m_mol must be of the same size.")
    assert all(isinstance(mols, int) and mols > 0 for mols in
               n_mols), "all n_mols must be int > 0"
    assert all(isinstance(m, (int, float)) and m > 0 for m in
               m_mol), "all m_mol must be float > 0"
    vol = box_size[0]* nano * box_size[1] * nano * box_size[2] * nano
    density = [float(mols * (m / N_A) * milli / vol) for mols, m in zip(
        n_mols, m_mol)]
    return density
