from coffe.amb.sim import AmbCalculation
import os

try:
    os.mkdir("./output_II")
except:
    pass

# MINIMIZATION
wdir = "./output_II/emin"
structure = "../../inpcrd"
topology = "../../prmtop"
mdin_file = "../../em_mdin"
emin = AmbCalculation(structure,
                      topology,
                      mdin_file,
                      work_dir=wdir,
                      overwrite=True)
emin()

# NPT EQUILIBRATION
wdir = "./output_II/npt"
structure = "../emin/restrt"
mdin_file = "../../npt_mdin"
npt = AmbCalculation(structure,
                     topology,
                     mdin_file,
                     work_dir=wdir,
                     overwrite=True)
npt()

# NPT PRODUCTION
wdir = "./output_II/prod"
structure = "../npt/restrt"
mdin_file = "../../prod_mdin"
prod = AmbCalculation(structure,
                      topology,
                      mdin_file,
                      work_dir=wdir,
                      overwrite=True)
prod()
