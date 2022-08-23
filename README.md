# PREMSO-2022
Source code and cofiguration files for "Determining Lennard-Jones parameters using multiscale target data through presampling-enhanced, surrogate-assisted global optimization"

## Requirements
- Python 3
- Gromacs >= 2016.3
- Amber

## About the files in this repository
* `./coffe/` contains the code that was used to obtains the results that we present in our work. This is basically a version of [COFFE(Comprehensive Optimization Force Field Environment)](https://gitlab.com/Olllom/coffe/), which is a python package that allows us to run Gromacs simulations on a slurm batch system from python code.
* `./coffe/coffe/grow/` contains the optimization code and code to steer the experiments that we did:
    * `optimization_algorithms.py` the CMA-ES(`class CMAES`) and MSAEOP (`class BayesianOptimization`) algorithms
    * `sampling.py` the Latin Hypercube Sampling and it's optimization
    * `grow_sander_ff_opt.py` the Energy Minimization steering
* `./inputs/` contains the required input files
* `example_call.py` / `example.cfg` script and config file to run an example optimization run
* `pipfreeze.txt` a dump of installed pip packages, that where required to run our software

## Installation
Install required python packages, e.g.


    pip -r pipfreeze.txt
    
Copy oplsaa-andi.ff to a directory that is in the Gromacs force field search path. This is a copy of the OPLSAA force field.

Install the optimization software:

    cd coffe
    python setup.py develop --user
    
Check that it works by spawning a new shell and typing:

    which coffe
    coffe --help
    
## Example optimization
Make sure that `./out/` contains only the `.keep` file.

To run a "small" optimization task, type

    python example_call.py

This might require additional configuration of your system, depending on your configuration of Gromacs and Amber.
