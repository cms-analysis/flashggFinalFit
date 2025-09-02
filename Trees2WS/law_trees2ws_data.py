import law
import os
import ROOT
import uproot
from collections import OrderedDict as od
import yaml
import subprocess
import shutil

from commonTools import *
from commonObjects import *

from framework import Task
from framework import HTCondorWorkflow, SlurmWorkflow

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

class Trees2WSData(Task, HTCondorWorkflow, SlurmWorkflow, law.LocalWorkflow):
    # input_path = law.Parameter(description="Path to the data input ROOT file")
    output_dir = law.Parameter(default = '', description="Path to the output directory")
    variable = law.Parameter(default='', description="Variable to be used for output folder naming")
    year = law.Parameter(default='2022', description="Year")
    apply_mass_cut = law.Parameter(default=False, description="Apply mass cut")
    mass_cut_range = law.Parameter(default='100,180', description="Mass cut range")
    batch_flavor = law.Parameter(default="htcondor", description="Batch system to use")

    def create_branch_map(self):
        branch_map = {i: val for i, val in enumerate(range(1))}
        return branch_map

    def output(self):

        # Load the input configuration
        if self.variable == '':
            input_config = os.path.join(os.environ["ANALYSIS_PATH"], f"config/{self.year}_inclusive.yml")
        else:
            input_config = os.path.join(os.environ["ANALYSIS_PATH"], f"config/{self.year}_{self.variable}.yml")

        if not os.path.exists(input_config):
            print(f"[ERROR] {input_config} does not exist. Exiting...")
            return

        # Import the configuration options from the config file
        with open(input_config, 'r') as file:
            config = yaml.safe_load(file)
        if self.output_dir == '':
            output_dir = config["outputFolder"]
        else:
            output_dir = self.output_dir

        if self.variable == '':
            ws_dir = os.path.join(output_dir, 'input_output_data', f"input_output_data_{self.year}/ws/")
        else:
            ws_dir = os.path.join(output_dir, 'input_output_data', f"input_output_data_{self.variable}_{self.year}/ws/")

        return law.LocalFileTarget(os.path.join(ws_dir, "allData.root"))

    def run(self):

        # Load the input configuration
        if self.variable == '':
            input_config = os.path.join(os.environ["ANALYSIS_PATH"], f"config/{self.year}_inclusive.yml")
        else:
            input_config = os.path.join(os.environ["ANALYSIS_PATH"], f"config/{self.year}_{self.variable}.yml")

        if not os.path.exists(input_config):
            print(f"[ERROR] {input_config} does not exist. Exiting...")
            return

        # Import the configuration options from the config file
        with open(input_config, 'r') as file:
            config = yaml.safe_load(file)
        if self.output_dir == '':
            output_dir = config["outputFolder"]
        else:
            output_dir = self.output_dir
        
        if self.batch_flavor == "slurm/psi":
            # Have to use /scratch/batch_username/ for slurm/psi
            os.environ["TARGET_PATH"] = f"/scratch/{os.environ['USER']}/{os.environ['SLURM_JOB_ID']}"
            temp_output_dir = os.environ["TARGET_PATH"]
        else:
            temp_output_dir = output_dir
            
        # Step 1: Create the output directory if it doesn't exist
        if self.variable == '':
            temp_ws_dir = os.path.join(temp_output_dir, 'input_output_data', f"input_output_data_{self.year}/ws/")
        else:
            temp_ws_dir = os.path.join(temp_output_dir, 'input_output_data', f"input_output_data_{self.variable}_{self.year}/ws/")

        if self.batch_flavor == "slurm/psi":
            if self.variable == '':
                final_ws_dir = os.path.join(output_dir, 'input_output_data', f"input_output_data_{self.year}/ws/")
            else:
                final_ws_dir = os.path.join(output_dir, 'input_output_data', f"input_output_data_{self.variable}_{self.year}/ws/")
            # Have to use the xrdfs for the pnfs file system while on PSI Tier 3.
            execute_command([f'xrdfs root://t3dcachedb03.psi.ch:1094/ mkdir -p {final_ws_dir}'], shell=True)

        os.makedirs(temp_ws_dir, exist_ok=True)
            
        input_path = config["inputFiles"]["Trees2WSData"]
        
        config = config[f"trees2wsCfg"]
        input_tree_dir = config['inputTreeDir']
        data_vars = config['dataVars']
        categories = config['cats']
        apply_mass_cut = config["apply_mass_cut"]
        massCutRange = config["mass_cut_range"]
        

        # Step 2: Convert data trees to RooWorkspace
        # Open the input ROOT file
        f = uproot.open(input_path)
        list_of_tree_names = f.keys() if input_tree_dir == '' else f[input_tree_dir].keys()

        if categories == 'auto':
            categories = []
        for tn in list_of_tree_names:
            if "sigma" in tn: continue
            c = tn.split("_%s_"%sqrts__)[-1].split(";")[0]
            categories.append(c)
            
        f = ROOT.TFile(input_path)

        # Create ROOT output workspace
        output_ws_file = os.path.join(temp_ws_dir, f"allData_{self.year}.root")
        fout = ROOT.TFile(output_ws_file, "RECREATE")
        foutdir = fout.mkdir(inputWSName__.split("/")[0])
        foutdir.cd()
        ws = ROOT.RooWorkspace(inputWSName__.split("/")[1],inputWSName__.split("/")[1])

        # Function to add variables to workspace
        def add_vars_to_workspace(_ws, _dataVars):
            intLumi = ROOT.RooRealVar("intLumi", "intLumi", 1000., 0., 999999999.)
            intLumi.setConstant(True)
            getattr(_ws, 'import')(intLumi)
            _vars = od()
            for var in _dataVars:
                if var == "CMS_hgg_mass":
                    _vars[var] = ROOT.RooRealVar(var, var, 125., 100., 180.)
                    _vars[var].setBins(160)
                elif var == "dZ":
                    _vars[var] = ROOT.RooRealVar(var, var, 0., -20., 20.)
                    _vars[var].setBins(40)
                elif (var == "weight"):
                    _vars[var] = ROOT.RooRealVar(var, var, 0.)
                else:
                    _vars[var] = ROOT.RooRealVar(var, var, 1., -999999, 999999)
                    _vars[var].setBins(1)
                getattr(_ws, 'import')(_vars[var], ROOT.RooFit.Silence())
            return _vars.keys()

        # Add variables to the workspace
        var_names = add_vars_to_workspace(ws, data_vars)

        # Function to make RooArgSet
        def make_argset(_ws, _varNames):
            _aset = ROOT.RooArgSet()
            for v in _varNames:
                _aset.add(_ws.var(v))
            return _aset

        # Make the argument set
        aset = make_argset(ws, var_names)
        
        # Loop over categories and extract data
        for cat in categories:
            print(" --> Extracting events from category: %s"%cat)
            if input_tree_dir == '': treeName = "Data_%s_%s"%(sqrts__,cat)
            else: treeName = "%s/Data_%s_%s"%(input_tree_dir,sqrts__,cat)
            print("    * tree: %s"%treeName)
            t = f.Get(treeName)

            # Define dataset for the category
            dname = "Data_%s_%s"%(sqrts__,cat)  
            d = ROOT.RooDataSet(dname, dname, aset, 'weight')
                
            # Loop over events in the tree and add to the dataset
            for ev in t:
                if self.apply_mass_cut:
                    if(getattr(ev,"CMS_hgg_mass") < float(massCutRange.split(",")[0])) | (getattr(ev,"CMS_hgg_mass") > float(massCutRange.split(",")[1])): continue
                for var in data_vars: 
                    if var == "weight": continue
                    # if convert_boolean_string(self.bootstrap_flag) == True:
                    #     if var == "weight_bootstrap_%s"%bootstrap_index: continue
                    if "weight_bootstrap" in var:
                        branch = t.GetBranch(var)
                        leaf = branch.GetLeaf(var)
                        branch.GetEntry(ev.GetReadEntry())
                        value = int(leaf.GetValue())
                    else:
                        value = getattr(ev, var)
                    ws.var(var).setVal(value)
                    d.add(aset,1.)

            # Add dataset to the workspace
            getattr(ws, 'import')(d)

        # Write the workspace to the output file
        ws.Write()
        fout.Close()

        # Step 3: Rename the output file
        all_data_file = os.path.join(temp_ws_dir, "allData.root")
        os.rename(output_ws_file, all_data_file)
        print(f"Workspace written and renamed to {all_data_file}")
        
        if self.batch_flavor == "slurm/psi":
            if "/work" in output_dir:
                slurm_copy_command = [
                    'cp', '-rf',
                    f'{all_data_file}',
                    f'{final_ws_dir}/allData.root'
                ]
            else:
                # Copying output files to final destination on the /pnfs.
                slurm_copy_command = [
                    'xrdcp', '-rf',
                    f'{all_data_file}',
                    'root://t3dcachedb03.psi.ch:1094//' + f'{final_ws_dir}' + 'allData.root'
                ]
            print(slurm_copy_command)
            execute_command(slurm_copy_command)
            # Cleaning up scratch space.
            shutil.rmtree(temp_output_dir)