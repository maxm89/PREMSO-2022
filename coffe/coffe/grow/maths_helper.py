# -*- coding: utf-8 -*-

from math import sqrt

class Constraints:
    """
    Class representation of the parameter space constraints.

    Constraints can be accessed either as

    - self.bounds:
    List of tuples [(lb, ub)] where each tuple represents the constraints
    of one dimension

    or as

    - self.lower_bounds/ self.upper_bounds 
    2-tuple of lists ([lbs],[ubs]) where one list contains the lower bounds
    for all dimensions and one list contains all upper bounds
    """

    def __init__(self, bounds):
        """
        Arguments:
        bounds : list of tuples (lb, ub)
        """
        self.bounds = bounds
        self.gen_bound_tuple()

    def gen_bound_tuple(self):
        """
        converts the bounds into a single tuple of lower bounds and 
        upper bounds lists (lbs, ubs)

        """
        lower_bounds, upper_bounds = [], []
        for bound in self.bounds:
            lower_bounds.append(bound[0])
            upper_bounds.append(bound[1])

        self.lower_bounds = lower_bounds
        self.upper_bounds = upper_bounds

    

def norm(v):
    """ calculates euclidean norm of vector v """
    norm_v = 0
    for i in range(len(v)):
        norm_v += pow(v[i], 2)
    norm_v = sqrt(norm_v)
    return(norm_v)

def scale(x, new, old):
    scaled = []
    for dim in range(len(old)):
        scaled.append(scale_dim(x[dim], old[dim], new[dim]))
    return scaled

def scale_dim(x, old, new):
    x = ((x-old[0])/(old[1]-old[0]))*(new[1]-new[0])+new[0]
    return x
