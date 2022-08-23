# -*- coding: utf-8 -*-

"""Classes for GROW optimization of FF parameters"""

from coffe.core.decorators import args_from_configfile
from coffe.grow.optimization_algorithms import OptimizationAlgorithm

from os import path

class GROWOptimization:

    @args_from_configfile
    def __init__(self, out_path, overwrite_out_path, opt_method, cfg, 
                 experiment_name=None):
        """
        Args:

        """
        
        if experiment_name:
            out_path = path.join(out_path, experiment_name)

        algo = OptimizationAlgorithm. \
            factor_optimization_algorithm(out_path=out_path, 
                                          opt_method=opt_method, 
                                          cfg=cfg,
                                          cfg_file=cfg,
                                          section="OPT")

        algo.optimize()
