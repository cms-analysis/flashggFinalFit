import os, sys
import glob
import re
from optparse import OptionParser
from collections import OrderedDict as od
import json

def get_options():
  parser = OptionParser()
  parser.add_option('--inputDatacard',dest='inputDatacard', default="", help="Input datacard")
  parser.add_option('--systMap',dest='systMap', default="", help="Form name:mode:val,name2:mode2:val2 (e.g. CMS_hgg_tth_parton_shower:const_ggH_TTH:0.650/1.350)")
  return parser.parse_args()
(opt,args) = get_options()

if not os.path.exists( opt.inputDatacard ):
  print " --> [ERROR] Input datacard %s does not exist."%opt.inputDatacard
  sys.exit(1)

catLine = ''
procLine = ''
sprior = 'lnN'

nBinLine = 0
nProcLine = 0
with open(opt.inputDatacard,'r') as f:
  # Skip first bin line
  for line in f:
    if line.split(" ")[0] == 'bin':
      if nBinLine == 0: nBinLine += 1
      else: catLine = line
    if line.split(" ")[0] == "process":
      if nProcLine == 0: 
        procLine = line
        nProcLine += 1

procs = []
cats = []
for c in catLine.split(" "):
  if "RECO" in c: cats.append(c)
for p in procLine.split(" "):
  if ("hgg" in p)|("bkg" in p): procs.append(p)

# Initiate ordered dict for each line
systs = od()
for syst in opt.systMap.split("+"):
  sname = syst.split(":")[0]
  stype = syst.split(":")[1]
  sval = syst.split(":")[2]
  systs[sname] = od()

  # Const with rgx for proc and cat
  if "const" in stype:
    proc_rgx = stype.split("_")[1]
    cat_rgx = stype.split("_")[2]
    for i in range(len(procs)):
      p,c = procs[i], cats[i]
      key = "%s__%s"%(p,c)
      if( proc_rgx in p )&( cat_rgx in c ): systs[sname][key] = sval
      else: systs[sname][key] = '-'

  # Json file for ue/ps norm uncertainties
  if "ue_norm" in stype:
    with open(sval,"r") as jsonfile: ue_vals = json.load(jsonfile)
    for i in range(len(procs)):
      p,c = procs[i], cats[i]
      key = "%s__%s"%(p,c)
      # Remove year and decay tag
      if "hgg" in p:
        p_stripped = "_".join(p.split("_")[:-2])
        if p_stripped in ue_vals: 
          up, down = ue_vals[p_stripped]['ue_up'], ue_vals[p_stripped]['ue_down']
          if( up == 1. )&( down == 1. ): v = '-'
          elif( up == 1. ): v = "%.3f"%down
          elif( down == 1. ): v = "%.3f"%up
          else: v = "%.3f/%.3f"%(down,up)
        else: v = "-"
      else: v = '-'
      # Add value
      systs[sname][key] = v

  elif "ps_norm" in stype:
    with open(sval,"r") as jsonfile: ps_vals = json.load(jsonfile)
    for i in range(len(procs)):
      p,c = procs[i], cats[i]
      key = "%s__%s"%(p,c)
      # Remove year and decay tag
      if "hgg" in p:
        p_stripped = "_".join(p.split("_")[:-2])
        if p_stripped in ps_vals: 
          up, down = ps_vals[p_stripped]['ps_up'], ps_vals[p_stripped]['ps_down']
          if( up == 1. )&( down == 1. ): v = '-'
          elif( up == 1. ): v = "%.3f"%down
          elif( down == 1. ): v = "%.3f"%up
          else: v = "%.3f/%.3f"%(down,up)
        else: v = "-"
      else: v = '-'
      # Add value
      systs[sname][key] = v

  elif "scale" in stype:
    with open(sval,"r") as jsonfile: sc_vals = json.load(jsonfile)
    for i in range(len(procs)):
      p,c = procs[i], cats[i]
      key = "%s__%s"%(p,c)
      # Remove year and decay tag
      if "hgg" in p:
        p_stripped = "_".join(p.split("_")[:-2])
        if p_stripped in sc_vals: 
          up, down = sc_vals[p_stripped]['scale_up'], sc_vals[p_stripped]['scale_down']
          if( up == 1. )&( down == 1. ): v = '-'
          elif( up == 1. ): v = "%.3f"%down
          elif( down == 1. ): v = "%.3f"%up
          else: v = "%.3f/%.3f"%(down,up)
        else: v = "-"
      else: v = '-'
      # Add value
      systs[sname][key] = v

  # Json file for ue/ps shape uncertainties
  if "ue_shape" in stype:
    with open(sval,"r") as jsonfile: ue_vals = json.load(jsonfile)
    for i in range(len(procs)):
      p,c = procs[i], cats[i]
      # Remove year and decay tag
      if "hgg" in p:
        p_stripped = "_".join(p.split("_")[:-2])
        key = "%s__%s"%(p_stripped,c)
        if key in ue_vals: 
          up, down = ue_vals[key]['ue_up'], ue_vals[key]['ue_down']
          if( up == 1. )&( down == 1. ): v = '-'
          elif( up == 1. ): v = "%.3f"%down
          elif( down == 1. ): v = "%.3f"%up
          else: v = "%.3f/%.3f"%(down,up)
        else: v = "-"
      else: v = '-'
      key = "%s__%s"%(p,c)
      systs[sname][key] = v

  if "ps_shape" in stype:
    with open(sval,"r") as jsonfile: ps_vals = json.load(jsonfile)
    for i in range(len(procs)):
      p,c = procs[i], cats[i]
      # Remove year and decay tag
      if "hgg" in p:
        p_stripped = "_".join(p.split("_")[:-2])
        key = "%s__%s"%(p_stripped,c)
        if key in ps_vals: 
          up, down = ps_vals[key]['ps_up'], ps_vals[key]['ps_down']
          if( up == 1. )&( down == 1. ): v = '-'
          elif( up == 1. ): v = "%.3f"%down
          elif( down == 1. ): v = "%.3f"%up
          else: v = "%.3f/%.3f"%(down,up)
        else: v = "-"
      else: v = '-'
      key = "%s__%s"%(p,c)
      systs[sname][key] = v

  if "btagreshapenorm" in stype:
    with open(sval,"r") as jsonfile: pc_vals = json.load(jsonfile)
    for i in range(len(procs)):
      p,c = procs[i], cats[i]
      # Remove year and decay tag
      if "hgg" in p:
        p_stripped = "_".join(p.split("_")[:-2])
        key = "%s__%s"%(p_stripped,c)
        if key in pc_vals: 
          var = pc_vals[key]['btagreshape_norm']
          if( var == 1. ): v = '-'
          else: v = "%.3f"%var
        else: v = "-"
      else: v = '-'
      key = "%s__%s"%(p,c)
      systs[sname][key] = v

# Write to file
with open("output_addLine.txt","w") as fout:
  for s,vals in systs.iteritems():
     sline = "%-50s  %s  "%(s,sprior)
     for v in vals.itervalues(): sline += "%s "%v    
     sline = sline[:-1]
     fout.write("%s\n\n"%sline)
