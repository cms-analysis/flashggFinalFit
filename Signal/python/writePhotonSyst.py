# New script to write photon systematics
# * Input is pandas dataframe

print " ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HGG PHOTON SYST WRITE ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ "
import ROOT
import pandas as pd
import pickle
import os, sys
from optparse import OptionParser
import glob
import re

def leave():
  print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HGG PHOTON SYST WRITER (END) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ "
  sys.exit(1)

# Diagonal proc x cat
parallelProc = {
  "RECO_0J_PTH_0_10_Tag0":"GG2H_0J_PTH_0_10,3",
  "RECO_0J_PTH_0_10_Tag1":"GG2H_0J_PTH_0_10,3",
  "RECO_0J_PTH_0_10_Tag2":"GG2H_0J_PTH_0_10,3",
  "RECO_0J_PTH_GT10_Tag0":"GG2H_0J_PTH_GT10,3",
  "RECO_0J_PTH_GT10_Tag1":"GG2H_0J_PTH_GT10,3",
  "RECO_0J_PTH_GT10_Tag2":"GG2H_0J_PTH_GT10,3",
  "RECO_1J_PTH_0_60_Tag0":"GG2H_1J_PTH_0_60,3",
  "RECO_1J_PTH_0_60_Tag1":"GG2H_1J_PTH_0_60,3",
  "RECO_1J_PTH_0_60_Tag2":"GG2H_1J_PTH_0_60,3",
  "RECO_1J_PTH_120_200_Tag0":"GG2H_1J_PTH_120_200,3",
  "RECO_1J_PTH_120_200_Tag1":"GG2H_1J_PTH_120_200,3",
  "RECO_1J_PTH_120_200_Tag2":"GG2H_1J_PTH_120_200,3",
  "RECO_1J_PTH_60_120_Tag0":"GG2H_1J_PTH_60_120,3",
  "RECO_1J_PTH_60_120_Tag1":"GG2H_1J_PTH_60_120,3",
  "RECO_1J_PTH_60_120_Tag2":"GG2H_1J_PTH_60_120,3",
  "RECO_GE2J_PTH_0_60_Tag0":"GG2H_GE2J_MJJ_0_350_PTH_0_60,3",
  "RECO_GE2J_PTH_0_60_Tag1":"GG2H_GE2J_MJJ_0_350_PTH_0_60,2",
  "RECO_GE2J_PTH_0_60_Tag2":"GG2H_GE2J_MJJ_0_350_PTH_0_60,2",
  "RECO_GE2J_PTH_120_200_Tag0":"GG2H_GE2J_MJJ_0_350_PTH_120_200,2",
  "RECO_GE2J_PTH_120_200_Tag1":"GG2H_GE2J_MJJ_0_350_PTH_120_200,2",
  "RECO_GE2J_PTH_120_200_Tag2":"GG2H_GE2J_MJJ_0_350_PTH_120_200,2",
  "RECO_GE2J_PTH_60_120_Tag0":"GG2H_GE2J_MJJ_0_350_PTH_60_120,2",
  "RECO_GE2J_PTH_60_120_Tag1":"GG2H_GE2J_MJJ_0_350_PTH_60_120,2",
  "RECO_GE2J_PTH_60_120_Tag2":"GG2H_GE2J_MJJ_0_350_PTH_60_120,2",
  "RECO_PTH_200_300_Tag0":"GG2H_PTH_200_300,2",
  "RECO_PTH_200_300_Tag1":"GG2H_PTH_200_300,2",
  "RECO_PTH_300_450_Tag0":"GG2H_PTH_300_450,2",
  "RECO_PTH_300_450_Tag1":"GG2H_PTH_300_450,1",
  "RECO_PTH_450_650_Tag0":"GG2H_PTH_450_650,1",
  "RECO_PTH_GT650_Tag0":"GG2H_PTH_GT650,1",
  "RECO_THQ_LEP":"THQ,2",
  "RECO_TTH_HAD_PTH_0_60_Tag0":"TTH_PTH_0_60,1",
  "RECO_TTH_HAD_PTH_0_60_Tag1":"TTH_PTH_0_60,1",
  "RECO_TTH_HAD_PTH_0_60_Tag2":"TTH_PTH_0_60,1",
  "RECO_TTH_HAD_PTH_0_60_Tag3":"TTH_PTH_0_60,1",
  "RECO_TTH_HAD_PTH_120_200_Tag0":"TTH_PTH_120_200,1",
  "RECO_TTH_HAD_PTH_120_200_Tag1":"TTH_PTH_120_200,1",
  "RECO_TTH_HAD_PTH_120_200_Tag2":"TTH_PTH_120_200,1",
  "RECO_TTH_HAD_PTH_120_200_Tag3":"TTH_PTH_120_200,1",
  "RECO_TTH_HAD_PTH_60_120_Tag0":"TTH_PTH_60_120,1",
  "RECO_TTH_HAD_PTH_60_120_Tag1":"TTH_PTH_60_120,1",
  "RECO_TTH_HAD_PTH_60_120_Tag2":"TTH_PTH_60_120,1",
  "RECO_TTH_HAD_PTH_60_120_Tag3":"TTH_PTH_60_120,1",
  "RECO_TTH_HAD_PTH_GT200_Tag0":"TTH_PTH_200_300,1",
  "RECO_TTH_HAD_PTH_GT200_Tag1":"TTH_PTH_200_300,1",
  "RECO_TTH_HAD_PTH_GT200_Tag2":"TTH_PTH_200_300,1",
  "RECO_TTH_HAD_PTH_GT200_Tag3":"TTH_PTH_200_300,1",
  "RECO_TTH_LEP_PTH_0_60_Tag0":"TTH_PTH_0_60,1",
  "RECO_TTH_LEP_PTH_0_60_Tag1":"TTH_PTH_0_60,1",
  "RECO_TTH_LEP_PTH_0_60_Tag2":"TTH_PTH_0_60,1",
  "RECO_TTH_LEP_PTH_0_60_Tag3":"TTH_PTH_0_60,1",
  "RECO_TTH_LEP_PTH_120_200_Tag0":"TTH_PTH_120_200,1",
  "RECO_TTH_LEP_PTH_120_200_Tag1":"TTH_PTH_120_200,1",
  "RECO_TTH_LEP_PTH_60_120_Tag0":"TTH_PTH_60_120,1",
  "RECO_TTH_LEP_PTH_60_120_Tag1":"TTH_PTH_60_120,1",
  "RECO_TTH_LEP_PTH_GT200_Tag0":"TTH_PTH_200_300,1",
  "RECO_TTH_LEP_PTH_GT200_Tag1":"TTH_PTH_200_300,1",
  "RECO_VBFLIKEGGH_Tag0":"GG2H_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25,1",
  "RECO_VBFLIKEGGH_Tag1":"GG2H_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25,1",
  "RECO_VBFTOPO_BSM_Tag0":"VBF_GE2J_MJJ_GT350_PTH_GT200,2",
  "RECO_VBFTOPO_BSM_Tag1":"VBF_GE2J_MJJ_GT350_PTH_GT200,2",
  "RECO_VBFTOPO_JET3VETO_HIGHMJJ_Tag0":"VBF_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25,2",
  "RECO_VBFTOPO_JET3VETO_HIGHMJJ_Tag1":"VBF_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25,2",
  "RECO_VBFTOPO_JET3VETO_LOWMJJ_Tag0":"VBF_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25,2",
  "RECO_VBFTOPO_JET3VETO_LOWMJJ_Tag1":"VBF_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25,2",
  "RECO_VBFTOPO_JET3_HIGHMJJ_Tag0":"VBF_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25,2",
  "RECO_VBFTOPO_JET3_HIGHMJJ_Tag1":"VBF_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25,2",
  "RECO_VBFTOPO_JET3_LOWMJJ_Tag0":"VBF_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25,1",
  "RECO_VBFTOPO_JET3_LOWMJJ_Tag1":"VBF_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25,2",
  "RECO_VBFTOPO_VHHAD_Tag0":"WH2HQQ_GE2J_MJJ_60_120,2",
  "RECO_VBFTOPO_VHHAD_Tag1":"WH2HQQ_GE2J_MJJ_60_120,2",
  "RECO_VH_MET_Tag0":"QQ2HLL_PTV_150_250_0J,1",
  "RECO_VH_MET_Tag1":"QQ2HLL_PTV_75_150,1",
  "RECO_WH_LEP_HIGH_Tag0":"QQ2HLNU_PTV_75_150,3",
  "RECO_WH_LEP_HIGH_Tag1":"QQ2HLNU_PTV_75_150,2",
  "RECO_WH_LEP_HIGH_Tag2":"QQ2HLNU_PTV_75_150,1",
  "RECO_WH_LEP_LOW_Tag0":"QQ2HLNU_PTV_0_75,1",
  "RECO_WH_LEP_LOW_Tag1":"QQ2HLNU_PTV_0_75,2",
  "RECO_WH_LEP_LOW_Tag2":"QQ2HLNU_PTV_0_75,1",
  "RECO_ZH_LEP_Tag0":"QQ2HLL_PTV_75_150,1",
  "RECO_ZH_LEP_Tag1":"QQ2HLL_PTV_75_150,1"
}

def get_options():
  parser = OptionParser()
  parser.add_option("--cats", dest='cats', default='', help="RECO categories")
  parser.add_option("--ext", dest='ext', default='', help="Extension")
  parser.add_option("--scales", dest='scales', default='', help="Photon shape systematics: scales")
  parser.add_option("--scalesCorr", dest='scalesCorr', default='', help='Photon shape systematics: scalesCorr')
  parser.add_option("--scalesGlobal", dest='scalesGlobal', default='', help='Photon shape systematics: scalesGlobal')
  parser.add_option("--smears", dest='smears', default='', help='Photon shape systematics: smears')
  parser.add_option("--setNonDiagonal", dest='setNonDiagonal', default='', help='Set non diagonal to [zero,diag]')
  return parser.parse_args()
(opt,args) = get_options()

# Loop over categories and check if pkl files exist: if not then leave
for cat in opt.cats.split(","):
  if not os.path.exists("./outdir_%s/calcPhotonSyst/pkl/%s.pkl"%(opt.ext,cat)):
    print " --> [ERROR] pkl file does not exist for %s: ./outdir_%s/calcPhotonSyst/pkl/%s.pkl"%(cat,opt.ext,cat)
    leave()

diagStr = '_%s'%opt.setNonDiagonal if opt.setNonDiagonal in ['zero','diag'] else ''
print " --> Writing photon systematics to ./dat/photonCatSyst_%s%s.dat"%(opt.ext,diagStr)

# Else open file to write to
f = open("./dat/photonCatSyst_%s%s.dat"%(opt.ext,diagStr),"w")
# Write preamble
f.write("# this file has been autogenerated by Signal/python/writePhotonSyst.py\n\n")
systs = {'scales':'','scalesCorr':'','scalesGlobal':'','smears':''}
outExtSyst = {'scales':'13TeVscale','scalesCorr':'scale','scalesGlobal':'13TeVscale','smears':'13TeVsmear'}
for stype in ['scales','scalesCorr','scalesGlobal','smears']:
  for s in getattr(opt,stype).split(","):
    sname = "%s_%s"%(s.split(":")[0],outExtSyst[stype])
    if len(s.split(":")) == 1: systs[stype]+= "%s,"%sname 
    else:
      sname = ":".join([sname,":".join(s.split(":")[1:])])
      systs[stype] += "%s,"%sname
for stype, slist in systs.iteritems(): 
  if slist[-1] == ",": systs[stype] = slist[:-1]
f.write("photonCatScales=%s\n"%systs['scales'])
f.write("photonCatScalesCorr=%s\n"%systs['scalesCorr'])
f.write("photonCatSmears=%s\n"%systs['smears'])
f.write("globalScales=%s\n\n"%systs['scalesGlobal'])
f.write("# photonCat                   mean_change    sigma_change    rate_change\n")

# Loop over categories
for cat_idx in range(len(opt.cats.split(","))):
  cat = opt.cats.split(",")[cat_idx]
  # Extract dataframe from pkl file
  with open("./outdir_%s/calcPhotonSyst/pkl/%s.pkl"%(opt.ext,cat),"rb") as fin: data = pickle.load(fin)
  # Loop over rows in pickle file
  for ir,r in data.iterrows():
    f.write("diphotonCat=%g\n"%cat_idx)
    f.write("proc=%s\n"%r['proc'])
    # Loop over systematics
    for stype in ['scales','smears','scalesCorr']:
      for s in systs[stype].split(","):
        if opt.setNonDiagonal == 'zero':
          if r['proc']==parallelProc[cat].split(",")[0]: f.write("%-35s %-13.8f %-13.8f %-13.8f\n"%(s,r['%s_mean'%s],r['%s_sigma'%s],r['%s_rate'%s]))
          else: f.write("%-35s %-13.8f %-13.8f %-13.8f\n"%(s,0.,0.,0.))
        elif opt.setNonDiagonal == 'diag':
          mask = (data['cat']==cat)&(data['proc']==parallelProc[cat].split(",")[0])
          if len(data[mask])==0:
            print " --> [ERROR] No diagonal proc (%s) found for cat: %s. Leaving"%(parallelProc[cat].split(",")[0],cat)
            leave()
          r_diag = data[mask].iloc[0]
          f.write("%-35s %-13.8f %-13.8f %-13.8f\n"%(s,r_diag['%s_mean'%s],r_diag['%s_sigma'%s],r_diag['%s_rate'%s])) 
        else:
          f.write("%-35s %-13.8f %-13.8f %-13.8f\n"%(s,r['%s_mean'%s],r['%s_sigma'%s],r['%s_rate'%s]))
    f.write("\n")

# Close file
f.close()
    

