#!/usr/bin/env python

"""Small wrapper script to rebuild the documentation for the Python API.
"""

import coffe
import os
import shutil
import sys


try:
    import alabaster
except ImportError:
    print("The alabaster theme is not installed on your machine. "
          "\n    :'-(  That is a shame  :'-( \n"
          "But there is an easy way to fix this:\n"
          "Reinstall coffe via setup.py and try again.")
    sys.exit(1)


project_root = os.path.dirname(os.path.dirname(coffe.__file__))
print("Updating coffe documentation files from {}".format(project_root))

os.chdir(os.path.join(project_root, "docs"))
try:
    shutil.rmtree("_build")
    print("Old docs/_build directory removed...")
except:
    pass

os.system("sphinx-apidoc ../coffe -f -o .")
os.system("make html")

print("Done. Open the following file in a webbrowser:")
print(os.path.join(project_root, "docs", "_build", "html", "index.html"))
