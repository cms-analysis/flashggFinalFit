import ROOT
import os
import glob
import re
from optparse import OptionParser
import subprocess
import json

def rooiter(x):
  iter = x.iterator()
  ret = iter.Next()
  while ret:
    yield ret
    ret = iter.Next()

def get_options():
    parser = OptionParser()
    parser.add_option('--inputWSFile', dest='inputWSFile', default='Datacard.root', help="Input workspace")
    parser.add_option('--MH', dest='MH', default='125.38', help="MH")
    parser.add_option('--initial-fit-param', dest='initial_fit_param', default='lumi_13TeV_uncorrelated_2016', help="Initial fit parameter (combine must have an input parameter to fit to, pick any low impact nuisance)")
    parser.add_option('--nToys', dest='nToys', default=2000, type='int', help="Number of toys")
    parser.add_option('--mode', dest='mode', default="setup", help="[setup,generate,fixed,envelope]")
    return parser.parse_args()
(opt,args) = get_options()

if opt.mode == "setup":

    # Get list of pdfindeices
    f = ROOT.TFile(opt.inputWSFile)
    w = f.Get("w")
    cats = w.allCats()
    pdf_index = []
    for cat in rooiter(cats):
        if "pdfindex" in cat.GetName(): pdf_index.append(cat.GetName()) 
    f.Close()
   
    # Initial fit fixing params to be zero
    cmd = "combine -m %s -d %s -M MultiDimFit --cminDefaultMinimizerStrategy 0 --setParameters MH=%s,r=0 --freezeParameters MH,r -P %s -n _initial --saveWorkspace --saveSpecifiedIndex %s --X-rtd MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_maskChannels=2; cd .."%(opt.MH,opt.inputWSFile,opt.MH,opt.initial_fit_param,",".join(pdf_index))
    print(cmd)
    os.system(cmd)

    # Save best fit pdf indices to json file
    f_res = ROOT.TFile("higgsCombine_initial.MultiDimFit.mH%s.root"%opt.MH)
    t = f_res.Get("limit")
    t.GetEntry(0)
    pdf_index_bf = {}
    for index in pdf_index: pdf_index_bf[index] = getattr(t,index)
    f_res.Close()
    with open("pdfindex.json","w") as jf:
        json.dump(pdf_index_bf, jf)

if opt.mode == "generate":

    cmd = "combine -m %s -d higgsCombine_initial.MultiDimFit.mH%s.root -M GenerateOnly --setParameters MH=%s --freezeParameters MH --expectSignal 0 -n _toy_ --saveToys --snapshotName MultiDimFit -t %s -s -1\n\n"%(opt.MH,opt.MH,opt.MH,opt.nToys)
    print(cmd)
    os.system(cmd)

    cmd = "mv higgsCombine_toy_* toys.root"
    os.system(cmd)

if opt.mode == "fixed":

    # Get pdf index and the best fit values
    with open("pdfindex.json", "r") as jf:
        pdf_index_bf = json.load(jf)

    pdf_index_freeze = ",".join(list(pdf_index_bf.keys()))
    pdf_index_set = ""
    for k,v in list(pdf_index_bf.items()): pdf_index_set += "%s=%s,"%(k,v)
    pdf_index_set = pdf_index_set[:-1]

    cmd = "combine -m %s -d higgsCombine_initial.MultiDimFit.mH%s.root -M Significance --snapshotName MultiDimFit --cminDefaultMinimizerStrategy 0 --setParameters MH=%s,%s --expectSignal 0 --freezeParameters MH,%s -n _fixed_ -t %s --X-rtd MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_maskChannels=2 --toysFile toys.root --X-rtd ADDNLL_RECURSIVE=1; mv higgsCombine_fixed_* fit_fixed.root"%(opt.MH,opt.MH,opt.MH,pdf_index_set,pdf_index_freeze,opt.nToys)
    print(cmd)
    os.system(cmd)

if opt.mode == "envelope":

    cmd = "combine -m %s -d higgsCombine_initial.MultiDimFit.mH%s.root -M Significance --snapshotName MultiDimFit --cminDefaultMinimizerStrategy 0 --setParameters MH=%s --expectSignal 0 --freezeParameters MH -n _envelope_ -t %s --X-rtd MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_maskChannels=2 --toysFile toys.root --X-rtd ADDNLL_RECURSIVE=1; mv higgsCombine_envelope_* fit_envelope.root"%(opt.MH,opt.MH,opt.MH,opt.nToys)
    print(cmd)
    os.system(cmd)
