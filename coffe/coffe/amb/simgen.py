# -*- coding: utf-8 -*-

"""High-level simulation plan generator for Amber calculations."""

from __future__ import absolute_import, division, print_function

import os
from copy import deepcopy

import coffe.core.coffedir
from coffe.core import filesys, cmdchain, decorators
from coffe.amb import sim, util


class AmbChainGenerator(coffe.core.coffedir.CoffeWorkDir):
    """A generator for amber simulation plans."""

    @decorators.args_from_configfile
    def __init__(self, names=[], mdin_files=[], mdin_options=None, types=None,
                 root_dir="."):
        """Constructor

        Args:
            names list(str): names of individual calulations (then
                subdirectories)
            mdin_files list(str): a list of mdin files (one for each element in
                names)
            mdin_options list(dict): a list of dictionaries, where each
                dictionary specifies a set of mdin options
            types list(str): a list of amber calculation types (like
                AmbCalculation)
            root_dir (str): the root directory (for relative paths in mdin,
                structure, and topology files)
        """

        assert isinstance(mdin_files, list) and len(mdin_files) == len(names)
        assert all(isinstance(mdin, str) for mdin in mdin_files)
        assert isinstance(root_dir, str) and os.path.exists(root_dir)

        self.root_dir = os.path.abspath(root_dir)
        if mdin_options is None:
            self.mdin_options = [{} for _ in names]
        else:
            assert len(mdin_options) == len(names)
            for opt in mdin_options:
                assert isinstance(opt, dict)
            self.mdin_options = deepcopy(mdin_options)
        if types is None:
            self.types = [sim.AmbCalculation for _ in names]
        else:
            assert isinstance(types, list) and len(types) == len(names)
            self.types = deepcopy(types)

        self.names = deepcopy(names)
        self.mdin_files = [os.path.join(self.root_dir, m) for m in mdin_files]

        for n in self.names:
            assert isinstance(n, str)
        for f in self.mdin_files:
            assert os.path.isfile(f)
        for o in self.mdin_options:
            assert isinstance(o, dict)
        for t in self.types:
            assert t in [sim.AmbCalculation, sim.AmbCalculationEarlyStopping]

    def generate(self, work_dir, structure, topology, overwrite=False):
        """Generate a chain of amber simulations.

        Args:
            work_dir (str): name of working directory
            structure (str): structure file (inpcrd)
            topology (str): topology file (prmtop)
            overwrite (bool):

        Returns:
            cc (CommandChain): command chain for this simulation

        Note:
            structure and topology ARE RELATIVE TO ROOT_DIR, not WORK_DIR
        """
        initial_struc = os.path.join(self.root_dir, structure)
        top = os.path.join(self.root_dir, topology)
        assert isinstance(initial_struc, str) and os.path.isfile(initial_struc)
        assert isinstance(top, str) and os.path.isfile(top)
        cc = cmdchain.CommandChain(work_dir=work_dir)
        intermediate_struc = initial_struc
        restart=False
        for name, mdin, opt, SimType in zip(self.names, self.mdin_files,
                                            self.mdin_options, self.types):
            simulation = SimType(structure=intermediate_struc, topology=top,
                                 mdin_file=mdin,
                                 work_dir=os.path.join(cc.work_dir, name),
                                 mdin_options=opt, overwrite=overwrite,
                                 restart=restart
                                 )
            cc += [simulation]
            # Use final structure as input structure for next calculation step
            intermediate_struc = os.path.join(simulation.work_dir, "restrt")
            # If this was not a minimization run, use velocities from the
            # restart file for next calculation step
            if util.read_mdin_option(mdin, "cntrl.imin") is not 1:
                restart=True
        return cc
