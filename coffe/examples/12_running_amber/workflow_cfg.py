from coffe.amb.sim import AmbCalculation
import os

try:
    os.mkdir("./output_cfg")
except:
    pass

# MINIMIZATION
emin = AmbCalculation(cfg_file="workflow.cfg",section="emin")
emin()

# NPT EQUILIBRATION
npt = AmbCalculation(cfg_file="workflow.cfg",section="npt")
npt()

# NPT PRODUCTION
prod = AmbCalculation(cfg_file="workflow.cfg",section="prod")
prod()
