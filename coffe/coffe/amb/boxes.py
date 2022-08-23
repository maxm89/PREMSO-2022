# -*- coding: utf-8 -*-

"""Tools for setting up simulation boxes in Amber"""

from __future__ import absolute_import, division, print_function
from coffe.core.decorators import args_from_configfile
import coffe.amb.util as ambutil
from coffe.core import filesys

import os


# @args_from_configfile
# def amb_mkbox_homogeneous(substance, n_mols, box_size, ff_dir=None, amb_ff=None,
#                           create_itp=True, include_topology=None, work_dir=".",
#                           substance_name="substance", box_name="box"):
#     """Make a box that contains molecules of a single species.
#     Returns: (structure, topology)
#         structure           -- Structure file.
#         topology            -- Topology file.
#     Arguments:
#         substance           -- Input structure file containing a single molecule.
#         n_mols              -- Number of molecules.
#         box_size            -- Box size in nm (either float or three-dimensional vector of floats)
#         ff_dir              -- (Optional) Forcefield directory.
#         amb_ff              -- (Optional) Forcefield name of Gromacs' built-in force field.
#         create_itp          -- Flag to call pdb2amb, if include_topology is not given (default: True).
#         include_topology    -- (Optional) Include topology.
#         work_dir            -- Working directory (default=".").
#         substance_name      -- Name of the substance.
#         box_name            -- Name for the system.
#     """
#     local_variables = locals()
#     _work_dir, coffe_dir, logger = filesys.prepare_coffe_work_dir(work_dir)
#     logger.info("Creating a homogeneous box with {}.".format(local_variables))
#
#     try:
#         _substance = filesys.make_abspath(substance, _work_dir)
#         assert isinstance(n_mols, int) and n_mols > 0, "n_mols must be integer > 0"
#         if include_topology is not None:
#             _include_topology = filesys.make_abspath(include_topology, _work_dir)
#         _ff_dir = ff_dir
#         if ff_dir is not None:
#             _ff_dir = filesys.make_abspath(ff_dir, _work_dir)
#     except AssertionError as e:
#         logger.exception(e)
#         raise e
#
#     # Create itp
#     # TODO(AK) enable usage of top files
#     itp_list = [include_topology]
#     if include_topology is None:
#         if create_itp:
#             itp = os.path.join(_work_dir, "include_topology.itp")
#             itp, ff_itp = ambutil.amb_pdb2itp(_substance, itp, _ff_dir, amb_ff, _work_dir)
#             ambutil.rename_substance_in_itp(itp, substance_name)
#             itp_list = [itp]
#         else:
#             itp_list = []
#     else:
#         ff_itp = os.path.join("{}.ff".format(amb_ff),"forcefield.itp")
#
#     # Create box
#     structure = filesys.make_abspath("conf.gro", _work_dir, check_exists=False)
#     ambutil.amb_insert_n_molecules(box_size, _substance, n_mols, structure, _work_dir)
#
#     # Create topology
#     topology = ambutil.amb_make_top([substance_name], [n_mols], itp_list, os.path.dirname(ff_itp), _work_dir, box_name)
#     logger.info("Homogeneous system created successfully.")
#     logger.info(".... Structure file: {}".format(structure))
#     logger.info(".... Topology file: {}".format(topology))
#     return os.path.abspath(structure), os.path.abspath(topology)
#
#
# @args_from_configfile
# def amb_mkbox_twophase():
#     #TODO(FR,PR) create box for two-phase systems
#     raise NotImplementedError()
#
#
# @args_from_configfile
# def amb_mkbox_solvation():
#     #TODO(AK) create box to calculate free energies of solvation
#     raise NotImplementedError()
#
#
# # === High-level interface ===
#
# ALLOWED_BOX_TYPES = ["homogeneous","twophase","solvation"]
#
#
# @args_from_configfile
# def amb_mkbox(boxtype=None, *args, **kwargs):
#     assert boxtype in ALLOWED_BOX_TYPES, \
#         "boxtype {} is not in allowed boxtypes {}".format(boxtype, ", ".join(ALLOWED_BOX_TYPES))
#     if boxtype == "homogeneous":
#         amb_mkbox_homogeneous(*args, **kwargs)
#     elif boxtype == "twophase":
#         amb_mkbox_twophase(*args, **kwargs)
#     elif boxtype == "solvation":
#         amb_mkbox_solvation(*args, **kwargs)
#     else:
#         raise NotImplementedError()
