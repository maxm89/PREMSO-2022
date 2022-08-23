import os.path
import os
from subprocess import call
from time import sleep
from coffe.core import cluster
from coffe.grow.grow_sander_ff_opt import mstart
import pandas as pd

class SanderWrapper:

    def __init__(self, outdir, bindir, extrm_template, mol2_file, 
                 leaprc_file, w2p_file, target_names, batch_template=None, oncluster=False):
        self.outdir = outdir
        self.bindir = bindir
        self.extrm_template = extrm_template
        self.batch_template = batch_template
        self.oncluster = oncluster
        self.mol2_file = mol2_file
        self.leaprc_file = leaprc_file
        self.w2p_file = w2p_file
        self.target_names = target_names

        self._make_dir()

    def get_results(self):
        df = pd.read_csv(self.res_file, header=None)
        results = [e[0] for e in df.values[1:]]
        return results


    def _make_dir(self):
        try:
            os.mkdir(self.outdir)
        except:
            print("Directory for simulation does already exist.")
            print("Trying to continue.")


    def simulate(self, x):
        mm = MMCalc(x, self.outdir, self.bindir, self.extrm_template, self.mol2_file, 
                    self.leaprc_file, self.w2p_file, self.target_names)        
        if self.oncluster:
            job_name = "amb"
            job = cluster.ClusterJob("slurm", self.batch_template, 
                                     job_name, self.outdir)   
            print("job created")
            job += mm
            print("job added")
            job.submit()
            print("job submitted")
            
            # wait until the job is done or aborted
            while(job.status not in ["completed", "error"]):
                sleep(5)

        else:
            mm()

        self.res_file = mm.result_file_path()


class MMCalc:

    def __init__(self, x, dirname, bindir, extrm_template, mol2_file, 
                 leaprc_file, w2p_file, target_names):
        self.x = x
        self.dirname = dirname
        self.outpath = os.path.join(dirname, "out")
        self.bindir = bindir
        self.extrm_template = extrm_template
        self.mol2_file = mol2_file
        self.leaprc_file = leaprc_file
        self.w2p_file = w2p_file
        self.target_names = target_names

    def result_file_path(self):
        return os.path.join(self.outpath, "properties.txt")

    def __call__(self):
        self.__mm__()

    def __mm__(self):
        mstart(self.x, self.outpath, self.bindir, self.extrm_template, self.mol2_file, 
                 self.leaprc_file, self.w2p_file, self.target_names)

