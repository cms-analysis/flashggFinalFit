import law
import os
import ROOT
import re
import uproot
from collections import OrderedDict as od
import glob, shutil
import errno
import yaml

import pandas
import numpy as np

from commonTools import *
from commonObjects import *
from T2WSTools.STXS_tools import *
from T2WSTools.diff_tools import *

from framework import Task
from framework import HTCondorWorkflow, SlurmWorkflow

# Function to safely create a directory
def safe_mkdir(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

def leave():
  print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HGG TREES 2 WS (END) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
  exit(0)
  
def convert_boolean_string(string):
    if (string == "True") or (string == "true") or (string == True):
        return True
    else:
        return False

class Trees2WSSingleProcess(Task, HTCondorWorkflow, SlurmWorkflow, law.LocalWorkflow):#(law.Task): #(Task, HTCondorWorkflow, law.LocalWorkflow):
    input_paths = law.Parameter(description="Paths to the data input ROOT files")
    era = law.Parameter(description="Current era.")
    output_dir = law.Parameter(description="Path to the output directory")
    variable = law.Parameter(default='', description="Variable to be used for output folder naming")
    year = law.Parameter(default='2022', description="Year")
    apply_mass_cut = law.Parameter(default=False, description="Apply mass cut")
    mass_cut_range = law.Parameter(default='100,180', description="Mass cut range")
    # input_mass = law.Parameter(default='125', description="Input mass")
    # productionMode = law.Parameter(default='ggh', description="Production mode [ggh,vbf,vh,wh,zh,tth,thq,ggzh,bbh]")
    decayExt = law.Parameter(default='', description="Decay extension")
    doNNLOPS = law.Parameter(default=False, description="Add NNLOPS weight variable: NNLOPSweight")
    doSystematics = law.Parameter(default=False, description="Add systematics datasets to output WS")
    doSTXSSplitting = law.Parameter(default=False, description="Split output WS per STXS bin")
    doDiffSplitting = law.Parameter(default=False, description="Split output WS per differential bin")
    doInOutSplitting = law.Parameter(default=False, description="Split output WS into in/out fiducial based on some variable in the input trees (to be improved).")

    htcondor_job_kwargs_submit = {"spool": True}  
    
    def create_branch_map(self):
        # map branch indexes to ascii numbers from 97 to 122 ("a" to "z")
        mode_proc_mass_list = [
            (mode, mass, input_path)
            for mode, process in production_modes
            for mass in input_masses
            for input_path in glob.glob(f"{self.input_paths}/{process}_M-{mass}_{self.era}/*.root")
        ]
        branch_map = {i: mode_proc_mass for i, mode_proc_mass in enumerate(mode_proc_mass_list)}
        return branch_map

    def output(self):
        
        current_mode_proc_mass = self.branch_data
        
        productionMode = current_mode_proc_mass[0]
        input_mass = current_mode_proc_mass[1]
        input_path = current_mode_proc_mass[2]
               
        apply_mass_cut = convert_boolean_string(self.apply_mass_cut)
        doNNLOPS = convert_boolean_string(self.doNNLOPS)
        doSystematics = convert_boolean_string(self.doSystematics)
        doSTXSSplitting = convert_boolean_string(self.doSTXSSplitting)
        doDiffSplitting = convert_boolean_string(self.doDiffSplitting)
        doInOutSplitting = convert_boolean_string(self.doInOutSplitting)
        
        outputFileTargets = []
        if doInOutSplitting: fiducialIds = [True, False]
        else: fiducialIds = [0] # If we do not perform in/out splitting, we want to have one inclusive (for particle-level) process definition, our code int for that is zero

        if doInOutSplitting:

            for fiducialId in fiducialIds:
                                
                # In the end, the STXS and fiducial in/out splitting should maybe be harmonised, this looks a bit ugly
                
                if fiducialId == True: fidTag = "in"
                elif fiducialId == False: fidTag = "out"
                else: fidTag = "incl"

                # Define output workspace file
                if self.output_dir is not None:
                    outputWSDir = os.path.join(self.output_dir,"ws_{}_{}".format(dataToProc(productionMode), fidTag))
                else:
                    outputWSDir = os.path.join(os.path.dirname(input_path),"ws_{}_{}".format(dataToProc(productionMode), fidTag))
                if not os.path.exists(outputWSDir): os.system("mkdir -p %s"%outputWSDir)
                os.system("mkdir -p %s"%os.path.join(self.output_dir, 'filechecker'))
                outputWSFile = os.path.join(outputWSDir,re.sub(r"\.root","_{}_{}.root".format(dataToProc(productionMode), fidTag),os.path.basename(input_path)))                
                outputFileTargets.append(law.LocalFileTarget(os.path.join(self.output_dir, 'filechecker', f'{productionMode}_{input_mass}_{fidTag}.txt')))
                outputFileTargets.append(law.LocalFileTarget(outputWSFile))
            
        elif doSTXSSplitting:
            #STXS currently not implemented
            pass
                
        elif doDiffSplitting and not (self.variable == ''):
            varBins = [entry[1] for entry in differentialProcTable_[self.variable]]
            for currentBin in varBins:

                # Extract diffBin
                diffBin = productionMode + "_" + currentBin

                # Define output workspace file
                if self.output_dir is not None:
                    outputWSDir = os.path.join(self.output_dir,"ws_{}".format(diffBin))
                else:
                    outputWSDir = os.path.join(os.path.dirname(input_path),"ws_{}".format(diffBin))
                outputWSFile = os.path.join(outputWSDir,re.sub(r"\.root","_{}.root".format(diffBin),os.path.basename(input_path)))
                os.system("mkdir -p %s"%os.path.join(self.output_dir, 'filechecker'))
                outputFileTargets.append(law.LocalFileTarget(os.path.join(self.output_dir, 'filechecker', f'{productionMode}_{input_mass}_{currentBin}.txt')))
                outputFileTargets.append(law.LocalFileTarget(outputWSFile))        
        return outputFileTargets

    def run(self):
        
        current_mode_proc_mass = self.branch_data
        
        productionMode = current_mode_proc_mass[0]
        input_mass = current_mode_proc_mass[1]
        input_path = current_mode_proc_mass[2]
        
        apply_mass_cut = convert_boolean_string(self.apply_mass_cut)
        doNNLOPS = convert_boolean_string(self.doNNLOPS)
        doSystematics = convert_boolean_string(self.doSystematics)
        doSTXSSplitting = convert_boolean_string(self.doSTXSSplitting)
        doDiffSplitting = convert_boolean_string(self.doDiffSplitting)
        doInOutSplitting = convert_boolean_string(self.doInOutSplitting)
                
        # Create output path if it does not exist
        os.makedirs(self.output_dir, exist_ok=True)
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Production modes to skip theory weights: fill with 1's
        modesToSkipTheoryWeights = ['bbh','thq','thw']
        
        if self.variable == '':
            input_config = os.environ["ANALYSIS_PATH"] + f"/config/{self.year[:4]}_inclusive.yml"
        else:
            input_config = os.environ["ANALYSIS_PATH"] + f"/config/{self.year[:4]}_{self.variable}.yml"

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Extract options from config file:
        options = od()
        if input_config != '':
            if os.path.exists( input_config ):
                
                with open(input_config, 'r') as file:
                    config = yaml.safe_load(file)
                    
                config = config[f"trees2wsCfg"]
                inputTreeDir     = config['inputTreeDir']
                mainVars         = config['mainVars']
                stxsVar          = config['stxsVar']
                diffVar          = config['diffVar']
                systematicsVars  = config['systematicsVars']
                theoryWeightContainers = config['theoryWeightContainers']
                systematics      = config['systematics']
                cats             = config['cats']


            else:
                print( "[ERROR] %s config file does not exist. Leaving..."%input_config)
                leave()
        else:
            print( "[ERROR] Please specify config file to run from. Leaving..."%input_config)
            leave()
            
        # Function to add vars to workspace
        def add_vars_to_workspace(_ws=None,_data=None,_stxsVar=None):
            # Add intLumi var
            intLumi = ROOT.RooRealVar("intLumi","intLumi",1000.,0.,999999999.)
            intLumi.setConstant(True)
            getattr(_ws,'import')(intLumi)
            # Add vars specified by dataframe columns: skipping cat, stxsvar and type
            _vars = od()
            for var in _data.columns:
                if var in ['type','cat',_stxsVar]: continue
                if 'fiducial' in var: continue
                if "diff" in var: continue
                if var == "CMS_hgg_mass": 
                    _vars[var] = ROOT.RooRealVar(var,var,125.,100.,180.)
                    _vars[var].setBins(160)
                elif var == "dZ": 
                    _vars[var] = ROOT.RooRealVar(var,var,0.,-20.,20.)
                    _vars[var].setBins(40)
                elif var == "weight": 
                    _vars[var] = ROOT.RooRealVar(var,var,0.)
                else:
                    _vars[var] = ROOT.RooRealVar(var,var,1.,-999999,999999)
                    _vars[var].setBins(1)
                getattr(_ws,'import')(_vars[var],ROOT.RooFit.Silence())
            return _vars.keys()
        
        # Function to make RooArgSet
        def make_argset(_ws=None,_varNames=None):
            _aset = ROOT.RooArgSet()
            for v in _varNames: _aset.add(_ws.var(v))
            return _aset


        def create_workspace(df, sdf, outputWSFile, productionMode_string):
            # Open file and initiate workspace
            fout = ROOT.TFile(outputWSFile,"RECREATE")
            foutdir = fout.mkdir(inputWSName__.split("/")[0])
            foutdir.cd()
            ws = ROOT.RooWorkspace(inputWSName__.split("/")[1],inputWSName__.split("/")[1])
            
            # Add variables to workspace
            varNames = add_vars_to_workspace(ws,df,stxsVar)

            # Loop over cats
            for cat in cats:

                # a) make RooDataSets: type = nominal/notag
                mask = (df['cat']==cat)

                # Define RooDataSet
                dName = "%s_%s_%s_%s"%(productionMode_string,input_mass,sqrts__,cat)
                
                # Make argset
                aset = make_argset(ws,varNames)

                # Convert tree to RooDataset and add to workspace
                d = ROOT.RooDataSet(dName,dName,aset,'weight')
                
                # Loop over events in dataframe and add entry
                for row in df[mask][varNames].to_numpy():
                    for i, val in enumerate(row):
                        aset[i].setVal(val)
                    d.add(aset,aset.getRealValue("weight"))
                
                getattr(ws,'import')(d)

                if self.doSystematics:
                    # b) make RooDataHists for systematic variations
                    if cat == "NOTAG": continue
                    for s in systematics:
                        for direction in ['Up','Down']:
                            # Create mask for systematic variation
                            mask = (sdf['type']=='%s%s'%(s,direction))&(sdf['cat']==cat)
                            
                            # Define RooDataHist
                            hName = "%s_%s_%s_%s_%s%s01sigma"%(productionMode_string,input_mass,sqrts__,cat,s,direction)

                            # Make argset: drop weight column for histogrammed observables
                            systematicsVarsDropWeight = []
                            for var in systematicsVars:
                                if ('fiducial' in var) or ("diff" in var): continue
                                if var != "weight": systematicsVarsDropWeight.append(var)
                            aset = make_argset(ws,systematicsVarsDropWeight)
                            
                            h = ROOT.RooDataHist(hName,hName,aset)
                            for row, weight in zip(sdf[mask][systematicsVarsDropWeight].to_numpy(),sdf[mask]["weight"].to_numpy()):
                                for i, val in enumerate(row):
                                    aset[i].setVal(val)
                                h.add(aset,weight)
                            
                            # Add to workspace
                            getattr(ws,'import')(h)

            # Write WS to file
            ws.Write()

            # Close file and delete workspace from heap
            fout.Close()

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # For theory weights: create vars for each weight
        theoryWeightColumns = {}
        for ts, nWeights in theoryWeightContainers.items(): theoryWeightColumns[ts] = ["%s_%g"%(ts[:-1],i) for i in range(0,nWeights)] # drop final s from container name

        # If year == 2018, add HET
        if self.year == '2018': systematics.append("JetHEM")

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # UPROOT file
        f = uproot.open(input_path)
        if inputTreeDir == '': listOfTreeNames == f.keys()
        else: listOfTreeNames = f[inputTreeDir].keys()
        # If cats = 'auto' then determine from list of trees
        if cats == 'auto':
            cats = []
            for tn in listOfTreeNames:
                if "sigma" in tn: continue
                c = tn.split("_%s_"%sqrts__)[-1].split(";")[0]
                cats.append(c)
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # 1) Convert tree to pandas dataframe
        # Create dataframe to store all events in file
        data = pandas.DataFrame()
        if doSystematics: sdata = pandas.DataFrame()

        # Loop over categories: fill dataframe
        for cat in cats:
            print( " --> Extracting events from category: %s"%cat)
            if inputTreeDir == '': treeName = "%s_%s_%s_%s"%(productionMode,input_mass,sqrts__,cat)
            else: treeName = "%s/%s_%s_%s_%s"%(inputTreeDir,productionMode,input_mass,sqrts__,cat)
            print("    * tree: %s"%treeName)
            # Extract tree from uproot
            t = f[treeName]
            if t.num_entries == 0: continue
            
            # Convert tree to pandas dataframe
            dfs = {}
            
            # Theory weights
            for ts, tsColumns in theoryWeightColumns.items():
                if productionMode in modesToSkipTheoryWeights: 
                    dfs[ts] = pandas.DataFrame(np.ones(shape=(t.num_entries,theoryWeightContainers[ts])))
                else:
                    dfs[ts] = pandas.DataFrame(np.reshape(np.array(t[ts].array()),(t.num_entries,len(tsColumns))))
                dfs[ts].columns = tsColumns
                
            # Main variables to add to nominal RooDataSets
            # For wildcards use filter_name functionality
            mainVars_dropWildcards = []
            for var in mainVars:
                if "*" not in var:
                    mainVars_dropWildcards.append(var)
                
            dfs['main'] = t.arrays(mainVars_dropWildcards, library='pd')

            for var in mainVars:
                if "*" in var:
                    dfs[var] = t.arrays(filter_name=var, library='pd')

            # Concatenate current dataframes
            df = pandas.concat(dfs.values(), axis=1)

            # Add STXS splitting var if splitting necessary
            if doSTXSSplitting: 
                pass
                # df[stxsVar] = t.arrays(stxsVar, library='pd')

            # For experimental phase space
            df['type'] = 'nominal'
            
            # Add NNLOPS variable
            if (doNNLOPS):
                if productionMode == 'ggh': df['NNLOPSweight'] = t.arrays(['NNLOPSweight'], library='pd')
                else: df['NNLOPSweight'] = 1.

            # Add columns specifying category add to overall dataframe
            df['cat'] = cat
            data = pandas.concat([data,df], ignore_index=True, axis=0, sort=False)

            # For systematics trees: only for events in experimental phase space
            if doSystematics:
                sdf = pandas.DataFrame()
                for s in systematics:
                    print("    --> Systematic: %s"%re.sub("YEAR",self.year,s))
                    for direction in ['Up','Down']:
                        streeName = "%s_%s%s01sigma"%(treeName,s,direction)
                        # If year in streeName then replace by year being processed
                        streeName = re.sub("YEAR",self.year,streeName)
                        st = f[streeName]
                        if len(st)==0: continue
                        sdf = st.arrays(systematicsVars, library='pd')
                        sdf['type'] = "%s%s"%(s,direction)
                        # Add STXS splitting var if splitting necessary
                        if doSTXSSplitting: 
                            pass
                            # sdf[stxsVar] = st.arrays(stxsVar, library='pd')
                    
                        # Add column specifying category and add to systematics dataframe
                        sdf['cat'] = cat
                        sdata = pandas.concat([sdata,sdf], ignore_index=True, axis=0, sort=False)
            
        # If not splitting by STXS bin then add dummy column to dataframe
        if not doSTXSSplitting:
            data[stxsVar] = 'nosplit'  
            if self.doSystematics: sdata[stxsVar] = 'nosplit'



        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # 2) Convert pandas dataframe to RooWorkspace

        if doInOutSplitting: fiducialIds = data['fiducialGeometricFlag'].unique()
        else: fiducialIds = [0] # If we do not perform in/out splitting, we want to have one inclusive (for particle-level) process definition, our code int for that is zero
        
        if doInOutSplitting:

            for fiducialId in fiducialIds:
            
                if fiducialId == True: fidTag = "in"
                elif fiducialId == False: fidTag = "out"
                else: fidTag = "incl"

                if doInOutSplitting:
                    fiducial_mask = data['fiducialGeometricFlag'] == fiducialId
                    fiducial_mask_syst = sdata['fiducialGeometricFlag'] == fiducialId
                else:
                    fiducial_mask = data['CMS_hgg_mass'] > 0 # Basically a true mask because we are all inclusive
                    fiducial_mask_syst = sdata['CMS_hgg_mass'] > 0

                df = data[fiducial_mask]
                if doSystematics: 
                    sdf = sdata[fiducial_mask_syst]

                # Define output workspace file
                if self.output_dir is not None:
                    outputWSDir = os.path.join(self.output_dir, "ws_{}_{}".format(dataToProc(productionMode), fidTag)) # Multiple slashes are normalised away, no worries ("../test/" and "../test" are equivalent)
                else:
                    outputWSDir = os.path.join(
                        os.path.dirname(input_path),
                        "ws_{}_{}".format(dataToProc(productionMode), fidTag)
                    )
                if not os.path.exists(outputWSDir): os.system("mkdir -p %s"%outputWSDir)
                os.system("mkdir -p %s"%os.path.join(self.output_dir, 'filechecker'))
                outputWSFile = os.path.join(outputWSDir,re.sub(r"\.root","_{}_{}.root".format(dataToProc(productionMode), fidTag),os.path.basename(input_path)))
                print(" --> Creating output workspace: (%s)"%outputWSFile)
                
                productionMode_string = productionMode + "_" + fidTag # This is, for example, "ggh_in"

                create_workspace(df, sdf, outputWSFile, productionMode_string)
                
                # Check if output workspace is > 2000 bytes (== file empty)
                try:
                    file_size = os.path.getsize(outputWSFile)  # Get the file size in bytes
                    if file_size > 2000:
                        with open(os.path.join(self.output_dir, 'filechecker', f'{productionMode}_{input_mass}_{fidTag}.txt'), 'w') as f:
                            pass
                except OSError:
                    # Handle the case where the file does not exist or is inaccessible
                    print(f"Error creating file. Probably I/O error.")
                    return False


        elif (doSTXSSplitting):
            
            for stxsId in data[stxsVar].unique():
                df = data[data[stxsVar]==stxsId]
                sdf = None
                if doSystematics: sdf = sdata[sdata[stxsVar]==stxsId]

                # Extract stxsBin
                stxsBin = flashggSTXSDict[int(stxsId)]
                if productionMode == "wh": 
                    if "QQ2HQQ" in stxsBin: stxsBin = re.sub("QQ2HQQ","WH2HQQ",stxsBin)
                elif productionMode == "zh": 
                    if "QQ2HQQ" in stxsBin: stxsBin = re.sub("QQ2HQQ","ZH2HQQ",stxsBin)
                # ggZH: split by decay mode
                elif productionMode == "ggzh":
                    if self.decayExt == "_ZToQQ": stxsBin = re.sub("GG2H","GG2HQQ",stxsBin)
                    elif self.decayExt == "_ZToNuNu": stxsBin = re.sub("GG2HLL","GG2HNUNU",stxsBin)
                # For tHL split into separate bins for tHq and tHW
                elif productionMode == "thq": stxsBin = re.sub("TH","THQ",stxsBin)
                elif productionMode == 'thw': stxsBin = re.sub("TH","THW",stxsBin)

                # Define output workspace file
                outputWSDir = os.path.join(
                    os.path.dirname(input_path),
                    "ws_{}".format(stxsBin)
                )
                if not os.path.exists(outputWSDir): os.system("mkdir -p %s"%outputWSDir)
                os.system("mkdir -p %s"%os.path.join(self.output_dir, 'filechecker'))
                outputWSFile = os.path.join(outputWSDir,re.sub(r"\.root","_{}.root".format(stxsBin),os.path.basename(input_path)))
                print(" --> Creating output workspace for STXS bin: %s (%s)"%(stxsBin,outputWSFile))

                productionMode_string = productionMode

                create_workspace(df, sdf, outputWSFile, productionMode_string)
                
                # Check if output workspace is > 2000 bytes (== file empty)
                try:
                    file_size = os.path.getsize(outputWSFile)  # Get the file size in bytes
                    if file_size > 2000:
                        with open(os.path.join(self.output_dir, 'filechecker', f'{productionMode}_{input_mass}_{stxsBin}.txt'), 'w') as f:
                            pass
                except OSError:
                    # Handle the case where the file does not exist or is inaccessible
                    print(f"Error creating file. Probably I/O error.")
                    return False

        elif doDiffSplitting:
            
            for diffId in data[diffVar].unique():
                # diffId should be a gen-level pt bin
                df = data[data[diffVar]==diffId]
                sdf = None
                if doSystematics: sdf = sdata[sdata[diffVar]==diffId]

                # For the moment, skip these events (as their count is usually very small)
                if int(diffId) == 0: continue

                # Extract diffBin
                currentBin = getBinNameByHiggsDNANumber(self.variable, int(diffId))
                diffBin = productionMode + "_" + currentBin
                print("diffBin", diffBin)

                # Define output workspace file
                if self.output_dir is not None:
                    outputWSDir = os.path.join(
                        self.output_dir,
                        "ws_{}".format(diffBin)
                    )
                else:
                    outputWSDir = os.path.join(
                        os.path.dirname(input_path),
                        "ws_{}".format(diffBin)
                    )
                if not os.path.exists(outputWSDir): os.system("mkdir -p %s"%outputWSDir)
                os.system("mkdir -p %s"%os.path.join(self.output_dir, 'filechecker'))
                outputWSFile = os.path.join(outputWSDir, re.sub(r"\.root","_{}.root".format(diffBin),os.path.basename(input_path)))
                print(" --> Creating output workspace for differential bin: %s (%s)"%(diffBin,outputWSFile))

                productionMode_string = productionMode

                create_workspace(df, sdf, outputWSFile, productionMode_string)
        
                # Check if output workspace is > 2000 bytes (== file empty)
                try:
                    file_size = os.path.getsize(outputWSFile)  # Get the file size in bytes
                    if file_size > 2000:
                        print(os.path.join(self.output_dir, 'filechecker', f'{productionMode}_{input_mass}_{currentBin}.txt'))
                        with open(os.path.join(self.output_dir, 'filechecker', f'{productionMode}_{input_mass}_{currentBin}.txt'), 'w') as f:
                            pass
                except OSError:
                    # Handle the case where the file does not exist or is inaccessible
                    print(f"Error creating file. Probably I/O error.")
                    return False
        

class Trees2WS(law.Task):
    output_dir = law.Parameter(default = '', description="Path to the output directory")
    variable = law.Parameter(default='', description="Variable to be used for output folder naming")
    year = law.Parameter(default='2022', description="Year")
    
    def requires(self):
        # req() is defined on all tasks and handles the passing of all parameter values that are
        # common between the required task and the instance (self)
        
        # Load the input configuration
        if self.variable == '':
            input_config = os.environ["ANALYSIS_PATH"] + f"/config/{self.year}_inclusive.yml"
        else:
            input_config = os.environ["ANALYSIS_PATH"] + f"/config/{self.year}_{self.variable}.yml"
        
        with open(input_config, 'r') as file:
            config = yaml.safe_load(file)
        if self.output_dir == '':
            output_dir = config["outputFolder"]
        else:
            output_dir = self.output_dir
        input_paths = config["inputFiles"]["Trees2WS"]
        
        config = config["trees2wsCfg"]
                
        doSTXSSplitting = convert_boolean_string(config["doSTXSSplitting"])
        doDiffSplitting = convert_boolean_string(config["doDiffSplitting"])
        doInOutSplitting = convert_boolean_string(config["doInOutSplitting"])
        doSystematics = convert_boolean_string(config["doSystematics"])
        mass_cut = convert_boolean_string(config["apply_mass_cut"])
        mass_cut_r = config["mass_cut_range"]

        tasks = []
        
        era_list = [
        (era, self.variable, input_paths)
        for era in allErasMap[f"{self.year}"]
        ]
    
        i = 1
        for era, var, path_to_root_files in era_list:
            if var == '':
                current_output_path = output_dir + "/input_output_{}{}".format(self.year, era)
            else:
                current_output_path = output_dir + "/input_output_{}_{}{}".format(var, self.year, era)
                            
            tasks.append(Trees2WSSingleProcess(input_paths=path_to_root_files, era=era, apply_mass_cut=mass_cut, mass_cut_range=mass_cut_r, year=f"{self.year}{era}", doSystematics=doSystematics, doDiffSplitting=doDiffSplitting, doSTXSSplitting=doSTXSSplitting, doInOutSplitting=doInOutSplitting, output_dir=current_output_path, variable=var, version=f"v{i}", workflow=config['execution']))
            i += 1
        
        return tasks    
    def output(self):
        
        # returns output folder
        if self.variable == '':
            input_config = os.environ["ANALYSIS_PATH"] + f"/config/{self.year}_inclusive.yml"
        else:
            input_config = os.environ["ANALYSIS_PATH"] + f"/config/{self.year}_{self.variable}.yml"
        
        with open(input_config, 'r') as file:
            config = yaml.safe_load(file)

        if self.output_dir == '':
            output_dir = config["outputFolder"]
        else:
            output_dir = self.output_dir
        
        input_paths = config["inputFiles"]["Trees2WS"]
        
        era_list_with_variable = [
            (era, self.variable)
            for era in allErasMap[f"{self.year}"]
        ]
        outputFolders = []
        for era, var in era_list_with_variable:
            if var == '':
                current_output_path = output_dir + "/input_output_{}{}".format(self.year, era)
            else:
                current_output_path = output_dir + "/input_output_{}_{}{}".format(var, self.year, era)
                
            outputFolders.append(law.LocalFileTarget(current_output_path + '/ws_signal'))
        
        return outputFolders
    
    def run(self):
        
        print("Trees2WS ran through. Moving output to the subdirectory ./ws_signal")
        
        if self.variable == '':
            input_config = os.environ["ANALYSIS_PATH"] + f"/config/{self.year}_inclusive.yml"
        else:
            input_config = os.environ["ANALYSIS_PATH"] + f"/config/{self.year}_{self.variable}.yml"
        
        with open(input_config, 'r') as file:
            config = yaml.safe_load(file)

        if self.output_dir == '':
            output_dir = config["outputFolder"]
        else:
            output_dir = self.output_dir
        
        era_list_with_variable = [
            (era, self.variable)
            for era in allErasMap[f"{self.year}"]
        ]
        
        outputFolders = []
        for era, var in era_list_with_variable:
            if var == '':
                current_output_path = output_dir + "/input_output_{}{}".format(self.year, era)
            else:
                current_output_path = output_dir + "/input_output_{}_{}{}".format(var, self.year, era)
            outputFolders.append(current_output_path)

            
        for currentEra in outputFolders:
            # Create ws_signal folder
            dst_folder = currentEra + "/ws_signal"
            safe_mkdir(dst_folder)
            
            # Copy files to ws_signal
            src_file_list = glob.glob(os.path.join(currentEra, "ws_*", "*"))
            for currentFile in src_file_list:
                if not os.path.samefile(currentFile, dst_folder):
                    shutil.copy2(currentFile, dst_folder)
                else:
                    print(f"Skip copying {currentFile} since it is already in ws_signal.")
            
        print("Copy completed.")

        return True
    
    