# -*- coding: utf-8 -*-

"""Pdb file parser.

This module provides functions to read from pdb files
"""

from __future__ import absolute_import, division, print_function

from coffe.core import coffedir

import pytraj as pt
import os
import pandas as pd


def read_pdb_structure(pdbfile):
    """Function that returns the output structure of a Gamess log file;

    Args:
        pdbfile (str):  Structure file in pdb format

    Returns:
        output (list):  list of the lines of the log file that define the
                        molecular structure.

    """
    output = []
    pdbfile.seek(0)
    for line in pdbfile.readlines():
        if line[0:6] == "ATOM  ":
            atomline = [line[13:16], line[31:38], line[39:46], line[47:54]]
            atomline = [x.strip() for x in atomline]
            output.append(atomline)
    return output


def are_pdbs_equal(pdb1, pdb2, tol=0.0010000001):
    """Check if coordinates in pdb files are equal.

    Args:
        pdb1 (str):     Filename of first pdb file.
        pdb2 (str):     Filename of second pdb file.
        tol (float):    Tolerance for coordinate comparison
                        [default=0.0010000001].

    Returns:
        bool:           True, if coordinates are equal up to tolerance.
    """
    assert os.path.isfile(pdb1)
    assert os.path.isfile(pdb2)
    with open(pdb1, "r") as f1:
        coord1 = {name: [float(x), float(y), float(z)] for name, x, y, z in
                  read_pdb_structure(f1)}
    with open(pdb2, "r") as f2:
        coord2 = {name: [float(x), float(y), float(z)] for name, x, y, z in
                  read_pdb_structure(f2)}
    if coord1.keys() != coord2.keys():
        return False
    for k in coord1:
        for i in range(3):
            if abs(coord1[k][i] - coord2[k][i]) > tol:
                return False
    return True


def compute_geometry(pdbfile, atomlist, name="none", work_dir="."):
    """

    Args:
        pdbfile (str):      pdbfile of the molecule
        atomlist (str):     List of atoms that define the bond, angle or
                            dihedral, separated by commas or dashes,
                            i.e. C1-C5-C8-C11
        name (str):         name of the geometric parameter, i.e. phi,
                            C-C-bond, ...
        work_dir (str):     working directory

    Returns:
        thisgeom (list):    geometry as list of pdb file name, parameter name,
                            atoms, parameter type, parameter value, conformation

    """
    with coffedir.CoffeWorkDir(work_dir, "Computing geometry", locals()) as cwd:
        _pdbfile = cwd.abspath(str(pdbfile))
        _geomdatafile = cwd.abspath(str(pdbfile)) + ".geom"

        # Clean atomlist by replacing commas with dashes
        atomlist_cleaned = atomlist.replace(",", "-").replace("\n", "")
        atoms = atomlist_cleaned.split("-")

        # Get type of geometric observable form number of atoms
        natoms = len(atoms)
        geomtype = None
        conformation = "-"
        assert natoms > 1
        assert natoms < 5
        if natoms == 2:
            geomtype = "bond"
            value = compute_distance(_pdbfile, atoms)
        elif natoms == 3:
            geomtype = "angle"
            value = compute_angle(_pdbfile, atoms)
        elif natoms == 4:
            geomtype = "dihedral"
            value = compute_dihedral(_pdbfile, atoms)
            conformation = compute_dihedral_conformation(value)

        # Prepare Pandas DataFrame and file
        thisgeom = pd.DataFrame(
            columns=("file", "name", "atoms", "type", "value", "conf"),
            data=[[_pdbfile, name, atomlist_cleaned,
                   geomtype, value, conformation]],
            dtype=float
        )

        # Keep existing data
        if os.path.isfile(_geomdatafile):
            geomdata = pd.read_csv(_geomdatafile, delim_whitespace=True)
            geomdata = geomdata.append(thisgeom)
        else:
            geomdata = thisgeom

        # Clean up data
        geomdata = geomdata.drop_duplicates().sort_values(
            by=['type', 'name']).reset_index(drop=True)

        # Write to file
        with open(_geomdatafile, 'w') as out:
            pd.set_option('expand_frame_repr', False)
            pd.set_option('max_colwidth', 120)
            out.write(geomdata.__repr__())
        return thisgeom


def compute_distance(pdbfile, atoms):
    """

    Args:
        pdbfile (str):  pdbfile of the molecule
        atoms (str):    list of two atoms that define the distance, e.g. [C1,C5]

    Returns:
        distance (str): distance of the two atoms

    """
    traj = pt.iterload(pdbfile)
    distance = pt.distance(traj, ':1@{} :1@{}'.format(atoms[0], atoms[1]))[0]
    return distance


def compute_angle(pdbfile, atoms):
    """

    Args:
        pdbfile (str):  pdbfile of the molecule
        atoms (str):    list of three atoms that define the angle,
                        e.g. [C1,C5,C8]

    Returns:
        angle (float):  angle in degrees

    """
    traj = pt.iterload(pdbfile)
    angle = pt.angle(traj, ':1@{} :1@{} :1@{}'
                     .format(atoms[0], atoms[1], atoms[2]))[0]
    return angle


def compute_dihedral(pdbfile, atoms):
    """

    Args:
        pdbfile (str):      pdbfile of the molecule
        atoms (str):        list of four atoms that define the dihedral,
                            e.g. [C1,C5,C8,C11]

    Returns:
        dihedral (float):   dihedral in degrees

    """
    traj = pt.iterload(pdbfile)
    dihedral = pt.dihedral(traj, ':1@{} :1@{} :1@{} :1@{}'
                           .format(atoms[0], atoms[1], atoms[2], atoms[3]))[0]
    return dihedral


def compute_dihedral_conformation(value):
    """

    Args:
        value (float):  A torsion value in degrees

    Returns:
        conf (str):     conformation of the dihedral, C[is], G[auche]+,
                        G[auche]-, A[nti]+, A[nti]-, T[rans]

    """
    conf = ""
    if -30 < value < 30:
        conf = "C"
    elif 30 <= value <= 90:
        conf = "G+"
    elif -90 <= value <= -30:
        conf = "G-"
    elif 90 < value < 150:
        conf = "A+"
    elif -150 < value < -90:
        conf = "A-"
    elif -210 <= value <= -150 or 150 <= value <= 210:
        conf = "T"
    return conf


def compute_conformation(pdbfile, confdeffile, work_dir="."):
    """

    Args:
        pdbfile (str):      pdbfile of the molecule
        confdeffile (str):  file with molecular conformation definition
        work_dir (str):     working directory

    Returns:
        conformation (str): conformation of the molecule, e.g. TTG+

    """
    with coffedir.CoffeWorkDir(work_dir, "Computing geometry", locals()) as cwd:
        _pdbfile = cwd.abspath(str(pdbfile))
        _confdeffile = cwd.abspath(confdeffile)
        molconffile = cwd.abspath("{}.molconf".format(
            os.path.basename(_pdbfile)), check_exists=False)
        conformation = ""
        with open(_confdeffile, 'rt') as f:
            for line in f:
                name = line.split(' ')[0]
                atomlist = line.strip().split(' ')[1].split(",")
                atoms = "-".join(atomlist)
                geom = compute_geometry(_pdbfile, atoms, name,
                                        work_dir=work_dir)
                conformation = conformation + geom['conf'][0]
            conformation = pd.DataFrame(columns=("file", "conf"),
                                        data=[[_pdbfile, conformation]],
                                        dtype=float
                                        )
        if os.path.isfile(molconffile):
            conf = pd.read_csv(molconffile, delim_whitespace=True)
            conf = conf.append(conformation)
        else:
            conf = conformation
        with open(molconffile, 'w') as out:
            pd.set_option('expand_frame_repr', False)
            pd.set_option('max_colwidth', 120)
            out.write(conf.__repr__())
        return conformation
