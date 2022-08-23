# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages
import versioneer
import sys

# Custom commands for versioning
cmdclass = versioneer.get_cmdclass()

# Custom commands for building the docs
try:
    from sphinx.setup_command import BuildDoc
    cmdclass['build_sphinx'] = BuildDoc
except ImportError:
    print("Could not import sphinx. build_sphinx command not installed.")


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()


requirements = [
    'Click>=7.0',
    'six',
    'numpy>=1.12',
    'f90nml', # for reading/writing amber mdin files
    'pytraj>=2.0.2',
    'plumbum>=1.6',
    'natsort>=5.0',
    'pandas',
    #'sphinx',
    'nbsphinx', # sphinx documentation for jupyter notebooks
    'sphinx_click', # sphinx documentation for click
    'alabaster', # alabaster theme for documentation
    'packaging',
    'scipy>=1.0.0',
    # put package requirements here
]

if sys.version_info[0] < 3:
    requirements.append('matplotlib<3')
else:
    requirements.append('matplotlib')

setup_requirements = [
    'pytest-runner',
    #  put setup requirements (distutils extensions, etc.) here
]

test_requirements = [
    'pytest>=3.4',
    # put package test requirements here
]

setup(
    name='coffe',
    version=versioneer.get_version(),
    description="Comprehensive Optimization Force Field Environment",
    long_description=readme + '\n\n' + history,
    author="Andreas Krämer",
    author_email='kraemer.research@gmail.com',
    url='https://github.com/Olllom/coffe',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'coffe=coffe.cli:main'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license="GNU General Public License v3",
    zip_safe=False,
    keywords='coffe',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
    cmdclass=cmdclass,
)
