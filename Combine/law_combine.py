import law
import os
import subprocess
import ROOT
import uproot
import glob
import yaml
import errno
import shutil
import warnings
# Suppress // UserWarning: The value of the smallest subnormal for <class 'numpy.float64'> type is zero // warning.
warnings.filterwarnings("ignore", category=UserWarning, module="numpy.core.getlimits")
from scipy.stats import chi2

from commonTools import *
from commonObjects import *

from Datacard.law_datacard import *

from framework import Task
from framework import HTCondorWorkflow, SlurmWorkflow

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

def execute_command(command, return_output=False, shell=False):
    try:
        result = subprocess.run(command, check=True, text=True, capture_output=True, shell=shell, env=os.environ)
        print("Script output:", result.stdout)
        print("Script executed successfully.")
        if return_output:
            return (result.stdout).split("\n")[0]
    except subprocess.CalledProcessError as e:
        print("Error executing script:", e.stderr)
        
def manually_copy_t3(src, dst):
    # List files in the directory
    list_command = ["xrdfs", "root://t3dcachedb.psi.ch", "ls", src]
    file_list = subprocess.check_output(list_command).decode().splitlines()
    
    print(file_list)

    # Copy each file
    for file_path in file_list:
        filename = file_path.split("/")[-1]
        if "bkgfTest-Data" in filename: continue
        if "/pnfs" in file_path: 
            src_file = f"root://t3dcachedb.psi.ch:1094/{file_path}"
            dest_file = f"root://t3dcachedb.psi.ch:1094/{dst}/{filename}"
            
            print(f"Copying {filename}...")
            print(f"xrdcp -rf {src_file} {dest_file}")
            execute_command([f"xrdcp -rf {src_file} {dest_file}"], shell=True)
        else:
            print(f"Copying {filename}...")
            print(f"cp -rf {file_path} {dst}/{filename}")
            execute_command([f"cp -rf {file_path} {dst}/{filename}"], shell=True)

def manually_move_t3(src, dst):
    # List files in the directory
    list_command = ["xrdfs", "root://t3dcachedb.psi.ch", "ls", src]
    file_list = subprocess.check_output(list_command).decode().splitlines()
    
    print(file_list)

    # Copy each file
    for file_path in file_list:
        filename = file_path.split("/")[-1]
        if "bkgfTest-Data" in filename: continue
        if "/pnfs" in file_path: 
            src_file = f"root://t3dcachedb.psi.ch:1094/{file_path}"
            dest_file = f"root://t3dcachedb.psi.ch:1094/{dst}/{filename}"
            
            print(f"Moving {filename} on or off the PSI SE...")
            
            print(f"xrdfs root://t3dcachedb.psi.ch:1094/ mv -f {src_file} {dest_file}")
            execute_command([f"xrdfs root://t3dcachedb.psi.ch:1094/ mv -f {src_file} {dest_file}"], shell=True)
        else:
            print(f"Moving {filename}...")
            print(f"mv -f {file_path} {dst}/{filename}")
            execute_command([f"mv -f {file_path} {dst}/{filename}"], shell=True)
    
class PrepareTheDirectory(Task, HTCondorWorkflow, SlurmWorkflow, law.LocalWorkflow):#(law.Task): #(Task, HTCondorWorkflow, law.LocalWorkflow):
    output_dir = law.Parameter(default = '', description="Path to the output directory")
    variable = law.Parameter(default="", description="Variable to be used")
    year = law.Parameter(default='2022', description="Year")

    batch_flavor = law.Parameter(default="htcondor", description="Batch system to use")

    # def requires(self):
    def workflow_requires(self):
        workflow_reqs = super().workflow_requires()

        tasks = {}

        if workflow_reqs:
            tasks.update(workflow_reqs)
        
        if self.variable == '':
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_inclusive.yml")
        else:
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_{self.variable}.yml")
        
        #Load central config file
        with open(configYamlPath, 'r') as file:
            config = yaml.safe_load(file)
        
        if self.output_dir == '':
            output_dir = config['outputFolder']
        else:
            output_dir = self.output_dir
        
        yieldsConfig = config['datacard_yields']
            
        tasks["MakeDatacard"] = MakeDatacard(output_dir=output_dir, variable=self.variable, year=self.year, version=self.variable if self.variable != "" else "inclusive", workflow=yieldsConfig["execution"], batch_flavor=self.batch_flavor, slurm_partition=yieldsConfig['batchPartition'], slurm_memory=yieldsConfig['batchMemory'], slurm_max_runtime=yieldsConfig['batchMaxRuntime'], htcondor_partition=yieldsConfig['batchPartition'], htcondor_memory=yieldsConfig['batchMemory'], htcondor_max_runtime=yieldsConfig['batchMaxRuntime'])
        
        return tasks
    
    def create_branch_map(self):
        # map branch indexes to ascii numbers from 97 to 122 ("a" to "z")    
        branch_map = {i: i for i in range(1)}
        return branch_map

    def output(self):
        
        background_suffix = ""
        
        if self.variable == '':
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_inclusive.yml")
            fitFolderName = f'runFits_mu_fiducial'
        else:
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_{self.variable}.yml")
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
            output_data.append(os.path.join(output_dir, 'Combine', model_folder_name, 'background'+background_suffix))
            output_data.append(os.path.join(output_dir, 'Combine', model_folder_name, 'signal'))
        else:
            output_data.append(os.path.join(output_dir, 'Combine', signal_model_folder_name))
            output_data.append(os.path.join(output_dir, 'Combine', signal_model_folder_name, 'signal'))
            
            output_data.append(os.path.join(output_dir, 'Combine', background_model_folder_name))
            output_data.append(os.path.join(output_dir, 'Combine', background_model_folder_name, 'background'+background_suffix))
        
        # Define the file paths
        if self.variable == '':
            output_data.append(os.path.join(output_dir, 'Combine', f'Datacard_{self.year}.txt'))
        else:
            output_data.append(os.path.join(output_dir, 'Combine', f'Datacard_{self.variable}_{self.year}.txt'))
        
        for i, output in enumerate(output_data):
            output_data[i] = law.LocalFileTarget(output)

        return output_data

    def run(self):
        background_suffix = f""
        
        if self.variable == '':
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_inclusive.yml")
            fitFolderName = f'runFits_mu_fiducial'
        else:
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_{self.variable}.yml")
            fitFolderName = f'runFits_{self.variable}'

        #Load central config file
        with open(configYamlPath, 'r') as file:
            config = yaml.safe_load(file)

        if self.output_dir == '':
            output_dir = config['outputFolder']
        else:
            output_dir = self.output_dir

        # Creating the Combine directory alongside the Models dir
        if self.batch_flavor == "slurm/psi":
            execute_command([f"xrdfs root://t3dcachedb.psi.ch:1094/ mkdir -p {os.path.join(output_dir, 'Combine', fitFolderName)}"], shell=True)
        else:
            safe_mkdir(os.path.join(output_dir, 'Combine'))
            safe_mkdir(os.path.join(output_dir, 'Combine', fitFolderName))

        signal_model_folder_name = config['datacard_yields']['sigModelWSDir'].split('/')[-2]
        background_model_folder_name = config['datacard_yields']['bkgModelWSDir'].split('/')[-2]

        if signal_model_folder_name == background_model_folder_name:
            model_folder_name = signal_model_folder_name
            Model_dst_path = os.path.join(output_dir, 'Combine', model_folder_name)
            background_dst_path = os.path.join(output_dir, 'Combine', model_folder_name, 'background'+background_suffix)
            signal_dst_path = os.path.join(output_dir, 'Combine', model_folder_name, 'signal')
            if self.batch_flavor == "slurm/psi":
                execute_command([f'xrdfs root://t3dcachedb.psi.ch:1094/ mkdir -p {Model_dst_path}'], shell=True)
            else:
                safe_mkdir(Model_dst_path)
        else:
            signalModel_dst_path = os.path.join(output_dir, 'Combine', signal_model_folder_name)
            signal_dst_path = os.path.join(output_dir, 'Combine', signal_model_folder_name, 'signal')
            if self.batch_flavor == "slurm/psi":
                execute_command([f'xrdfs root://t3dcachedb.psi.ch:1094/ mkdir -p {signalModel_dst_path}'], shell=True)
            else:
                safe_mkdir(signalModel_dst_path)
            
            backgroundModel_dst_path = os.path.join(output_dir, 'Combine', background_model_folder_name)
            background_dst_path = os.path.join(output_dir, 'Combine', background_model_folder_name, 'background'+background_suffix)
            if self.batch_flavor == "slurm/psi":
                execute_command([f'xrdfs root://t3dcachedb.psi.ch:1094/ mkdir -p {backgroundModel_dst_path}'], shell=True)
            else:
                safe_mkdir(backgroundModel_dst_path)

        if self.batch_flavor == "slurm/psi":
            execute_command([f'xrdfs root://t3dcachedb.psi.ch:1094/ mkdir -p {signal_dst_path}'], shell=True)
            execute_command([f'xrdfs root://t3dcachedb.psi.ch:1094/ mkdir -p {background_dst_path}'], shell=True)
        else:
            safe_mkdir(signal_dst_path)
            safe_mkdir(background_dst_path)

        # Copying relevant files in Models directory
        background_src_path = os.path.join(output_dir, "Background", f"outdir_{config['backgroundScriptCfg']['ext']}"+background_suffix)
        signal_src_path = os.path.join(output_dir, f"outdir_packaged{config[f'packaged_{self.year}']['ext']}/")

        if self.batch_flavor == "slurm/psi":
            manually_copy_t3(background_src_path, background_dst_path)
            manually_copy_t3(signal_src_path, signal_dst_path)
        else:
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
            if self.batch_flavor == "slurm/psi":
                execute_command([f'xrdcp -rf root://t3dcachedb.psi.ch:1094/{datacard_file_cleaned} root://t3dcachedb.psi.ch:1094/{destination_file}'], shell=True)
            else:
                shutil.copy2(datacard_file_cleaned, destination_file)
        else:
            # Otherwise, copy the uncleaned file
            if self.batch_flavor == "slurm/psi":
                execute_command([f'xrdcp -rf root://t3dcachedb.psi.ch:1094/{datacard_file} root://t3dcachedb.psi.ch:1094/{destination_file}'], shell=True)
            else:
                shutil.copy2(datacard_file, destination_file)
            
        print("Combine directory sucessfully prepared.")


class RunText2Workspace(Task, HTCondorWorkflow, SlurmWorkflow, law.LocalWorkflow): #(law.Task): #(Task, HTCondorWorkflow, law.LocalWorkflow):
    output_dir = law.Parameter(default = '', description="Path to the output directory")
    variable = law.Parameter(default="", description="Variable to be used")
    year = law.Parameter(default='2022', description="Year")

    batch_flavor = law.Parameter(default="htcondor", description="Batch system to use")

    # def requires(self):
    def workflow_requires(self):
        workflow_reqs = super().workflow_requires()

        tasks = {}

        if workflow_reqs:
            tasks.update(workflow_reqs)
        
        if self.variable == '':
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_inclusive.yml")
        else:
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_{self.variable}.yml")
        
        #Load central config file
        with open(configYamlPath, 'r') as file:
            config = yaml.safe_load(file)
        
        if self.output_dir == '':
            output_dir = config['outputFolder']
        else:
            output_dir = self.output_dir
            
        fitConfig = config['combine_fit']

        tasks["PrepareTheDirectory"] = PrepareTheDirectory(output_dir=output_dir, variable=self.variable, year=self.year, version=self.variable if self.variable != "" else "inclusive", workflow=fitConfig["execution"], batch_flavor=self.batch_flavor, slurm_partition=fitConfig['batchPartition'], slurm_memory=fitConfig['batchMemory'], slurm_max_runtime=fitConfig['batchMaxRuntime'], htcondor_partition=fitConfig['batchPartition'], htcondor_memory=fitConfig['batchMemory'], htcondor_max_runtime=fitConfig['batchMaxRuntime'])
        
        return tasks
    
    def create_branch_map(self):
        # map branch indexes to ascii numbers from 97 to 122 ("a" to "z")        
        branch_map = {i: i for i in range(1)}
        return branch_map

    def output(self):
        if self.variable == '':
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_inclusive.yml")
        else:
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_{self.variable}.yml")

        #Load central config file
        with open(configYamlPath, 'r') as file:
            config = yaml.safe_load(file)

        if self.output_dir == '':
            output_dir = config['outputFolder']
        else:
            output_dir = self.output_dir

        # Define the file paths
        if self.variable == '':
            output = [os.path.join(output_dir, 'Combine', f'Datacard_{self.year}.root')]
        else:
            output = [os.path.join(output_dir, 'Combine', f'Datacard_{self.variable}_{self.year}.root')]

        outputFileTargets = []

        for _, current_output_path in enumerate(output):
            outputFileTargets.append(law.LocalFileTarget(current_output_path))
        
        # print(outputFileTargets)

        return outputFileTargets

    def run(self):      

        if self.variable == '':
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_inclusive.yml")
            mode = "mu_fiducial"
            datacard_name = f"Datacard_{self.year}"
        else:
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_{self.variable}.yml")
            mode = self.variable
            datacard_name = f"Datacard_{self.variable}_{self.year}"
            workspace_name = datacard_name

        #Load central config file
        with open(configYamlPath, 'r') as file:
            config = yaml.safe_load(file)
        
        if self.output_dir == '':
            output_dir = config['outputFolder']
        else:
            output_dir = self.output_dir
            
        script_path = os.path.join(os.environ["ANALYSIS_PATH"],"Combine/RunText2Workspace.py")
        
        if self.batch_flavor == "slurm/psi":
            # Have to use /scratch/batch_username/ for slurm/psi
            os.environ["TARGET_PATH"] = f"/scratch/{os.environ['USER']}/{os.environ['SLURM_JOB_ID']}"
            execute_command([f'mkdir -p $TARGET_PATH/Combine/{config["datacard_yields"]["sigModelWSDir"]}'], shell=True)
            execute_command([f'mkdir -p $TARGET_PATH/Combine/{config["datacard_yields"]["bkgModelWSDir"]}'], shell=True)
            # Keep t2w_jobs for debugging purposes
            execute_command([f'mkdir -p $TARGET_PATH/Combine/t2w_jobs'], shell=True)    
            temp_output_dir = os.environ["TARGET_PATH"]
            
            # Copy concerning datacard + Model to scratch dir, cause of how RunText2Workspace works..
            # Copying datacard...
            slurm_copy_command = [
                'xrdcp', '-rf',
                'root://t3dcachedb.psi.ch:1094//'+ f'{output_dir}/Combine/{datacard_name}.txt',
                f'{temp_output_dir}/Combine'
            ]
            execute_command(slurm_copy_command)
            # Copying Signal Model...
            slurm_copy_command = [
                'xrdcp', '-rf',
                'root://t3dcachedb.psi.ch:1094//'+ f'{output_dir}/Combine/{config["datacard_yields"]["sigModelWSDir"]}',
                f'{temp_output_dir}/Combine/{config["datacard_yields"]["sigModelWSDir"].split("/")[-2]}'
            ]
            execute_command(slurm_copy_command)
            # Copying Background Model...
            slurm_copy_command = [
                'xrdcp', '-rf',
                'root://t3dcachedb.psi.ch:1094//'+ f'{output_dir}/Combine/{config["datacard_yields"]["bkgModelWSDir"]}',
                f'{temp_output_dir}/Combine/{config["datacard_yields"]["bkgModelWSDir"].split("/")[-2]}'
            ]
            execute_command(slurm_copy_command)
        else:
            temp_output_dir = output_dir
        
        datacards_dir = os.path.join(temp_output_dir, 'Combine')

        arguments = [
            "python3",
            script_path,
            "--inputName", datacard_name,
            "--outputDir", temp_output_dir,
            "--outputName", workspace_name,
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
        
        if self.batch_flavor == "slurm/psi":
            # Copy workspaces to workspaces folder
            list_command = ["ls", os.path.join(temp_output_dir, 'Combine', 't2w_jobs')]
            file_list = subprocess.check_output(list_command).decode().splitlines()

            print(file_list)
            execute_command([f'xrdcp -rf {datacards_dir}/{datacard_name}.root root://t3dcachedb.psi.ch:1094//{output_dir}/Combine/'], shell=True)
            execute_command([f"xrdcp -rf {os.path.join(temp_output_dir, 'Combine', 't2w_jobs/')} root://t3dcachedb.psi.ch:1094//{output_dir}/Combine/t2w_jobs/"], shell=True)
            shutil.rmtree(temp_output_dir)
        
class AsimovFitCategoryFirstStep(Task, SlurmWorkflow, HTCondorWorkflow, law.LocalWorkflow): #(law.Task): #(Task, HTCondorWorkflow, law.LocalWorkflow):
    output_dir = law.Parameter(default = '', description="Path to the output directory")
    variable = law.Parameter(default="", description="Variable to be used")
    year = law.Parameter(default='2022', description="Year")
    cats = law.Parameter(description="Current category")
    
    batch_flavor = law.Parameter(default="htcondor", description="Batch system to use")

    # def requires(self):
    def workflow_requires(self):
        workflow_reqs = super().workflow_requires()

        tasks = {}

        if workflow_reqs:
            tasks.update(workflow_reqs)
        
        if self.variable == '':
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_inclusive.yml")
        else:
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_{self.variable}.yml")
        
        #Load central config file
        with open(configYamlPath, 'r') as file:
            config = yaml.safe_load(file)
        
        if self.output_dir == '':
            output_dir = config['outputFolder']
        else:
            output_dir = self.output_dir
        
        fitConfig = config['combine_fit']
            
        tasks["RunT2WS"] = RunText2Workspace(output_dir=output_dir, variable=self.variable, year=self.year, version=self.variable if self.variable != "" else "inclusive", workflow=fitConfig["execution"], batch_flavor=self.batch_flavor, slurm_partition=fitConfig['batchPartition'], slurm_memory=fitConfig['batchMemory'], slurm_max_runtime=fitConfig['batchMaxRuntime'], htcondor_partition=fitConfig['batchPartition'], htcondor_memory=fitConfig['batchMemory'], htcondor_max_runtime=fitConfig['batchMaxRuntime'])
        
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
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_inclusive.yml")
        else:
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_{self.variable}.yml")
        
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
            
        output = [os.path.join(output_dir, 'Combine', fitFolderName, 'asimov')]

        if self.variable != '':
            output += [os.path.join(output_dir, 'Combine', fitFolderName, 'asimov', f'higgsCombinefirstStep_{current_branch}.MultiDimFit.mH125.38.root')]
            output += [os.path.join(output_dir, 'Combine', fitFolderName, 'asimov', f'multidimfitfirstStep_{current_branch}.root')]
        
        outputFileTargets = []
                
        for _, current_output_path in enumerate(output):
            outputFileTargets.append(law.LocalFileTarget(current_output_path))

        return outputFileTargets

    def run(self):
        current_branch = self.branch_data
        
        if self.variable == '':
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_inclusive.yml")
            fitFolderName = f'runFits_mu_fiducial'
            
        else:
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_{self.variable}.yml")
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

        cwd = os.getcwd()

        if self.batch_flavor == "slurm/psi":
            # Have to use /scratch/batch_username/ for slurm/psi
            if "/work" in output_dir:
                execute_command([f'mkdir -p {output_dir}/Combine/{fitFolderName}/asimov'], shell=True)
            else:   
                execute_command([f'xrdfs root://t3dcachedb.psi.ch:1094/ mkdir -p {output_dir}/Combine/{fitFolderName}/asimov'], shell=True)

            os.environ["TARGET_PATH"] = f"/scratch/{os.environ['USER']}/{os.environ['SLURM_JOB_ID']}"
            execute_command([f'mkdir -p $TARGET_PATH/Combine/{fitFolderName}/asimov'], shell=True)
            os.chdir(os.path.join(os.environ["TARGET_PATH"], 'Combine', fitFolderName, 'asimov'))
        else:
            execute_command([f'mkdir -p {output_dir}/Combine/{fitFolderName}/asimov'], shell=True)
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
                # "--X-rtd", "MINIMIZER_skipDiscreteIterations", # According to Mauro: Try without profiling
                "-t", "-1",
                "-P", f"{current_branch}",
                "--saveFitResult",
                "--saveSpecifiedIndex", f"""{",".join(combineVariableDict[f'{self.year}'][f'{self.variable}']['pdfIndeces'])}""",
                "--floatOtherPOIs", "1"
            ]
            arguments.append("--setParameters")
            arguments.append(f"""{",".join(combineVariableDict[f'{self.year}'][f'{self.variable}']['paramStr'])}""")
            command = arguments
            # print(command)
            try:
                result = subprocess.run(command, check=True, text=True, capture_output=True)
                print("Script output:", result.stdout)
                print("Script executed successfully.")
            except subprocess.CalledProcessError as e:
                print("Error executing script:", e.stderr)
        
        # Copy the files back to pnfs if we are on slurm/psi
        if self.batch_flavor == "slurm/psi":
            # Have to copy over the output to the final directory
            # Don't forget to VOMS!
            if "/work" in output_dir:
                slurm_copy_command = [
                    'cp', '-rf',
                    f"{os.environ['TARGET_PATH']}/Combine/",
                    output_dir
                ]
            else:
                slurm_copy_command = [
                    'xrdcp', '-rf',
                    f"{os.environ['TARGET_PATH']}/Combine/",
                    'root://t3dcachedb.psi.ch:1094//'+output_dir
                ]
            print(slurm_copy_command)
            execute_command(slurm_copy_command)
            # Clean up the temporary directory
            shutil.rmtree(os.environ["TARGET_PATH"])
            
        os.chdir(cwd)
        
class CreateAsimovFitFirstStep(law.Task): #(law.Task): #(Task, HTCondorWorkflow, law.LocalWorkflow):
    output_dir = law.Parameter(default = '', description="Path to the output directory")
    variable = law.Parameter(default="", description="Variable to be used")
    year = law.Parameter(default='2022', description="Year")
    
    batch_flavor = law.Parameter(default="htcondor", description="Batch system to use")
        
    def requires(self):
        
        if self.variable == '':
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_inclusive.yml")
        else:
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_{self.variable}.yml")
        
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
            cats = ",".join(combineVariableDict[f'{self.year}'][f'{self.variable}']['paramStrNoOne'])
            version = f"{self.variable}_v1"
        
        impactConfig = config['combine_impacts']
        
        tasks += [AsimovFitCategoryFirstStep(output_dir=output_dir, variable=self.variable, year=self.year, cats=cats, version=version, workflow=impactConfig["execution"], batch_flavor=self.batch_flavor, slurm_partition=impactConfig['batchPartition'], slurm_memory=impactConfig['batchMemory'], slurm_max_runtime=impactConfig['batchMaxRuntime'], htcondor_partition=impactConfig['batchPartition'], htcondor_memory=impactConfig['batchMemory'], htcondor_max_runtime=impactConfig['batchMaxRuntime'])]
            
        return tasks
    
    def create_branch_map(self):
        branch_list = [0]
        
        branch_map = {i: branch for i, branch in enumerate(branch_list)}
        return branch_map

    def output(self):
        if self.variable == '':
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_inclusive.yml")
        else:
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_{self.variable}.yml")
        
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

class AsimovFitCategorySyst(Task, HTCondorWorkflow, SlurmWorkflow, law.LocalWorkflow): #(law.Task): #(Task, HTCondorWorkflow, law.LocalWorkflow):
    output_dir = law.Parameter(default = '', description="Path to the output directory")
    variable = law.Parameter(default="", description="Variable to be used")
    year = law.Parameter(default='2022', description="Year")
    cat = law.Parameter(description="Current category")
    nPoints = law.Parameter(default=30, description="Number of points for the LL scan")
    
    batch_flavor = law.Parameter(default="htcondor", description="Batch system to use")

    # def requires(self):
    def workflow_requires(self):
        workflow_reqs = super().workflow_requires()

        tasks = {}

        if workflow_reqs:
            tasks.update(workflow_reqs)
        
        if self.variable == '':
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_inclusive.yml")
        else:
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_{self.variable}.yml")
        
        #Load central config file
        with open(configYamlPath, 'r') as file:
            config = yaml.safe_load(file)
        
        if self.output_dir == '':
            output_dir = config['outputFolder']
        else:
            output_dir = self.output_dir
               
        tasks["CreateAsimovFitFirstStep"] = CreateAsimovFitFirstStep(output_dir=output_dir, variable=self.variable, year=self.year, batch_flavor=self.batch_flavor)
        
        return tasks
    
    def create_branch_map(self):
        branch_map = {i: current_point for i, current_point in enumerate(range(int(self.nPoints)))}
        return branch_map

    def output(self):
        current_point = self.branch_data
        
        if self.variable == '':
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_inclusive.yml")
        else:
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_{self.variable}.yml")
        
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
            
        output = [os.path.join(output_dir, 'Combine', fitFolderName, 'asimov')]
        
        output += [os.path.join(output_dir, 'Combine', fitFolderName, 'asimov', f'higgsCombineAsimovPostFitScanFit_{self.cat}.POINTS.{current_point}.{current_point}.MultiDimFit.mH125.38.root')]
        
        outputFileTargets = []
                
        for _, current_output_path in enumerate(output):
            outputFileTargets.append(law.LocalFileTarget(current_output_path))
            
        return outputFileTargets

    def run(self):
        current_point = self.branch_data
        
        if self.variable == '':
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_inclusive.yml")
            fitFolderName = f'runFits_mu_fiducial'
            
        else:
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_{self.variable}.yml")
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
            
        cwd = os.getcwd()
        if self.batch_flavor == "slurm/psi":
            # Have to use /scratch/batch_username/ for slurm/psi
            if "/work" in output_dir:
                execute_command([f'mkdir -p {output_dir}/Combine/{fitFolderName}/asimov'], shell=True)
            else:   
                execute_command([f'xrdfs root://t3dcachedb.psi.ch:1094/ mkdir -p {output_dir}/Combine/{fitFolderName}/asimov'], shell=True)

            os.environ["TARGET_PATH"] = f"/scratch/{os.environ['USER']}/{os.environ['SLURM_JOB_ID']}"
            execute_command([f'mkdir -p $TARGET_PATH/Combine/{fitFolderName}/asimov'], shell=True)
            os.chdir(os.path.join(os.environ["TARGET_PATH"], 'Combine', fitFolderName, 'asimov'))
        else:
            execute_command([f'mkdir -p {output_dir}/Combine/{fitFolderName}/asimov'], shell=True)
            os.chdir(os.path.join(output_dir, 'Combine', fitFolderName, 'asimov'))

        first_output = os.path.join(output_dir, 'Combine', fitFolderName, 'asimov')

        def check_pdf_idx(param):
            # Run the ROOT command
            command = f'root -l -q \'{os.environ["ANALYSIS_PATH"]}/Combine/checkPdfIdx.C("{first_output}/higgsCombinefirstStep_{param}.MultiDimFit.mH125.38.root")\''
            
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
                # "--X-rtd", "MINIMIZER_skipDiscreteIterations", # According to Mauro: Try without profiling
                "-t", "-1",
                "-P", f"{self.cat}",
                "--firstPoint", f"{current_point}",
                "--lastPoint", f"{current_point}",
                "--saveFitResult",
                "--floatOtherPOIs", "1",
                "--alignEdges", "1",
                "--saveSpecifiedIndex", f"""{",".join(combineVariableDict[f'{self.year}'][f'{self.variable}']['pdfIndeces'])}""",
                "--setParameters", f"""{pdfIdx},{",".join(combineVariableDict[f'{self.year}'][f'{self.variable}']['paramStr'])}""",
                # "--setParameters", f"""{",".join(combineVariableDict[f'{self.year}'][f'{self.variable}']['paramStr'])}""", # According to Mauro: Try without profiling
            ]
            command = arguments
            # print(command)
            try:
                result = subprocess.run(command, check=True, text=True, capture_output=True)
                print("Script output:", result.stdout)
                print("Script executed successfully.")
            except subprocess.CalledProcessError as e:
                print("Error executing script:", e.stderr)
            
        # Copy the files back to pnfs if we are on slurm/psi
        if self.batch_flavor == "slurm/psi":
            # Have to copy over the output to the final directory
            # Don't forget to VOMS!
            if "/work" in output_dir:
                slurm_copy_command = [
                    'cp', '-rf',
                    f"{os.environ['TARGET_PATH']}/Combine/",
                    output_dir
                ]
            else:
                slurm_copy_command = [
                    'xrdcp', '-rf',
                    f"{os.environ['TARGET_PATH']}/Combine/",
                    'root://t3dcachedb.psi.ch:1094//'+output_dir
                ]
            print(slurm_copy_command)
            execute_command(slurm_copy_command)
            # Clean up the temporary directory
            shutil.rmtree(os.environ["TARGET_PATH"])
            
        os.chdir(cwd)
        
class AsimovFitCategoryStat(Task, HTCondorWorkflow, SlurmWorkflow, law.LocalWorkflow): #(law.Task): #(Task, HTCondorWorkflow, law.LocalWorkflow):
    output_dir = law.Parameter(default = '', description="Path to the output directory")
    variable = law.Parameter(default="", description="Variable to be used")
    year = law.Parameter(default='2022', description="Year")
    cat = law.Parameter(description="Current category")
    nPoints = law.Parameter(default=30, description="Number of points for the LL scan")
    
    batch_flavor = law.Parameter(default="htcondor", description="Batch system to use")

    # def requires(self):
    def workflow_requires(self):
        workflow_reqs = super().workflow_requires()

        tasks = {}

        if workflow_reqs:
            tasks.update(workflow_reqs)
        
        if self.variable == '':
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_inclusive.yml")
        else:
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_{self.variable}.yml")
        
        #Load central config file
        with open(configYamlPath, 'r') as file:
            config = yaml.safe_load(file)
        
        if self.output_dir == '':
            output_dir = config['outputFolder']
        else:
            output_dir = self.output_dir
                
        tasks["CreateAsimovFitFirstStep"] = CreateAsimovFitFirstStep(output_dir=output_dir, variable=self.variable, year=self.year, batch_flavor=self.batch_flavor)
        
        return tasks
    
    def create_branch_map(self):
        branch_map = {i: current_point for i, current_point in enumerate(range(int(self.nPoints)))}
        return branch_map

    def output(self):
        current_point = self.branch_data
        
        if self.variable == '':
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_inclusive.yml")
        else:
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_{self.variable}.yml")
        
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
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_inclusive.yml")
            fitFolderName = f'runFits_mu_fiducial'
            
        else:
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_{self.variable}.yml")
            fitFolderName = f'runFits_{self.variable}'
                    
        #Load central config file
        with open(configYamlPath, 'r') as file:
            config = yaml.safe_load(file)
        
        if self.output_dir == '':
            output_dir = config['outputFolder']
        else:
            output_dir = self.output_dir  
        
        cwd = os.getcwd()
        if self.batch_flavor == "slurm/psi":
            # Have to use /scratch/batch_username/ for slurm/psi
            if "/work" in output_dir:
                execute_command([f'mkdir -p {output_dir}/Combine/{fitFolderName}/asimov'], shell=True)
            else:   
                execute_command([f'xrdfs root://t3dcachedb.psi.ch:1094/ mkdir -p {output_dir}/Combine/{fitFolderName}/asimov'], shell=True)

            os.environ["TARGET_PATH"] = f"/scratch/{os.environ['USER']}/{os.environ['SLURM_JOB_ID']}"
            execute_command([f'mkdir -p $TARGET_PATH/Combine/{fitFolderName}/asimov'], shell=True)
            os.chdir(os.path.join(os.environ["TARGET_PATH"], 'Combine', fitFolderName, 'asimov'))
        else:
            execute_command([f'mkdir -p {output_dir}/Combine/{fitFolderName}/asimov'], shell=True)
            os.chdir(os.path.join(output_dir, 'Combine', fitFolderName, 'asimov'))
            
        first_output = os.path.join(output_dir, 'Combine', fitFolderName, 'asimov')
        
        def check_pdf_idx(param):
            # Run the ROOT command
            command = f'root -l -q \'{os.environ["ANALYSIS_PATH"]}/Combine/checkPdfIdx.C("{first_output}/higgsCombinefirstStep_{param}.MultiDimFit.mH125.38.root")\''
            
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
                # "--X-rtd", "MINIMIZER_skipDiscreteIterations", # According to Mauro: Try without profiling
                "-t", "-1",
                "-P", f"{self.cat}",
                "--firstPoint", f"{current_point}",
                "--lastPoint", f"{current_point}",
                "--saveFitResult",
                "--floatOtherPOIs", "1",
                "--alignEdges", "1",
                "--snapshotName", "MultiDimFit",
                "--saveSpecifiedIndex", f"""{",".join(combineVariableDict[f'{self.year}'][f'{self.variable}']['pdfIndeces'])}""",
                "--setParameters", f"""{pdfIdx},{",".join(combineVariableDict[f'{self.year}'][f'{self.variable}']['paramStr'])}""",
                # "--setParameters", f"""{",".join(combineVariableDict[f'{self.year}'][f'{self.variable}']['paramStr'])}""", # According to Mauro: Try without profiling
            ]
            command = arguments
            # print(command)
            try:
                result = subprocess.run(command, check=True, text=True, capture_output=True)
                print("Script output:", result.stdout)
                print("Script executed successfully.")
            except subprocess.CalledProcessError as e:
                print("Error executing script:", e.stderr)
        
        # Copy the files back to pnfs if we are on slurm/psi
        if self.batch_flavor == "slurm/psi":
            # Have to copy over the output to the final directory
            # Don't forget to VOMS!
            if "/work" in output_dir:
                slurm_copy_command = [
                    'cp', '-rf',
                    f"{os.environ['TARGET_PATH']}/Combine/",
                    output_dir
                ]
            else:
                slurm_copy_command = [
                    'xrdcp', '-rf',
                    f"{os.environ['TARGET_PATH']}/Combine/",
                    'root://t3dcachedb.psi.ch:1094//'+output_dir
                ]
            print(slurm_copy_command)
            execute_command(slurm_copy_command)
            # Clean up the temporary directory
            shutil.rmtree(os.environ["TARGET_PATH"])
        
        os.chdir(cwd)
        
class CreateAsimovFit(Task, SlurmWorkflow, HTCondorWorkflow, law.LocalWorkflow): #(law.Task): #(Task, HTCondorWorkflow, law.LocalWorkflow):
    output_dir = law.Parameter(default = '', description="Path to the output directory")
    variable = law.Parameter(default="", description="Variable to be used")
    year = law.Parameter(default='2022', description="Year")
    
    batch_flavor = law.Parameter(default="htcondor", description="Batch system to use")

    # def requires(self):
    def workflow_requires(self):
        workflow_reqs = super().workflow_requires()

        tasks = {}

        if workflow_reqs:
            tasks.update(workflow_reqs)
        
        if self.variable == '':
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_inclusive.yml")
        else:
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_{self.variable}.yml")
        
        #Load central config file
        with open(configYamlPath, 'r') as file:
            config = yaml.safe_load(file)
        
        if self.output_dir == '':
            output_dir = config['outputFolder']
        else:
            output_dir = self.output_dir
                        
        if self.variable == '':
            cat = "r"
            tasks["AsimovFitCategorySyst"] = AsimovFitCategorySyst(output_dir=output_dir, variable=self.variable, year=self.year, cat=cat, nPoints=config["combine_fit"]["asimov_numPoints"], version=f"inclusive_v1", workflow=config["combine_fit"]["execution"], batch_flavor=self.batch_flavor, slurm_partition=config["combine_fit"]['batchPartition'], slurm_memory=config["combine_fit"]['batchMemory'], slurm_max_runtime=config["combine_fit"]['batchMaxRuntime'], htcondor_partition=config["combine_fit"]['batchPartition'], htcondor_memory=config["combine_fit"]['batchMemory'], htcondor_max_runtime=config["combine_fit"]['batchMaxRuntime'])
            tasks["AsimovFitCategoryStat"] = AsimovFitCategoryStat(output_dir=output_dir, variable=self.variable, year=self.year, cat=cat, nPoints=config["combine_fit"]["asimov_numPoints"], version=f"inclusive_v1", workflow=config["combine_fit"]["execution"], batch_flavor=self.batch_flavor, slurm_partition=config["combine_fit"]['batchPartition'], slurm_memory=config["combine_fit"]['batchMemory'], slurm_max_runtime=config["combine_fit"]['batchMaxRuntime'], htcondor_partition=config["combine_fit"]['batchPartition'], htcondor_memory=config["combine_fit"]['batchMemory'], htcondor_max_runtime=config["combine_fit"]['batchMaxRuntime'])
        else:
            version_index = 1
            for cat in combineVariableDict[f'{self.year}'][f'{self.variable}']['paramStrNoOne']:
                tasks[f"AsimovFitCategorySyst_{cat}"] = AsimovFitCategorySyst(output_dir=output_dir, variable=self.variable, year=self.year, cat=cat, nPoints=config["combine_fit"]["asimov_numPoints"], version=f"{self.variable}_v{version_index}", workflow=config["combine_fit"]["execution"], batch_flavor=self.batch_flavor, slurm_partition=config["combine_fit"]['batchPartition'], slurm_memory=config["combine_fit"]['batchMemory'], slurm_max_runtime=config["combine_fit"]['batchMaxRuntime'], htcondor_partition=config["combine_fit"]['batchPartition'], htcondor_memory=config["combine_fit"]['batchMemory'], htcondor_max_runtime=config["combine_fit"]['batchMaxRuntime'])
                tasks[f"AsimovFitCategoryStat_{cat}"] = AsimovFitCategoryStat(output_dir=output_dir, variable=self.variable, year=self.year, cat=cat, nPoints=config["combine_fit"]["asimov_numPoints"], version=f"{self.variable}_v{version_index}", workflow=config["combine_fit"]["execution"], batch_flavor=self.batch_flavor, slurm_partition=config["combine_fit"]['batchPartition'], slurm_memory=config["combine_fit"]['batchMemory'], slurm_max_runtime=config["combine_fit"]['batchMaxRuntime'], htcondor_partition=config["combine_fit"]['batchPartition'], htcondor_memory=config["combine_fit"]['batchMemory'], htcondor_max_runtime=config["combine_fit"]['batchMaxRuntime'])
                version_index += 1
        
        return tasks
    
    def create_branch_map(self):
        # map branch indexes to ascii numbers from 97 to 122 ("a" to "z")        
        branch_list = [0]
        
        branch_map = {i: branch for i, branch in enumerate(branch_list)}
        return branch_map

    def output(self):
        if self.variable == '':
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_inclusive.yml")
        else:
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_{self.variable}.yml")
        
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
            for cat in combineVariableDict[f'{self.year}'][f'{self.variable}']['paramStrNoOne']:
                
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
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_inclusive.yml")
            fitFolderName = f'runFits_mu_fiducial'
        else:
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_{self.variable}.yml")
            fitFolderName = f'runFits_{self.variable}'
            
                    
        #Load central config file
        with open(configYamlPath, 'r') as file:
            config = yaml.safe_load(file)
        
        if self.output_dir == '':
            output_dir = config['outputFolder']
        else:
            output_dir = self.output_dir  
            
        cwd = os.getcwd()
        
        if self.batch_flavor == "slurm/psi":
            # Have to use /scratch/batch_username/ for slurm/psi
            if "/work" in output_dir:
                execute_command([f'mkdir -p {output_dir}/Combine/{fitFolderName}/asimov/scans'], shell=True)
            else:   
                execute_command([f'xrdfs root://t3dcachedb.psi.ch:1094/ mkdir -p {output_dir}/Combine/{fitFolderName}/asimov/scans'], shell=True)

            os.environ["TARGET_PATH"] = f"/scratch/{os.environ['USER']}/{os.environ['SLURM_JOB_ID']}"
            execute_command([f'mkdir -p $TARGET_PATH/Combine/{fitFolderName}/asimov/scans'], shell=True)
            os.chdir(os.path.join(os.environ["TARGET_PATH"], 'Combine', fitFolderName, 'asimov'))
        else:
            execute_command([f'mkdir -p {output_dir}/Combine/{fitFolderName}/asimov/scans'], shell=True)
            os.chdir(os.path.join(output_dir, 'Combine', fitFolderName, 'asimov'))
        
        if self.variable == '':
            cats = ["r"]
        else:
            cats = combineVariableDict[f'{self.year}'][f'{self.variable}']['paramStrNoOne']
        
        if self.batch_flavor == "slurm/psi":
            # Have to copy over the input to the JOB directory
            # Don't forget to VOMS!
            if "/work" in output_dir:
                slurm_copy_command = [
                    'cp', '-rf',
                    f'{output_dir}/Combine/{fitFolderName}/asimov',
                    f"{os.environ['TARGET_PATH']}/Combine/{fitFolderName}"
                ]
            else:
                slurm_copy_command = [
                    'xrdcp', '-rf',
                    'root://t3dcachedb.psi.ch:1094//'+f'{output_dir}/Combine/{fitFolderName}/asimov',
                    f"{os.environ['TARGET_PATH']}/Combine/{fitFolderName}"
                ]
            print(slurm_copy_command)
            execute_command(slurm_copy_command)
        
        for cat in cats:
        
            arguments = [
                "hadd", "-f",
                f"{os.path.join(output_dir, 'Combine', fitFolderName, 'asimov', f'higgsCombineAsimovPostFitScanFit_{cat}.root')}"
            ]
            for i in range(config["combine_fit"]["asimov_numPoints"]):
                arguments.append(os.path.join(output_dir, 'Combine', fitFolderName, 'asimov', f'higgsCombineAsimovPostFitScanFit_{cat}.POINTS.{i}.{i}.MultiDimFit.mH125.38.root'))
            if self.batch_flavor == "slurm/psi":
                arguments = [
                    "hadd", "-f",
                    f"{os.path.join(os.environ['TARGET_PATH'], 'Combine', fitFolderName, 'asimov', f'higgsCombineAsimovPostFitScanFit_{cat}.root')}"
                ]
                for i in range(config["combine_fit"]["asimov_numPoints"]):
                    arguments.append(os.path.join(os.environ['TARGET_PATH'], 'Combine', fitFolderName, 'asimov', f'higgsCombineAsimovPostFitScanFit_{cat}.POINTS.{i}.{i}.MultiDimFit.mH125.38.root'))
            command = arguments
            # print(command)
            try:
                result = subprocess.run(command, check=True, text=True, capture_output=True)
                print("Script output:", result.stdout)
                print("Script executed successfully.")
            except subprocess.CalledProcessError as e:
                print("Error executing script:", e.stderr)
                
            
            arguments = [
                "hadd", "-f",
                f"{os.path.join(output_dir, 'Combine', fitFolderName, 'asimov', f'higgsCombineAsimovPostFitScanStat_{cat}.root')}"
            ]
            for i in range(config["combine_fit"]["asimov_numPoints"]):
                arguments.append(os.path.join(output_dir, 'Combine', fitFolderName, 'asimov', f'higgsCombineAsimovPostFitScanStat_{cat}.POINTS.{i}.{i}.MultiDimFit.mH125.38.root'))
            if self.batch_flavor == "slurm/psi":
                arguments = [
                    "hadd", "-f",
                    f"{os.path.join(os.environ['TARGET_PATH'], 'Combine', fitFolderName, 'asimov', f'higgsCombineAsimovPostFitScanStat_{cat}.root')}"
                ]
                for i in range(config["combine_fit"]["asimov_numPoints"]):
                    arguments.append(os.path.join(os.environ['TARGET_PATH'], 'Combine', fitFolderName, 'asimov', f'higgsCombineAsimovPostFitScanStat_{cat}.POINTS.{i}.{i}.MultiDimFit.mH125.38.root'))
            command = arguments
            print(command)
            try:
                result = subprocess.run(command, check=True, text=True, capture_output=True)
                print("Script output:", result.stdout)
                print("Script executed successfully.")
            except subprocess.CalledProcessError as e:
                print("Error executing script:", e.stderr)

            # change to the scans directory
            if self.batch_flavor == "slurm/psi":
                os.chdir(os.path.join(os.environ["TARGET_PATH"], 'Combine', fitFolderName, 'asimov', 'scans'))
            else:
                os.chdir(os.path.join(output_dir, 'Combine', fitFolderName, 'asimov', 'scans'))

            arguments = [
                "python3", f"{os.environ['CMSSW_BASE']}/bin/{os.environ['SCRAM_ARCH']}/plot1DScan.py",
                # "plot1DScan.py",
                os.path.join(output_dir, 'Combine', fitFolderName, 'asimov', f'higgsCombineAsimovPostFitScanFit_{cat}.root'),
                "-o", f"scan_{cat}",
                "--POI", f"{cat}",
                "--others", os.path.join(output_dir, 'Combine', fitFolderName, 'asimov', f'higgsCombineAsimovPostFitScanStat_{cat}.root')+":stat-only:2",
                "--main-label", "Expected",
                "--translate", os.path.join(os.environ["ANALYSIS_PATH"], 'Combine', 'pois.json')
            ]
            if self.batch_flavor == "slurm/psi":
                arguments = [
                    "python3", f"{os.environ['CMSSW_BASE']}/bin/{os.environ['SCRAM_ARCH']}/plot1DScan.py",
                    # "plot1DScan.py",
                    os.path.join(os.environ['TARGET_PATH'], 'Combine', fitFolderName, 'asimov', f'higgsCombineAsimovPostFitScanFit_{cat}.root'),
                    "-o", f"scan_{cat}",
                    "--POI", f"{cat}",
                    "--others", os.path.join(os.environ['TARGET_PATH'], 'Combine', fitFolderName, 'asimov', f'higgsCombineAsimovPostFitScanStat_{cat}.root')+":stat-only:2",
                    "--main-label", "Expected",
                    "--translate", os.path.join(os.environ["ANALYSIS_PATH"], 'Combine', 'pois.json')
                ]
            command = arguments
            print(command)
            try:
                result = subprocess.run(command, check=True, text=True, capture_output=True)
                print("Script output:", result.stdout)
                print("Script executed successfully.")
            except subprocess.CalledProcessError as e:
                print("Error executing script:", e.stderr)
    
        # Copy the files back to pnfs if we are on slurm/psi
        if self.batch_flavor == "slurm/psi":
            # Have to copy over the output to the final directory
            # Don't forget to VOMS!
            if "/work" in output_dir:
                slurm_copy_command = [
                    'cp', '-rf',
                    f"{os.environ['TARGET_PATH']}/Combine/",
                    output_dir
                ]
            else:
                slurm_copy_command = [
                    'xrdcp', '-rf',
                    f"{os.environ['TARGET_PATH']}/Combine/",
                    'root://t3dcachedb.psi.ch:1094//'+output_dir
                ]
            print(slurm_copy_command)
            execute_command(slurm_copy_command)
            # Clean up the temporary directory
            shutil.rmtree(os.environ["TARGET_PATH"])
            
        os.chdir(cwd)
        
class AsimovImpactFirstStep(Task, SlurmWorkflow, HTCondorWorkflow, law.LocalWorkflow): #(law.Task): #(Task, HTCondorWorkflow, law.LocalWorkflow):
    output_dir = law.Parameter(default = '', description="Path to the output directory")
    variable = law.Parameter(default="", description="Variable to be used")
    year = law.Parameter(default='2022', description="Year")
    
    batch_flavor = law.Parameter(default="htcondor", description="Batch system to use")

    # def requires(self):
    def workflow_requires(self):
        workflow_reqs = super().workflow_requires()

        tasks = {}

        if workflow_reqs:
            tasks.update(workflow_reqs)
        
        if self.variable == '':
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_inclusive.yml")
        else:
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_{self.variable}.yml")
        
        #Load central config file
        with open(configYamlPath, 'r') as file:
            config = yaml.safe_load(file)
        
        if self.output_dir == '':
            output_dir = config['outputFolder']
        else:
            output_dir = self.output_dir
        
        impactConfig = config["combine_impacts"]    
        
        tasks["RunT2WS"] = RunText2Workspace(output_dir=output_dir, variable=self.variable, year=self.year, version=self.variable if self.variable != "" else "inclusive", workflow=impactConfig["execution"], batch_flavor=self.batch_flavor, slurm_partition=impactConfig['batchPartition'], slurm_memory=impactConfig['batchMemory'], slurm_max_runtime=impactConfig['batchMaxRuntime'], htcondor_partition=impactConfig['batchPartition'], htcondor_memory=impactConfig['batchMemory'], htcondor_max_runtime=impactConfig['batchMaxRuntime'])
        
        return tasks

    def create_branch_map(self):
        branch_map = {i: current_branch for i, current_branch in enumerate([0])}
        return branch_map

    def output(self):        
        if self.variable == '':
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_inclusive.yml")
        else:
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_{self.variable}.yml")
        
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
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_inclusive.yml")
            fitFolderName = f'runFits_mu_fiducial'
            
        else:
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_{self.variable}.yml")
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
        
        cwd = os.getcwd()
        if self.batch_flavor == "slurm/psi":
            # Have to use /scratch/batch_username/ for slurm/psi
            if "/work" in output_dir:
                execute_command([f'mkdir -p {output_dir}/Combine/{fitFolderName}/impact'], shell=True)
            else:   
                execute_command([f'xrdfs root://t3dcachedb.psi.ch:1094/ mkdir -p {output_dir}/Combine/{fitFolderName}/impact'], shell=True)

            os.environ["TARGET_PATH"] = f"/scratch/{os.environ['USER']}/{os.environ['SLURM_JOB_ID']}"
            execute_command([f'mkdir -p $TARGET_PATH/Combine/{fitFolderName}/impact'], shell=True)
            os.chdir(os.path.join(os.environ["TARGET_PATH"], 'Combine', fitFolderName, 'impact'))
        else:
            execute_command([f'mkdir -p {output_dir}/Combine/{fitFolderName}/impact'], shell=True)
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
                "--redefineSignalPOIs", f"""{",".join(combineVariableDict[f'{self.year}'][f'{self.variable}']['paramStrNoOne'])}""",
                "--freezeParameters", "MH",
                "-m", "125.38",
                "-n", "_initialFit_Test",
                "--cminDefaultMinimizerStrategy=0",
                "--X-rtd", "MINIMIZER_freezeDisassociatedParams",
                "--X-rtd", "MINIMIZER_multiMin_hideConstants",
                "--X-rtd", "MINIMIZER_multiMin_maskConstraints",
                "--X-rtd", "MINIMIZER_multiMin_maskChannels=2",
                "-t", "-1",
                "--setParameters", f"""{",".join(combineVariableDict[f'{self.year}'][f'{self.variable}']['paramStr'])}"""
            ]
            command = arguments
            # print(command)
            try:
                result = subprocess.run(command, check=True, text=True, capture_output=True)
                print("Script output:", result.stdout)
                print("Script executed successfully.")
            except subprocess.CalledProcessError as e:
                print("Error executing script:", e.stderr)

        # Copy the files back to pnfs if we are on slurm/psi
        if self.batch_flavor == "slurm/psi":
            # Have to copy over the output to the final directory
            # Don't forget to VOMS!
            if "/work" in output_dir:
                slurm_copy_command = [
                    'cp', '-rf',
                    f"{os.environ['TARGET_PATH']}/Combine/",
                    output_dir
                ]
            else:
                slurm_copy_command = [
                    'xrdcp', '-rf',
                    f"{os.environ['TARGET_PATH']}/Combine/",
                    'root://t3dcachedb.psi.ch:1094//'+output_dir
                ]
            print(slurm_copy_command)
            execute_command(slurm_copy_command)
            # Clean up the temporary directory
            shutil.rmtree(os.environ["TARGET_PATH"])
        
            
        os.chdir(cwd)
        
class AsimovImpactSecondStep(Task, HTCondorWorkflow, SlurmWorkflow, law.LocalWorkflow): #(law.Task): #(Task, HTCondorWorkflow, law.LocalWorkflow):
    output_dir = law.Parameter(default = '', description="Path to the output directory")
    variable = law.Parameter(default="", description="Variable to be used")
    year = law.Parameter(default='2022', description="Year")

    batch_flavor = law.Parameter(default="htcondor", description="Batch system to use")

    # def requires(self):
    def workflow_requires(self):
        workflow_reqs = super().workflow_requires()

        tasks = {}

        if workflow_reqs:
            tasks.update(workflow_reqs)
        
        if self.variable == '':
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_inclusive.yml")
        else:
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_{self.variable}.yml")
        
        #Load central config file
        with open(configYamlPath, 'r') as file:
            config = yaml.safe_load(file)
        
        if self.output_dir == '':
            output_dir = config['outputFolder']
        else:
            output_dir = self.output_dir
        
        impactConfig = config["combine_impacts"]
            
        tasks["AsimovImpactFirstStep"] = AsimovImpactFirstStep(output_dir=output_dir, variable=self.variable, year=self.year, batch_flavor=self.batch_flavor, workflow=impactConfig["execution"], version=self.variable if self.variable != '' else 'inclusive', slurm_partition=impactConfig['batchPartition'], slurm_memory=impactConfig['batchMemory'], slurm_max_runtime=impactConfig['batchMaxRuntime'], htcondor_partition=impactConfig['batchPartition'], htcondor_memory=impactConfig['batchMemory'], htcondor_max_runtime=impactConfig['batchMaxRuntime'])
        
        return tasks

    def create_branch_map(self):
        
        if self.variable == '':
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_inclusive.yml")
        else:
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_{self.variable}.yml")
                  
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
            poiList = combineVariableDict[f'{self.year}'][f'{self.variable}']['paramStrNoOne']
        
        paramList = all_free_parameters(datacard_path, 'w', 'ModelConfig', poiList)

        
        branch_map = {i: current_param for i, current_param in enumerate(paramList)}
        return branch_map

    def output(self):        
        current_param = self.branch_data
        
        if self.variable == '':
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_inclusive.yml")
        else:
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_{self.variable}.yml")
        
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
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_inclusive.yml")
            fitFolderName = f'runFits_mu_fiducial'
            
        else:
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_{self.variable}.yml")
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
        
        cwd = os.getcwd()
        if self.batch_flavor == "slurm/psi":
            # Have to use /scratch/batch_username/ for slurm/psi
            if "/work" in output_dir:
                execute_command([f'mkdir -p {output_dir}/Combine/{fitFolderName}/impact'], shell=True)
            else:   
                execute_command([f'xrdfs root://t3dcachedb.psi.ch:1094/ mkdir -p {output_dir}/Combine/{fitFolderName}/impact'], shell=True)

            os.environ["TARGET_PATH"] = f"/scratch/{os.environ['USER']}/{os.environ['SLURM_JOB_ID']}"
            execute_command([f'mkdir -p $TARGET_PATH/Combine/{fitFolderName}/impact'], shell=True)
            os.chdir(os.path.join(os.environ["TARGET_PATH"], 'Combine', fitFolderName, 'impact'))
        else:
            execute_command([f'mkdir -p {output_dir}/Combine/{fitFolderName}/impact'], shell=True)
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
                "--redefineSignalPOIs", f"""{",".join(combineVariableDict[f'{self.year}'][f'{self.variable}']['paramStrNoOne'])}""",
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
                "--setParameters", f"""{",".join(combineVariableDict[f'{self.year}'][f'{self.variable}']['paramStr'])}"""
            ]
            command = arguments
            # print(command)
            try:
                result = subprocess.run(command, check=True, text=True, capture_output=True)
                print("Script output:", result.stdout)
                print("Script executed successfully.")
            except subprocess.CalledProcessError as e:
                print("Error executing script:", e.stderr)

        # Copy the files back to pnfs if we are on slurm/psi
        if self.batch_flavor == "slurm/psi":
            # Have to copy over the output to the final directory
            # Don't forget to VOMS!
            if "/work" in output_dir:
                slurm_copy_command = [
                    'cp', '-rf',
                    f"{os.environ['TARGET_PATH']}/Combine/",
                    output_dir
                ]
            else:
                slurm_copy_command = [
                    'xrdcp', '-rf',
                    f"{os.environ['TARGET_PATH']}/Combine/",
                    'root://t3dcachedb.psi.ch:1094//'+output_dir
                ]
            print(slurm_copy_command)
            execute_command(slurm_copy_command)
            # Clean up the temporary directory
            shutil.rmtree(os.environ["TARGET_PATH"])
        
        os.chdir(cwd)
        
class AsimovImpactThirdStep(Task, SlurmWorkflow, HTCondorWorkflow, law.LocalWorkflow): #(law.Task): #(Task, HTCondorWorkflow, law.LocalWorkflow):
    output_dir = law.Parameter(default = '', description="Path to the output directory")
    variable = law.Parameter(default="", description="Variable to be used")
    year = law.Parameter(default='2022', description="Year")

    batch_flavor = law.Parameter(default="htcondor", description="Batch system to use")

    # def requires(self):
    def workflow_requires(self):
        workflow_reqs = super().workflow_requires()

        tasks = {}

        if workflow_reqs:
            tasks.update(workflow_reqs)
        
        if self.variable == '':
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_inclusive.yml")
        else:
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_{self.variable}.yml")
        
        #Load central config file
        with open(configYamlPath, 'r') as file:
            config = yaml.safe_load(file)
        
        impactConfig = config["combine_impacts"]
        
        if self.output_dir == '':
            output_dir = config['outputFolder']
        else:
            output_dir = self.output_dir
        
        tasks["AsimovImpactSecondStep"] = AsimovImpactSecondStep(output_dir=output_dir, variable=self.variable, year=self.year, batch_flavor=self.batch_flavor, workflow=impactConfig["execution"], version=self.variable if self.variable != '' else 'inclusive', slurm_partition=impactConfig['batchPartition'], slurm_memory=impactConfig['batchMemory'], slurm_max_runtime=impactConfig['batchMaxRuntime'], htcondor_partition=impactConfig['batchPartition'], htcondor_memory=impactConfig['batchMemory'], htcondor_max_runtime=impactConfig['batchMaxRuntime'])
        
        return tasks

    def create_branch_map(self):
        branch_map = {i: current_branch for i, current_branch in enumerate([0])}
        return branch_map

    def output(self):
        if self.variable == '':
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_inclusive.yml")
        else:
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_{self.variable}.yml")
        
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
            output += [os.path.join(output_dir, 'Combine', fitFolderName, 'impact', 'impacts')]
            output += [os.path.join(output_dir, 'Combine', fitFolderName, 'impact', 'impacts', f'impacts.pdf')]
            output += [os.path.join(output_dir, 'Combine', fitFolderName, 'impact', 'impacts', 'impacts_corrected_dropBkgModelParams.json')]
            
        else:
            for cat in combineVariableDict[f'{self.year}'][f'{self.variable}']['paramStrNoOne']:
                output += [os.path.join(output_dir, 'Combine', fitFolderName, 'impact', 'impacts')]
                output += [os.path.join(output_dir, 'Combine', fitFolderName, 'impact', 'impacts', f'impacts_{cat}.pdf')]
                
        output += [os.path.join(output_dir, 'Combine', fitFolderName, 'impact', 'impacts', f'impacts.json')]
        
        outputFileTargets = []
                
        for _, current_output_path in enumerate(output):
            outputFileTargets.append(law.LocalFileTarget(current_output_path))
            
        # print(outputFileTargets)

        return outputFileTargets

    def run(self):
        if self.variable == '':
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_inclusive.yml")
            fitFolderName = f'runFits_mu_fiducial'
            
        else:
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_{self.variable}.yml")
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

        cwd = os.getcwd()
        if self.batch_flavor == "slurm/psi":
            # Have to use /scratch/batch_username/ for slurm/psi
            if "/work" in output_dir:
                execute_command([f'mkdir -p {output_dir}/Combine/{fitFolderName}/impact/impacts'], shell=True)
            else:   
                execute_command([f'xrdfs root://t3dcachedb.psi.ch:1094/ mkdir -p {output_dir}/Combine/{fitFolderName}/impact/impacts'], shell=True)

            os.environ["TARGET_PATH"] = f"/scratch/{os.environ['USER']}/{os.environ['SLURM_JOB_ID']}"
            execute_command([f'mkdir -p $TARGET_PATH/Combine/{fitFolderName}/impact/impacts'], shell=True)
            if "/work" in output_dir:
                slurm_copy_command = [
                    'cp', '-rf',
                    f'{output_dir}/Combine/{fitFolderName}/impact',
                    f'{os.environ["TARGET_PATH"]}/Combine/{fitFolderName}'
                ]
            else:
                slurm_copy_command = [
                    'xrdcp', '-rf',
                    'root://t3dcachedb.psi.ch:1094//'+ f'{output_dir}/Combine/{fitFolderName}/impact',
                    f'{os.environ["TARGET_PATH"]}/Combine/{fitFolderName}'
                ]
            execute_command(slurm_copy_command)
            os.chdir(os.path.join(os.environ["TARGET_PATH"], 'Combine', fitFolderName, 'impact'))
            temp_output_dir = os.environ["TARGET_PATH"]
        else:
            execute_command([f'mkdir -p {output_dir}/Combine/{fitFolderName}/impact/impacts'], shell=True)
            os.chdir(os.path.join(output_dir, 'Combine', fitFolderName, 'impact'))
            temp_output_dir = output_dir

        if self.variable == '':
            arguments = [
                "combineTool.py",
                "-M", "Impacts",
                "-d", datacard_path,
                "-m", "125.38",
                "-o", "impacts/impacts.json"
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
                f"{os.path.join(os.environ['ANALYSIS_PATH'], 'Plots', 'correctImpacts.py')}",
                "--impactsJson", f"{os.path.join(temp_output_dir, 'Combine', fitFolderName, 'impact', 'impacts', 'impacts.json')}",
                "--frozenParam", "MH",
                "--dropBkgModelParams"
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
                "-i", "impacts/impacts_corrected_dropBkgModelParams.json",
                "-o", "impacts/impacts",

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
                "-o", "impacts/impacts.json",
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
                
            for cat in combineVariableDict[f'{self.year}'][f'{self.variable}']['paramStrNoOne']:
                arguments = [
                    "plotImpacts.py",
                    "-i", "impacts/impacts.json",
                    "-o", f"impacts/impacts_{cat}",
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

        # Copy the files back to pnfs if we are on slurm/psi
        if self.batch_flavor == "slurm/psi":
            # Have to copy over the output to the final directory
            # Don't forget to VOMS!
            if "/work" in output_dir:
                slurm_copy_command = [
                    'cp', '-rf',
                    f"{os.environ['TARGET_PATH']}/Combine/",
                    output_dir
                ]
            else:
                slurm_copy_command = [
                    'xrdcp', '-rf',
                    f"{os.environ['TARGET_PATH']}/Combine/",
                    'root://t3dcachedb.psi.ch:1094//'+output_dir
                ]
            print(slurm_copy_command)
            execute_command(slurm_copy_command)
            # Clean up the temporary directory
            shutil.rmtree(os.environ["TARGET_PATH"])
            
        os.chdir(cwd)


class AsimovCovCorrHesse(Task, SlurmWorkflow, HTCondorWorkflow, law.LocalWorkflow): #(law.Task): #(Task, HTCondorWorkflow, law.LocalWorkflow):
    output_dir = law.Parameter(default = '', description="Path to the output directory")
    variable = law.Parameter(default="", description="Variable to be used")
    year = law.Parameter(default='2022', description="Year")

    batch_flavor = law.Parameter(default="htcondor", description="Batch system to use")

    # def requires(self):
    def workflow_requires(self):
        workflow_reqs = super().workflow_requires()

        tasks = {}

        if workflow_reqs:
            tasks.update(workflow_reqs)
        
        if self.variable == '':
            print("Running AsimovCovCorrHesse for inclusive does not make sense. Please specify a variable.")
            exit(1)
        else:
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_{self.variable}.yml")
        
        #Load central config file
        with open(configYamlPath, 'r') as file:
            config = yaml.safe_load(file)
        
        hesseConfig = config["combine_hesse"]
        
        if self.output_dir == '':
            output_dir = config['outputFolder']
        else:
            output_dir = self.output_dir
        
        tasks["RunT2WS"] = RunText2Workspace(output_dir=output_dir, variable=self.variable, year=self.year, batch_flavor=self.batch_flavor, workflow=hesseConfig["execution"], version=self.variable, slurm_partition=hesseConfig['batchPartition'], slurm_memory=hesseConfig['batchMemory'], slurm_max_runtime=hesseConfig['batchMaxRuntime'], htcondor_partition=hesseConfig['batchPartition'], htcondor_memory=hesseConfig['batchMemory'], htcondor_max_runtime=hesseConfig['batchMaxRuntime'])
        
        return tasks

    def create_branch_map(self):
        branch_map = {i: current_branch for i, current_branch in enumerate([0])}
        return branch_map

    def output(self):        
        if self.variable == '':
            print("Running AsimovCovCorrHesse for inclusive does not make sense. Please specify a variable.")
            exit(1)
        else:
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_{self.variable}.yml")
        
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
            
        if self.variable == "":
            output = []
        else:
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
            print("Running AsimovCovCorrHesse for inclusive does not make sense. Please specify a variable.")
            exit(1)
            
        else:
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_{self.variable}.yml")
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
        
        cwd = os.getcwd()
        
        if self.batch_flavor == "slurm/psi":
            # Have to use /scratch/batch_username/ for slurm/psi
            if "/work" in output_dir:
                execute_command([f'mkdir -p {output_dir}/Combine/{fitFolderName}/hesse'], shell=True)
            else:   
                execute_command([f'xrdfs root://t3dcachedb.psi.ch:1094/ mkdir -p {output_dir}/Combine/{fitFolderName}/hesse'], shell=True)

            os.environ["TARGET_PATH"] = f"/scratch/{os.environ['USER']}/{os.environ['SLURM_JOB_ID']}"
            execute_command([f'mkdir -p $TARGET_PATH/Combine/{fitFolderName}/hesse'], shell=True)
            os.chdir(os.path.join(os.environ["TARGET_PATH"], 'Combine', fitFolderName, 'hesse'))
        else:
            execute_command([f'mkdir -p {output_dir}/Combine/{fitFolderName}/hesse'], shell=True)
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
            "--saveSpecifiedIndex", f"""{",".join(combineVariableDict[f'{self.year}'][f'{self.variable}']['pdfIndeces'])}""",
            "--floatOtherPOIs", "1",
            "--robustHesse", "1",
            "--robustHesseSave", "1",
            "--cminDefaultMinimizerStrategy=0",
            "--X-rtd", "MINIMIZER_freezeDisassociatedParams",
            "--X-rtd", "MINIMIZER_multiMin_hideConstants",
            "--X-rtd", "MINIMIZER_multiMin_maskConstraints",
            "--X-rtd", "MINIMIZER_multiMin_maskChannels=2",
            "--X-rtd", "MINIMIZER_skipDiscreteIterations", # According to Mauro: Try without profiling
            "-t", "-1",
            "--setParameters", f"""{",".join(combineVariableDict[f'{self.year}'][f'{self.variable}']['paramStr'])}"""
        ]
        command = arguments
        # print(command)
        try:
            result = subprocess.run(command, check=True, text=True, capture_output=True)
            print("Script output:", result.stdout)
            print("Script executed successfully.")
        except subprocess.CalledProcessError as e:
            print("Error executing script:", e.stderr)

        # Copy the files back to pnfs if we are on slurm/psi
        if self.batch_flavor == "slurm/psi":
            # Have to copy over the output to the final directory
            # Don't forget to VOMS!
            if "/work" in output_dir:
                slurm_copy_command = [
                    'cp', '-rf',
                    f"{os.environ['TARGET_PATH']}/Combine/",
                    output_dir
                ]
            else:
                slurm_copy_command = [
                    'xrdcp', '-rf',
                    f"{os.environ['TARGET_PATH']}/Combine/",
                    'root://t3dcachedb.psi.ch:1094//'+output_dir
                ]
            print(slurm_copy_command)
            execute_command(slurm_copy_command)
            # Clean up the temporary directory
            shutil.rmtree(os.environ["TARGET_PATH"])
            
        os.chdir(cwd)
        
class AsimovCovCorr(Task, SlurmWorkflow, HTCondorWorkflow, law.LocalWorkflow): #(law.Task): #(Task, HTCondorWorkflow, law.LocalWorkflow):
    output_dir = law.Parameter(default = '', description="Path to the output directory")
    variable = law.Parameter(default="", description="Variable to be used")
    year = law.Parameter(default='2022', description="Year")
    noPreliminary = law.Parameter(default=False, description="Flag, if final plot should bear the Preliminary.")

    batch_flavor = law.Parameter(default="htcondor", description="Batch system to use")


    # def requires(self):
    def workflow_requires(self):
        workflow_reqs = super().workflow_requires()

        tasks = {}

        if workflow_reqs:
            tasks.update(workflow_reqs)
        
        if self.variable == '':
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_inclusive.yml")
        else:
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_{self.variable}.yml")
        
        #Load central config file
        with open(configYamlPath, 'r') as file:
            config = yaml.safe_load(file)
        
        if self.output_dir == '':
            output_dir = config['outputFolder']
        else:
            output_dir = self.output_dir
        
        if self.variable == '':
            print("Running AsimovCovCorr for inclusive does not make sense. Please specify a variable.")
            exit(1)
        else:
            version = self.variable
            tasks["AsimovCovCorrHesse"] = AsimovCovCorrHesse(output_dir=output_dir, variable=self.variable, year=self.year, version=version, workflow=config["combine_hesse"]["execution"], batch_flavor=self.batch_flavor, slurm_partition=config["combine_hesse"]['batchPartition'], slurm_memory=config["combine_hesse"]['batchMemory'], slurm_max_runtime=config["combine_hesse"]['batchMaxRuntime'], htcondor_partition=config["combine_hesse"]['batchPartition'], htcondor_memory=config["combine_hesse"]['batchMemory'], htcondor_max_runtime=config["combine_hesse"]['batchMaxRuntime'])
        
        return tasks

    def create_branch_map(self):
        branch_map = {i: current_branch for i, current_branch in enumerate([0])}
        return branch_map

    def output(self):        
        if self.variable == '':
            print("Running AsimovCovCorr for inclusive does not make sense. Please specify a variable.")
            exit(1)
        else:
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_{self.variable}.yml")
        
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
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_{self.variable}.yml")
            fitFolderName = f'runFits_{self.variable}'
                  
        #Load central config file
        with open(configYamlPath, 'r') as file:
            config = yaml.safe_load(file)
        
        if self.output_dir == '':
            output_dir = config['outputFolder']
        else:
            output_dir = self.output_dir  
            
        # if self.variable == '':
        #     datacard_path = os.path.join(output_dir, 'Combine', f'Datacard_{self.year}.root')
        # else:
        #     datacard_path = os.path.join(output_dir, 'Combine', f'Datacard_{self.variable}_{self.year}.root')
        
        if self.batch_flavor == "slurm/psi":
            # Have to use /scratch/batch_username/ for slurm/psi
            if "/work" in output_dir:
                execute_command([f'mkdir -p {output_dir}/Combine/{fitFolderName}/hesse/Plots'], shell=True)
            else:   
                execute_command([f'xrdfs root://t3dcachedb.psi.ch:1094/ mkdir -p {output_dir}/Combine/{fitFolderName}/hesse/Plots'], shell=True)

            os.environ["TARGET_PATH"] = f"/scratch/{os.environ['USER']}/{os.environ['SLURM_JOB_ID']}"
            execute_command([f'mkdir -p $TARGET_PATH/Combine/{fitFolderName}/hesse/Plots'], shell=True)

            if "/work" in output_dir:
                slurm_copy_command = [
                    'cp', '-rf',
                    f'{output_dir}/Combine/{fitFolderName}/hesse',
                    f'{os.environ["TARGET_PATH"]}/Combine/{fitFolderName}/'
                ]
            else:
                slurm_copy_command = [
                    'xrdcp', '-rf',
                    'root://t3dcachedb.psi.ch:1094//'+ f'{output_dir}/Combine/{fitFolderName}/hesse',
                    f'{os.environ["TARGET_PATH"]}/Combine/{fitFolderName}/'
                ]
            execute_command(slurm_copy_command)
            temp_output_dir = os.environ["TARGET_PATH"]
            # output_dir = os.path.join(os.environ["TARGET_PATH"], 'Combine', fitFolderName, 'hesse', 'Plots')
        else:
            execute_command([f'mkdir -p {output_dir}/Combine/{fitFolderName}/hesse/Plots'], shell=True)
            temp_output_dir = output_dir
            # output_dir = os.path.join(output_dir, 'Combine', fitFolderName, 'hesse', 'Plots')            
        
        cwd = os.getcwd()
        os.chdir(os.path.join(os.environ["ANALYSIS_PATH"], 'Plots'))

        arguments = [
            "python3",
            f"{os.path.join(os.environ['ANALYSIS_PATH'], 'Plots', 'makeCorrMatrix.py')}",
            "--inputJson", f"{os.path.join(os.environ['ANALYSIS_PATH'], 'Plots', 'inputs_robustHesse.json')}",
            "--mode", f"{self.variable}",
            "--input", f"{os.path.join(output_dir, 'Combine', fitFolderName, 'hesse', f'robustHessefirstStep.root')}",
            "--output", f"{os.path.join(temp_output_dir, 'Combine', fitFolderName, 'hesse', 'Plots')}",
            "--translate", f"{os.path.join(os.environ['ANALYSIS_PATH'], 'Plots', 'poi_differential_hesse_noLabels.json')}"
        ]
        if convert_boolean_string(self.noPreliminary):
            arguments.append("--noPreliminary")
        command = arguments
        print(command)
        try:
            result = subprocess.run(command, check=True, text=True, capture_output=True)
            print("Script output:", result.stdout)
            print("Script executed successfully.")
        except subprocess.CalledProcessError as e:
            print("Error executing script:", e.stderr)
            
        arguments = [
            "python3",
            f"{os.path.join(os.environ['ANALYSIS_PATH'], 'Plots', 'makeCorrMatrix.py')}",
            "--inputJson", f"{os.path.join(os.environ['ANALYSIS_PATH'], 'Plots', 'inputs_robustHesse.json')}",
            "--mode", f"{self.variable}",
            "--input", f"{os.path.join(output_dir, 'Combine', fitFolderName, 'hesse', f'robustHessefirstStep.root')}",
            "--output", f"{os.path.join(temp_output_dir, 'Combine', fitFolderName, 'hesse', 'Plots')}",
            "--translate", f"{os.path.join(os.environ['ANALYSIS_PATH'], 'Plots', 'poi_differential_hesse_noLabels.json')}",
            "--doCov"
        ]
        if convert_boolean_string(self.noPreliminary):
            arguments.append("--noPreliminary")
        command = arguments
        print(command)
        try:
            result = subprocess.run(command, check=True, text=True, capture_output=True)
            print("Script output:", result.stdout)
            print("Script executed successfully.")
        except subprocess.CalledProcessError as e:
            print("Error executing script:", e.stderr)
        
        # Copy the files back to pnfs if we are on slurm/psi
        if self.batch_flavor == "slurm/psi":
            # Have to copy over the output to the final directory
            # Don't forget to VOMS!
            if "/work" in output_dir:
                slurm_copy_command = [
                    'cp', '-rf',
                    f"{os.environ['TARGET_PATH']}/Combine/",
                    output_dir
                ]
            else:
                slurm_copy_command = [
                    'xrdcp', '-rf',
                    f"{os.environ['TARGET_PATH']}/Combine/",
                    'root://t3dcachedb.psi.ch:1094//'+output_dir
                ]
            print(slurm_copy_command)
            execute_command(slurm_copy_command)
            # Clean up the temporary directory
            shutil.rmtree(os.environ["TARGET_PATH"])
            
        os.chdir(cwd)

class UnblindedFitSystSingle(Task, SlurmWorkflow, HTCondorWorkflow, law.LocalWorkflow): #(law.Task): #(Task, HTCondorWorkflow, law.LocalWorkflow):
    output_dir = law.Parameter(default = '', description="Path to the output directory")
    variable = law.Parameter(default="", description="Variable to be used")
    year = law.Parameter(default='2022', description="Year")

    batch_flavor = law.Parameter(default="htcondor", description="Batch system to use")

    # def requires(self):
    def workflow_requires(self):
        workflow_reqs = super().workflow_requires()

        tasks = {}

        if workflow_reqs:
            tasks.update(workflow_reqs)
        
        if self.variable == '':
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_inclusive.yml")
        else:
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_{self.variable}.yml")
        
        #Load central config file
        with open(configYamlPath, 'r') as file:
            config = yaml.safe_load(file)
        
        if self.output_dir == '':
            output_dir = config['outputFolder']
        else:
            output_dir = self.output_dir
               
        tasks["RunT2WS"] = RunText2Workspace(output_dir=output_dir, variable=self.variable, year=self.year, version=self.variable if self.variable != "" else "inclusive", batch_flavor=self.batch_flavor, slurm_partition=config["combine_fit"]['batchPartition'], slurm_memory=config["combine_fit"]['batchMemory'], slurm_max_runtime=config["combine_fit"]['batchMaxRuntime'], htcondor_partition=config["combine_fit"]['batchPartition'], htcondor_memory=config["combine_fit"]['batchMemory'], htcondor_max_runtime=config["combine_fit"]['batchMaxRuntime'])
        
        return tasks
    
    def create_branch_map(self):
        if self.variable == '':
            param_list = ["r"]
        else:
            param_list = combineVariableDict[f'{self.year}'][f'{self.variable}']['paramStrNoOne']
        branch_map = {i: current_cat for i, current_cat in enumerate(param_list)}
        return branch_map

    def output(self):
        current_cat = self.branch_data
        
        if self.variable == '':
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_inclusive.yml")
        else:
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_{self.variable}.yml")
        
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
        
        output = [os.path.join(output_dir, 'Combine', fitFolderName, 'dataFit')]
        output += [os.path.join(output_dir, 'Combine', fitFolderName, 'dataFit', f'higgsCombineDataPostFitBestFit_{current_cat}.MultiDimFit.mH125.38.root')]
        
        outputFileTargets = []
                
        for _, current_output_path in enumerate(output):
            outputFileTargets.append(law.LocalFileTarget(current_output_path))
            
        # print("AsimovFitCategorySyst", outputFileTargets)

        return outputFileTargets

    def run(self):
        current_cat = self.branch_data
        
        if self.variable == '':
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_inclusive.yml")
            fitFolderName = f'runFits_mu_fiducial'
            
        else:
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_{self.variable}.yml")
            fitFolderName = f'runFits_{self.variable}'
                    
        #Load central config file
        with open(configYamlPath, 'r') as file:
            config = yaml.safe_load(file)
        
        if self.output_dir == '':
            output_dir = config['outputFolder']
        else:
            output_dir = self.output_dir
        
        
        cwd = os.getcwd()
        
        if self.variable == '':
            datacard_path = os.path.join(output_dir, 'Combine', f'Datacard_{self.year}.root')
        else:
            datacard_path = os.path.join(output_dir, 'Combine', f'Datacard_{self.variable}_{self.year}.root')
        if self.batch_flavor == "slurm/psi":
            # Have to use /scratch/batch_username/ for slurm/psi
            os.environ["TARGET_PATH"] = f"/scratch/{os.environ['USER']}/{os.environ['SLURM_JOB_ID']}"
            execute_command([f'mkdir -p $TARGET_PATH/Combine/{fitFolderName}/dataFit'], shell=True)
            os.chdir(os.path.join(os.environ["TARGET_PATH"], 'Combine', fitFolderName, 'dataFit'))
        else:
            os.chdir(os.path.join(output_dir, 'Combine', fitFolderName, 'dataFit'))

        if self.variable == '':
            arguments = [
                "combine",
                "-M", "MultiDimFit",
                "-d", datacard_path,
                "--freezeParameters", "MH",
                "-m", "125.38",
                "-n", f"DataPostFitBestFit_{current_cat}",
                "--cminDefaultMinimizerStrategy=0",
                "--algo", "singles",
                "--X-rtd", "MINIMIZER_freezeDisassociatedParams",
                "--X-rtd", "MINIMIZER_multiMin_hideConstants",
                "--X-rtd", "MINIMIZER_multiMin_maskConstraints",
                "--X-rtd", "MINIMIZER_multiMin_maskChannels=2",
                "-P", "r",
                "--floatOtherPOIs", "1",
                "--saveWorkspace",
                "--saveFitResult",
                "--cminApproxPreFitTolerance", f"{config['combine_fit']['cminApproxPreFitTolerance']}",
                "--rMin", f"{config['combine_fit']['rMin']}",
                "--rMax", f"{config['combine_fit']['rMax']}"
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
                datacard_path,
                "--freezeParameters", "MH",
                "-m", "125.38",
                "-n", f"DataPostFitBestFit_{current_cat}",
                "--cminDefaultMinimizerStrategy=0",
                "--algo", "singles",
                "--X-rtd", "MINIMIZER_freezeDisassociatedParams",
                "--X-rtd", "MINIMIZER_multiMin_hideConstants",
                "--X-rtd", "MINIMIZER_multiMin_maskConstraints",
                "--X-rtd", "MINIMIZER_multiMin_maskChannels=2",
                "-P", f"{current_cat}",
                "--cminApproxPreFitTolerance", f"{config['combine_fit']['cminApproxPreFitTolerance']}",
                # "--stepSize", "0.05", 
                # "--setCrossingTolerance", "0.00005",
                "--saveFitResult",
                "--floatOtherPOIs", "1",
                "--saveWorkspace",
                "--saveSpecifiedIndex", f"""{",".join(combineVariableDict[f'{self.year}'][f'{self.variable}']['pdfIndeces'])}""",
            ]
            command = arguments
            # print(command)
            try:
                result = subprocess.run(command, check=True, text=True, capture_output=True)
                print("Script output:", result.stdout)
                print("Script executed successfully.")
            except subprocess.CalledProcessError as e:
                print("Error executing script:", e.stderr)

        # Copy the files back to pnfs if we are on slurm/psi
        if self.batch_flavor == "slurm/psi":
            # Have to copy over the output to the final directory
            # Don't forget to VOMS!
            slurm_copy_command = [
                'xrdcp', '-rf',
                f"{os.environ['TARGET_PATH']}/Combine/",
                'root://t3dcachedb.psi.ch:1094//'+output_dir
            ]
            print(slurm_copy_command)
            execute_command(slurm_copy_command)
            # Clean up the temporary directory
            shutil.rmtree(os.environ["TARGET_PATH"])

        os.chdir(cwd)

class UnblindedFitStatSingle(Task,SlurmWorkflow, HTCondorWorkflow, law.LocalWorkflow): #(law.Task): #(Task, HTCondorWorkflow, law.LocalWorkflow):
    output_dir = law.Parameter(default = '', description="Path to the output directory")
    variable = law.Parameter(default="", description="Variable to be used")
    year = law.Parameter(default='2022', description="Year")
    
    batch_flavor = law.Parameter(default="htcondor", description="Batch system to use")

    # def requires(self):
    def workflow_requires(self):
        workflow_reqs = super().workflow_requires()

        tasks = {}

        if workflow_reqs:
            tasks.update(workflow_reqs)
        
        if self.variable == '':
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_inclusive.yml")
        else:
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_{self.variable}.yml")
        
        #Load central config file
        with open(configYamlPath, 'r') as file:
            config = yaml.safe_load(file)
        
        if self.output_dir == '':
            output_dir = config['outputFolder']
        else:
            output_dir = self.output_dir
        
        fitConfig = config["combine_fit"]        
        
        if self.variable == '':
            tasks["RunT2WS"] = RunText2Workspace(output_dir=output_dir, variable=self.variable, year=self.year, batch_flavor=self.batch_flavor, version="inclusive", workflow=fitConfig['execution'], slurm_partition=fitConfig['batchPartition'], slurm_memory=fitConfig['batchMemory'], slurm_max_runtime=fitConfig['batchMaxRuntime'], htcondor_partition=fitConfig['batchPartition'], htcondor_memory=fitConfig['batchMemory'], htcondor_max_runtime=fitConfig['batchMaxRuntime'])
        else:
            tasks["UnblindedFitSystSingle"] = UnblindedFitSystSingle(output_dir=output_dir, variable=self.variable, year=self.year, batch_flavor=self.batch_flavor, version=f'{self.variable}', workflow=fitConfig['execution'], slurm_partition=fitConfig['batchPartition'], slurm_memory=fitConfig['batchMemory'], slurm_max_runtime=fitConfig['batchMaxRuntime'], htcondor_partition=fitConfig['batchPartition'], htcondor_memory=fitConfig['batchMemory'], htcondor_max_runtime=fitConfig['batchMaxRuntime'])
        
        return tasks
    
    def create_branch_map(self):
        if self.variable == '':
            param_list = ["r"]
        else:
            param_list = combineVariableDict[f'{self.year}'][f'{self.variable}']['paramStrNoOne']
        branch_map = {i: current_cat for i, current_cat in enumerate(param_list)}
        return branch_map

    def output(self):
        cat = self.branch_data
        
        if self.variable == '':
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_inclusive.yml")
        else:
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_{self.variable}.yml")
        
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

        output = [os.path.join(output_dir, 'Combine', fitFolderName, 'dataFit', f'higgsCombineDataPostFitBestFitStat_{cat}.MultiDimFit.mH125.38.root')]
        
        outputFileTargets = []
                
        for _, current_output_path in enumerate(output):
            outputFileTargets.append(law.LocalFileTarget(current_output_path))
                    
        return outputFileTargets

    def run(self):
        cat = self.branch_data

        if self.variable == '':
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_inclusive.yml")
            fitFolderName = f'runFits_mu_fiducial'
            
        else:
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_{self.variable}.yml")
            fitFolderName = f'runFits_{self.variable}'
                    
        #Load central config file
        with open(configYamlPath, 'r') as file:
            config = yaml.safe_load(file)
        
        if self.output_dir == '':
            output_dir = config['outputFolder']
        else:
            output_dir = self.output_dir  

        cwd = os.getcwd()
        if self.batch_flavor == "slurm/psi":
            # Have to use /scratch/batch_username/ for slurm/psi
            if "/work" in output_dir:
                execute_command([f'mkdir -p {output_dir}/Combine/{fitFolderName}/dataFit'], shell=True)
            else:   
                execute_command([f'xrdfs root://t3dcachedb.psi.ch:1094/ mkdir -p {output_dir}/Combine/{fitFolderName}/dataFit'], shell=True)

            os.environ["TARGET_PATH"] = f"/scratch/{os.environ['USER']}/{os.environ['SLURM_JOB_ID']}"
            execute_command([f'mkdir -p $TARGET_PATH/Combine/{fitFolderName}/dataFit'], shell=True)
            os.chdir(os.path.join(os.environ["TARGET_PATH"], 'Combine', fitFolderName, 'dataFit'))
        else:
            execute_command([f'mkdir -p {output_dir}/Combine/{fitFolderName}/dataFit'], shell=True)
            os.chdir(os.path.join(output_dir, 'Combine', fitFolderName, 'dataFit'))
    
        firstStepPath = os.path.join(output_dir, 'Combine', fitFolderName, 'dataFit', f"higgsCombineDataPostFitBestFit_{cat}.MultiDimFit.mH125.38.root")
                
        if self.variable == '':
            arguments = [
                "combine",
                "-M", "MultiDimFit",
                firstStepPath,
                "--freezeParameters", "allConstrainedNuisances,MH",
                "-m", "125.38",
                "-n", f"DataPostFitBestFitStat_{cat}",
                "--cminDefaultMinimizerStrategy=0",
                "--algo", "singles",
                "--rMin", f"{config['combine_fit']['rMin']}",
                "--rMax", f"{config['combine_fit']['rMax']}",
                "--X-rtd", "MINIMIZER_freezeDisassociatedParams",
                "--X-rtd", "MINIMIZER_multiMin_hideConstants",
                "--X-rtd", "MINIMIZER_multiMin_maskConstraints",
                "--X-rtd", "MINIMIZER_multiMin_maskChannels=2",
                "-P", f"{cat}",
                "--floatOtherPOIs", "1",
                "--saveFitResult",
                "--snapshotName", "MultiDimFit",
                "-w", "w",
                "--cminApproxPreFitTolerance", f"{config['combine_fit']['cminApproxPreFitTolerance']}"
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
                "-n", f"DataPostFitBestFitStat_{cat}",
                "--cminDefaultMinimizerStrategy=0",
                "--algo", "singles",
                "--X-rtd", "MINIMIZER_freezeDisassociatedParams",
                "--X-rtd", "MINIMIZER_multiMin_hideConstants",
                "--X-rtd", "MINIMIZER_multiMin_maskConstraints",
                "--X-rtd", "MINIMIZER_multiMin_maskChannels=2",
                "-P", f"{cat}",
                "--saveFitResult",
                "--floatOtherPOIs", "1",
                "--snapshotName", "MultiDimFit",
                "-w", "w",
            ]
            command = arguments
            # print(command)
            try:
                result = subprocess.run(command, check=True, text=True, capture_output=True)
                print("Script output:", result.stdout)
                print("Script executed successfully.")
            except subprocess.CalledProcessError as e:
                print("Error executing script:", e.stderr)
            
        # Copy the files back to pnfs if we are on slurm/psi
        if self.batch_flavor == "slurm/psi":
            # Have to copy over the output to the final directory
            # Don't forget to VOMS!
            if "/work" in output_dir:
                slurm_copy_command = [
                    'cp', '-rf',
                    f"{os.environ['TARGET_PATH']}/Combine/",
                    output_dir
                ]
            else:
                slurm_copy_command = [
                    'xrdcp', '-rf',
                    f"{os.environ['TARGET_PATH']}/Combine/",
                    'root://t3dcachedb.psi.ch:1094//'+output_dir
                ]
            print(slurm_copy_command)
            execute_command(slurm_copy_command)
            # Clean up the temporary directory
            shutil.rmtree(os.environ["TARGET_PATH"])
                
        
        os.chdir(cwd)
        
class UnblindedFitCategorySyst(Task, HTCondorWorkflow, SlurmWorkflow, law.LocalWorkflow): #(law.Task): #(Task, HTCondorWorkflow, law.LocalWorkflow):
    output_dir = law.Parameter(default = '', description="Path to the output directory")
    variable = law.Parameter(default="", description="Variable to be used")
    year = law.Parameter(default='2022', description="Year")
    nPoints = law.Parameter(default=30, description="Number of points for the LL scan")
    
    batch_flavor = law.Parameter(default="htcondor", description="Batch system to use")

    # def requires(self):
    def workflow_requires(self):
        workflow_reqs = super().workflow_requires()

        tasks = {}

        if workflow_reqs:
            tasks.update(workflow_reqs)
        
        if self.variable == '':
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_inclusive.yml")
        else:
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_{self.variable}.yml")
        
        #Load central config file
        with open(configYamlPath, 'r') as file:
            config = yaml.safe_load(file)
        
        if self.output_dir == '':
            output_dir = config['outputFolder']
        else:
            output_dir = self.output_dir
               
        tasks["RunT2WS"] = RunText2Workspace(output_dir=output_dir, variable=self.variable, year=self.year, batch_flavor=self.batch_flavor, workflow=config["combine_fit"]["execution"], version=self.variable if self.variable != "" else "inclusive", slurm_partition=config["combine_fit"]['batchPartition'], slurm_memory=config["combine_fit"]['batchMemory'], slurm_max_runtime=config["combine_fit"]['batchMaxRuntime'], htcondor_partition=config["combine_fit"]['batchPartition'], htcondor_memory=config["combine_fit"]['batchMemory'], htcondor_max_runtime=config["combine_fit"]['batchMaxRuntime'])
        
        return tasks
    
    def create_branch_map(self):
        if self.variable == '':
            param_list = ["r"]
        else:
            param_list = combineVariableDict[f'{self.year}'][f'{self.variable}']['paramStrNoOne']
        branch_map = {i: current_cat for i, current_cat in enumerate(param_list)}
        return branch_map

    def output(self):
        current_cat = self.branch_data
        
        if self.variable == '':
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_inclusive.yml")
        else:
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_{self.variable}.yml")
        
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
        
        output = [os.path.join(output_dir, 'Combine', fitFolderName, 'dataFit')]
        output += [os.path.join(output_dir, 'Combine', fitFolderName, 'dataFit', f'higgsCombineDataPostFitScanFit_{current_cat}.MultiDimFit.mH125.38.root')]
        
        outputFileTargets = []
                
        for _, current_output_path in enumerate(output):
            outputFileTargets.append(law.LocalFileTarget(current_output_path))
            
        # print("AsimovFitCategorySyst", outputFileTargets)

        return outputFileTargets

    def run(self):
        current_cat = self.branch_data
        
        if self.variable == '':
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_inclusive.yml")
            fitFolderName = f'runFits_mu_fiducial'
            
        else:
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_{self.variable}.yml")
            fitFolderName = f'runFits_{self.variable}'
                    
        #Load central config file
        with open(configYamlPath, 'r') as file:
            config = yaml.safe_load(file)
        
        if self.output_dir == '':
            output_dir = config['outputFolder']
        else:
            output_dir = self.output_dir  
        
        cwd = os.getcwd()
        if self.batch_flavor == "slurm/psi":
            # Have to use /scratch/batch_username/ for slurm/psi
            if "/work" in output_dir:
                execute_command([f'mkdir -p {output_dir}/Combine/{fitFolderName}/dataFit'], shell=True)
            else:   
                execute_command([f'xrdfs root://t3dcachedb.psi.ch:1094/ mkdir -p {output_dir}/Combine/{fitFolderName}/dataFit'], shell=True)

            os.environ["TARGET_PATH"] = f"/scratch/{os.environ['USER']}/{os.environ['SLURM_JOB_ID']}"
            execute_command([f'mkdir -p $TARGET_PATH/Combine/{fitFolderName}/dataFit'], shell=True)
            os.chdir(os.path.join(os.environ["TARGET_PATH"], 'Combine', fitFolderName, 'dataFit'))
        else:
            execute_command([f'mkdir -p {output_dir}/Combine/{fitFolderName}/dataFit'], shell=True)
            os.chdir(os.path.join(output_dir, 'Combine', fitFolderName, 'dataFit'))
        
        if self.variable == '':
            datacard_path = os.path.join(output_dir, 'Combine', f'Datacard_{self.year}.root')
        else:
            datacard_path = os.path.join(output_dir, 'Combine', f'Datacard_{self.variable}_{self.year}.root')
            
        if self.variable == '':
            arguments = [
                "combine",
                "-M", "MultiDimFit",
                "-d", datacard_path,
                "--freezeParameters", "MH",
                "-m", "125.38",
                "-n", f"DataPostFitScanFit_{current_cat}",
                "--cminDefaultMinimizerStrategy=0",
                "--algo", "grid",
                "--points", f"{int(self.nPoints)}",
                "--X-rtd", "MINIMIZER_freezeDisassociatedParams",
                "--X-rtd", "MINIMIZER_multiMin_hideConstants",
                "--X-rtd", "MINIMIZER_multiMin_maskConstraints",
                "--X-rtd", "MINIMIZER_multiMin_maskChannels=2",
                "-P", "r",
                "--floatOtherPOIs", "1",
                "--saveWorkspace",
                "--saveFitResult",
                "--cminApproxPreFitTolerance", f"{config['combine_fit']['cminApproxPreFitTolerance']}",
                "--rMin", f"{config['combine_fit']['rMin']}",
                "--rMax", f"{config['combine_fit']['rMax']}"
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
                datacard_path,
                "--freezeParameters", "MH",
                "-m", "125.38",
                "-n", f"DataPostFitScanFit_{current_cat}",
                "--cminDefaultMinimizerStrategy=0",
                "--algo", "grid",
                "--points", f"{int(self.nPoints)}",
                "--X-rtd", "MINIMIZER_freezeDisassociatedParams",
                "--X-rtd", "MINIMIZER_multiMin_hideConstants",
                "--X-rtd", "MINIMIZER_multiMin_maskConstraints",
                "--X-rtd", "MINIMIZER_multiMin_maskChannels=2",
                "-P", f"{current_cat}",
                "--saveFitResult",
                "--floatOtherPOIs", "1",
                "--saveWorkspace",
                "--saveSpecifiedIndex", f"""{",".join(combineVariableDict[f'{self.year}'][f'{self.variable}']['pdfIndeces'])}""",
            ]
            command = arguments
            # print(command)
            try:
                result = subprocess.run(command, check=True, text=True, capture_output=True)
                print("Script output:", result.stdout)
                print("Script executed successfully.")
            except subprocess.CalledProcessError as e:
                print("Error executing script:", e.stderr)
        
        # Copy the files back to pnfs if we are on slurm/psi
        if self.batch_flavor == "slurm/psi":
            # Have to copy over the output to the final directory
            # Don't forget to VOMS!
            if "/work" in output_dir:
                slurm_copy_command = [
                    'cp', '-rf',
                    f"{os.environ['TARGET_PATH']}/Combine/",
                    output_dir
                ]
            else:
                slurm_copy_command = [
                    'xrdcp', '-rf',
                    f"{os.environ['TARGET_PATH']}/Combine/",
                    'root://t3dcachedb.psi.ch:1094//'+output_dir
                ]
            print(slurm_copy_command)
            execute_command(slurm_copy_command)
            # Clean up the temporary directory
            shutil.rmtree(os.environ["TARGET_PATH"])
            
        os.chdir(cwd)
        
class UnblindedFitCategoryStat(Task, HTCondorWorkflow, SlurmWorkflow, law.LocalWorkflow): #(law.Task): #(Task, HTCondorWorkflow, law.LocalWorkflow):
    output_dir = law.Parameter(default = '', description="Path to the output directory")
    variable = law.Parameter(default="", description="Variable to be used")
    year = law.Parameter(default='2022', description="Year")
    nPoints = law.Parameter(default=30, description="Number of points for the LL scan")
    
    batch_flavor = law.Parameter(default="htcondor", description="Batch system to use")

    # def requires(self):
    def workflow_requires(self):
        workflow_reqs = super().workflow_requires()

        tasks = {}

        if workflow_reqs:
            tasks.update(workflow_reqs)
        
        if self.variable == '':
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_inclusive.yml")
        else:
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_{self.variable}.yml")
        
        #Load central config file
        with open(configYamlPath, 'r') as file:
            config = yaml.safe_load(file)
        
        if self.output_dir == '':
            output_dir = config['outputFolder']
        else:
            output_dir = self.output_dir
        
        fitConfig = config["combine_fit"]
                
        if self.variable == '':
            tasks["RunT2WS"] = RunText2Workspace(output_dir=output_dir, variable=self.variable, year=self.year, batch_flavor=self.batch_flavor, version='inclusive', workflow=fitConfig["execution"], slurm_partition=fitConfig['batchPartition'], slurm_memory=fitConfig['batchMemory'], slurm_max_runtime=fitConfig['batchMaxRuntime'], htcondor_partition=fitConfig['batchPartition'], htcondor_memory=fitConfig['batchMemory'], htcondor_max_runtime=fitConfig['batchMaxRuntime'])
        else:
            tasks["UnblindedFitCategorySyst"] = UnblindedFitCategorySyst(output_dir=output_dir, variable=self.variable, year=self.year, nPoints=self.nPoints, batch_flavor=self.batch_flavor, version=f'{self.variable}', workflow=fitConfig["execution"], slurm_partition=fitConfig['batchPartition'], slurm_memory=fitConfig['batchMemory'], slurm_max_runtime=fitConfig['batchMaxRuntime'], htcondor_partition=fitConfig['batchPartition'], htcondor_memory=fitConfig['batchMemory'], htcondor_max_runtime=fitConfig['batchMaxRuntime'])
        
        return tasks
    
    def create_branch_map(self):
        if self.variable == '':
            param_list = ["r"]
        else:
            param_list = combineVariableDict[f'{self.year}'][f'{self.variable}']['paramStrNoOne']
        branch_map = {i: current_cat for i, current_cat in enumerate(param_list)}
        return branch_map

    def output(self):
        cat = self.branch_data
        
        if self.variable == '':
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_inclusive.yml")
        else:
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_{self.variable}.yml")
        
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
        output = [os.path.join(output_dir, 'Combine', fitFolderName, 'dataFit', f'higgsCombineDataPostFitScanStat_{cat}.MultiDimFit.mH125.38.root')]
        
        outputFileTargets = []
                
        for _, current_output_path in enumerate(output):
            outputFileTargets.append(law.LocalFileTarget(current_output_path))

        return outputFileTargets

    def run(self):
        cat = self.branch_data

        if self.variable == '':
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_inclusive.yml")
            fitFolderName = f'runFits_mu_fiducial'
            
        else:
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_{self.variable}.yml")
            fitFolderName = f'runFits_{self.variable}'
                    
        #Load central config file
        with open(configYamlPath, 'r') as file:
            config = yaml.safe_load(file)
        
        if self.output_dir == '':
            output_dir = config['outputFolder']
        else:
            output_dir = self.output_dir  

        cwd = os.getcwd()
        if self.batch_flavor == "slurm/psi":
            # Have to use /scratch/batch_username/ for slurm/psi
            if "/work" in output_dir:
                execute_command([f'mkdir -p {output_dir}/Combine/{fitFolderName}/dataFit'], shell=True)
            else:   
                execute_command([f'xrdfs root://t3dcachedb.psi.ch:1094/ mkdir -p {output_dir}/Combine/{fitFolderName}/dataFit'], shell=True)

            os.environ["TARGET_PATH"] = f"/scratch/{os.environ['USER']}/{os.environ['SLURM_JOB_ID']}"
            execute_command([f'mkdir -p $TARGET_PATH/Combine/{fitFolderName}/dataFit'], shell=True)
            os.chdir(os.path.join(os.environ["TARGET_PATH"], 'Combine', fitFolderName, 'dataFit'))
        else:
            execute_command([f'mkdir -p {output_dir}/Combine/{fitFolderName}/dataFit'], shell=True)
            os.chdir(os.path.join(output_dir, 'Combine', fitFolderName, 'dataFit'))
    
        firstStepPath = os.path.join(output_dir, 'Combine', fitFolderName, 'dataFit', f"higgsCombineDataPostFitScanFit_{cat}.MultiDimFit.mH125.38.root")
                
        if self.variable == '':
            arguments = [
                "combine",
                "-M", "MultiDimFit",
                firstStepPath,
                "--freezeParameters", "allConstrainedNuisances,MH",
                "-m", "125.38",
                "-n", f"DataPostFitScanStat_{cat}",
                "--cminDefaultMinimizerStrategy=0",
                "--algo", "grid",
                "--rMin", f"{config['combine_fit']['rMin']}",
                "--rMax", f"{config['combine_fit']['rMax']}",
                "--points", f"{int(self.nPoints)}",
                "--X-rtd", "MINIMIZER_freezeDisassociatedParams",
                "--X-rtd", "MINIMIZER_multiMin_hideConstants",
                "--X-rtd", "MINIMIZER_multiMin_maskConstraints",
                "--X-rtd", "MINIMIZER_multiMin_maskChannels=2",
                "-P", f"{cat}",
                "--floatOtherPOIs", "1",
                "--saveFitResult",
                "--snapshotName", "MultiDimFit",
                "-w", "w",
                "--cminApproxPreFitTolerance", f"{config['combine_fit']['cminApproxPreFitTolerance']}"
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
                "-n", f"DataPostFitScanStat_{cat}",
                "--cminDefaultMinimizerStrategy=0",
                "--algo", "grid",
                "--points", f"{int(self.nPoints)}",
                "--X-rtd", "MINIMIZER_freezeDisassociatedParams",
                "--X-rtd", "MINIMIZER_multiMin_hideConstants",
                "--X-rtd", "MINIMIZER_multiMin_maskConstraints",
                "--X-rtd", "MINIMIZER_multiMin_maskChannels=2",
                "-P", f"{cat}",
                "--saveFitResult",
                "--floatOtherPOIs", "1",
                "--snapshotName", "MultiDimFit",
                "-w", "w",
            ]
            command = arguments
            # print(command)
            try:
                result = subprocess.run(command, check=True, text=True, capture_output=True)
                print("Script output:", result.stdout)
                print("Script executed successfully.")
            except subprocess.CalledProcessError as e:
                print("Error executing script:", e.stderr)
            
        # Copy the files back to pnfs if we are on slurm/psi
        if self.batch_flavor == "slurm/psi":
            # Have to copy over the output to the final directory
            # Don't forget to VOMS!
            if "/work" in output_dir:
                slurm_copy_command = [
                    'cp', '-rf',
                    f"{os.environ['TARGET_PATH']}/Combine/",
                    output_dir
                ]
            else:
                slurm_copy_command = [
                    'xrdcp', '-rf',
                    f"{os.environ['TARGET_PATH']}/Combine/",
                    'root://t3dcachedb.psi.ch:1094//'+output_dir
                ]
            print(slurm_copy_command)
            execute_command(slurm_copy_command)
            # Clean up the temporary directory
            shutil.rmtree(os.environ["TARGET_PATH"])
        
        os.chdir(cwd)
        
class CreateUnblindedFit(Task, SlurmWorkflow, HTCondorWorkflow, law.LocalWorkflow): #(law.Task): #(Task, HTCondorWorkflow, law.LocalWorkflow):
    output_dir = law.Parameter(default = '', description="Path to the output directory")
    variable = law.Parameter(default="", description="Variable to be used")
    year = law.Parameter(default='2022', description="Year")

    batch_flavor = law.Parameter(default="htcondor", description="Batch system to use")

    # def requires(self):
    def workflow_requires(self):
        workflow_reqs = super().workflow_requires()

        tasks = {}

        if workflow_reqs:
            tasks.update(workflow_reqs)
        
        if self.variable == '':
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_inclusive.yml")
        else:
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_{self.variable}.yml")
        
        #Load central config file
        with open(configYamlPath, 'r') as file:
            config = yaml.safe_load(file)
        
        if self.output_dir == '':
            output_dir = config['outputFolder']
        else:
            output_dir = self.output_dir

        fitConfig = config["combine_fit"]
            
        tasks["UnblindedFitCategorySyst"] = UnblindedFitCategorySyst(output_dir=output_dir, variable=self.variable, year=self.year, batch_flavor=self.batch_flavor, nPoints=fitConfig["unblindedFit_numPoints"], version=self.variable if self.variable != "" else "inclusive", workflow=fitConfig["execution"], slurm_partition=fitConfig['batchPartition'], slurm_memory=fitConfig['batchMemory'], slurm_max_runtime=fitConfig['batchMaxRuntime'], htcondor_partition=fitConfig['batchPartition'], htcondor_memory=fitConfig['batchMemory'], htcondor_max_runtime=fitConfig['batchMaxRuntime'])
        tasks["UnblindedFitCategoryStat"] = UnblindedFitCategoryStat(output_dir=output_dir, variable=self.variable, year=self.year, batch_flavor=self.batch_flavor, nPoints=fitConfig["unblindedFit_numPoints"], version=self.variable if self.variable != "" else "inclusive", workflow=fitConfig["execution"], slurm_partition=fitConfig['batchPartition'], slurm_memory=fitConfig['batchMemory'], slurm_max_runtime=fitConfig['batchMaxRuntime'], htcondor_partition=fitConfig['batchPartition'], htcondor_memory=fitConfig['batchMemory'], htcondor_max_runtime=fitConfig['batchMaxRuntime'])
        
        return tasks
    
    def create_branch_map(self):
        # map branch indexes to ascii numbers from 97 to 122 ("a" to "z")        
        branch_list = [0]
        
        branch_map = {i: branch for i, branch in enumerate(branch_list)}
        return branch_map

    def output(self):
        if self.variable == '':
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_inclusive.yml")
        else:
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_{self.variable}.yml")
        
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

        output += [os.path.join(output_dir, 'Combine', fitFolderName, 'dataFit', 'scans')]
        
        if self.variable == '':
            cat = "r"
            output += [os.path.join(output_dir, 'Combine', fitFolderName, 'dataFit', 'scans', f'scan_{cat}_observed.root')]
            output += [os.path.join(output_dir, 'Combine', fitFolderName, 'dataFit', 'scans', f'scan_{cat}_observed.pdf')]
            output += [os.path.join(output_dir, 'Combine', fitFolderName, 'dataFit', 'scans', f'scan_{cat}_observed.png')]
        else:
            for cat in combineVariableDict[f'{self.year}'][f'{self.variable}']['paramStrNoOne']:
                
                output += [os.path.join(output_dir, 'Combine', fitFolderName, 'dataFit', 'scans', f'scan_{cat}_observed.root')]
                output += [os.path.join(output_dir, 'Combine', fitFolderName, 'dataFit', 'scans', f'scan_{cat}_observed.pdf')]
                output += [os.path.join(output_dir, 'Combine', fitFolderName, 'dataFit', 'scans', f'scan_{cat}_observed.png')]

        outputFileTargets = []
                
        for _, current_output_path in enumerate(output):
            outputFileTargets.append(law.LocalFileTarget(current_output_path))
            
        return outputFileTargets

    def run(self):
        
        if self.variable == '':
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_inclusive.yml")
            fitFolderName = f'runFits_mu_fiducial'
        else:
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_{self.variable}.yml")
            fitFolderName = f'runFits_{self.variable}'
            
                    
        #Load central config file
        with open(configYamlPath, 'r') as file:
            config = yaml.safe_load(file)
        
        if self.output_dir == '':
            output_dir = config['outputFolder']
        else:
            output_dir = self.output_dir  

        cwd = os.getcwd()
        if self.batch_flavor == "slurm/psi":
            # Have to use /scratch/batch_username/ for slurm/psi
            if "/work" in output_dir:
                execute_command([f'mkdir -p {output_dir}/Combine/{fitFolderName}/dataFit/scans'], shell=True)
            else:   
                execute_command([f'xrdfs root://t3dcachedb.psi.ch:1094/ mkdir -p {output_dir}/Combine/{fitFolderName}/dataFit/scans'], shell=True)

            os.environ["TARGET_PATH"] = f"/scratch/{os.environ['USER']}/{os.environ['SLURM_JOB_ID']}"
            execute_command([f'mkdir -p $TARGET_PATH/Combine/{fitFolderName}/dataFit/scans'], shell=True)
            os.chdir(os.path.join(os.environ["TARGET_PATH"], 'Combine', fitFolderName, 'dataFit'))
        else:
            execute_command([f'mkdir -p {output_dir}/Combine/{fitFolderName}/dataFit/scans'], shell=True)
            os.chdir(os.path.join(output_dir, 'Combine', fitFolderName, 'dataFit'))
        
        if self.variable == '':
            cats = ["r"]
        else:
            cats = combineVariableDict[f'{self.year}'][f'{self.variable}']['paramStrNoOne']
        
        if self.batch_flavor == "slurm/psi":
            # Have to copy over the input to the JOB directory
            # Don't forget to VOMS!
            if "/work" in output_dir:
                slurm_copy_command = [
                    'cp', '-rf',
                    f'{output_dir}/Combine/{fitFolderName}/dataFit',
                    f"{os.environ['TARGET_PATH']}/Combine/{fitFolderName}"
                ]
            else:
                slurm_copy_command = [
                    'xrdcp', '-rf',
                    'root://t3dcachedb.psi.ch:1094//'+f'{output_dir}/Combine/{fitFolderName}/dataFit',
                    f"{os.environ['TARGET_PATH']}/Combine/{fitFolderName}"
                ]
            print(slurm_copy_command)
            execute_command(slurm_copy_command)
        
        for cat in cats:
            arguments = [
                "plot1DScan.py",
                os.path.join(output_dir, 'Combine', fitFolderName, 'dataFit', f'higgsCombineDataPostFitScanFit_{cat}.MultiDimFit.mH125.38.root'),
                "-o", f"scans/scan_{cat}_observed",
                "--POI", f"{cat}",
                "--others", os.path.join(output_dir, 'Combine', fitFolderName, 'dataFit', f'higgsCombineDataPostFitScanStat_{cat}.MultiDimFit.mH125.38.root')+":stat-only:2",
                "--main-label", "Observed",
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
        
        # Copy the files back to pnfs if we are on slurm/psi
        if self.batch_flavor == "slurm/psi":
            # Have to copy over the output to the final directory
            # Don't forget to VOMS!
            if "/work" in output_dir:
                slurm_copy_command = [
                    'cp', '-rf',
                    f"{os.environ['TARGET_PATH']}/Combine/",
                    output_dir
                ]
            else:
                slurm_copy_command = [
                    'xrdcp', '-rf',
                    f"{os.environ['TARGET_PATH']}/Combine/",
                    'root://t3dcachedb.psi.ch:1094//'+output_dir
                ]
            print(slurm_copy_command)
            execute_command(slurm_copy_command)
            # Clean up the temporary directory
            shutil.rmtree(os.environ["TARGET_PATH"])
                
        os.chdir(cwd)

class UnblindedCovCorrHesse(Task, HTCondorWorkflow, SlurmWorkflow, law.LocalWorkflow): #(law.Task): #(Task, HTCondorWorkflow, law.LocalWorkflow):
    output_dir = law.Parameter(default = '', description="Path to the output directory")
    variable = law.Parameter(default="", description="Variable to be used")
    year = law.Parameter(default='2022', description="Year")

    batch_flavor = law.Parameter(default="htcondor", description="Batch system to use")

    # def requires(self):
    def workflow_requires(self):
        workflow_reqs = super().workflow_requires()

        tasks = {}

        if workflow_reqs:
            tasks.update(workflow_reqs)
        
        if self.variable == '':
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_inclusive.yml")
        else:
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_{self.variable}.yml")
        
        #Load central config file
        with open(configYamlPath, 'r') as file:
            config = yaml.safe_load(file)
        
        if self.output_dir == '':
            output_dir = config['outputFolder']
        else:
            output_dir = self.output_dir

        tasks["RunT2WS"] = RunText2Workspace(output_dir=output_dir, variable=self.variable, year=self.year, batch_flavor=self.batch_flavor, workflow=config["combine_fit"]["execution"], version=self.variable if self.variable != "" else "inclusive", slurm_partition=config["combine_fit"]['batchPartition'], slurm_memory=config["combine_fit"]['batchMemory'], slurm_max_runtime=config["combine_fit"]['batchMaxRuntime'], htcondor_partition=config["combine_fit"]['batchPartition'], htcondor_memory=config["combine_fit"]['batchMemory'], htcondor_max_runtime=config["combine_fit"]['batchMaxRuntime'])
        
        return tasks

    def create_branch_map(self):
        branch_map = {i: current_branch for i, current_branch in enumerate([0])}
        return branch_map

    def output(self):        
        if self.variable == '':
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_inclusive.yml")
        else:
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_{self.variable}.yml")
        
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
                  
        if self.variable == '':
            output = []
        else:
            output = [os.path.join(output_dir, 'Combine', fitFolderName, 'hesse')]

            output += [os.path.join(output_dir, 'Combine', fitFolderName, 'hesse', f'robustHessefirstStep_data.root')]
            output += [os.path.join(output_dir, 'Combine', fitFolderName, 'hesse', f'multidimfitfirstStep_data.root')]
            output += [os.path.join(output_dir, 'Combine', fitFolderName, 'hesse', f'higgsCombinefirstStep_data.MultiDimFit.mH125.38.root')]
            
        outputFileTargets = []
                
        for _, current_output_path in enumerate(output):
            outputFileTargets.append(law.LocalFileTarget(current_output_path))

        return outputFileTargets

    def run(self):
       
        if self.variable == '':
            print("Running UnblindedCovCorrHesse for inclusive does not make sense. Please specify a variable.")
            exit(1)
            
        else:
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_{self.variable}.yml")
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

        cwd = os.getcwd()
        
        if self.batch_flavor == "slurm/psi":
            # Have to use /scratch/batch_username/ for slurm/psi
            if "/work" in output_dir:
                execute_command([f'mkdir -p {output_dir}/Combine/{fitFolderName}/hesse'], shell=True)
            else:
                execute_command([f'xrdfs root://t3dcachedb.psi.ch:1094/ mkdir -p {output_dir}/Combine/{fitFolderName}/hesse'], shell=True)

            os.environ["TARGET_PATH"] = f"/scratch/{os.environ['USER']}/{os.environ['SLURM_JOB_ID']}"
            execute_command([f'mkdir -p $TARGET_PATH/Combine/{fitFolderName}/hesse'], shell=True)
            os.chdir(os.path.join(os.environ["TARGET_PATH"], 'Combine', fitFolderName, 'hesse'))
        else:
            execute_command([f'mkdir -p {output_dir}/Combine/{fitFolderName}/hesse'], shell=True)
            os.chdir(os.path.join(output_dir, 'Combine', fitFolderName, 'hesse'))

        arguments = [
            "combine",
            "-M", "MultiDimFit",
            datacard_path,
            "--freezeParameters", "MH",
            "-m", "125.38",
            "-n", "firstStep_data",
            "--saveWorkspace",
            "--saveFitResult",
            "--saveSpecifiedIndex", f"""{",".join(combineVariableDict[f'{self.year}'][f'{self.variable}']['pdfIndeces'])}""",
            "--floatOtherPOIs", "1",
            "--robustHesse", "1",
            "--robustHesseSave", "1",
            "--cminDefaultMinimizerStrategy=0",
            "--X-rtd", "MINIMIZER_freezeDisassociatedParams",
            "--X-rtd", "MINIMIZER_multiMin_hideConstants",
            "--X-rtd", "MINIMIZER_multiMin_maskConstraints",
            "--X-rtd", "MINIMIZER_multiMin_maskChannels=2"
        ]
        command = arguments
        print(command)
        try:
            result = subprocess.run(command, check=True, text=True, capture_output=True)
            print("Script output:", result.stdout)
            print("Script executed successfully.")
        except subprocess.CalledProcessError as e:
            print("Error executing script:", e.stderr)
        
        # Copy the files back to pnfs if we are on slurm/psi
        if self.batch_flavor == "slurm/psi":
            # Have to copy over the output to the final directory
            # Don't forget to VOMS!
            if "/work" in output_dir:
                slurm_copy_command = [
                    'cp', '-rf',
                    f"{os.environ['TARGET_PATH']}/Combine/",
                    output_dir
                ]
            else:
                slurm_copy_command = [
                    'xrdcp', '-rf',
                    f"{os.environ['TARGET_PATH']}/Combine/",
                    'root://t3dcachedb.psi.ch:1094//'+output_dir
                ]
            print(slurm_copy_command)
            execute_command(slurm_copy_command)
            # Clean up the temporary directory
            shutil.rmtree(os.environ["TARGET_PATH"])
            
        os.chdir(cwd)
        
class UnblindedCovCorr(Task, SlurmWorkflow, HTCondorWorkflow, law.LocalWorkflow): #(law.Task): #(Task, HTCondorWorkflow, law.LocalWorkflow):
    output_dir = law.Parameter(default = '', description="Path to the output directory")
    variable = law.Parameter(default="", description="Variable to be used")
    year = law.Parameter(default='2022', description="Year")
    noPreliminary = law.Parameter(default=False, description="Flag, if final plot should bear the Preliminary.")

    batch_flavor = law.Parameter(default="htcondor", description="Batch system to use")

    # def requires(self):
    def workflow_requires(self):
        workflow_reqs = super().workflow_requires()

        tasks = {}

        if workflow_reqs:
            tasks.update(workflow_reqs)
        
        if self.variable == '':
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_inclusive.yml")
        else:
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_{self.variable}.yml")
        
        #Load central config file
        with open(configYamlPath, 'r') as file:
            config = yaml.safe_load(file)
        
        if self.output_dir == '':
            output_dir = config['outputFolder']
        else:
            output_dir = self.output_dir
            
        if self.variable == '':
            version = 'r'
        else:
            version = self.variable

        corrConfig = config["combine_hesse"]
            
        tasks["UnblindedCovCorrHesse"] = UnblindedCovCorrHesse(output_dir=output_dir, variable=self.variable, year=self.year, version=version, workflow=corrConfig["execution"], slurm_partition=corrConfig['batchPartition'], slurm_memory=corrConfig['batchMemory'], slurm_max_runtime=corrConfig['batchMaxRuntime'], htcondor_partition=corrConfig['batchPartition'], htcondor_memory=corrConfig['batchMemory'], htcondor_max_runtime=corrConfig['batchMaxRuntime'], batch_flavor=self.batch_flavor)
        
        return tasks

    def create_branch_map(self):
        branch_map = {i: current_branch for i, current_branch in enumerate([0])}
        return branch_map

    def output(self):        
        if self.variable == '':
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_inclusive.yml")
        else:
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_{self.variable}.yml")
        
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
        output = [os.path.join(output_dir, 'Combine', fitFolderName, 'hesse', 'Plots', 'data')]

        output += [os.path.join(output_dir, 'Combine', fitFolderName, 'hesse', 'Plots', 'data', f'corrMatrix_{self.variable}_syst_obs.pdf')]
        output += [os.path.join(output_dir, 'Combine', fitFolderName, 'hesse', 'Plots', 'data', f'corrMatrix_{self.variable}_syst_obs.png')]
        output += [os.path.join(output_dir, 'Combine', fitFolderName, 'hesse', 'Plots', 'data', f'covMatrix_{self.variable}_syst_obs.pdf')]
        output += [os.path.join(output_dir, 'Combine', fitFolderName, 'hesse', 'Plots', 'data', f'covMatrix_{self.variable}_syst_obs.png')]
        
        outputFileTargets = []
                
        for _, current_output_path in enumerate(output):
            outputFileTargets.append(law.LocalFileTarget(current_output_path))
            
        # print(outputFileTargets)

        return outputFileTargets

    def run(self):
       
        if self.variable == '':
            print("Running UnblindedCovCorrHesse for inclusive does not make sense. Please specify a variable.")
            exit(1)
            
        else:
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_{self.variable}.yml")
            fitFolderName = f'runFits_{self.variable}'
                  
        #Load central config file
        with open(configYamlPath, 'r') as file:
            config = yaml.safe_load(file)
        
        if self.output_dir == '':
            output_dir = config['outputFolder']
        else:
            output_dir = self.output_dir  

        if self.batch_flavor == "slurm/psi":
            # Have to use /scratch/batch_username/ for slurm/psi
            if "/work" in output_dir:
                execute_command([f'mkdir -p {output_dir}/Combine/{fitFolderName}/hesse/Plots/data'], shell=True)
            else:   
                execute_command([f'xrdfs root://t3dcachedb.psi.ch:1094/ mkdir -p {output_dir}/Combine/{fitFolderName}/hesse/Plots/data'], shell=True)

            os.environ["TARGET_PATH"] = f"/scratch/{os.environ['USER']}/{os.environ['SLURM_JOB_ID']}"
            execute_command([f'mkdir -p $TARGET_PATH/Combine/{fitFolderName}/hesse/Plots/data'], shell=True)

            if "/work" in output_dir:
                slurm_copy_command = [
                    'cp', '-rf',
                    f'{output_dir}/Combine/{fitFolderName}/hesse',
                    f'{os.environ["TARGET_PATH"]}/Combine/{fitFolderName}/'
                ]
            else:
                slurm_copy_command = [
                    'xrdcp', '-rf',
                    'root://t3dcachedb.psi.ch:1094//'+ f'{output_dir}/Combine/{fitFolderName}/hesse',
                    f'{os.environ["TARGET_PATH"]}/Combine/{fitFolderName}/'
                ]
            execute_command(slurm_copy_command)
            # output_dir = os.path.join(os.environ["TARGET_PATH"], 'Combine', fitFolderName, 'hesse', 'Plots', 'data')
            temp_output_dir = os.environ["TARGET_PATH"]
        else:
            execute_command([f'mkdir -p {output_dir}/Combine/{fitFolderName}/hesse/Plots/data'], shell=True)
            temp_output_dir = output_dir
            # output_dir = os.path.join(output_dir, 'Combine', fitFolderName, 'hesse', 'Plots', 'data')     
        
        cwd = os.getcwd()
        os.chdir(os.path.join(os.environ["ANALYSIS_PATH"], 'Plots'))

        arguments = [
            "python3",
            f"{os.path.join(os.environ['ANALYSIS_PATH'], 'Plots', 'makeCorrMatrix.py')}",
            "--inputJson", f"{os.path.join(os.environ['ANALYSIS_PATH'], 'Plots', 'inputs_robustHesse.json')}",
            "--mode", f"{self.variable}",
            "--input", f"{os.path.join(temp_output_dir, 'Combine', fitFolderName, 'hesse', f'robustHessefirstStep_data.root')}",
            "--output", f"{os.path.join(temp_output_dir, 'Combine', fitFolderName, 'hesse', 'Plots', 'data')}",
            "--translate", f"{os.path.join(os.environ['ANALYSIS_PATH'], 'Plots', 'poi_differential_hesse_noLabels.json')}",
            "--doObserved"
        ]
        if convert_boolean_string(self.noPreliminary):
            arguments.append("--noPreliminary")
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
            f"{os.path.join(os.environ['ANALYSIS_PATH'], 'Plots', 'makeCorrMatrix.py')}",
            "--inputJson", f"{os.path.join(os.environ['ANALYSIS_PATH'], 'Plots', 'inputs_robustHesse.json')}",
            "--mode", f"{self.variable}",
            "--input", f"{os.path.join(temp_output_dir, 'Combine', fitFolderName, 'hesse', f'robustHessefirstStep_data.root')}",
            "--output", f"{os.path.join(temp_output_dir, 'Combine', fitFolderName, 'hesse', 'Plots', 'data')}",
            "--translate", f"{os.path.join(os.environ['ANALYSIS_PATH'], 'Plots', 'poi_differential_hesse_noLabels.json')}",
            "--doCov",
            "--doObserved"
        ]
        if convert_boolean_string(self.noPreliminary):
            arguments.append("--noPreliminary")
        command = arguments
        # print(command)
        try:
            result = subprocess.run(command, check=True, text=True, capture_output=True)
            print("Script output:", result.stdout)
            print("Script executed successfully.")
        except subprocess.CalledProcessError as e:
            print("Error executing script:", e.stderr)
            
        # Copy the files back to pnfs if we are on slurm/psi
        if self.batch_flavor == "slurm/psi":
            # Have to copy over the output to the final directory
            # Don't forget to VOMS!
            if "/work" in output_dir:
                slurm_copy_command = [
                    'cp', '-rf',
                    f"{os.environ['TARGET_PATH']}/Combine/",
                    output_dir
                ]
            else:
                slurm_copy_command = [
                    'xrdcp', '-rf',
                    f"{os.environ['TARGET_PATH']}/Combine/",
                    'root://t3dcachedb.psi.ch:1094//'+output_dir
                ]
            print(slurm_copy_command)
            execute_command(slurm_copy_command)
            # Clean up the temporary directory
            shutil.rmtree(os.environ["TARGET_PATH"])    
        
        os.chdir(cwd)
        
        
class UnblindedImpactFirstStep(Task, SlurmWorkflow, HTCondorWorkflow, law.LocalWorkflow): #(law.Task): #(Task, HTCondorWorkflow, law.LocalWorkflow):
    output_dir = law.Parameter(default = '', description="Path to the output directory")
    variable = law.Parameter(default="", description="Variable to be used")
    year = law.Parameter(default='2022', description="Year")

    batch_flavor = law.Parameter(default="htcondor", description="Batch system to use")

    # def requires(self):
    def workflow_requires(self):
        workflow_reqs = super().workflow_requires()

        tasks = {}

        if workflow_reqs:
            tasks.update(workflow_reqs)
        
        if self.variable == '':
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_inclusive.yml")
        else:
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_{self.variable}.yml")
        
        #Load central config file
        with open(configYamlPath, 'r') as file:
            config = yaml.safe_load(file)
        
        if self.output_dir == '':
            output_dir = config['outputFolder']
        else:
            output_dir = self.output_dir
        
        impactConfig = config["combine_impacts"]
            
        tasks["RunT2WS"] = RunText2Workspace(output_dir=output_dir, variable=self.variable, year=self.year, batch_flavor=self.batch_flavor, workflow=impactConfig["execution"], version=self.variable if self.variable != "" else "inclusive", slurm_partition=impactConfig['batchPartition'], slurm_memory=impactConfig['batchMemory'], slurm_max_runtime=impactConfig['batchMaxRuntime'], htcondor_partition=impactConfig['batchPartition'], htcondor_memory=impactConfig['batchMemory'], htcondor_max_runtime=impactConfig['batchMaxRuntime'])
    
        return tasks

    def create_branch_map(self):
        branch_map = {i: current_branch for i, current_branch in enumerate([0])}
        return branch_map

    def output(self):        
        if self.variable == '':
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_inclusive.yml")
        else:
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_{self.variable}.yml")
        
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
            
        output = [os.path.join(output_dir, 'Combine', fitFolderName, 'impact', 'unblinded')]

        output += [os.path.join(output_dir, 'Combine', fitFolderName, 'impact', 'unblinded', f'higgsCombine_initialFit_Test.MultiDimFit.mH125.38.root')]
        
        outputFileTargets = []
                
        for _, current_output_path in enumerate(output):
            outputFileTargets.append(law.LocalFileTarget(current_output_path))

        return outputFileTargets

    def run(self):
       
        if self.variable == '':
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_inclusive.yml")
            fitFolderName = f'runFits_mu_fiducial'
            
        else:
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_{self.variable}.yml")
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
        
        cwd = os.getcwd()

        if self.batch_flavor == "slurm/psi":
            # Have to use /scratch/batch_username/ for slurm/psi
            if "/work" in output_dir:
                execute_command([f'mkdir -p {output_dir}/Combine/{fitFolderName}/impact/unblinded'], shell=True)
            else:   
                execute_command([f'xrdfs root://t3dcachedb.psi.ch:1094/ mkdir -p {output_dir}/Combine/{fitFolderName}/impact/unblinded'], shell=True)

            os.environ["TARGET_PATH"] = f"/scratch/{os.environ['USER']}/{os.environ['SLURM_JOB_ID']}"
            execute_command([f'mkdir -p $TARGET_PATH/Combine/{fitFolderName}/impact/unblinded'], shell=True)
            os.chdir(os.path.join(os.environ["TARGET_PATH"], 'Combine', fitFolderName, 'impact', 'unblinded'))
        else:
            execute_command([f'mkdir -p {output_dir}/Combine/{fitFolderName}/impact/unblinded'], shell=True)
            os.chdir(os.path.join(output_dir, 'Combine', fitFolderName, 'impact', 'unblinded'))
                    
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
                "--cminApproxPreFitTolerance", f"{config['combine_impacts']['cminApproxPreFitTolerance']}",
                "--setParameters", f"{config['combine_impacts']['setParameters']}"
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
                "--redefineSignalPOIs", f"""{",".join(combineVariableDict[f'{self.year}'][f'{self.variable}']['paramStrNoOne'])}""",
                "--freezeParameters", "MH",
                "-m", "125.38",
                "--robustFit", "1",
                "-n", "_initialFit_Test",
                "--cminDefaultMinimizerStrategy=0",
                "--X-rtd", "MINIMIZER_freezeDisassociatedParams",
                "--X-rtd", "MINIMIZER_multiMin_hideConstants",
                "--X-rtd", "MINIMIZER_multiMin_maskConstraints",
                "--X-rtd", "MINIMIZER_multiMin_maskChannels=2"
            ]
            command = arguments
            # print(command)
            try:
                result = subprocess.run(command, check=True, text=True, capture_output=True)
                print("Script output:", result.stdout)
                print("Script executed successfully.")
            except subprocess.CalledProcessError as e:
                print("Error executing script:", e.stderr)

        # Copy the files back to pnfs if we are on slurm/psi
        if self.batch_flavor == "slurm/psi":
            # Have to copy over the output to the final directory
            # Don't forget to VOMS!
            if "/work" in output_dir:
                slurm_copy_command = [
                    'cp', '-rf',
                    f"{os.environ['TARGET_PATH']}/Combine/",
                    output_dir
                ]
            else:
                slurm_copy_command = [
                    'xrdcp', '-rf',
                    f"{os.environ['TARGET_PATH']}/Combine/",
                    'root://t3dcachedb.psi.ch:1094//'+output_dir
                ]
            print(slurm_copy_command)
            execute_command(slurm_copy_command)
            # Clean up the temporary directory
            shutil.rmtree(os.environ["TARGET_PATH"])   
            
        os.chdir(cwd)
        
class UnblindedImpactSecondStep(Task, HTCondorWorkflow, SlurmWorkflow, law.LocalWorkflow): #(law.Task): #(Task, HTCondorWorkflow, law.LocalWorkflow):
    output_dir = law.Parameter(default = '', description="Path to the output directory")
    variable = law.Parameter(default="", description="Variable to be used")
    year = law.Parameter(default='2022', description="Year")

    batch_flavor = law.Parameter(default="htcondor", description="Batch system to use")

    # def requires(self):
    def workflow_requires(self):
        workflow_reqs = super().workflow_requires()

        tasks = {}

        if workflow_reqs:
            tasks.update(workflow_reqs)
        
        if self.variable == '':
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_inclusive.yml")
        else:
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_{self.variable}.yml")
        
        #Load central config file
        with open(configYamlPath, 'r') as file:
            config = yaml.safe_load(file)
        
        if self.output_dir == '':
            output_dir = config['outputFolder']
        else:
            output_dir = self.output_dir

        impactConfig = config["combine_impacts"]
            
        tasks["UnblindedImpactFirstStep"] = UnblindedImpactFirstStep(output_dir=output_dir, variable=self.variable, year=self.year, batch_flavor=self.batch_flavor, workflow=impactConfig["execution"], version=self.variable if self.variable != "" else "inclusive", slurm_partition=impactConfig['batchPartition'], slurm_memory=impactConfig['batchMemory'], slurm_max_runtime=impactConfig['batchMaxRuntime'], htcondor_partition=impactConfig['batchPartition'], htcondor_memory=impactConfig['batchMemory'], htcondor_max_runtime=impactConfig['batchMaxRuntime'])
        
        return tasks

    def create_branch_map(self):
        
        if self.variable == '':
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_inclusive.yml")
        else:
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_{self.variable}.yml")
                  
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

        if self.variable == '':
            poiList = ["r"]
        else:
            poiList = combineVariableDict[f'{self.year}'][f'{self.variable}']['paramStrNoOne']
        
        paramList = all_free_parameters(datacard_path, 'w', 'ModelConfig', poiList)

        
        branch_map = {i: current_param for i, current_param in enumerate(paramList)}
        return branch_map

    def output(self):        
        current_param = self.branch_data
        
        if self.variable == '':
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_inclusive.yml")
        else:
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_{self.variable}.yml")
        
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
        output = [os.path.join(output_dir, 'Combine', fitFolderName, 'impact', 'unblinded')]

        output += [os.path.join(output_dir, 'Combine', fitFolderName, 'impact', 'unblinded', f'higgsCombine_paramFit_Test_{current_param}.MultiDimFit.mH125.38.root')]
        
        outputFileTargets = []
                
        for _, current_output_path in enumerate(output):
            outputFileTargets.append(law.LocalFileTarget(current_output_path))
            
        # print(outputFileTargets)

        return outputFileTargets

    def run(self):
        current_param = self.branch_data
       
        if self.variable == '':
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_inclusive.yml")
            fitFolderName = f'runFits_mu_fiducial'
            
        else:
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_{self.variable}.yml")
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
        
        cwd = os.getcwd()

        if self.batch_flavor == "slurm/psi":
            # Have to use /scratch/batch_username/ for slurm/psi
            if "/work" in output_dir:
                execute_command([f'mkdir -p {output_dir}/Combine/{fitFolderName}/impact/unblinded'], shell=True)
            else:   
                execute_command([f'xrdfs root://t3dcachedb.psi.ch:1094/ mkdir -p {output_dir}/Combine/{fitFolderName}/impact/unblinded'], shell=True)

            os.environ["TARGET_PATH"] = f"/scratch/{os.environ['USER']}/{os.environ['SLURM_JOB_ID']}"
            execute_command([f'mkdir -p $TARGET_PATH/Combine/{fitFolderName}/impact/unblinded'], shell=True)
            os.chdir(os.path.join(os.environ["TARGET_PATH"], 'Combine', fitFolderName, 'impact', 'unblinded'))
        else:
            execute_command([f'mkdir -p {output_dir}/Combine/{fitFolderName}/impact/unblinded'], shell=True)
            os.chdir(os.path.join(output_dir, 'Combine', fitFolderName, 'impact', 'unblinded'))

        if self.variable == '':
            
            initial_fit = os.path.join(output_dir, 'Combine', fitFolderName, 'impact', 'unblinded', f'higgsCombine_initialFit_Test.MultiDimFit.mH125.38.root')
            
            f = ROOT.TFile(initial_fit)
            tree = f.Get("limit")
            
            if not tree:
                print("Error: Tree 'limit' not found in the file.")
                exit(1)
            # Access the branch 'r_YH_0p9_2p5' and get its first value
            if hasattr(tree, 'r'):
                tree.GetEntry(0)  # Load the first entry
                poi_bf_value = getattr(tree, 'r')  # Access the branch value
                poi_bf_string = f'r={poi_bf_value}'
                print(f"First value of branch 'r': {poi_bf_value}")
            else:
                print("Error: Branch 'r' not found in the tree.")
                exit(1)

            arguments = [
                "combine",
                "-M", "MultiDimFit",
                "-d", datacard_path,
                "--algo", "impact",
                "--redefineSignalPOIs", "r",
                "--freezeParameters", "MH",
                "-m", "125.38",
                "-P", f"{current_param}",
                "--setParameters", poi_bf_string,
                "--floatOtherPOIs", "1",
                "--saveInactivePOI", "1",
                "--robustFit", "1",
                "-n", f"_paramFit_Test_{current_param}",
                "--cminDefaultMinimizerStrategy=0",
                "--X-rtd", "MINIMIZER_freezeDisassociatedParams",
                "--X-rtd", "MINIMIZER_multiMin_hideConstants",
                "--X-rtd", "MINIMIZER_multiMin_maskConstraints",
                "--X-rtd", "MINIMIZER_multiMin_maskChannels=2",
                "--cminApproxPreFitTolerance", f"{config['combine_impacts']['cminApproxPreFitTolerance']}",
                "--stepSize", f"{config['combine_impacts']['stepSize']}",
                "--setCrossingTolerance", f"{config['combine_impacts']['setCrossingTolerance']}",
                "--robustHesse", "1"
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

            initial_fit = os.path.join(output_dir, 'Combine', fitFolderName, 'impact', 'unblinded', f'higgsCombine_initialFit_Test.MultiDimFit.mH125.38.root')

            poi_bf = []
            
            f = ROOT.TFile(initial_fit)
            tree = f.Get("limit")
            
            if not tree:
                print("Error: Tree 'limit' not found in the file.")
                exit(1)

            for poi in combineVariableDict[f'{self.year}'][f'{self.variable}']['paramStrNoOne']:
                # Access the branch 'r_YH_0p9_2p5' and get its first value
                if hasattr(tree, poi):
                    tree.GetEntry(0)  # Load the first entry
                    first_value = getattr(tree, poi)  # Access the branch value
                    poi_bf.append(f'{poi}={first_value}')
                    print(f"First value of branch '{poi}': {first_value}")
                else:
                    print(f"Error: Branch '{poi}' not found in the tree.")
                    exit(1)

            poi_bf_string = ",".join(poi_bf)
        
            arguments = [
                "combine",
                "-M", "MultiDimFit",
                "-d", datacard_path,
                "--algo", "impact",
                "--redefineSignalPOIs", f"""{",".join(combineVariableDict[f'{self.year}'][f'{self.variable}']['paramStrNoOne'])}""",
                "--setParameters", poi_bf_string,
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
                "--X-rtd", "MINIMIZER_multiMin_maskChannels=2"
            ]
            command = arguments
            # print(command)
            try:
                result = subprocess.run(command, check=True, text=True, capture_output=True)
                print("Script output:", result.stdout)
                print("Script executed successfully.")
            except subprocess.CalledProcessError as e:
                print("Error executing script:", e.stderr)

        # Copy the files back to pnfs if we are on slurm/psi
        if self.batch_flavor == "slurm/psi":
            # Have to copy over the output to the final directory
            # Don't forget to VOMS!
            if "/work" in output_dir:
                slurm_copy_command = [
                    'cp', '-rf',
                    f"{os.environ['TARGET_PATH']}/Combine/",
                    output_dir
                ]
            else:
                slurm_copy_command = [
                    'xrdcp', '-rf',
                    f"{os.environ['TARGET_PATH']}/Combine/",
                    'root://t3dcachedb.psi.ch:1094//'+output_dir
                ]
            print(slurm_copy_command)
            execute_command(slurm_copy_command)
            # Clean up the temporary directory
            shutil.rmtree(os.environ["TARGET_PATH"])
            
        os.chdir(cwd)
        
class UnblindedImpactThirdStep(Task, SlurmWorkflow, HTCondorWorkflow, law.LocalWorkflow): #(law.Task): #(Task, HTCondorWorkflow, law.LocalWorkflow):
    output_dir = law.Parameter(default = '', description="Path to the output directory")
    variable = law.Parameter(default="", description="Variable to be used")
    year = law.Parameter(default='2022', description="Year")

    batch_flavor = law.Parameter(default="htcondor", description="Batch system to use")

    # def requires(self):
    def workflow_requires(self):
        workflow_reqs = super().workflow_requires()

        tasks = {}

        if workflow_reqs:
            tasks.update(workflow_reqs)
        
        if self.variable == '':
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_inclusive.yml")
            version = 'r'
        else:
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_{self.variable}.yml")
            version = self.variable
        
        #Load central config file
        with open(configYamlPath, 'r') as file:
            config = yaml.safe_load(file)
        
        if self.output_dir == '':
            output_dir = config['outputFolder']
        else:
            output_dir = self.output_dir

        impactConfig = config["combine_impacts"]
            
        tasks["UnblindedImpactSecondStep"] = UnblindedImpactSecondStep(output_dir=output_dir, variable=self.variable, year=self.year, version=version, workflow=impactConfig["execution"], slurm_partition=impactConfig['batchPartition'], slurm_memory=impactConfig['batchMemory'], slurm_max_runtime=impactConfig['batchMaxRuntime'], htcondor_partition=impactConfig['batchPartition'], htcondor_memory=impactConfig['batchMemory'], htcondor_max_runtime=impactConfig['batchMaxRuntime'], batch_flavor=self.batch_flavor)
        
        return tasks

    def create_branch_map(self):

        branch_map = {i: current_branch for i, current_branch in enumerate([0])}
        return branch_map

    def output(self):
        if self.variable == '':
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_inclusive.yml")
        else:
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_{self.variable}.yml")
        
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
            output += [os.path.join(output_dir, 'Combine', fitFolderName, 'impact', 'unblinded', 'impacts')]
            output += [os.path.join(output_dir, 'Combine', fitFolderName, 'impact', 'unblinded', 'impacts', f'impacts_unblinded.pdf')]
            output += [os.path.join(output_dir, 'Combine', fitFolderName, 'impact', 'unblinded', 'impacts', 'impacts_corrected_dropBkgModelParams.json')]
            
        else:
            for cat in combineVariableDict[f'{self.year}'][f'{self.variable}']['paramStrNoOne']:
                output += [os.path.join(output_dir, 'Combine', fitFolderName, 'impact', 'unblinded', 'impacts')]
                output += [os.path.join(output_dir, 'Combine', fitFolderName, 'impact', 'unblinded', 'impacts', f'impacts_unblinded_{cat}.pdf')]
                output += [os.path.join(output_dir, 'Combine', fitFolderName, 'impact', 'unblinded', 'impacts', 'impacts_corrected_dropBkgModelParams.json')]
                
        output += [os.path.join(output_dir, 'Combine', fitFolderName, 'impact', 'unblinded', 'impacts', f'impacts.json')]
        
        outputFileTargets = []
                
        for _, current_output_path in enumerate(output):
            outputFileTargets.append(law.LocalFileTarget(current_output_path))
            
        # print(outputFileTargets)

        return outputFileTargets

    def run(self):
       
        if self.variable == '':
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_inclusive.yml")
            fitFolderName = f'runFits_mu_fiducial'
            
        else:
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_{self.variable}.yml")
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

        cwd = os.getcwd()

        if self.batch_flavor == "slurm/psi":
            # Have to use /scratch/batch_username/ for slurm/psi
            if "/work" in output_dir:
                execute_command([f'mkdir -p {output_dir}/Combine/{fitFolderName}/impact/unblinded/impacts'], shell=True)
            else:   
                execute_command([f'xrdfs root://t3dcachedb.psi.ch:1094/ mkdir -p {output_dir}/Combine/{fitFolderName}/impact/unblinded/impacts'], shell=True)

            os.environ["TARGET_PATH"] = f"/scratch/{os.environ['USER']}/{os.environ['SLURM_JOB_ID']}"
            execute_command([f'mkdir -p $TARGET_PATH/Combine/{fitFolderName}/impact/unblinded/impacts'], shell=True)
            os.chdir(os.path.join(os.environ["TARGET_PATH"], 'Combine', fitFolderName, 'impact', 'unblinded'))

            if "/work" in output_dir:
                slurm_copy_command = [
                    'cp', '-rf',
                    f'{output_dir}/Combine/{fitFolderName}/impact/unblinded',
                    f'{os.environ["TARGET_PATH"]}/Combine/{fitFolderName}/impact'
                ]
            else:
                slurm_copy_command = [
                    'xrdcp', '-rf',
                    'root://t3dcachedb.psi.ch:1094//'+ f'{output_dir}/Combine/{fitFolderName}/impact/unblinded',
                    f'{os.environ["TARGET_PATH"]}/Combine/{fitFolderName}/impact'
                ]
            execute_command(slurm_copy_command)
            temp_output_dir = os.environ["TARGET_PATH"]
        else:
            execute_command([f'mkdir -p {output_dir}/Combine/{fitFolderName}/impact/unblinded/impacts'], shell=True)
            os.chdir(os.path.join(output_dir, 'Combine', fitFolderName, 'impact', 'unblinded'))
            temp_output_dir = output_dir

        if self.variable == '':
            arguments = [
                "combineTool.py",
                "-M", "Impacts",
                "-d", datacard_path,
                "-m", "125.38",
                "-o", "impacts/impacts.json"
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
                f"{os.path.join(os.environ['ANALYSIS_PATH'], 'Plots', 'correctImpacts.py')}",
                "--impactsJson", f"{os.path.join(temp_output_dir, 'Combine', fitFolderName, 'impact', 'unblinded', 'impacts', 'impacts.json')}",
                "--frozenParam", "MH",
                "--dropBkgModelParams"
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
                "-i", f"{os.path.join(temp_output_dir, 'Combine', fitFolderName, 'impact', 'unblinded', 'impacts', 'impacts_corrected_dropBkgModelParams.json')}",
                "-o", "impacts/impacts_unblinded",
            ]
            if config['combine_impacts']['not_show_POI']:
                arguments.append("--blind")
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
                "-o", "impacts/impacts.json",
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
                
            arguments = [
                "python3",
                f"{os.path.join(os.environ['ANALYSIS_PATH'], 'Plots', 'correctImpacts.py')}",
                "--impactsJson", f"{os.path.join(temp_output_dir, 'Combine', fitFolderName, 'impact', 'unblinded', 'impacts', 'impacts.json')}",
                "--frozenParam", "MH",
                "--dropBkgModelParams"
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
                
            for cat in combineVariableDict[f'{self.year}'][f'{self.variable}']['paramStrNoOne']:
                arguments = [
                    "plotImpacts.py",
                    "-i", f"{os.path.join(temp_output_dir, 'Combine', fitFolderName, 'impact', 'unblinded', 'impacts', 'impacts_corrected_dropBkgModelParams.json')}",
                    "-o", f"impacts/impacts_unblinded_{cat}",
                    "--POI", f"{cat}",
                    "--translate", f"{os.path.join(os.environ['ANALYSIS_PATH'], 'Combine', 'pois.json')}",
                ]
                if config['combine_impacts']['not_show_POI']:
                    arguments.append("--blind")
                command = arguments
                # print(command)
                try:
                    result = subprocess.run(command, check=True, text=True, capture_output=True)
                    print("Script output:", result.stdout)
                    print("Script executed successfully.")
                except subprocess.CalledProcessError as e:
                    print("Error executing script:", e.stderr)

        # Copy the files back to pnfs if we are on slurm/psi
        if self.batch_flavor == "slurm/psi":
            # Have to copy over the output to the final directory
            # Don't forget to VOMS!
            if "/work" in output_dir:
                slurm_copy_command = [
                    'cp', '-rf',
                    f"{os.environ['TARGET_PATH']}/Combine/",
                    output_dir
                ]
            else:
                slurm_copy_command = [
                    'xrdcp', '-rf',
                    f"{os.environ['TARGET_PATH']}/Combine/",
                    'root://t3dcachedb.psi.ch:1094//'+output_dir
                ]
            print(slurm_copy_command)
            execute_command(slurm_copy_command)
            # Clean up the temporary directory
            shutil.rmtree(os.environ["TARGET_PATH"])
            
        os.chdir(cwd)
        
        
class MggBestFit(Task, HTCondorWorkflow, SlurmWorkflow, law.LocalWorkflow): #(law.Task): #(Task, HTCondorWorkflow, law.LocalWorkflow):
    output_dir = law.Parameter(default = '', description="Path to the output directory")
    variable = law.Parameter(default="", description="Variable to be used")
    year = law.Parameter(default='2022', description="Year")

    batch_flavor = law.Parameter(default="htcondor", description="Batch system to use")

    # def requires(self):
    def workflow_requires(self):
        workflow_reqs = super().workflow_requires()

        tasks = {}

        if workflow_reqs:
            tasks.update(workflow_reqs)
        
        if self.variable == '':
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_inclusive.yml")
        else:
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_{self.variable}.yml")
        
        #Load central config file
        with open(configYamlPath, 'r') as file:
            config = yaml.safe_load(file)
        
        if self.output_dir == '':
            output_dir = config['outputFolder']
        else:
            output_dir = self.output_dir

        toyConfig = config["combine_mggToys"]

        tasks["RunT2WS"] = RunText2Workspace(output_dir=output_dir, variable=self.variable, year=self.year, batch_flavor=self.batch_flavor, workflow=toyConfig["execution"], version=self.variable if self.variable != "" else "inclusive", slurm_partition=toyConfig['batchPartition'], slurm_memory=toyConfig['batchMemory'], slurm_max_runtime=toyConfig['batchMaxRuntime'], htcondor_partition=toyConfig['batchPartition'], htcondor_memory=toyConfig['batchMemory'], htcondor_max_runtime=toyConfig['batchMaxRuntime'])

        return tasks

    def create_branch_map(self):
            
        if self.variable == "":
            cat_list = ["r"]
        else:
            cat_list = combineVariableDict[f'{self.year}'][f'{self.variable}']['paramStrNoOne']

        branch_map = {i: current_cat for i, current_cat in enumerate(cat_list)}
        return branch_map

    def output(self):        
        cat = self.branch_data
                
        if self.variable == '':
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_inclusive.yml")
        else:
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_{self.variable}.yml")
        
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
            
        output = [os.path.join(output_dir, 'Combine', fitFolderName, 'postFit')]
        output += [os.path.join(output_dir, 'Combine', fitFolderName, 'postFit', f'SplusBModels_{cat}')]
        output += [os.path.join(output_dir, 'Combine', fitFolderName, 'postFit', f'SplusBModels_{cat}', f'higgsCombine_bestfit_syst_obs_{cat}.MultiDimFit.mH125.38.root')]
        
        outputFileTargets = []
                
        for _, current_output_path in enumerate(output):
            outputFileTargets.append(law.LocalFileTarget(current_output_path))
            
        # print(outputFileTargets)

        return outputFileTargets

    def run(self):
        cat = self.branch_data
       
        if self.variable == '':
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_inclusive.yml")
            fitFolderName = f'runFits_mu_fiducial'
            
        else:
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_{self.variable}.yml")
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
             
        cwd = os.getcwd()

        if self.batch_flavor == "slurm/psi":
            # Have to use /scratch/batch_username/ for slurm/psi
            if "/work" in output_dir:
                execute_command([f'mkdir -p {output_dir}/Combine/{fitFolderName}/postFit/SplusBModels_{cat}'], shell=True)
            else:   
                execute_command([f'xrdfs root://t3dcachedb.psi.ch:1094/ mkdir -p {output_dir}/Combine/{fitFolderName}/postFit/SplusBModels_{cat}'], shell=True)

            os.environ["TARGET_PATH"] = f"/scratch/{os.environ['USER']}/{os.environ['SLURM_JOB_ID']}"
            execute_command([f'mkdir -p $TARGET_PATH/Combine/{fitFolderName}/postFit/SplusBModels_{cat}'], shell=True)
            os.chdir(os.path.join(os.environ["TARGET_PATH"], 'Combine', fitFolderName, 'postFit', f'SplusBModels_{cat}'))
        else:
            execute_command([f'mkdir -p {output_dir}/Combine/{fitFolderName}/postFit/SplusBModels_{cat}'], shell=True)
            os.chdir(os.path.join(output_dir, 'Combine', fitFolderName, 'postFit', f'SplusBModels_{cat}'))

        arguments = [
            "combine",
            "--floatOtherPOIs", "1",
            "-P", f"{cat}",
            "--freezeParameters", "MH",
            "--saveInactivePOI", "1",
            "--saveWorkspace",
            "--saveSpecifiedNuis", "all",
            "--cminDefaultMinimizerStrategy", "0",
            "--X-rtd", "MINIMIZER_freezeDisassociatedParams",
            "--X-rtd", "MINIMIZER_multiMin_hideConstants",
            "--X-rtd", "MINIMIZER_multiMin_maskConstraints",
            "--X-rtd", "MINIMIZER_multiMin_maskChannels=2",
            "-M", f"{config['combine_mggToys']['loadSnapshot']}",
            "-m", "125.38",
            "-d", datacard_path,
            "-n", f"_bestfit_syst_obs_{cat}"
        ]
        command = arguments
        # print(command)
        try:
            result = subprocess.run(command, check=True, text=True, capture_output=True)
            print("Script output:", result.stdout)
            print("Script executed successfully.")
        except subprocess.CalledProcessError as e:
            print("Error executing script:", e.stderr)

        # Copy the files back to pnfs if we are on slurm/psi
        if self.batch_flavor == "slurm/psi":
            # Have to copy over the output to the final directory
            # Don't forget to VOMS!
            if "/work" in output_dir:
                slurm_copy_command = [
                    'cp', '-rf',
                    f"{os.environ['TARGET_PATH']}/Combine/",
                    output_dir
                ]
            else:
                slurm_copy_command = [
                    'xrdcp', '-rf',
                    f"{os.environ['TARGET_PATH']}/Combine/",
                    'root://t3dcachedb.psi.ch:1094//'+output_dir
                ]
            print(slurm_copy_command)
            execute_command(slurm_copy_command)
            # Clean up the temporary directory
            shutil.rmtree(os.environ["TARGET_PATH"])
        
        os.chdir(cwd)
        
class MggToyGeneration(Task, HTCondorWorkflow, SlurmWorkflow, law.LocalWorkflow): #(law.Task): #(Task, HTCondorWorkflow, law.LocalWorkflow):
    output_dir = law.Parameter(default = '', description="Path to the output directory")
    variable = law.Parameter(default="", description="Variable to be used")
    year = law.Parameter(default='2022', description="Year")
    is_postfit = law.Parameter(default=False, description="Flag that signifies if toys are created for postfit mass distributions.")

    batch_flavor = law.Parameter(default="htcondor", description="Batch system to use")

    # def requires(self):
    def workflow_requires(self):
        workflow_reqs = super().workflow_requires()

        tasks = {}

        if workflow_reqs:
            tasks.update(workflow_reqs)
        
        if self.variable == '':
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_inclusive.yml")
        else:
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_{self.variable}.yml")
        
        #Load central config file
        with open(configYamlPath, 'r') as file:
            config = yaml.safe_load(file)

        mggConfig = config['combine_mggToys']
        
        if self.output_dir == '':
            output_dir = config['outputFolder']
        else:
            output_dir = self.output_dir

        if convert_boolean_string(self.is_postfit):
            if self.variable == "":
                version = 'r'
            else:
                version = self.variable
            tasks["MggBestFit"] = MggBestFit(output_dir=output_dir, variable=self.variable, year=self.year, batch_flavor=self.batch_flavor, version=version, workflow=mggConfig['execution'], slurm_partition=mggConfig['batchPartition'], slurm_memory=mggConfig['batchMemory'], slurm_max_runtime=mggConfig['batchMaxRuntime'], htcondor_partition=mggConfig['batchPartition'], htcondor_memory=mggConfig['batchMemory'], htcondor_max_runtime=mggConfig['batchMaxRuntime'])
        else:
            tasks["RunT2WS"] = RunText2Workspace(output_dir=output_dir, variable=self.variable, year=self.year, batch_flavor=self.batch_flavor, workflow=mggConfig["execution"], version=self.variable if self.variable != "" else "inclusive", slurm_partition=mggConfig['batchPartition'], slurm_memory=mggConfig['batchMemory'], slurm_max_runtime=mggConfig['batchMaxRuntime'], htcondor_partition=mggConfig['batchPartition'], htcondor_memory=mggConfig['batchMemory'], htcondor_max_runtime=mggConfig['batchMaxRuntime'])
            
        return tasks

    def create_branch_map(self):
        
        if self.variable == '':
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_inclusive.yml")
        else:
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_{self.variable}.yml")
                  
        #Load central config file
        with open(configYamlPath, 'r') as file:
            config = yaml.safe_load(file)
            
        if self.variable == "":
            cat_list = ["r"]
        else:
            cat_list = combineVariableDict[f'{self.year}'][f'{self.variable}']['paramStrNoOne']
        nToys = config['combine_mggToys']['nToys']
        
        toy_cat_list = [
            (toy, cat)
            for toy in range(int(nToys))
            for cat in cat_list
        ]
        
        branch_map = {i: current_toy for i, current_toy in enumerate(toy_cat_list)}
        return branch_map

    def output(self):        
        toy, cat = self.branch_data
                
        if self.variable == '':
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_inclusive.yml")
        else:
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_{self.variable}.yml")
        
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
            
        if convert_boolean_string(self.is_postfit):
            output = [os.path.join(output_dir, 'Combine', fitFolderName, 'postFit', f'SplusBModels_{cat}', 'toys')]
            output += [os.path.join(output_dir, 'Combine', fitFolderName, 'postFit', f'SplusBModels_{cat}', 'toys', 'filechecker')]
            output += [os.path.join(output_dir, 'Combine', fitFolderName, 'postFit', f'SplusBModels_{cat}', 'toys', 'filechecker', f'toy_{toy}_ok.txt')]
            output += [os.path.join(output_dir, 'Combine', fitFolderName, 'postFit', f'SplusBModels_{cat}', 'toys', f'toy_{toy}.root')]
        else:
            output = [os.path.join(output_dir, 'Combine', fitFolderName, 'preFit')]
            output += [os.path.join(output_dir, 'Combine', fitFolderName, 'preFit', f'SplusBModels_{cat}')]
            output += [os.path.join(output_dir, 'Combine', fitFolderName, 'preFit', f'SplusBModels_{cat}', 'toys')]
            output += [os.path.join(output_dir, 'Combine', fitFolderName, 'preFit', f'SplusBModels_{cat}', 'toys', 'filechecker')]
            output += [os.path.join(output_dir, 'Combine', fitFolderName, 'preFit', f'SplusBModels_{cat}', 'toys', 'filechecker', f'toy_{toy}_ok.txt')]
            output += [os.path.join(output_dir, 'Combine', fitFolderName, 'preFit', f'SplusBModels_{cat}', 'toys', f'toy_{toy}.root')]
        
        outputFileTargets = []
                
        for _, current_output_path in enumerate(output):
            outputFileTargets.append(law.LocalFileTarget(current_output_path))
            
        # print(outputFileTargets)

        return outputFileTargets

    def run(self):
        toy, cat = self.branch_data
       
        if self.variable == '':
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_inclusive.yml")
            fitFolderName = f'runFits_mu_fiducial'
            
        else:
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_{self.variable}.yml")
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
             
        cwd = os.getcwd()

        if convert_boolean_string(self.is_postfit):

            os.environ["TARGET_PATH"] = f"/scratch/{os.environ['USER']}/{os.environ['SLURM_JOB_ID']}"

            if self.batch_flavor == "slurm/psi":
                # Have to use /scratch/batch_username/ for slurm/psi
                if "/work" in output_dir:
                    execute_command([f'mkdir -p {output_dir}/Combine/{fitFolderName}/postFit/SplusBModels_{cat}/toys/filechecker'], shell=True)
                else:   
                    execute_command([f'xrdfs root://t3dcachedb.psi.ch:1094/ mkdir -p {output_dir}/Combine/{fitFolderName}/postFit/SplusBModels_{cat}/toys/filechecker'], shell=True)

                execute_command([f'mkdir -p $TARGET_PATH/Combine/{fitFolderName}/postFit/SplusBModels_{cat}/toys/filechecker'], shell=True)
                os.chdir(os.path.join(os.environ["TARGET_PATH"], 'Combine', fitFolderName, 'postFit', f'SplusBModels_{cat}', 'toys'))
            else:
                execute_command([f'mkdir -p {output_dir}/Combine/{fitFolderName}/postFit/SplusBModels_{cat}/toys/filechecker'], shell=True)
                os.chdir(os.path.join(output_dir, 'Combine', fitFolderName, 'postFit', f'SplusBModels_{cat}', 'toys'))
        
            best_fit = os.path.join(output_dir, 'Combine', fitFolderName, 'postFit', f'SplusBModels_{cat}', f'higgsCombine_bestfit_syst_obs_{cat}.MultiDimFit.mH125.38.root')

            f = ROOT.TFile(best_fit)
            w = f.Get("w")
            w.loadSnapshot(config['combine_mggToys']['loadSnapshot'])
            poi_bf = w.var(cat).getVal()

            arguments = [
                "combine",
                best_fit,
                "-M", "GenerateOnly",
                "-m", "125.380",
                "--saveWorkspace",
                "--toysFrequentist",
                "--bypassFrequentistFit",
                "-t", "1",
                "-s", "-1",
                "-n", f"_{toy}_gen_step",
                "--setParameters", f"{cat}={poi_bf}",
                "--snapshotName", f"{config['combine_mggToys']['loadSnapshot']}"
            ]
            command = arguments
            # print(command)
            try:
                result = subprocess.run(command, check=True, text=True, capture_output=True)
                print("Script output:", result.stdout)
                print("Script executed successfully.")
            except subprocess.CalledProcessError as e:
                print("Error executing script:", e.stderr)
                
            # Define the source pattern and destination path
            # On the PSI Tier 3 when executed with SLURM, the Toys are on the Storage Element which needs special handling
            # For this reason, introduce a "toy_output_dir" which is in the slurm/psi case the /scratch directory
            # and in the other cases the output_dir
            if self.batch_flavor == "slurm/psi" and "/pnfs" in output_dir:
                toy_output_dir = os.environ["TARGET_PATH"]
            else:
                toy_output_dir = output_dir

            source_pattern = os.path.join(toy_output_dir, 'Combine', fitFolderName, 'postFit', f'SplusBModels_{cat}', 'toys', f'higgsCombine_{toy}_gen_step*.root')
            destination = os.path.join(toy_output_dir, 'Combine', fitFolderName, 'postFit', f'SplusBModels_{cat}', 'toys', f'gen_{toy}.root')

            # Use glob to find files matching the source pattern
            source_files = glob.glob(source_pattern)

            if not source_files:
                print("No files found matching the pattern.")
            else:
                # Move each matched file to the destination
                for source_file in source_files:
                    try:
                        print(f"Moving {source_file} to {destination}")
                        if self.batch_flavor == "slurm/psi" and (("/pnfs" in source_file) or ("/pnfs" in destination)):
                            manually_move_t3(source_file, destination)
                        else:
                            shutil.move(source_file, destination)
                        print("File moved successfully.")
                    except Exception as e:
                        print(f"Error moving file {source_file}: {e}")

            arguments = [
                "combine",
                f"gen_{toy}.root",
                "-m", "125.380",
                "-M", f"{config['combine_mggToys']['loadSnapshot']}",
                "-P", f"{cat}",
                "--floatOtherPOIs=1",
                "--saveWorkspace",
                "--toysFrequentist",
                "--bypassFrequentistFit",
                "-t", "1",
                "--setParameters", f"{cat}={poi_bf}",
                "-s", "-1",
                "-n", f"_{toy}_fit_step",
                "--cminDefaultMinimizerStrategy", "0",
                "--X-rtd", "MINIMIZER_freezeDisassociatedParams",
                "--X-rtd", "MINIMIZER_multiMin_hideConstants",
                "--X-rtd", "MINIMIZER_multiMin_maskConstraints",
                "--X-rtd", "MINIMIZER_multiMin_maskChannels=2"
            ]
            command = arguments
            # print(command)
            try:
                result = subprocess.run(command, check=True, text=True, capture_output=True)
                print("Script output:", result.stdout)
                print("Script executed successfully.")
            except subprocess.CalledProcessError as e:
                print("Error executing script:", e.stderr)    
                
            # Define the source pattern and destination path
            source_pattern = os.path.join(toy_output_dir, 'Combine', fitFolderName, 'postFit', f'SplusBModels_{cat}', 'toys', f'higgsCombine_{toy}_fit_step*.root')
            destination = os.path.join(toy_output_dir, 'Combine', fitFolderName, 'postFit', f'SplusBModels_{cat}', 'toys', f'fit_{toy}.root')

            # Use glob to find files matching the source pattern
            source_files = glob.glob(source_pattern)

            if not source_files:
                print("No files found matching the pattern.")
            else:
                # Move each matched file to the destination
                for source_file in source_files:
                    try:
                        print(f"Moving {source_file} to {destination}")
                        if self.batch_flavor == "slurm/psi" and (("/pnfs" in source_file) or ("/pnfs" in destination)):
                            manually_move_t3(source_file, destination)
                        else:
                            shutil.move(source_file, destination)
                        print("File moved successfully.")
                    except Exception as e:
                        print(f"Error moving file {source_file}: {e}")

            arguments = [
                "combine",
                f"fit_{toy}.root",
                "-m", "125.380",
                "--snapshotName", f"{config['combine_mggToys']['loadSnapshot']}",
                "-M", "GenerateOnly",
                "--saveToys",
                "--toysFrequentist",
                "--bypassFrequentistFit",
                "-t", "-1",
                "-n", f"_{toy}_throw_step"
            ]
            if self.variable == '':
                arguments.append("--setParameters")
                arguments.append("r=0")
            else:
                arguments.append("--setParameters")
                arguments.append(f"{cat}=0")
            command = arguments
            # print(command)
            try:
                result = subprocess.run(command, check=True, text=True, capture_output=True)
                print("Script output:", result.stdout)
                print("Script executed successfully.")
            except subprocess.CalledProcessError as e:
                print("Error executing script:", e.stderr)
                
            # Define the source pattern and destination path
            source_pattern = os.path.join(toy_output_dir, 'Combine', fitFolderName, 'postFit', f'SplusBModels_{cat}', 'toys', f'higgsCombine_{toy}_throw_step*.root')
            destination = os.path.join(toy_output_dir, 'Combine', fitFolderName, 'postFit', f'SplusBModels_{cat}', 'toys', f'toy_{toy}.root')

            # Use glob to find files matching the source pattern
            source_files = glob.glob(source_pattern)

            if not source_files:
                print("No files found matching the pattern.")
            else:
                # Move each matched file to the destination
                for source_file in source_files:
                    try:
                        print(f"Moving {source_file} to {destination}")
                        if self.batch_flavor == "slurm/psi" and (("/pnfs" in source_file) or ("/pnfs" in destination)):
                            manually_move_t3(source_file, destination)
                        else:
                            shutil.move(source_file, destination)
                        print("File moved successfully.")
                    except Exception as e:
                        print(f"Error moving file {source_file}: {e}")
                        
            # Define the files to remove
            files_to_remove = [os.path.join(toy_output_dir, 'Combine', fitFolderName, 'postFit', f'SplusBModels_{cat}', 'toys', f'gen_{toy}.root'), os.path.join(toy_output_dir, 'Combine', fitFolderName, 'postFit', f'SplusBModels_{cat}', 'toys', f'fit_{toy}.root')]

            # Remove each specified file
            for file_path in files_to_remove:
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        print(f"{file_path} removed successfully.")
                    else:
                        print(f"{file_path} does not exist.")
                except Exception as e:
                    print(f"Error removing file {file_path}: {e}")
            
            # Check if toy is > 1000 bytes (== file empty)
            try:
                file_size = os.path.getsize(os.path.join(toy_output_dir, 'Combine', fitFolderName, 'postFit', f'SplusBModels_{cat}', 'toys', f'toy_{toy}.root'))  # Get the file size in bytes
                if file_size > 1000:
                    with open(os.path.join(toy_output_dir, 'Combine', fitFolderName, 'postFit', f'SplusBModels_{cat}', 'toys', 'filechecker', f'toy_{toy}_ok.txt'), 'w') as f:
                        pass
            except OSError:
                # Handle the case where the file does not exist or is inaccessible
                print(f"Error creating file. Probably I/O error.")
                return False

        else:

            if self.batch_flavor == "slurm/psi":
                # Have to use /scratch/batch_username/ for slurm/psi
                if "/work" in output_dir:
                    execute_command([f'mkdir -p {output_dir}/Combine/{fitFolderName}/preFit/SplusBModels_{cat}/toys/filechecker'], shell=True)
                else:   
                    execute_command([f'xrdfs root://t3dcachedb.psi.ch:1094/ mkdir -p {output_dir}/Combine/{fitFolderName}/preFit/SplusBModels_{cat}/toys/filechecker'], shell=True)

                os.environ["TARGET_PATH"] = f"/scratch/{os.environ['USER']}/{os.environ['SLURM_JOB_ID']}"
                execute_command([f'mkdir -p $TARGET_PATH/Combine/{fitFolderName}/preFit/SplusBModels_{cat}/toys/filechecker'], shell=True)
                os.chdir(os.path.join(os.environ["TARGET_PATH"], 'Combine', fitFolderName, 'preFit', f'SplusBModels_{cat}', 'toys'))
            else:
                execute_command([f'mkdir -p {output_dir}/Combine/{fitFolderName}/preFit/SplusBModels_{cat}/toys/filechecker'], shell=True)
                os.chdir(os.path.join(output_dir, 'Combine', fitFolderName, 'preFit', f'SplusBModels_{cat}', 'toys'))

            arguments = [
                "combine",
                "-M", "GenerateOnly",
                "-d", datacard_path,
                "-m", "125.380",
                "--saveWorkspace",
                "--toysFrequentist",
                "--bypassFrequentistFit",
                "-t", "1",
                "-s", "-1",
                "-n", f"_{toy}_gen_step",
            ]
            arguments.append("--setParameters")
            if self.variable == '':
                arguments.append('r=1')
            else:
                arguments.append(f"""{",".join(combineVariableDict[f'{self.year}'][f'{self.variable}']['paramStr'])}""")
            command = arguments
            # print(command)
            try:
                result = subprocess.run(command, check=True, text=True, capture_output=True)
                print("Script output:", result.stdout)
                print("Script executed successfully.")
            except subprocess.CalledProcessError as e:
                print("Error executing script:", e.stderr)

            # Define the source pattern and destination path
            # On the PSI Tier 3 when executed with SLURM, the Toys are on the Storage Element which needs special handling
            # For this reason, introduce a "toy_output_dir" which is in the slurm/psi case the /scratch directory
            # and in the other cases the output_dir
            if self.batch_flavor == "slurm/psi" and "/pnfs" in output_dir:
                toy_output_dir = os.environ["TARGET_PATH"]
            else:
                toy_output_dir = output_dir
                
            source_pattern = os.path.join(toy_output_dir, 'Combine', fitFolderName, 'preFit', f'SplusBModels_{cat}', 'toys', f'higgsCombine_{toy}_gen_step*.root')
            destination = os.path.join(toy_output_dir, 'Combine', fitFolderName, 'preFit', f'SplusBModels_{cat}', 'toys', f'gen_{toy}.root')

            # Use glob to find files matching the source pattern
            source_files = glob.glob(source_pattern)

            if not source_files:
                print("No files found matching the pattern.")
            else:
                # Move each matched file to the destination
                for source_file in source_files:
                    try:
                        print(f"Moving {source_file} to {destination}")
                        if (self.batch_flavor == "slurm/psi") and (("/pnfs" in source_file) or ("/pnfs" in destination)):
                            manually_move_t3(source_file, destination)
                        else:
                            shutil.move(source_file, destination)
                        print("File moved successfully.")
                    except Exception as e:
                        print(f"Error moving file {source_file}: {e}")

            arguments = [
                "combine",
                f"gen_{toy}.root",
                "-m", "125.380",
                "-M", f"{config['combine_mggToys']['loadSnapshot']}",
                "-P", f"{cat}",
                "--floatOtherPOIs=1",
                "--saveWorkspace",
                "--toysFrequentist",
                "--bypassFrequentistFit",
                "-t", "1",
                "-s", "-1",
                "-n", f"_{toy}_fit_step",
                "--cminDefaultMinimizerStrategy", "0",
                "--X-rtd", "MINIMIZER_freezeDisassociatedParams",
                "--X-rtd", "MINIMIZER_multiMin_hideConstants",
                "--X-rtd", "MINIMIZER_multiMin_maskConstraints",
                "--X-rtd", "MINIMIZER_multiMin_maskChannels=2"
            ]
            arguments.append("--setParameters")
            if self.variable == '':
                arguments.append('r=1')
            else:
                arguments.append(f"""{",".join(combineVariableDict[f'{self.year}'][f'{self.variable}']['paramStr'])}""")
            command = arguments
            # print(command)
            try:
                result = subprocess.run(command, check=True, text=True, capture_output=True)
                print("Script output:", result.stdout)
                print("Script executed successfully.")
            except subprocess.CalledProcessError as e:
                print("Error executing script:", e.stderr)    
                
            # Define the source pattern and destination path
            source_pattern = os.path.join(toy_output_dir, 'Combine', fitFolderName, 'preFit', f'SplusBModels_{cat}', 'toys', f'higgsCombine_{toy}_fit_step*.root')
            destination = os.path.join(toy_output_dir, 'Combine', fitFolderName, 'preFit', f'SplusBModels_{cat}', 'toys', f'fit_{toy}.root')

            # Use glob to find files matching the source pattern
            source_files = glob.glob(source_pattern)

            if not source_files:
                print("No files found matching the pattern.")
            else:
                # Move each matched file to the destination
                for source_file in source_files:
                    try:
                        print(f"Moving {source_file} to {destination}")
                        if self.batch_flavor == "slurm/psi" and (("/pnfs" in source_file) or ("/pnfs" in destination)):
                            manually_move_t3(source_file, destination)
                        else:
                            shutil.move(source_file, destination)
                        print("File moved successfully.")
                    except Exception as e:
                        print(f"Error moving file {source_file}: {e}")
                
            arguments = [
                "combine",
                f"fit_{toy}.root",
                "-m", "125.38",
                "--snapshotName", f"{config['combine_mggToys']['loadSnapshot']}",
                "-M", "GenerateOnly",
                "--saveToys",
                "--toysFrequentist",
                "--bypassFrequentistFit",
                "-t", "-1",
                "-n", f"_{toy}_throw_step"
            ]
            arguments.append("--setParameters")
            if self.variable == '':
                arguments.append('r=0')
            else:
                arguments.append(f"""{(",".join(combineVariableDict[f'{self.year}'][f'{self.variable}']['paramStr'])).replace("=1", "=0")}""")
            command = arguments
            # print(command)
            try:
                result = subprocess.run(command, check=True, text=True, capture_output=True)
                print("Script output:", result.stdout)
                print("Script executed successfully.")
            except subprocess.CalledProcessError as e:
                print("Error executing script:", e.stderr)
                
            # Define the source pattern and destination path
            source_pattern = os.path.join(toy_output_dir, 'Combine', fitFolderName, 'preFit', f'SplusBModels_{cat}', 'toys', f'higgsCombine_{toy}_throw_step*.root')
            destination = os.path.join(toy_output_dir, 'Combine', fitFolderName, 'preFit', f'SplusBModels_{cat}', 'toys', f'toy_{toy}.root')

            # Use glob to find files matching the source pattern
            source_files = glob.glob(source_pattern)

            if not source_files:
                print("No files found matching the pattern.")
            else:
                # Move each matched file to the destination
                for source_file in source_files:
                    try:
                        print(f"Moving {source_file} to {destination}")
                        if self.batch_flavor == "slurm/psi" and (("/pnfs" in source_file) or ("/pnfs" in destination)):
                            manually_move_t3(source_file, destination)
                        else:
                            shutil.move(source_file, destination)
                        print("File moved successfully.")
                    except Exception as e:
                        print(f"Error moving file {source_file}: {e}")
                        
            # Define the files to remove
            files_to_remove = [os.path.join(toy_output_dir, 'Combine', fitFolderName, 'preFit', f'SplusBModels_{cat}', 'toys', f'gen_{toy}.root'), os.path.join(toy_output_dir, 'Combine', fitFolderName, 'preFit', f'SplusBModels_{cat}', 'toys', f'fit_{toy}.root')]

            # Remove each specified file
            for file_path in files_to_remove:
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        print(f"{file_path} removed successfully.")
                    else:
                        print(f"{file_path} does not exist.")
                except Exception as e:
                    print(f"Error removing file {file_path}: {e}")
            
            # Check if toy is > 1000 bytes (== file empty)
            try:
                file_size = os.path.getsize(os.path.join(toy_output_dir, 'Combine', fitFolderName, 'preFit', f'SplusBModels_{cat}', 'toys', f'toy_{toy}.root'))  # Get the file size in bytes
                if file_size > 1000:
                    with open(os.path.join(toy_output_dir, 'Combine', fitFolderName, 'preFit', f'SplusBModels_{cat}', 'toys', 'filechecker', f'toy_{toy}_ok.txt'), 'w') as f:
                        pass
            except OSError:
                # Handle the case where the file does not exist or is inaccessible
                print(f"Error creating file. Probably I/O error.")
                return False

        # Copy the files back to pnfs if we are on slurm/psi
        if self.batch_flavor == "slurm/psi":
            # Have to copy over the output to the final directory
            # Don't forget to VOMS!
            if "/work" in output_dir:
                slurm_copy_command = [
                    'cp', '-rf',
                    f"{os.environ['TARGET_PATH']}/Combine/",
                    output_dir
                ]
            else:
                slurm_copy_command = [
                    'xrdcp', '-rf',
                    f"{os.environ['TARGET_PATH']}/Combine/",
                    'root://t3dcachedb.psi.ch:1094//'+output_dir
                ]
            print(slurm_copy_command)
            execute_command(slurm_copy_command)
            # Clean up the temporary directory
            shutil.rmtree(os.environ["TARGET_PATH"])
        
        os.chdir(cwd)
        
class MggDistribution(Task, SlurmWorkflow, HTCondorWorkflow, law.LocalWorkflow): #(law.Task): #(Task, HTCondorWorkflow, law.LocalWorkflow):
    output_dir = law.Parameter(default = '', description="Path to the output directory")
    variable = law.Parameter(default="", description="Variable to be used")
    year = law.Parameter(default='2022', description="Year")
    is_postfit = law.Parameter(default=False, description="Flag that signifies if toys are created for postfit mass distributions.")

    batch_flavor = law.Parameter(default="htcondor", description="Batch system to use")

    # def requires(self):
    def workflow_requires(self):
        workflow_reqs = super().workflow_requires()

        tasks = {}

        if workflow_reqs:
            tasks.update(workflow_reqs)
        
        if self.variable == '':
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_inclusive.yml")
        else:
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_{self.variable}.yml")
        
        #Load central config file
        with open(configYamlPath, 'r') as file:
            config = yaml.safe_load(file)
        
        mggConfig = config['combine_mggToys']
        
        if self.output_dir == '':
            output_dir = config['outputFolder']
        else:
            output_dir = self.output_dir
        
        if config['combine_mggToys']['doBands']:
            if convert_boolean_string(self.is_postfit):
                tasks["MggToyGeneration"] = MggToyGeneration(output_dir=output_dir, variable=self.variable, year=self.year, is_postfit=convert_boolean_string(self.is_postfit), batch_flavor=self.batch_flavor, version=f"{self.variable if self.variable != '' else 'r'}_postfit", workflow=mggConfig["execution"], slurm_partition=mggConfig['batchPartition'], slurm_memory=mggConfig['batchMemory'], slurm_max_runtime=mggConfig['batchMaxRuntime'], htcondor_partition=mggConfig['batchPartition'], htcondor_memory=mggConfig['batchMemory'], htcondor_max_runtime=mggConfig['batchMaxRuntime'])
            else:
                tasks["MggToyGeneration"] = MggToyGeneration(output_dir=output_dir, variable=self.variable, year=self.year, is_postfit=convert_boolean_string(self.is_postfit), batch_flavor=self.batch_flavor, version=f"{self.variable if self.variable != '' else 'r'}_prefit", workflow=mggConfig["execution"], slurm_partition=mggConfig['batchPartition'], slurm_memory=mggConfig['batchMemory'], slurm_max_runtime=mggConfig['batchMaxRuntime'], htcondor_partition=mggConfig['batchPartition'], htcondor_memory=mggConfig['batchMemory'], htcondor_max_runtime=mggConfig['batchMaxRuntime'])
        else:
            if convert_boolean_string(self.is_postfit):
                fitConfig = config["combine_fit"]
                tasks["CreateUnblindedFit"] = CreateUnblindedFit(output_dir=output_dir, variable=self.variable, year=self.year, batch_flavor=self.batch_flavor, version=f"{self.variable if self.variable != '' else 'r'}_prefit", workflow=fitConfig["execution"], slurm_partition=fitConfig['batchPartition'], slurm_memory=fitConfig['batchMemory'], slurm_max_runtime=fitConfig['batchMaxRuntime'], htcondor_partition=fitConfig['batchPartition'], htcondor_memory=fitConfig['batchMemory'], htcondor_max_runtime=fitConfig['batchMaxRuntime'])
            else:
                tasks["RunT2WS"] = RunText2Workspace(output_dir=output_dir, variable=self.variable, year=self.year, version=self.variable if self.variable != "" else "inclusive", workflow=mggConfig["execution"], batch_flavor=self.batch_flavor, slurm_partition=mggConfig['batchPartition'], slurm_memory=mggConfig['batchMemory'], slurm_max_runtime=mggConfig['batchMaxRuntime'], htcondor_partition=mggConfig['batchPartition'], htcondor_memory=mggConfig['batchMemory'], htcondor_max_runtime=mggConfig['batchMaxRuntime'])
        
        return tasks

    def create_branch_map(self):
        if self.variable == '':
            cat_list = ["r"]
        else:
            cat_list = combineVariableDict[f'{self.year}'][f'{self.variable}']['paramStrNoOne']
        branch_map = {i: cat for i, cat in enumerate(cat_list)}
        return branch_map

    def output(self):
        cat = self.branch_data
        
        if self.variable == '':
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_inclusive.yml")
        else:
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_{self.variable}.yml")

        #Load central config file
        with open(configYamlPath, 'r') as file:
            config = yaml.safe_load(file)

        if self.output_dir == '':
            output_dir = config['outputFolder']
        else:
            output_dir = self.output_dir

        if self.variable == '':
            fitFolderName = f'runFits_mu_fiducial'
            reco_cats_with_bmw = ['best_resolution', 'medium_resolution', 'worst_resolution']
        else:
            fitFolderName = f'runFits_{self.variable}'
            reco_cats_with_bmw = [element for element in combineVariableDict[f'{self.year}'][self.variable]['catsStrWithBMW'] if "_".join(cat.split("_")[2:]) in element]
            
        
        output = []
        if convert_boolean_string(self.is_postfit):
            output += [os.path.join(output_dir, 'Combine', fitFolderName, 'postFit', 'jsons')]
            output += [os.path.join(output_dir, 'Combine', fitFolderName, 'postFit', 'jsons', f'catsWeights_sospb_{cat}_CMS_hgg_mass.json')]
            
            output += [os.path.join(output_dir, 'Combine', fitFolderName, 'postFit', f'SplusBModels_{cat}', f'_{cat}_{catWithBMW}_CMS_hgg_mass.pdf') for catWithBMW in reco_cats_with_bmw]
            output += [os.path.join(output_dir, 'Combine', fitFolderName, 'postFit', f'SplusBModels_{cat}', f'_{cat}_{catWithBMW}_CMS_hgg_mass.png') for catWithBMW in reco_cats_with_bmw]
            output += [os.path.join(output_dir, 'Combine', fitFolderName, 'postFit', f'SplusBModels_{cat}', f'_{cat}_all_CMS_hgg_mass.pdf')]
            output += [os.path.join(output_dir, 'Combine', fitFolderName, 'postFit', f'SplusBModels_{cat}', f'_{cat}_all_CMS_hgg_mass.png')]
            output += [os.path.join(output_dir, 'Combine', fitFolderName, 'postFit', f'SplusBModels_{cat}', f'_{cat}_wall_CMS_hgg_mass.pdf')]
            output += [os.path.join(output_dir, 'Combine', fitFolderName, 'postFit', f'SplusBModels_{cat}', f'_{cat}_wall_CMS_hgg_mass.png')]
        else:
            output += [os.path.join(output_dir, 'Combine', fitFolderName, 'preFit', 'jsons')]
            output += [os.path.join(output_dir, 'Combine', fitFolderName, 'preFit', 'jsons', f'catsWeights_sospb_{cat}_CMS_hgg_mass.json')]
            
            output += [os.path.join(output_dir, 'Combine', fitFolderName, 'preFit', f'SplusBModels_{cat}', f'_{cat}_{catWithBMW}_CMS_hgg_mass.pdf') for catWithBMW in reco_cats_with_bmw]
            output += [os.path.join(output_dir, 'Combine', fitFolderName, 'preFit', f'SplusBModels_{cat}', f'_{cat}_{catWithBMW}_CMS_hgg_mass.png') for catWithBMW in reco_cats_with_bmw]
            output += [os.path.join(output_dir, 'Combine', fitFolderName, 'preFit', f'SplusBModels_{cat}', f'_{cat}_all_CMS_hgg_mass.pdf')]
            output += [os.path.join(output_dir, 'Combine', fitFolderName, 'preFit', f'SplusBModels_{cat}', f'_{cat}_all_CMS_hgg_mass.png')]
            output += [os.path.join(output_dir, 'Combine', fitFolderName, 'preFit', f'SplusBModels_{cat}', f'_{cat}_wall_CMS_hgg_mass.pdf')]
            output += [os.path.join(output_dir, 'Combine', fitFolderName, 'preFit', f'SplusBModels_{cat}', f'_{cat}_wall_CMS_hgg_mass.png')]
                
        
        outputFileTargets = []
                
        for _, current_output_path in enumerate(output):
            outputFileTargets.append(law.LocalFileTarget(current_output_path))
            
        # print(outputFileTargets)

        return outputFileTargets

    def run(self):
        cat = self.branch_data
       
        if self.variable == '':
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_inclusive.yml")
            fitFolderName = f'runFits_mu_fiducial'

        else:
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_{self.variable}.yml")
            fitFolderName = f'runFits_{self.variable}'

        #Load central config file
        with open(configYamlPath, 'r') as file:
            config = yaml.safe_load(file)

        if self.output_dir == '':
            output_dir = config['outputFolder']
        else:
            output_dir = self.output_dir  
            
        main_dir = os.getcwd()
        
        if convert_boolean_string(self.is_postfit):

            if self.batch_flavor == "slurm/psi":
                # Have to use /scratch/batch_username/ for slurm/psi
                if "/work" in output_dir:
                    execute_command([f'mkdir -p {output_dir}/Combine/{fitFolderName}/postFit/SplusBModels_{cat}/'], shell=True)
                else:   
                    execute_command([f'xrdfs root://t3dcachedb.psi.ch:1094/ mkdir -p {output_dir}/Combine/{fitFolderName}/postFit/SplusBModels_{cat}/'], shell=True)

                os.environ["TARGET_PATH"] = f"/scratch/{os.environ['USER']}/{os.environ['SLURM_JOB_ID']}"
                execute_command([f'mkdir -p $TARGET_PATH/Combine/{fitFolderName}/postFit/SplusBModels_{cat}/'], shell=True)
                
                if "/work" in output_dir:
                    slurm_copy_command = [
                        'cp', '-rf',
                        f'{output_dir}/Combine/{fitFolderName}/postFit/SplusBModels_{cat}/toys',
                        f'{os.environ["TARGET_PATH"]}/Combine/{fitFolderName}/postFit/SplusBModels_{cat}/'
                    ]
                else:
                    slurm_copy_command = [
                        'xrdcp', '-rf',
                        'root://t3dcachedb.psi.ch:1094//'+ f'{output_dir}/Combine/{fitFolderName}/postFit/SplusBModels_{cat}/toys',
                        f'{os.environ["TARGET_PATH"]}/Combine/{fitFolderName}/postFit/SplusBModels_{cat}/'
                    ]
                execute_command(slurm_copy_command)
                os.chdir(os.path.join(os.environ["TARGET_PATH"], 'Combine', fitFolderName, 'postFit'))
            else:
                execute_command([f'mkdir -p {output_dir}/Combine/{fitFolderName}/postFit/SplusBModels_{cat}/'], shell=True)
                os.chdir(os.path.join(output_dir, 'Combine', fitFolderName, 'postFit'))
            
            best_fit = os.path.join(output_dir, 'Combine', fitFolderName, 'postFit', f'SplusBModels_{cat}', f'higgsCombine_bestfit_syst_obs_{cat}.MultiDimFit.mH125.38.root')
            
            if self.variable == '':
                # firstStep_path = os.path.join(output_dir, 'Combine', f'Datacard_{self.year}.root')
                reco_cats_with_bmw = ['best_resolution', 'medium_resolution', 'worst_resolution']
            else:
                # firstStep_path = os.path.join(output_dir, 'Combine', fitFolderName, 'dataFit', f'higgsCombineDataPostFitScanFit_{cat}.MultiDimFit.mH125.38.root')
                reco_cats_with_bmw = [element for element in combineVariableDict[f'{self.year}'][self.variable]['catsStrWithBMW'] if "_".join(cat.split("_")[2:]) in element]

            arguments = [
                "python3",
                f"{os.path.join(os.environ['ANALYSIS_PATH'], 'Plots', 'makeSplusBModelPlot.py')}",
                "--inputWSFile", best_fit,
                "--loadSnapshot", f"{config['combine_mggToys']['loadSnapshot']}",
                "--cats", f"{','.join(reco_cats_with_bmw)}",
                "--doZeroes",
                "--unblind",
                "--translateCats", f"{os.path.join(os.environ['ANALYSIS_PATH'], 'Plots', 'cats.json')}",
                "--doSumCategories",
                "--doCatWeights",
                "--saveWeights",
                "--ext", f"_{cat}",
                "--POI", f"{cat}"
            ]
            if config['combine_mggToys']['doBands']:
                arguments.append("--doBands")
                arguments.append("--doToyVeto")
                arguments.append("--saveToyYields")
            command = arguments
            print(command)
            try:
                result = subprocess.run(command, check=True, text=True, capture_output=True)
                print("Script output:", result.stdout)
                print("Script executed successfully.")
            except subprocess.CalledProcessError as e:
                print("Error executing script:", e.stderr)
            
            # Change directory
            # os.chdir(f"./SplusBModels_{cat}")

            # if self.variable != "":
            #     # Extract parts from the parameter
            #     parts = cat.split('_')
            #     pattern = f"{parts[2]}_{parts[3]}"

            #     # Define source and target directories
            #     source_dir = "."
            #     target_dir = "../Plots"

            #     # Iterate over files in the source directory
            #     for filename in os.listdir(source_dir):
            #         # Check if the pattern is in the filename
            #         if pattern in filename:
            #             # Construct full source and destination paths
            #             source_path = os.path.join(source_dir, filename)
            #             target_path = os.path.join(target_dir, filename)
            #             # Copy the file to the target directory
            #             shutil.copy(source_path, target_path)
            #             print(f"Copied {filename} to {target_dir}")

            # Go back one directory
            os.chdir("..")
            
        else: 
            
            if self.batch_flavor == "slurm/psi":
                # Have to use /scratch/batch_username/ for slurm/psi
                if "/work" in output_dir:
                    execute_command([f'mkdir -p {output_dir}/Combine/{fitFolderName}/preFit/SplusBModels_{cat}/'], shell=True)
                else:   
                    execute_command([f'xrdfs root://t3dcachedb.psi.ch:1094/ mkdir -p {output_dir}/Combine/{fitFolderName}/preFit/SplusBModels_{cat}/'], shell=True)
                os.environ["TARGET_PATH"] = f"/scratch/{os.environ['USER']}/{os.environ['SLURM_JOB_ID']}"
                execute_command([f'mkdir -p $TARGET_PATH/Combine/{fitFolderName}/preFit/SplusBModels_{cat}/'], shell=True)

                if "/work" in output_dir:
                    slurm_copy_command = [
                        'cp', '-rf',
                        f'{output_dir}/Combine/{fitFolderName}/preFit/SplusBModels_{cat}/toys',
                        f'{os.environ["TARGET_PATH"]}/Combine/{fitFolderName}/preFit/SplusBModels_{cat}/'
                    ]
                else:
                    slurm_copy_command = [
                        'xrdcp', '-rf',
                        'root://t3dcachedb.psi.ch:1094//'+ f'{output_dir}/Combine/{fitFolderName}/preFit/SplusBModels_{cat}/toys',
                        f'{os.environ["TARGET_PATH"]}/Combine/{fitFolderName}/preFit/SplusBModels_{cat}/'
                    ]
                execute_command(slurm_copy_command)
                os.chdir(os.path.join(os.environ["TARGET_PATH"], 'Combine', fitFolderName, 'preFit'))
            else:
                execute_command([f'mkdir -p {output_dir}/Combine/{fitFolderName}/preFit/SplusBModels_{cat}/'], shell=True)
                os.chdir(os.path.join(output_dir, 'Combine', fitFolderName, 'preFit'))
            
            if self.variable == '':
                datacard_path = os.path.join(output_dir, 'Combine', f'Datacard_{self.year}.root')
            else:
                datacard_path = os.path.join(output_dir, 'Combine', f'Datacard_{self.variable}_{self.year}.root')
                
            if self.variable == '':
                reco_cats_with_bmw = ['best_resolution', 'medium_resolution', 'worst_resolution']
            else:
                reco_cats_with_bmw = [element for element in combineVariableDict[f'{self.year}'][self.variable]['catsStrWithBMW'] if "_".join(cat.split("_")[2:]) in element]
                
            arguments = [
                "python3",
                f"{os.path.join(os.environ['ANALYSIS_PATH'], 'Plots', 'makeSplusBModelPlot.py')}",
                "--inputWSFile", datacard_path,
                "--cats", f"{','.join(reco_cats_with_bmw)}",
                "--doZeroes",
                "--blindingRegion", "125,125",
                "--translateCats", f"{os.path.join(os.environ['ANALYSIS_PATH'], 'Plots', 'cats.json')}",
                "--doSumCategories",
                "--doCatWeights",
                "--saveWeights",
                "--ext", f"_{cat}",
                "--POI", f"{cat}"
            ]
            if config['combine_mggToys']['doBands']:
                arguments.append("--doBands")
                arguments.append("--doToyVeto")
                arguments.append("--saveToyYields")
            command = arguments
            print(command)
            try:
                result = subprocess.run(command, check=True, text=True, capture_output=True)
                print("Script output:", result.stdout)
                print("Script executed successfully.")
            except subprocess.CalledProcessError as e:
                print("Error executing script:", e.stderr)

        # Copy the files back to pnfs if we are on slurm/psi
        if self.batch_flavor == "slurm/psi":
            # Have to copy over the output to the final directory
            # Don't forget to VOMS!
            if "/work" in output_dir:
                slurm_copy_command = [
                    'cp', '-rf',
                    f"{os.environ['TARGET_PATH']}/Combine/",
                    output_dir
                ]
            else:
                slurm_copy_command = [
                    'xrdcp', '-rf',
                    f"{os.environ['TARGET_PATH']}/Combine/",
                    'root://t3dcachedb.psi.ch:1094//'+output_dir
                ]
            print(slurm_copy_command)
            execute_command(slurm_copy_command)
            # Clean up the temporary directory
            shutil.rmtree(os.environ["TARGET_PATH"])

        os.chdir(main_dir)
        
        
class PValueCalculation(Task, SlurmWorkflow, HTCondorWorkflow, law.LocalWorkflow): #(law.Task): #(Task, HTCondorWorkflow, law.LocalWorkflow):
    output_dir = law.Parameter(default = '', description="Path to the output directory")
    variable = law.Parameter(default="", description="Variable to be used")
    year = law.Parameter(default='2022', description="Year")

    batch_flavor = law.Parameter(default="htcondor", description="Batch system to use")

    # def requires(self):
    def workflow_requires(self):
        workflow_reqs = super().workflow_requires()

        tasks = {}

        if workflow_reqs:
            tasks.update(workflow_reqs)
        
        if self.variable == '':
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_inclusive.yml")
        else:
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_{self.variable}.yml")
        
        #Load central config file
        with open(configYamlPath, 'r') as file:
            config = yaml.safe_load(file)
        
        if self.output_dir == '':
            output_dir = config['outputFolder']
        else:
            output_dir = self.output_dir
        
        fitConfig = config["combine_fit"]
        tasks["CreateUnblindedFit"] = CreateUnblindedFit(output_dir=output_dir, variable=self.variable, year=self.year, batch_flavor=self.batch_flavor, version=f"{self.variable if self.variable != '' else 'inclusive'}", workflow=fitConfig["execution"], slurm_partition=fitConfig['batchPartition'], slurm_memory=fitConfig['batchMemory'], slurm_max_runtime=fitConfig['batchMaxRuntime'], htcondor_partition=fitConfig['batchPartition'], htcondor_memory=fitConfig['batchMemory'], htcondor_max_runtime=fitConfig['batchMaxRuntime'])
        
        return tasks

    def create_branch_map(self):
        # if self.variable == '':
        #     cat_list = ["r"]
        # else:
        #     cat_list = combineVariableDict[f'{self.year}'][f'{self.variable}']['paramStrNoOne']
        # branch_map = {i: cat for i, cat in enumerate(cat_list)}
        branch_map = {i: value for i, value in enumerate([0])}
        return branch_map

    def output(self):
        
        if self.variable == '':
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_inclusive.yml")
        else:
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_{self.variable}.yml")
        
        #Load central config file
        with open(configYamlPath, 'r') as file:
            config = yaml.safe_load(file)
        
        if self.output_dir == '':
            output_dir = config['outputFolder']
        else:
            output_dir = self.output_dir

        if self.variable == '':
            fitFolderName = f'runFits_mu_fiducial'
            output = []
        else:
            fitFolderName = f'runFits_{self.variable}'
            output = [os.path.join(output_dir, 'Combine', fitFolderName, 'dataFit', f'higgsCombine.pvalue.MultiDimFit.mH125.38.root')]
            output += [os.path.join(output_dir, 'Combine', fitFolderName, f'pvalue.txt')]

        outputFileTargets = []
                
        for _, current_output_path in enumerate(output):
            outputFileTargets.append(law.LocalFileTarget(current_output_path))
            
        # print(outputFileTargets)

        return outputFileTargets
    
    def run(self):
       
        if self.variable == '':
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_inclusive.yml")
            fitFolderName = f'runFits_mu_fiducial'

        else:
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"],"config",f"{self.year}_{self.variable}.yml")
            fitFolderName = f'runFits_{self.variable}'

        #Load central config file
        with open(configYamlPath, 'r') as file:
            config = yaml.safe_load(file)

        if self.output_dir == '':
            output_dir = config['outputFolder']
        else:
            output_dir = self.output_dir  
            
        cwd = os.getcwd()
        if self.batch_flavor == "slurm/psi":
            # Have to use /scratch/batch_username/ for slurm/psi
            if "/work" in output_dir:
                execute_command([f'mkdir -p {output_dir}/Combine/{fitFolderName}/dataFit'], shell=True)
            else:   
                execute_command([f'xrdfs root://t3dcachedb.psi.ch:1094/ mkdir -p {output_dir}/Combine/{fitFolderName}/dataFit'], shell=True)

            os.environ["TARGET_PATH"] = f"/scratch/{os.environ['USER']}/{os.environ['SLURM_JOB_ID']}"
            execute_command([f'mkdir -p $TARGET_PATH/Combine/{fitFolderName}/dataFit'], shell=True)
            os.chdir(os.path.join(os.environ["TARGET_PATH"], 'Combine', fitFolderName, 'dataFit'))
            temp_output_dir = os.environ["TARGET_PATH"]
        else:
            execute_command([f'mkdir -p {output_dir}/Combine/{fitFolderName}/dataFit'], shell=True)
            os.chdir(os.path.join(output_dir, 'Combine', fitFolderName, 'dataFit'))
            temp_output_dir = output_dir
                    
        # Define the file to check
        pvalue_file = os.path.join(temp_output_dir, 'Combine', fitFolderName, 'dataFit', f'higgsCombine.pvalue.MultiDimFit.mH125.38.root')

        # Check if the file exists
        if not os.path.isfile(pvalue_file):
            print("The pvalue file does not exist in the current directory. Creating it...")
            # Iterate over the parameters
            command = [
                "combine",
                "-M", "MultiDimFit",
                os.path.join(output_dir, 'Combine', fitFolderName, 'dataFit', f"higgsCombineDataPostFitScanFit_{combineVariableDict[f'{self.year}'][f'{self.variable}']['paramStrNoOne'][0]}.MultiDimFit.mH125.38.root"),
                "--algo", "fixed",
                "--X-rtd", "MINIMIZER_freezeDisassociatedParams",
                "--X-rtd", "MINIMIZER_multiMin_hideConstants",
                "--X-rtd", "MINIMIZER_multiMin_maskConstraints",
                "--X-rtd", "MINIMIZER_multiMin_maskChannels=2",
                "--freezeParameters", "MH",
                "--fixedPointPOIs", f"{','.join(combineVariableDict[f'{self.year}'][f'{self.variable}']['paramStr'])},MH=125.38",
                "-n", ".pvalue",
                "-m", "125.38",
                "--saveWorkspace"
            ]
            # print(command)
            try:
                result = subprocess.run(command, check=True, text=True, capture_output=True)
                print("Script output:", result.stdout)
                print("Script executed successfully.")
            except subprocess.CalledProcessError as e:
                print("Error executing script:", e.stderr)
        else:
            print("The pvalue file exists in the current directory. Skipping the creation.")
            
        # Define variables
        file_path = os.path.realpath(pvalue_file)


        # Count the number of elements in paramStrNoOne
        n_bins = len(combineVariableDict[f'{self.year}'][f'{self.variable}']['paramStrNoOne'])

        # Change directory to the fitFolderName
        os.chdir("../")

        def calculate_pvalue(filename, n_bins):
            """
            Function to calculate the p-value given a ROOT file and number of bins.
            """
            try:
                # Open the ROOT file and read the deltaNLL values
                nll_data = uproot.open(filename)["limit"].arrays()
                nll = nll_data['deltaNLL'][1]  # Extract the second value in deltaNLL array

                # Compute the p-value
                chi2pdf = chi2(n_bins)
                pval = 1 - chi2pdf.cdf(2 * nll)

                return pval
            except Exception as e:
                print(f"Error while calculating p-value: {e}")
                return None
        # Calculate the p-value
        pvalue = calculate_pvalue(file_path, n_bins)
        
        # Rounding to two significant digits
        pvalue = round(pvalue, 2 - int(f"{pvalue:.1e}".split('e')[1]) - 1)

        if pvalue is not None:
            # Define your differential variable for printing
            output_file = "pvalue.txt"
            try:
                with open(output_file, "w") as f:
                    f.write(f"{pvalue}")
                print(f"P-value written to {output_file}")
            except Exception as e:
                print(f"Error writing to file: {e}")
            print(f"The p-value of the variable {self.variable} is: {pvalue}")
        else:
            print("Failed to calculate the p-value.")

        # Copy the files back to pnfs if we are on slurm/psi
        if self.batch_flavor == "slurm/psi":
            # Have to copy over the output to the final directory
            # Don't forget to VOMS!
            if "/work" in output_dir:
                slurm_copy_command = [
                    'cp', '-rf',
                    f"{os.environ['TARGET_PATH']}/Combine/",
                    output_dir
                ]
            else:
                slurm_copy_command = [
                    'xrdcp', '-rf',
                    f"{os.environ['TARGET_PATH']}/Combine/",
                    'root://t3dcachedb.psi.ch:1094//'+output_dir
                ]
            print(slurm_copy_command)
            execute_command(slurm_copy_command)
            # Clean up the temporary directory
            shutil.rmtree(os.environ["TARGET_PATH"])

        os.chdir(cwd)
