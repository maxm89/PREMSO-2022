# -*- coding: utf-8 -*-

"""Test functions for the placeholder module."""

from __future__ import absolute_import, division, print_function

from coffe.core import placeholder
import shutil
import os
import pytest
import math
from coffe.core import pkgdata, thirdparty
from coffe.gmx import sim


def test_replace(tmpdir):
    tmpfile = os.path.join(str(tmpdir), "foo.txt")
    shutil.copyfile(pkgdata.abspath("./data/foo.txt"),
                    tmpfile
                    )
    placeholder.replace_string(tmpfile, "foo", "bar")
    with open(tmpfile, 'r') as f:
        assert any("bar" in l for l in f)


def test_replace_onepara(tmpdir):
    tmpfile = os.path.join(str(tmpdir), "nbfix.itp")
    shutil.copyfile(pkgdata.abspath("../gmx/data/charmm36-nbfix/charmm36-nbfix.ff/nbfix.itp"),
                    tmpfile
                    )
    placeholder.replace_placeholders(tmpfile, ["OC2s"], [math.pi + 1.0])
    with open(tmpfile, "r") as f:
        for line in f:
            assert not "OC2s" in line
        f.seek(0) # go back to beginning of file
        assert any("{:.15f}".format(math.pi + 1.0) in line for line in f)


def test_replace_via_dict(tmpdir):
    tmpfile = os.path.join(str(tmpdir), "nbfix.itp")
    shutil.copyfile(pkgdata.abspath("../gmx/data/charmm36-nbfix/charmm36-nbfix.ff/nbfix.itp"),
                    tmpfile
                    )
    placeholder.replace_placeholders(tmpfile, para_dict={"OC2s": math.pi + 1.0})
    with open(tmpfile, "r") as f:
        for line in f:
            assert not "OC2s" in line
        f.seek(0) # go back to beginning of file
        assert any("{:.15f}".format(math.pi + 1.0) in line for line in f)


def test_replace_morepara(tmpdir):
    tmpfile = os.path.join(str(tmpdir), "nbfix.itp")
    shutil.copyfile(pkgdata.abspath("../gmx/data/charmm36-nbfix/charmm36-nbfix.ff/nbfix.itp"),
                    tmpfile
                    )
    placeholder.replace_placeholders(tmpfile, ["OC2s", "OC2e", "OC3s"], [math.pi + 1.0, math.pi + 2.0, math.pi + 3.0])
    with open(tmpfile, "r") as f:
        for line in f:
            assert not "OC2s" in line
            assert not "OC2e" in line
            assert not "OC3s" in line
        f.seek(0) # go back to beginning of file
        assert any("{:.15f}".format(math.pi + 1.0) in line for line in f)
        f.seek(0)
        assert any("{:.15f}".format(math.pi + 2.0) in line for line in f)
        f.seek(0)
        assert any("{:.15f}".format(math.pi + 3.0) in line for line in f)


def test_replace_withvalue(tmpdir):
    tmpfile = os.path.join(str(tmpdir), "nbfix.itp")
    shutil.copyfile(pkgdata.abspath("../gmx/data/charmm36-nbfix/charmm36-nbfix.ff/nbfix.itp"),
                    tmpfile
                    )
    placeholder.replace_placeholders(tmpfile, ["HH3e"], [math.pi + 1.0])
    with open(tmpfile, "r") as f:
        for line in f:
            assert not "HH3e" in line
        f.seek(0)  # go back to beginning of file
        assert any("{:.15f}".format(math.pi + 1.0) in line for line in f)


def test_extract_include():
    f = pkgdata.abspath("../gmx/data/charmm36-nbfix/charmm36-nbfix.ff/forcefield.itp")
    line_from_f = '#include "ffnonbonded.itp"\n'
    bare, directory = placeholder.extract_include(line_from_f, f)
    include = pkgdata.abspath("../gmx/data/charmm36-nbfix/charmm36-nbfix.ff/ffnonbonded.itp")
    assert os.path.samefile(os.path.join(directory, bare), include)


def test_get_includes():
    f = pkgdata.abspath("../gmx/data/charmm36-nbfix/charmm36-nbfix.ff/forcefield.itp")
    result = placeholder.get_includes(f)
    expected = ["ffnonbonded.itp", "ffbonded.itp", "gb.itp", "cmap.itp", "nbfix.itp", "waters_andi.itp"]
    assert set(result) == set(expected)


def test_read_values():
    f = pkgdata.abspath("../gmx/data/charmm36-nbfix/charmm36-nbfix.ff/nbfix.itp")
    p = ["HH3s", "HH3e"]
    values = placeholder.read_values(f, p)
    assert len(values) == 2
    assert values["HH3s"] is None
    assert values["HH3e"] == pytest.approx(0.139022425816844, 1e-10)


def test_has_placeholders():
    assert placeholder.has_placeholders(pkgdata.abspath("../gmx/data/charmm36-nbfix/charmm36-nbfix.ff/nbfix.itp"))


def test_has_no_placeholders():
    assert not placeholder.has_placeholders(pkgdata.abspath("../gmx/data/charmm36-nbfix/charmm36-nbfix.ff/spc.itp"))


def test_get_placeholders():
    ph = placeholder.get_placeholders(pkgdata.abspath("../gmx/data/charmm36-nbfix/charmm36-nbfix.ff/nbfix.itp"))
    expected = {"OC2s","OC2e","OC3s","OC3e","OH2s","OH2e","OH3s","OH3e",
                "HC2s","HC2e","HC3s","HC3e","HH2s","HH2e","HH3s","HH3e"}
    assert set(ph) == expected


def test_get_included_files():
    includes = placeholder.get_included_files_for_recursion(pkgdata.abspath("../gmx/data/test_ff.top"))
    expected = {
        pkgdata.abspath("../gmx/data/test_ff.itp"),
        pkgdata.abspath("../gmx/data/charmm36-nbfix/charmm36-nbfix.ff/forcefield.itp"),
    }
    assert set(includes) == expected


def test_get_included_files_for_ff():
    includes = placeholder.get_included_files_for_recursion(
        pkgdata.abspath("../gmx/data/charmm36-nbfix/charmm36-nbfix.ff/forcefield.itp"))
    expected = {
        pkgdata.abspath("../gmx/data/charmm36-nbfix/charmm36-nbfix.ff/alkanes_andi.rtp"),
        pkgdata.abspath("../gmx/data/charmm36-nbfix/charmm36-nbfix.ff/atomtypes.atp"),
        pkgdata.abspath("../gmx/data/charmm36-nbfix/charmm36-nbfix.ff/cmap.itp"),
        pkgdata.abspath("../gmx/data/charmm36-nbfix/charmm36-nbfix.ff/ffbonded.itp"),
        pkgdata.abspath("../gmx/data/charmm36-nbfix/charmm36-nbfix.ff/ffnonbonded.itp"),
        pkgdata.abspath("../gmx/data/charmm36-nbfix/charmm36-nbfix.ff/gb.itp"),
        pkgdata.abspath("../gmx/data/charmm36-nbfix/charmm36-nbfix.ff/ions.itp"),
        pkgdata.abspath("../gmx/data/charmm36-nbfix/charmm36-nbfix.ff/merged.rtp"),
        pkgdata.abspath("../gmx/data/charmm36-nbfix/charmm36-nbfix.ff/nbfix.itp"),
        pkgdata.abspath("../gmx/data/charmm36-nbfix/charmm36-nbfix.ff/spc.itp"),
        pkgdata.abspath("../gmx/data/charmm36-nbfix/charmm36-nbfix.ff/spce.itp"),
        pkgdata.abspath("../gmx/data/charmm36-nbfix/charmm36-nbfix.ff/tip3p.itp"),
        pkgdata.abspath("../gmx/data/charmm36-nbfix/charmm36-nbfix.ff/waters_andi.itp"),
    }
    assert set(includes) == expected


def test_recursive_get_placeholders():
    ph = placeholder.recursive_get_placeholders(pkgdata.abspath("../gmx/data/test_ff.top"))
    expected = {"OC2s","OC2e","OC3s","OC3e","OH2s","OH2e","OH3s","OH3e",
                "HC2s","HC2e","HC3s","HC3e","HH2s","HH2e","HH3s","HH3e", "mass"}
    assert set(ph) == expected


def test_recursive_read_values():
    names = ["HH3s", "HH3e", "mass", ]
    values = placeholder.recursive_read_values(pkgdata.abspath("../gmx/data/test_ff.top"), names)
    assert len(values) == 3
    assert values["HH3s"] is None
    assert values["HH3e"] == pytest.approx(0.139022425816844, 1e-10)
    assert values["mass"] == pytest.approx(15.999400, 1e-10)


def test_recursive_has_placeholders():
    assert placeholder.recursive_has_placeholders(pkgdata.abspath("../gmx/data/test_ff.top"))
    assert placeholder.recursive_has_placeholders(
        pkgdata.abspath("../gmx/data/charmm36-nbfix/charmm36-nbfix.ff/forcefield.itp"))
    assert not placeholder.recursive_has_placeholders(
        pkgdata.abspath("../gmx/data/boxes/charmm36-andi/charmm36-andi.ff/forcefield.itp"))


def top_with_replaced_paras(tmpdir):
    """Instead of Fixture. Returns a new (temporary) topology file with replaced parameters."""
    tmp = str(tmpdir)
    top = pkgdata.abspath("../gmx/data/test_ff.top")
    assert placeholder.has_placeholders(top)
    values = {"OC2s": 1.0, "OC2e": 2.0, "OC3s": 3.0, "OC3e": 4.0, "OH2s": 5.0, "OH2e": 6.0, "OH3s": 7.0,
              "OH3e": 8.0, "HC2s": 9.0, "HC2e": 10.0, "HC3s": 11.0, "HC3e": 12.0, "HH2s": 13.0,
              "HH2e": 14.0, "HH3s": 15.0, "HH3e": 16.0, "mass": 17.0}
    placeholder.recursive_replace_placeholders_to_new_dir(top, tmp, values)
    return os.path.join(tmp, "test_ff.top")


def test_recursive_replace_parameters_to_new_dir_thisfile(tmpdir):
    new_top = top_with_replaced_paras(tmpdir)
    assert os.path.isfile(new_top)
    assert not placeholder.has_placeholders(new_top)


def test_recursive_replace_parameters_to_new_dir_included(tmpdir):
    new_top = top_with_replaced_paras(tmpdir)
    assert os.path.isfile(new_top)
    assert not placeholder.recursive_has_placeholders(new_top)


def test_recursive_replace_with_defaults(tmpdir):
    tmp = str(tmpdir)
    top = pkgdata.abspath("../gmx/data/test_ff.top")
    values = {"OC2s": 1.0, "OC2e": 2.0, "OC3s": 3.0, "OC3e": 4.0, "OH2s": 5.0, "OH2e": 6.0, "OH3s": 7.0,
              "OH3e": 8.0, "HC2s": 9.0, "HC2e": 10.0, "HC3s": 11.0, "HC3e": 12.0, "HH2s": 13.0,
              "HH2e": 14.0, "HH3s": 15.0}
    new_top = placeholder.recursive_replace_with_defaults(top, tmp, values)
    assert not placeholder.recursive_has_placeholders(new_top)


@pytest.mark.skipif(not thirdparty.GROMACS.exists, reason="Sanity check requires gromacs preprocessor.")
def test_sanity_after_recursive_replacement(tmpdir):
    new_top = top_with_replaced_paras(tmpdir)
    s = pkgdata.abspath("../gmx/data/test_structure.pdb")
    mdp = pkgdata.abspath("../gmx/data/test_mdp.mdp")
    wd = os.path.join(str(tmpdir),"test_sim")
    sim.GmxCalculation(s, new_top, mdp, wd)
