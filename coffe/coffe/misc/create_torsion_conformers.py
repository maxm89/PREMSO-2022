# -*- coding: utf-8 -*-

"""Create pdb files that differ in their torsion conformation, using a single
pdb input file. """

from __future__ import absolute_import, division, print_function

import os
import subprocess

from coffe.core import coffedir, thirdparty
from coffe.misc import reformat_number


def degrees(increment, number_conf):
    """Create a list of angles values (degree)."""
    angles = list(range(0, int(number_conf) * int(increment), int(increment)))
    print(angles)
    return angles


def create_torsion_conformers(inputfile=None, int_coord_1=None,
                              number_conf_1=None, degree_inc_1=None,
                              int_coord_2=None, number_conf_2=None,
                              degree_inc_2=None, int_coord_3=None,
                              number_conf_3=None, degree_inc_3=None,
                              work_dir="."):
    """Creates different conformers via torsion(s) rotations.

    Returns:
        pdbs                -- A series pdb formatted files, each being a
                                different conformers

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

    Examples:
        create_torsion_conformations -i molecule.pdb -int1 1,11,8,5 -d1 30 -n1 12

        create_torsion_conformations -i molecule.pdb -int1 1,11,8,5 -d1 30 -n1 12 -int2 11,8,5,16 -d2 30 -n2 12

    Third party software required: pymol
    """
    thirdparty.PYMOL.require()

    if inputfile is None:
        raise TypeError("Must specify pdb input file (-i flag)")
    else:
        if not os.path.isfile(inputfile):
            raise IOError(inputfile + " does not exists or is set incorrectly.")
    if int_coord_1 is None:
        raise TypeError("Must specify first internal coordinate ID numbers (-int1 flag)")
    if degree_inc_1 is None:
        raise TypeError("Must specify how many degrees to rotate by (-d1 flag).")
    if number_conf_1 is None:
        raise TypeError("Must specify how many conformations to make (-n1 flag).")

    atoms_tors_1 = int_coord_1.split(',')
    angle_values_1 = degrees(degree_inc_1, number_conf_1)

    if int_coord_2 is not None:
        atoms_tors_2 = int_coord_2.split(',')
        angle_values_2 = degrees(degree_inc_2, number_conf_2)

    if int_coord_3 is not None:
        atoms_tors_3 = int_coord_3.split(',')
        angle_values_3 = degrees(degree_inc_3, number_conf_3)

    local_variables = locals()
    _work_dir, coffe_dir, logger = coffedir.prepare_coffe_work_dir(work_dir)
    logger.info("Generating pdb files that differ in torsion angle(s).\n"
                "   External program ran using: pymol -Qkqc pymolscript.pml\n"
                "   Input parameters: {}.\n".format(local_variables))

    ############################################################################

    f = open(work_dir + '/' + 'pymolscript.pml', 'w')
    f.write('set retain_order, 1\n')
    f.write('load ' + inputfile + '\n')

    index_1 = 1

    while index_1 <= number_conf_1:
        reformatted_index_1 = reformat_number.reformat_number(index_1,
                                                              number_conf_1)

        if int_coord_3:
            index_3 = 1
            while index_3 <= number_conf_3:
                index_2 = 1
                while index_2 <= number_conf_2:
                    reformatted_index_2 = reformat_number.reformat_number(
                        index_2, number_conf_2)
                    reformatted_index_3 = reformat_number.reformat_number(
                        index_3, number_conf_3)

                    # print('\033[92m', '           Creating ' + str(
                    #     reformatted_index_1) + '-' + str(
                    #     reformatted_index_2) + '-' + str(
                    #     reformatted_index_3) + '.pdb (i.e. ' +
                    #       str(angle_values_1[index_1 - 1]) + ', ' +
                    #       str(angle_values_2[index_2 - 1]) + ' and ' +
                    #       str(angle_values_3[index_3 - 1]) + ' degrees)',
                    #       '\x1b[0m')

                    f.write('set_dihedral id ' + str(
                        atoms_tors_1[0]) + ', id ' + str(atoms_tors_1[1]) +
                            ', id ' + str(atoms_tors_1[2]) + ', id ' + str(
                        atoms_tors_1[3]) + ', ' +
                            str(angle_values_1[index_1 - 1]) + '\n')
                    f.write('set_dihedral id ' + str(
                        atoms_tors_2[0]) + ', id ' + str(atoms_tors_2[1]) +
                            ', id ' + str(atoms_tors_2[2]) + ', id ' + str(
                        atoms_tors_2[3]) + ', ' +
                            str(angle_values_2[index_2 - 1]) + '\n')
                    f.write('set_dihedral id ' + str(
                        atoms_tors_3[0]) + ', id ' + str(atoms_tors_3[1]) +
                            ', id ' + str(atoms_tors_3[2]) + ', id ' + str(
                        atoms_tors_3[3]) + ', ' +
                            str(angle_values_3[index_3 - 1]) + '\n')

                    f.write('save ' + work_dir + '/' + str(
                        reformatted_index_1) + '-' + str(
                        reformatted_index_2) + '-' +
                            str(reformatted_index_3) + '.pdb\n')
                    index_2 += 1
                index_3 += 1

        elif int_coord_2:
            index_2 = 1
            while index_2 <= number_conf_2:
                reformatted_index_2 = reformat_number.reformat_number(index_2,
                                                                number_conf_2)

                # print('\033[92m', '           Creating ' + str(
                #     reformatted_index_1) + '-' + str(
                #     reformatted_index_2) + '.pdb (i.e. ' + str(
                #     angle_values_1[index_1 - 1]) + ' and ' + str(
                #     angle_values_2[index_2 - 1]) + ' degrees)', '\x1b[0m')

                f.write(
                    'set_dihedral id ' + str(atoms_tors_1[0]) + ', id ' + str(
                        atoms_tors_1[1]) + ', id ' + str(
                        atoms_tors_1[2]) + ', id ' + str(
                        atoms_tors_1[3]) + ', ' + str(
                        angle_values_1[index_1 - 1]) + '\n')
                f.write(
                    'set_dihedral id ' + str(atoms_tors_2[0]) + ', id ' + str(
                        atoms_tors_2[1]) + ', id ' + str(
                        atoms_tors_2[2]) + ', id ' + str(
                        atoms_tors_2[3]) + ', ' + str(
                        angle_values_2[index_2 - 1]) + '\n')

                f.write('save ' + work_dir + '/' + str(
                    reformatted_index_1) + '-' + str(
                    reformatted_index_2) + '.pdb\n')
                index_2 += 1

        else:
            # print('\033[92m', '           Creating ' + str(
            #     reformatted_index_1) + '.pdb (i.e. ' + str(
            #     angle_values_1[index_1 - 1]) + ' degrees)', '\x1b[0m')

            f.write('set_dihedral id ' + str(atoms_tors_1[0]) + ', id ' + str(
                atoms_tors_1[1]) + ', id ' + str(
                atoms_tors_1[2]) + ', id ' + str(atoms_tors_1[3]) + ', ' + str(
                angle_values_1[index_1 - 1]) + '\n')

            f.write(
                'save ' + work_dir + '/' + str(reformatted_index_1) + '.pdb\n')
        index_1 += 1

    f.close()

    subprocess.call(['pymol', '-Qkqc', work_dir + '/' + 'pymolscript.pml'],
                    shell=False)
