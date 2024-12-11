# -*- coding: utf-8 -*-
"""
Created on Wed May  8 13:00:16 2024

@author: klaus
"""

import numpy as np

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def string_split(to_split,delimiters):
    
    substrings = []
    used_delimiters = []
    new_string = ""
    for i in to_split:
        if i in delimiters:
            if len(new_string)>0:
                substrings.append(new_string)
                new_string=""
                used_delimiters.append(i)
        else:
            new_string += i
    if len(new_string)>0:
        substrings.append(new_string)
            
    return substrings,used_delimiters

def load_data(filename,xmin=-np.inf,xmax=np.inf):
    
    x = []
    y = []
    e = []
    
    with open(filename,'r') as inputfile:
        for line in inputfile:
            if not line.startswith('#'):
                data = list(line.strip().split())
                x.append(float(data[0]))
                y.append(float(data[1]))
                if len(data) == 3:
                    e.append(float(data[2]))
                else:
                    e.append(np.sqrt(float(data[1])))
         
    x = np.array(x)
    y = np.array(y)
    e = np.array(e)
         
    y = y[x>=xmin]
    e = e[x>=xmin]
    x = x[x>=xmin]
    
    y = y[x<=xmax]
    e = e[x<=xmax]
    x = x[x<=xmax]

    return x,y,e

def load_grasp_data(filename,xmin=-np.inf,xmax=np.inf):
    
    x = []
    y = []
    e = []
    eq = []
    
    with open(filename,'r') as inputfile:
        for line in inputfile:
            data = list(line.strip().split())
            if len(data) == 4:
                try:
                    x.append(float(data[0]))
                    y.append(float(data[1]))
                    e.append(float(data[2]))
                    eq.append(float(data[3]))
                except:
                    pass
            elif len(data) == 3:
                try:
                    x.append(float(data[0]))
                    y.append(float(data[1]))
                    e.append(float(data[2]))
                    eq.append(0.01*float(data[0]))
                except:
                    pass
            elif len(data) == 2:
                try:
                    x.append(float(data[0]))
                    y.append(float(data[1]))
                    e.append(np.sqrt(float(data[1])))
                    eq.append(0.01*float(data[0]))
                except:
                    pass

            
    x = np.array(x)
    y = np.array(y)
    e = np.array(e)
    eq = np.array(eq)
         
    y = y[x>=xmin]
    e = e[x>=xmin]
    eq = eq[x>=xmin]
    x = x[x>=xmin]
    
    
    y = y[x<=xmax]
    e = e[x<=xmax]
    eq = eq[x<=xmax]
    x = x[x<=xmax]

    return x,y,e,eq


def linear_function(x, m, b):
    return m * x + b


def gaussian(x, x0, sigma, area, const):
    prefactor = area / np.sqrt(2 * np.pi * sigma * sigma)
    exponent = -0.5 * np.power(((x - x0) / sigma), 2)
    gaussian = prefactor * np.exp(exponent) + const

    return gaussian


def lin_interpolate(x1, y1, e1, x2, y2, e2, x_det):
    a = (y2 - y1) / (x2 - x1)
    ea = np.sqrt((e1 * e1) + (e2 * e2))
    eb = np.sqrt((e1 * e1) + (e2 * e2) + (ea * ea))
    b = 0.5 * (y2 + y1 - a * (x1 + x2))
    ydet = a * x_det + b
    edet = np.sqrt((x_det * x_det * ea * ea) + (eb * eb))
    return x_det, ydet, edet


def spline_data(x0, data):
    x1 = np.array(data[0])
    y1 = np.array(data[1])
    e1 = np.array(data[2])

    y2 = []
    e2 = []

    for x in x0:
        eps = x * 1e-4
        diff = np.abs(np.subtract(x1, x))
        if diff.min() < eps:
            eq_ind = np.argmin(diff)
            y2.append(y1[eq_ind])
            e2.append(e1[eq_ind])
        else:
            min_ind = np.where(x1 < x)[0]
            max_ind = np.where(x1 > x)[0]
            if len(min_ind) == 0:
                xx1 = x1[max_ind[0]]
                xx2 = x1[max_ind[1]]
                yy1 = y1[max_ind[0]]
                yy2 = y1[max_ind[1]]
                ee1 = e1[max_ind[0]]
                ee2 = e1[max_ind[1]]
                xdet, ydet, edet = lin_interpolate(xx1, yy1, ee1, xx2, yy2, ee2, x)
            elif len(max_ind) == 0:
                xx1 = x1[min_ind[-1]]
                xx2 = x1[min_ind[-2]]
                yy1 = y1[min_ind[-1]]
                yy2 = y1[min_ind[-2]]
                ee1 = e1[min_ind[-1]]
                ee2 = e1[min_ind[-2]]
                xdet, ydet, edet = lin_interpolate(xx1, yy1, ee1, xx2, yy2, ee2, x)
            else:
                xx1 = x1[max_ind[0]]
                yy1 = y1[max_ind[0]]
                ee1 = e1[max_ind[0]]
                xx2 = x1[min_ind[-1]]
                yy2 = y1[min_ind[-1]]
                ee2 = e1[min_ind[-1]]
                xdet, ydet, edet = lin_interpolate(xx1, yy1, ee1, xx2, yy2, ee2, x)

            y2.append(ydet)
            e2.append(edet)

    return x0, y2, e2