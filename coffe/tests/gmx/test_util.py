# -*- coding: utf-8 -*-

"""Tests for coffe.gmx.util functions"""

from __future__ import absolute_import, division, print_function
import os
import shutil

import pytest

from coffe.core.globconf import CONFIG
import coffe.gmx.util as gmxutil
from coffe.core import pkgdata, shell, thirdparty

# skip all if gromacs is not installed
pytestmark = pytest.mark.skipif(not thirdparty.GROMACS.exists,
                                reason="The tests in this module require a functioning gromacs installation")

def test_gmx_make_top(tmpdir):
    substances = ["NHEX"]
    nmols = [1]
    top = gmxutil.gmx_make_top(substances, nmols,
                               forcefield_dir=pkgdata.abspath("data/boxes/charmm36-andi/charmm36-andi.ff"),
                               work_dir=str(tmpdir))
    assert os.path.isfile(top)


def test_gmx_pdb2itp(tmpdir):
    ff_dir = pkgdata.abspath("data/boxes/charmm36-andi/charmm36-andi.ff")
    pdb = pkgdata.abspath("data/boxes/c16.pdb")
    itp = os.path.join(str(tmpdir), "out.itp")
    log = os.path.join(str(tmpdir), "cmdline.txt")
    itp, ff_include = gmxutil.gmx_pdb2itp(pdb, itp, ff_dir=ff_dir, work_dir=str(tmpdir))
    assert os.path.isfile(itp)
    #assert os.path.isfile(ff_include)


def test_gmx_pdb2itp_builtin_ff(tmpdir):
    ff = "oplsaa"
    pdb = pkgdata.abspath("data/boxes/1AKI.pdb")
    itp = os.path.join(str(tmpdir), "out.itp")
    itp, ff_include = gmxutil.gmx_pdb2itp(pdb, itp, gmx_ff=ff, work_dir=str(tmpdir), water="spce")
    assert os.path.isfile(itp)
    assert ff_include is not None


def test_gmx_pdb2itp_failure(tmpdir):
    ff = "oplsaa"
    pdb = pkgdata.abspath("data/boxes/c16.pdb") # this c16 pdb should not work with opls
    itp = os.path.join(str(tmpdir), "out.itp")
    with pytest.raises(gmxutil.GromacsError) as e:
        def pdb2itp(*args, **kwargs):
            gmxutil.gmx_pdb2itp(*args, **kwargs)
        pdb2itp(pdb, itp, gmx_ff=ff, work_dir=str(tmpdir), water="spce")
    assert ("fatal error" in str(e).lower())


def test_gmx_insert_n_molecules(tmpdir):
    # make initial box
    pdb = pkgdata.abspath("data/boxes/c16.pdb")
    box = os.path.join(str(tmpdir),"box.gro")
    final = os.path.join(str(tmpdir),"solvated.gro")
    cmd = "{} editconf -f {} -box 1.5 -o {}".format(CONFIG.gmx, pdb, box)
    shell.call_cmd(cmd, os.path.join(str(tmpdir), "cmdline_editconf.txt"))
    # add 150 molecules
    gmxutil.gmx_insert_n_molecules(os.path.join(str(tmpdir),"box.gro"),
                                   pdb,
                                   150, final, str(tmpdir))
    # check number of atoms in final
    n_final = 0
    with open(final,"r") as f:
        i = 0
        for line in f:
            i += 1
            if i == 2:
                n_final = int(line.strip())
                break
    assert n_final == 50*151  # (NHEX = 50 atoms, 150+1 molecules)


def test_gmx_insert_n_molecules_in_empty_box(tmpdir):
    # make initial box
    pdb = pkgdata.abspath("data/boxes/c16.pdb")
    final = os.path.join(str(tmpdir),"solvated.gro")
    gmxutil.gmx_insert_n_molecules(4.0,
                                   pdb,
                                   150, final, str(tmpdir))
    # check number of atoms in final
    n_final = 0
    with open(final,"r") as f:
        i = 0
        for line in f:
            i += 1
            if i == 2:
                n_final = int(line.strip())
                break
    assert n_final == 50*150 #(NHEX = 50 atoms, 150 molecules)


def test_fail_insert_n_molecules(tmpdir):
    pdb = pkgdata.abspath("data/corrupted.pdb")
    final = os.path.join(str(tmpdir),"solvated.gro")
    with pytest.raises(gmxutil.GromacsError) as e:
        def insert_molecules(*args, **kwargs):
            # this construct allows to access the error message
            gmxutil.gmx_insert_n_molecules(*args, **kwargs)
        insert_molecules(4.0, pdb, 150, final, str(tmpdir))
    print (e)
    assert ("fatal error" in str(e).lower())


def test_rename_substance_in_itp(tmpdir):
    tmp = os.path.join(str(tmpdir), 'test.itp')
    shutil.copy(pkgdata.abspath("data/test_ff.itp"), tmp)
    gmxutil.rename_substance_in_itp(tmp, "waterwaterwater")
    with open(tmp,"r") as f:
      for line in f:
         if "waterwaterwater" in line:
            return
    assert False


def test_option_in_line():
    assert gmxutil._option_in_line("rlist", "rlist                    = 1.1; .....\n") == "1.1"


def test_option_in_line2():
    assert gmxutil._option_in_line("rlist", "rlist                    = 1.1\n") == "1.1"


def test_read_mpd_option():
    mdp = pkgdata.abspath("data/test_mdp.mdp")
    assert gmxutil.read_mdp_option(mdp, "rlist") == "1.1"


def test_set_mpd_options(tmpdir):
    mdp = os.path.join(str(tmpdir), "test_mdp.mdp")
    shutil.copy(pkgdata.abspath("data/test_mdp.mdp"), mdp)
    options = {"nsteps":222, "hey": "jude", "emtol": 3.1415926}
    gmxutil.set_mdp_options(mdp, options)
    for key in options:
        assert gmxutil.read_mdp_option(mdp, key) == str(options[key])


def test_read_not_exists():
    with pytest.raises(AssertionError):
        gmxutil.read_mdp_option(pkgdata.abspath("data/test_mdpppp.mdp"), "nsteps")


def test_read_no_such_option():
    with pytest.raises(AssertionError):
        gmxutil.read_mdp_option(pkgdata.abspath("data/test_mdp.mdp"), "aldksjf")


def test_type_failure(tmpdir):
    mdp = os.path.join(str(tmpdir), "test_mdp.mdp")
    shutil.copy(pkgdata.abspath("data/test_mdp.mdp"), mdp)
    with pytest.raises(AssertionError):
        gmxutil.set_mdp_options(mdp, [])
    with pytest.raises(AssertionError):
        gmxutil.set_mdp_options(1, {})


def test_set_and_read_mdp_option_newfile(tmpdir):
    mdp = os.path.join(str(tmpdir), "test_mdp.mdp")
    options = {"nsteps":222, "hey": "jude", "emtol": 3.1415926}
    gmxutil.set_mdp_options(pkgdata.abspath("data/test_mdp.mdp"), options, new_file=mdp)
    for key in options:
        assert gmxutil.read_mdp_option(mdp, key) == str(options[key])
