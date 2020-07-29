import os
from optparse import OptionParser

def get_options():
  parser = OptionParser()
  parser.add_option('--POI', dest='POI', default='r', help="Parameter of interest")
  parser.add_option('--mode', dest='mode', default='mu_inclusive', help="Mode")
  parser.add_option('--ext', dest='ext', default='', help="If running from datacard with extension")
  return parser.parse_args()
(opt,args) = get_options()


#cmdLine = "plot1DScan.py ./runFits%s_%s/profile1D_syst_%s.root --y-cut 20 --y-max 20 --output ./runFits%s_%s/Plots/profile1D_%s%s --POI %s --translate ../Plots/pois_stage0.json --main-label Expected --main-color 1 --others ./runFits%s_%s/profile1D_statonly_%s.root:\"Stat. only\":1 --logo-sub \"Preliminary\" --breakdown Syst,Stat"%(opt.ext,opt.mode,opt.POI,opt.ext,opt.mode,opt.POI,opt.ext,opt.POI,opt.ext,opt.mode,opt.POI)

#cmdLine = "plot1DScan.py ./runFits%s_%s/profile1D_syst_obs_%s.root --y-cut 20 --y-max 20 --output ./runFits%s_%s/Plots/profile1D_%s_obs%s --POI %s --translate ../Plots/pois_stage0.json --main-label Observed --main-color 1 --others  ./runFits%s_%s/profile1D_statonly_obs_%s.root:\"Stat. only\":1 --logo-sub \"Preliminary\" --breakdown Syst,Stat"%(opt.ext,opt.mode,opt.POI,opt.ext,opt.mode,opt.POI,opt.ext,opt.POI,opt.ext,opt.mode,opt.POI)

#cmdLine = "plot1DScan.py ./runFits%s_%s/profile1D_syst_fixedMH_obs_%s.root --y-cut 20 --y-max 20 --output ./runFits%s_%s/Plots/profile1D_%s_fixedMH_obs%s --POI %s --translate ../Plots/pois_stage0.json --main-label Observed --main-color 1 --others  ./runFits%s_%s/profile1D_stat_fixedMH_obs_%s.root:\"Stat. only\":1 --logo-sub \"Preliminary\" --breakdown Syst,Stat"%(opt.ext,opt.mode,opt.POI,opt.ext,opt.mode,opt.POI,opt.ext,opt.POI,opt.ext,opt.mode,opt.POI)

cmdLine = "plot1DScan.py ./runFits%s_%s/profile1D_syst_fixedMH_%s.root --y-cut 20 --y-max 20 --output ./runFits%s_%s/Plots/profile1D_%s_fixedMH%s --POI %s --translate ../Plots/pois_maximal.json --main-label Expected --main-color 1 --others  ./runFits%s_%s/profile1D_stat_fixedMH_%s.root:\"Stat. only\":1 --logo-sub \"Preliminary\" --breakdown Syst,Stat"%(opt.ext,opt.mode,opt.POI,opt.ext,opt.mode,opt.POI,opt.ext,opt.POI,opt.ext,opt.mode,opt.POI)

#cmdLine = "plot1DScan.py ./runFits%s_%s/profile1D_syst_obs_%s.root --y-cut 20 --y-max 20 --output ./runFits%s_%s/Plots/profile1D_%s_obs%s_withTHUShape --POI %s --translate ../Plots/pois_maximal.json --main-label Observed --main-color 1 --others  ./runFits%s_%s/profile1D_removeTHUShape_obs_%s.root:\"Remove th. shape unc\":2 ./runFits%s_%s/profile1D_statonly_obs_%s.root:\"Stat. only\":1 --logo-sub \"Preliminary\" --breakdown Th.Shp,Exp,Stat"%(opt.ext,opt.mode,opt.POI,opt.ext,opt.mode,opt.POI,opt.ext,opt.POI,opt.ext,opt.mode,opt.POI,opt.ext,opt.mode,opt.POI)

#cmdLine = "plot1DScan.py ./runFits%s_%s/profile1D_syst_%s.root --y-cut 20 --y-max 20 --output ./runFits%s_%s/Plots/profile1D_%s%s --POI %s --translate ../Plots/pois_mu.json --main-label Expected --main-color 1 --others ./runFits%s_%s/profile1D_removeTHU_%s.root:\"Remove th. unc\":2  ./runFits%s_%s/profile1D_statonly_%s.root:\"Stat. only\":1 --logo-sub \"Preliminary\" --breakdown Th,Exp,Stat"%(opt.ext,opt.mode,opt.POI,opt.ext,opt.mode,opt.POI,opt.ext,opt.POI,opt.ext,opt.mode,opt.POI,opt.ext,opt.mode,opt.POI)

#cmdLine = "plot1DScan.py ./runFits%s_%s/profile1D_syst_obs_%s.root --y-cut 20 --y-max 20 --output ./runFits%s_%s/Plots/profile1D_%s_obs%s --POI %s --translate ../Plots/pois_mu.json --main-label Observed --main-color 1 --others ./runFits%s_%s/profile1D_removeTHU_obs_%s.root:\"Remove th. unc\":2  ./runFits%s_%s/profile1D_statonly_obs_%s.root:\"Stat. only\":1 --logo-sub \"Preliminary\" --breakdown Th,Exp,Stat"%(opt.ext,opt.mode,opt.POI,opt.ext,opt.mode,opt.POI,opt.ext,opt.POI,opt.ext,opt.mode,opt.POI,opt.ext,opt.mode,opt.POI)

#cmdLine = "plot1DScan.py ./runFits%s_%s/profile1D_syst_fixedMH_obs_%s.root --y-cut 20 --y-max 20 --output ./runFits%s_%s/Plots/profile1D_%s_fixedMH_obs%s --POI %s --translate ../Plots/pois_mu.json --main-label Observed --main-color 1 --others ./runFits%s_%s/profile1D_removeTHU_fixedMH_obs_%s.root:\"Remove th. unc\":2  ./runFits%s_%s/profile1D_stat_fixedMH_obs_%s.root:\"Stat. only\":1 --logo-sub \"Preliminary\" --breakdown Th,Exp,Stat"%(opt.ext,opt.mode,opt.POI,opt.ext,opt.mode,opt.POI,opt.ext,opt.POI,opt.ext,opt.mode,opt.POI,opt.ext,opt.mode,opt.POI)

#cmdLine = "plot1DScan.py ./runFits%s_%s/profile1D_syst_fixedMH_%s.root --y-cut 20 --y-max 20 --output ./runFits%s_%s/Plots/profile1D_%s_fixedMH%s --POI %s --translate ../Plots/pois_mu.json --main-label Expected --main-color 1 --others ./runFits%s_%s/profile1D_removeTHU_fixedMH_%s.root:\"Remove th. unc\":2  ./runFits%s_%s/profile1D_stat_fixedMH_%s.root:\"Stat. only\":1 --logo-sub \"Preliminary\" --breakdown Th,Exp,Stat"%(opt.ext,opt.mode,opt.POI,opt.ext,opt.mode,opt.POI,opt.ext,opt.POI,opt.ext,opt.mode,opt.POI,opt.ext,opt.mode,opt.POI)

#cmdLine = "plot1DScan.py ./runFits%s_%s/profile1D_syst_obs_%s.root --y-cut 20 --y-max 20 --output ./runFits%s_%s/Plots/profile1D_%s_obs%s_MH_cmp --POI %s --translate ../Plots/pois_minimal.json --main-label Profiled --main-color 1 --others ./runFits%s_%s/profile1D_syst_fixedMH_fine_obs_%s.root:\"Fixed (125.38 GeV)\":2  --logo-sub \"Preliminary\""%(opt.ext,opt.mode,opt.POI,opt.ext,opt.mode,opt.POI,opt.ext,opt.POI,opt.ext,opt.mode,opt.POI)
#cmdLine = "plot1DScan.py ./runFits%s_%s/profile1D_syst_obs_%s.root --y-cut 20 --y-max 20 --output ./runFits%s_%s/Plots/profile1D_%s_obs%s_MH_cmp --POI %s --translate ../Plots/pois_mu.json --main-label Profiled --main-color 1 --others ./runFits%s_%s/profile1D_syst_fixedMH_obs_%s.root:\"Fixed (125.38 GeV)\":2  --logo-sub \"Preliminary\""%(opt.ext,opt.mode,opt.POI,opt.ext,opt.mode,opt.POI,opt.ext,opt.POI,opt.ext,opt.mode,opt.POI)

os.system(cmdLine)
