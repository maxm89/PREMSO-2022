.. README for sphinx
.. Keep text up to date with top-level README.rst (for gitlab)
.. Those are two separate files, because
.. a) otherwise the links do not work and there is no convincing workaround
.. b) having different representations on gitlab and readthedocs could be helpful


=====
coffe
=====


Comprehensive Optimization Force Field Environment

A Python package for automation of molecular simulations and optimization of force field parameters.

* Free software: GNU General Public License v3

* Contributions, questions, feature requests and bug reports are appreciated: https://gitlab.com/olllom/coffe/issues

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


Instructions for downloading and installing the code can be found here:

.. toctree::
   :maxdepth: 1

   notebooks/01_getting_started.ipynb



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

Some functions in coffe/quantum still use *perl* and *OpenBabel* (we might remove this dependency in the future).

It is absolutely not necessary to have all of these programs installed to benefit from coffe.
(In most cases you will use only one simulation program anyway.) Coffe will notify you, if you hit
a dependency that is not installed on your system.


