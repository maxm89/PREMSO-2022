# -*- coding: utf-8 -*-

"""Classes for Gromacs simulations"""

from __future__ import absolute_import, division, print_function

import pytest
import os
from coffe.core import cmdchain, thirdparty, pkgdata, saver
from coffe.gmx import sim as gmxsim
from coffe.gmx import util as gmxutil


class SomeCallable(object):
    def __init__(self):
        self.i = 0

    def __call__(self):
        self.i += 1
        pass


class SomeInvalid1(object):
    pass


class SomeInvalid2(object):
    def __call__(self, arg):
        pass


def test_has_empty_call():
    assert cmdchain.has_empty_call(SomeCallable())


def test_has_no_empty_call1():
    assert not cmdchain.has_empty_call(SomeInvalid1())


def test_has_no_empty_call2():
    assert not cmdchain.has_empty_call(SomeInvalid2())


def test_empty_construction(tmpdir):
    cmdchain.CommandChain(work_dir=str(tmpdir))


def test_nonempty_construction(tmpdir):
    cmdchain.CommandChain([SomeCallable()], work_dir=str(tmpdir))


def test_nonempty_construction_failure(tmpdir):
    with pytest.raises(AssertionError):
        cmdchain.CommandChain([SomeInvalid1()], work_dir=str(tmpdir))


def test_adding(tmpdir):
    cc = cmdchain.CommandChain(work_dir=str(tmpdir))
    cc += [SomeCallable()]


def test_adding_failure(tmpdir):
    cc = cmdchain.CommandChain(work_dir=str(tmpdir))
    with pytest.raises(AssertionError):
        cc += [SomeInvalid1()]


def test_len_zero(tmpdir):
    cc2 = cmdchain.CommandChain(work_dir=str(tmpdir))
    print (cc2.commands)
    assert len(cc2) == 0


def test_len_nonzero(tmpdir):
    cc = cmdchain.CommandChain(work_dir=str(tmpdir))
    cc += [SomeCallable() for _ in range(2)]
    print(cc.commands)
    assert len(cc) == len(cc.commands)
    assert len(cc) == 2


def test_call(tmpdir):
    cc = cmdchain.CommandChain(work_dir=str(tmpdir))
    assert len(cc) == 0
    cc += [SomeCallable() for _ in range(5)]
    assert len(cc) == 5
    cc()
    for c in cc:
        assert c.i == 1


def test_hierarchical(tmpdir):
    cc = cmdchain.CommandChain(work_dir=str(tmpdir))
    cc2 = cmdchain.CommandChain(work_dir=os.path.join(str(tmpdir), "cc2"))
    cc2 += [SomeCallable() for _ in range(2)]
    cc += [SomeCallable(), cc2]


@pytest.fixture
def my_gmx_sim(tmpdir):
    s = pkgdata.abspath("../gmx/data/test_structure.pdb")
    t = pkgdata.abspath("../gmx/data/test_topology.top")
    mdp = pkgdata.abspath("../gmx/data/test_mdp.mdp")
    wd = [os.path.join(str(tmpdir), "test_sim{}".format(i)) for i in range(2)]
    cc = cmdchain.CommandChain(work_dir=str(tmpdir))
    cc += [gmxsim.GmxCalculation(s, t, mdp, wd[i]) for i in range(2)]
    return cc


@pytest.mark.skipif(not thirdparty.GROMACS.exists,
                    reason="Test works with Gromacs only.")
def test_sim_chain(my_gmx_sim):
    cc = my_gmx_sim
    assert len(cc) == 2
    cc()
    assert os.path.isfile(os.path.join(cc.work_dir,"test_sim0/confout.gro"))
    assert os.path.isfile(os.path.join(cc.work_dir,"test_sim1/confout.gro"))


@pytest.mark.skipif(not thirdparty.GROMACS.exists,
                    reason="Test works with Gromacs only.")
def test_exception_logging(my_gmx_sim):
    cc = my_gmx_sim
    # manually place a bug
    os.remove(os.path.join(cc[1].work_dir, "topol.tpr"))
    with pytest.raises(gmxutil.GromacsError) as e:
        cc()
    # check if error is logged in command chain
    with open(os.path.join(cc.coffe_dir, "log.txt"),"r") as f:
        assert "GromacsError" in f.read()


@pytest.mark.skipif(not thirdparty.GROMACS.exists,
                    reason="Test works with Gromacs only.")
def test_save_load_sim_chain(my_gmx_sim):
    cc = my_gmx_sim
    dump = os.path.join(str(cc.work_dir), "obj.dump")
    saver.save(cc, dump)
    cc2 = saver.load(dump)
    assert sorted(cc2.__dict__.keys()) == sorted(cc.__dict__.keys())
    # compare keys of commands
    for c, c2 in zip(cc, cc2):
        assert sorted(c2.__dict__.keys()) == sorted(c.__dict__.keys())


