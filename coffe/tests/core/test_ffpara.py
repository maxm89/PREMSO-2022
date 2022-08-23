import os

import pytest

from coffe.core import ffpara, pkgdata, placeholder, thirdparty
from coffe.gmx import sim


def opt2ff1(x):
    assert len(x) == 2
    y = [i for i in range(16)]
    return [y[i] + x[0] * 1.5 + x[1] for i in range(16)]


def opt2ff2(x):
    assert len(x) == 2
    y = [i for i in range(17)]
    return [y[i] + x[0] * 1.5 + x[1] for i in range(17)]


def opt2ff3(x):
    assert len(x) == 2
    y = [i for i in range(16)]
    return [y[i] + x[0] * 1.5 + x[1] for i in range(16)]


def opt2ff4(x):
    assert len(x) == 2
    y = [i for i in range(18)]
    return [y[i] + x[0] * 1.5 + x[1] for i in range(18)]


def nbfix_parameter_names():
    paras = []
    for c1 in ["O", "H"]:
        for c2 in ["C", "H"]:
            for c3 in ["2", "3"]:
                for c4 in ["s", "e"]:
                    paras += [c1 + c2 + c3 + c4]
    return paras


@pytest.fixture
def c36_nbfix(tmpdir):
    top = pkgdata.abspath("../gmx/data/charmm36-nbfix/charmm36-nbfix.ff/forcefield.itp")
    opt = ["sc1", "sc2"]
    return ffpara.ParameterFactory(topology=top, ff_para_names=nbfix_parameter_names(),
                                   opt_para_names=opt, opt2ff=opt2ff1, work_dir=str(tmpdir),
                                   mode="gromacs_topology"
                                   )



def test_ffpara_factory_construction(c36_nbfix):
    _ = c36_nbfix


def test_ffpara_makepara(c36_nbfix):
    factory = c36_nbfix
    p = factory.make_parameter_set([0, 1], os.path.join(factory.work_dir, "a"), immediate_apply=False)
    assert os.path.realpath(p.template_top) == \
           os.path.realpath(pkgdata.abspath("../gmx/data/charmm36-nbfix/charmm36-nbfix.ff/forcefield.itp"))
    assert p.ff_para_values == [i + 1 for i in range(16)]


@pytest.fixture
def factory_tmp(tmpdir):
    top = pkgdata.abspath("../gmx/data/test_ff.top")
    paras = nbfix_parameter_names()
    paras += ["mass"]
    opt = ["sc1", "sc2"]
    factory = ffpara.ParameterFactory(topology=top, ff_para_names=paras,
                                      opt_para_names=opt, opt2ff=opt2ff2, work_dir=str(tmpdir))
    return factory, str(tmpdir)


def test_ffpara_apply2top(factory_tmp):
    factory, tmp = factory_tmp
    p = factory.make_parameter_set([0, 1], "a")
    # assert that includes were changed
    assert not placeholder.recursive_has_placeholders(p.topology, mode="gromacs_topology")


@pytest.mark.skipif(not thirdparty.GROMACS.exists, reason="Sanity check requires gmx preprocessor.")
def test_ffpara_gmx_sanity_check(factory_tmp):
    factory, tmp = factory_tmp
    s = pkgdata.abspath("../gmx/data/test_structure.pdb")
    mdp = pkgdata.abspath("../gmx/data/test_mdp.mdp")
    wd = os.path.join(tmp,"test_sim")
    sim.GmxCalculation(s, factory.make_parameter_set([0, 1], "a").topology, mdp, wd)


def test_ffpara_para_not_in_ffparanames(tmpdir):
    top = pkgdata.abspath("../gmx/data/test_ff.top")
    paras = nbfix_parameter_names()
    opt = ["sc1", "sc2"]
    with pytest.raises(ffpara.FFParameterError):
        ffpara.ParameterFactory(topology=top, ff_para_names=paras,
                                opt_para_names=opt, opt2ff=opt2ff3, work_dir=str(tmpdir))


def test_ffpara_para_not_in_templatetop(tmpdir):
    top = pkgdata.abspath("../gmx/data/test_ff.top")
    paras = nbfix_parameter_names() + ["mass", "krass"]
    opt = ["sc1", "sc2"]
    with pytest.raises(ffpara.FFParameterError):
        ffpara.ParameterFactory(topology=top, ff_para_names=paras,
                                opt_para_names=opt, opt2ff=opt2ff4, work_dir=str(tmpdir))


def test_ffpara_top_not_ready(tmpdir):
    with pytest.raises(ffpara.FFParameterError):
        p = ffpara.FFParameters(pkgdata.abspath("../gmx/data/charmm36-nbfix/charmm36-nbfix.ff/forcefield.itp"),
                                ff_para_names=nbfix_parameter_names(),
                                ff_para_values=[i + 1 for i in range(16)],
                                opt_para_names=nbfix_parameter_names(),
                                opt_para_values=[i + 1 for i in range(16)],
                                work_dir=str(tmpdir),
                                immediate_apply=False
                                )
        p.topology
