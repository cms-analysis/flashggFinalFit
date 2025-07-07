import law
import luigi
import os
import yaml
import errno

from commonTools import *
from commonObjects import *

from Datacard.law_datacard import *
from Background.law_background import *
from Trees2WS.law_trees2ws import *
from Signal.law_signal import *
from Combine.law_combine import *

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

class FinalFits(law.Task):
    variable = law.Parameter(default="", description="Variable to be used")
    output_dir = law.Parameter(default = '', description="Path to the output directory")
    year = law.Parameter(default='2022', description="Year")
    
    # Unblinded fits and impacts
    unblinded_fits = law.Parameter(default=False, description="Produce unblinded fits")
    unblinded_stage_one = law.Parameter(default=False, description="Produce Stage 1 unblinded results")
    unblinded_stage_two = law.Parameter(default=False, description="Produce Stage 2 unblinded results")
    unblinded_stage_three = law.Parameter(default=False, description="Produce Stage 3 unblinded results")
    pvalue = law.Parameter(default=False, description="Produce p-value for the unblinded fit")
    
    # Asimov fits and impacts
    asimov_fits = law.Parameter(default=False, description="Produce the Asimov fits")
    asimov_impacts = law.Parameter(default=False, description="Produce the Asimov impacts")
    
    batch_system = law.Parameter(default="slurm", description="Batch system to use")
    batch_flavor = law.Parameter(default="slurm", description="Special treatment for PSI Slurm batch system")
    
    def requires(self):
        # req() is defined on all tasks and handles the passing of all parameter values that are
        # common between the required task and the instance (self)
        
        if self.variable == '':
            # configYamlPath = os.path.dirname(os.path.abspath(__file__)) + f"/../config/{self.year}_inclusive.yml"
            configYamlPath = os.environ["ANALYSIS_PATH"] + f"/config/{self.year}_inclusive.yml"
        else:
            # configYamlPath = os.path.dirname(os.path.abspath(__file__)) + f"/../config/{self.year}_{self.variable}.yml"
            configYamlPath = os.environ["ANALYSIS_PATH"] + f"/config/{self.year}_{self.variable}.yml"
        
        #Load central config file
        with open(configYamlPath, 'r') as file:
            config = yaml.safe_load(file)
        
        if self.output_dir == '':
            output_dir = config['outputFolder']
        else:
            output_dir = self.output_dir
        
        if convert_boolean_string(self.unblinded_fits):
            tasks = [Background(variable=self.variable, output_dir=output_dir, year=self.year, batch_flavor=self.batch_flavor, version=self.variable if self.variable != "" else "inclusive", workflow=self.batch_system), CreateAsimovFit(variable=self.variable, output_dir=output_dir, year=self.year, batch_flavor=self.batch_flavor, version=self.variable if self.variable != '' else 'inclusive', workflow=self.batch_system), CreateUnblindedFit(variable=self.variable, output_dir=output_dir, year=self.year, batch_flavor=self.batch_flavor, version=self.variable if self.variable != "" else "inclusive", workflow=self.batch_system)]
        elif convert_boolean_string(self.unblinded_stage_one):
            impactConfig = config["combine_impacts"]
            tasks = [Background(variable=self.variable, output_dir=output_dir, year=self.year, batch_flavor=self.batch_flavor, version=self.variable if self.variable != "" else "inclusive", workflow=self.batch_system), CreateAsimovFit(variable=self.variable, output_dir=output_dir, year=self.year, batch_flavor=self.batch_flavor, version=self.variable if self.variable != '' else 'inclusive', workflow=self.batch_system), UnblindedImpactThirdStep(variable=self.variable, output_dir=output_dir, year=self.year, batch_flavor=self.batch_flavor, version=self.variable if self.variable != "" else "inclusive", workflow=impactConfig["execution"], slurm_partition=impactConfig['batchPartition'], slurm_memory=impactConfig['batchMemory'], slurm_max_runtime=impactConfig['batchMaxRuntime'], htcondor_partition=impactConfig['batchPartition'], htcondor_memory=impactConfig['batchMemory'], htcondor_max_runtime=impactConfig['batchMaxRuntime'])]
        elif convert_boolean_string(self.unblinded_stage_two):
            impactConfig = config["combine_impacts"]
            mggConfig = config["combine_mggToys"]
            tasks = [Background(variable=self.variable, output_dir=output_dir, year=self.year, batch_flavor=self.batch_flavor, version=self.variable if self.variable != "" else "inclusive", workflow=self.batch_system), CreateAsimovFit(variable=self.variable, output_dir=output_dir, year=self.year, batch_flavor=self.batch_flavor, version=self.variable if self.variable != '' else 'inclusive', workflow=self.batch_system), UnblindedImpactThirdStep(variable=self.variable, output_dir=output_dir, year=self.year, batch_flavor=self.batch_flavor, version=self.variable if self.variable != "" else "inclusive", workflow=impactConfig["execution"], slurm_partition=impactConfig['batchPartition'], slurm_memory=impactConfig['batchMemory'], slurm_max_runtime=impactConfig['batchMaxRuntime'], htcondor_partition=impactConfig['batchPartition'], htcondor_memory=impactConfig['batchMemory'], htcondor_max_runtime=impactConfig['batchMaxRuntime']), MggDistribution(variable=self.variable, output_dir=output_dir, year=self.year, batch_flavor=self.batch_flavor, version=self.variable if self.variable != "" else "inclusive", workflow=mggConfig["execution"], slurm_partition=mggConfig['batchPartition'], slurm_memory=mggConfig['batchMemory'], slurm_max_runtime=mggConfig['batchMaxRuntime'], htcondor_partition=mggConfig['batchPartition'], htcondor_memory=mggConfig['batchMemory'], htcondor_max_runtime=mggConfig['batchMaxRuntime'], is_postfit=False)]
        elif convert_boolean_string(self.unblinded_stage_three):
            impactConfig = config["combine_impacts"]
            mggConfig = config["combine_mggToys"]
            tasks = [Background(variable=self.variable, output_dir=output_dir, year=self.year, batch_flavor=self.batch_flavor, version=self.variable if self.variable != "" else "inclusive", workflow=self.batch_system), CreateAsimovFit(variable=self.variable, output_dir=output_dir, year=self.year, batch_flavor=self.batch_flavor, version=self.variable if self.variable != '' else 'inclusive', workflow=self.batch_system), UnblindedImpactThirdStep(variable=self.variable, output_dir=output_dir, year=self.year, batch_flavor=self.batch_flavor, version=self.variable if self.variable != "" else "inclusive", workflow=impactConfig["execution"], slurm_partition=impactConfig['batchPartition'], slurm_memory=impactConfig['batchMemory'], slurm_max_runtime=impactConfig['batchMaxRuntime'], htcondor_partition=impactConfig['batchPartition'], htcondor_memory=impactConfig['batchMemory'], htcondor_max_runtime=impactConfig['batchMaxRuntime']), MggDistribution(variable=self.variable, output_dir=output_dir, year=self.year, batch_flavor=self.batch_flavor, version=self.variable if self.variable != "" else "inclusive", workflow=mggConfig["execution"], slurm_partition=mggConfig['batchPartition'], slurm_memory=mggConfig['batchMemory'], slurm_max_runtime=mggConfig['batchMaxRuntime'], htcondor_partition=mggConfig['batchPartition'], htcondor_memory=mggConfig['batchMemory'], htcondor_max_runtime=mggConfig['batchMaxRuntime'], is_postfit=True)]
        elif convert_boolean_string(self.pvalue):
            tasks = [Background(variable=self.variable, output_dir=output_dir, year=self.year, batch_flavor=self.batch_flavor, version=self.variable if self.variable != "" else "inclusive", workflow=self.batch_system), PValueCalculation(variable=self.variable, output_dir=output_dir, year=self.year, batch_flavor=self.batch_flavor, version=self.variable if self.variable != '' else 'inclusive', workflow=self.batch_system, slurm_partition=hesseConfig['batchPartition'], slurm_memory=hesseConfig['batchMemory'], slurm_max_runtime=hesseConfig['batchMaxRuntime'], htcondor_partition=hesseConfig['batchPartition'], htcondor_memory=hesseConfig['batchMemory'], htcondor_max_runtime=hesseConfig['batchMaxRuntime'])]
        elif convert_boolean_string(self.asimov_fits):
            tasks = [Background(variable=self.variable, output_dir=output_dir, year=self.year, batch_flavor=self.batch_flavor, version=self.variable if self.variable != "" else "inclusive", workflow=self.batch_system), CreateAsimovFit(variable=self.variable, output_dir=output_dir, year=self.year, batch_flavor=self.batch_flavor, version=self.variable if self.variable != '' else 'inclusive', workflow=self.batch_system)]
        elif convert_boolean_string(self.asimov_impacts):
            tasks = [Background(variable=self.variable, output_dir=output_dir, year=self.year, batch_flavor=self.batch_flavor, version=self.variable if self.variable != "" else "inclusive", workflow=self.batch_system), AsimovImpactThirdStep(variable=self.variable, output_dir=output_dir, year=self.year, batch_flavor=self.batch_flavor, version=self.variable if self.variable != '' else 'inclusive', workflow=self.batch_system)]
        else:
            print("No final fit tasks selected. Please set the appropriate parameters to True.")
            exit(1)

        return tasks

    def output(self):
        # returns output folder
        
        if self.variable == '':
            # configYamlPath = os.path.dirname(os.path.abspath(__file__)) + f"/../config/{self.year}_inclusive.yml"
            configYamlPath = os.environ["ANALYSIS_PATH"] + f"/config/{self.year}_inclusive.yml"
        else:
            # configYamlPath = os.path.dirname(os.path.abspath(__file__)) + f"/../config/{self.year}_{self.variable}.yml"
            configYamlPath = os.environ["ANALYSIS_PATH"] + f"/config/{self.year}_{self.variable}.yml"
        
        #Load central config file
        with open(configYamlPath, 'r') as file:
            config = yaml.safe_load(file)
            
        if self.output_dir == '':
            output_dir = config['outputFolder']
        else:
            output_dir = self.output_dir
            
        datacard_config = config["datacard"]
        background_config = config["backgroundScriptCfg"]   
        
        output_paths = []
        
        if self.variable == '': 
            # Signal+Datacard output
            if datacard_config['saveDataFrame']:
                output_paths.append(law.LocalFileTarget(output_dir+ f"/Datacards/Dataframe"))
                output_paths.append(law.LocalFileTarget(output_dir+ f"/Datacards/Dataframe/Datacard_{self.year}.pkl"))
                output_paths.append(law.LocalFileTarget(output_dir+ f"/Datacards/Dataframe/Datacard_{self.year}_unsymmetrized.pkl"))
            output_paths.append(law.LocalFileTarget(output_dir+ f"/Datacards/Datacard_{self.year}.txt"))
            
            # Background output
            output_paths.append(law.LocalFileTarget(output_dir + f"/outdir_{background_config['ext']}"))     
            output_paths.append(law.LocalFileTarget(output_dir + f"/outdir_{background_config['ext']}/bkgfTest-Data/fTestResults.txt"))
        else:
            # Signal+Datacard output
            if datacard_config['saveDataFrame']:
                output_paths.append(law.LocalFileTarget(output_dir+ f"/Datacards/Dataframe"))
                output_paths.append(law.LocalFileTarget(output_dir+ f"/Datacards/Dataframe/Datacard_{self.variable}_{self.year}.pkl"))
                output_paths.append(law.LocalFileTarget(output_dir+ f"/Datacards/Dataframe/Datacard_{self.variable}_{self.year}_unsymmetrized.pkl"))
            output_paths.append(law.LocalFileTarget(output_dir+ f"/Datacards/Datacard_{self.variable}_{self.year}.txt"))
            output_paths.append(law.LocalFileTarget(output_dir+ f"/Datacards/Datacard_{self.variable}_{self.year}_unsymmetrized.txt"))
            
            # Background output
            output_paths.append(law.LocalFileTarget(output_dir + f"/outdir_{background_config['ext']}_{self.variable}"))
            output_paths.append(law.LocalFileTarget(output_dir + f"/outdir_{background_config['ext']}_{self.variable}/bkgfTest-Data/fTestResults.txt"))
            
        return output_paths
                
    
    def run(self):
        
        return True