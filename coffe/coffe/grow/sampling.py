# -*- coding: utf-8 -*-
import copy
import math
import matplotlib.pyplot as plt
import numpy as np
from pyDOE import lhs
from scipy.spatial.distance import cdist


def random_sampling(dim, num_points):
    pass

def lh_sampling(num_points, bounds, n_dim = None, optimize=False, tries=1):
    '''
    Generates a latin hypercube design with <num_points> points in 
    <n_dim> dimensions. <len(bounds)> needs to match <n_dim>.
    If <tries> > 1, <tries> designs are created and the best w.r.t. the 
    min distance will be returned.
    bounds is a list of tuples (lb, ub)
    '''

    assert(num_points > 1)

    #bounds = [(-5.,1.), (0,1), (5,10)]
    if bounds is None:
        bounds = [(0, 1)]
        
    num_bounds = len(bounds)
    if n_dim is None or n_dim < num_bounds:   
        n_dim = num_bounds
    else:
        if num_bounds < n_dim:
            last = bounds[num_bounds-1]
            reps = [last] * (n_dim - num_bounds)
            bounds = bounds + reps
            
    dim = np.array(bounds)
    
    solutions = []
    solutions_fitness = []

    for _ in range(tries):
        X = _constraint_lhs(n_dim, dim, num_points)
        solutions.append(X)
        solutions_fitness.append(min_distance(X))
        
    imin = np.argmax(solutions_fitness)
    
    if optimize:
        return _sa_design(solutions[imin])
    else:
        return solutions[imin]

def _constraint_lhs(n_dim, dims, num_points):
    u = lhs(n_dim, samples=num_points)
    # Map the uniform lhs into space constrained by bounds
    return [list(x) for x in (u * np.diff(dims).T + dims[:, 0])]

def plot_design(X):
    xs = [x[0] for x in X]
    ys = [x[1] for x in X]
    
    plt.scatter(xs, ys)

def _maximin_distance(X):
    pass

def min_distance(X):
    dist_matrix= cdist(X, X)
    # replace the zeros on the diagonal
    np.fill_diagonal(dist_matrix, np.inf)
    # distance along all axis
    return np.min(dist_matrix, (0, 1))

def _sa_design(X):
    '''
    Simulated Annealing optimization of X w.r.t. min_distance
    '''

    def _perturbate(sol):
        '''
        swap a single coordinate from two points at random
        '''
        X = copy.deepcopy(sol)
        ind_a = np.random.randint(0, len(X))
        ind_b = np.random.randint(0, len(X))
        comp = np.random.randint(0, len(X[0]))
        X[ind_a][comp], X[ind_b][comp] = X[ind_b][comp], X[ind_a][comp]
        return X
    
    def _accept(new_f, old_f, T):
        '''
        Accept worse solutions (new < old) at higher propability when the
        temperature is high
        '''
        if new_f > old_f:
            return True
        else:
            # ap is at most 1, so tune the exclusive interval bound
            # to increase the propability that a solution that doesnt
            # change the min distance is accepted
            r = np.random.uniform(0, 2)
            # exponent should be negated for minimization
            ap = math.exp((new_f - old_f) / T)
            #print(ap)
            return r <= ap
        
    best_X = copy.deepcopy(X)
    best_f = min_distance(best_X)
    print(f'old f:{best_f}')
    
    T = 1.0
    T_min = 0.0000001
    alpha = 0.9
    
    while T > T_min:
        
        for i in range(1, 100):
            
            new_X = _perturbate(best_X)
            new_f = min_distance(new_X)
            
            if _accept(new_f, best_f, T):
                best_X, best_f = new_X, new_f
                
        T *= alpha
    
    print(f'new f:{best_f}')
    return best_X
            
        
    