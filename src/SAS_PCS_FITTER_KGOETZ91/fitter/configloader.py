# -*- coding: utf-8 -*-
"""
Created on Wed May  8 10:22:49 2024

@author: klaus
"""

import numpy as np
import pandas as pd
from numbers import Number
from math import isnan

from helpers.functions import string_split,is_number

from bumps.parameter import Parameter,Constraint,Operator
from os.path import join

class PDParameter:
    
    def __init__(self,name,pdtype):
        self.name = name
        self.value = pdtype

class ParameterSet:
    
    def __str__(self):
        printlist = ""
        for i in self._parameters.keys():
            par = self._parameters[i]
            printlist += f"{i}, {par.name}, {par.value}, {par.bounds}, {par.fixed}\n"
        return f"{self._name}\n"+printlist
    
    def __repr__(self):
        printlist = []
        for i in self._parameters.keys():
            printlist.append(f"Parameter({i})")
        return f"{self._name}\n"+np.array(printlist).__str__()+"\n"
    
    def __getitem__(self,sliced):
        result = self._parameters.__getitem__(sliced)
        return result
    
    def __iter__(self):
        return self._parameters.__iter__()
    
    def __contains__(self,item):
        return (item in self._parameters.keys())
    
    def _perform_single_operation(self,x1,x2,operation):
        if operation == "+":
            new_param = x1+x2
        elif operation == "-":
            new_param = x1-x2
        elif operation == "*":
            new_param = x1*x2
        elif operation == "/":
            new_param = x1/x2
        elif operation == "^":
            new_param = x1**x2
        else:
            raise KeyError(f"Unknown operation type: {operation}")
        
        return new_param
    
    def _find_par(self,parent_set,parstring):
        if is_number(parstring):
            return float(parstring)
        else:
            return parent_set[parstring]
    
    def _parse_simple_string(self,to_parse,parent_set):
        order_operations = ["^","/","*","+","-"]
        d_params, signs = string_split(to_parse,order_operations)
        signs = list(signs)
        
        d_params = [self._find_par(parent_set,i) for i in d_params]
        
        for operation in order_operations:
            occurences = np.array(signs)==operation
            if any(occurences):
                for ctr,sign in enumerate(signs):
                    if occurences[ctr]:
                        d_params[ctr] = self._perform_single_operation(
                            d_params[ctr],d_params.pop(ctr+1),signs.pop(ctr))
                        
        return d_params[0]
        
    
    def _parse_parameter_math(self,to_parse,parent_set):
        obrackets = np.array(["(","[","{"])
        cbrackets = np.array([")","]","}"])
        
        if any(e in to_parse for e in obrackets):
            temp_par_number =0
            string_list = []
            ob_list = []
            temp_string = ""
            for character in to_parse:
                if character in obrackets:
                    string_list.append(temp_string)
                    ob_list.append(character)
                    temp_string = ""
                elif character in cbrackets:
                    if ob_list.pop(-1)==obrackets[cbrackets==character][0]:
                        temp_par_number += 1
                        temp_par = self._parse_simple_string(temp_string,parent_set)
                        parent_set.add(f"temp_par{temp_par_number}",temp_par)
                        temp_string = string_list.pop(-1)+f"temp_par{temp_par_number}"
                    else:
                        raise KeyError(f"Paranthesis error: Expected"+
                                       f"{cbrackets[obrackets]==ob_list[-1][0]}"+
                                       f" but found {character}")
                else:
                    temp_string += character
            result_param = self._parse_simple_string(temp_string,parent_set)
        else:
            result_param = self._parse_simple_string(to_parse,parent_set)
        
        return result_param
    
    def _create_new_parameter(self,line,parent_set):
        i = line
        name = i[0]
        if isinstance(i[1],str):
            if i[1] in ["lognormal", "gaussian"]:
                new_param = PDParameter(name,i[1])
                self._parameters[name]= new_param
            elif any(e in i[1] for e in ["+","-","/","*","^"]):
                new_param = self._parse_parameter_math(i[1],parent_set)
                bounds = (-np.inf,np.inf)
                new_param.name = name
                new_param.range(bounds[0],bounds[1])
                new_param.fixed = True
                self._parameters[name] = new_param
            else:
                self._parameters[name]=parent_set[i[1]]
        elif not isnan(i[1]):
            bounds=(float(i[2]),float(i[3]))
            fixed=(i[4]==1)
            new_param = Parameter(name=name,value=i[1])
            new_param.range(bounds[0],bounds[1])
            new_param.fixed=fixed
            self._parameters[name]=new_param
    
    def _create_parameters(self,dataframe,parent_set):
        for line in dataframe.values:
            self._create_new_parameter(line,parent_set)
        
    def __init__(self,name,dataframe,parent_set=None):
        self._name = str(name)
        self._parameters = {}
        if type(parent_set) == type(None):
            parent_set=self._parameters
        elif not isinstance(parent_set,ParameterSet):
            raise TypeError("Parent Parameter Set needs to be None or a valid"+
                            "Parameter set")
        self._create_parameters(dataframe,parent_set)
        
    def name(self):
        return str(self._name)
    
    def add(self,key,value):
        if isinstance(value,Parameter) or isinstance(value,Operator):
            self._parameters[key]=value
        else:
            raise TypeError("Only bumps Parameters can be added to a Parameterset")
    
class Setup:
    
    def __init__(self,setupsheet):
        self._bsetup = BumpsSetup(setupsheet)
        self._msetup = ModelSetup(setupsheet)

class ModelSetup:
    
    def __init__(self,setup_sheet):
        self._q_limits = [(i,j) for i,j in zip(setup_sheet['Qmin'],setup_sheet['Qmax'])
                          if (isinstance(i,Number) and isinstance(j,Number) and
                              not isnan(i) and not isnan(j))]
        self._model_names = [i for i in setup_sheet['Modelname'] if isinstance(i,str)]
        self._data_files = [i for i in setup_sheet['Data Files'] if isinstance(i,str)]
        self._kernel_strings = [i for i in setup_sheet['Kernels'] if isinstance(i,str)]
    
    def get_setups(self):
        return list(zip(self._model_names,self._data_files,self._q_limits,
                        self._kernel_strings))
    
    def get_modelnames(self):
        return np.array(self._model_names)
    
    def get_datasets(self):
        return np.array(self._data_files)
    
    def get_kernels(self):
        return np.array(self._kernel_strings)

class BumpsSetup:
    
    def _create_bumps_string(self):
        result = ""
        for i,j in self._bumps_parameters:
            if isinstance(j,str) or (isinstance(j,Number) and not isnan(j)):
                if i =="store":
                    self._storage_path =f"{j}"
                result += f"--{i}={j} "
            else:
                result += f"--{i} "
        return result
    
    def __init__(self,setup_sheet):
        
        self._storage_path = "fit"
        self._bumps_parameters = [(i,j) for i,j in zip(setup_sheet['Bumps Parameters'],
                                                       setup_sheet['Value'])
                                  if isinstance(i,str)]
        self._bumps_string = self._create_bumps_string()
    
    def storage_path(self):
        return self._storage_path
    
    def get_bumps(self,model_file="model.py",config_file="config.xlsx"):
        logfile="log.log"
        return f"{self._bumps_string} {model_file} {config_file} > {join(self._storage_path,logfile)}"
        

class ConfigLoader:

    def __init__(self,filename):
        self._sheet_list = pd.read_excel(filename,sheet_name=None)
        self._sets = None
        
    def get_sheet(self,indicator):
        sheet_copy = pd.DataFrame(self._sheet_list[indicator])
        return sheet_copy

    def get_parameter_sets(self):
        return np.array(self._sets)

    def create_parametersets(self):
        self._sets = {}
        for parameter_sheet in list(self._sheet_list)[1:]:
            colums = self._sheet_list[parameter_sheet].shape[1]+1
            if parameter_sheet == "Global Parameters":
                name = f"{parameter_sheet}"
                frame = pd.DataFrame(self._sheet_list[parameter_sheet])
                self._sets[name]=ParameterSet(name,frame)
            else:
                self._sets[parameter_sheet]={}
                for i in range(int(colums/6)):
                    start = i*6
                    end = start+5
                    frame = pd.DataFrame(self._sheet_list[parameter_sheet].iloc[:,start:end])
                    name = f"{parameter_sheet}_{list(frame)[0]}"
                    self._sets[parameter_sheet][name]=(ParameterSet(name,frame,
                                                        self._sets["Global Parameters"]))
        return self._sets
