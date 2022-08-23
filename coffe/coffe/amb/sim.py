# -*- coding: utf-8 -*-

"""Classes for Amber calculations"""

from __future__ import absolute_import, division, print_function

import os
import shutil

from coffe.core.globconf import CONFIG

from coffe.core import coffedir
from coffe.core import filesys
from coffe.core.decorators import args_from_configfile
from coffe.core import shell, thirdparty
from coffe.amb import util as ambutil


class AmbCalculation(coffedir.CoffeWorkDir):
    """Base class for all Amber calculations."""

    @args_from_configfile
    @coffedir.log_exceptions
    def __init__(self, structure, topology, mdin_file, work_dir=".",
                 mdin_options={}, overwrite=False, restart=False):
        """Constructor.

        Args:
            structure (str): structure file (inpcrd, restart,...). Does not
                have to exist upon construction.
            topology (str): topology file (prmtop)
            mdin_file (str): configuration file for Amber (mdin)
            work_dir (str): working directory (default: current working
                directory)
            mdin_options (list(dict)): a dictionary that specifies mdp
            options to be
                changed (default: {})
            overwrite (bool):
            restart (bool): boolean to restart a simulation with given
                velocities. Restart mdin options will be set.
        """

        if overwrite:
            try:
                shutil.rmtree(work_dir)
            except OSError:
                pass

        super(AmbCalculation, self).__init__(work_dir, "AmbCalculation",
                                             locals())

        if overwrite:
            self.logger.info("Runs in overwrite mode: Old directory contents "
                             "were removed.")
        self.logger.info(
            "Creating AmbCalculation instance with {}".format(locals()))
        self.logger.info("Sander Version: {}".format(
            thirdparty.AMBER.version))

        self.topology = self.abspath(topology)
        self.mdin_file = self.abspath(mdin_file)
        self.mdin_options = mdin_options
        self.structure = self.abspath(structure, check_exists=False)
        self.checkpoint = None
        if restart:
            self.mdin_options["cntrl.irest"] = 1
            self.mdin_options["cntrl.ntx"] = 5
        self.terminated_file = os.path.join(self.coffe_dir, "terminated.txt")

        # check if mdin file exists
        if os.path.isfile(self.mdin_file):
            self.logger.info("Mdin file {} exists.".format(mdin_file))

        # apply mdin options
        if self.mdin_options != {}:
            new_mdin = os.path.join(self.work_dir, "steering_mdin")
            ambutil.set_mdin_options(self.mdin_file, self.mdin_options,
                                     new_mdin)
            self.mdin_file = new_mdin

        # check if structure file exists
        if os.path.isfile(self.structure):
            self.logger.info("Structure file {} exists.".format(self.structure))

        else:
            if os.path.basename(self.structure) == "inpcrd" \
                    or os.path.basename(self.structure) == "restrt":
                self.logger.info("Structure file {} does not exist upon "
                                 "construction."
                                 .format(self.structure))
            else:
                self.logger.warning("The indicated structure file {} does not "
                                    "exist and the basename of the structure "
                                    "file ( != 'inpcrd', 'restrt') does not "
                                    "indicate that the structure will be "
                                    "created by another Amber calculation."
                                    .format(self.structure))

        # check if topology file exists
        if os.path.isfile(self.topology):
            self.logger.info("Topology file {} exists.".format(self.topology))

        else:
            if os.path.basename(self.topology) == "prmtop":
                self.logger.info(
                    "Topology file {} does not exist upon construction.".format(
                        self.topology))
            else:
                self.logger.warning("The indicated topology file {} does not "
                                    "exist and the basename of the topology "
                                    "file ( != 'prmtop') does not indicate "
                                    "that the structure will be created by "
                                    "another Amber calculation."
                                    .format(self.topology))

    @coffedir.log_exceptions
    def __call__(self):
        """Run Sander calculation."""
        self.logger.info("Running calculation")
        self._ambermd()
        self.logger.info("Amb calculation finished.")

    @coffedir.log_exceptions
    def _ambermd(self):
        """Run Sander executable."""
        command = CONFIG.amb_md + " -i {} -p {} -c {}"\
            .format(self.mdin_file, self.topology, self.structure)
        try:
            stdout = filesys.stdout_filename(self.coffe_dir, CONFIG.amb_md)
            stderr = filesys.stderr_filename(self.coffe_dir, CONFIG.amb_md)
            shell.call_cmd(command, stdout_file=stdout, stderr_file=stderr,
                           work_dir=self.work_dir)
        except shell.ShellError as e:
            raise ambutil.AmberError(e, stderr)

        assert os.path.isfile(os.path.join(self.work_dir, "mdout")), \
            "Output file 'mdout' was not created by sander."


class AmbCalculationEarlyStopping(AmbCalculation):
    # TODO(MS) implement early stopping
    pass
