# -*- coding: utf-8 -*-
"""
Created on Wed May  8 17:10:35 2024

@author: klaus
"""

import subprocess
from os.path import isdir
from os import makedirs

from fitter.configloader import ConfigLoader,BumpsSetup

config_file = "example.xlsx"
model_file = "model.py"


config = ConfigLoader(config_file)
bumpsetup = BumpsSetup(config.get_sheet("Setup"))
storage_path = bumpsetup.storage_path()

if not isdir(storage_path):
    makedirs(storage_path)

bumpstring = f"bumps {bumpsetup.get_bumps(model_file,config_file)}"
power_shell_path = r'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe'
process_string = f'{power_shell_path} {bumpstring}'

print(process_string)

subprocess.call(process_string, shell=True)