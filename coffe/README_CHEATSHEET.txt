## Commands and sequence for adding new Package (i.e. a meta-level directory -- e.g. amb, gmx, qm)
1. cd ~/git/coffe/coffe
2. mkdir Name_New_Package
3. cd Name_New_Package
4. touch __init__.py

## Immediately go create an identical test subdirectory
1. cd ~/git/coffe/tests
2. cp -r ../coffe/Name_New_Package .

## Add a new Module (i.e. a new python script)
1. Create or copy the script to the appropriate Package directory (e.g. Name_New_Package)
2. Add to the header (above import commands):
# -*- coding: utf-8 -*-

"""A docstring that describes what the module does."""

from __future__ import absolute_import, division, print_function


## Add a new branch to gitlab
git push origin Branch_Name

## Misc. git commands:
git branch
git checkout master
git checkout Branch_Name
git status

## Setup coffe for developer
python3 setup.py develop --user

## test individual files (e.g. tests/analysis/test_name.py)
py.test test/sub_dir/test_name.py
py.test test/sub_dir/test_name.py -s
pytest -vs tests/sub_dir/test_name.py ## shows what is normally printed
python3 -m pytest -v tests/sub_dir/test_name.py ## suppresses what is normally printed


## Having trouble getting commands when typing coffe
## see http://amber-md.github.io/pytraj/latest/installation.html
sudo mv $AMBERHOME/lib/python2.7/site-packages/pytraj $AMBERHOME/lib/python2.7/site-packages/pytraj.old
sudo mv $AMBERHOME/lib/python2.7/site-packages/pytraj-1.0.4-py2.7.egg-info $AMBERHOME/lib/python2.7/site-packages/pytraj-1.0.4-py2.7.egg-info.old

## Creating web page for manual:
git checkout sphinxdoc
python3 setup.py develop --user
python3 docs/update_doc.py
