# Script to convert data trees to RooWorkspace (compatible for finalFits)
# Assumes tree names of the format:
# * Data_<sqrts>_category
import os, sys, re
from optparse import OptionParser
from collections import OrderedDict as od
from importlib import import_module

import json
import ROOT
import pandas as pd
import numpy as np

from commonTools import *
from commonObjects import *
from tools.STXS_tools import *

def get_options():
    parser = OptionParser()
    parser.add_option('--inputConfig', dest='inputConfig', default="", help='Input config file')
    parser.add_option('--inputMass', dest='inputMass', default="125", help='Higgs mass')
    parser.add_option('--inputTreeFile',dest='inputTreeFile', default="./output_0.root", help='Input tree file')
    parser.add_option('--outputWSDir',dest='outputWSDir', default=None, help='Output dir (default is same as input dir)')
    parser.add_option('--applyMassCut',dest='applyMassCut', default=False, action="store_true", help='Apply cut on CMS_hgg_mass')
    parser.add_option('--massCutRange',dest='massCutRange', default='100,180', help='CMS_hgg_mass cut range')
    parser.add_option('--categorisationConfig',default='category_STXS_stage1p2.json')
    return parser.parse_args()

(opt, args) = get_options()

def leave():
    print("~~~~~~~~~~~~~~~~~~~~~~~~~ SCRIPT END ~~~~~~~~~~~~~~~~~~~~~~~~~")
    exit(0)

# Load config
if opt.inputConfig == '' or not os.path.exists(opt.inputConfig):
    print(f"[ERROR] Config file {opt.inputConfig} not found.")
    leave()

_cfg = import_module(re.sub(".py$", "", opt.inputConfig)).trees2wsCfg

inputTreeDir     = _cfg['inputTreeDir'].rstrip('/')
dataVars         = _cfg['dataVars']
stxsVar          = _cfg['stxsVar']
cats             = _cfg['cats']

with open(opt.categorisationConfig, "r") as f:
        cat_dict = json.load(f)
merged=pd.DataFrame([])
for file in glob.glob(opt.inputTreeFile+'/*/*.parquet'):
    merged = pd.concat([merged,pd.read_parquet(file)])

# Auto-detect categories from .parquet files in inputTreeFile directory
if cats == 'auto':
    if not os.path.isdir(opt.inputTreeFile):
        print(f"[ERROR] Input directory '{opt.inputTreeFile}' does not exist.")
        leave()

    cats = []
    for cat in merged.pred_ia.unique():
        if cat!=0:
            cats.append(cat_dict['cat_dict'][str(cat)])

    if not cats:
        print(f"[ERROR] No parquet files found in '{opt.inputTreeFile}'")
        leave()
    else:
        print(f"[INFO] Detected categories: {cats}")

cats=list(cat_dict['cat_dict'].values() )# ensure ALL cats are included



# Combine data
data = pd.DataFrame()

merged['cat'] = merged['pred_ia'].map(str).map(cat_dict['cat_dict'])
data=merged.copy()
# ~~~~~~~ RooWorkspace Helpers ~~~~~~~
def add_vars_to_workspace(ws, df, stxsVar):
    intLumi = ROOT.RooRealVar("intLumi", "intLumi", 1000., 0., 999999999.)
    intLumi.setConstant(True)
    getattr(ws, 'import')(intLumi)

    rvars = od()
    for col in df.columns:
        if col in ['cat', 'type', stxsVar, '']: continue
        if col == "CMS_hgg_mass":
            rvar = ROOT.RooRealVar(col, col, 125., 100., 180.)
            rvar.setBins(160)
        elif col == "dZ":
            rvar = ROOT.RooRealVar(col, col, 0., -20., 20.)
            rvar.setBins(40)
        elif col == "weight":
            rvar = ROOT.RooRealVar(col, col, 0.)
        else:
            rvar = ROOT.RooRealVar(col, col, 1., -999999, 999999)
            rvar.setBins(1)
        getattr(ws, 'import')(rvar, ROOT.RooFit.Silence())
        rvars[col] = rvar
    return list(rvars.keys())

def make_argset(ws, var_names):
    aset = ROOT.RooArgSet()
    for name in var_names:
        aset.add(ws.var(name))
    return aset

print('A')
data[stxsVar]=stxsVar
# ~~~~~~~ RooWorkspace Creation ~~~~~~~
for stxsId in data[stxsVar].unique():
    print('B')
    df = data[data[stxsVar] == stxsId]

    

    output_dir = f"{opt.inputTreeFile}/ws_data"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"allData_data.root")
    print(f"[INFO] Creating workspace: {output_file}")

    fout = ROOT.TFile(output_file, "RECREATE")

    foutdir = fout.mkdir(inputTreeDir)
    foutdir.cd()  # IMPORTANT: switch to that directory

    ws = ROOT.RooWorkspace("cms_hgg_13TeV", "cms_hgg_13TeV")

    
    if 'mass' in df.columns:
        df = df.rename(columns={'mass': 'CMS_hgg_mass'})
    reduced_df = df[dataVars]
    

    var_names = add_vars_to_workspace(ws, reduced_df, stxsVar)
    # for cat in cats:
        
        
    #     df_cat = df[df['cat'] == cat]
    #     print(f"[DEBUG] Dataset for category '{cat}' has {len(df_cat)} events before dropping NaNs.")
    #     print(f"[DEBUG] Columns available: {df_cat.columns.tolist()}")
    #     print(f"[DEBUG] Variables expected: {var_names}")
    #     aset = make_argset(ws, var_names)
    #     dset_name = f"{opt.productionMode}_{opt.inputMass}_{opt.year}_{cat}"
    #     dset = ROOT.RooDataSet(dset_name, dset_name, aset, ROOT.RooFit.WeightVar("weight"))
    #     numeric_var_names = [v for v in var_names if pd.api.types.is_numeric_dtype(df_cat[v])]
        
    #     df_cat[var_names] = df_cat[var_names].apply(pd.to_numeric, errors='coerce')
    #     df_cat = df_cat.dropna(subset=var_names)

    #     for row in df_cat[var_names].to_numpy():
    #         for i, val in enumerate(row):
    #             aset[i].setVal(val)
    #         dset.add(aset, aset.getRealValue("weight"))
    #     getattr(ws, 'import')(dset)

    for cat in cats:
        
        
        
        df_cat = df[df['cat'] == cat]

        
        

        aset = make_argset(ws, var_names)  # full list (workspace needs everything)
        cat_renamed=cat#'_'.join(cat.split('_')[1:-1])
        dset_name = f"Data_13TeV_{cat_renamed}"
        dset = ROOT.RooDataSet(dset_name, dset_name, aset, ROOT.RooFit.WeightVar("weight"))

        # Only try to convert numeric columns
        numeric_var_names = [v for v in var_names if v in df_cat.columns and pd.api.types.is_numeric_dtype(df_cat[v])]
        df_cat[numeric_var_names] = df_cat[numeric_var_names].apply(pd.to_numeric, errors='coerce')
        df_cat = df_cat.dropna(subset=numeric_var_names)

        print(f"[INFO] Category {cat} has {len(df_cat)} entries after cleaning.")

        for row in df_cat[numeric_var_names].itertuples(index=False, name=None):
            for name, val in zip(numeric_var_names, row):
                var = aset.find(name)
                if var:  # safeguard
                    var.setVal(float(val))
                
            dset.add(aset, aset.find("weight").getVal())

        getattr(ws, 'import')(dset)


    print(ws)
    ws.Print('v')
    ws.Write()
    fout.Close()

print("~~~~~~~~~~~~~~~~~~~~~~~~~ ALL WORKSPACES DONE ~~~~~~~~~~~~~~~~~~~~~~~~~")