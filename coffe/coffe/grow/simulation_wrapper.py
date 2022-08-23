# -*- coding: utf-8 -*-

# executer.py in old grow

from coffe.core import cluster
from coffe.gmx import observables
from coffe.gmx import simgen

import numpy as np
import os
import pandas as pd
from shutil import copy
from time import sleep


class GromacsSimulation:
    """
    Wrapper class for the Gromacs simulations.
    Generates a coffe simulation chain, submits it to the cluster
    and stores the result in a file.
    """
    def __init__(self, new_dir_name, mdp_files, top_template, gro_file,
                 mdp_dir,batch_system, batch_template, oncluster=False, 
                 job_name = None):
        self.on_cluster = oncluster
        self.dir_name = new_dir_name
        self.mdp_files = mdp_files
        self.top_template = top_template
        self.gro_file = gro_file
        self.mdp_dir = mdp_dir
        self.batch_system = batch_system
        self.batch_template = batch_template
        
        if job_name == None:
            job_name = "coffe_job"
        self.job_name = job_name
        
        # Create a new directory for the simulation
        self._make_dir()
        
        # And copy the required mdp files into it
        self._copy_files()


    def simulate(self, x):
        if self._results_available(self.dir_name):
            return None
        
        self.top_template.write_to(self.dir_name, x)
        self.top_file = os.path.join(self.dir_name, 
                                     self.top_template.file_name)

        # Init the coffe simulation chain
        self._init_chain()
        
        if self.on_cluster:
            queueing =self.batch_system
            batch_template = self.batch_template

            job_name = self.job_name
            work_dir = self.dir_name
            job = cluster.ClusterJob(queueing, batch_template, job_name, work_dir)   
            print("job created")
            job += self.chain
            print("job added")
            job.submit()
            print("job submitted")
            
            # wait until the job is done or aborted
            while(job.status not in ["completed", "error"]):
                sleep(5)
        else:
            self.chain()
            


    def _init_chain(self):
        """
        Builds a simulation chain that executes the simulations
        specified for the object.
        """
        
        if self._results_available(self.dir_name):
            # Recover simulation that was already done (in caller)
            return None
        
        self.mdp_names = []
        
        # use the names of the mdp files as names for the simulation directories
        # e.g. "prod.mdp" -> "prod"
        for mdp in self.mdp_files:
            mdp_name = mdp.split(".")[0]
            self.mdp_names.append(mdp_name)
            
        mdp_file_paths = []
        for mdp_file in self.mdp_files:
            mdp_file_paths.append(os.path.join(self.dir_name, mdp_file))
            
        generator = simgen.GmxChainGenerator(
                names=self.mdp_names,
                mdp_files=mdp_file_paths
                )
        
        self.chain = generator.generate(self.dir_name,self.gro_file, self.top_file)


    def _store_results(self, location, properties):
        df = pd.DataFrame(data={'properties': [properties]})
        path = os.path.join(location, "properties.csv")
        df.to_csv(path, index=False)
        
    def _results_available(self, location):
        return os.path.isfile(os.path.join(location, "properties.csv"))
        
    def _read_results(self, location):
        path = os.path.join(location, "properties.csv")
        df = pd.read_csv(path)
        return df.values
    
    def _make_dir(self):
        try:
            os.mkdir(self.dir_name)
        except:
            print("Directory for simulation does already exist.")
            print("Trying to continue.")
            
    def _copy_files(self):
        for file in self.mdp_files:
            copy(os.path.join(self.mdp_dir, file), self.dir_name)
            
    def get_results(self, prop):
        # Read the results of the command chain
        
        if self._results_available(self.dir_name):
            return self._read_results(self.dir_name)
        
        allowed_properties = ["Density", "Pressure", "Temperature"]
        assert(prop in allowed_properties)

        results = observables.gmx_calc_energy(os.path.join(self.dir_name, 
                                                           self.mdp_names[-1]), [prop])
        
        # results is an array containing: (t, result)
        # calculate mean, sd using double precision according to np docs
        mean = np.mean(results, axis=0, dtype=np.float64)
        sd = np.std(results, axis=0, dtype=np.float64)
        
        self._store_results(self.dir_name, mean[1])
        
        print(mean[1], sd[1])
        
        return mean[1]
