# -*- coding: utf-8 -*-

"""
A python module for checking existence, versions, ... of third-party software.

See a list of the programs used by coffe by typing::

    coffe programs

to the console.

The present module defines third-party programs as instances of
:class:`~Requirement`.
Any third-party program used by coffe should be set up as a global constant,
as follows::

    GROMACS = Requirement("Gromacs", "gmx", parse_gmx_version)

(check out the class documentation of :class:`~Requirement` for the details).
Each function or method in coffe that depends on a third-party requirement
should call the :meth:`~Requirement.require`, e.g. a function that uses
Gromacs would call::

    import thirdparty
    ...
    def gmx_function():
        thirdparty.GROMACS.require()

or (as a shortcut)::

    @thirdparty.GROMACS
    def gmx_function():
        ...

To check for a minimal version, use::

    def gmx_function():
        thirdparty.GROMACS.require(version="5.1.4")

(version checks are not available to the decorator syntax).

To invoke a unit test only if a third-party requirement is met, use::


    @pytest.mark.skipif(not thirdparty.GROMACS.exists, reason="No Gromacs.")
    def test_gmx_function():
        ...

or, to skip a whole module::

    pytestmark = pytest.mark.skipif(
        not thirdparty.GROMACS.exists,
        reason="This tests requires Gromacs"
    )



"""

from __future__ import absolute_import, division, print_function

import subprocess
import functools
import warnings

from packaging.version import Version, InvalidVersion

from coffe.core import pkgdata, graffiti

from coffe.core.globconf import CONFIG
from coffe.core import pkgdata

# ========== GENERIC PART ============

def program_exists(prog_name):
    """Checks if a program is callable."""
    assert isinstance(prog_name, str)
    p = subprocess.Popen(["which", prog_name], stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    out, err = p.communicate()
    return (p.returncode == 0) and (out != "")


class RequirementMissingError(Exception):
    """A third-party requirement is not met."""
    pass


class Requirement(object):
    """
    Checks for third-party programs that are required by some parts of coffe.
    """

    VERSION_NOT_PARSED = "Not parsed."  # !

    def __init__(self, program_name, program_cmd, program_opts="",
                 version_parser=lambda x: x, version_flag="--version"):
        """

        Args:
            program_name (str): Human-readable name of the program.
            program_cmd (str): Console command associated with the program.
            program_opts (str): Command line options for the program.
            version_parser (func): A function that takes the stdout from
                :code:`program_cmd version_flag` as a string and returns
                the version as a string.
            version_flag (str): The flag that the program uses to
                print its version.
        """
        self._program_name = program_name
        self._program_cmd = program_cmd
        self._program_opts = program_opts
        self._version_parser = version_parser
        self._version_flag = version_flag
        self._version = self._obtain_version()
        self._executable = self._obtain_executable()

    @property
    def name(self):
        """str: Program name."""
        return self._program_name

    @property
    def command(self):
        """str: Program's shell command."""
        return self._program_cmd

    @property
    def options(self):
        """str: Options to shell command"""
        return self._program_opts

    @property
    def executable(self):
        """str: Full path of the executable."""
        return self._executable

    @property
    def version(self):
        """str: Version string."""
        return self._version

    @property
    def exists(self):
        """bool: Program is installed and visible to coffe."""
        return self.version is not ""

    def _obtain_version(self):
        """Obtain the version by calling the program with the version flag.

        Returns:
            str: Version. If the program exists, but the version could not
                be parsed, return :code:`"Not parsed."` If the program does not
                exist, return an empty string.
        """
        try:
            # TODO: I'm sure we can avoid this ugly if-else, but gmx does not
            #  accept "" as an argument...
            if self._program_opts is not "":
                p = subprocess.Popen([self._program_cmd, self._program_opts,
                                      self._version_flag],
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.STDOUT)
            else:
                p = subprocess.Popen([self._program_cmd, self._version_flag],
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.STDOUT)
            out, _ = p.communicate()
            assert p.returncode == 0
            return self._version_parser(out.decode("latin-1"))
        except:  # maybe program has no --version flag
            try:
                assert program_exists(self._program_cmd)
                return Requirement.VERSION_NOT_PARSED
            except:
                return ""

    def _obtain_executable(self):
        """Obtain the executable by calling the 'which <program_cmd>'.

        Returns:
             str: The path of the program. Empty string, if not found.
        """
        try:
            p = subprocess.Popen(["which", self._program_cmd],
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT)
            out, err = p.communicate()
            assert p.returncode == 0
            return out.decode("latin-1").strip()
        except:  # executable can not be found
            return ""

    def require(self, version=None):
        """
        Is called by parts of coffe that require certain third-party
        programs.

        Args:
            version (str): Minimal version required for the
                code that calls this function.

        Raises:
            RequireThirdpartyError: If the program was not found
                or the version is too old.
        """
        if not self.exists:
            raise RequirementMissingError("{} not found.".format(
                self._program_name))
        if version is None:
            return
        if self.version == Requirement.VERSION_NOT_PARSED:
            return
        try:
            required = Version(version)
            present = Version(self.version)
            if not present >= required:
                raise RequirementMissingError(
                    "Works only for {} versions"
                    ">= {}. You are using version {}.".format(
                        self._program_name, version, self.version
                    ))
        except InvalidVersion:
            # if the version could not be interpreted,
            # assume that the requirement is satisfied
            pass

    def __call__(self, func):
        """To be used as aecorator."""

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            self.require()
            func(*args, **kwargs)

        wrapper.__wrapped__ = func  # required for python 2
        return wrapper


# ========== SPECIFIC PART ============

# GROMACS

def parse_gmx_version(stdout):
    for line in stdout.split("\n"):
        if line.strip().startswith("GROMACS version:"):
            return line.strip().replace(
                "GROMACS version:", "").replace("VERSION", "").strip()
    return Requirement.VERSION_NOT_PARSED


GROMACS = Requirement("Gromacs", "gmx", version_parser=parse_gmx_version)  #:


# AMBER

def parse_amb_version(stdout):
    for line in stdout.split("\n"):
        if line.strip().startswith("sander: Version "):
            return line.strip().replace("sander: Version ", "").replace(
                "VERSION", "").strip()
    return Requirement.VERSION_NOT_PARSED


AMBER = Requirement("Amber", "sander", version_parser=parse_amb_version)  #:

# Batch Submission Systems

TORQUE = Requirement("Torque", "qstat")  #:
SLURM = Requirement("Slurm", "squeue")  #:


# Pymol

def parse_pymol_version(stdout):
    for line in stdout.split("\n"):
        if line.strip().startswith("PyMOL"):
            return line.replace(" PyMOL(TM) Molecular Graphics System, "
                                "Version ", "").rstrip('.')
    return Requirement.VERSION_NOT_PARSED


PYMOL = Requirement("Pymol", "pymol", program_opts="-c",
                    version_parser=parse_pymol_version)  #:


# OpenBabel

def parse_babel_version(stdout):
    for line in stdout.split("\n"):
        if line.strip().startswith("Open Babel"):
            return line.replace("Open Babel", "").strip().split()[0]
    return stdout[0]


BABEL = Requirement("OpenBabel", "babel", version_parser=parse_babel_version)  #:


# ========== MISCELLANEOUS =============


def print_version_list():
    """
    Print a list of the programs, versions, and executables used by coffe.
    """
    programs = [GROMACS, AMBER, TORQUE, SLURM, PYMOL, BABEL]
    graffiti.echo("\n{:15.12} {:15.12} {:12.10} {:15.12} {}".format(
        "Program", "Command", "Status", "Version", "Excecutable"),
        graffiti.BOLD, graffiti.DARKGOLDENROD
    )
    graffiti.echo("{:15.12} {:15.12} {:12.10} {:15.12} {}".format(
        *(("-" * 12,) * 5)),
        graffiti.DARKGOLDENROD
    )
    for prog in programs:
        graffiti.echo("{:15.12} {:15.12} {:12.10} {:15.12} {}".format(
            prog.name,
            prog.command,
            "Found" if prog.exists else "Not Found",
            prog.version,
            prog.executable
        ))
    graffiti.echo("{:15.12} {:15.12} {:12.10} {:15.12} {}".format(
        *(("-" * 12,) * 5)),
        graffiti.DARKGOLDENROD
    )


def get_git_sha():
    """Return coffe git sha."""
    try:
        return subprocess.check_output(
            ["git", "describe", "--always"],
            cwd=pkgdata.abspath(".")).strip().decode("latin-1")
    except:
        return ""


# ========== DEPRECATED INTERFACE =============

# Just to support the old interface.
# In the future, use the called statements directly,
# e.g. AMBER.require()

def check_for_amb():
    """
    make sure that Sander is installed
    """
    warnings.warn("Use AMBER.require() instead.", PendingDeprecationWarning)
    AMBER.require()


def is_amb_ok():
    warnings.warn("Use AMBER.exists instead.", DeprecationWarning)
    return AMBER.exists


def amb_version():
    """
    get sander version
    """
    warnings.warn("Use AMBER.version instead.", DeprecationWarning)
    return AMBER.version


def check_for_gmx():
    """
    make sure that gromacs is installed
    """
    try:
        p = subprocess.Popen([CONFIG.gmx, "--version"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        p.communicate()
        assert p.returncode == 0
    except OSError:
        raise OSError("No Gromacs executable found.")


def is_gmx_ok():
    warnings.warn("Use GROMACS.exists instead.", DeprecationWarning)
    return GROMACS.exists


def gmx_version():
    """
    get gromacs version
    """
    check_for_gmx()
    try:
        p = subprocess.Popen([CONFIG.gmx, "--version"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        stdout, _ = p.communicate()
        assert p.returncode == 0
        for line in stdout.decode("latin-1").split("\n"):
            if line.strip().startswith("GROMACS version:"):
                return line.strip().replace("GROMACS version:","").replace("VERSION","").strip()
    except OSError:
        raise OSError("Gromacs version could not be determined.")


def check_for_torque():
    """
    make sure that qsub system exists
    """
    warnings.warn("Use TORQUE.require() instead.", DeprecationWarning)
    TORQUE.require()


def is_torque_ok():
    warnings.warn("Use TORQUE.exists instead.", DeprecationWarning)
    return TORQUE.exists


def check_for_slurm():
    """
    make sure that slurm system exists
    """
    warnings.warn("Use SLURM.require() instead.", DeprecationWarning)
    SLURM.require()


def is_slurm_ok():
    warnings.warn("Use SLURM.exists instead.", DeprecationWarning)
    return SLURM.exists


def check_for_pymol():
    """
    make sure that pymol is installed
    """
    warnings.warn("Use PYMOL.require() instead.", DeprecationWarning)
    PYMOL.require()


def is_pymol_ok():
    warnings.warn("Use PYMOL.exists instead.", DeprecationWarning)
    return PYMOL.exists


def check_for_babel():
    """
    make sure that babel is installed
    """
    warnings.warn("Use BABEL.require() instead.", DeprecationWarning)
    BABEL.require()


def is_babel_ok():
    warnings.warn("Use BABEL.exists instead.", DeprecationWarning)
    return BABEL.exists


def babel_version():
    """
    get babel version
    """
    warnings.warn("Use BABEL.version instead.", DeprecationWarning)
    return BABEL.version
