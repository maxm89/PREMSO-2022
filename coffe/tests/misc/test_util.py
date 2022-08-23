# -*- coding: utf-8 -*-

"""Tests for coffe.misc.util functions"""

from __future__ import absolute_import, division, print_function


import collections
import glob
import os

from coffe.core import pkgdata
import coffe.misc.util as miscutil


def do_sorting(unsorted):
    temp_list = []
    for item in unsorted:
        temp_list.append(os.path.basename(item))
        unsorted = temp_list
    natural_sorted = miscutil.natural_sort(unsorted)
    return natural_sorted


def test_sort1():
    """Test 1 for naturally sorting lists."""
    directory_target = pkgdata.abspath('data/Sort_01')
    target_list = ['molecule-1-psi.inp.log', 'molecule-2-psi.inp.log',
                   'molecule-3-psi.inp.log', 'molecule-4-psi.inp.log',
                   'molecule-5-psi.inp.log', 'molecule-6-psi.inp.log',
                   'molecule-7-psi.inp.log', 'molecule-8-psi.inp.log',
                   'molecule-9-psi.inp.log', 'molecule-10-psi.inp.log',
                   'molecule-11-psi.inp.log', 'molecule-12-psi.inp.log']
    unsorted = glob.glob(directory_target + "/*.inp.log")
    natural_sorted = do_sorting(unsorted)
    assert natural_sorted == target_list


def test_sort2():
    """Test 2 for naturally sorting lists."""
    directory_target = pkgdata.abspath('data/Sort_02')
    target_list = ['molecule-01-psi.inp.log', 'molecule-02-psi.inp.log',
                   'molecule-03-psi.inp.log', 'molecule-04-psi.inp.log',
                   'molecule-05-psi.inp.log', 'molecule-06-psi.inp.log',
                   'molecule-07-psi.inp.log', 'molecule-08-psi.inp.log',
                   'molecule-09-psi.inp.log', 'molecule-10-psi.inp.log',
                   'molecule-11-psi.inp.log', 'molecule-12-psi.inp.log']
    unsorted = glob.glob(directory_target + "/*.inp.log")
    natural_sorted = do_sorting(unsorted)
    assert natural_sorted == target_list


def test_sort3():
    """Test 3 for naturally sorting lists."""
    directory_target = pkgdata.abspath('data/Sort_03')
    target_list = ['molecule-a-psi.inp.log', 'molecule-b-psi.inp.log',
                   'molecule-c-psi.inp.log', 'molecule-d-psi.inp.log']
    unsorted = glob.glob(directory_target + "/*.inp.log")
    natural_sorted = do_sorting(unsorted)
    assert natural_sorted == target_list


def test_sort4():
    """Test 4 for naturally sorting lists."""
    directory_target = pkgdata.abspath('data/Sort_04')
    target_list = ['molecule-1-psi.inp.log', 'molecule-02-psi.inp.log',
                   'molecule-3-psi.inp.log', 'molecule-4-psi.inp.log',
                   'molecule-05-psi.inp.log', 'molecule-06-psi.inp.log',
                   'molecule-7-psi.inp.log', 'molecule-08-psi.inp.log',
                   'molecule-9-psi.inp.log', 'molecule-10-psi.inp.log',
                   'molecule-11-psi.inp.log', 'molecule-12-psi.inp.log']
    unsorted = glob.glob(directory_target + "/*.inp.log")
    natural_sorted = do_sorting(unsorted)
    assert natural_sorted == target_list


def test_merge_two_ordered_dictionaries():
    """Test to merge two ordered dictionaries and obtain a single ordered one back."""
    dictionary_1 = collections.OrderedDict()
    dictionary_1['file_HF_1'] = 1.2
    dictionary_1['file_HF_2'] = 2.5
    dictionary_1['file_HF_3'] = 3.0

    dictionary_2 = collections.OrderedDict()
    dictionary_2['file_MP2_1'] = 1.4
    dictionary_2['file_MP2_4'] = 2.2
    dictionary_2['file_MP2_3'] = 3.5

    target_dictionary = collections.OrderedDict()
    target_dictionary['file_HF_1'] = 1.2
    target_dictionary['file_HF_2'] = 2.5
    target_dictionary['file_HF_3'] = 3.0
    target_dictionary['file_MP2_1'] = 1.4
    target_dictionary['file_MP2_4'] = 2.2
    target_dictionary['file_MP2_3'] = 3.5

    merged_dictionary = collections.OrderedDict()
    merged_dictionary = miscutil.merge_two_ordered_dictionaries(dictionary_1, dictionary_2)
    assert merged_dictionary == target_dictionary


def test_basename_test1():
    """Test 1 for coffe.misc.util.basename function."""
    inputname = 'supermolecule.pdb'
    target = 'supermolecule'

    basenamefile = miscutil.extract_basename_string(inputname)

    assert basenamefile == target


def test_basename_test2():
    """Test 2 for coffe.misc.util.basename function, testing string with multiple periods."""
    inputname = 'supermolecule.log.pdb'
    target = 'supermolecule'

    basenamefile = miscutil.extract_basename_string(inputname)

    assert basenamefile == target
