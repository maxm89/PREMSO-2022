.. README for Gitlab
.. Keep text up to date with top-level docs/readme.rst (for sphinx)
.. Those are two separate files, because
.. a) otherwise the links do not work and there is no convincing workaround
.. b) having different representations on gitlab and readthedocs could be helpful


=====
coffe
=====


.. image:: https://gitlab.com/Olllom/coffe/badges/master/build.svg
        :target: https://gitlab.com/Olllom/coffe/pipelines
        :alt: Continuous Integration

.. image:: https://img.shields.io/pypi/v/coffe.svg
        :target: https://pypi.python.org/pypi/coffe#
        :alt: pypi

.. image https://img.shields.io/travis/Olllom/coffe.svg
        :target: https://travis-ci.org/Olllom/coffe

.. image:: https://readthedocs.org/projects/coffe/badge/?version=latest
        :target: https://coffe.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. see https://anaconda.org/conda-forge/plotly/badges for conda badges

Comprehensive Optimization Force Field Environment

A Python package for automation of molecular simulations and optimization of force field parameters.

* Free software: GNU General Public License v3

* Documentation: https://coffe.readthedocs.io.


Features
--------

* Automated composure of simulation systems in Gromacs
* Automated simulation workflows in Gromacs
* Interaction with slurm and torque submission systems
* Advanced stopping conditions for Gromacs simulations (TBD)
* ... more to come


Getting started
---------------


Instructions for downloading and installing the code can be found here: Installation_.

.. _Installation: docs/notebooks/01_getting_started.ipynb



Third-party Software
--------------------

The following third-party software is **not** required to install coffe.
However, a lot of coffe's functionality depends on molecular simulation packages.
In order to use program-specific functions, these programs have to be installed.

1) Gromacs (optional): Required for everything in coffe/gmx.
   Make sure the command *gmx* can be called from a terminal.
2) Amber (optional): Required for everything in coffe/amb.
   Make sure the the Amber executables *sander*, ... can be called from a terminal.
3) CHARMM (optional): Required for everything in coffe/chm.
   Make sure the command *charmm* can be called from a terminal.

Some functions in coffe/quantum still use *perl*, *pymol* and *OpenBabel*
(we might remove these dependencies in the future).

It is absolutely not necessary to have all of these programs installed to benefit from coffe.
(In most cases you will use only one simulation program anyway.) Coffe will notify you, if you hit
a dependency that is not installed on your system.




Tutorials
---------

-  Using coffe with Gromacs:

   1) Creating boxes using Gromacs: Tutorial1_.
   2) Running Gromacs simulations: Tutorial2_.
   3) Full Gromacs workflow on cluster: Tutorial3_.
   4) Full Gromacs two-phase simulation: Tutorial4_.

.. _Tutorial1: examples/01_creating_boxes_using_gmx/boxes.ipynb
.. _Tutorial2: examples/02_running_gmx/gmx.ipynb
.. _Tutorial3: examples/03_full_gmx_sim_on_cluster/gmx_advanced.ipynb
.. _Tutorial4: examples/04_full_simulation_twophase_box/twophase_boxes.ipynb


-  Using coffe with Amber:

   1) Running Amber simulations: Tutorial12_.

.. _Tutorial12: examples/12_running_amber/amb.ipynb

Developers' Guide
-----------------

1) `Coding conventions`_
2) `Notes on how to add modules, classes, functions, etc.`_
3) `Contributing to the code`_
4)  `Notes to core developers`_

.. _Coding conventions: docs/notebooks/02_coding_conventions.ipynb
.. _Notes on how to add modules, classes, functions, etc.: docs/notebooks/03_adding_stuff.ipynb
.. _Contributing to the code: CONTRIBUTING.rst
.. _Notes to core developers: docs/notebooks/04_mergerequests.ipynb


Related Work
------------

The docker images for the continuous integration framework are hosted on `this github page`_.

.. _this github page: https://github.com/olllom/docker_coffe


Credits
---------

Find out about the authors here_.

.. _here: AUTHORS.rst
