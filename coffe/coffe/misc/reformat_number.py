# -*- coding: utf-8 -*-

"""Takes a number and returns a string that has leading zeros plus the number.
How many leading zero depends on the number of digits that a second number has
(i.e. len(list)).

Works on whole integers from 1 to 9999 (i.e. not negative numbers of > 10,0000

Usage: reformat_number(number, total)

Examples:   reformat_number(2, 1) would return '2'
            reformat_number(5, 10) would return '05'
            reformat_number(10, 100) would return '010'
            reformat_number(8, 1000) would return '0008'
"""
from __future__ import absolute_import, division, print_function


#  def that sets index from 1-99 to 01-99
def reformat10(index):
    """Reformat numbers 1--99 to 01--10--99."""
    newindex = None
    if index < 10:
        newindex = "0" + str(index)
    elif 10 <= index <= 99:
        newindex = index

    return newindex


# def that sets index from 1-999 to 001-999
def reformat100(index):
    """Reformat numbers 1-999 to 001--010--999."""
    newindex = None
    if index < 10:
        newindex = "00" + str(index)
    elif 10 <= index <= 99:
        newindex = "0" + str(index)
    elif 100 <= index <= 999:
        newindex = index

    return newindex


# def that sets index from 1-9999 to 0001-9999
def reformat1000(index):
    """Reformat numbers 1-9999 to 0001--0010--0100-9999."""

    newindex = None
    if index < 10:
        newindex = "000" + str(index)
    elif 10 <= index <= 99:
        newindex = "00" + str(index)
    elif 100 <= index <= 999:
        newindex = "0" + str(index)
    elif 1000 <= index <= 9999:
        newindex = index

    return newindex


###############################################################################
# Expects to be given two numbers, and will return one
def reformat_number(index=None, total=None):
    """Based on the given total, distributes the given index number to
    reindex10, reindex100, or reindex1000 function."""

    finalindex = None
    if index < 1:
        raise TypeError("The reformatting of numbers can not be done on whole "
                        "numbers less than 1.")

    if index >= 10000:
        raise TypeError("The reformatting of numbers can not be done on whole "
                        "numbers over 9999. Once could code this ability into "
                        "reformat_number.py.")

    if 1 <= total < 10:
        finalindex = index  # do nothing
    elif 10 <= total <= 99:
        finalindex = reformat10(index)
    elif 100 <= total <= 999:
        finalindex = reformat100(index)
    elif 1000 <= total <= 9999:
        finalindex = reformat1000(index)

    return str(finalindex)
