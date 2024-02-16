import ROOT

import numpy as np
import scipy.interpolate as spi
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import argparse
import json
import os

def loadJson(path):
  with open(path, "r") as f:
    return json.load(f)

def unique(a, b):
  return 0.5*(a+b)*(a+b+1)+b

def getNuisanceDatacardName(name, year):
  if name == "fnufUnc":
    return "CMS_hgg_nuisance_funf_13TeVscaleCorr"
  elif name == "materialUnc":
    return "CMS_hgg_nuisance_material_13TeVscaleCorr"
  elif name == "PhoSmearUnc":
    return "CMS_hgg_nuisance_MCSmear_13TeVsmear_%s"%year
  elif name == "PhoScaleUnc":
    return "CMS_hgg_nuisance_MCScale_13TeVscale_%s"%year
  elif name == "PUWeight":
    return "CMS_hgg_nuisance_pileup_13TeVscale_%s"%year
  elif name == "JESUnc2":
    return "CMS_hgg_nuisance_scale_j_absolute_13TeVscaleCorr"
  elif name == "JESUnc3":
    return "CMS_hgg_nuisance_scale_j_absolute_13TeVscale_%s"%year
  elif name == "JESUnc4":
    return "CMS_hgg_nuisance_scale_j_flavorQCD_13TeVscaleCorr"
  elif name == "JESUnc5":
    return "CMS_hgg_nuisance_scale_j_BBEC1_13TeVscaleCorr"
  elif name == "JESUnc6":
    return "CMS_hgg_nuisance_scale_j_BBEC1_13TeVscale_%s"%year
  elif name == "JESUnc11":
    return "CMS_hgg_nuisance_scale_j_relativeBal_13TeVscaleCorr"
  elif name == "JESUnc12":
    return "CMS_hgg_nuisance_scale_j_relativeSample_13TeVscale_%s"%year
  elif name == "bTagSF8":
    return "CMS_hgg_nuisance_btag_cferr1_13TeVscaleCorr"
  elif name == "bTagSF9":
    return "CMS_hgg_nuisance_btag_cferr2_13TeVscaleCorr"
  elif name == "JERUnc":
    return "CMS_hgg_nuisance_res_j_13TeVscale_%s"%year
  else:
    raise Exception("Unexpected shape systematic: %s"%name)

def makeWorkspace(models, systematicss, year, cat, workspace_output, mgg_range, doSyst):
  suffix = "_%s_cat%s"%(year, cat)

  model = models[year][cat]
  masses = model.keys()

  mx = np.array([int(m.split("_")[0]) for m in masses])
  my = np.array([int(m.split("_")[1]) for m in masses])
  mx_my = unique(mx, my)

  masses = list(np.array(masses)[np.argsort(mx_my)])
  mx_my = np.sort(mx_my)
    
  norms = np.asarray([model[m]["this mass"]["norm"] for m in masses])
  popts = np.asarray([model[m]["this mass"]["parameters"] for m in masses])
  mx_my_arr = np.asarray(mx_my, dtype=float)

  # for m in masses:
    # if "same_score" not in model[m].keys():
    #   print(year, cat, m)
    #   assert False
    # if "grad_norm_pos" not in model[m]["same_score"].keys():
    #   print(year, cat, m)
    #   assert False

  if "same_score" in model[masses[0]].keys():
    grad_dms = np.asarray([model[m]["same_score"]["grad_dm"] for m in masses])
    grad_sigmas = np.asarray([model[m]["same_score"]["grad_sigma"] for m in masses])
    grad_norms_pos = np.asarray([model[m]["same_score"]["grad_norm_pos"] for m in masses])
    grad_norms_neg = np.asarray([model[m]["same_score"]["grad_norm_neg"] for m in masses])
  else:
    grad_dms = np.asarray([0.0 for m in masses])
    grad_sigmas = np.asarray([0.0 for m in masses])
    grad_norms_pos = np.asarray([0.0 for m in masses])
    grad_norms_neg = np.asarray([0.0 for m in masses])

  MX = ROOT.RooRealVar("MX", "MX", mx[0], mx.min(), mx.max())
  MY = ROOT.RooRealVar("MY", "MY", my[0], my.min(), my.max())
  MX_MY = ROOT.RooFormulaVar("MX_MY", "MX_MY", "0.5*(@0+@1)*(@0+@1+1)+@1", ROOT.RooArgList(MX, MY))
  
  CMS_hgg_mass = ROOT.RooRealVar("CMS_hgg_mass", "CMS_hgg_mass", mgg_range[0], mgg_range[0], mgg_range[1])
  dZ = ROOT.RooRealVar("dZ", "dZ", 0, -20, 20)
  MH = ROOT.RooRealVar("MH", "MH", mgg_range[0], mgg_range[0], mgg_range[1])

  grad_dm = ROOT.RooSpline1D("grad_dm"+suffix, "grad_dm"+suffix, MX_MY, len(mx_my_arr), mx_my_arr, grad_dms)
  grad_sigma = ROOT.RooSpline1D("grad_sigma"+suffix, "grad_sigma"+suffix, MX_MY, len(mx_my_arr), mx_my_arr, grad_sigmas)
  grad_norm_pos = ROOT.RooSpline1D("grad_norm_pos"+suffix, "grad_norm_pos"+suffix, MX_MY, len(mx_my_arr), mx_my_arr, grad_norms_pos)
  grad_norm_neg = ROOT.RooSpline1D("grad_norm_neg"+suffix, "grad_norm_neg"+suffix, MX_MY, len(mx_my_arr), mx_my_arr, grad_norms_neg)

  sig_norm_spline = ROOT.RooSpline1D("sig_norm_spline"+suffix, "sig_norm_spline"+suffix, MX_MY, len(mx_my_arr), mx_my_arr, norms)
  dm_spline = ROOT.RooSpline1D("dm_spline"+suffix, "dm_spline"+suffix, MX_MY, len(mx_my_arr), mx_my_arr, np.array(popts[:, 1]))
  sigma_spline = ROOT.RooSpline1D("sigma_spline"+suffix, "sigma_spline"+suffix, MX_MY, len(mx_my_arr), mx_my_arr, np.array(popts[:, 2]))

  sig_norm_nominal = ROOT.RooFormulaVar("sig_norm_nominal"+suffix, "sig_norm_nominal"+suffix, "@0+(@1-@2)*( (@1>@2) ? @3 : @4 )", ROOT.RooArgList(sig_norm_spline,MH,MY,grad_norm_pos,grad_norm_neg))
  dm_nominal = ROOT.RooFormulaVar("dm_nominal"+suffix, "dm_nominal"+suffix, "@0+(@1-@2)*@3", ROOT.RooArgList(dm_spline,MH,MY,grad_dm))
  sigma_nominal = ROOT.RooFormulaVar("sigma_nominal"+suffix, "sigma_nominal"+suffix, "@0+(@1-@2)*@3", ROOT.RooArgList(sigma_spline,MH,MY,grad_sigma))
  
  mean_nominal = ROOT.RooFormulaVar("mean_nominal"+suffix, "mean_nominal"+suffix, "@0+@1", ROOT.RooArgList(MH, dm_nominal))
  n1 = ROOT.RooSpline1D("n1"+suffix, "n1"+suffix, MX_MY, len(mx_my_arr), mx_my_arr, np.array(popts[:, 4]))
  n2 = ROOT.RooSpline1D("n2"+suffix, "n2"+suffix, MX_MY, len(mx_my_arr), mx_my_arr, np.array(popts[:, 6]))
  a1 = ROOT.RooSpline1D("a1"+suffix, "a1"+suffix, MX_MY, len(mx_my_arr), mx_my_arr, np.array(popts[:, 3]))
  a2 = ROOT.RooSpline1D("a2"+suffix, "a2"+suffix, MX_MY, len(mx_my_arr), mx_my_arr, np.array(popts[:, 5]))

  if doSyst:
    systematics = systematicss[year][cat]

    #creates splines for const values
    const_sys_names = [name for name in systematics[systematics.keys()[0]].keys() if "_" in name]
    consts_splines = {}
    for systematic in const_sys_names:
      values = np.asarray([systematics[m][systematic] for m in masses])
      consts_splines[systematic] = ROOT.RooSpline1D(systematic+suffix, systematic+suffix, MX_MY, len(mx_my_arr), mx_my_arr, values)

    #create nuisances
    nuisances = {}
    nuisance_names = set(["_".join(name.split("_")[:-1]) for name in const_sys_names])
    for name in nuisance_names:
      nuisances[name] = ROOT.RooRealVar(getNuisanceDatacardName(name, year),getNuisanceDatacardName(name, year), 0, -5, 5)

    #create RooFormulaVars including the systematics
    get_nuisance = lambda name, var: nuisances[name]
    get_const = lambda name, var: consts_splines["%s_%s"%(name, var)]

    formula = "@0*(1." + "".join(["+@%d*@%d"%(i*2+1,i*2+2) for i in range(len(const_sys_names)//3)]) + ")"
    sig_norm_rooArgList = ROOT.RooArgList(sig_norm_nominal)
    mean_rooArgList = ROOT.RooArgList(mean_nominal)
    sigma_rooArgList = ROOT.RooArgList(sigma_nominal)
    for name in nuisance_names:
      print(name)
      for f in (get_const, get_nuisance):
        sig_norm_rooArgList.add(f(name, "rate"))
        mean_rooArgList.add(f(name, "mean"))
        sigma_rooArgList.add(f(name, "sigma"))
    
    sig_norm = ROOT.RooFormulaVar("sig%s_norm"%suffix, "sig%s_norm"%suffix, formula, sig_norm_rooArgList)
    mean = ROOT.RooFormulaVar("mean"+suffix, "mean"+suffix, formula, mean_rooArgList)
    sigma = ROOT.RooFormulaVar("sigma"+suffix, "sigma"+suffix, formula, sigma_rooArgList)
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

  #wsig_13TeV.Print()
  wsig_13TeV.writeToFile(workspace_output)

def tryMake(path):
  if not os.path.exists(path):
    os.makedirs(path)

def main(args):
  with open(os.path.join(args.indir, "model.json"), "r") as f:
    models = json.load(f)
  if args.doSyst:
    with open(os.path.join(args.indir, "systematics.json"), "r") as f:
      systematics = json.load(f)
  else:
    systematics = None

  years = sorted(models.keys())
  cats = sorted(models[years[0]].keys())
  tryMake(args.outdir)

  for year in years:
    print(year)
    for cat in cats:
      print(cat)
      out_path = os.path.join(args.outdir, "sig_%s_cat%s.root"%(year, cat))
      makeWorkspace(models, systematics, year, cat, out_path, args.mgg_range, args.doSyst)

if __name__=="__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('--indir', '-i', type=str, required=True)
  parser.add_argument('--outdir', '-o', type=str, required=True)
  parser.add_argument('--mgg-range', type=float, nargs=2, default=(100,180))
  parser.add_argument('--doSyst', action="store_true", default=False)
  args = parser.parse_args()

  main(args)


