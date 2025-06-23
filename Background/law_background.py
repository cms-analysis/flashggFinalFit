import law
import os
import subprocess
import glob
import yaml
import errno
import subprocess
import shutil

from commonTools import *
from commonObjects import *

from Trees2WS.law_trees2ws_data import *

from framework import Task
from framework import HTCondorWorkflow, SlurmWorkflow

# Function to safely create a directory
def safe_mkdir(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

def execute_command(command, return_output=False, shell=False):
    try:
        result = subprocess.run(command, check=True, text=True, capture_output=True, shell=shell, env=os.environ)
        print("Script output:", result.stdout)
        print("Script executed successfully.")
        if return_output:
            return (result.stdout).split("\n")[0]
    except subprocess.CalledProcessError as e:
        print("Error executing script:", e.stderr)

class BackgroundCategory(Task, HTCondorWorkflow, SlurmWorkflow, law.LocalWorkflow):#(law.Task): #(Task, HTCondorWorkflow, law.LocalWorkflow):
    input_path = law.Parameter(description="Path to the alldata input ROOT file")
    output_dir = law.Parameter(description="Path to the output directory")
    ext = law.Parameter(default="earlyAnalysis", description="Extension to be used for output folder naming")
    year = law.Parameter(default='2022', description="Year")
    cats = law.Parameter(description="List of categories separated by a comma.")
    cat_offset = law.Parameter(description="Category offset")
    variable = law.Parameter(default="", description="Variable to be used")

    batch_flavor = law.Parameter(default="htcondor", description="Batch system to use")

    htcondor_job_kwargs_submit = {"spool": True}
    
    def requires(self):
        
        if self.variable == '':
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"], f"config/{self.year}_inclusive.yml")
        else:
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"], f"config/{self.year}_{self.variable}.yml")
        
        #Load central config file
        with open(configYamlPath, 'r') as file:
            config = yaml.safe_load(file)
        
        if self.output_dir == '':
            output_dir = config['outputFolder']
        else:
            output_dir = self.output_dir
            
        tasks = [Trees2WSData(output_dir=output_dir, variable=self.variable, year=self.year, version='v1', workflow='local', batch_flavor=self.batch_flavor)]
        
        return tasks
    
    def create_branch_map(self):
        # map branch indexes to ascii numbers from 97 to 122 ("a" to "z")
        nCats = len(self.cats.split(","))
              
        cat_list = [
            (self.cats.split(",")[categoryIndex], str(int(self.cat_offset)+categoryIndex))
            for categoryIndex in range(nCats)
        ]        
        branch_map = {i: cat_catOffset for i, cat_catOffset in enumerate(cat_list)}
        return branch_map

    def output(self):
        cat, cat_offset = self.branch_data
        outdir_ext = os.path.join(self.output_dir, 'Background', f'outdir_{self.ext}')

        
        outputFileTargets = []
        
        bkg_plots = glob.glob(os.path.join(outdir_ext, f'bkgfTest-Data/*_cat{cat_offset}.png'))
        bkg_plots += glob.glob(os.path.join(outdir_ext, f'bkgfTest-Data/*_cat{cat_offset}.pdf'))
        bkg_plots += glob.glob(os.path.join(outdir_ext, f'bkgfTest-Data/*_cat{cat_offset}.pdf_gofTest.pdf'))
    
        output_paths = [os.path.join(outdir_ext, f'CMS-HGG_multipdf_{cat}.root'), os.path.join(outdir_ext, f'bkgfTest-Data/multipdf_{cat}.pdf'), os.path.join(outdir_ext, f'bkgfTest-Data/multipdf_{cat}.png')]
        
        output_paths += bkg_plots

   
        for _, current_output_path in enumerate(output_paths):
            outputFileTargets.append(law.LocalFileTarget(current_output_path))

        return outputFileTargets

    def run(self):
        cat, cat_offset = self.branch_data
        input_path = self.input_path
        
        if self.batch_flavor == "slurm/psi":
            # Have to use /scratch/batch_username/ for slurm/psi
            os.environ["TARGET_PATH"] = f"/scratch/{os.environ['USER']}/{os.environ['SLURM_JOB_ID']}"
            temp_output_dir = os.environ["TARGET_PATH"]
            execute_command([f'xrdfs root://t3dcachedb.psi.ch:1094/ mkdir -p {self.output_dir}/Background'], shell=True)
            execute_command([f'xrdfs root://t3dcachedb.psi.ch:1094/ mkdir -p {self.output_dir}/Background/outdir_{self.ext}'], shell=True)
            safe_mkdir(temp_output_dir)
        else:
            temp_output_dir = self.output_dir
            safe_mkdir(temp_output_dir)
        
        if temp_output_dir[-1] != "/":
            temp_output_dir += "/"

        script_path = os.path.join(os.environ["ANALYSIS_PATH"], "Background/runBackgroundScripts.sh")
        arguments = [
            "-i", input_path,
            "-p", "none",
            "-f", cat,
            "--outputFolder", f"{temp_output_dir}",
            "--ext", f'{self.ext}',
            "--catOffset", cat_offset,
            "--intLumi", f"{lumiMap[self.year]}",
            "--year", f"{self.year}",
            "--batch", "local",
            "--queue", "microcentury",
            "--sigFile", "none",
            "--isData",
            "--fTest"
        ]
        command = [script_path] + arguments
        # print("Output:", command)
        
        # Move to background folder
        original_dir = os.getcwd()
        os.chdir(os.path.join(os.environ["ANALYSIS_PATH"], "Background"))
        try:
            result = subprocess.run(command, check=True, text=True, capture_output=True)
            print("Script output:", result.stdout)
            print("Script executed successfully.")
        except subprocess.CalledProcessError as e:
            print("Error executing script:", e.stderr)
        os.chdir(original_dir)

        if self.batch_flavor == "slurm/psi":
            bkg_folder = f"outdir_{self.ext}"
            execute_command([f"ls -al {temp_output_dir}/*"], shell=True)
            if "/work" in self.output_dir:
                slurm_copy_command = [
                    'cp', '-rf',
                    f'{temp_output_dir}/{bkg_folder}',
                     f'{self.output_dir}/Background/'
                ]
            else:
                # Copying output files to final destination on the /pnfs.
                slurm_copy_command = [
                    'xrdcp', '-rf',
                    f'{temp_output_dir}/{bkg_folder}',
                    'root://t3dcachedb.psi.ch:1094//'+ f'{self.output_dir}/Background/'
                ]
            execute_command(slurm_copy_command)
            # Cleaning up scratch space.
            shutil.rmtree(temp_output_dir)
        
        

class Background(law.Task):
    variable = law.Parameter(default="", description="Variable to be used")
    output_dir = law.Parameter(default = '', description="Path to the output directory")
    year = law.Parameter(default='2022', description="Year")

    batch_flavor = law.Parameter(default="htcondor", description="Batch system to use")
    
    def requires(self):
        # req() is defined on all tasks and handles the passing of all parameter values that are
        # common between the required task and the instance (self)
        
        if self.variable == '':
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"], f"config/{self.year}_inclusive.yml")
        else:
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"], f"config/{self.year}_{self.variable}.yml")
        
        #Load central config file
        with open(configYamlPath, 'r') as file:
            config = yaml.safe_load(file)
        
        if self.output_dir == '':
            output_dir = config['outputFolder']
        else:
            output_dir = self.output_dir
            
        
        input_path = config['inputFiles']['Trees2WSData']
                    
        config = config["backgroundScriptCfg"]
        
        if config['cats'] == 'auto':
            config['cats'] = (extractListOfCatsFromHiggsDNAAllData(input_path))
        config['nCats'] = len(config['cats'].split(","))
    
        # Add dummy entries for procs and signalFitWSFile (used in old plotting script)
        config['signalFitWSFile'] = 'none'
        config['procs'] = 'none'
        config['batch'] = 'local'
        config['queue'] = 'none'
        if self.year == 'combined': config['year'] = 'all'
        else: config['year'] = self.year     
        config['intLumi'] = lumiMap[self.year]
                
        if self.variable == '':
            all_data_input_path = os.path.join(output_dir, "input_output_data", f"input_output_data_{self.year}/ws/allData.root")
        else:
            all_data_input_path = os.path.join(output_dir, "input_output_data", f"input_output_data_{self.variable}_{self.year}/ws/allData.root")
            
        tasks = [BackgroundCategory(input_path=all_data_input_path, output_dir=output_dir, year=self.year, cats=config['cats'], cat_offset=config['catOffset'], variable=self.variable, ext=config['ext'], version='v1', workflow=config['execution'], batch_flavor=self.batch_flavor, slurm_partition="short", slurm_max_runtime=1)]
        return tasks

    def output(self):
        # returns output folder
        
        if self.variable == '':
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"], f"config/{self.year}_inclusive.yml")
        else:
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"], f"config/{self.year}_{self.variable}.yml")
        
        #Load central config file
        with open(configYamlPath, 'r') as file:
            config = yaml.safe_load(file)
            
        if self.output_dir == '':
            output_dir = config['outputFolder']
        else:
            output_dir = self.output_dir
            
        config = config["backgroundScriptCfg"]
        ext=config['ext']
        
        output_paths = []

        if self.variable == '': 
            output_paths.append(law.LocalFileTarget(os.path.join(output_dir, "Background", f"outdir_{ext}")))
            
            output_paths.append(law.LocalFileTarget(os.path.join(output_dir, "Background", f'outdir_{ext}/bkgfTest-Data/fTestResults.txt')))
        else:
            output_paths.append(law.LocalFileTarget(os.path.join(output_dir, "Background", f"outdir_{ext}_{self.variable}")))
            
            output_paths.append(law.LocalFileTarget(os.path.join(output_dir, "Background", f'outdir_{ext}_{self.variable}/bkgfTest-Data/fTestResults.txt')))
                        
        return output_paths
                
    
    def run(self):
        
        return True


class OneBackground(Task, HTCondorWorkflow, SlurmWorkflow, law.LocalWorkflow):#(law.Task): #(Task, HTCondorWorkflow, law.LocalWorkflow):
    output_dir = law.Parameter(default="", description="Path to the output directory")
    year = law.Parameter(default='2022', description="Year")
    variable = law.Parameter(default="", description="Variable to be used")

    batch_flavor = law.Parameter(default="htcondor", description="Batch system to use")

    htcondor_job_kwargs_submit = {"spool": True}
    
    def requires(self):
        
        if self.variable == '':
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"], f"config/{self.year}_inclusive.yml")
        else:
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"], f"config/{self.year}_{self.variable}.yml")
        
        #Load central config file
        with open(configYamlPath, 'r') as file:
            config = yaml.safe_load(file)
        
        if self.output_dir == '':
            output_dir = config['outputFolder']
        else:
            output_dir = self.output_dir
            
        tasks = [Trees2WSData(output_dir=output_dir, variable=self.variable, year=self.year, version='v1', workflow='local', batch_flavor=self.batch_flavor)]
        
        return tasks
    
    def create_branch_map(self):
        # Creating a branch map for the categories
        if self.variable == '':
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"], f"config/{self.year}_inclusive.yml")
        else:
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"], f"config/{self.year}_{self.variable}.yml")
        
        #Load central config file
        with open(configYamlPath, 'r') as file:
            config = yaml.safe_load(file)

        input_path = config['inputFiles']['Trees2WSData']
                    
        config = config["backgroundScriptCfg"]
        
        if config['cats'] == 'auto':
            config['cats'] = (extractListOfCatsFromHiggsDNAAllData(input_path))

        nCats = len(config['cats'].split(","))
              
        cat_list = [
            (config['cats'].split(",")[categoryIndex], str(int(config['catOffset'])+categoryIndex))
            for categoryIndex in range(nCats)
        ]        
        branch_map = {i: cat_catOffset for i, cat_catOffset in enumerate(cat_list)}
        return branch_map

    def output(self):
        if self.variable == '':
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"], f"config/{self.year}_inclusive.yml")
        else:
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"], f"config/{self.year}_{self.variable}.yml")
        
        #Load central config file
        with open(configYamlPath, 'r') as file:
            config = yaml.safe_load(file)
        
        if self.output_dir == '':
            output_dir = config['outputFolder']
        else:
            output_dir = self.output_dir
                    
        config = config["backgroundScriptCfg"]
        
        cat, cat_offset = self.branch_data
        outdir_ext = os.path.join(output_dir, 'Background', f'outdir_{config["ext"]}')

        
        outputFileTargets = []
        
        bkg_plots = glob.glob(os.path.join(outdir_ext, f'bkgfTest-Data/*_cat{cat_offset}.png'))
        bkg_plots += glob.glob(os.path.join(outdir_ext, f'bkgfTest-Data/*_cat{cat_offset}.pdf'))
        bkg_plots += glob.glob(os.path.join(outdir_ext, f'bkgfTest-Data/*_cat{cat_offset}.pdf_gofTest.pdf'))
    
        output_paths = [os.path.join(outdir_ext, f'CMS-HGG_multipdf_{cat}.root'), os.path.join(outdir_ext, f'bkgfTest-Data/multipdf_{cat}.pdf'), os.path.join(outdir_ext, f'bkgfTest-Data/multipdf_{cat}.png')]
        
        output_paths += bkg_plots
   
        for _, current_output_path in enumerate(output_paths):
            outputFileTargets.append(law.LocalFileTarget(current_output_path))

        return outputFileTargets

    def run(self):
        if self.variable == '':
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"], f"config/{self.year}_inclusive.yml")
        else:
            configYamlPath = os.path.join(os.environ["ANALYSIS_PATH"], f"config/{self.year}_{self.variable}.yml")
        
        #Load central config file
        with open(configYamlPath, 'r') as file:
            config = yaml.safe_load(file)
        
        if self.output_dir == '':
            output_dir = config['outputFolder']
        else:
            output_dir = self.output_dir
            
        
        input_path = config['inputFiles']['Trees2WSData']
                    
        config = config["backgroundScriptCfg"]
        
        if config['cats'] == 'auto':
            config['cats'] = (extractListOfCatsFromHiggsDNAAllData(input_path))
        config['nCats'] = len(config['cats'].split(","))
    
        # Add dummy entries for procs and signalFitWSFile (used in old plotting script)
        config['signalFitWSFile'] = 'none'
        config['procs'] = 'none'
        config['batch'] = 'local'
        config['queue'] = 'none'
        if self.year == 'combined': config['year'] = 'all'
        else: config['year'] = self.year     
        config['intLumi'] = lumiMap[self.year]
                
        if self.variable == '':
            all_data_input_path = os.path.join(output_dir, "input_output_data", f"input_output_data_{self.year}/ws/allData.root")
        else:
            all_data_input_path = os.path.join(output_dir, "input_output_data", f"input_output_data_{self.variable}_{self.year}/ws/allData.root")

        cat, cat_offset = self.branch_data
        input_path = all_data_input_path
        
        if self.batch_flavor == "slurm/psi":
            # Have to use /scratch/batch_username/ for slurm/psi
            os.environ["TARGET_PATH"] = f"/scratch/{os.environ['USER']}/{os.environ['SLURM_JOB_ID']}"
            temp_output_dir = os.environ["TARGET_PATH"]
            execute_command([f'xrdfs root://t3dcachedb.psi.ch:1094/ mkdir -p {output_dir}/Background'], shell=True)
            execute_command([f'xrdfs root://t3dcachedb.psi.ch:1094/ mkdir -p {output_dir}/Background/outdir_{config["ext"]}'], shell=True)
            safe_mkdir(temp_output_dir)
        else:
            temp_output_dir = output_dir
            safe_mkdir(temp_output_dir)
        
        if temp_output_dir[-1] != "/":
            temp_output_dir += "/"

        script_path = os.path.join(os.environ["ANALYSIS_PATH"], "Background/runBackgroundScripts.sh")
        arguments = [
            "-i", input_path,
            "-p", "none",
            "-f", cat,
            "--outputFolder", f"{temp_output_dir}",
            "--ext", f'{config["ext"]}',
            "--catOffset", cat_offset,
            "--intLumi", f"{lumiMap[self.year]}",
            "--year", f"{self.year}",
            "--batch", "local",
            "--queue", "microcentury",
            "--sigFile", "none",
            "--isData",
            "--fTest"
        ]
        command = [script_path] + arguments
        # print("Output:", command)
        
        # Move to background folder
        original_dir = os.getcwd()
        os.chdir(os.path.join(os.environ["ANALYSIS_PATH"], "Background"))
        try:
            result = subprocess.run(command, check=True, text=True, capture_output=True)
            print("Script output:", result.stdout)
            print("Script executed successfully.")
        except subprocess.CalledProcessError as e:
            print("Error executing script:", e.stderr)
        os.chdir(original_dir)

        if self.batch_flavor == "slurm/psi":
            bkg_folder = f"outdir_{config['ext']}"
            execute_command([f"ls -al {temp_output_dir}/*"], shell=True)
            if "/work" in output_dir:
                slurm_copy_command = [
                    'cp', '-rf',
                    f'{temp_output_dir}/{bkg_folder}',
                     f'{output_dir}/Background/'
                ]
            else:
                # Copying output files to final destination on the /pnfs.
                slurm_copy_command = [
                    'xrdcp', '-rf',
                    f'{temp_output_dir}/{bkg_folder}',
                    'root://t3dcachedb.psi.ch:1094//'+ f'{output_dir}/Background/'
                ]
            execute_command(slurm_copy_command)
            # Cleaning up scratch space.
            shutil.rmtree(temp_output_dir)
        