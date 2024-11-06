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
            fitFolderName = f'runFits_mu_fiducial'
        else:
            configYamlPath = os.environ["ANALYSIS_PATH"] + f"/config/{self.year}_{self.variable}.yml"
            fitFolderName = f'runFits_{self.variable}'
        
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
            
        output_data.append(os.path.join(output_dir, 'Combine', fitFolderName))
        
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
            fitFolderName = f'runFits_mu_fiducial'
        else:
            configYamlPath = os.environ["ANALYSIS_PATH"] + f"/config/{self.year}_{self.variable}.yml"
            fitFolderName = f'runFits_{self.variable}'
        
        #Load central config file
        with open(configYamlPath, 'r') as file:
            config = yaml.safe_load(file)
        
        if self.output_dir == '':
            output_dir = config['outputFolder']
        else:
            output_dir = self.output_dir
            
        # Creating the Combine directory alongside the Models dir
        safe_mkdir(os.path.join(output_dir, 'Combine'))
        safe_mkdir(os.path.join(output_dir, 'Combine', fitFolderName))
        
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

        # output = [os.path.join(output_dir, 'Combine', f'')]
        
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
            
        # print(outputFileTargets)

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
        
class AsimovFitCategoryFirstStep(Task, HTCondorWorkflow, law.LocalWorkflow): #(law.Task): #(Task, HTCondorWorkflow, law.LocalWorkflow):
    output_dir = law.Parameter(default = '', description="Path to the output directory")
    variable = law.Parameter(default="", description="Variable to be used")
    year = law.Parameter(default='2022', description="Year")
    cats = law.Parameter(description="Current category")
    
    htcondor_job_kwargs_submit = {"spool": True}
    
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
            
        tasks = [RunText2Workspace(output_dir=output_dir, variable=self.variable, year=self.year)]
        
        return tasks

    def create_branch_map(self):

        if self.variable == '':
            branch_map = {i: cat for i, cat in enumerate(["r"])}
        else:
            nCats = len(self.cats.split(","))
            
            cat_list = [
                self.cats.split(",")[categoryIndex]
                for categoryIndex in range(nCats)
            ]
            
            branch_map = {i: cat for i, cat in enumerate(cat_list)}
        return branch_map

    def output(self):
        current_branch = self.branch_data
        
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

        if self.variable == '':
            fitFolderName = f'runFits_mu_fiducial'
        else:
            fitFolderName = f'runFits_{self.variable}'
            
        # output = [os.path.join(output_dir, 'Combine', fitFolderName)]
        output = [os.path.join(output_dir, 'Combine', fitFolderName, 'asimov')]

        if self.variable != '':
            output += [os.path.join(output_dir, 'Combine', fitFolderName, 'asimov', f'higgsCombinefirstStep_{current_branch}.MultiDimFit.mH125.38.root')]
            output += [os.path.join(output_dir, 'Combine', fitFolderName, 'asimov', f'multidimfitfirstStep_{current_branch}.root')]
        
        outputFileTargets = []
                
        for _, current_output_path in enumerate(output):
            outputFileTargets.append(law.LocalFileTarget(current_output_path))
            
        # print(outputFileTargets)

        return outputFileTargets

    def run(self):
        current_branch = self.branch_data
        
        if self.variable == '':
            configYamlPath = os.environ["ANALYSIS_PATH"] + f"/config/{self.year}_inclusive.yml"
            fitFolderName = f'runFits_mu_fiducial'
            
        else:
            configYamlPath = os.environ["ANALYSIS_PATH"] + f"/config/{self.year}_{self.variable}.yml"
            fitFolderName = f'runFits_{self.variable}'
                  
        #Load central config file
        with open(configYamlPath, 'r') as file:
            config = yaml.safe_load(file)
        
        if self.output_dir == '':
            output_dir = config['outputFolder']
        else:
            output_dir = self.output_dir  
            
        if self.variable == '':
            datacard_path = os.path.join(output_dir, 'Combine', f'Datacard_{self.year}.root')
        else:
            datacard_path = os.path.join(output_dir, 'Combine', f'Datacard_{self.variable}_{self.year}.root')
            
        # safe_mkdir(os.path.join(output_dir, 'Combine', fitFolderName))
        safe_mkdir(os.path.join(output_dir, 'Combine', fitFolderName, 'asimov'))
        
        cwd = os.getcwd()
        os.chdir(os.path.join(output_dir, 'Combine', fitFolderName, 'asimov'))
                    
        if self.variable != '':
            arguments = [
                "combine",
                "-M", "MultiDimFit",
                datacard_path,
                "--freezeParameters", "MH",
                "-m", "125.38",
                "-n", f"firstStep_{current_branch}",
                "--cminDefaultMinimizerStrategy=0",
                "--expectSignal", "1",
                "--saveWorkspace",
                "--X-rtd", "MINIMIZER_freezeDisassociatedParams",
                "--X-rtd", "MINIMIZER_multiMin_hideConstants",
                "--X-rtd", "MINIMIZER_multiMin_maskConstraints",
                "--X-rtd", "MINIMIZER_multiMin_maskChannels=2",
                "-t", "-1",
                "-P", f"{current_branch}",
                "--saveFitResult",
                "--saveSpecifiedIndex", f"""{",".join(combineVariableDict[f'{self.variable}']['pdfIndeces'])}""",
                "--floatOtherPOIs", "1"
            ]
            arguments.append("--setParameters")
            arguments.append(f"""{",".join(combineVariableDict[f'{self.variable}']['paramStr'])}""")
            command = arguments
            # print(command)
            try:
                result = subprocess.run(command, check=True, text=True, capture_output=True)
                print("Script output:", result.stdout)
                print("Script executed successfully.")
            except subprocess.CalledProcessError as e:
                print("Error executing script:", e.stderr)
            
        os.chdir(cwd)
        
class CreateAsimovFitFirstStep(law.Task): #(law.Task): #(Task, HTCondorWorkflow, law.LocalWorkflow):
    output_dir = law.Parameter(default = '', description="Path to the output directory")
    variable = law.Parameter(default="", description="Variable to be used")
    year = law.Parameter(default='2022', description="Year")
        
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
            
        tasks = []
        if self.variable == '':
            cats = ["r"]
            version = "inclusive_v1"
        else:
            cats = ",".join(combineVariableDict[f'{self.variable}']['paramStrNoOne'])
            version = f"{self.variable}_v1"
        
        tasks += [AsimovFitCategoryFirstStep(output_dir=output_dir, variable=self.variable, year=self.year, cats=cats, version=version, workflow="local")]
        
        return tasks
    
    def create_branch_map(self):
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

        if self.variable == '':
            fitFolderName = f'runFits_mu_fiducial'
        else:
            fitFolderName = f'runFits_{self.variable}'
            
        output = []
            
        output += [os.path.join(output_dir, 'Combine', fitFolderName, 'asimov')]
                
        outputFileTargets = []
        
                        
        for _, current_output_path in enumerate(output):
            outputFileTargets.append(law.LocalFileTarget(current_output_path))
            
        # print(outputFileTargets)

        return outputFileTargets

    def run(self):
        
        return True

class AsimovFitCategorySyst(Task, HTCondorWorkflow, law.LocalWorkflow): #(law.Task): #(Task, HTCondorWorkflow, law.LocalWorkflow):
    output_dir = law.Parameter(default = '', description="Path to the output directory")
    variable = law.Parameter(default="", description="Variable to be used")
    year = law.Parameter(default='2022', description="Year")
    cat = law.Parameter(description="Current category")
    nPoints = law.Parameter(default=30, description="Number of points for the LL scan")
    
    htcondor_job_kwargs_submit = {"spool": True}
    
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
               
        tasks = [CreateAsimovFitFirstStep(output_dir=output_dir, variable=self.variable, year=self.year)]
        
        return tasks
    
    def create_branch_map(self):
        branch_map = {i: current_point for i, current_point in enumerate(range(int(self.nPoints)))}
        return branch_map

    def output(self):
        current_point = self.branch_data
        
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

        if self.variable == '':
            fitFolderName = f'runFits_mu_fiducial'
        else:
            fitFolderName = f'runFits_{self.variable}'
            
        # output = [os.path.join(output_dir, 'Combine', fitFolderName)]
        output = [os.path.join(output_dir, 'Combine', fitFolderName, 'asimov')]
        
        output += [os.path.join(output_dir, 'Combine', fitFolderName, 'asimov', f'higgsCombineAsimovPostFitScanFit_{self.cat}.POINTS.{current_point}.{current_point}.MultiDimFit.mH125.38.root')]
        
        outputFileTargets = []
                
        for _, current_output_path in enumerate(output):
            outputFileTargets.append(law.LocalFileTarget(current_output_path))
            
        # print("AsimovFitCategorySyst", outputFileTargets)

        return outputFileTargets

    def run(self):
        current_point = self.branch_data
        
        if self.variable == '':
            configYamlPath = os.environ["ANALYSIS_PATH"] + f"/config/{self.year}_inclusive.yml"
            fitFolderName = f'runFits_mu_fiducial'
            
        else:
            configYamlPath = os.environ["ANALYSIS_PATH"] + f"/config/{self.year}_{self.variable}.yml"
            fitFolderName = f'runFits_{self.variable}'
                    
        #Load central config file
        with open(configYamlPath, 'r') as file:
            config = yaml.safe_load(file)
        
        if self.output_dir == '':
            output_dir = config['outputFolder']
        else:
            output_dir = self.output_dir  
            
        if self.variable == '':
            datacard_path = os.path.join(output_dir, 'Combine', f'Datacard_{self.year}.root')
        else:
            datacard_path = os.path.join(output_dir, 'Combine', f'Datacard_{self.variable}_{self.year}.root')
            
        safe_mkdir(os.path.join(output_dir, 'Combine', fitFolderName))
        safe_mkdir(os.path.join(output_dir, 'Combine', fitFolderName, 'asimov'))
        
        cwd = os.getcwd()
        os.chdir(os.path.join(output_dir, 'Combine', fitFolderName, 'asimov'))

        def check_pdf_idx(param):
            # Run the ROOT command
            command = f'root -l -q \'{os.environ["ANALYSIS_PATH"]}/Combine/checkPdfIdx.C("higgsCombinefirstStep_{param}.MultiDimFit.mH125.38.root")\''
            
            # Execute the command and capture the output
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            
            # Get the output and check for errors
            pdfIdx = result.stdout.strip()
            
            if result.returncode != 0:
                print("Error executing the command:", result.stderr)
                return None
            
            if pdfIdx.startswith("Processing"):
                pdfIdx = pdfIdx.split('X', 1)[-1]  # Split on the first 'X'
            
            # Remove the last comma
            pdfIdx = pdfIdx.rstrip(',')

            # Print the final result
            print(pdfIdx)
            return pdfIdx

        if self.variable == '':
            arguments = [
                "combine",
                "-M", "MultiDimFit",
                "-d", datacard_path,
                "--freezeParameters", "MH",
                "-m", "125.38",
                "-n", f"AsimovPostFitScanFit_{self.cat}.POINTS.{current_point}.{current_point}",
                "--cminDefaultMinimizerStrategy=0",
                "--algo", "grid",
                "--points", f"{int(self.nPoints)}",
                "--expectSignal", "1",
                "--X-rtd", "MINIMIZER_freezeDisassociatedParams",
                "--X-rtd", "MINIMIZER_multiMin_hideConstants",
                "--X-rtd", "MINIMIZER_multiMin_maskConstraints",
                "--X-rtd", "MINIMIZER_multiMin_maskChannels=2",
                "-t", "-1",
                "-P", "r",
                "--firstPoint", f"{current_point}",
                "--lastPoint", f"{current_point}",
                "--floatOtherPOIs", "1",
                "--alignEdges", "1",
                "--setParameterRanges", f"{config['combine_fit']['setParameterRange']}",
                "--saveSpecifiedNuis", "all"
            ]
            command = arguments
            # print(command)
            try:
                result = subprocess.run(command, check=True, text=True, capture_output=True)
                print("Script output:", result.stdout)
                print("Script executed successfully.")
            except subprocess.CalledProcessError as e:
                print("Error executing script:", e.stderr)
            
        else:
            pdfIdx = check_pdf_idx(self.cat)        
            
            arguments = [
                "combineTool.py",
                "-M", "MultiDimFit",
                datacard_path,
                "--freezeParameters", "MH",
                "-m", "125.38",
                "-n", f"AsimovPostFitScanFit_{self.cat}.POINTS.{current_point}.{current_point}",
                "--cminDefaultMinimizerStrategy=0",
                "--algo", "grid",
                "--points", f"{int(self.nPoints)}",
                "--expectSignal", "1",
                "--X-rtd", "MINIMIZER_freezeDisassociatedParams",
                "--X-rtd", "MINIMIZER_multiMin_hideConstants",
                "--X-rtd", "MINIMIZER_multiMin_maskConstraints",
                "--X-rtd", "MINIMIZER_multiMin_maskChannels=2",
                "-t", "-1",
                "-P", f"{self.cat}",
                "--firstPoint", f"{current_point}",
                "--lastPoint", f"{current_point}",
                "--saveFitResult",
                "--floatOtherPOIs", "1",
                "--alignEdges", "1",
                "--saveSpecifiedIndex", f"""{",".join(combineVariableDict[f'{self.variable}']['pdfIndeces'])}""",
                "--setParameters", f"""{pdfIdx},{",".join(combineVariableDict[f'{self.variable}']['paramStr'])}"""
            ]
            command = arguments
            # print(command)
            try:
                result = subprocess.run(command, check=True, text=True, capture_output=True)
                print("Script output:", result.stdout)
                print("Script executed successfully.")
            except subprocess.CalledProcessError as e:
                print("Error executing script:", e.stderr)
            
        os.chdir(cwd)
        
class AsimovFitCategoryStat(Task, HTCondorWorkflow, law.LocalWorkflow): #(law.Task): #(Task, HTCondorWorkflow, law.LocalWorkflow):
    output_dir = law.Parameter(default = '', description="Path to the output directory")
    variable = law.Parameter(default="", description="Variable to be used")
    year = law.Parameter(default='2022', description="Year")
    cat = law.Parameter(description="Current category")
    nPoints = law.Parameter(default=30, description="Number of points for the LL scan")
    
    htcondor_job_kwargs_submit = {"spool": True}
    
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
                
        tasks = [CreateAsimovFitFirstStep(output_dir=output_dir, variable=self.variable, year=self.year)]
        
        return tasks
    
    def create_branch_map(self):
        branch_map = {i: current_point for i, current_point in enumerate(range(int(self.nPoints)))}
        return branch_map

    def output(self):
        current_point = self.branch_data
        
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

        if self.variable == '':
            fitFolderName = f'runFits_mu_fiducial'
        else:
            fitFolderName = f'runFits_{self.variable}'
            
        # output = [os.path.join(output_dir, 'Combine', fitFolderName)]
        output = [os.path.join(output_dir, 'Combine', fitFolderName, 'asimov')]
        
        output += [os.path.join(output_dir, 'Combine', fitFolderName, 'asimov', f'higgsCombineAsimovPostFitScanStat_{self.cat}.POINTS.{current_point}.{current_point}.MultiDimFit.mH125.38.root')]
        
        outputFileTargets = []
                
        for _, current_output_path in enumerate(output):
            outputFileTargets.append(law.LocalFileTarget(current_output_path))
            
        # print("AsimovFitCategoryStat", outputFileTargets)
        
        return outputFileTargets

    def run(self):
        current_point = self.branch_data
        
        if self.variable == '':
            configYamlPath = os.environ["ANALYSIS_PATH"] + f"/config/{self.year}_inclusive.yml"
            fitFolderName = f'runFits_mu_fiducial'
            
        else:
            configYamlPath = os.environ["ANALYSIS_PATH"] + f"/config/{self.year}_{self.variable}.yml"
            fitFolderName = f'runFits_{self.variable}'
                    
        #Load central config file
        with open(configYamlPath, 'r') as file:
            config = yaml.safe_load(file)
        
        if self.output_dir == '':
            output_dir = config['outputFolder']
        else:
            output_dir = self.output_dir  
            
        safe_mkdir(os.path.join(output_dir, 'Combine', fitFolderName))
        safe_mkdir(os.path.join(output_dir, 'Combine', fitFolderName, 'asimov'))
        
        cwd = os.getcwd()
        os.chdir(os.path.join(output_dir, 'Combine', fitFolderName, 'asimov'))

        def check_pdf_idx(param):
            # Run the ROOT command
            command = f'root -l -q \'{os.environ["ANALYSIS_PATH"]}/Combine/checkPdfIdx.C("higgsCombinefirstStep_{param}.MultiDimFit.mH125.38.root")\''
            
            # Execute the command and capture the output
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            
            # Get the output and check for errors
            pdfIdx = result.stdout.strip()
            
            if result.returncode != 0:
                print("Error executing the command:", result.stderr)
                return None
            
            if pdfIdx.startswith("Processing"):
                pdfIdx = pdfIdx.split('X', 1)[-1]  # Split on the first 'X'
            
            # Remove the last comma
            pdfIdx = pdfIdx.rstrip(',')

            # Print the final result
            print(pdfIdx)
            return pdfIdx
        
        pdfIdx = check_pdf_idx(self.cat)        
    
        firstStepPath = os.path.join(output_dir, 'Combine', fitFolderName, 'asimov', f"higgsCombinefirstStep_{self.cat}.MultiDimFit.mH125.38.root")
        
        if self.variable == '':
            datacard_path = os.path.join(output_dir, 'Combine', f'Datacard_{self.year}.root')
            arguments = [
                "combine",
                "-M", "MultiDimFit",
                "-d", datacard_path,
                "--freezeParameters", "allConstrainedNuisances,MH",
                "-m", "125.38",
                "-n", f"AsimovPostFitScanStat_{self.cat}.POINTS.{current_point}.{current_point}",
                "--cminDefaultMinimizerStrategy=0",
                "--algo", "grid",
                "--points", f"{int(self.nPoints)}",
                "--expectSignal", "1",
                "--X-rtd", "MINIMIZER_freezeDisassociatedParams",
                "--X-rtd", "MINIMIZER_multiMin_hideConstants",
                "--X-rtd", "MINIMIZER_multiMin_maskConstraints",
                "--X-rtd", "MINIMIZER_multiMin_maskChannels=2",
                "-t", "-1",
                "-P", "r",
                "--firstPoint", f"{current_point}",
                "--lastPoint", f"{current_point}",
                "--floatOtherPOIs", "1",
                "--alignEdges", "1",
                "--setParameterRanges", f"{config['combine_fit']['setParameterRange']}",
                "--saveSpecifiedNuis", "all"
            ]
            command = arguments
            # print(command)
            try:
                result = subprocess.run(command, check=True, text=True, capture_output=True)
                print("Script output:", result.stdout)
                print("Script executed successfully.")
            except subprocess.CalledProcessError as e:
                print("Error executing script:", e.stderr)
            
        else:
            arguments = [
                "combineTool.py",
                "-M", "MultiDimFit",
                firstStepPath,
                "--freezeParameters", "allConstrainedNuisances,MH",
                "-m", "125.38",
                "-n", f"AsimovPostFitScanStat_{self.cat}.POINTS.{current_point}.{current_point}",
                "--cminDefaultMinimizerStrategy=0",
                "--algo", "grid",
                "--points", f"{int(self.nPoints)}",
                "--expectSignal", "1",
                "--X-rtd", "MINIMIZER_freezeDisassociatedParams",
                "--X-rtd", "MINIMIZER_multiMin_hideConstants",
                "--X-rtd", "MINIMIZER_multiMin_maskConstraints",
                "--X-rtd", "MINIMIZER_multiMin_maskChannels=2",
                "-t", "-1",
                "-P", f"{self.cat}",
                "--firstPoint", f"{current_point}",
                "--lastPoint", f"{current_point}",
                "--saveFitResult",
                "--floatOtherPOIs", "1",
                "--alignEdges", "1",
                "--snapshotName", "MultiDimFit",
                "--saveSpecifiedIndex", f"""{",".join(combineVariableDict[f'{self.variable}']['pdfIndeces'])}""",
                "--setParameters", f"""{pdfIdx},{",".join(combineVariableDict[f'{self.variable}']['paramStr'])}"""
            ]
            command = arguments
            # print(command)
            try:
                result = subprocess.run(command, check=True, text=True, capture_output=True)
                print("Script output:", result.stdout)
                print("Script executed successfully.")
            except subprocess.CalledProcessError as e:
                print("Error executing script:", e.stderr)
                
        
        os.chdir(cwd)
        
class CreateAsimovFit(law.Task): #(law.Task): #(Task, HTCondorWorkflow, law.LocalWorkflow):
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
            
        tasks = []
        if self.variable == '':
            cat = "r"
            tasks += [AsimovFitCategorySyst(output_dir=output_dir, variable=self.variable, year=self.year, cat=cat, nPoints=config["combine_fit"]["asimov_numPoints"], version=f"inclusive_v1", workflow=config["combine_fit"]["execution"]), AsimovFitCategoryStat(output_dir=output_dir, variable=self.variable, year=self.year, cat=cat, nPoints=config["combine_fit"]["asimov_numPoints"], version=f"inclusive_v1", workflow=config["combine_fit"]["execution"])]
        else:
            version_index = 1
            for cat in combineVariableDict[f'{self.variable}']['paramStrNoOne']:
                tasks += [AsimovFitCategorySyst(output_dir=output_dir, variable=self.variable, year=self.year, cat=cat, nPoints=config["combine_fit"]["asimov_numPoints"], version=f"{self.variable}_v{version_index}", workflow=config["combine_fit"]["execution"]), AsimovFitCategoryStat(output_dir=output_dir, variable=self.variable, year=self.year, cat=cat, nPoints=config["combine_fit"]["asimov_numPoints"], version=f"{self.variable}_v{version_index}", workflow=config["combine_fit"]["execution"])]
                version_index += 1
        
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

        if self.variable == '':
            fitFolderName = f'runFits_mu_fiducial'
        else:
            fitFolderName = f'runFits_{self.variable}'
            
        output = []
            
        output += [os.path.join(output_dir, 'Combine', fitFolderName, 'asimov', 'scans')]
        
        if self.variable == '':
            cat = "r"
            output += [os.path.join(output_dir, 'Combine', fitFolderName, 'asimov', f'higgsCombineAsimovPostFitScanFit_{cat}.root')]
            output += [os.path.join(output_dir, 'Combine', fitFolderName, 'asimov', f'higgsCombineAsimovPostFitScanStat_{cat}.root')]
            output += [os.path.join(output_dir, 'Combine', fitFolderName, 'asimov', 'scans', f'scan_{cat}.root')]
            output += [os.path.join(output_dir, 'Combine', fitFolderName, 'asimov', 'scans', f'scan_{cat}.pdf')]
            output += [os.path.join(output_dir, 'Combine', fitFolderName, 'asimov', 'scans', f'scan_{cat}.png')]
        else:
            for cat in combineVariableDict[f'{self.variable}']['paramStrNoOne']:
                
                output += [os.path.join(output_dir, 'Combine', fitFolderName, 'asimov', f'higgsCombineAsimovPostFitScanFit_{cat}.root')]
                output += [os.path.join(output_dir, 'Combine', fitFolderName, 'asimov', f'higgsCombineAsimovPostFitScanStat_{cat}.root')]
                output += [os.path.join(output_dir, 'Combine', fitFolderName, 'asimov', 'scans', f'scan_{cat}.root')]
                output += [os.path.join(output_dir, 'Combine', fitFolderName, 'asimov', 'scans', f'scan_{cat}.pdf')]
                output += [os.path.join(output_dir, 'Combine', fitFolderName, 'asimov', 'scans', f'scan_{cat}.png')]

        outputFileTargets = []
                
        for _, current_output_path in enumerate(output):
            outputFileTargets.append(law.LocalFileTarget(current_output_path))
            
        # print(outputFileTargets)

        return outputFileTargets

    def run(self):
        
        if self.variable == '':
            configYamlPath = os.environ["ANALYSIS_PATH"] + f"/config/{self.year}_inclusive.yml"
            fitFolderName = f'runFits_mu_fiducial'
        else:
            configYamlPath = os.environ["ANALYSIS_PATH"] + f"/config/{self.year}_{self.variable}.yml"
            fitFolderName = f'runFits_{self.variable}'
            
                    
        #Load central config file
        with open(configYamlPath, 'r') as file:
            config = yaml.safe_load(file)
        
        if self.output_dir == '':
            output_dir = config['outputFolder']
        else:
            output_dir = self.output_dir  
            
        safe_mkdir(os.path.join(output_dir, 'Combine', fitFolderName, 'asimov', 'scans'))
            

        cwd = os.getcwd()
        os.chdir(os.path.join(output_dir, 'Combine', fitFolderName, 'asimov'))
        
        if self.variable == '':
            cats = ["r"]
        else:
            cats = combineVariableDict[f'{self.variable}']['paramStrNoOne']
        
        for cat in cats:
        
            arguments = [
                "hadd",
                f"{os.path.join(output_dir, 'Combine', fitFolderName, 'asimov', f'higgsCombineAsimovPostFitScanFit_{cat}.root')}"
            ]
            for i in range(config["combine_fit"]["asimov_numPoints"]):
                arguments.append(os.path.join(output_dir, 'Combine', fitFolderName, 'asimov', f'higgsCombineAsimovPostFitScanFit_{cat}.POINTS.{i}.{i}.MultiDimFit.mH125.38.root'))
            command = arguments
            # print(command)
            try:
                result = subprocess.run(command, check=True, text=True, capture_output=True)
                print("Script output:", result.stdout)
                print("Script executed successfully.")
            except subprocess.CalledProcessError as e:
                print("Error executing script:", e.stderr)
                
            
            arguments = [
                "hadd",
                f"{os.path.join(output_dir, 'Combine', fitFolderName, 'asimov', f'higgsCombineAsimovPostFitScanStat_{cat}.root')}"
            ]
            for i in range(config["combine_fit"]["asimov_numPoints"]):
                arguments.append(os.path.join(output_dir, 'Combine', fitFolderName, 'asimov', f'higgsCombineAsimovPostFitScanStat_{cat}.POINTS.{i}.{i}.MultiDimFit.mH125.38.root'))
            command = arguments
            # print(command)
            try:
                result = subprocess.run(command, check=True, text=True, capture_output=True)
                print("Script output:", result.stdout)
                print("Script executed successfully.")
            except subprocess.CalledProcessError as e:
                print("Error executing script:", e.stderr)

            arguments = [
                "plot1DScan.py",
                os.path.join(output_dir, 'Combine', fitFolderName, 'asimov', f'higgsCombineAsimovPostFitScanFit_{cat}.root'),
                "-o", f"scans/scan_{cat}",
                "--POI", f"{cat}",
                "--others", os.path.join(output_dir, 'Combine', fitFolderName, 'asimov', f'higgsCombineAsimovPostFitScanStat_{cat}.root')+":stat-only:2",
                "--main-label", "Expected",
                "--translate", os.path.join(os.environ["ANALYSIS_PATH"], 'Combine', 'pois.json')
            ]
            command = arguments
            # print(command)
            try:
                result = subprocess.run(command, check=True, text=True, capture_output=True)
                print("Script output:", result.stdout)
                print("Script executed successfully.")
            except subprocess.CalledProcessError as e:
                print("Error executing script:", e.stderr)
            
        os.chdir(cwd)
        
class AsimovImpactFirstStep(law.Task): #(law.Task): #(Task, HTCondorWorkflow, law.LocalWorkflow):
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
            
        tasks = [RunText2Workspace(output_dir=output_dir, variable=self.variable, year=self.year)]
        
        return tasks

    def create_branch_map(self):
        branch_map = {i: current_branch for i, current_branch in enumerate([0])}
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

        if self.variable == '':
            fitFolderName = f'runFits_mu_fiducial'
        else:
            fitFolderName = f'runFits_{self.variable}'
            
        # output = [os.path.join(output_dir, 'Combine', fitFolderName)]
        output = [os.path.join(output_dir, 'Combine', fitFolderName, 'impact')]

        output += [os.path.join(output_dir, 'Combine', fitFolderName, 'impact', f'higgsCombine_initialFit_Test.MultiDimFit.mH125.38.root')]
        
        outputFileTargets = []
                
        for _, current_output_path in enumerate(output):
            outputFileTargets.append(law.LocalFileTarget(current_output_path))
            
        # print(outputFileTargets)

        return outputFileTargets

    def run(self):
       
        if self.variable == '':
            configYamlPath = os.environ["ANALYSIS_PATH"] + f"/config/{self.year}_inclusive.yml"
            fitFolderName = f'runFits_mu_fiducial'
            
        else:
            configYamlPath = os.environ["ANALYSIS_PATH"] + f"/config/{self.year}_{self.variable}.yml"
            fitFolderName = f'runFits_{self.variable}'
                  
        #Load central config file
        with open(configYamlPath, 'r') as file:
            config = yaml.safe_load(file)
        
        if self.output_dir == '':
            output_dir = config['outputFolder']
        else:
            output_dir = self.output_dir  
            
        if self.variable == '':
            datacard_path = os.path.join(output_dir, 'Combine', f'Datacard_{self.year}.root')
        else:
            datacard_path = os.path.join(output_dir, 'Combine', f'Datacard_{self.variable}_{self.year}.root')
            
        safe_mkdir(os.path.join(output_dir, 'Combine', fitFolderName))
        safe_mkdir(os.path.join(output_dir, 'Combine', fitFolderName, 'impact'))
        
        cwd = os.getcwd()
        os.chdir(os.path.join(output_dir, 'Combine', fitFolderName, 'impact'))
                    
        if self.variable == '':
            arguments = [
                "combineTool.py",
                "-M", "Impacts",
                "-d", datacard_path,
                "--doInitialFit",
                "--robustFit", "1",
                "--freezeParameters", "MH",
                "-m", "125.38",
                "--cminDefaultMinimizerStrategy=0",
                "--X-rtd", "MINIMIZER_freezeDisassociatedParams",
                "--X-rtd", "MINIMIZER_multiMin_hideConstants",
                "--X-rtd", "MINIMIZER_multiMin_maskConstraints",
                "--X-rtd", "MINIMIZER_multiMin_maskChannels=2",
                "-t", "-1",
                "--setParameters", "r=1"
            ]
            command = arguments
            # print(command)
            try:
                result = subprocess.run(command, check=True, text=True, capture_output=True)
                print("Script output:", result.stdout)
                print("Script executed successfully.")
            except subprocess.CalledProcessError as e:
                print("Error executing script:", e.stderr)
        else:
            arguments = [
                "combine",
                "-M", "MultiDimFit",
                "-d", datacard_path,
                "--algo", "singles",
                "--redefineSignalPOIs", f"""{",".join(combineVariableDict[f'{self.variable}']['paramStrNoOne'])}""",
                "--freezeParameters", "MH",
                "-m", "125.38",
                "-n", "_initialFit_Test",
                "--cminDefaultMinimizerStrategy=0",
                "--X-rtd", "MINIMIZER_freezeDisassociatedParams",
                "--X-rtd", "MINIMIZER_multiMin_hideConstants",
                "--X-rtd", "MINIMIZER_multiMin_maskConstraints",
                "--X-rtd", "MINIMIZER_multiMin_maskChannels=2",
                "-t", "-1",
                "--setParameters", f"""{",".join(combineVariableDict[f'{self.variable}']['paramStr'])}"""
            ]
            command = arguments
            # print(command)
            try:
                result = subprocess.run(command, check=True, text=True, capture_output=True)
                print("Script output:", result.stdout)
                print("Script executed successfully.")
            except subprocess.CalledProcessError as e:
                print("Error executing script:", e.stderr)
            
        os.chdir(cwd)
        
class AsimovImpactSecondStep(Task, HTCondorWorkflow, law.LocalWorkflow): #(law.Task): #(Task, HTCondorWorkflow, law.LocalWorkflow):
    output_dir = law.Parameter(default = '', description="Path to the output directory")
    variable = law.Parameter(default="", description="Variable to be used")
    year = law.Parameter(default='2022', description="Year")
    
    htcondor_job_kwargs_submit = {"spool": True}
    
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
            
        tasks = [AsimovImpactFirstStep(output_dir=output_dir, variable=self.variable, year=self.year)]
        
        return tasks

    def create_branch_map(self):
        
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
            
        if self.variable == '':
            datacard_path = os.path.join(output_dir, 'Combine', f'Datacard_{self.year}.root')
        else:
            datacard_path = os.path.join(output_dir, 'Combine', f'Datacard_{self.variable}_{self.year}.root')
    
        # As seen in CMSSW_14_1_0_pre4/src/CombineHarvester/CombineTools/python/combine/Impacts.py
        def all_free_parameters(file, wsp, mc, pois):
            res = []
            wsFile = ROOT.TFile.Open(file)
            w = wsFile.Get(wsp)
            config = w.genobj(mc)
            pdfvars = config.GetPdf().getParameters(config.GetObservables())
            it = pdfvars.createIterator()
            var = it.Next()
            while var:
                if var.GetName() not in pois and (not var.isConstant()) and var.InheritsFrom("RooRealVar"):
                    res.append(var.GetName())
                var = it.Next()
            return res
        
        # def list_from_workspace(file, workspace, set):
        #     """Create a list of strings from a RooWorkspace set"""
        #     res = []
        #     wsFile = ROOT.TFile(file)
        #     ws = wsFile.Get(workspace)
        #     argSet = ws.set(set)
        #     it = argSet.createIterator()
        #     var = it.Next()
        #     while var:
        #         res.append(var.GetName())
        #         var = it.Next()
        #     return res

        if self.variable == '':
            poiList = ["r"]
        else:
            poiList = combineVariableDict[f'{self.variable}']['paramStrNoOne']
        
        paramList = all_free_parameters(datacard_path, 'w', 'ModelConfig', poiList)

        
        branch_map = {i: current_param for i, current_param in enumerate(paramList)}
        return branch_map

    def output(self):        
        current_param = self.branch_data
        
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

        if self.variable == '':
            fitFolderName = f'runFits_mu_fiducial'
        else:
            fitFolderName = f'runFits_{self.variable}'
            
        # output = [os.path.join(output_dir, 'Combine', fitFolderName)]
        output = [os.path.join(output_dir, 'Combine', fitFolderName, 'impact')]

        output += [os.path.join(output_dir, 'Combine', fitFolderName, 'impact', f'higgsCombine_paramFit_Test_{current_param}.MultiDimFit.mH125.38.root')]
        
        outputFileTargets = []
                
        for _, current_output_path in enumerate(output):
            outputFileTargets.append(law.LocalFileTarget(current_output_path))
            
        # print(outputFileTargets)

        return outputFileTargets

    def run(self):
        current_param = self.branch_data
       
        if self.variable == '':
            configYamlPath = os.environ["ANALYSIS_PATH"] + f"/config/{self.year}_inclusive.yml"
            fitFolderName = f'runFits_mu_fiducial'
            
        else:
            configYamlPath = os.environ["ANALYSIS_PATH"] + f"/config/{self.year}_{self.variable}.yml"
            fitFolderName = f'runFits_{self.variable}'
                  
        #Load central config file
        with open(configYamlPath, 'r') as file:
            config = yaml.safe_load(file)
        
        if self.output_dir == '':
            output_dir = config['outputFolder']
        else:
            output_dir = self.output_dir  
            
        if self.variable == '':
            datacard_path = os.path.join(output_dir, 'Combine', f'Datacard_{self.year}.root')
        else:
            datacard_path = os.path.join(output_dir, 'Combine', f'Datacard_{self.variable}_{self.year}.root')
            
        safe_mkdir(os.path.join(output_dir, 'Combine', fitFolderName))
        safe_mkdir(os.path.join(output_dir, 'Combine', fitFolderName, 'impact'))
        
        cwd = os.getcwd()
        os.chdir(os.path.join(output_dir, 'Combine', fitFolderName, 'impact'))

        if self.variable == '':
            arguments = [
                "combine",
                "-M", "MultiDimFit",
                "-d", datacard_path,
                "--algo", "impact",
                "--redefineSignalPOIs", "r",
                "--freezeParameters", "MH",
                "-m", "125.38",
                "-P", f"{current_param}",
                "--floatOtherPOIs", "1",
                "--saveInactivePOI", "1",
                "--robustFit", "1",
                "-n", f"_paramFit_Test_{current_param}",
                "--cminDefaultMinimizerStrategy=0",
                "--X-rtd", "MINIMIZER_freezeDisassociatedParams",
                "--X-rtd", "MINIMIZER_multiMin_hideConstants",
                "--X-rtd", "MINIMIZER_multiMin_maskConstraints",
                "--X-rtd", "MINIMIZER_multiMin_maskChannels=2",
                "-t", "-1",
                "--setParameters", "r=1"
            ]
            command = arguments
            # print(command)
            try:
                result = subprocess.run(command, check=True, text=True, capture_output=True)
                print("Script output:", result.stdout)
                print("Script executed successfully.")
            except subprocess.CalledProcessError as e:
                print("Error executing script:", e.stderr)
        else:
            arguments = [
                "combine",
                "-M", "MultiDimFit",
                "-d", datacard_path,
                "--algo", "impact",
                "--redefineSignalPOIs", f"""{",".join(combineVariableDict[f'{self.variable}']['paramStrNoOne'])}""",
                "--freezeParameters", "MH",
                "-m", "125.38",
                "-P", f"{current_param}",
                "--floatOtherPOIs", "1",
                "--saveInactivePOI", "1",
                "--robustFit", "1",
                "-n", f"_paramFit_Test_{current_param}",
                "--cminDefaultMinimizerStrategy=0",
                "--X-rtd", "MINIMIZER_freezeDisassociatedParams",
                "--X-rtd", "MINIMIZER_multiMin_hideConstants",
                "--X-rtd", "MINIMIZER_multiMin_maskConstraints",
                "--X-rtd", "MINIMIZER_multiMin_maskChannels=2",
                "-t", "-1",
                "--setParameters", f"""{",".join(combineVariableDict[f'{self.variable}']['paramStr'])}"""
            ]
            command = arguments
            # print(command)
            try:
                result = subprocess.run(command, check=True, text=True, capture_output=True)
                print("Script output:", result.stdout)
                print("Script executed successfully.")
            except subprocess.CalledProcessError as e:
                print("Error executing script:", e.stderr)
            
        os.chdir(cwd)
        
class AsimovImpactThirdStep(law.Task): #(law.Task): #(Task, HTCondorWorkflow, law.LocalWorkflow):
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
            
        tasks = [AsimovImpactSecondStep(output_dir=output_dir, variable=self.variable, year=self.year, version="v1", workflow="htcondor")]
        
        return tasks

    def create_branch_map(self):

        branch_map = {i: current_branch for i, current_branch in enumerate([0])}
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

        if self.variable == '':
            fitFolderName = f'runFits_mu_fiducial'
        else:
            fitFolderName = f'runFits_{self.variable}'

        output = []
        if self.variable == '':
            cat = "r"
            output += [os.path.join(output_dir, 'Combine', fitFolderName, 'impact', f'impacts_{cat}.pdf')]
            output += [os.path.join(output_dir, 'Combine', fitFolderName, 'impact', 'impacts_corrected_dropBkgModelParams.json')]
            
        else:
            for cat in combineVariableDict[f'{self.variable}']['paramStrNoOne']:
                output += [os.path.join(output_dir, 'Combine', fitFolderName, 'impact', f'impacts_{cat}.pdf')]
                
        output += [os.path.join(output_dir, 'Combine', fitFolderName, 'impact', f'impacts.json')]
        
        outputFileTargets = []
                
        for _, current_output_path in enumerate(output):
            outputFileTargets.append(law.LocalFileTarget(current_output_path))
            
        # print(outputFileTargets)

        return outputFileTargets

    def run(self):
       
        if self.variable == '':
            configYamlPath = os.environ["ANALYSIS_PATH"] + f"/config/{self.year}_inclusive.yml"
            fitFolderName = f'runFits_mu_fiducial'
            
        else:
            configYamlPath = os.environ["ANALYSIS_PATH"] + f"/config/{self.year}_{self.variable}.yml"
            fitFolderName = f'runFits_{self.variable}'
                  
        #Load central config file
        with open(configYamlPath, 'r') as file:
            config = yaml.safe_load(file)
        
        if self.output_dir == '':
            output_dir = config['outputFolder']
        else:
            output_dir = self.output_dir  
            
        if self.variable == '':
            datacard_path = os.path.join(output_dir, 'Combine', f'Datacard_{self.year}.root')
        else:
            datacard_path = os.path.join(output_dir, 'Combine', f'Datacard_{self.variable}_{self.year}.root')
            
        safe_mkdir(os.path.join(output_dir, 'Combine', fitFolderName))
        safe_mkdir(os.path.join(output_dir, 'Combine', fitFolderName, 'impact'))
        
        cwd = os.getcwd()
        os.chdir(os.path.join(output_dir, 'Combine', fitFolderName, 'impact'))

        if self.variable == '':
            arguments = [
                "combineTool.py",
                "-M", "Impacts",
                "-d", datacard_path,
                "-m", "125.38",
                "-o", f"{os.path.join(output_dir, 'Combine', fitFolderName, 'impact', 'impacts.json')}"
            ]
            command = arguments
            # print(command)
            try:
                result = subprocess.run(command, check=True, text=True, capture_output=True)
                print("Script output:", result.stdout)
                print("Script executed successfully.")
            except subprocess.CalledProcessError as e:
                print("Error executing script:", e.stderr)

            arguments = [
                "python3",
                f"{os.path.join(os.environ['ANALYSIS_PATH'], 'Combine', 'correctImpacts.py')}",
                "--impactsJson", f"{os.path.join(output_dir, 'Combine', fitFolderName, 'impact', 'impacts.json')}",
                "--frozenParam", "MH",
                "dropBkgModelParams"
            ]
            command = arguments
            # print(command)
            try:
                result = subprocess.run(command, check=True, text=True, capture_output=True)
                print("Script output:", result.stdout)
                print("Script executed successfully.")
            except subprocess.CalledProcessError as e:
                print("Error executing script:", e.stderr)
                
            arguments = [
                "plotImpacts.py",
                "-i", f"{os.path.join(output_dir, 'Combine', fitFolderName, 'impact', 'impacts_corrected_dropBkgModelParams.json')}",
                "-o", "impacts"
            ]
            command = arguments
            # print(command)
            try:
                result = subprocess.run(command, check=True, text=True, capture_output=True)
                print("Script output:", result.stdout)
                print("Script executed successfully.")
            except subprocess.CalledProcessError as e:
                print("Error executing script:", e.stderr)
        else:
            arguments = [
                "combineTool.py",
                "-M", "Impacts",
                "-d", datacard_path,
                "--freezeParameters", "MH",
                "-m", "125.38",
                "-o", f"{os.path.join(output_dir, 'Combine', fitFolderName, 'impact', 'impacts.json')}",
            ]
            if (config["combine_impacts"]["exclude"] != ""):
                arguments.append("--exclude")
                arguments.append(config["combine_impacts"]["exclude"])
            command = arguments
            # print(command)
            try:
                result = subprocess.run(command, check=True, text=True, capture_output=True)
                print("Script output:", result.stdout)
                print("Script executed successfully.")
            except subprocess.CalledProcessError as e:
                print("Error executing script:", e.stderr)
                
            for cat in combineVariableDict[f'{self.variable}']['paramStrNoOne']:
                arguments = [
                    "plotImpacts.py",
                    "-i", f"{os.path.join(output_dir, 'Combine', fitFolderName, 'impact', 'impacts.json')}",
                    "-o", f"impacts_{cat}",
                    "--POI", f"{cat}"
                ]
                command = arguments
                # print(command)
                try:
                    result = subprocess.run(command, check=True, text=True, capture_output=True)
                    print("Script output:", result.stdout)
                    print("Script executed successfully.")
                except subprocess.CalledProcessError as e:
                    print("Error executing script:", e.stderr)
            
        os.chdir(cwd)


class AsimovCovCorrHesse(Task, HTCondorWorkflow, law.LocalWorkflow): #(law.Task): #(Task, HTCondorWorkflow, law.LocalWorkflow):
    output_dir = law.Parameter(default = '', description="Path to the output directory")
    variable = law.Parameter(default="", description="Variable to be used")
    year = law.Parameter(default='2022', description="Year")
    
    htcondor_job_kwargs_submit = {"spool": True}
    
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
            
        tasks = [RunText2Workspace(output_dir=output_dir, variable=self.variable, year=self.year)]
        
        return tasks

    def create_branch_map(self):
        branch_map = {i: current_branch for i, current_branch in enumerate([0])}
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

        if self.variable == '':
            fitFolderName = f'runFits_mu_fiducial'
        else:
            fitFolderName = f'runFits_{self.variable}'
            
        # output = [os.path.join(output_dir, 'Combine', fitFolderName)]
        output = [os.path.join(output_dir, 'Combine', fitFolderName, 'hesse')]
        
        
        output += [os.path.join(output_dir, 'Combine', fitFolderName, 'hesse', f'robustHessefirstStep.root')]
        output += [os.path.join(output_dir, 'Combine', fitFolderName, 'hesse', f'multidimfitfirstStep.root')]
        output += [os.path.join(output_dir, 'Combine', fitFolderName, 'hesse', f'higgsCombinefirstStep.MultiDimFit.mH125.38.root')]
        
        outputFileTargets = []
                
        for _, current_output_path in enumerate(output):
            outputFileTargets.append(law.LocalFileTarget(current_output_path))
            
        # print(outputFileTargets)

        return outputFileTargets

    def run(self):
       
        if self.variable == '':
            # Does not make sense inclusively
            return True
            
        else:
            configYamlPath = os.environ["ANALYSIS_PATH"] + f"/config/{self.year}_{self.variable}.yml"
            fitFolderName = f'runFits_{self.variable}'
                  
        #Load central config file
        with open(configYamlPath, 'r') as file:
            config = yaml.safe_load(file)
        
        if self.output_dir == '':
            output_dir = config['outputFolder']
        else:
            output_dir = self.output_dir  
            
        if self.variable == '':
            datacard_path = os.path.join(output_dir, 'Combine', f'Datacard_{self.year}.root')
        else:
            datacard_path = os.path.join(output_dir, 'Combine', f'Datacard_{self.variable}_{self.year}.root')
            
        safe_mkdir(os.path.join(output_dir, 'Combine', fitFolderName))
        safe_mkdir(os.path.join(output_dir, 'Combine', fitFolderName, 'hesse'))
        
        cwd = os.getcwd()
        os.chdir(os.path.join(output_dir, 'Combine', fitFolderName, 'hesse'))
                    
        arguments = [
            "combine",
            "-M", "MultiDimFit",
            datacard_path,
            "--freezeParameters", "MH",
            "-m", "125.38",
            "-n", "firstStep",
            "--saveWorkspace",
            "--saveFitResult",
            "--saveSpecifiedIndex", f"""{",".join(combineVariableDict[f'{self.variable}']['pdfIndeces'])}""",
            "--floatOtherPOIs", "1",
            "--robustHesse", "1",
            "--robustHesseSave", "1",
            "--cminDefaultMinimizerStrategy=0",
            "--X-rtd", "MINIMIZER_freezeDisassociatedParams",
            "--X-rtd", "MINIMIZER_multiMin_hideConstants",
            "--X-rtd", "MINIMIZER_multiMin_maskConstraints",
            "--X-rtd", "MINIMIZER_multiMin_maskChannels=2",
            "-t", "-1",
            "--setParameters", f"""{",".join(combineVariableDict[f'{self.variable}']['paramStr'])}"""
        ]
        command = arguments
        # print(command)
        try:
            result = subprocess.run(command, check=True, text=True, capture_output=True)
            print("Script output:", result.stdout)
            print("Script executed successfully.")
        except subprocess.CalledProcessError as e:
            print("Error executing script:", e.stderr)
            
        os.chdir(cwd)
        
class AsimovCovCorr(law.Task): #(law.Task): #(Task, HTCondorWorkflow, law.LocalWorkflow):
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
            
        tasks = [AsimovCovCorrHesse(output_dir=output_dir, variable=self.variable, year=self.year, version="v1", workflow=config["combine_hesse"]["execution"])]
        
        return tasks

    def create_branch_map(self):
        branch_map = {i: current_branch for i, current_branch in enumerate([0])}
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

        if self.variable == '':
            fitFolderName = f'runFits_mu_fiducial'
        else:
            fitFolderName = f'runFits_{self.variable}'
            
        # output = [os.path.join(output_dir, 'Combine', fitFolderName)]
        output = [os.path.join(output_dir, 'Combine', fitFolderName, 'hesse', 'Plots')]

        output += [os.path.join(output_dir, 'Combine', fitFolderName, 'hesse', 'Plots', f'corrMatrix_{self.variable}_syst.pdf')]
        output += [os.path.join(output_dir, 'Combine', fitFolderName, 'hesse', 'Plots', f'corrMatrix_{self.variable}_syst.png')]
        output += [os.path.join(output_dir, 'Combine', fitFolderName, 'hesse', 'Plots', f'covMatrix_{self.variable}_syst.pdf')]
        output += [os.path.join(output_dir, 'Combine', fitFolderName, 'hesse', 'Plots', f'covMatrix_{self.variable}_syst.png')]
        
        outputFileTargets = []
                
        for _, current_output_path in enumerate(output):
            outputFileTargets.append(law.LocalFileTarget(current_output_path))
            
        # print(outputFileTargets)

        return outputFileTargets

    def run(self):
       
        if self.variable == '':
            # Does not make sense inclusively
            return True
            
        else:
            configYamlPath = os.environ["ANALYSIS_PATH"] + f"/config/{self.year}_{self.variable}.yml"
            fitFolderName = f'runFits_{self.variable}'
                  
        #Load central config file
        with open(configYamlPath, 'r') as file:
            config = yaml.safe_load(file)
        
        if self.output_dir == '':
            output_dir = config['outputFolder']
        else:
            output_dir = self.output_dir  
            
        if self.variable == '':
            datacard_path = os.path.join(output_dir, 'Combine', f'Datacard_{self.year}.root')
        else:
            datacard_path = os.path.join(output_dir, 'Combine', f'Datacard_{self.variable}_{self.year}.root')
            
        safe_mkdir(os.path.join(output_dir, 'Combine', fitFolderName))
        safe_mkdir(os.path.join(output_dir, 'Combine', fitFolderName, 'hesse'))
        safe_mkdir(os.path.join(output_dir, 'Combine', fitFolderName, 'hesse', 'Plots'))
        
        cwd = os.getcwd()
        os.chdir(os.path.join(os.environ["ANALYSIS_PATH"], 'Plots'))

        arguments = [
            "python3"
            f"{os.path.join(os.environ['ANALYSIS_PATH'], 'Plots', 'makeCorrMatrix.py')}",
            "--inputJson", f"{os.path.join(os.environ['ANALYSIS_PATH'], 'Plots', 'inputs_robustHesse.json')}",
            "--mode", f"{self.variable}",
            "--input", f"{os.path.join(output_dir, 'Combine', fitFolderName, 'hesse', f'robustHessefirstStep.root')}",
            "--output", f"{os.path.join(output_dir, 'Combine', fitFolderName, 'hesse', 'Plots')}",
            "--translate", f"{os.path.join(os.environ['ANALYSIS_PATH'], 'Combine', 'poi_differential_hesse.json')}"
        ]
        command = arguments
        # print(command)
        try:
            result = subprocess.run(command, check=True, text=True, capture_output=True)
            print("Script output:", result.stdout)
            print("Script executed successfully.")
        except subprocess.CalledProcessError as e:
            print("Error executing script:", e.stderr)
            
        arguments = [
            "python3"
            f"{os.path.join(os.environ['ANALYSIS_PATH'], 'Plots', 'makeCorrMatrix.py')}",
            "--inputJson", f"{os.path.join(os.environ['ANALYSIS_PATH'], 'Plots', 'inputs_robustHesse.json')}",
            "--mode", f"{self.variable}",
            "--input", f"{os.path.join(output_dir, 'Combine', fitFolderName, 'hesse', f'robustHessefirstStep.root')}",
            "--output", f"{os.path.join(output_dir, 'Combine', fitFolderName, 'hesse', 'Plots')}",
            "--translate", f"{os.path.join(os.environ['ANALYSIS_PATH'], 'Combine', 'poi_differential_hesse.json')}",
            "--doCov"
        ]
        command = arguments
        # print(command)
        try:
            result = subprocess.run(command, check=True, text=True, capture_output=True)
            print("Script output:", result.stdout)
            print("Script executed successfully.")
        except subprocess.CalledProcessError as e:
            print("Error executing script:", e.stderr)
            
        os.chdir(cwd)