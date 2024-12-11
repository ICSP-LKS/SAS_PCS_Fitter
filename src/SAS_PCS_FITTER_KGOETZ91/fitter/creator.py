# -*- coding: utf-8 -*-
"""
Created on Mon May 13 08:58:03 2024

@author: klaus
"""

from sasmodels.core import load_model
from sasmodels.bumps_model import Model

import pandas as pd
pd.io.formats.excel.ExcelFormatter.header_style = None

import numpy as np

class Creator:
    
    def _standard_setup(self):
        result = {"Modelname": ["Model1","","","",""],
                  "Data Files": ["path/to/data","","","",""],
                  "Qmin": [1e-4,"","","",""],
                  "Qmax": [10,"","","",""],
                  "Kernels": [self._modelstring,"","","",""],
                  "Bumps Parameters": ["fit", "cov", "store", "overwrite", "noshow"],
                  "Value": ["amoeba", "", "fit", "", ""],
                  "Commentary": ["Sets the fit algorithm used",
                                 "Calculate the covariance Matrix at end of fit",
                                 "Path to where to store the data",
                                 "needed to overwrite data in store directory",
                                 "If active no plot windows are generated at the end of fit"]
                  }
        return result
    
    def _standard_glob(self):
        result = {"Global Parameters": ["Example"],
                  "value": [1],
                  "lbound": [-np.inf],
                  "ubound": [np.inf],
                  "fixed": [1],
                  "Commentary": ["Exemplary global parameter"],
                  }
        return result
    
    def _pars_to_dict(self,dict_name,pars):
        result = {dict_name:[],"value":[],"lbound":[],"ubound":[],"fixed":[]}
        for par in pars:
            limits = par.bounds.to_dict()["limits"]
            result[dict_name].append(par.name)
            result["value"].append(par.name)
            result["lbound"].append(limits[0])
            result["ubound"].append(limits[1])
            result["ubound"].append(1 if par.fixed else 0)
            
            if "pd_nsigma" in par.name:
                result[dict_name].append(par.name[:-6]+"type")
                result["value"].append("lognorm")
                result["lbound"].append("")
                result["ubound"].append("")
                result["ubound"].append("")
        
        return result
        
    def _create_model_dict(self):
        parameters = self._model.parameters()
        setup_pars = ["background", "scale"]
        setup = {"Setup":[],"value":[],"lbound":[],"ubound":[],"fixed":[]}
        
        result =[]
        
        for setup_par in setup_pars:
            par = parameters.pop(setup_par)
            setup["Setup"].append(setup_par)
            setup["value"].append(par.value)
            limits = par.bounds.to_dict()
            setup["lbound"].append(limits["limits"][0])
            setup["ubound"].append(limits["limits"][1])
            setup["fixed"].append(1 if par.fixed else 0)
        
        result.append(setup)
        
        par_names = list(parameters.keys())
        fractions = [list(i.split("_"))[-1] for i in par_names
                     if list(i.split("_"))[-1] == "scale"]
        if len(fractions)>1:
            uniques = [list(i.split("_"))[0] for i in par_names
                         if list(i.split("_"))[-1] == "scale"]
            for i in range(len(fractions)):
                t_pars = [parameters[j] for j in par_names
                          if list(j.split("_"))[0] in uniques[i]]
                result.append(self._pars_to_dict(f"F{i+1}",t_pars))
        else:
            result.append(self._pars_to_dict("Fraction",parameters))
            
        return(result)
    
    def __init__(self, modelstring):
        self._modelstring = modelstring
        self._model = Model(load_model(modelstring))
        self.create_config_file()
        
    def create_config_file(self,filename="config.xlsx"):
        setup = pd.DataFrame(self._standard_setup())
        glob = pd.DataFrame(self._standard_glob())
        model = self._create_model_dict()
        with pd.ExcelWriter("test.xlsx") as writer:
            setup.to_excel(writer,sheet_name="Setup",index=False)
            glob.to_excel(writer,sheet_name="Global Parameters",index=False)
            for frac in model:
                pd.DataFrame(frac)
                
        
a = Creator("sphere+sphere*sphere")

# df1 = pd.DataFrame({"1":[1],"2":[2],"3":[3],"4":[4]})
# df2 = pd.DataFrame([[1,2,3,4],[5,6,7,8]], columns=["a","b","","d"])

# with pd.ExcelWriter("test.xlsx") as writer:
#     df1.to_excel(writer,sheet_name="1",index=False)
#     df2.to_excel(writer,sheet_name="2",startcol=0,index=False)
#     df2.to_excel(writer,sheet_name="2",startcol=7,index=False)
