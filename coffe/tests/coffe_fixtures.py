# -*- coding: utf-8 -*-

"""
Fixtures that can be used by all coffe tests.
"""

from __future__ import absolute_import, division, print_function

import shutil
import os
import pkg_resources
import pytest
import inspect
from coffe.core import pkgdata


@pytest.yield_fixture(params=["abs", "rel"])
def absrel_tmpdir(tmpdir, request):
    """A fixture that runs test for relative and absolute paths."""
    if request.param == "abs":
        yield tmpdir
    elif request.param == "rel":
        os.chdir(str(tmpdir))

        # override pkgdata.abspath
        def f(rel):
            try:
                os.mkdir(os.path.join(str(tmpdir),"absrel_tmpdir"))
            except OSError:
                pass

            caller = inspect.stack()[1]
            mod = inspect.getmodule(caller[0])
            if os.path.isfile(rel):
                shutil.copy(pkg_resources.resource_filename(mod.__name__, rel), tmpdir)
                return os.path.join("absrel_tmpdir", os.path.basename(rel))
            else:
                pass
                # TODO(AK) copy directory
        tmp = pkgdata.abspath
        pkgdata.abspath = f
        yield "."
        pkgdata.abspath = tmp

    else:
        raise NotImplementedError()
