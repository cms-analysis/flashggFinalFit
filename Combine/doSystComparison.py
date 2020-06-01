import os
from optparse import OptionParser

def get_options():
  parser = OptionParser()
  parser.add_option('--POI', dest='POI', default='r', help="Parameter of interest")
  parser.add_option('--mode', dest='mode', default='mu_inclusive', help="Mode")
  parser.add_option('--ext', dest='ext', default='', help="If running from datacard with extension")
  return parser.parse_args()
(opt,args) = get_options()


#cmdLine = "plot1DScan.py ./runFits%s_%s/profile1D_syst_%s.root --y-cut 20 --y-max 20 --output ./runFits%s_%s/Plots/profile1D_%s%s --POI %s --translate ../Plots/pois_maximal.json --main-label Expected --main-color 1 --others ./runFits%s_%s/profile1D_statonly_%s.root:\"Stat. only\":1 --logo-sub \"Preliminary\" --breakdown Syst,Stat"%(opt.ext,opt.mode,opt.POI,opt.ext,opt.mode,opt.POI,opt.ext,opt.POI,opt.ext,opt.mode,opt.POI)
#os.system(cmdLine)

#cmdLine = "plot1DScan.py ./runFits%s_%s/profile1D_syst_obs_%s.root --y-cut 20 --y-max 20 --output ./runFits%s_%s/Plots/profile1D_%s_obs%s --POI %s --translate ../Plots/pois_maximal.json --main-label Observed --main-color 1 --others  ./runFits%s_%s/profile1D_statonly_obs_%s.root:\"Stat. only\":1 --logo-sub \"Preliminary\" --breakdown Syst,Stat"%(opt.ext,opt.mode,opt.POI,opt.ext,opt.mode,opt.POI,opt.ext,opt.POI,opt.ext,opt.mode,opt.POI)
#os.system(cmdLine)

cmdLine = "plot1DScan.py ./runFits%s_%s/profile1D_syst_obs_%s.root --y-cut 20 --y-max 20 --output ./runFits%s_%s/Plots/profile1D_%s_obs%s_withTHUShape --POI %s --translate ../Plots/pois_maximal.json --main-label Observed --main-color 1 --others  ./runFits%s_%s/profile1D_removeTHUShape_obs_%s.root:\"Remove th. shape unc\":2 ./runFits%s_%s/profile1D_statonly_obs_%s.root:\"Stat. only\":1 --logo-sub \"Preliminary\" --breakdown Th.Shp,Exp,Stat"%(opt.ext,opt.mode,opt.POI,opt.ext,opt.mode,opt.POI,opt.ext,opt.POI,opt.ext,opt.mode,opt.POI,opt.ext,opt.mode,opt.POI)
os.system(cmdLine)

#cmdLine = "plot1DScan.py ./runFits%s_%s/profile1D_syst_%s.root --y-cut 20 --y-max 20 --output ./runFits%s_%s/Plots/profile1D_%s%s --POI %s --translate ../Plots/pois_mu.json --main-label Expected --main-color 1 --others ./runFits%s_%s/profile1D_removeTHU_%s.root:\"Remove th. unc\":2  ./runFits%s_%s/profile1D_statonly_%s.root:\"Stat. only\":1 --logo-sub \"Preliminary\" --breakdown Th,Exp,Stat"%(opt.ext,opt.mode,opt.POI,opt.ext,opt.mode,opt.POI,opt.ext,opt.POI,opt.ext,opt.mode,opt.POI,opt.ext,opt.mode,opt.POI)
#os.system(cmdLine)

#cmdLine = "plot1DScan.py ./runFits%s_%s/profile1D_syst_obs_%s.root --y-cut 20 --y-max 20 --output ./runFits%s_%s/Plots/profile1D_%s_obs%s --POI %s --translate ../Plots/pois_mu.json --main-label Observed --main-color 1 --others ./runFits%s_%s/profile1D_removeTHU_obs_%s.root:\"Remove th. unc\":2  ./runFits%s_%s/profile1D_statonly_obs_%s.root:\"Stat. only\":1 --logo-sub \"Preliminary\" --breakdown Th,Exp,Stat"%(opt.ext,opt.mode,opt.POI,opt.ext,opt.mode,opt.POI,opt.ext,opt.POI,opt.ext,opt.mode,opt.POI,opt.ext,opt.mode,opt.POI)
#os.system(cmdLine)

#cmdLine = "plot1DScan.py ./runFits_stage1p2_intermediate_mjj/profile1D_syst_removeShape_%s.root --y-cut 20 --y-max 20 --output ./runFits_stage1p2_intermediate_mjj/Plots/profile1D_%s_removeShape --POI %s --translate /vols/build/cms/jl2117/hgg/FinalFits/legacy/March20_prep/CMSSW_10_2_13/src/flashggFinalFit/Plots/pois.json --main-label Expected --main-color 1 --others ./runFits_stage1p2_intermediate_mjj/profile1D_removeTHUShape_removeShape.root:\"Remove th. shape unc.\":2  ./runFits_stage1p2_intermediate_mjj/profile1D_statonly_%s.root:\"Stat. only\":1 --logo-sub \"Preliminary (rem. shape)\" --breakdown ThShp,Exp,Stat"%(opt.POI,opt.POI,opt.POI,opt.POI,opt.POI)

#print cmdLine
#os.system(cmdLine)
