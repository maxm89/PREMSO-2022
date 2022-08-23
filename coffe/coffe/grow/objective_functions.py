# -*- coding: utf-8 -*-

from coffe.core.decorators import args_from_configfile
from coffe.grow.simulation_wrapper import GromacsSimulation
from coffe.grow.conf import SanderWrapper

import numpy as np
import os
import pandas as pd
import re
import threading

"""Objective Function hierarchy"""


class ObjectiveFunction:
    '''
    Abstract base class for objective function
    '''
    def __init__(self):
        pass
        
    def _make_objfun_dir(self, abs_dir_path, resumeable=True):
        try:
            os.mkdir(abs_dir_path)
        except FileExistsError:
            print("Directory does already exists. Trying to continue.")
            pass
            
def gmx_callback(ret_list, x, dir_name, top_template, gro_file, mdp_files, mdp_dir,
                 batch_system, batch_template, on_cluster):
    """
    Wrapper function for Gromacs simulation
    """
    sim = GromacsSimulation(dir_name, mdp_files, 
                            top_template, gro_file, mdp_dir, batch_system,
                            batch_template, oncluster=on_cluster)
    sim.simulate(x)
    ret_list.append(sim.get_results("Density"))
    
def mm_callback(ret_list, x, outdir, bin_dir, extrm_template, 
                batchtemplate, on_cluster, mol2_file, leaprc_file, w2p_file, target_names):
    """
    Wrapper function for the energy minimizations
    """
    sw = SanderWrapper(outdir, bin_dir, extrm_template, mol2_file, leaprc_file, w2p_file, 
                       target_names, batch_template=batchtemplate, oncluster=on_cluster)
    sw.simulate(x)
    res = sw.get_results()
    for e in res:
        ret_list.append(e)


class MultiscaleLossFunction(ObjectiveFunction):
    """
    Multiscale loss function.
    
    Directory <out_path> is created and function evaluations will create 
    subdirectories in it.
    """
    def __init__(self, out_path, opt_with_md=True, opt_with_mm=True):
        self.out_path = out_path        
        self.targets = []

        self.opt_with_md = opt_with_md
        self.opt_with_mm = opt_with_mm

    def get_function_value(self, xi, feval_number, res_queue=None):
        """
        Calculates the function value <fi> at x=<xi>. <fi> is put at the end 
        of <res_queue>. 


        Arguments:
        xi: (list-like) the parameter set at which the function is evaluated
        feval_number: (int) unique number of the function evaluation
        res_queue: (thread-safe std lib queue) queue in which the results are put

        Returns:
        returns nothing
        """
        # create directory <feval_number> in <out_path>
        evaluation_dir = os.path.join(self.out_path, str(feval_number))
        self._make_objfun_dir(evaluation_dir)


        if self.opt_with_md:
            pproperties = []
            dirname = os.path.join(evaluation_dir, "PP")

            kw = dict(x=xi, top_template=self.top_template, dir_name=dirname,
                      ret_list=pproperties, gro_file=self.gro_file,
                      mdp_files=self.mdp_files, mdp_dir=self.mdp_dir,
                      batch_system=self.batch_system,
                      batch_template=self.batch_template, 
                      on_cluster=self.on_cluster)        

            # Start MD first since it will take longer
            md_thread = threading.Thread(target=gmx_callback,
                                         kwargs=kw)
            md_thread.start()
        
        if self.opt_with_mm:
            mmdir = os.path.join(evaluation_dir, "QMMM")
            mmproperties = []

            kwmm = dict(x=xi, outdir=mmdir, bin_dir=self.bin_dir, 
                        extrm_template=self.extrm_template, 
                        batchtemplate=self.batch_template,
                        mol2_file=self.mol2_file, leaprc_file=self.leaprc_file, 
                        w2p_file=self.w2p_file,
                        target_names=self.target_names,
                        on_cluster=self.on_cluster,
                        ret_list=mmproperties)

            mm_thread = threading.Thread(target=mm_callback,
                                         kwargs=kwmm)

            mm_thread.start()

            # wait for the mm calculations to finish
            mm_thread.join()

            mmloss = self.calc_mmloss(mmproperties)
            mmloss_raw = mmloss

            if mmloss > -1:
                # if everything went right
                mmloss = mmloss*self.scale_mm*self.weight_mm
                mmloss = np.tanh(mmloss)
        else:
            mmloss = 0.0

        if self.opt_with_md:
            # wait for md to finish
            md_thread.join()

            pploss = 700-pproperties[0]
            pploss = pploss / 700
            pploss = pploss*pploss
        else:
            pploss = 0.0

        if mmloss == -1:
            # if mm has produced strange results
            res = -1
        else:
            # add mm loss
            res = (self.weight_md*pploss)+(mmloss)
            res = np.tanh(res)
        
        # put the results into res_queue
        print("i=", feval_number, ":",  res, pploss, mmloss_raw, xi)
        res_queue.put((feval_number, xi, res))
        return
        
    def calc_mmloss(self, mmproperties):
        res = np.array(mmproperties)

        no_zeros = (res==0).sum()
        if no_zeros > 5:
            return 200

        df = pd.read_csv(self.targets, header=None)
        targets = [e[0] for e in df.values[1:]]
        targets = np.array(targets)

        # loss
        temp = targets-res

        # normalize
        temp = temp/targets

        # squared, to be positive
        temp = temp*temp

        weights = np.zeros(95)
        weights = weights + 0.0052
        temp = temp*weights

        return temp.sum()

    @args_from_configfile
    def _init_pp(self, mdp_files, gro_file, top_file_template, 
                 mdp_dir, targets, scale_md=1, weight_md=0.5, **kwargs):
        self.mdp_files = mdp_files
        self.gro_file = gro_file
        self.top_template = TopFileTemplate(top_file_template, "topol.top")
        self.mdp_dir = mdp_dir
        self.targets.append(targets)
        self.scale_md = scale_md
        self.weight_md = weight_md
    
    @args_from_configfile
    def _init_qm(self, bin_dir, extrm_template, mol2_file, leaprc_file, w2p_file,
                 target_names, targets,scale_mm=1e-4, weight_mm=0.5):
        self.bin_dir = bin_dir
        self.extrm_template = extrm_template
        self.scale_mm = scale_mm
        self.weight_mm = weight_mm
        self.targets = targets
        self.mol2_file = mol2_file
        self.leaprc_file = leaprc_file
        self.w2p_file = w2p_file
        self.target_names = target_names
        
    @args_from_configfile
    def _init_batch_sys(self, batch_system, batch_template, on_cluster):
        self.batch_system = batch_system
        self.batch_template = batch_template
        self.on_cluster = on_cluster
        
    def build_loss_function(out_path, md_config, opt_with_md=True, opt_with_mm=True,
                            qm_config=None, batch_config=None):
        if qm_config is None:
            qm_config = md_config
        if batch_config is None:
            batch_config = qm_config
        
        loss_function = MultiscaleLossFunction(out_path, opt_with_md, opt_with_mm)
        
        loss_function._init_pp(cfg_file=md_config, section="MD")
        loss_function._init_qm(cfg_file=qm_config, section="QM")
        loss_function._init_batch_sys(cfg_file=batch_config, section="BATCH")
        
        return loss_function
        
class TopFileTemplate():
    def __init__(self, top_file_src, target_name):
        self._read_template(top_file_src)
        self._no_params = self._count_placeholders(self.content)
        self.target_name = target_name

    def write_to(self, target_dir, x):
        """
        Writes the given parameter vector (x) into the .top file template.
        Asserts that len(x) equals the number of place holders in the template.
        """
        content = self._fill_params(x)
        f = open(os.path.join(target_dir, self.target_name), "w")
        f.write(content)
        f.close()

    def _read_template(self, top_file_src):
        f = open(top_file_src)
        self.content = f.read()
        f.close()
        
    @property
    def file_name(self):
        return self.target_name

    def _fill_params(self, x):
        placeholders = ["<X_{num}>".format(num=i) for i in range(1, len(x)+1)]
        mappings = zip(placeholders, x)
        content = self._replace_all(mappings)
        return content

    def _replace_all(self, mappings):
        content = self.content
        for placeholder, replacement in mappings:
            content = content.replace(placeholder, str(replacement))
        return content

    def _count_placeholders(self, content):
        return len(re.findall(r'<\d+>', content))
        
