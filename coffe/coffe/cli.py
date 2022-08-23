# -*- coding: utf-8 -*-

"""Console script for coffe. cli = command line interface."""

from __future__ import absolute_import, division, print_function

import coffe
import click
import sys
import pandas

from coffe.core import globconf
from coffe.core.globconf import CONFIG
from coffe.analysis import analysiscli
from coffe.gmx import gmxcli
from coffe.quantum import quantumcli
from coffe.misc import misccli
from coffe.core import corecli
from coffe.core import saver, thirdparty, coffedir
from coffe.core.graffiti import *


# ================================
#       Root Commands
# ================================

@click.group()
@click.version_option(version=coffe.__version__)
@click.option("-v", "--verbosity", type=int, default=-50,
              help="Verbosity of coffe (-1: CRITICAL, 0: ERROR, 1: WARNING, 2: INFO [default], 3: DEBUG)")
@click.option("-c", "--color", type=int, default=-1,
              help="Color representation of console output "
                   "(-1 [default]: autodetect, according to the terminal you are using,"
                   "  0: no color,   1: 8 Colors, "
                   "  2: 16 Colors,   3: 256 Colors,   4: 24 Bit Colors). ")
def main(verbosity, color, args=None):
    """Console script for coffe."""
    # calculate verbosity
    if verbosity == -50:
        v = 20
    else:
        v = (4-verbosity)*10
    coffedir.set_global_log_level(v)
    # calculate color
    if color != -1:
        set_global_use_color(color)
    # Welcome message
    echo("\nCOFFE -- Comprehensive Optimization Force Field Environment", DARKGOLDENROD, BOLD, UNDERLINE)
    echo("Version: {}; git sha: {}".format(coffe.__version__, thirdparty.get_git_sha()), LIGHTGRAY, indent=4)
    echo("Python Version: {}".format(sys.version), LIGHTGRAY, indent=4)
    echo("When using COFFE, please cite: Leeve Kölsche Jongens & the Kid from Missouri", DARKGOLDENROD, indent=4)
    if verbosity != -50:
        echo("Verbosity set to {}".format(logging.getLevelName(v)))
    if color != -1:
        echo("Color scheme set to {}".format(color))


@main.command()
@click.argument('filename')
def run_class(filename):
    """Run an instance of a callable class that has been pickled by coffe.core.saver.save"""
    click.echo("Running instance")
    saver.load_and_run(filename)


@main.command()
@click.option('--defaults/--no-defaults', default=False,
              help="Whether or not default options should be printed.")
def config(defaults):
    """Print coffe's local configuration to the console.

    To customize the settings, create a config file named .coffe.conf
    in the local directory, any parent directory, or in your home directory.

    Config files must have one section [coffe] and accept only options
    that are specified in the defaults file. For details, type::

        coffe config --defaults

    to the console.

    If different configuration files hold conflicting options,
    coffe will always prefer the special setting (subdirectory)
    over more general settings (parent directory/home directory).
    """
    pandas.options.display.max_colwidth = 999
    pandas.options.display.width = 180
    df = CONFIG.get_sources(omit_defaults=not defaults)
    if not defaults:
        if len(df) == 0:
            print("\nCoffe is running with the default settings. "
                  "To get information on how to customize this behavior "
                  "run \n    coffe config --help.\n\n"
                  "To list the default options, type \n"
                  "    coffe config --defaults \n")
            return
        else:
            msg = ("Here is a list of the non-default settings that coffe "
                   "uses when being run in the local directory. "
                   "To also list settings that are retrieved from"
                   "the default configuration, type \n"
                   "    coffe config --defaults \n")
    else:
        msg = ("Here is a list of the settings that coffe "
               "uses when being run in the local directory: \n")
    print("\n", msg, "\n", df, "\n")

@main.command()
@click.argument('message')
@click.option('-s', '--style', default="[]", type=str,
              help="A list with styles from coffe.core.graffiti. "
                   "For example: [RED,BOLD,UNDERLINE]. Do not use spaces.")
def log(message, style):
    """Print custom logs to logfile in .coffe/log.txt.
    This program is mainly here to test coffe's --verbosity and --color arguments.
    """
    with coffedir.CoffeWorkDir(".") as cwd:
        # interpret style
        a = eval(style)
        cwd.logger.info(message, *a)


@main.command()
def programs():
    """
    Print a list of the third-party programs, versions, and
    executables that will be used by coffe.
    """
    thirdparty.print_version_list()


# ================================
#       Analysis COMMANDS
#   - defined in analysis/analysiscli.py -
# ================================

@main.group()
def analysis():
    """General analysis interface"""
    click.echo("General analysis interface.")

analysis.add_command(analysiscli.relative_energy_csv)
analysis.add_command(analysiscli.rmsd_pdb_csv)
analysis.add_command(analysiscli.compute_distance)
analysis.add_command(analysiscli.compute_angle)
analysis.add_command(analysiscli.compute_dihedral)
analysis.add_command(analysiscli.compute_conformation)

# ================================
#       GROMACS COMMANDS
#    - defined in gmx/gmxcli.py -
# ================================

@main.group()
def gmx():
    """Gromacs interface"""
    try:
        thirdparty.check_for_gmx()
    except OSError as e:
        print(e)
        sys.exit(1)
    click.echo("Gromacs interface.")
    click.echo("Gromacs version: {}".format(thirdparty.gmx_version()))


gmx.add_command(gmxcli.mkbox)
gmx.add_command(gmxcli.density_fit)


# ================================
#       QUANTUM COMMANDS
# - defined in quantum/gmxcli.py -
# ================================

@main.group()
def quantum():
    """Quantum interface to psi4 and GAMESS"""
    click.echo("Psi4 and Gamess interface.")


quantum.add_command(quantumcli.create_qm_opt)
quantum.add_command(quantumcli.get_qm_energies)
quantum.add_command(quantumcli.log2pdb)
quantum.add_command(quantumcli.log2xyz)

# ================================
#       MISC COMMANDS
#   - defined in misc/misccli.py -
# ================================


@main.group()
def misc():
    """Misc interface"""
    click.echo("Misc interface.")


misc.add_command(misccli.create_torsion_conformations)

# ================================
#       Core COMMANDS
#   - defined in analysis/corecli.py -
# ================================


@main.group()
def core():
    """Core interface"""
    click.echo("Core interface.")


core.add_command(corecli.update_cluster_status)

# ================================
#       Main Function
# ================================

if __name__ == "__main__":
    main()
