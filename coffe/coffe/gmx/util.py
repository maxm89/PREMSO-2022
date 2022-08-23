# -*- coding: utf-8 -*-

"""Utility and helper functions for Gromacs"""

from __future__ import absolute_import, division, print_function

from coffe.core.globconf import CONFIG
from coffe.core import filesys, shell, coffedir
import os
import shutil
import re
import subprocess


def gmx_parse_fatal_error(filename):
    """Extract error message from gromacs output.
    Arguments:
        file  --  a file containing gromacs' stderr output
    """
    errmsg = ""
    in_msg = False
    with open(filename, "r") as f:
        for line in f:
            if line.strip().lower().startswith("fatal"):
                in_msg = True
            if in_msg:
                errmsg += line
    return errmsg


class GromacsError(Exception):
    def __init__(self, exception, stderr_file):
        try:
            gmx_msg = gmx_parse_fatal_error(stderr_file)
            assert gmx_msg != ""
            msg = gmx_msg + ("Details in {}\n\n\n".format(stderr_file))
            super(GromacsError, self).__init__(msg)
        except Exception as e:
            super(GromacsError, self).__init__(str(exception))


def gmx_make_top(substances, n_mols, include_topologies=[], forcefield_dir=None,
                 work_dir=".", box_name="Simulation box"):
    """Make topology file.
    Returns:    Return a topology file topol.top.

    Parameters:
        substances          -- A list of molecule names.
        n_mols              -- A list of integers specifying the number of molecules for each substance.
        include_topologies  -- list of .itp files
        ff_directory        -- (Optional) Main directory of the Gromacs forcefield
        work_dir            -- The coffe working directory
        box_name            -- Name of the simulation system.
    """

    with coffedir.CoffeWorkDir(work_dir, "gmx_make_top", locals()) as cwd:
        cwd.logger.info("Making topology file.")

        # check input

        assert isinstance(n_mols, list), "n_mols must be a list of integers."
        for n in n_mols:
            assert isinstance(n, int), "n_mols must be a list of integers."
        assert isinstance(substances, list), "substances must be a list."
        assert len(substances) == len(
            n_mols), "n_mols must have the same length as substances"
        for s in substances:
            assert isinstance(s, str), "substances must be strings"
        assert isinstance(include_topologies,
                          list), "include_topologies must be list"
        _include_topologies = [filesys.make_abspath(itp, cwd.work_dir) for itp
                               in include_topologies]
        #            assert os.path.isfile(os.path.join(_forcefield_dir, "forcefield.itp")),\
        #                "ff_directory is not a forcefield (has no file forcefield.itp)"
        assert isinstance(box_name, str), "box_name must be string."

        # make top
        top_file = cwd.abspath("topol.top", check_exists=False)
        with open(top_file, 'wt') as f:
            f.write(
                "; Gromacs topology file created by coffe [gmx_make_top()]\n\n")
            if forcefield_dir is not None:
                f.write("; Force field\n")
                f.write('#include "{}"\n'.format(
                    os.path.join(forcefield_dir, "forcefield.itp")))
            f.write("; Include topologies\n")
            for itp in _include_topologies:
                f.write('#include "{}"\n\n'.format(os.path.abspath(itp)))
            f.write('[ system ]\n')
            f.write("{}\n\n".format(box_name))
            f.write('[ molecules ]\n')
            f.write('; Compound     #mols\n')
            for substance, n in zip(substances, n_mols):
                f.write('{}        {}\n'.format(substance, n))

        cwd.logger.info("Created topology file {}".format(top_file))
        return top_file


def gmx_pdb2itp(pdb_file, itp_file, ff_dir=None, gmx_ff=None, work_dir=".",
                water="none"):
    """Make an itp file (include topology) from a pdb file;
    the pdb file should contain a single non-water molecule.
    Returns: itp_file, ff_include
        itp_file    --  Resulting itp file of the molecule.
        ff_include  --  forcefield.itp file from the required forcefield

    Parameters:
        pdb_file    --  Structure file for a single molecule.
        itp_file    --  (Output) Include topology file; will be created.
        ff_dir      --  A forcefield directory (has to be the only FF directory in its parent folder).
        gmx_ff      --  The name of a Gromacs forcefield (ff_dir and gmx_ff are mutually exclusive).
        work_dir    --  Coffe working directory.
        water       --  Water model (default none).
    """
    with coffedir.CoffeWorkDir(work_dir, "gmx_pdb2itp", locals()) as cwd:

        cwd.logger.info("Creating include topology (.itp) from pdb file.")
        # check input
        _pdb_file = cwd.abspath(pdb_file)
        _itp_file = cwd.abspath(itp_file, check_exists=False)
        assert filesys.is_writable(os.path.dirname(
            _itp_file)), "directory of output .itp file is not writable"
        assert not ((gmx_ff is None) and (
            ff_dir is None)), "Either ff_dir or gmx_ff dir must be specified."
        assert ((gmx_ff is None) or (
            ff_dir is None)), "ff_dir and gmx_ff are mutually exclusive"
        ff = gmx_ff
        if ff_dir is not None:
            ff = cwd.abspath(ff_dir)
            assert os.path.isfile(os.path.join(ff,
                                               "forcefield.itp")), "Your force field does not have a forcefield.itp file."

        # Gromacs command
        posre = cwd.abspath("posre.itp", check_exists=False)
        confout = cwd.abspath("confout.gro", check_exists=False)
        top = cwd.abspath("topol.top", check_exists=False)
        cmd = "{} pdb2gmx -f {} -o {} -p {} -i {} -water {}".format(CONFIG.gmx,
                                                                    _pdb_file,
                                                                    confout,
                                                                    top, posre,
                                                                    water)
        inp = "1\n"
        wd = cwd.work_dir
        if gmx_ff is not None:
            cmd += " -ff {}".format(ff)
            inp = None
        else:
            wd = filesys.parent_dir(ff)

        try:
            cwd.call_cmd(cmd, stdin_string=inp, work_dir=wd)
        except shell.ShellError as e:
            raise GromacsError(e, cwd.last_errfile)

        ff_include = None
        ### CUT THE TOP FILE ###
        # delete last sections and replace include path by absolute path
        cwd.logger.info("Removing position restraints.")
        with open(top, 'rt') as f:
            with open(_itp_file, 'wt') as out:
                out.write("; This file was changed by coffe [gmx_pdb2itp()]")
                for line in f:
                    if line.strip().startswith("#include"):
                        # the first include is the forcefield
                        # assuming that all other includes come after '; Include Position restraint file'
                        # write absolute path
                        ff_include = line.replace("#include", "").replace('"',
                                                                          '').replace(
                            "'", "").strip()
                        if ff_dir is not None:
                            ff_include = filesys.make_abspath(ff_include, wd)
                        assert os.path.basename(ff_include) == "forcefield.itp"
                        pass
                    elif line.strip().startswith(
                            '; Include Position restraint file')\
                            or line.strip().replace(
                            ' ', '').startswith('[system]'):
                        # represents the end of the itp file
                        break
                    else:
                        # normal behavior: copy file from top to itp
                        out.write(line)

        # clean up
        try:
            os.remove(top)
            os.remove(confout)
            os.remove(posre)
        except IOError:
            pass
        cwd.logger.info("Itp file created: {}".format(itp_file))
        cwd.logger.debug("Force field include file: {}".format(ff_include))
        return itp_file, ff_include


def gmx_insert_n_molecules(initial_box, input_structure, nmol, final_box,
                           work_dir="."):
    """Randomly inserts molecules so that the final box definitely contains nmol
    molecules of a certain type. Returns the filename of the final box.

    This function iteratively calls Gromacs' function gmx insert-molecules
    until all molecules fit inside the box.

    Arguments:
    initial_box     --  Either a structure file (.gro, .pdb, ...) of the (usually empty) box,
                        or a three-dimensional vector of floats describing the box dimensions (in nm),
                        or a single float, describing the length of a cubic box (in nm)
    input_structure --  structure file (.gro, .pdb, ...) of inserted molecule
    nmol            --  number of molecules to be inserted
    final_box       --  structure file (.gro, .pdb, ...) of the box
                        that is created by this function
    log_file        --  log file to store the stderr output of gmx
    """

    with coffedir.CoffeWorkDir(work_dir, "gmx_insert_n_molecules",
                               locals()) as cwd:
        cwd.logger.info(
            "Inserting {} molecules into initial box {}.".format(nmol,
                                                                 initial_box))

        if isinstance(initial_box, float) or isinstance(initial_box, int):
            assert initial_box > 0, "Box size (initial_box) must not be zero."
            inibox = [initial_box] * 3
        elif isinstance(initial_box, list):
            assert len(
                initial_box) == 3, "Box size (initial_box) must be three-dimensional."
            for i in initial_box:
                assert isinstance(i, (int, float)), "Box size (initial_box) " \
                                                    "is no numeric vector."
            inibox = initial_box
        else:
            inibox = cwd.abspath(initial_box)
        structure = cwd.abspath(input_structure)
        assert isinstance(nmol, int), "nmol has to be an integer"

        final = cwd.abspath(final_box, check_exists=False)

        base_cmd = "{} insert-molecules -ci {} -o {}".format(CONFIG.gmx,
                                                             structure, final)
        if isinstance(inibox, list):
            cmd = base_cmd + " -nmol {} -box {} {} {}".format(nmol, *inibox)
        else:
            cmd = base_cmd + " -nmol {} -f {}".format(nmol, inibox)
        success = False
        scale = 0.57  # scaling factor for van-der-Waals radii (see gromacs doc)

        while not success:
            try:
                cwd.call_cmd(cmd)

            except shell.ShellError as e:
                raise GromacsError(e, cwd.last_errfile)

            # parse gromacs output to check how many molecules have been added
            assert os.path.isfile(cwd.last_errfile)
            line = filesys.grep_line(cwd.last_errfile, "Added")
            added = int(line.strip().split()[1])
            if added == nmol:
                success = True
            else:
                scale *= 0.8
                if isinstance(inibox, list):
                    os.remove(final)
                    cmd = "{} -scale {} -nmol {} -box {} {} {}".format(base_cmd,
                                                                       scale,
                                                                       nmol,
                                                                       *inibox)
                elif os.path.isfile(inibox):
                    nmol -= added
                    cmd = "{} -scale {} -nmol {} -f {}".format(base_cmd, scale,
                                                               nmol, final)

        assert os.path.isfile(final), "Box could not be created ({})".format(
            final)
        cwd.logger.info(
            "Box created: {}. Final vdW scaling: {}".format(final, scale))
        return final


def rename_substance_in_itp(itp_file, mol_name):
    """Rename a molecule in its itp file."""
    assert os.path.isfile(itp_file)
    bak = os.path.join(os.path.dirname(itp_file), "bak.itp")
    shutil.move(itp_file, bak)
    attention = False
    with open(bak, 'rt') as f:
        with open(itp_file, 'wt') as out:
            for line in f:
                if attention:
                    if line.startswith(';'):
                        out.write(line)
                    else:
                        nrexcl = int(line.strip().split()[1])
                        out.write("%s %i" % (mol_name, nrexcl))
                        attention = False
                else:
                    out.write(line)
                if "moleculetype" in line:
                    attention = True
    os.remove(bak)


# ======================================================== #
# ========== READING AND MANIPULATING MDP FILES ========== #
# ======================================================== #


def _option_in_line(option, line):
    """Check if the specified option is defined in the
    line of an mdp file and return its value
    """
    option = option.lower().replace("_", "-")
    line = line.lower().replace("_", "-")
    if not (option in line):
        return

    # delete comments
    no_comments = re.split('[;#]', line.strip())[0]
    if not (option in no_comments):
        return
    opt_val = re.split('[:=]', no_comments.strip())
    if not len(opt_val) == 2:
        return
    opt, val = opt_val
    if not (opt.strip() == option.strip()):
        return
    val = val.strip()
    if val == "":
        val = " "  # This is to make lines like "option = " pass  # a value with bool(value) = True
    return val


def set_mdp_options(mdp, options, new_file=None):
    """Set options in an mdp file (Gromacs configuration file).
    Note that options are case sensitive.

    Args:
        mdp (str): The file.
        options (dict): {"option": value}
        new_file (str): If specified, a copy is created
            and the original file is not touched
    """
    assert isinstance(mdp, str) and os.path.isfile(mdp)
    assert isinstance(options, dict)
    if new_file is not None:
        assert filesys.is_writable(os.path.dirname(new_file))

    # read
    with open(mdp, "r") as f:
        content = f.readlines()

    # manipulate
    for key in options:
        replaced = False
        item = "{}     =   {}  ; set by coffe\n".format(key, options[key])
        for i in range(len(content)):
            if _option_in_line(key, content[i]):
                assert not replaced, "Option {} found multiple " \
                                     "times in mdp file {}".format(key, mdp)
                content[i] = item
                replaced = True
        if not replaced:
            content += ["\n", item]

    # write
    write_to = mdp
    if new_file is not None:
        write_to = new_file
    with open(write_to, "w") as f:
        for line in content:
            f.write(line)


def read_mdp_option(mdp, key):
    """Read options from an mdp file (gromacs configuration).

    Args:
        mdp: The file.
        key: {"key": value}

    Returns:
        the key's value as a string
    """
    assert os.path.isfile(mdp)
    assert isinstance(key, str)
    result = None
    with open(mdp, "r") as f:
        for line in f:
            val = _option_in_line(key, line)
            if val is not None:
                assert result is None, "Found option {} " \
                                       "more than once in {}".format(mdp, key)
                result = val

    assert result is not None, "No option {} in mdp file {}".format(key, mdp)
    return result


def gmx_genconf(initial_structure, n_box=[1, 1, 1], dist=[0, 0, 0],
                confout="out.gro", work_dir="."):
    """Generates a copy of box and place it at a distance from the original one

    Args:
        initial_structure: initial structure that you want to copy
        n_box: number of boxes in x,y,z (default = [1,1,1])
        dist: distance between boxes (default= [0,0,0])
        confout: name of output
        work_dir: working directory (default= ".")

    Returns:
        new structure file
    """
    with coffedir.CoffeWorkDir(work_dir, "gmx_genconf", locals()) as cwd:

        assert isinstance(n_box, list) and len(
            n_box) == 3, "N_box must be three-dimensional!"
        assert isinstance(dist, list) and len(
            dist) == 3, "The distance-vector must be three-dimensional!"
        out_structure = work_dir + "/" + confout
        cmd = "gmx genconf -f {} -o {}".format(initial_structure, out_structure)
        if n_box.count(1) != 3:
            cmd += " -nbox {} {} {}".format(*n_box)
        if dist.count(0) != 3:
            cmd += " -dist {} {} {}".format(*dist)
        p = subprocess.Popen(cmd, shell=True)
        p.wait()

        assert os.path.isfile(
            out_structure), "Box could not be created ({})".format(
            out_structure)
        return out_structure


def gmx_editconf(initial_structure, box_resize=False, box_size=[0, 0, 0],
                 confout="out.gro", trans=[0, 0, 0], work_dir=".", renumber=-1):
    """Edits the input structure
    Arguments:
        initial_structure:              -- initial structure that you want to edit
        box_resize:                     -- (boolean) Resizing of the box
        box_size[x,y,z]:                -- (optional) box size (can be a float or integer or a three dimensional vector of floats or integers)
        confout:                        -- name of output
        trans [x,y,z]:                  -- (optional) translates the box along the given vector
        renumber:                       -- (optional, int) renumbers the Residues in the box
    Returns:                            returns the edited structure
    """
    with coffedir.CoffeWorkDir(work_dir, "gmx_genconf", locals()) as cwd:

        if box_resize:
            if isinstance(box_size, float) or isinstance(box_size, int):
                assert box_size > 0, "New box size must not be zero."
                new_box = [box_size] * 3
            elif isinstance(box_size, list):
                assert len(
                    box_size) == 3, "New box size must be three-dimensional."
                for i in box_size:
                    assert isinstance(i, float) or isinstance(i,
                                                              int), "New box size is no numeric vector."
                new_box = box_size
            else:
                new_box = cwd.abspath(box_size)
        assert isinstance(trans,
                          list), "Translation vector must be three-dimensional"
        assert isinstance(renumber, int), "Renumber must be an integer"

        out_structure = work_dir + "/" + confout
        cmd = "gmx editconf -f {} -o {}".format(initial_structure,
                                                out_structure)
        if trans.count(0) != 3:
            cmd += " -translate {} {} {}".format(*trans)
        if box_resize:
            cmd += " -box {} {} {}".format(*new_box)
        if renumber >= 0:
            cmd += " -resnr {}".format(renumber)
        p = subprocess.Popen(cmd, shell=True)
        p.wait()

        assert os.path.isfile(
            out_structure), "Box could not be created ({})".format(
            out_structure)
        return out_structure
