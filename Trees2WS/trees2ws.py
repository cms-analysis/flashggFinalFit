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
    parser.add_option('--productionMode', dest='productionMode', default="ggh", help='Production mode')
    parser.add_option('--year', dest='year', default="2016", help='Year')
    parser.add_option('--decayExt', dest='decayExt', default='', help='Decay extension')
    parser.add_option('--doNNLOPS', dest='doNNLOPS', default=False, action="store_true", help='Add NNLOPS weight')
    parser.add_option('--doSystematics', dest='doSystematics', default=False, action="store_true", help='Add systematics')
    parser.add_option('--doSTXSSplitting', dest='doSTXSSplitting', default=False, action="store_true", help='Split WS by STXS bin')
    parser.add_option('--categorisationConfig',default='category_STXS_stage1p2.json')
    parser.add_option('-v',default=False,action="store_true")
    parser.add_option('--skiplength',default=10000000000)
    parser.add_option('--reduceprocs',default=[])
    return parser.parse_args()

(opt, args) = get_options()

proc=opt.inputTreeFile.split('/')[-2]


if proc in opt.reduceprocs:
    skip_len=int(opt.skiplength)
else:
    skip_len=10000000000000000000

def leave():
    print("~~~~~~~~~~~~~~~~~~~~~~~~~ SCRIPT END ~~~~~~~~~~~~~~~~~~~~~~~~~")
    exit(0)

# Load config
if opt.inputConfig == '' or not os.path.exists(opt.inputConfig):
    print(f"[ERROR] Config file {opt.inputConfig} not found.")
    leave()

_cfg = import_module(re.sub(".py$", "", opt.inputConfig)).trees2wsCfg

inputTreeDir     = _cfg['inputTreeDir'].rstrip('/')
mainVars         = _cfg['mainVars']
stxsVar          = _cfg['stxsVar']
systematicsVars  = _cfg['systematicsVars']
theoryWeightContainers = _cfg['theoryWeightContainers']
systematics      = _cfg['systematics']
cats             = _cfg['cats']

# If STXS var is not defined, disable splitting
if not stxsVar:
    opt.doSTXSSplitting = False
    stxsVar = 'nosplit'
    print("[INFO] STXS variable not defined. Disabling STXS splitting.")

# CHANGING STRUCTURE
import pyarrow.parquet as pq
import glob
import random

def fast_sample_single_file(dirpath, n):
    # take only nominal, non-systematic files
    files = [
        f for f in glob.glob(f"{dirpath}/*.parquet")
        if "Up" not in f and "Down" not in f and "ws_" not in f
    ]

    if not files:
        return pd.DataFrame()

    # pick ONE random file
    f = random.choice(files)
    pf = pq.ParquetFile(f)

    dfs = []
    total = 0

    # iter_batches lets you stop early
    for batch in pf.iter_batches(batch_size=20000):
        df = batch.to_pandas()
        dfs.append(df)
        total += len(df)
        if total >= n:
            break

    return pd.concat(dfs).iloc[:n]

if skip_len < 1e15:  # skiplen active
    merged = fast_sample_single_file(opt.inputTreeFile, skip_len)
else:
    merged = fast_sample_single_file(opt.inputTreeFile,skip_len) 
print('nominal merged')
# Auto-detect categories from .parquet files in inputTreeFile directory
if cats == 'auto':
    if not os.path.isdir(opt.inputTreeFile):
        print(f"[ERROR] Input directory '{opt.inputTreeFile}' does not exist.")
        leave()

    
    # for f in os.listdir(opt.inputTreeFile):
    #     if f.endswith(".parquet"):
    #         cats.append(f.replace(".parquet", ""))
    
    with open(opt.categorisationConfig, "r") as f:
        cat_dict = json.load(f)

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

# Add HEM for 2018
if opt.year == '2018':
    systematics.append("JetHEM")

# Theory weight names
modesToSkipTheoryWeights = ['bbh', 'thq', 'thw']
theoryWeightColumns = {
    ts: [f"{ts[:-1]}_{i}" for i in range(n)] for ts, n in theoryWeightContainers.items()
}



merged['cat'] = merged['pred_ia'].map(str).map(cat_dict['cat_dict'])
merged['type'] = 'nominal'
data = merged.copy()
# Ensure STXS var
if stxsVar not in data.columns:
    data[stxsVar] = 'nosplit'
# # Combine data
# data = pd.DataFrame()

# for cat in cats:
#     # parquet_path = os.path.join(opt.inputTreeFile, f"{cat}.parquet")
#     # print(f"[INFO] Loading {parquet_path}")
#     # if not os.path.exists(parquet_path):
#     #     print(f"[WARNING] Missing file: {parquet_path}. Skipping...")
#     #     continue
    

#     # df = pd.read_parquet(parquet_path)
#     df= merged
#     if df.empty:
#         print(f"[WARNING] Empty parquet: {parquet_path}")
#         continue

#     

#     # Add theory weight cols if missing
#     for ts, cols in theoryWeightColumns.items():
#         for col in cols:
#             if col not in df.columns:
#                 df[col] = 1.0 if opt.productionMode in modesToSkipTheoryWeights else 0.0

#     # Metadata
    
#     df['cat'] = df['pred'].map(str).map(cat_dict['cat_dict'])
#     # print(f'cat==={}')
#     df['type'] = 'nominal'
#     if opt.doNNLOPS and "NNLOPSweight" not in df.columns:
#         df["NNLOPSweight"] = 1.0

#     data = pd.concat([data, df], ignore_index=True)

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

# ~~~~~~~ RooWorkspace Creation ~~~~~~~
for stxsId in data[stxsVar].unique():
    df = data[data[stxsVar] == stxsId]

    if stxsVar == 'nosplit':
        stxsBin = opt.productionMode
    else:
        stxsBin = flashggSTXSDict.get(int(stxsId), f"unknownSTXS_{stxsId}")
        if opt.productionMode == "wh":
            stxsBin = stxsBin.replace("QQ2HQQ", "WH2HQQ")
        elif opt.productionMode == "zh":
            stxsBin = stxsBin.replace("QQ2HQQ", "ZH2HQQ")
        elif opt.productionMode == "ggzh":
            if opt.decayExt == "_ZToQQ":
                stxsBin = stxsBin.replace("GG2H", "GG2HQQ")
            elif opt.decayExt == "_ZToNuNu":
                stxsBin = stxsBin.replace("GG2HLL", "GG2HNUNU")
        elif opt.productionMode == "thq":
            stxsBin = stxsBin.replace("TH", "THQ")
        elif opt.productionMode == "thw":
            stxsBin = stxsBin.replace("TH", "THW")

    output_dir = f"{opt.inputTreeFile}/ws_{stxsBin}"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"output_{stxsBin}_M{opt.inputMass}_pythia8_{stxsBin}.root")
    print(f"[INFO] Creating workspace: {output_file}")

    fout = ROOT.TFile(output_file, "RECREATE")

    foutdir = fout.mkdir(inputTreeDir)
    foutdir.cd()  # IMPORTANT: switch to that directory

    ws = ROOT.RooWorkspace("cms_hgg_13TeV", "cms_hgg_13TeV")

    
    if 'mass' in df.columns:
        df = df.rename(columns={'mass': 'CMS_hgg_mass'})
    reduced_df = df[mainVars ]
    

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

        if len(df_cat) > skip_len:
            df_cat = df_cat.iloc[:skip_len]
            if opt.v:
                print(f"[INFO] Truncated nominal category '{cat}' to {skip_len} entries.")
        

        aset = make_argset(ws, var_names)  # full list (workspace needs everything)
        cat_renamed=cat#'_'.join(cat.split('_')[:-1])
        dset_name = f"{opt.productionMode}_{opt.year}_hgg_{opt.inputMass}_13TeV_{cat_renamed}"
        dset = ROOT.RooDataSet(dset_name, dset_name, aset, ROOT.RooFit.WeightVar("weight"))

        # Only try to convert numeric columns
        numeric_var_names = [v for v in var_names if v in df_cat.columns and pd.api.types.is_numeric_dtype(df_cat[v])]
        df_cat[numeric_var_names] = df_cat[numeric_var_names].astype('float64')
        df_cat = df_cat.dropna(subset=numeric_var_names)

        if opt.v:
            print(f"[INFO] Category {cat} has {len(df_cat)} entries after cleaning.")

        # for row in df_cat[numeric_var_names].to_numpy():
        #     for i, val in enumerate(row):
        #         aset[i].setVal(float(val))
        #     dset.add(aset, aset.getRealValue("weight"))
        for row in df_cat[numeric_var_names].itertuples(index=False, name=None):
            for name, val in zip(numeric_var_names, row):
                var = aset.find(name)
                if var:  # safeguard
                    var.setVal(float(val))
            dset.add(aset, aset.find("weight").getVal())

        getattr(ws, 'import')(dset)
    
    if opt.doSystematics:
        def fast_sample_syst_single_file(dirpath, syst, direction, n):
            """
            Load only ONE parquet file for each systematic variation,
            take first n rows, and stop.
            """

            # Example matches: ...PileupUp.parquet, ...JERDown.parquet
            files = [
                f for f in glob.glob(f"{dirpath}/*.parquet")
                if syst in f and direction in f and "ws_" not in f
            ]

            if not files:
                return pd.DataFrame()

            # Pick the largest file (most likely to contain enough rows)
            f = max(files, key=os.path.getsize)

            # Read only first n rows
            try:
                table = pq.read_table(f)
                return table.to_pandas()
            except Exception as e:
                print(f"[ERROR] Could not read {f}: {e}")
                return pd.DataFrame()

            

        for cat in cats:
            catcopy=cat
            
            for syst in systematics:
                for direction in ['Down',"Up"]:#, "Down"]:
                    syst_name = f"{syst}{direction}"
                    # print(f'systname={syst_name}')
                

                    merged_sys = fast_sample_syst_single_file(opt.inputTreeFile, syst, direction, skip_len)
                    
                    merged_sys['cat'] = merged_sys['pred_ia'].map(str).map(cat_dict['cat_dict'])
                    merged_sys = merged_sys[merged_sys['cat'] == cat]
                    
                    # if 'Down' in syst_name:
                    # print('print'+direction)
                    # print(merged_sys.tail()) 
            
                
                # catcopy = catcopy.replace(catcopy,catcopy.split('_merged')[0])
                # catcopy+='_merged'
                # print(catcopy)
                # syst_file = os.path.join(opt.inputTreeFile, f"{catcopy}_{syst_name}01sigma.parquet")
                
                # if not os.path.exists(syst_file):
                #     print(f"[WARNING] Missing systematic file: {syst_file}")
                #     continue

                # sdf = pd.read_parquet(syst_file)
                    sdf = merged_sys
                    if len(sdf) > skip_len:
                        sdf = sdf.iloc[:skip_len]
                        if opt.v:
                            print(f"[INFO] Truncated systematic '{syst_name}' for category '{cat}' to {skip_len} entries.")
                    
                    if sdf.empty:
                       if opt.v:
                        print(f"[WARNING] Empty systematic parquet:") # {syst_file}")
                        # continue                      
                    if 'mass' in sdf.columns:
                        sdf = sdf.rename(columns={'mass': 'CMS_hgg_mass'})

                    # If splitting: ensure STXS var
                    if stxsVar not in sdf.columns:
                        sdf[stxsVar] = stxsId

                    # Clean and ensure needed vars
                    systematicsVarsDropWeight = [v for v in systematicsVars if v != 'weight']
                    for v in systematicsVarsDropWeight:
                        if v not in sdf.columns:
                            print(f"[ERROR] Missing var {v} in {syst_file}")
                            break

                    sdf = sdf.dropna(subset=systematicsVarsDropWeight + ['weight'])

                    aset = make_argset(ws, systematicsVarsDropWeight)
                    hist_name = f"{opt.productionMode}_{opt.year}_hgg_{opt.inputMass}_13TeV_{catcopy}_{syst_name}01sigma"
                    # print(f"[DEBUG] Importing histogram: {hist_name}")
                    hist = ROOT.RooDataHist(hist_name, hist_name, aset)

                    for row, weight in zip(sdf[systematicsVarsDropWeight].to_numpy(), sdf["weight"].to_numpy()):
                        for i, val in enumerate(row):
                            aset[i].setVal(float(val))
                        hist.add(aset, weight)

                    getattr(ws, 'import')(hist)
                    if opt.v:
                        print(f"[INFO] Imported systematics hist: {hist_name}")
    if opt.v:
        print(ws)
    

        ws.Print('v')
    ws.Write()
    fout.Close()

    # up=0
    # down=0
    # ne=ws.data('BBH_FID_preEE_hgg_125_13TeV_RECO_ggH_0J_PTH_0_10')
    # for i in range(ne.numEntries()):
    #     entry=ne.get(i)
    #     u=entry['weight_PileupUp'].getVal()
    #     d=entry['weight_PileupDown'].getVal()
    #     up+=u 
    #     down+=d 
    # print(up)
    # print(down)

    # print('now for ID SF:')
    # up=0
    # down=0
    # ne=ws.data('BBH_FID_preEE_hgg_125_13TeV_RECO_ggH_0J_PTH_0_10')
    # for i in range(ne.numEntries()):
    #     entry=ne.get(i)
    #     u=entry['weight_SF_photon_IDDown'].getVal()
    #     d=entry['weight_SF_photon_IDUp'].getVal()
    #     up+=u 
    #     down+=d 
    # print(up)
    # print(down)

print("~~~~~~~~~~~~~~~~~~~~~~~~~ ALL WORKSPACES DONE ~~~~~~~~~~~~~~~~~~~~~~~~~")


print(' WARNING: In this setup, parquet files had background (pred=0). This got dropped when making RooWS!')

debug= False

if debug:
    for i in merged.cat.unique():
        proc=opt.inputTreeFile.split('/')[-3]
        n=f'{proc}_preEE_hgg_125_13TeV_{i}'
        print(f'{i} and {merged[merged.cat==i].weight.sum()} vs root: {ws.data(n).Print()}')
        print('\n')