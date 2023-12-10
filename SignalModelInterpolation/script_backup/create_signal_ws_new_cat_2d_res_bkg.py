import ROOT

import numpy as np
import scipy.interpolate as spi
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import argparse
import json
import os

DO_SYST = True

def loadJson(path):
  with open(path, "r") as f:
    return json.load(f)

def unique(a, b):
  return 0.5*(a+b)*(a+b+1)+b

def getNuisanceDatacardName(name, year):
  if name == "fnuf":
    return "CMS_hgg_nuisance_funf_13TeVscaleCorr"
  elif name == "material":
    return "CMS_hgg_nuisance_material_13TeVscaleCorr"
  elif name == "smear":
    return "CMS_hgg_nuisance_MCSmear_smear_13TeVsmear_%s"%year
  elif name == "scale":
    return "CMS_hgg_nuisance_MCScale_scale_13TeVscale_%s"%year
  else:
    raise Exception("Unexpected shape systematic: %s"%name)

def makeWorkspace(models, systematicss, year, cat, workspace_output, mgg_range, proc):
  suffix = "_%s_cat%s_%s"%(year, cat, proc)

  model = models[year][cat]
  masses = model.keys()

  mx = np.array([int(m.split("_")[0]) for m in masses])
  my = np.array([int(m.split("_")[1]) for m in masses])
  mx_my = unique(mx, my)

  masses = list(np.array(masses)[np.argsort(mx_my)])
  mx_my = np.sort(mx_my)
    
  norms = np.asarray([model[m]["norm"] for m in masses])
  popts = np.asarray([model[m]["parameters"] for m in masses])
  mx_my_arr = np.asarray(mx_my, dtype=float)

  MX = ROOT.RooRealVar("MX", "MX", mx[0], mx.min(), mx.max())
  MY = ROOT.RooRealVar("MY", "MY", my[0], my.min(), my.max())
  MX_MY = ROOT.RooFormulaVar("MX_MY", "MX_MY", "0.5*(@0+@1)*(@0+@1+1)+@1", ROOT.RooArgList(MX, MY))
  
  CMS_hgg_mass = ROOT.RooRealVar("CMS_hgg_mass", "CMS_hgg_mass", mgg_range[0], mgg_range[0], mgg_range[1])
  dZ = ROOT.RooRealVar("dZ", "dZ", 0, -20, 20)
  MH = ROOT.RooRealVar("MH", "MH", mgg_range[0], mgg_range[0], mgg_range[1])

  #print(popts)
  #print(year, cat)
  sig_norm_nominal = ROOT.RooSpline1D("sig_norm_nominal"+suffix, "sig_norm_nominal"+suffix, MX_MY, len(mx_my_arr), mx_my_arr, norms)
  dm_nominal = ROOT.RooSpline1D("dm_noninal"+suffix, "dm_nominal"+suffix, MX_MY, len(mx_my_arr), mx_my_arr, np.array(popts[:, 1]))
  sigma_nominal = ROOT.RooSpline1D("sigma_nominal"+suffix, "sigma_nominal"+suffix, MX_MY, len(mx_my_arr), mx_my_arr, np.array(popts[:, 2]))

  mean_nominal = ROOT.RooFormulaVar("mean_nominal"+suffix, "mean_nominal"+suffix, "@0+@1", ROOT.RooArgList(MH, dm_nominal))
  n1 = ROOT.RooSpline1D("n1"+suffix, "n1"+suffix, MX_MY, len(mx_my_arr), mx_my_arr, np.array(popts[:, 4]))
  n2 = ROOT.RooSpline1D("n2"+suffix, "n2"+suffix, MX_MY, len(mx_my_arr), mx_my_arr, np.array(popts[:, 6]))
  a1 = ROOT.RooSpline1D("a1"+suffix, "a1"+suffix, MX_MY, len(mx_my_arr), mx_my_arr, np.array(popts[:, 3]))
  a2 = ROOT.RooSpline1D("a2"+suffix, "a2"+suffix, MX_MY, len(mx_my_arr), mx_my_arr, np.array(popts[:, 5]))

  if DO_SYST:
    systematics = systematicss[year][cat]

    #creates splines for const values
    const_sys_names = [name for name in systematics[masses[0]].keys() if "const" in name]
    consts_splines = {}
    for systematic in const_sys_names:
      values = np.asarray([systematics[m][systematic] for m in masses])
      consts_splines[systematic] = ROOT.RooSpline1D(systematic+suffix, systematic+suffix, MX_MY, len(mx_my_arr), mx_my_arr, values)

    #create nuisances
    nuisances = {}
    nuisance_names = set([name.split("_")[2] for name in const_sys_names])
    for name in nuisance_names:
      nuisances[name] = ROOT.RooRealVar(getNuisanceDatacardName(name, year),getNuisanceDatacardName(name, year), 0, -5, 5)

    #create RooFormulaVars including the systematics
    get_nuisance = lambda name, var: nuisances[name]
    get_const = lambda name, var: consts_splines["const_%s_%s"%(var, name)]

    formula = "@0*(1." + "".join(["+@%d*@%d"%(i*2+1,i*2+2) for i in range(len(const_sys_names)//3)]) + ")"
    #print(formula)
    #print(sig_norm_nominal)
    
    sig_norm = ROOT.RooFormulaVar("sig%s_norm"%suffix, "sig%s_norm"%suffix, formula, ROOT.RooArgList(sig_norm_nominal, *[f(name, "rate") for name in nuisance_names for f in (get_const, get_nuisance)]))
    mean = ROOT.RooFormulaVar("mean"+suffix, "mean"+suffix, formula,  ROOT.RooArgList(mean_nominal, *[f(name, "mean") for name in nuisance_names for f in (get_const, get_nuisance)]))
    sigma = ROOT.RooFormulaVar("sigma"+suffix, "sigma"+suffix, formula,  ROOT.RooArgList(sigma_nominal, *[f(name, "sigma") for name in nuisance_names for f in (get_const, get_nuisance)]))
  else:
    sig_norm = ROOT.RooFormulaVar("sig%s_norm"%suffix, "sig%s_norm"%suffix, "@0", ROOT.RooArgList(sig_norm_nominal))
    mean = ROOT.RooFormulaVar("mean"+suffix, "mean"+suffix, "@0", ROOT.RooArgList(mean_nominal))
    sigma = ROOT.RooFormulaVar("sigma"+suffix, "sigma"+suffix, "@0", ROOT.RooArgList(sigma_nominal))
  
  sig = ROOT.RooDoubleCBFast("sig"+suffix, "sig"+suffix, CMS_hgg_mass, mean, sigma, a1, n1, a2, n2)

  wsig_13TeV = ROOT.RooWorkspace("wsig_13TeV", "wsig_13TeV")

  imp = getattr(wsig_13TeV, "import")

  imp(CMS_hgg_mass)
  imp(MH)
  imp(dZ)

  imp(sig)
  imp(sig_norm, ROOT.RooFit.RecycleConflictNodes())

  wsig_13TeV.writeToFile(workspace_output)

def tryMake(path):
  if not os.path.exists(path):
    os.makedirs(path)

def rearrangeModels(models):
  sig_procs = ["VBFH_M125", "VH_M125", "ggH_M125", "ttH_M125"]

  years = models.keys()
  SRs = models[years[0]].keys()
  masses = models[years[0]][SRs[0]].keys()

  new_models = {}
  for proc in sig_procs:
    new_models[proc] = {}
    for year in years:
      new_models[proc][year] = {}
      for SR in SRs:
        new_models[proc][year][SR] = {}
        for mass in masses:
          new_models[proc][year][SR][mass] = models[year][SR][mass][proc]

  return new_models

def main(args):
  with open(os.path.join(args.indir, "model.json"), "r") as f:
    models = rearrangeModels(json.load(f))
  if DO_SYST:
    with open(os.path.join(args.indir, "systematics.json"), "r") as f:
      systematics = rearrangeModels(json.load(f))
  else:
    systematics = None

  with open("rearranged_model.json", "w") as f:
    json.dump(models, f, indent=4, sort_keys=True)
  with open("rearranged_systematics.json", "w") as f:
    json.dump(systematics, f, indent=4, sort_keys=True)

  procs = sorted(models.keys())
  years = sorted(models[procs[0]].keys())
  cats = sorted(models[procs[0]][years[0]].keys())
  print(procs)
  print(years)
  print(cats)
  tryMake(args.outdir)

  for proc in procs:
    for year in years:
      for cat in cats:
        out_path = os.path.join(args.outdir, "%s_%s_cat%s.root"%(proc, year, cat))
        makeWorkspace(models[proc], systematics[proc], year, cat, out_path, args.mgg_range, proc)

if __name__=="__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('--indir', '-i', type=str, required=True)
  parser.add_argument('--outdir', '-o', type=str, required=True)
  parser.add_argument('--mgg-range', type=float, nargs=2, default=(100,180))
  args = parser.parse_args()

  main(args)


