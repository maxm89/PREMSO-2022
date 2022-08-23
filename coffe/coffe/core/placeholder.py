# -*- coding: utf-8 -*-

"""Recursive Replacement of COFFE Placeholders in file and included files.
COFFE Placeholders have the form :code:`?_name_?` or :code:?_name_value_?`.

Examples:

    You could have a script which sets the number of time steps
    and time step size in a simulation like this::

        nsteps = ?_nsteps_?
        dt = ?_dt_0.0001_?

    In this example, the time step has a default argument, while the number
    of time step HAS to be specified by the user.
"""

from __future__ import absolute_import, division, print_function

import fileinput
import os
import shutil
from coffe.core import filesys


def replace_string(filename, old, new):
    """Replace old by new in file.
    Creates a backup file filename.bak

    Args:
        filename(str): Exiting file.
        old (str): String to be replaced.
        new (str): Replacing string.

    """
    for line in fileinput.FileInput(filename, inplace=True, backup='.bak'):
        nl = line
        nl = nl.replace(old, new)
        print(nl.replace("\n",""))  # the comma supresses adding another newline statement


def replace_placeholders(filename, para_names=None, para_values=None, para_dict=None):
    """Replace placeholders in a file by values.
    Placeholders are denoted by

    Args:
        filename (str): An existing file.
        para_names (:obj:list of :obj:str): Parameter names.
        para_values (:obj:list of values): Values will be converted to strings.
        para_dict: (:obj:dict, optional): A dictionary that can be passed as an alternative
                to the lists para_names and para_values.

    Raises:
        AssertionError: If para_dict and (para_names, para_values) are not given, or both given.
                        If the filename is not a file. If the placeholders have bad format.
    """
    assert os.path.isfile(filename)
    if para_dict is None:
        assert para_names is not None, \
                "placeholder.replace_placeholders failed: "\
                "specify EITHER para_names+para_values OR para_dict"
        assert para_values is not None,\
                "placeholder.replace_placeholders failed: "\
                "specify EITHER para_names+para_values OR para_dict"
    else:
        assert para_names is None,\
                "placeholder.replace_placeholders failed: "\
                "specify EITHER para_names+para_values OR para_dict"
        assert para_values is None,\
                "placeholder.replace_placeholders failed: "\
                "specify EITHER para_names+para_values OR para_dict"
        para_names = list(para_dict.keys())
        para_values = list(para_dict.values())
    assert len(para_names) == len(para_values)
    for line in fileinput.FileInput(filename, inplace=True, backup='.bak'):
        nl = line
        if "?" in line:
            for i in range(len(para_names)):
                part1 = "?_{}_".format(para_names[i])
                if part1 in nl:
                    if part1 + "?" in nl: # format: ?_name_?
                        nl = nl.replace("?_{}_?".format(para_names[i]),
                                        "{:.15f}".format(para_values[i]))
                    else: # format: ?_name_value_?
                        tmp = nl.split(part1)[1] # tmp = value_?.....
                        assert "_?" in tmp,\
                                "coffe parameters need to have the format ?_name_?"\
                                " or ?_name_value_? Check format of parameter {} in file {}."\
                                " I got as far as extracting {}"\
                                " The line was '{}'".format(
                                    para_names[i], filename, tmp, nl)
                        value = tmp.split("_?")[0] # tmp = name_value
                        nl = nl.replace("{}{}_?".format(part1, value),
                                        "{:.15f}".format(para_values[i]))
        print(nl.replace("\n",""))  # the comma supresses adding another newline statement


def extract_include(line, basefile, comment_sep=';'):
    """Extract include from a line of a gromacs topology file.
    """
    assert "#include" in line
    bare = (line.replace("#include", "").strip().split(comment_sep)[0].
            strip().replace('"', '').replace("'", "").strip())
    directory = os.path.dirname(basefile)
    filename = os.path.abspath(os.path.join(directory, bare)) # join has no effect, when bare is absolute path
    assert os.path.isfile(filename)
    return bare, directory


def get_includes(filename, comment_sep=';', abspath=False):
    """Get the included top files from a given topology file.
    """
    assert os.path.isfile(filename)
    includes = []
    with open(filename, "r") as ff:
        for line in ff:
            if ("#include" in line) and (not line.strip().startswith(comment_sep)):
                # figure out included file
                bare, dirname = extract_include(line, filename)
                if abspath:
                    includes += [os.path.normpath(os.path.abspath(os.path.join(dirname,bare)))]
                else:
                    includes += [bare]
    return includes


def read_values(filename, para_names):
    """Read initial values given in the form ?_name_initialvalue_?

    Args:
        filename: the parameter file which contains the placeholders
        para_names: a list of parameter names

    Returns: A dict of {para_names: values}.
             If value is not specified for a parameter, the dict value is :code:`{None}`.

    """
    assert os.path.isfile(filename)
    assert isinstance(para_names, list)
    values = {p: None for p in para_names}
    with open(filename, 'r') as f:
        for nl in f:
            for p in para_names:
                part1 = "?_{}_".format(p)
                if part1 in nl:
                    if part1 + "?" in nl:  # format: ?_name_?
                        continue
                    else:  # format: ?_name_value_?
                        tmp = nl.split(part1)[1]  # tmp = value_?.....
                        assert "_?" in tmp, \
                            "coffe parameters need to have the format ?_name_?" \
                            " or ?_name_value_? Check format of parameter {} in file {}." \
                            " I got as far as extracting {}" \
                            " The line was '{}'".format(
                                p, filename, tmp, nl)
                        values[p] = float(tmp.split("_?")[0])  # tmp = name_value
    return values


def has_placeholders(filename, comment_sep=';'):
    """
    check if a given file has placeholders
    """
    assert os.path.isfile(filename)
    with open(filename, "r") as ff:
        for line in ff:
            if ("?" in line) and (not line.strip().startswith(comment_sep)):
                # get parameter
                lst = line.strip().split("?")
                for el in lst:
                    if el.startswith("_") and el.endswith("_"):
                        para = el[1:len(el) - 1]
                        assert len(para) > 0
                        return True
    return False


def get_placeholders(filename, comment_sep=';'):
    """
    extract placeholders from a given topology file
    """
    assert os.path.isfile(filename)
    parameters = []
    with open(filename, 'r') as f:
        for nl in f:
            if "?" in nl:
                tmp = nl.split(comment_sep)[0] # erase comment
                raw_para = tmp.split('?')
                for p in raw_para:
                    if p.endswith('_') and p.startswith('_'):
                        parameters += [p.split('_')[1]]
    return parameters


# =======================================================================
# ========================= RECURSIVE FUNCTIONS =========================
# =======================================================================


def get_comment_sep(mode):
    if mode == "gromacs_topology":
        return ';'
    elif mode == "charmm_stream":
        return '!'
    else:
        raise NotImplementedError("get_comment_sep does not support mode {}".format(mode))


def get_included_files_for_recursion(filename, mode="gromacs_topology", abspath=True):
    """Get a list of files that are included.

    Args:
        filename:
        mode: "gromacs_topology" (default): Use "#include" keyword for recursion
                                            and recurse into all forcefield files in directory
                                            if filename is "forcefield.itp" is included.
              "charmm_stream"             : not implemented yet
        abspath:

    Returns:

    """
    assert os.path.isfile(filename)
    result = []
    if mode == "gromacs_topology":
        if os.path.basename(filename) == "forcefield.itp":
            # get all files for force field files
            lst = os.listdir(os.path.dirname(filename))
            for f in lst:
                if os.path.basename(f) == "forcefield.itp":
                    continue
                full = os.path.normpath(os.path.abspath(os.path.join(os.path.dirname(filename), f)))
                if any(full.endswith(suff) for suff in [".top", ".itp", ".rtp", ".atp"]):
                    if abspath:
                        result += [full]
                    else:
                        result += [f]
        else:
            return get_includes(filename, comment_sep=';', abspath=abspath)
    elif mode == "charmm_stream":
        pass
    return result


def recursive_get_placeholders(filename, mode="gromacs_topology"):
    """Recursive version of get_placeholders.
    Get all placeholders in a file and included files.

    Args:
        filename (str): Root file.
        comment_sep (str): Character that introduces a comment.
        mode (str): See documentation for :meth:`~get_included_files_for_recursion`.

    Returns:
        :obj:list of :obj:str : List of placeholders.

    """
    comment_sep = get_comment_sep(mode)

    assert os.path.isfile(filename)
    placeholders = get_placeholders(filename, comment_sep)
    included = get_included_files_for_recursion(filename, mode)
    for inc in included:
        ph = recursive_get_placeholders(inc, mode)
        placeholders += ph
    return placeholders


def recursive_read_values(filename, para_names, mode="gromacs_topology"):
    """Recursive version of read_values.
    Read all parameter values like ?_name_value_? in file and included files.

    Args:
        filename (str): Root file for recursion.
        para_names (:obj:list of :obj:str): List of parameter names for which values should be read.
        mode (str): See documentation for :meth:`~get_included_files_for_recursion`.

    Returns:
        :obj:dict : Dictionary :code:`{para_name: default_value}` of default values. Parameters
                    without default values are assigned a value of None.
    """
    assert os.path.isfile(filename)
    values = read_values(filename, para_names)
    included = get_included_files_for_recursion(filename, mode)
    for inc in included:
        vals = recursive_read_values(inc, para_names, mode)
        for v in vals:
            if vals[v] is not None:
                values[v] = vals[v]
    return values


def recursive_has_placeholders(filename, mode="gromacs_topology"):
    """Check if file or any included file has placeholder.

    Args:
        filename (str): Root file for recursion.
        comment_sep (str): Character that introduces a comment.
        mode (str): See documentation for :meth:`~get_included_files_for_recursion`.

    Returns:

    """
    comment_sep = get_comment_sep(mode)
    assert os.path.isfile(filename)
    if has_placeholders(filename, comment_sep):
        return True
    included = get_included_files_for_recursion(filename, mode)
    for inc in included:
        if recursive_has_placeholders(inc, mode):
            return True
    return False


def recursive_replace_placeholders_to_new_dir(filename, target_directory,
                                              para_dict, mode="gromacs_topology"):
    """Recursively replace placeholders without overwriting the original files.
    If a file needs to be changed, it is copied to the target_directory before.

    Args:
        filename (str): Root file for recursion (read-only).
        target_directory (str): Target directory for changed files.
        para_dict (:obj:dict):  A dictionary :code:`{para_name: para_value}`
                                for the parameter values.
        mode: See documentation for :meth:`~get_included_files_for_recursion`.

    Returns:
        str: New filename (=old filename, if the file was not copied and changed).

    """

    assert filesys.is_writable(target_directory)
    if not recursive_has_placeholders(filename, mode):
        return os.path.normpath(os.path.abspath(filename))

    if os.path.basename(filename) == "forcefield.itp":
        new_dirname = os.path.join(target_directory, "ff")
        while os.path.isdir(new_dirname):
            new_dirname += "I"
        os.mkdir(new_dirname)
        new_dirname = os.path.join(new_dirname, "ff.ff")
        shutil.copytree(os.path.dirname(filename), new_dirname)
        new_fffile = os.path.join(new_dirname, "forcefield.itp")
        includes = get_included_files_for_recursion(new_fffile, mode)
        # assumption: this is a dead end; no further includes out of the forcefield directory
        for inc in includes + [new_fffile]:
            replace_placeholders(inc, para_dict=para_dict)
        return new_fffile

    else:
        new_filename = os.path.join(target_directory, os.path.basename(filename))
        while os.path.isfile(new_filename):
            new_filename += "I"
        shutil.copyfile(filename, new_filename)
        replace_placeholders(new_filename, para_dict=para_dict)

        # replace includes by absolute paths and recurse
        raw_includes = get_included_files_for_recursion(filename, mode, abspath=False)
        abs_includes = get_included_files_for_recursion(filename, mode, abspath=True)
        for raw, abs in zip(raw_includes, abs_includes):
            #replace_string(new_filename, inc, abs)
            new = recursive_replace_placeholders_to_new_dir(abs, target_directory, para_dict, mode)
            replace_string(new_filename, raw, new)
        return new_filename


def recursive_replace_with_defaults(filename, target_directory, para_dict, mode="gromacs_topology"):
    """Same as :meth:`~recursive_replace_placeholders_to_new_dir`, with the only difference
    that parameters that are not defined in para_dict are assigned their default values,
    as defined by :code:`?_paraname_defaultvalue_?`.
    """
    phs = recursive_get_placeholders(filename, mode)
    defaults = recursive_read_values(filename, phs, mode)
    defaults.update(para_dict)
    return recursive_replace_placeholders_to_new_dir(filename, target_directory, defaults, mode)
