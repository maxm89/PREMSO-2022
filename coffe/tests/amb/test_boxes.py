# -*- coding: utf-8 -*-

"""Tests for coffe.amb.boxes functions"""

from __future__ import absolute_import, division, print_function
import os
import pytest
import coffe.amb.boxes as ambboxes
import coffe.amb.sim as ambsim
from coffe.core import pkgdata, thirdparty
from .box_fixture import boxes_environment


# skip all if Amber (sander) is not installed
pytestmark = pytest.mark.skipif(not thirdparty.AMBER.exists,
                                reason="The tests in this module require a functioning Amber (sander) installation")


# def test_amb_mkbox_homogeneous(tmpdir):
#     substance = pkgdata.abspath("data/boxes/c16.pdb")
#     ff = pkgdata.abspath("data/boxes/charmm36-andi/charmm36-andi.ff")
#     size = 5
#     n = 60
#     structure, topology = ambboxes.amb_mkbox_homogeneous(substance, n, size, ff_dir=ff, work_dir=str(tmpdir))
#     assert os.path.isfile(structure)
#     assert os.path.isfile(topology)
#     # check grompp
#     mdp_file = pkgdata.abspath("data/test_mdp.mdp")
#     ambsim.AmbCalculation(structure, topology, mdp_file, str(tmpdir))
#
#
# def test_mkbox_no_boxtype(boxes_environment):
#     with pytest.raises(AssertionError):
#         os.chdir(boxes_environment)
#         ambboxes.amb_mkbox(cfg_file=os.path.join(boxes_environment, "box_validity.cfg"),
#                            section="withouttype")
#
#
# def test_mkbox_cfg_boxtype(boxes_environment):
#     os.chdir(boxes_environment)
#     ambboxes.amb_mkbox(cfg_file=os.path.join(boxes_environment, "box_validity.cfg"),
#                        section="withtype")
#
#
# def test_mkbox_override_none_boxtype(boxes_environment):
#     os.chdir(boxes_environment)
#     ambboxes.amb_mkbox(boxtype=None, cfg_file=os.path.join(boxes_environment, "box_validity.cfg"),
#                        section="withtype")
#
#
# def test_mkbox_args_boxtype(boxes_environment):
#     os.chdir(boxes_environment)
#     ambboxes.amb_mkbox(boxtype="homogeneous",
#                        cfg_file=os.path.join(boxes_environment, "box_validity.cfg"),
#                        section="withouttype")
#
#
# def test_amb_mkbox_twophase(tmpdir):
#     #TODO(FR,PR) implement test
#     pass
#
#
# def test_amb_mkbox_solvation(tmpdir):
#     #TODO(AK) implement test
#     pass
