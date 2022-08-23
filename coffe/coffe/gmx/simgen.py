# -*- coding: utf-8 -*-

"""High-level simulation plan generator for Gromacs calculations."""

from __future__ import absolute_import, division, print_function

import coffe.core.coffedir
from coffe.core import filesys, cmdchain
from coffe.core.decorators import args_from_configfile
from coffe.gmx import sim, util
from copy import deepcopy
import os


class GmxChainGenerator(coffe.core.coffedir.CoffeWorkDir):
    """A generator for gromacs simulation plans."""

    @args_from_configfile
    def __init__(self, names=[], mdp_files=[], mdp_options=None, types=None, root_dir="."):
        """Constructor
        Arguments:
            names       -- names of individual calulations (then subdirectories)
            mdp_files   -- a list of mdp files
            mdp_options -- a list of dictionaries, where each dictionary specifies a set of mdp options
            types       -- a list of gromacs calculation types (like GmxCalculation)
            root_dir    -- the root directory (for relative paths in mdp, structure, and topology files)

        """

        assert isinstance(mdp_files, list) and len(mdp_files) == len(names)
        assert all(isinstance(mdp, str) for mdp in mdp_files)
        assert isinstance(root_dir, str) and os.path.exists(root_dir)

        self.root_dir = os.path.abspath(root_dir)
        if mdp_options is None:
            self.mdp_options = [{} for _ in names]
        else:
            assert len(mdp_options) == len(names)
            for opt in mdp_options:
                assert isinstance(opt, dict)
            self.mdp_options = deepcopy(mdp_options)
        if types is None:
            self.types = [sim.GmxCalculation for _ in names]
        else:
            assert isinstance(types, list) and len(types) == len(names)
            self.types = deepcopy(types)

        self.names = deepcopy(names)
        self.mdp_files = [os.path.join(self.root_dir, m) for m in mdp_files]

        for n in self.names:
            assert isinstance(n, str)
        for f in self.mdp_files:
            assert os.path.isfile(f)
        for o in self.mdp_options:
            assert isinstance(o, dict)
        for t in self.types:
            assert t in [sim.GmxCalculation, sim.GmxCalculationEarlyStopping]

    def generate(self, work_dir, structure, topology, overwrite=False):
        """Generate a chain of gromacs simulations.
        Arguments:


        Note: structure and topology ARE RELATIVE TO ROOT_DIR, not WORK_DIR
        Returns:
        """
        # TODO(AK) fill docstring
        initial_struc = os.path.join(self.root_dir, structure)
        top = os.path.join(self.root_dir, topology)
        assert isinstance(initial_struc, str) and os.path.isfile(initial_struc)
        assert isinstance(top, str) and os.path.isfile(top)
        cc = cmdchain.CommandChain(work_dir=work_dir)
        intermediate_struc = initial_struc
        intermediate_chkpt = None
        for name, mdp, opt, SimType in zip(self.names, self.mdp_files, self.mdp_options, self.types):
            simulation = SimType(structure=intermediate_struc, topology=top,
                                 mdp_file=mdp, work_dir=os.path.join(cc.work_dir, name),
                                 mdp_options=opt, overwrite=overwrite, checkpoint=intermediate_chkpt
                                 )
            cc += [simulation]
            intermediate_struc = os.path.join(simulation.work_dir, "confout.gro")
            # start from checkpoint
            intermediate_chkpt = None
            try:
                integrator = util.read_mdp_option(simulation.mdp_file, "integrator")
            except AssertionError:
                continue
            if integrator not in ["steep", "cg", "l-bfgs"]:
                intermediate_chkpt = os.path.join(simulation.work_dir, "state.cpt")
        return cc

