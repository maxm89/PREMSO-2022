# -*- coding: utf-8 -*-

"""Console script for miscellaneous commands."""

from __future__ import absolute_import, division, print_function

import click
from coffe.misc import create_torsion_conformers

@click.command()
@click.option('--inputfile', '-i',
              help='Name of the input PDB file',
              type=str,
              default=None)
@click.option('--int_coord_1', '-int1',
              help="The atoms defining the internal torsion angle that will "
                   "be rotated about (e,g, 1,2,3,4).",
              type=str,
              default=None)
@click.option('--degree_inc_1', '-d1',
              help="The degree increment that int_coord_1 will be rotated "
                   "until number_conf_1 is satisfied (e.g. 30).",
              type=int,
              default=None)
@click.option('--number_conf_1', '-n1',
              help="The number of conformations to make via int_coord_1 "
                   "rotation (e.g. 3, 7, or 12).",
              type=int,
              default=None)
@click.option('--int_coord_2', '-int2',
              help="The atoms defining the second internal torsion angle that "
                   "will be rotated about (e,g, 2,3,4,5).",
              type=str,
              default=None)
@click.option('--degree_inc_2', '-d2',
              help="The degree increment that int_coord_1 will be rotated "
                   "until number_conf_2 is satisfied (e.g. 30).",
              type=int,
              default=None)
@click.option('--number_conf_2', '-n2',
              help="The number of conformations to make via int_coord_2 "
                   "rotation (e.g. 3, 7, or 12).",
              type=int,
              default=None)
@click.option('--int_coord_3', '-int3',
              help="The atoms defining the third internal torsion angle that "
                   "will be rotated about (e,g, 3,4,5,6).",
              type=str,
              default=None)
@click.option('--degree_inc_3', '-d3',
              help="The degree increment that int_coord_1 will be rotated "
                   "until number_conf_3 is satisfied (e.g. 30).",
              type=int,
              default=None)
@click.option('--number_conf_3', '-n3',
              help="The number of conformations to make via int_coord_3 "
                   "rotation (e.g. 3, 7, or 12).",
              type=int,
              default=None)
@click.option('--work_dir', '-wd',
              help="The directory to place the output pdb files.",
              type=str,
              default='.')
def create_torsion_conformations(inputfile,
                                 int_coord_1, number_conf_1, degree_inc_1,
                                 int_coord_2, number_conf_2, degree_inc_2,
                                 int_coord_3, number_conf_3, degree_inc_3,
                                 work_dir):
    """Creates different conformers via torsion rotations.

    \b
    Returns:
        pdbs                -- A series pdb formatted files, each being a
                                different conformers

    \b
    Required Arguments:
        inputfile           -- A pdb input file (preferably, a previously
                                optimized structure) (e.g. molecule.pdb).
        int_coord_1         -- The first set of internal coordinate ID numbers
                                that will be modified (e.g. 1,2,3,4)
        number_conf_1       -- The number of conformations that will be
                                generated via int_coord_1 (e.g. 7 or 12)
        degree_inc_1         -- The angle value that will be used to
                                sequentially generate the conformations of
                                int_coord_1 - needs to be a whole number
                                (e.g. 30 degrees)

    \b
    Optional Arguments:
        int_coord_2         -- The second set of internal coordinate ID numbers
                                that will be modified
        number_conf_2       -- The number of conformations that will be
                                generated via int_coord_2 (e.g. 7 or 12)
        degree_inc_2         -- The angle value that will be used to
                                sequentially generate the conformations of
                                int_coord_2 -
                                needs to be a whole number (e.g. 30 degrees)
        int_coord_3         -- The third set of internal coordinate ID numbers
                                that will be modified
        number_conf_3       -- The number of conformations that will be
                                generated via int_coord_3 (e.g. 7 or 12)
        degree_inc_3         -- The angle value that will be used to
                                sequentially generate the conformations of
                                int_coord_3 - needs to be a whole number
                                (e.g. 30 degrees)
        work_dir            -- Working directory (default=".")

    \b
    Tips:
        a. The number of conformations (i.e. number_conf_1, 2, 3) can be
            determined by dividing the total angular space that you want
            to investigate (e.g. 120, 180 or 330 degrees), divide it by
            the degree increment (e.g. degree_inc_1=30) and add 1:
            (e.g. number_conf_1 = 330/30 + 1 = 12)
        b. A 30 degree increment is usually sufficient for explore the PES.
        c. For symmetric molecules like butane, inputting number_conf_1=7
            conformations with degree_inc_1=30 degree would give you 0-180
            degrees when rotating about the C-C-C-C torsion -- the 210-330
            degrees structures would be isomers of 30-150 degrees
        d. Rotating about 3 torsions in 30 degree increments (i.e.
            degree_inc_1, 2, 3 = 30), and for 0-330 (i.e.
            number_conf_1, 2, 3 = 12) would give provide you 1728
            (i.e. 12x12x12) possible conformations.

    \b
    Examples:

        create_torsion_conformations -i molecule.pdb -int1 1,11,8,5 \\
                                     -d1 30 -n1 12

        create_torsion_conformations -i molecule.pdb -int1 1,11,8,5 \\
                                     -d1 30 -n1 12 -int2 11,8,5,16 -d2 30 -n2 12
    """

    create_torsion_conformers.create_torsion_conformers(inputfile,
                                                        int_coord_1,
                                                        number_conf_1,
                                                        degree_inc_1,
                                                        int_coord_2,
                                                        number_conf_2,
                                                        degree_inc_2,
                                                        int_coord_3,
                                                        number_conf_3,
                                                        degree_inc_3,
                                                        work_dir)
