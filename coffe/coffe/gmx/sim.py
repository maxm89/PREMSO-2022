# -*- coding: utf-8 -*-

"""Classes for Gromacs calculations"""

from __future__ import absolute_import, division, print_function

import os
import shutil

from coffe.core.globconf import CONFIG

import coffe.core.coffedir
from coffe.core.decorators import args_from_configfile
from coffe.core import shell, thirdparty
from coffe.gmx import util as gmxutil


class GmxCalculation(coffe.core.coffedir.CoffeWorkDir):
    """Class for Gromacs calculations (simulations/minimizations)."""


    @coffe.core.coffedir.log_exceptions
    @args_from_configfile
    def __init__(self, structure, topology, mdp_file, work_dir=".", mdp_options={}, overwrite=False, checkpoint=None):
        """Supports :func:`~coffe.core.decorators.args_from_configfile`.
        If the structure file exists upon construction, the gromacs preprocessor (gmx grompp)
        is called upon construction. Otherwise, the preprocessor is called right before gmx mdrun.

        Args:
            structure: structure file (.gro,.pdb,...). Does not have to exist upon construction.
            topology: topology file(.top)
            mdp_file: configuration file for Gromacs (.mdp)
            work_dir: working directory (default: current working directory)
            mdp_options: a dictionary that specifies mdp options to be changed (default: {})
            overwrite: a boolean that specifies if a calculation is to be rerun, even if it was already terminated
            checkpoint: a gromacs checkpoint file to restart a simulation with given velocities

        Raises:
            AssertionError: if the input arguments do not match
            GromacsError: if something goes wrong in gromacs preprocessor
        """

        if overwrite:
            try:
                shutil.rmtree(work_dir)
            except OSError:
                pass

        super(GmxCalculation, self).__init__(work_dir, "GmxCalculation", locals())

        if overwrite:
            self.logger.info("Runs in overwrite mode: Old directory contents were removed.")
        self.logger.info("Gromacs Version: {}".format(thirdparty.gmx_version()))


        self.topology = self.abspath(topology)
        self.mdp_file = self.abspath(mdp_file)
        self.mdp_options = mdp_options
        self.structure = self.abspath(structure, check_exists=False)
        self.checkpoint = None
        if checkpoint is not None:
            self.checkpoint = self.abspath(checkpoint, check_exists=False)
            self.mdp_options["gen-vel"] = "no"
        self.terminated_file = os.path.join(self.coffe_dir, "terminated.txt")


        # apply mdp options
        if self.mdp_options != {}:
            new_mdp = os.path.join(self.work_dir, "steering.mdp")
            gmxutil.set_mdp_options(self.mdp_file, self.mdp_options, new_mdp)
            self.mdp_file = new_mdp

        # check if structure file (and checkpoint file) exist
        self.finished_grompp = False
        if self._ready_for_grompp():
            self._grompp()
            self.finished_grompp = True


    def _ready_for_grompp(self):
        """
        Prepare grompp command and copy over a checkpoint file (if required).
        If there are two competing checkpoint files (the one given in the
        constructor and a local state.cpt), take the newer one.
        Returns:
            bool: True, if is ready for grompp, False if not.

        """
        local_checkpoint = self.abspath("state.cpt", check_exists=False)
        if not os.path.isfile(self.structure):
            if os.path.basename(self.structure) == "confout.gro":
                self.logger.debug("Structure file {} does not exist. "
                                  "No grompp, yet.".format(self.structure))
            else:
                self.logger.warning("The indicated structure file {} does "
                                    "not exist and the basename "
                                    "of the structure file ( != 'confout.gro') does "
                                    "not indicate that the structure will be created "
                                    "by another Gromacs calculation.".format(self.structure))
            return False
        # structure is there; check if checkpoint is required
        if self.checkpoint is None:
            return True
        # checkpoint is required; check if exist
        if not os.path.isfile(self.checkpoint):
            self.logger.debug("Checkpoint file {} does not exist. "
                              "No grompp, yet.".format(self.structure))
            return False
        # checkpoint is there; check if there is a newer local checkpoint
        if os.path.isfile(local_checkpoint):
            if self.checkpoint == local_checkpoint:
                return True
            if (os.path.getmtime(local_checkpoint) >
                 os.path.getmtime(self.checkpoint)):
                self.logger.info("Found a checkpoint in the working directory "
                                 "that is newer than the checkpoint file provided "
                                 "to the constructor. Use the local checkpoint instead.")
                return True
            else:
                # non-local checkpoint is newer.
                # Remove local checkpoint so it does not get in the way.
                os.remove(local_checkpoint)
                return True

        # no local checkpoint
        return True

    @coffe.core.coffedir.log_exceptions
    def __call__(self):
        """Run Gromacs calculation.
        If the structure file did not exist upon construction,
        the gromacs preprocessor is called before the calculation.

        Raises:
            GromacsError: If something goes wrong in gromacs preprocessor (grompp) or calculation (mdrun).

        Returns:
            None
        """
        self.logger.info("Running calculation")
        if not self.finished_grompp:
            assert self._ready_for_grompp()
            self._grompp()
        self._mdrun()
        self.logger.info("Gmx calculation finished.")

    @coffe.core.coffedir.log_exceptions
    def _grompp(self):
        """Run Gromacs preprocessor."""
        self.logger.info("Starting Gromacs preprocessor.")
        try:
            cmd = "{} grompp -f {} -c {} -p {}".format(
                CONFIG.gmx, self.mdp_file, self.structure, self.topology)
            if self.checkpoint is not None:
                cmd += " -t {}".format(self.checkpoint)  # should be copied over at this point
            self.call_cmd(cmd)
        except shell.ShellError as e:
            raise gmxutil.GromacsError(e, self.last_errfile)

        assert os.path.isfile(os.path.join(self.work_dir, "topol.tpr")), \
            "Portable steering script 'topol.tpr' was not created by grompp."

    @coffe.core.coffedir.log_exceptions
    def _mdrun(self):
        """Run Gromacs mdrun."""
        command = CONFIG.gmx_mdrun + " -cpi state.cpt"
        try:
            self.call_cmd(command)
        except shell.ShellError as e:
            raise gmxutil.GromacsError(e, self.last_errfile)

        assert os.path.isfile(os.path.join(self.work_dir, "confout.gro")), \
            "Output file 'confout.gro' was not created by mdrun."


class GmxCalculationEarlyStopping(GmxCalculation):
    # TODO(AK) implement early stopping
    pass
