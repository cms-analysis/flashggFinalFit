import law
import os
import subprocess
import yaml
import errno
import shutil

from commonTools import *
from commonObjects import *

from Signal.law_signal import *

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
                

class MakeYieldsCategory(Task, HTCondorWorkflow, law.LocalWorkflow):#(law.Task): #(Task, HTCondorWorkflow, law.LocalWorkflow):
    inputWSDirMap = law.Parameter(description="Map. Format: year=inputWSDir (separate years by comma)")
    output_dir = law.Parameter(description="Path to the output directory")
    ext = law.Parameter(default="earlyAnalysis", description="Extension to be used for output folder naming")
    year = law.Parameter(default='2022', description="Year")
    cats = law.Parameter(description="List of categories separated with a comma.")
    procs = law.Parameter(description="Comma separated list of signal processes. auto = automatically inferred from input workspaces")
    mergeYears = law.Parameter(default=False, description="Merge category across years")
    skipBkg = law.Parameter(default=False, description="Only add signal processes to datacard")
    bkgScaler = law.Parameter(default=1., description="Add overall scale factor for background")
    sigModelWSDir = law.Parameter(default='./Models/signal', description="Input signal model WS directory")
    sigModelExt = law.Parameter(default='packaged', description="Extension used when saving signal model")
    bkgModelWSDir = law.Parameter(default='./Models/background', description="Input background model WS directory")
    bkgModelExt = law.Parameter(default='multipdf', description="Extension used when saving background model")
    # For yields calculations:
    skipZeroes = law.Parameter(default=False, description="Skip signal processes with 0 sum of weights")
    skipCOWCorr = law.Parameter(default=False, description="Skip centralObjectWeight correction for events in acceptance. Use if no centralObjectWeight in workspace")
    # For systematics:
    doSystematics = law.Parameter(default=False, description="Include systematics calculations and add to datacard")
    ignore_warnings = law.Parameter(default=False, description="Skip errors for missing systematics. Instead output warning message")
    
    mass = law.Parameter(default='125', description="Input workspace mass")
    nCats = law.Parameter(description="Number of Categories")
    variable = law.Parameter(default="", description="Variable to be used")
    
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
            
        tasks = [SignalPackaging(output_dir=output_dir, variable=self.variable, year=self.year)]
        
        return tasks
    
    
    def create_branch_map(self):
        # map branch indexes to ascii numbers from 97 to 122 ("a" to "z")
        nCats = len(self.cats.split(","))
        
        cat_list = [
            self.cats.split(",")[categoryIndex]
            for categoryIndex in range(nCats)
        ]
        
        branch_map = {i: cat for i, cat in enumerate(cat_list)}
        return branch_map

    def output(self):
        
        cat = self.branch_data

        return [law.LocalFileTarget(self.output_dir + f'/Datacards/yields_{self.ext}/{cat}.pkl')]

    def run(self):
        cat = self.branch_data
        
        safe_mkdir(self.output_dir)
        safe_mkdir(self.output_dir + "/Datacards")
        safe_mkdir(self.output_dir + f"/Datacards/yields_{self.ext}")
        
        script_path = os.environ["ANALYSIS_PATH"] + "/Datacard/makeYields.py"
        arguments = [
            "python3",
            script_path,
            "--inputWSDirMap", f"{self.inputWSDirMap}",
            "--cat", cat,
            "--outputDir", f"{self.output_dir}",
            "--ext", self.ext,
            "--procs", f"{self.procs}",
            "--mass", f"{self.mass}",
            "--bkgScaler", f"{self.bkgScaler}",
            "--sigModelWSDir", f"{self.sigModelWSDir}",
            "--sigModelExt", f"{self.sigModelExt}",
            "--bkgModelWSDir", f"{self.bkgModelWSDir}",
            "--bkgModelExt", f"{self.bkgModelExt}"
            ]
        if self.variable != '':
            arguments.append("--variable")
            arguments.append(f"{self.variable}")
        
        if convert_boolean_string(self.doSystematics): arguments.append("--doSystematics")
        if convert_boolean_string(self.mergeYears): arguments.append("--mergeYears")
        if convert_boolean_string(self.skipZeroes): arguments.append("--skipZeroes")
        if convert_boolean_string(self.ignore_warnings): arguments.append("--ignore-warnings")
        if convert_boolean_string(self.skipBkg): arguments.append("--skipBkg")
        if convert_boolean_string(self.skipCOWCorr): arguments.append("--skipCOWCorr")

    
        command = arguments
        # print("Output:", command)
        try:
            result = subprocess.run(command, check=True, text=True, capture_output=True)
            print("Script output:", result.stdout)
            print("Script executed successfully.")
        except subprocess.CalledProcessError as e:
            print("Error executing script:", e.stderr)

class MakeYields(law.Task):
    variable = law.Parameter(default="", description="Variable to be used")
    output_dir = law.Parameter(default = '', description="Path to the output directory")
    year = law.Parameter(default='2022', description="Year")
    
    def requires(self):
        # req() is defined on all tasks and handles the passing of all parameter values that are
        # common between the required task and the instance (self)
        
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
                
        input_path = config['inputFiles']['Trees2WSData']
        all_data_input_path = output_dir + f"input_output_data_{self.year}/ws/allData.root"
        
        packaged_config = config[f"packaged_{self.year}"]
                    
        datacard_config = config["datacard_yields"]
        
        if datacard_config['cats'] == 'auto':
            datacard_config['cats'] = (extractListOfCatsFromHiggsDNAAllData(input_path))
        datacard_config['nCats'] = len(datacard_config['cats'].split(","))
    
        if self.year == 'combined': datacard_config['year'] = 'all'
        else: datacard_config['year'] = self.year        
              
        inputWSDirMap = ''
        
        # Create inputWSDirMap
        if datacard_config['year'] == 'all':
            allYears = list(allErasMap.keys())
            for i, currentYear in enumerate(allErasMap.keys()):
                for j, currentEra in enumerate(allErasMap[currentYear]):
                    currentYearEra = currentYear + currentEra
                    if self.variable == '':
                        currentYearEraInputOutput = output_dir + "/input_output_{}{}/ws_signal".format(currentYear, currentEra)
                    else:
                        currentYearEraInputOutput = output_dir + "/input_output_{}_{}{}/ws_signal".format(self.variable, currentYear, currentEra)
                    if (i != len(allErasMap.keys()) - 1) and (j != len(allErasMap[currentYear]) - 1):  # Check if it's the last element of the last year
                        inputWSDirMap += currentYearEra + "=" + currentYearEraInputOutput + ","
                    else:
                        inputWSDirMap += currentYearEra + "=" + currentYearEraInputOutput
        else:
            for j, currentEra in enumerate(allErasMap[self.year]):
                currentYearEra = self.year + currentEra
                if self.variable == '':
                    currentYearEraInputOutput = output_dir + "/input_output_{}{}/ws_signal".format(self.year, currentEra)
                else:
                    currentYearEraInputOutput = output_dir + "/input_output_{}_{}{}/ws_signal".format(self.variable, self.year, currentEra)
                if (j != len(allErasMap[self.year]) - 1):  # Check if it's the last element of the last year
                    inputWSDirMap += currentYearEra + "=" + currentYearEraInputOutput + ","
                else:
                    inputWSDirMap += currentYearEra + "=" + currentYearEraInputOutput
        
        tasks = [MakeYieldsCategory(inputWSDirMap=inputWSDirMap, output_dir=output_dir, year=self.year, cats=datacard_config['cats'], procs=datacard_config['procs'], nCats=datacard_config['nCats'], ext=datacard_config['ext'], mergeYears=datacard_config['mergeYears'], skipBkg=datacard_config['skipBkg'], bkgScaler=datacard_config['bkgScaler'], sigModelWSDir=datacard_config['sigModelWSDir'], sigModelExt=f"packaged{packaged_config['ext']}", bkgModelWSDir=datacard_config['bkgModelWSDir'], bkgModelExt=datacard_config['bkgModelExt'], skipZeroes=datacard_config['skipZeroes'], skipCOWCorr=datacard_config['skipCOWCorr'], doSystematics=datacard_config['doSystematics'], ignore_warnings=datacard_config['ignore_warnings'], mass=datacard_config['mass'], variable=self.variable, version='v1', workflow=datacard_config['execution'])]
        
        return tasks
        
    def output(self):
        # returns output folder
        
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
            
        input_path = config['inputFiles']['Trees2WSData']
        
        datacard_config = config["datacard_yields"]
        
        output_paths = []
        
        output_paths.append(law.LocalFileTarget(output_dir + f"/Datacards/yields_{datacard_config['ext']}"))
        
        if datacard_config['cats'] == 'auto':
            datacard_config['cats'] = (extractListOfCatsFromHiggsDNAAllData(input_path))
        datacard_config['nCats'] = len(datacard_config['cats'].split(","))
        
        for cat in datacard_config['cats'].split(","):
            output_paths.append(law.LocalFileTarget(output_dir + f"/Datacards/yields_{datacard_config['ext']}/{cat}.pkl"))
                                  
        return output_paths
                
    
    def run(self):
        
        return True
    
class MakeDatacard(law.Task):
    variable = law.Parameter(default="", description="Variable to be used")
    output_dir = law.Parameter(default = '', description="Path to the output directory")
    year = law.Parameter(default='2022', description="Year")
    
    def requires(self):
        # req() is defined on all tasks and handles the passing of all parameter values that are
        # common between the required task and the instance (self)
        
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
        
        tasks = [MakeYields(variable=self.variable, output_dir=output_dir, year=self.year)]
        
        return tasks    

    def output(self):
        # returns output folder
        
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
            
        datacard_config = config["datacard"]
        
        output_paths = []
        
        if self.variable == '': 
            if datacard_config['saveDataFrame']:
                output_paths.append(law.LocalFileTarget(output_dir+ f"/Datacards/Dataframe/Datacard_{self.year}.pkl"))
                output_paths.append(law.LocalFileTarget(output_dir+ f"/Datacards/Dataframe/Datacard_{self.year}_unsymmetrized.pkl"))
            output_paths.append(law.LocalFileTarget(output_dir+ f"/Datacards/Datacard_{self.year}.txt"))
        else:
            if datacard_config['saveDataFrame']:
                output_paths.append(law.LocalFileTarget(output_dir+ f"/Datacards/Dataframe/Datacard_{self.variable}_{self.year}.pkl"))
                output_paths.append(law.LocalFileTarget(output_dir+ f"/Datacards/Dataframe/Datacard_{self.variable}_{self.year}_unsymmetrized.pkl"))
            output_paths.append(law.LocalFileTarget(output_dir+ f"/Datacards/Datacard_{self.variable}_{self.year}.txt"))
            output_paths.append(law.LocalFileTarget(output_dir+ f"/Datacards/Datacard_{self.variable}_{self.year}_unsymmetrized.txt"))
        return output_paths
                
    
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
            
        safe_mkdir(output_dir)
        output_dir = output_dir + "/Datacards/"
        safe_mkdir(output_dir)
        
        datacard_config = config["datacard"]
        yields_config = config["datacard_yields"]
        pklInputFiles = output_dir
        
        # if self.variable != '':
        #     yields_config["ext"] = yields_config["ext"]+'_'+self.variable
                    
        # Create years string
        years = ''
        if self.year == 'combined': datacard_config['year'] = 'all'
        else: datacard_config['year'] = self.year   
        
        if datacard_config['year'] == 'all':
            allYears = list(allErasMap.keys())
            for i, currentYear in enumerate(allErasMap.keys()):
                for j, currentEra in enumerate(allErasMap[currentYear]):
                    currentYearEra = currentYear + currentEra
                    if (i != len(allErasMap.keys()) - 1) and (j != len(allErasMap[currentYear]) - 1):  # Check if it's the last element of the last year
                        years += currentYearEra + ","
                    else:
                        years += currentYearEra
        else:
            for j, currentEra in enumerate(allErasMap[self.year]):
                currentYearEra = self.year + currentEra
                if (j != len(allErasMap[self.year]) - 1):  # Check if it's the last element of the last year
                    years += currentYearEra + ","
                else:
                    years += currentYearEra
        
        script_path = os.environ["ANALYSIS_PATH"] + "/Datacard/makeDatacard.py"
        arguments = [
            "python3",
            script_path,
            "--inputFiles", f"{pklInputFiles}",
            "--outputDir", f"{output_dir}",
            "--ext", yields_config["ext"],
            "--years", f"{years}",
            "--mass", f"{yields_config['mass']}",
            "--pruneThreshold", f"{datacard_config['pruneThreshold']}",
            "--analysis", f"{datacard_config['analysis']}",
            "--output", f"{datacard_config['output']}"
            ]
        if self.variable != '':
            arguments.append("--variable")
            arguments.append(f"{self.variable}")
        
        if convert_boolean_string(datacard_config["prune"]): arguments.append("--prune")
        if convert_boolean_string(datacard_config["doTrueYield"]): arguments.append("--doTrueYield")
        if convert_boolean_string(datacard_config["skipCOWCorr"]): arguments.append("--skipCOWCorr")
        if convert_boolean_string(datacard_config["doSystematics"]): arguments.append("--doSystematics")
        if convert_boolean_string(datacard_config["doMCStatUncertainty"]): arguments.append("--doMCStatUncertainty")
        if convert_boolean_string(datacard_config["doSTXSMerging"]): arguments.append("--doSTXSMerging")
        if convert_boolean_string(datacard_config["doSTXSScaleCorrelationScheme"]): arguments.append("--doSTXSScaleCorrelationScheme")
        if convert_boolean_string(datacard_config["saveDataFrame"]): arguments.append("--saveDataFrame")
    
        command = arguments
        # print("Output:", command)
        try:
            result = subprocess.run(command, check=True, text=True, capture_output=True)
            print("Script output:", result.stdout)
            print("Script executed successfully.")
        except subprocess.CalledProcessError as e:
            print("Error executing script:", e.stderr)
            
        
        if self.variable != '':
            
            clean_config = config["datacard_clean"]
            
            datacard_path = output_dir + datacard_config["output"] + ".txt"
            script_path = os.environ["ANALYSIS_PATH"] + "/Datacard/cleanDatacard.py"
            arguments = [
                "python3",
                script_path,
                "-d", f"{datacard_path}",
                "-f", f"{clean_config['factor']}",
                "--symmetrizeNuisance", f"{clean_config['symmetrizeNuisance']}",
                ]
            
            if convert_boolean_string(clean_config["removeDoubleSided"]): arguments.append("--removeDoubleSided")
            if convert_boolean_string(clean_config["removeNonDiagonal"]): arguments.append("--removeNonDiagonal")
            if convert_boolean_string(clean_config["verbose"]): arguments.append("--verbose")
        
            command = arguments
            # print("Output:", command)
            try:
                result = subprocess.run(command, check=True, text=True, capture_output=True)
                print("Script output:", result.stdout)
                print("Script executed successfully.")
            except subprocess.CalledProcessError as e:
                print("Error executing script:", e.stderr)
                
            
            shutil.move(datacard_path, output_dir + datacard_config["output"] + "_unsymmetrized.txt")
            shutil.move(output_dir + datacard_config["output"] + "_cleaned.txt", output_dir + datacard_config["output"] + ".txt")
        