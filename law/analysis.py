import law
import luigi
import os
import yaml
import errno

from commonTools import *
from commonObjects import *

from Datacard.law_datacard import *
from Background.law_background import *

# Function to safely create a directory
def safe_mkdir(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

class Trees2WSAndBackground(law.Task):
    variable = law.Parameter(default="", description="Variable to be used")
    output_dir = law.Parameter(default = '', description="Path to the output directory")
    year = law.Parameter(default='2022', description="Year")
    batch_flavor = law.Parameter(default="slurm", description="Batch system to use")
    
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
        
        tasks = [Trees2WS(variable=self.variable, output_dir=output_dir, year=self.year, batch_flavor=self.batch_flavor), Background(variable=self.variable, output_dir=output_dir, year=self.year, batch_flavor=self.batch_flavor)]
        
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
            
        background_config = config["backgroundScriptCfg"]   
        
        output_paths = []
        
        if self.variable == '': 
            # Background output
            output_paths.append(law.LocalFileTarget(output_dir + f"/outdir_{background_config['ext']}"))     
            output_paths.append(law.LocalFileTarget(output_dir + f"/outdir_{background_config['ext']}/bkgfTest-Data/fTestResults.txt"))
        else:
            # Background output
            output_paths.append(law.LocalFileTarget(output_dir + f"/outdir_{background_config['ext']}_{self.variable}"))
            output_paths.append(law.LocalFileTarget(output_dir + f"/outdir_{background_config['ext']}_{self.variable}/bkgfTest-Data/fTestResults.txt"))        
        
        era_list_with_variable = [
            (era, self.variable)
            for era in allErasMap[f"{self.year}"]
        ]
        for era, var in era_list_with_variable:
            if var == '':
                current_output_path = output_dir + "/input_output_{}{}".format(self.year, era)
            else:
                current_output_path = output_dir + "/input_output_{}_{}{}".format(var, self.year, era)
                
            output_paths.append(law.LocalFileTarget(current_output_path + '/ws_signal'))    
            
        return output_paths
                
    
    def run(self):
        # Suggestion by ChatGPT: We should ensure that the run() method produces a non-empty payload, otherwise the executable for htcondor could sometimes be empty and the submission fails
        with self.output()[0].open("w") as f:
            f.write("echo Running Trees2WSAndBackground\n")

        # if self.variable == '':
        #     # configYamlPath = os.path.dirname(os.path.abspath(__file__)) + f"/../config/{self.year}_inclusive.yml"
        #     configYamlPath = os.environ["ANALYSIS_PATH"] + f"/config/{self.year}_inclusive.yml"
        # else:
        #     # configYamlPath = os.path.dirname(os.path.abspath(__file__)) + f"/../config/{self.year}_{self.variable}.yml"
        #     configYamlPath = os.environ["ANALYSIS_PATH"] + f"/config/{self.year}_{self.variable}.yml"
        
        # #Load central config file
        # with open(configYamlPath, 'r') as file:
        #     config = yaml.safe_load(file)
        
        # if self.output_dir == '':
        #     output_dir = config['outputFolder']
        # else:
        #     output_dir = self.output_dir
        
        # # tasks = [Trees2WS(variable=self.variable, output_dir=output_dir, year=self.year), Background(variable=self.variable, output_dir=output_dir, year=self.year)]
        # tasks = [Trees2WS(variable=self.variable, output_dir=output_dir, year=self.year), Background(variable=self.variable, output_dir=output_dir, year=self.year)]
        
        # for current_task in tasks:
        #     # Ensure all dependencies are fulfilled
        #     for dependency in luigi.task.flatten(current_task.requires()):
        #         print(luigi.task.flatten(current_task.requires()))
        #         if not dependency.complete():
        #             dependency.requires()

        #     # Now run the task
        #     if not current_task.complete():
        #         current_task.run()
        
        return True
    
class PhotonSystAndFTest(law.Task):
    variable = law.Parameter(default="", description="Variable to be used")
    output_dir = law.Parameter(default = '', description="Path to the output directory")
    year = law.Parameter(default='2022', description="Year")
    
    batch_flavor = law.Parameter(default="slurm", description="Batch system to use")
    
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
        
        tasks = [CalcPhotonSyst(variable=self.variable, output_dir=output_dir, year=self.year, batch_flavor=self.batch_flavor), FTest(variable=self.variable, output_dir=output_dir, year=self.year, batch_flavor=self.batch_flavor)]
        
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
            
        data_input_path = config['inputFiles']['Trees2WSData']  
        
        output_paths = []
        
        # Loop over a years era
        for currentEra in allErasMap[f"{self.year}"]:

            if currentEra != "None":
                currentConfig = config[f"signalScriptCfg_{self.year}_{currentEra}"]
            else:
                currentConfig = config[f"signalScriptCfg_{self.year}"]
            # returns output folder
            
            output_paths.append(law.LocalFileTarget(output_dir + f"/outdir_{currentConfig['ext']}/calcPhotonSyst"))
            output_paths.append(law.LocalFileTarget(output_dir + f"/outdir_{currentConfig['ext']}/calcPhotonSyst/pkl"))
            
            output_paths.append(law.LocalFileTarget(output_dir + f"/outdir_{currentConfig['ext']}/fTest"))
            output_paths.append(law.LocalFileTarget(output_dir + f"/outdir_{currentConfig['ext']}/fTest/json"))
            output_paths.append(law.LocalFileTarget(output_dir + f"/outdir_{currentConfig['ext']}/fTest/Plots"))
            
            # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            # If proc/cat == auto. Extract processes and categories
            if currentConfig['cats'] == "auto":
                currentConfig['cats'] = extractListOfCatsFromHiggsDNAAllData(data_input_path)
                
            cat_list = currentConfig['cats'].split(",")
            for cat in cat_list:
                output_paths.append(law.LocalFileTarget(output_dir + f"/outdir_{currentConfig['ext']}/fTest/json/nGauss_{cat}.json"))
                output_paths.append(law.LocalFileTarget(output_dir + f"/outdir_{currentConfig['ext']}/calcPhotonSyst/pkl/{cat}.pkl"))
            
        return output_paths
    
    def run(self):
        return True



class FinalFits(law.Task):
    variable = law.Parameter(default="", description="Variable to be used")
    output_dir = law.Parameter(default = '', description="Path to the output directory")
    year = law.Parameter(default='2022', description="Year")
    
    batch_flavor = law.Parameter(default="slurm", description="Batch system to use")
    
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
        
        tasks = [Trees2WS(variable=self.variable, output_dir=output_dir, year=self.year, batch_flavor=self.batch_flavor), Background(variable=self.variable, output_dir=output_dir, year=self.year, batch_flavor=self.batch_flavor), MakeDatacard(variable=self.variable, output_dir=output_dir, year=self.year, batch_flavor=self.batch_flavor, version="v1")]
        
        return sorted(tasks)

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