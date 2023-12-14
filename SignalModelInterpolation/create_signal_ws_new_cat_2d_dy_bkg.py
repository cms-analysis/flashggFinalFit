import ROOT

import numpy as np
import argparse
import json
import os

def loadJson(path):
  with open(path, "r") as f:
    return json.load(f)

def unique(a, b):
  return 0.5*(a+b)*(a+b+1)+b

def makeWorkspace(models, cat, workspace_output, mgg_range):
  suffix = "_merged_cat%s_dy"%(cat)

  model = models[cat]
  masses = model.keys()

  mx = np.array([int(m.split("_")[0]) for m in masses])
  my = np.array([int(m.split("_")[1]) for m in masses])
  mx_my = unique(mx, my)

  masses = list(np.array(masses)[np.argsort(mx_my)])
  mx_my = np.sort(mx_my)
    
  norms = np.asarray([model[m]["norm"] for m in masses])
  norms_err = 2*np.asarray([model[m]["norm_err"] for m in masses])
  popts = np.asarray([model[m]["parameters"] for m in masses])
  perrs = 2*np.asarray([model[m]["parameters_err"] for m in masses])
  mx_my_arr = np.asarray(mx_my, dtype=float)

  MX = ROOT.RooRealVar("MX", "MX", mx[0], mx.min(), mx.max())
  MY = ROOT.RooRealVar("MY", "MY", my[0], my.min(), my.max())
  MX_MY = ROOT.RooFormulaVar("MX_MY", "MX_MY", "0.5*(@0+@1)*(@0+@1+1)+@1", ROOT.RooArgList(MX, MY))
  
  CMS_hgg_mass = ROOT.RooRealVar("CMS_hgg_mass", "CMS_hgg_mass", mgg_range[0], mgg_range[0], mgg_range[1])
  dZ = ROOT.RooRealVar("dZ", "dZ", 0, -20, 20)
  MH = ROOT.RooRealVar("MH", "MH", mgg_range[0], mgg_range[0], mgg_range[1])

  sig_norm_spline = ROOT.RooSpline1D("sig_norm_spline"+suffix, "sig_norm_spline"+suffix, MX_MY, len(mx_my_arr), mx_my_arr, norms)
  sig_norm_err_spline = ROOT.RooSpline1D("sig_norm_err_spline"+suffix, "sig_norm_err_spline"+suffix, MX_MY, len(mx_my_arr), mx_my_arr, norms_err)
  sig_mean_spline = ROOT.RooSpline1D("sig_mean_spline"+suffix, "sig_mean_spline"+suffix, MX_MY, len(mx_my_arr), mx_my_arr, np.array(popts[:, 0]))
  sig_mean_err_spline = ROOT.RooSpline1D("sig_mean_err_spline"+suffix, "sig_mean_err_spline"+suffix, MX_MY, len(mx_my_arr), mx_my_arr, np.array(perrs[:, 0]))
  sig_sigma_spline = ROOT.RooSpline1D("sig_sigma_spline"+suffix, "sig_sigma_spline"+suffix, MX_MY, len(mx_my_arr), mx_my_arr, np.array(popts[:, 1]))
  sig_sigma_err_spline = ROOT.RooSpline1D("sig_sigma_err_spline"+suffix, "sig_sigma_err_spline"+suffix, MX_MY, len(mx_my_arr), mx_my_arr, np.array(perrs[:, 1]))

  rsuffix = "_merged_dy"
  sig_norm_nuisance = ROOT.RooRealVar("CMS_hgg_nuisance_sig_norm"+rsuffix,"CMS_hgg_nuisance_sig_norm"+rsuffix, 0, -5, 5)
  sig_mean_nuisance = ROOT.RooRealVar("CMS_hgg_nuisance_sig_mean"+rsuffix,"CMS_hgg_nuisance_sig_mean"+rsuffix, 0, -5, 5)
  sig_sigma_nuisance = ROOT.RooRealVar("CMS_hgg_nuisance_sig_sigma"+rsuffix,"CMS_hgg_nuisance_sig_sigma"+rsuffix, 0, -5, 5)

  sig_norm_nuisance_cat = ROOT.RooRealVar("CMS_hgg_nuisance_sig_norm"+suffix,"CMS_hgg_nuisance_sig_norm"+suffix, 0, -5, 5)
  sig_mean_nuisance_cat = ROOT.RooRealVar("CMS_hgg_nuisance_sig_mean"+suffix,"CMS_hgg_nuisance_sig_mean"+suffix, 0, -5, 5)
  sig_sigma_nuisance_cat = ROOT.RooRealVar("CMS_hgg_nuisance_sig_sigma"+suffix,"CMS_hgg_nuisance_sig_sigma"+suffix, 0, -5, 5)

  #formula = "@0*(1." + "".join(["+@%d*@%d"%(i*2+1,i*2+2) for i in range(len(const_sys_names)//3)]) + ")"
  formula = "@0+@1*(@2+@3)"

  sig_norm = ROOT.RooFormulaVar("sig%s_norm"%suffix, "sig%s_norm"%suffix, formula, ROOT.RooArgList(sig_norm_spline, sig_norm_err_spline, sig_norm_nuisance, sig_norm_nuisance_cat))
  sig_mean = ROOT.RooFormulaVar("sig_mean"+suffix, "sig_mean"+suffix, formula,  ROOT.RooArgList(sig_mean_spline, sig_mean_err_spline, sig_mean_nuisance, sig_mean_nuisance_cat))
  sig_sigma = ROOT.RooFormulaVar("sig_sigma"+suffix, "sig_sigma"+suffix, formula,  ROOT.RooArgList(sig_sigma_spline, sig_sigma_err_spline, sig_sigma_nuisance, sig_sigma_nuisance_cat))
 
  sig = ROOT.RooGaussian("sig"+suffix, "sig"+suffix, CMS_hgg_mass, sig_mean, sig_sigma)

  wsig_13TeV = ROOT.RooWorkspace("wsig_13TeV", "wsig_13TeV")

  imp = getattr(wsig_13TeV, "import")

  imp(CMS_hgg_mass)
  imp(MH)
  imp(dZ)

  imp(sig)
  imp(sig_norm, ROOT.RooFit.RecycleConflictNodes())

  wsig_13TeV.Print()
  wsig_13TeV.writeToFile(workspace_output)

def tryMake(path):
  if not os.path.exists(path):
    os.makedirs(path)

def main(args):
  with open(os.path.join(args.indir, "model.json"), "r") as f:
    models = json.load(f)
  
  cats = sorted(models.keys())
  print(cats)
  tryMake(args.outdir)

  for cat in cats:
    out_path = os.path.join(args.outdir, "dy_merged_cat%s.root"%cat)
    makeWorkspace(models, cat, out_path, args.mgg_range)

if __name__=="__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('--indir', '-i', type=str, required=True)
  parser.add_argument('--outdir', '-o', type=str, required=True)
  parser.add_argument('--mgg-range', type=float, nargs=2, default=(100,180))
  args = parser.parse_args()

  main(args)


