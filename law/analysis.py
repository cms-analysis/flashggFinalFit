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
from Plots.Spectra.law_spectra import *

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
    unblinded_covcorr = law.Parameter(default=False, description="Produce the Unblinded covariance and correlation matrices")
    pvalue = law.Parameter(default=False, description="Produce p-value for the unblinded fit")
    
    # Asimov fits and impacts
    asimov_fits = law.Parameter(default=False, description="Produce the Asimov fits")
    asimov_impacts = law.Parameter(default=False, description="Produce the Asimov impacts")
    asimov_covcorr = law.Parameter(default=False, description="Produce the Asimov covariance and correlation matrices")

    # Differentials
    unblinded_diff_spectra = law.Parameter(default=False, description="Produce unblinded differential spectra for the given variable")
    asimov_diff_spectra = law.Parameter(default=False, description="Produce Asimov differential spectra for the given variable")
    
    batch_system = law.Parameter(default="htcondor", description="Batch system to use")
    batch_flavor = law.Parameter(default="htcondor", description="Special treatment for PSI Slurm batch system")
    
    def requires(self):
        # req() is defined on all tasks and handles the passing of all parameter values that are
        # common between the required task and the instance (self)
        
        tasks = {}
        
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
            tasks["CreateUnblindedFit"] = CreateUnblindedFit(variable=self.variable, output_dir=output_dir, year=self.year, batch_flavor=self.batch_flavor, version=self.variable if self.variable != "" else "inclusive", workflow=self.batch_system)
        if convert_boolean_string(self.unblinded_stage_one):
            impactConfig = config["combine_impacts"]
            tasks["UnblindedImpactThirdStep"] = UnblindedImpactThirdStep(variable=self.variable, output_dir=output_dir, year=self.year, batch_flavor=self.batch_flavor, version=self.variable if self.variable != "" else "inclusive", workflow=impactConfig["execution"], slurm_partition=impactConfig['batchPartition'], slurm_memory=impactConfig['batchMemory'], slurm_max_runtime=impactConfig['batchMaxRuntime'], htcondor_partition=impactConfig['batchPartition'], htcondor_memory=impactConfig['batchMemory'], htcondor_max_runtime=impactConfig['batchMaxRuntime'])
        if convert_boolean_string(self.unblinded_stage_two):
            impactConfig = config["combine_impacts"]
            mggConfig = config["combine_mggToys"]
            tasks["UnblindedImpactThirdStep"] = UnblindedImpactThirdStep(variable=self.variable, output_dir=output_dir, year=self.year, batch_flavor=self.batch_flavor, version=self.variable if self.variable != "" else "inclusive", workflow=impactConfig["execution"], slurm_partition=impactConfig['batchPartition'], slurm_memory=impactConfig['batchMemory'], slurm_max_runtime=impactConfig['batchMaxRuntime'], htcondor_partition=impactConfig['batchPartition'], htcondor_memory=impactConfig['batchMemory'], htcondor_max_runtime=impactConfig['batchMaxRuntime'])
            tasks["MggDistribution"] = MggDistribution(variable=self.variable, output_dir=output_dir, year=self.year, batch_flavor=self.batch_flavor, version=self.variable if self.variable != "" else "inclusive", workflow=mggConfig["execution"], slurm_partition=mggConfig['batchPartition'], slurm_memory=mggConfig['batchMemory'], slurm_max_runtime=mggConfig['batchMaxRuntime'], htcondor_partition=mggConfig['batchPartition'], htcondor_memory=mggConfig['batchMemory'], htcondor_max_runtime=mggConfig['batchMaxRuntime'], is_postfit=False)
        if convert_boolean_string(self.unblinded_stage_three):
            impactConfig = config["combine_impacts"]
            mggConfig = config["combine_mggToys"]
            tasks["UnblindedImpactThirdStep"] = UnblindedImpactThirdStep(variable=self.variable, output_dir=output_dir, year=self.year, batch_flavor=self.batch_flavor, version=self.variable if self.variable != "" else "inclusive", workflow=impactConfig["execution"], slurm_partition=impactConfig['batchPartition'], slurm_memory=impactConfig['batchMemory'], slurm_max_runtime=impactConfig['batchMaxRuntime'], htcondor_partition=impactConfig['batchPartition'], htcondor_memory=impactConfig['batchMemory'], htcondor_max_runtime=impactConfig['batchMaxRuntime'])
            tasks["CreateUnblindedFit"] = CreateUnblindedFit(variable=self.variable, output_dir=output_dir, year=self.year, batch_flavor=self.batch_flavor, version=self.variable if self.variable != '' else 'inclusive', workflow=self.batch_system)
            tasks["MggDistribution"] = MggDistribution(variable=self.variable, output_dir=output_dir, year=self.year, batch_flavor=self.batch_flavor, version=self.variable if self.variable != "" else "inclusive", workflow=mggConfig["execution"], slurm_partition=mggConfig['batchPartition'], slurm_memory=mggConfig['batchMemory'], slurm_max_runtime=mggConfig['batchMaxRuntime'], htcondor_partition=mggConfig['batchPartition'], htcondor_memory=mggConfig['batchMemory'], htcondor_max_runtime=mggConfig['batchMaxRuntime'], is_postfit=True)
        if convert_boolean_string(self.unblinded_covcorr):
            hesseConfig = config["combine_hesse"]
            tasks["UnblindedCovCorr"] = UnblindedCovCorr(variable=self.variable, output_dir=output_dir, year=self.year, batch_flavor=self.batch_flavor, version=self.variable if self.variable != '' else 'inclusive', workflow=hesseConfig["execution"], slurm_partition=hesseConfig['batchPartition'], slurm_memory=hesseConfig['batchMemory'], slurm_max_runtime=hesseConfig['batchMaxRuntime'], htcondor_partition=hesseConfig['batchPartition'], htcondor_memory=hesseConfig['batchMemory'], htcondor_max_runtime=hesseConfig['batchMaxRuntime'])
        if convert_boolean_string(self.pvalue):
            hesseConfig = config["combine_hesse"]
            tasks["PValueCalculation"] = PValueCalculation(variable=self.variable, output_dir=output_dir, year=self.year, batch_flavor=self.batch_flavor, version=self.variable if self.variable != '' else 'inclusive', workflow=self.batch_system, slurm_partition=hesseConfig['batchPartition'], slurm_memory=hesseConfig['batchMemory'], slurm_max_runtime=hesseConfig['batchMaxRuntime'], htcondor_partition=hesseConfig['batchPartition'], htcondor_memory=hesseConfig['batchMemory'], htcondor_max_runtime=hesseConfig['batchMaxRuntime'])
        if convert_boolean_string(self.asimov_fits):
            tasks["CreateAsimovFit"] = CreateAsimovFit(variable=self.variable, output_dir=output_dir, year=self.year, batch_flavor=self.batch_flavor, version=self.variable if self.variable != '' else 'inclusive', workflow=self.batch_system)
        if convert_boolean_string(self.asimov_impacts):
            tasks["AsimovImpactThirdStep"] = AsimovImpactThirdStep(variable=self.variable, output_dir=output_dir, year=self.year, batch_flavor=self.batch_flavor, version=self.variable if self.variable != '' else 'inclusive', workflow=self.batch_system)
        if convert_boolean_string(self.asimov_covcorr):
            hesseConfig = config["combine_hesse"]
            tasks["AsimovCovCorr"] = AsimovCovCorr(variable=self.variable, output_dir=output_dir, year=self.year, batch_flavor=self.batch_flavor, version=self.variable if self.variable != '' else 'inclusive', workflow=hesseConfig["execution"], slurm_partition=hesseConfig['batchPartition'], slurm_memory=hesseConfig['batchMemory'], slurm_max_runtime=hesseConfig['batchMaxRuntime'], htcondor_partition=hesseConfig['batchPartition'], htcondor_memory=hesseConfig['batchMemory'], htcondor_max_runtime=hesseConfig['batchMaxRuntime'])
        if convert_boolean_string(self.asimov_diff_spectra) and (self.variable != ''):
            tasks["CreateAsimovDiffSpectra"] = CreateDiffSpectra(variable=self.variable, output_dir=output_dir, year=self.year, batch_flavor=self.batch_flavor, batch_system=self.batch_system, is_unblinded=False)
        if convert_boolean_string(self.unblinded_diff_spectra) and (self.variable != ''):
            tasks["CreateUnblindedDiffSpectra"] = CreateDiffSpectra(variable=self.variable, output_dir=output_dir, year=self.year, batch_flavor=self.batch_flavor, batch_system=self.batch_system, is_unblinded=True)
        if (convert_boolean_string(self.asimov_diff_spectra) or convert_boolean_string(self.unblinded_diff_spectra)) and (self.variable == ''):
            print("Differential spectra can only be created for a specific variable. Please set the variable parameter to a valid value.")
            exit(1)
        if tasks == {}:
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

        if self.variable == '':
            fitFolderName = f'runFits_mu_fiducial'
        else:
            fitFolderName = f'runFits_{self.variable}'  
        
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
        
        if convert_boolean_string(self.unblinded_fits) or convert_boolean_string(self.unblinded_stage_three):
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
            
            for _, current_output_path in enumerate(output):
                output_paths.append(law.LocalFileTarget(current_output_path))
        
        if convert_boolean_string(self.unblinded_stage_one) or convert_boolean_string(self.unblinded_stage_two) or convert_boolean_string(self.unblinded_stage_three):
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

            for _, current_output_path in enumerate(output):
                output_paths.append(law.LocalFileTarget(current_output_path))
        
        if convert_boolean_string(self.unblinded_stage_two) or convert_boolean_string(self.unblinded_stage_three):
            if self.variable == '':
                reco_cats_with_bmw = ['best_resolution', 'medium_resolution', 'worst_resolution']
                cat_list = ["r"]
            else:
                reco_cats_with_bmw = [element for element in combineVariableDict[f'{self.year}'][self.variable]['catsStrWithBMW'] if "_".join(cat.split("_")[2:]) in element]
                cat_list = combineVariableDict[f'{self.year}'][f'{self.variable}']['paramStrNoOne']
            
            output = []
            for cat in cat_list:
                if convert_boolean_string(self.unblinded_stage_two):
                    output += [os.path.join(output_dir, 'Combine', fitFolderName, 'preFit', 'jsons')]
                    output += [os.path.join(output_dir, 'Combine', fitFolderName, 'preFit', 'jsons', f'catsWeights_sospb_{cat}_CMS_hgg_mass.json')]
                    
                    output += [os.path.join(output_dir, 'Combine', fitFolderName, 'preFit', f'SplusBModels_{cat}', f'_{cat}_{catWithBMW}_CMS_hgg_mass.pdf') for catWithBMW in reco_cats_with_bmw]
                    output += [os.path.join(output_dir, 'Combine', fitFolderName, 'preFit', f'SplusBModels_{cat}', f'_{cat}_{catWithBMW}_CMS_hgg_mass.png') for catWithBMW in reco_cats_with_bmw]
                    output += [os.path.join(output_dir, 'Combine', fitFolderName, 'preFit', f'SplusBModels_{cat}', f'_{cat}_all_CMS_hgg_mass.pdf')]
                    output += [os.path.join(output_dir, 'Combine', fitFolderName, 'preFit', f'SplusBModels_{cat}', f'_{cat}_all_CMS_hgg_mass.png')]
                    output += [os.path.join(output_dir, 'Combine', fitFolderName, 'preFit', f'SplusBModels_{cat}', f'_{cat}_wall_CMS_hgg_mass.pdf')]
                    output += [os.path.join(output_dir, 'Combine', fitFolderName, 'preFit', f'SplusBModels_{cat}', f'_{cat}_wall_CMS_hgg_mass.png')]
                else:
                    output += [os.path.join(output_dir, 'Combine', fitFolderName, 'postFit', 'jsons')]
                    output += [os.path.join(output_dir, 'Combine', fitFolderName, 'postFit', 'jsons', f'catsWeights_sospb_{cat}_CMS_hgg_mass.json')]
                    
                    output += [os.path.join(output_dir, 'Combine', fitFolderName, 'postFit', f'SplusBModels_{cat}', f'_{cat}_{catWithBMW}_CMS_hgg_mass.pdf') for catWithBMW in reco_cats_with_bmw]
                    output += [os.path.join(output_dir, 'Combine', fitFolderName, 'postFit', f'SplusBModels_{cat}', f'_{cat}_{catWithBMW}_CMS_hgg_mass.png') for catWithBMW in reco_cats_with_bmw]
                    output += [os.path.join(output_dir, 'Combine', fitFolderName, 'postFit', f'SplusBModels_{cat}', f'_{cat}_all_CMS_hgg_mass.pdf')]
                    output += [os.path.join(output_dir, 'Combine', fitFolderName, 'postFit', f'SplusBModels_{cat}', f'_{cat}_all_CMS_hgg_mass.png')]
                    output += [os.path.join(output_dir, 'Combine', fitFolderName, 'postFit', f'SplusBModels_{cat}', f'_{cat}_wall_CMS_hgg_mass.pdf')]
                    output += [os.path.join(output_dir, 'Combine', fitFolderName, 'postFit', f'SplusBModels_{cat}', f'_{cat}_wall_CMS_hgg_mass.png')]
            
            for _, current_output_path in enumerate(output):
                output_paths.append(law.LocalFileTarget(current_output_path))
        
        if convert_boolean_string(self.pvalue):
            if self.variable == '':
                print("P-value calculation is not supported for inclusive fits.")
                exit(1)
            else:
                output = [os.path.join(output_dir, 'Combine', fitFolderName, 'dataFit', f'higgsCombine.pvalue.MultiDimFit.mH125.38.root')]
                output += [os.path.join(output_dir, 'Combine', fitFolderName, f'pvalue.txt')]

            for _, current_output_path in enumerate(output):
                output_paths.append(law.LocalFileTarget(current_output_path))
        
        if convert_boolean_string(self.unblinded_covcorr):
            output = [os.path.join(output_dir, 'Combine', fitFolderName, 'hesse', 'Plots', 'data')]

            output += [os.path.join(output_dir, 'Combine', fitFolderName, 'hesse', 'Plots', 'data', f'corrMatrix_{self.variable}_syst_obs.pdf')]
            output += [os.path.join(output_dir, 'Combine', fitFolderName, 'hesse', 'Plots', 'data', f'corrMatrix_{self.variable}_syst_obs.png')]
            output += [os.path.join(output_dir, 'Combine', fitFolderName, 'hesse', 'Plots', 'data', f'covMatrix_{self.variable}_syst_obs.pdf')]
            output += [os.path.join(output_dir, 'Combine', fitFolderName, 'hesse', 'Plots', 'data', f'covMatrix_{self.variable}_syst_obs.png')]

            for _, current_output_path in enumerate(output):
                output_paths.append(law.LocalFileTarget(current_output_path))
                
        if convert_boolean_string(self.asimov_fits):
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

            for _, current_output_path in enumerate(output):
                output_paths.append(law.LocalFileTarget(current_output_path))

        if convert_boolean_string(self.asimov_impacts):
        
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

            for _, current_output_path in enumerate(output):
                output_paths.append(law.LocalFileTarget(current_output_path))

        if convert_boolean_string(self.asimov_covcorr):
            output = [os.path.join(output_dir, 'Combine', fitFolderName, 'hesse', 'Plots')]

            output += [os.path.join(output_dir, 'Combine', fitFolderName, 'hesse', 'Plots', f'corrMatrix_{self.variable}_syst.pdf')]
            output += [os.path.join(output_dir, 'Combine', fitFolderName, 'hesse', 'Plots', f'corrMatrix_{self.variable}_syst.png')]
            output += [os.path.join(output_dir, 'Combine', fitFolderName, 'hesse', 'Plots', f'covMatrix_{self.variable}_syst.pdf')]
            output += [os.path.join(output_dir, 'Combine', fitFolderName, 'hesse', 'Plots', f'covMatrix_{self.variable}_syst.png')]

            for _, current_output_path in enumerate(output):
                output_paths.append(law.LocalFileTarget(current_output_path))
            
        return output_paths
    
    def run(self):
        
        return True