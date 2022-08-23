# -*- coding: utf-8 -*-

"""Optimization Algorithm hierarchy"""


from coffe.core.decorators import args_from_configfile
from coffe.grow.maths_helper import scale, Constraints
from coffe.grow.objective_functions import MultiscaleLossFunction
from coffe.grow.sampling import lh_sampling

import copy
import cma
import numpy as np
from os import path, stat, system, makedirs, mkdir
import pandas as pd
from queue import Queue
from sklearn.gaussian_process.kernels import Matern, RBF, WhiteKernel
from sklearn.gaussian_process import GaussianProcessRegressor
import threading


class OptimizationAlgorithm:

    @args_from_configfile
    def __init__(self, bounds, **kwargs):
        self.constraints = Constraints(bounds)
    
    @staticmethod
    @args_from_configfile
    def factor_optimization_algorithm(opt_method, out_path, cfg,
                                      objective_function="multiscale", **kwargs):
        """
        Factory method for optimization algorithm object.

        Arguments:
        opt_method: (string) one out of [bayes_opt, cmaes]
        out_path: (string) dir path where the subdirectories for the simulations
        objective_function (string) one out of [multiscale, physical, quantum]

        Raises:
        AssertionError: if the input arguments do not match

        """

        try:
            mkdir(out_path)
        except FileExistsError:
            print("outpath exists already")
            
        print(out_path)
        if objective_function == "multiscale":
            obj_fun = MultiscaleLossFunction.build_loss_function(out_path, cfg)
        elif objective_function == "physical":
            obj_fun = MultiscaleLossFunction.build_loss_function(out_path, cfg, 
                                                                 opt_with_mm=False)
        elif objective_function == "quantum":
            obj_fun = MultiscaleLossFunction.build_loss_function(out_path, cfg, 
                                                                 opt_with_md=False)
        else:
            raise NotImplementedError()


        if (opt_method == "bayes_opt"):
            ret = BayesianOptimization(out_path=out_path, 
                                       cfg=cfg, loss_fun=obj_fun,
                                       cfg_file=cfg,
                                       section="OPT")
        elif (opt_method == "cmaes"):
            ret = CMAES(out_path=out_path, 
                                       cfg=cfg,
                                       cfg_file=cfg,
                                       section="OPT")
        else:
            raise NotImplementedError()

        return ret
    
class BayesianOptimization(OptimizationAlgorithm):
    
    @args_from_configfile
    def __init__(self, out_path, cfg, loss_fun,
                 kern="", 
                 max_fevals=200, 
                 init_fevals=100, 
                 par_evals_init=8,
                 par_evals_opt=4,
                 **kwargs):
        
        super().__init__(cfg_file=cfg, section="OPT")
        print(self.constraints)
        print(self.constraints.bounds)
        print(self.constraints.lower_bounds)
        self.loss = loss_fun
        self.max_fevals = max_fevals
        self.init_fevals = init_fevals
        self.par_evals_init = par_evals_init
        self.par_evals_opt = par_evals_opt
        self.out_path = out_path

        self.df = pd.DataFrame(columns=["x1", "x2", "x3", "x4", "obs"])
        self.batch_queue = Batch(out_path, self.loss, self.df)
        self.gp_mean = 10


        self.cube_bounds = [(0, 10), (0, 10), (0, 10), (0, 10)]

        # Scale x_i from bounds to cube_bounds using min-max transformation
        self.scale_x = True

        # Build model from log scaled y
        self.scale_y = True
        
        # Transform bounds for pycma
        lower_bounds = []
        upper_bounds = []

        for bound in self.cube_bounds:
            lower_bounds.append(bound[0])
            upper_bounds.append(bound[1])
        
        self.lower_bounds = lower_bounds
        self.upper_bounds = upper_bounds
        
        k =  RBF(length_scale=[1,1,1,1],
                length_scale_bounds=(1e-1, 0.9e1)) + \
        WhiteKernel(noise_level=0.1, noise_level_bounds=(1e-4, 5e-3))
        
        gp_params = {
            'kernel': k,
            'n_restarts_optimizer': 50,
        }
        
        # Model fallback for useful error messages
        self._model = GaussianProcessRegressor(**gp_params)
        
        
    def optimize(self):
        
        if self.batch_queue.pending_evaluations():
            # if optimization is continued and there are pending evaluations
            print("Recovering optimization run:", self.out_path)
            self._read_batch_file()
            self.batch_queue.process_queue(self.par_evals_init, self.df)
        else:
            # or starting a new optimization from a new Latin hypercube design
            self._initial_sampling()
            
        self._build_model()

        print(len(self.df.values), "/", self.max_fevals)

        for iter in range(len(self.df.values), self.max_fevals, self.par_evals_opt):
            # make new suggestions by optimizing the acquisition function
            X_sugg = self._suggest(batch_size=self.par_evals_opt)
            
            for iter, x in enumerate(X_sugg):
                
                id = int(self.df.index.max())+1
                point = (x, id)
                print("EVAL at:", point)
                self.batch_queue._put(point)
                xi = list(x)
                xi.append(-1)
                self.df.loc[id] = xi # init not yet simulated x with -1
                
            # and process the new observations
            self.batch_queue.process_queue(self.par_evals_init, self.df)

            # update model for next iteration
            self._build_model()

    def _initial_sampling(self):
        X = lh_sampling(self.init_fevals, self.constraints.bounds, optimize=True)

        # put initial points in queue and evaluate them in parallel
        for iter, x in enumerate(X):
            id = iter
            point = (x, id)
            self.batch_queue._put(point)
            x.append(-1)
            self.df.loc[id] = x # init not yet simulated x with -1
        
        self.batch_queue.process_queue(self.par_evals_init, self.df)
    
    def _suggest(self, batch_size=1):
        """
        Minimize the acquisition function using CMA-ES to suggest,
        where the model should be evaluated next.
        """
        
        kappas = [2.57]
        suggestions = []

        if batch_size > 1:
            # draw kappas from exponential distribution
            kappas = np.random.exponential(scale=2, size=batch_size)

        for i in range(batch_size):
            # start from arith. mean of lower and upper bounds
            mu0 = [(xl+xu)/2 for (xl, xu) in zip(self.lower_bounds, self.upper_bounds)]
            sig0 = 2 # optimum should be in mu0+3sig0

            arg = [self._model, kappas[i]]

            # minimize acquisition function
            x = cma.fmin(BayesianOptimization._lcb, mu0, sig0, args=arg, 
                         options={'BoundaryHandler': cma.BoundPenalty, 
                                  'bounds': [self.lower_bounds,
                                             self.upper_bounds]})
            suggestions.append(self._rescale(x[0]))

        return suggestions
    
  
    def _build_model(self):
        """
        Builds a GP out of the simulation loss values
        """
        X = []
        Y = []

        for row in self.df.values:
            # ignore failed simulations
            if row[-1] != -1:
                if self.scale_x:
                    scaled_x = self._scale_to_cube(row[:-1])
                else:
                    scaled_x = row[:-1]                    
                X.append(scaled_x)
                
                if self.scale_y:
                    # Values become < 0, so no bias necessary
                    scaled_y = np.log(row[-1])
                else:
                    # Add bias due to gpr zero mean
                    scaled_y = row[-1]+self.gp_mean
                Y.append(scaled_y)

        self._model.fit(X, Y)
        
    def _lcb(x, gp, kappa):
        """
        Lower Confidence Bound acquisition function
        """
        mean, std = gp.predict([x], return_std=True)

        return np.reshape(mean - kappa*std, 1)[0]
    
    def _scale_to_cube(self, x):
        return scale(x, self.cube_bounds, self.constraints.bounds)
        
    def _rescale(self, x):
        return scale(x, self.constraints.bounds, self.cube_bounds)
        
    def _read_batch_file(self):
        df_path = path.join(self.out_path, "batch.csv")
        df = pd.read_csv(df_path, index_col=0, encoding="utf-8-sig")

        for index, row in df.loc[df["obs"]==-1].iterrows():
            x = row[:-1]
            point = (x, index)
            self.batch_queue._put(point)
        self.df = df
        self.batch_queue.df = self.df
        
class CMAES(OptimizationAlgorithm):

    def __init__(self, out_path, cfg,
                 max_fevals=200, 
                 **kwargs):
        self.loss = MultiscaleLossFunction.build_loss_function(out_path, cfg)
        self.max_fevals = max_fevals
        self.out_path = out_path

        self.df = pd.DataFrame(columns=["x1", "x2", "x3", "x4", "obs"])
        self.batch_queue = Batch(out_path, self.loss, self.df)

        self.bounds = [(0.15, 0.52), (0.05, 0.25), (0.15, 0.70), (0.01, 0.35)]
        self.cube_bounds = [(0, 10), (0, 10), (0, 10), (0, 10)]
        
        self.scale_x = True
        self.scale_y = True
        
        # Transform bounds for pycma
        lower_bounds = []
        upper_bounds = []
        
        for bound in self.cube_bounds:
            lower_bounds.append(bound[0])
            upper_bounds.append(bound[1])
        
        self.lower_bounds = lower_bounds
        self.upper_bounds = upper_bounds
    
    def optimize(self):
        mu0 = [(xl+xu)/2 for (xl, xu) in zip(self.lower_bounds, self.upper_bounds)]
        sig0 = 2

        es = cma.CMAEvolutionStrategy(mu0, sig0,                         
                                      {'BoundaryHandler': cma.BoundPenalty, 
                                               'maxfevals': self.max_fevals-1,
                                               'bounds': [self.lower_bounds,
                                                          self.upper_bounds]})


        i=0
        while not es.stop():
            solutions = es.ask()
            ids = []
            for x in solutions:
                x = self._rescale(x.tolist())
                point = (x, i)
                ids.append(i)
                self.batch_queue._put(point)
                x.append(-1)
                self.df.loc[i] = x
                i = i+1
            
            self.batch_queue.process_queue(100, self.df)

            observations = self.get_observations(ids, scale=True)

            es.tell(solutions, observations)
            es.disp()
            es.result_pretty()

    def _scale_to_cube(self, x):
        return scale(x, self.cube_bounds, self.bounds)
        
    def _rescale(self, x):
        return scale(x, self.bounds, self.cube_bounds)

    def get_observations(self, ids, scale=False):
        observations = []
        for id in ids:
            obs = self.df.loc[id].obs
            if scale:
                obs = np.log(obs)
            observations.append(obs)
        return observations

class Batch:
    """
    A batch queue in which one may put parameter sets that will be evaluated
    in parallel on the specified objective function.

    A pandas DataFrame is used to maintain the observations after program
    abortion and to make them available to the caller.
    """

    def __init__(self, out_path, loss_fun, df):
        self.loss = loss_fun
        self.queue = Queue()
        self.res_queue = Queue()
        self.file_path = path.join(out_path, "batch.csv")
        self.df = df
        
    def pending_evaluations(self):
        if path.exists(self.file_path):
            return True
        return False
        
    def check_file(self):
        if not exists(self.file_path):
            self.df.to_csv(self.file_path)
        else:
            return True
               
    def _put(self, elem):
        self.queue.put(elem)
        
    def process_queue(self, max_parallel, df):
        """
        Processes the elements in queue q with max_parallel jobs in parallel
        q items are pairs (x, name)
        """

        cnt_parallel = 0
        threads = []
        
        while not self.queue.empty():
            
            while cnt_parallel < max_parallel and not self.queue.empty():
                # create a thread for each pending evaluation
                item = self.queue.get()
                kw = dict(xi=item[0], feval_number=item[1], 
                          res_queue=self.res_queue)
                t = threading.Thread(target=self.loss.get_function_value,
                                 kwargs=kw)
                t.start()
                threads.append(t)
                cnt_parallel += 1
                
            for thread in threads:
                # join the threads and collect the results
                thread.join()
                self._update_file()
                
            cnt_parallel = 0
            threads = []
                    
        # and reset the queue
        self.queue = Queue()
        self.res_queue = Queue()
            
        # caller extracts observations from df
        return None
    
    def _update_file(self):
        """
        Updates observation values in df
        """
        indices, xs, obss = self._to_array()

        for ind, x, obs in zip(indices, xs, obss):    
            self.df.loc[ind, "obs"] = np.reshape(obs, 1)[0]

        self.df.to_csv(self.file_path)
        
    
    def _to_array(self):
        q = copy.copy(self.res_queue)
        obs = []
        x = []
        indices = []
        
        while not q.empty():
            i = q.get()
            indices.append(i[0])
            x.append(i[1])
            obs.append(i[2])

        return (indices, x, obs)

    



