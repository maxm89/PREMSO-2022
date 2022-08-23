# -*- coding: utf-8 -*-

"""Console script for coffe's gromacs specific commands. cli = command line interface."""

from __future__ import absolute_import, division, print_function

import click
import os
from coffe.gmx import boxes, observables
from six.moves import configparser


@click.command()
def run():
    click.echo("Running gmx")


@click.command()
@click.argument('config', type=click.Path(exists=True))
@click.argument('section')
@click.option('--boxtype', type=str,
              help="box type (possible values: {})".format(", ".join(boxes.ALLOWED_BOX_TYPES)))
def mkbox(config, section, boxtype):
    """Create a box from the variables given in the section of a configuration file.

    Arguments:

        config      --  Configuration file.

        section     --  Section of the configuration file

    To see the supported arguments, take a look at the examples
    or check out the functions in :role:`coffe.gmx.boxes`
    """
    if os.path.dirname(config) not in ['','.']:
        raise click.ClickException("The config file must not have a path name. "
                                   "Make sure you run the command in the directory of the config file.")
        # This error is not absolutely neccesary, but it will prevent users from creating
        # working directories in unexpected places.

    if boxtype is not None:
        assert boxtype in boxes.ALLOWED_BOX_TYPES
    click.echo("Trying to create a simulation system from section [{}] of {}".format(section,config))

    boxes.gmx_mkbox(boxtype=boxtype, cfg_file=config, section=section)

    click.echo("...done.")

@click.command()
@click.argument("traj", type = click.Path(exists=True))
@click.argument("topol", type = click.Path(exists=True))
@click.option("--n_substances", type = int, default = 1, help= "Number of substances given in the trajectory")
@click.option("--first_frame", type = int, default = 0, help= "First frame to read in trajectory")
@click.option("--last_frame", type = int, default = 0, help= "Last frame to read in trajectory" )
@click.option("--dens", type = str, default = "mass", help = "Density Type. Possible Values: mass, number, charge")
@click.option("--plot", type = bool, default = False, help = "True: Show Plot")
@click.option("--out", type = str, default = "density.xvg", help = "Output name")
@click.option("--work_dir", type = str, default = ".", help = "Working directory")
def density_fit(traj, topol, n_substances, first_frame, last_frame, dens, plot, out, work_dir):
    assert dens == "mass" or dens == number or dens == charge
    click.echo("Trying to analyze densities...")
    liquid_density, vapor_density, interface_width, z_interface_l, z_interface_r, df =\
        observables.get_densities(traj,topol,n_substances, first_frame, last_frame, dens, plot, out, work_dir)
    click.echo("...done.")
    print("Curve Fit:")
    print("Liquid Density = {} kg/m³".format(liquid_density))
    print("Vapor Density = {} kg/m³".format(vapor_density))
    print("Interface Width = {} nm".format(interface_width))
    print("Position of the left interface in z = {} nm".format(z_interface_l))
    print("Position of the right interface in z = {} nm".format(z_interface_r))
    print("Averaged Densities:")
    print(df)
