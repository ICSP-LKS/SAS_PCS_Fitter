# -*- coding: utf-8 -*-
"""
Created on Wed May  8 10:42:18 2024

@author: klaus
"""
import sys
import matplotlib.pyplot as plt

from src.fitter.fitter import SASFitter

a = SASFitter(sys.argv[1])

problem = a.get_problem()