import law
import os
import subprocess
import importlib.util
import ROOT
import re
import uproot
from optparse import OptionParser
from collections import OrderedDict as od
from importlib import import_module
import glob
import yaml
import errno
import shutil

import pandas
import numpy as np
import awkward as ak

from commonTools import *
from commonObjects import *

from Datacard.datacard import *

from framework import Task
from framework import HTCondorWorkflow

# Function to safely create a directory
def safe_mkdir(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise
        
def convert_boolean_string(string):
    if (string == "True") or (string == "true") or (string == True):
        return True
    else:
        return False
    
class PrepareTheDirectory(law.Task):#(law.Task): #(Task, HTCondorWorkflow, law.LocalWorkflow):
    output_dir = law.Parameter(default = '', description="Path to the output directory")
    variable = law.Parameter(default="", description="Variable to be used")
    year = law.Parameter(default='2022', description="Year")
    
    # htcondor_job_kwargs_submit = {"spool": True}
    
    def requires(self):
        
        if self.variable == '':
            configYamlPath = os.environ["ANALYSIS_PATH"] + f"/config/{self.year}_inclusive.yml"
        else:
            configYamlPath = os.environ["ANALYSIS_PATH"] + f"/config/{self.year}_{self.variable}.yml"
        
        #Load central config file
        with open(configYamlPath, 'r') as file:
            config = yaml.safe_load(file)
        
        if self.output_dir == '':
            output_dir = config['outputFolder']
        else:
            output_dir = self.output_dir
            
        tasks = [MakeDatacard(output_dir=output_dir, variable=self.variable, year=self.year)]
        
        return tasks
    
    
    def create_branch_map(self):
        # map branch indexes to ascii numbers from 97 to 122 ("a" to "z")        
        branch_list = [0]
        
        branch_map = {i: branch for i, branch in enumerate(branch_list)}
        return branch_map

    def output(self):
        
        if self.variable == '':
            configYamlPath = os.environ["ANALYSIS_PATH"] + f"/config/{self.year}_inclusive.yml"
        else:
            configYamlPath = os.environ["ANALYSIS_PATH"] + f"/config/{self.year}_{self.variable}.yml"
        
        #Load central config file
        with open(configYamlPath, 'r') as file:
            config = yaml.safe_load(file)
        
        if self.output_dir == '':
            output_dir = config['outputFolder']
        else:
            output_dir = self.output_dir
        
        signal_model_folder_name = config['datacard_yields']['sigModelWSDir'].split('/')[-2]
        background_model_folder_name = config['datacard_yields']['bkgModelWSDir'].split('/')[-2]
        
        output_data = []
        
        output_data.append(os.path.join(output_dir, 'Combine'))
        
        if signal_model_folder_name == background_model_folder_name:
            model_folder_name = signal_model_folder_name
            output_data.append(os.path.join(output_dir, 'Combine', model_folder_name))
            output_data.append(os.path.join(output_dir, 'Combine', model_folder_name, 'background'))
            output_data.append(os.path.join(output_dir, 'Combine', model_folder_name, 'signal'))
        else:
            output_data.append(os.path.join(output_dir, 'Combine', signal_model_folder_name))
            output_data.append(os.path.join(output_dir, 'Combine', signal_model_folder_name, 'signal'))
            
            output_data.append(os.path.join(output_dir, 'Combine', background_model_folder_name))
            output_data.append(os.path.join(output_dir, 'Combine', background_model_folder_name, 'background'))
            
        # Define the file paths
        if self.variable == '':
            output_data.append(os.path.join(output_dir, 'Combine', f'Datacard_{self.year}.txt'))
        else:
            output_data.append(os.path.join(output_dir, 'Combine', f'Datacard_{self.variable}_{self.year}.txt'))
            
        for i, output in enumerate(output_data):
            output_data[i] = law.LocalFileTarget(output)

        return output_data

    def run(self):
        
        if self.variable == '':
            configYamlPath = os.environ["ANALYSIS_PATH"] + f"/config/{self.year}_inclusive.yml"
        else:
            configYamlPath = os.environ["ANALYSIS_PATH"] + f"/config/{self.year}_{self.variable}.yml"
        
        #Load central config file
        with open(configYamlPath, 'r') as file:
            config = yaml.safe_load(file)
        
        if self.output_dir == '':
            output_dir = config['outputFolder']
        else:
            output_dir = self.output_dir
            
        # Creating the Combine directory alongside the Models dir
        safe_mkdir(os.path.join(output_dir, 'Combine'))
        
        signal_model_folder_name = config['datacard_yields']['sigModelWSDir'].split('/')[-2]
        background_model_folder_name = config['datacard_yields']['bkgModelWSDir'].split('/')[-2]
        
        if signal_model_folder_name == background_model_folder_name:
            model_folder_name = signal_model_folder_name
            Model_dst_path = os.path.join(output_dir, 'Combine', model_folder_name)
            background_dst_path = os.path.join(output_dir, 'Combine', model_folder_name, 'background')
            signal_dst_path = os.path.join(output_dir, 'Combine', model_folder_name, 'signal')
            safe_mkdir(Model_dst_path)
        else:
            signalModel_dst_path = os.path.join(output_dir, 'Combine', signal_model_folder_name)
            signal_dst_path = os.path.join(output_dir, 'Combine', signal_model_folder_name, 'signal')
            safe_mkdir(signalModel_dst_path)
            
            backgroundModel_dst_path = os.path.join(output_dir, 'Combine', background_model_folder_name)
            background_dst_path = os.path.join(output_dir, 'Combine', background_model_folder_name, 'background')
            safe_mkdir(backgroundModel_dst_path)
                
        safe_mkdir(signal_dst_path)
        safe_mkdir(background_dst_path)
            
        # Copying relevant files in Models directory
        background_src_path = os.path.join(output_dir, f"outdir_{config['backgroundScriptCfg']['ext']}/")
        signal_src_path = os.path.join(output_dir, f"outdir_packaged{config[f'packaged_{self.year}']['ext']}/")
                
        shutil.copytree(background_src_path, background_dst_path, dirs_exist_ok=True)
        shutil.copytree(signal_src_path, signal_dst_path, dirs_exist_ok=True)
        
        # IDK for what that is useful
        path_pattern = f"{signal_model_folder_name}/signal/*_{self.year}.root"

        # Use glob to find all matching files
        for file_path in glob.glob(path_pattern):
            if os.path.isfile(file_path):  # Check if it's a file
                # Remove "_{self.year}" from the filename
                new_name = file_path.replace(f"_{self.year}.root", ".root")
                
                # Rename the file
                os.rename(file_path, new_name)
                
                print(f"Renamed {file_path} to {new_name}")

        # Define the file paths
        if self.variable == '':
            datacard_file_cleaned = os.path.join(output_dir, 'Datacards', f'Datacard_{self.year}_cleaned.txt')
            datacard_file = os.path.join(output_dir, 'Datacards', f'Datacard_{self.year}.txt')
            destination_file = os.path.join(output_dir, 'Combine', f'Datacard_{self.year}.txt')
        else:
            datacard_file_cleaned = os.path.join(output_dir, 'Datacards', f'Datacard_{self.variable}_{self.year}_cleaned.txt')
            datacard_file = os.path.join(output_dir, 'Datacards', f'Datacard_{self.variable}_{self.year}.txt')
            destination_file = os.path.join(output_dir, 'Combine', f'Datacard_{self.variable}_{self.year}.txt')

        # Check if the cleaned file exists
        if os.path.exists(datacard_file_cleaned):
            # Copy the cleaned file if it exists
            shutil.copy2(datacard_file_cleaned, destination_file)
        else:
            # Otherwise, copy the uncleaned file
            shutil.copy2(datacard_file, destination_file)
            
        print("Combine directory sucessfully prepared.")
        
        
class RunText2Workspace(law.Task): #(law.Task): #(Task, HTCondorWorkflow, law.LocalWorkflow):
    output_dir = law.Parameter(default = '', description="Path to the output directory")
    variable = law.Parameter(default="", description="Variable to be used")
    year = law.Parameter(default='2022', description="Year")
    
    # htcondor_job_kwargs_submit = {"spool": True}
    
    def requires(self):
        
        if self.variable == '':
            configYamlPath = os.environ["ANALYSIS_PATH"] + f"/config/{self.year}_inclusive.yml"
        else:
            configYamlPath = os.environ["ANALYSIS_PATH"] + f"/config/{self.year}_{self.variable}.yml"
        
        #Load central config file
        with open(configYamlPath, 'r') as file:
            config = yaml.safe_load(file)
        
        if self.output_dir == '':
            output_dir = config['outputFolder']
        else:
            output_dir = self.output_dir
            
        tasks = [PrepareTheDirectory(output_dir=output_dir, variable=self.variable, year=self.year)]
        
        return tasks
    
    def create_branch_map(self):
        # map branch indexes to ascii numbers from 97 to 122 ("a" to "z")        
        branch_list = [0]
        
        branch_map = {i: branch for i, branch in enumerate(branch_list)}
        return branch_map

    def output(self):
        
        if self.variable == '':
            configYamlPath = os.environ["ANALYSIS_PATH"] + f"/config/{self.year}_inclusive.yml"
        else:
            configYamlPath = os.environ["ANALYSIS_PATH"] + f"/config/{self.year}_{self.variable}.yml"
        
        #Load central config file
        with open(configYamlPath, 'r') as file:
            config = yaml.safe_load(file)
        
        if self.output_dir == '':
            output_dir = config['outputFolder']
        else:
            output_dir = self.output_dir

        output = [os.path.join(output_dir, 'Combine', f'')]
        
        # Define the file paths
        if self.variable == '':
            output = [os.path.join(output_dir, 'Combine', f'Datacard_{self.year}.root')]
            output += [os.path.join(output_dir, 'Combine', f't2w_jobs', 't2w_mu_fiducial.sh')]
        else:
            output = [os.path.join(output_dir, 'Combine', f'Datacard_{self.variable}_{self.year}.root')]
            output += [os.path.join(output_dir, 'Combine', f't2w_jobs', f't2w_{self.variable}.sh')]
            
        output += [os.path.join(output_dir, 'Combine', f't2w_jobs')]
                
        outputFileTargets = []
                
        for _, current_output_path in enumerate(output):
            outputFileTargets.append(law.LocalFileTarget(current_output_path))
            
        print(outputFileTargets)

        return outputFileTargets

    def run(self):      
        
        if self.variable == '':
            configYamlPath = os.environ["ANALYSIS_PATH"] + f"/config/{self.year}_inclusive.yml"
            mode = "mu_fiducial"
            datacard_name = f"Datacard_{self.year}"
        else:
            configYamlPath = os.environ["ANALYSIS_PATH"] + f"/config/{self.year}_{self.variable}.yml"
            mode = self.variable
            datacard_name = f"Datacard_{self.variable}_{self.year}"
        
        #Load central config file
        with open(configYamlPath, 'r') as file:
            config = yaml.safe_load(file)
        
        if self.output_dir == '':
            output_dir = config['outputFolder']
        else:
            output_dir = self.output_dir  
            
        script_path = os.environ["ANALYSIS_PATH"] + "/Combine/RunText2Workspace.py"
        # script_path = "RunText2Workspace.py"
        arguments = [
            "python3",
            script_path,
            "--outputDir", output_dir,
            "--outputName", datacard_name,
            "--mode", mode,
            "--common_opts", "-m 125.38 higgsMassRange=122,128",
            "--batch", "local"
        ]
        if self.variable != '':
            arguments.append("--ext")
            arguments.append(f"{self.variable}")
        command = arguments
        # print(command)
        try:
            result = subprocess.run(command, check=True, text=True, capture_output=True)
            print("Script output:", result.stdout)
            print("Script executed successfully.")
        except subprocess.CalledProcessError as e:
            print("Error executing script:", e.stderr)