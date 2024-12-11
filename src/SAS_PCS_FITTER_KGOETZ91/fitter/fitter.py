# -*- coding: utf-8 -*-
"""
Created on Wed May  8 11:21:42 2024

@author: klaus
"""

from fitter.configloader import ConfigLoader, BumpsSetup, ModelSetup
from helpers.functions import load_data, load_grasp_data

from sasmodels.bumps_model import Model, Experiment, Data1D
from sasmodels.core import load_model
from bumps.parameter import Parameter

import matplotlib.pyplot as plt

from bumps.names import FitProblem

class Submodel:

    def __init__(self,name,dataset,parameterset,model):
        self._name = name
        self._model = model
        self._data = dataset
        self._params = parameterset
        self.create_experiment()
        
    def create_experiment(self):
        for fraction in self._params:
            for modelname in self._params[fraction]:
                par = self._params[fraction][modelname]
                if "pd_type" in modelname:
                    setattr(self._model,modelname,par.value)
                else:
                    opar = self._model.parameters()[modelname]
                    setattr(self._model,modelname,par)
        
        self._experiment = Experiment(data=self._data,model=self._model,name=self._name)
        
    def get_experiment(self):
        return self._experiment
    
class SASFitter:
    
    def _create_models(self):
        
        setups = self._modelsetup.get_setups()
        for name,file,q_limits,kernel in setups:
            parameterset = self._parametersets[name]
            x,y,e,eq = load_grasp_data(file,q_limits[0],q_limits[1])
            data = Data1D(x,y,eq,e)
            model = Model(load_model(kernel))
            self._models.append(Submodel(name,data,parameterset,model))
            
            # if name == "SANS":
            #     print(f"{name}\n {file}\n {q_limits}\n {kernel}\n\n")
            #     excl_list = list(range(5,11))+["mphi","mtheta","M0","up"]
            #     for paramname in model.parameters():
            #         par = model.parameters()[paramname]
            #         if not any(str(e) in paramname for e in excl_list):
            #             print(f"{par}: {par.value} {par.bounds} {par.nllf()}")
        
    def __init__(self,configfile):
        self._config = ConfigLoader(configfile)
        self._bumpsetup = BumpsSetup(self._config.get_sheet("Setup"))
        self._modelsetup = ModelSetup(self._config.get_sheet("Setup"))
        self._parametersets = self._config.create_parametersets()
        
        # for pset in self._parametersets:
        #     if pset == "Global Parameters":
            
        #         for param in self._parametersets[pset]:
        #             par = self._parametersets[pset][param]
        #             if str(par.nllf()) == "inf":
        #                 print(f"{pset} {param}\n")
                    
        #             # print(f"\nName: New:{par.name}")
        #             # print(f"Value: New:{par.value}")
        #             # print(f"Bounds: New:{par.bounds}")
        #             # print(f"Fittable: New:{par.fittable}")
        #             # print(f"Fixed: New:{par.fixed}")
        #             # print(f"NLLF: New:{par.nllf()}")
        #     else:
        #         for paramsubset in self._parametersets[pset]:
                    
        #             print(f"\n {paramsubset}\n")
        #             for param in self._parametersets[pset][paramsubset]:
        #                 par = self._parametersets[pset][paramsubset][param]
        #                 if type(par) == type(Parameter(0)):
        #                     if str(par.nllf()) == "inf":
        #                         print(f"{pset} {param}\n")
                        
        #                 # print(f"{pset} {param}\n")
                        
        #                 # print(f"\nName: New:{par.name}")
        #                 # print(f"Value: New:{par.value}")
        #                 # print(f"Bounds: New:{par.bounds}")
        #                 # print(f"Fittable: New:{par.fittable}")
        #                 # print(f"Fixed: New:{par.fixed}")
        #                 # print(f"NLLF: New:{par.nllf()}")
        

        self._models = []
        self._create_models()
        
        self._experiments = [i.get_experiment() for i in self._models]
       
        self._problem = FitProblem(self._experiments)
        
    def get_problem(self):
        return self._problem
    
    def plot_models(self):
        plt.clf()
        for exp in self._experiments:
            exp.plot()