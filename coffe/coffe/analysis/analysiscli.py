# -*- coding: utf-8 -*-

"""Console script for coffe's general analysis commands."""

from __future__ import absolute_import, division, print_function

import ast
import click
import os
import pandas as pd

from coffe.analysis import relative_energies
from coffe.analysis import rmsd
from coffe.analysis import pdb_reader
from coffe.core import filesys


@click.command()
@click.option('--inputfile', '-i',
              help="Input csv file that contains one column of filenames and "
                   "column(s) of energies. Column headers should be included.",
              type=str, default='Energies_raw.csv')
@click.option('--convert', '-c',
              help="[hartree2kcal | no] Do you want to convert the numbers from"
                   "a) Hartree to kcal/mol"
                   "or not?", type=str, default='no')
@click.option('--outfilename', '-o',
              help="The output filename for which the relative energies will be"
                   "written to.", type=str, default='Energies_rel.csv')
def relative_energy_csv(inputfile, convert, outfilename):
    """Creating relative energies on a per column basis.

    Args:
        inputfile (str): [Energies_raw.csv] input file
        convert (str): [no] conversion from Hartree to kcal/mol
        outfilename (str): [Energies_rel.csv] output file
    """
    relative_energies.relative_energies_csv(inputfile, convert, outfilename)


@click.command()
@click.option('--inputfiles', '-i',
              help="""List of individual PDB files to be compared.""", type=str,
              default=None)
@click.option('--outputfile', '-o', help="Output file name (default: rmsd.csv)",
              type=str, default='rmsd.csv')
@click.option('--work_dir', '-wd', help="The work directory.", type=str,
              default=os.getcwd())
def rmsd_pdb_csv(inputfiles, outputfile, work_dir):
    """Compute the RMSD of individual PDB files.

    Args:
        inputfiles (str): pdb input file(s)
        outputfile: [rmsd.csv] output file
        work_dir: ["."] working directory

    Example:
        coffe analysis rmsd_individual_csv -i "['directory/molecule-1.pdb',
        'directory/molecule-2.pdb']" -o test.csv
    """
    # ast.literal_eval is used to parse the input string to a list
    rmsd.rmsd_individual_csv(ast.literal_eval(inputfiles), outputfile, work_dir)


@click.command()
@click.option('--name', '-n', help="[C-C] The name of the bond.", type=str,
              default='bondname')
@click.option('--atoms', '-a', help="[C1,C5] The atoms defining the distance.",
              type=str, default='')
@click.argument('inputpdb', nargs=-1, type=str)
def compute_distance(inputpdb, name, atoms):
    """Compute atom distance from pdbfile(s) using pytraj

    Args:
        inputpdb (str): pdbfile(s)
        name (str): name of the bond/distance
        atoms (str): two atomnames, separated by commas or dashes
    """
    atomlist = atoms.split(",")
    atomlist_cleaned = "-".join(atomlist)
    assert len(atomlist_cleaned.split("-")) == 2,\
        "--atoms/-a must be a string of two atomnames, e.g. C1,C5"
    click.echo("Computing {} ({}) distance from {}\n"
               .format(atomlist_cleaned, name, ', '.join(inputpdb)))
    distances = pd.DataFrame([])
    for pdbfile in inputpdb:
        distances = distances.append(
            pdb_reader.compute_geometry(pdbfile, atomlist_cleaned, name),
            ignore_index=True)
    pd.set_option('expand_frame_repr', False)
    pd.set_option('max_colwidth', 120)
    print(distances)


@click.command()
@click.option('--name', '-n', help="[alpha] The name of the angle.", type=str,
              default='anglename')
@click.option('--atoms', '-a',
              help="[C1,C5,C8] The atoms defining the angle.", type=str,
              default='')
@click.argument('inputpdb', nargs=-1, type=str)
def compute_angle(inputpdb, name, atoms):
    """Compute angle from pdbfile(s) using pytraj

    Args:
        inputpdb (str): pdbfile(s)
        name (str): name of the angle
        atoms (str): three atomnames, separated by commas or dashes
    """
    atomlist = atoms.split(",")
    atomlist_cleaned = "-".join(atomlist)
    assert len(atomlist_cleaned.split("-")) == 3,\
        "--atoms/-a must be a string of three atomnames, e.g. C1,C5,C8"
    click.echo("Computing {} ({}) angle from {}\n"
               .format(atomlist_cleaned, name, ', '.join(inputpdb)))
    angles = pd.DataFrame([])
    for pdbfile in inputpdb:
        angles = angles.append(
            pdb_reader.compute_geometry(pdbfile, atomlist_cleaned, name),
            ignore_index=True)
    pd.set_option('expand_frame_repr', False)
    pd.set_option('max_colwidth', 120)
    print(angles)


@click.command()
@click.option('--name', '-n', help="[phi] The name of the dihedral angle.",
              type=str, default='torsionname')
@click.option('--atoms', '-a',
              help="[C1,C5,C8,C11] The atoms defining the dihedral.",
              type=str, default='')
@click.argument('inputpdb', nargs=-1, type=str)
def compute_dihedral(inputpdb, name, atoms):
    """Compute dihedral from pdbfile(s) using pytraj

    Args:
        inputpdb (str): pdbfile(s)
        name (str): name of the dihedral
        atoms (str): four atomnames, separated by commas or dashes

    Returns:
    """
    atomlist = atoms.split(",")
    atomlist_cleaned = "-".join(atomlist)
    assert len(atomlist_cleaned.split("-")) == 4,\
        "--atoms/-a must be a string of four atomnames, e.g. C1,C5,C8,C11"
    click.echo("Computing {} ({}) dihedral from {}\n"
               .format(atomlist_cleaned, name, ', '.join(inputpdb)))
    dihedrals = pd.DataFrame([])
    for pdbfile in inputpdb:
        dihedrals = dihedrals.append(
            pdb_reader.compute_geometry(pdbfile, atomlist_cleaned, name),
            ignore_index=True)
    pd.set_option('expand_frame_repr', False)
    pd.set_option('max_colwidth', 120)
    print(dihedrals)


@click.command()
@click.option('--confdef', '-c',
              help="[molconf.def] The name of the file, where the "
                   "conformation is defined.", type=str, default='molconf.def')
@click.option('--confout', '-o',
              help="[molconf.out] The name of the file, where the "
                   "conformation is defined.", type=click.File('w'),
              default='molconf.out')
@click.option('--work_dir', '-wd',
              help="The directory to place the output pdb files.", type=str,
              default='.')
@click.argument('inputpdb', nargs=-1, type=str)
def compute_conformation(inputpdb, confdef, confout, work_dir):
    """Compute molecular conformations from pdbfile(s) using pytraj.
    Conformations have to be defined in the confdef file.

    Args:
        inputpdb (str): pdbfile(s)
        confdef (str): conformation definition file
        confout (str): conformation output file
        work_dir (str): working directory

    Returns:
    """

    click.echo("Computing conformation from {}\n"
               .format(', '.join(pdb for pdb in inputpdb)))
    conformations = pd.DataFrame([])
    for pdbfile in inputpdb:
        conformations = conformations.append(
            pdb_reader.compute_conformation(pdbfile, confdef),
            ignore_index=True)
    molconffile = filesys.make_abspath(
        "{}".format(os.path.basename(confout.name)), work_dir,
        check_exists=False)
    with open(molconffile, 'w') as out:
        pd.set_option('expand_frame_repr', False)
        pd.set_option('max_colwidth', 120)
        out.write(conformations.__repr__())
    pd.set_option('expand_frame_repr', False)
    pd.set_option('max_colwidth', 120)
    print(conformations)
