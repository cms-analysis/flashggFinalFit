# Script to make migration + purity matrices and output yields table
#  * Read in PANDAS dataframe

import os, sys
import re
from optparse import OptionParser
import ROOT
import pandas as pd
import glob
import pickle
import json
from collections import OrderedDict as od
# Scripts for plotting
from usefulStyle import setCanvas, drawCMS, drawEnPu, drawEnYear, formatHisto
from shanePalette import set_color_palette

print " ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HGG YIELDS TABLES RUN II ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ "
def leave():
  print " ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HGG YIELDS TABLES RUN II (END) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ "
  sys.exit(1)

# Define STXS stage 0 mapping to procs
stage0 = od()
stage0["ggH"] = ['ggH_0J_PTH_0_10','ggZH_had_0J_PTH_0_10','ggH_0J_PTH_GT10','ggZH_had_0J_PTH_GT10','ggH_1J_PTH_0_60','ggZH_had_1J_PTH_0_60','ggH_1J_PTH_60_120','ggZH_had_1J_PTH_60_120','ggH_1J_PTH_120_200','ggZH_had_1J_PTH_120_200','ggH_GE2J_MJJ_0_350_PTH_0_60','ggZH_had_GE2J_MJJ_0_350_PTH_0_60','ggH_GE2J_MJJ_0_350_PTH_60_120','ggZH_had_GE2J_MJJ_0_350_PTH_60_120','ggH_GE2J_MJJ_0_350_PTH_120_200','ggZH_had_GE2J_MJJ_0_350_PTH_120_200','ggH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','ggH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','ggH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','ggH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25','ggZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','ggZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','ggZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','ggZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25','ggH_PTH_200_300','ggZH_had_PTH_200_300','ggH_PTH_300_450','ggH_PTH_450_650','ggH_PTH_GT650','ggZH_had_PTH_300_450','ggZH_had_PTH_450_650','ggZH_had_PTH_GT650']
stage0["VBF"] = ['qqH_0J','qqH_1J','qqH_GE2J_MJJ_0_60','qqH_GE2J_MJJ_60_120','qqH_GE2J_MJJ_120_350','qqH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','qqH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','qqH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','qqH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25','qqH_GE2J_MJJ_GT350_PTH_GT200']
stage0["VH_had"] = ['WH_had_0J','WH_had_1J','WH_had_GE2J_MJJ_0_60','WH_had_GE2J_MJJ_60_120','WH_had_GE2J_MJJ_120_350','WH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','WH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','WH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','WH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25','WH_had_GE2J_MJJ_GT350_PTH_GT200','ZH_had_0J','ZH_had_1J','ZH_had_GE2J_MJJ_0_60','ZH_had_GE2J_MJJ_60_120','ZH_had_GE2J_MJJ_120_350','ZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','ZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','ZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','ZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25','ZH_had_GE2J_MJJ_GT350_PTH_GT200']
stage0["WH_lep"] = ['WH_lep_PTV_0_75','WH_lep_PTV_75_150','WH_lep_PTV_150_250_0J','WH_lep_PTV_150_250_GE1J','WH_lep_PTV_GT250']
stage0["ZH_lep"] = ['ZH_lep_PTV_0_75','ZH_lep_PTV_75_150','ZH_lep_PTV_150_250_0J','ZH_lep_PTV_150_250_GE1J','ZH_lep_PTV_GT250']
stage0["ggZH_lep"] = ['ggZH_ll_PTV_0_75','ggZH_ll_PTV_75_150','ggZH_ll_PTV_150_250_0J','ggZH_ll_PTV_150_250_GE1J','ggZH_ll_PTV_GT250','ggZH_nunu_PTV_0_75','ggZH_nunu_PTV_75_150','ggZH_nunu_PTV_150_250_0J','ggZH_nunu_PTV_150_250_GE1J','ggZH_nunu_PTV_GT250']
stage0["ttH"] = ['ttH_PTH_0_60','ttH_PTH_60_120','ttH_PTH_120_200','ttH_PTH_200_300','ttH_PTH_GT300']
stage0["bbH"] = ['bbH']
stage0["tHq"] = ['tHq']
stage0["tHW"] = ['tHW']

target_procs = od()
# ggH tags
target_procs["RECO_0J_PTH_0_10_Tag0"] = ['ggH_0J_PTH_0_10','ggZH_had_0J_PTH_0_10']
target_procs["RECO_0J_PTH_0_10_Tag1"] = ['ggH_0J_PTH_0_10','ggZH_had_0J_PTH_0_10']
target_procs["RECO_0J_PTH_0_10_Tag2"] = ['ggH_0J_PTH_0_10','ggZH_had_0J_PTH_0_10']
target_procs["RECO_0J_PTH_GT10_Tag0"] = ['ggH_0J_PTH_GT10','ggZH_had_0J_PTH_GT10']
target_procs["RECO_0J_PTH_GT10_Tag1"] = ['ggH_0J_PTH_GT10','ggZH_had_0J_PTH_GT10']
target_procs["RECO_0J_PTH_GT10_Tag2"] = ['ggH_0J_PTH_GT10','ggZH_had_0J_PTH_GT10']
target_procs["RECO_1J_PTH_0_60_Tag0"] = ['ggH_1J_PTH_0_60','ggZH_had_1J_PTH_0_60']
target_procs["RECO_1J_PTH_0_60_Tag1"] = ['ggH_1J_PTH_0_60','ggZH_had_1J_PTH_0_60']
target_procs["RECO_1J_PTH_0_60_Tag2"] = ['ggH_1J_PTH_0_60','ggZH_had_1J_PTH_0_60']
target_procs["RECO_1J_PTH_60_120_Tag0"] = ['ggH_1J_PTH_60_120','ggZH_had_1J_PTH_60_120']
target_procs["RECO_1J_PTH_60_120_Tag1"] = ['ggH_1J_PTH_60_120','ggZH_had_1J_PTH_60_120']
target_procs["RECO_1J_PTH_60_120_Tag2"] = ['ggH_1J_PTH_60_120','ggZH_had_1J_PTH_60_120']
target_procs["RECO_1J_PTH_120_200_Tag0"] = ['ggH_1J_PTH_120_200','ggZH_had_1J_PTH_120_200']
target_procs["RECO_1J_PTH_120_200_Tag1"] = ['ggH_1J_PTH_120_200','ggZH_had_1J_PTH_120_200']
target_procs["RECO_1J_PTH_120_200_Tag2"] = ['ggH_1J_PTH_120_200','ggZH_had_1J_PTH_120_200']
target_procs["RECO_GE2J_PTH_0_60_Tag0"] = ['ggH_GE2J_MJJ_0_350_PTH_0_60','ggZH_had_GE2J_MJJ_0_350_PTH_0_60']
target_procs["RECO_GE2J_PTH_0_60_Tag1"] = ['ggH_GE2J_MJJ_0_350_PTH_0_60','ggZH_had_GE2J_MJJ_0_350_PTH_0_60']
target_procs["RECO_GE2J_PTH_0_60_Tag2"] = ['ggH_GE2J_MJJ_0_350_PTH_0_60','ggZH_had_GE2J_MJJ_0_350_PTH_0_60']
target_procs["RECO_GE2J_PTH_60_120_Tag0"] = ['ggH_GE2J_MJJ_0_350_PTH_60_120','ggZH_had_GE2J_MJJ_0_350_PTH_60_120']
target_procs["RECO_GE2J_PTH_60_120_Tag1"] = ['ggH_GE2J_MJJ_0_350_PTH_60_120','ggZH_had_GE2J_MJJ_0_350_PTH_60_120']
target_procs["RECO_GE2J_PTH_60_120_Tag2"] = ['ggH_GE2J_MJJ_0_350_PTH_60_120','ggZH_had_GE2J_MJJ_0_350_PTH_60_120']
target_procs["RECO_GE2J_PTH_120_200_Tag0"] = ['ggH_GE2J_MJJ_0_350_PTH_120_200','ggZH_had_GE2J_MJJ_0_350_PTH_120_200']
target_procs["RECO_GE2J_PTH_120_200_Tag1"] = ['ggH_GE2J_MJJ_0_350_PTH_120_200','ggZH_had_GE2J_MJJ_0_350_PTH_120_200']
target_procs["RECO_GE2J_PTH_120_200_Tag2"] = ['ggH_GE2J_MJJ_0_350_PTH_120_200','ggZH_had_GE2J_MJJ_0_350_PTH_120_200']
target_procs["RECO_VBFLIKEGGH_Tag0"] = ['ggH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','ggH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','ggH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','ggH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25','ggZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','ggZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','ggZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','ggZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25']
target_procs["RECO_VBFLIKEGGH_Tag1"] = ['ggH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','ggH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','ggH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','ggH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25','ggZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','ggZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','ggZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','ggZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25']
target_procs["RECO_PTH_200_300_Tag0"] = ['ggH_PTH_200_300','ggZH_had_PTH_200_300']
target_procs["RECO_PTH_200_300_Tag1"] = ['ggH_PTH_200_300','ggZH_had_PTH_200_300']
target_procs["RECO_PTH_300_450_Tag0"] = ['ggH_PTH_300_450','ggZH_had_PTH_300_450']
target_procs["RECO_PTH_300_450_Tag1"] = ['ggH_PTH_300_450','ggZH_had_PTH_300_450']
target_procs["RECO_PTH_450_650_Tag0"] = ['ggH_PTH_450_650','ggZH_had_PTH_450_650']
target_procs["RECO_PTH_GT650_Tag0"] = ['ggH_PTH_GT650','ggZH_had_PTH_GT650']
# Top tags
target_procs["RECO_THQ_LEP"] = ['tHq']
target_procs["RECO_TTH_LEP_PTH_0_60_Tag0"] = ['ttH_PTH_0_60']
target_procs["RECO_TTH_LEP_PTH_0_60_Tag1"] = ['ttH_PTH_0_60']
target_procs["RECO_TTH_LEP_PTH_0_60_Tag2"] = ['ttH_PTH_0_60']
target_procs["RECO_TTH_LEP_PTH_0_60_Tag3"] = ['ttH_PTH_0_60']
target_procs["RECO_TTH_LEP_PTH_60_120_Tag0"] = ['ttH_PTH_60_120']
target_procs["RECO_TTH_LEP_PTH_60_120_Tag1"] = ['ttH_PTH_60_120']
target_procs["RECO_TTH_LEP_PTH_120_200_Tag0"] = ['ttH_PTH_120_200']
target_procs["RECO_TTH_LEP_PTH_120_200_Tag1"] = ['ttH_PTH_120_200']
target_procs["RECO_TTH_LEP_PTH_GT200_Tag0"] = ['ttH_PTH_200_300','ttH_PTH_GT300']
target_procs["RECO_TTH_LEP_PTH_GT200_Tag1"] = ['ttH_PTH_200_300','ttH_PTH_GT300']
target_procs["RECO_TTH_HAD_PTH_0_60_Tag0"] = ['ttH_PTH_0_60']
target_procs["RECO_TTH_HAD_PTH_0_60_Tag1"] = ['ttH_PTH_0_60']
target_procs["RECO_TTH_HAD_PTH_0_60_Tag2"] = ['ttH_PTH_0_60']
target_procs["RECO_TTH_HAD_PTH_0_60_Tag3"] = ['ttH_PTH_0_60']
target_procs["RECO_TTH_HAD_PTH_60_120_Tag0"] = ['ttH_PTH_60_120']
target_procs["RECO_TTH_HAD_PTH_60_120_Tag1"] = ['ttH_PTH_60_120']
target_procs["RECO_TTH_HAD_PTH_60_120_Tag2"] = ['ttH_PTH_60_120']
target_procs["RECO_TTH_HAD_PTH_60_120_Tag3"] = ['ttH_PTH_60_120']
target_procs["RECO_TTH_HAD_PTH_120_200_Tag0"] = ['ttH_PTH_120_200']
target_procs["RECO_TTH_HAD_PTH_120_200_Tag1"] = ['ttH_PTH_120_200']
target_procs["RECO_TTH_HAD_PTH_120_200_Tag2"] = ['ttH_PTH_120_200']
target_procs["RECO_TTH_HAD_PTH_120_200_Tag3"] = ['ttH_PTH_120_200']
target_procs["RECO_TTH_HAD_PTH_GT200_Tag0"] = ['ttH_PTH_200_300','ttH_PTH_GT300']
target_procs["RECO_TTH_HAD_PTH_GT200_Tag1"] = ['ttH_PTH_200_300','ttH_PTH_GT300']
target_procs["RECO_TTH_HAD_PTH_GT200_Tag2"] = ['ttH_PTH_200_300','ttH_PTH_GT300']
target_procs["RECO_TTH_HAD_PTH_GT200_Tag3"] = ['ttH_PTH_200_300','ttH_PTH_GT300']
# VH tags
target_procs["RECO_ZH_LEP_Tag0"] = ['ZH_lep_PTV_0_75','ZH_lep_PTV_75_150','ZH_lep_PTV_150_250_0J','ZH_lep_PTV_150_250_GE1J','ZH_lep_PTV_GT250','ggZH_ll_PTV_0_75','ggZH_ll_PTV_75_150','ggZH_ll_PTV_150_250_0J','ggZH_ll_PTV_150_250_GE1J','ggZH_ll_PTV_GT250','ggZH_nunu_PTV_0_75','ggZH_nunu_PTV_75_150','ggZH_nunu_PTV_150_250_0J','ggZH_nunu_PTV_150_250_GE1J','ggZH_nunu_PTV_GT250']
target_procs["RECO_ZH_LEP_Tag1"] = ['ZH_lep_PTV_0_75','ZH_lep_PTV_75_150','ZH_lep_PTV_150_250_0J','ZH_lep_PTV_150_250_GE1J','ZH_lep_PTV_GT250','ggZH_ll_PTV_0_75','ggZH_ll_PTV_75_150','ggZH_ll_PTV_150_250_0J','ggZH_ll_PTV_150_250_GE1J','ggZH_ll_PTV_GT250','ggZH_nunu_PTV_0_75','ggZH_nunu_PTV_75_150','ggZH_nunu_PTV_150_250_0J','ggZH_nunu_PTV_150_250_GE1J','ggZH_nunu_PTV_GT250']
target_procs["RECO_WH_LEP_LOW_Tag0"] = ['WH_lep_PTV_0_75']
target_procs["RECO_WH_LEP_LOW_Tag1"] = ['WH_lep_PTV_0_75']
target_procs["RECO_WH_LEP_LOW_Tag2"] = ['WH_lep_PTV_0_75']
target_procs["RECO_WH_LEP_HIGH_Tag0"] = ['WH_lep_PTV_75_150','WH_lep_PTV_150_250_0J','WH_lep_PTV_150_250_GE1J','WH_lep_PTV_GT250']
target_procs["RECO_WH_LEP_HIGH_Tag1"] = ['WH_lep_PTV_75_150','WH_lep_PTV_150_250_0J','WH_lep_PTV_150_250_GE1J','WH_lep_PTV_GT250']
target_procs["RECO_WH_LEP_HIGH_Tag2"] = ['WH_lep_PTV_75_150','WH_lep_PTV_150_250_0J','WH_lep_PTV_150_250_GE1J','WH_lep_PTV_GT250']
target_procs["RECO_VH_MET_Tag0"] = ['WH_lep_PTV_0_75','WH_lep_PTV_75_150','WH_lep_PTV_150_250_0J','WH_lep_PTV_150_250_GE1J','WH_lep_PTV_GT250','ZH_lep_PTV_0_75','ZH_lep_PTV_75_150','ZH_lep_PTV_150_250_0J','ZH_lep_PTV_150_250_GE1J','ZH_lep_PTV_GT250','ggZH_ll_PTV_0_75','ggZH_ll_PTV_75_150','ggZH_ll_PTV_150_250_0J','ggZH_ll_PTV_150_250_GE1J','ggZH_ll_PTV_GT250','ggZH_nunu_PTV_0_75','ggZH_nunu_PTV_75_150','ggZH_nunu_PTV_150_250_0J','ggZH_nunu_PTV_150_250_GE1J','ggZH_nunu_PTV_GT250']
target_procs["RECO_VH_MET_Tag1"] = ['WH_lep_PTV_0_75','WH_lep_PTV_75_150','WH_lep_PTV_150_250_0J','WH_lep_PTV_150_250_GE1J','WH_lep_PTV_GT250','ZH_lep_PTV_0_75','ZH_lep_PTV_75_150','ZH_lep_PTV_150_250_0J','ZH_lep_PTV_150_250_GE1J','ZH_lep_PTV_GT250','ggZH_ll_PTV_0_75','ggZH_ll_PTV_75_150','ggZH_ll_PTV_150_250_0J','ggZH_ll_PTV_150_250_GE1J','ggZH_ll_PTV_GT250','ggZH_nunu_PTV_0_75','ggZH_nunu_PTV_75_150','ggZH_nunu_PTV_150_250_0J','ggZH_nunu_PTV_150_250_GE1J','ggZH_nunu_PTV_GT250']
# VBF tags
target_procs["RECO_VBFTOPO_JET3VETO_LOWMJJ_Tag0"] = ['qqH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','WH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','ZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25']
target_procs["RECO_VBFTOPO_JET3VETO_LOWMJJ_Tag1"] = ['qqH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','WH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','ZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25']
target_procs["RECO_VBFTOPO_JET3VETO_HIGHMJJ_Tag0"] = ['qqH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','WH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','ZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25']
target_procs["RECO_VBFTOPO_JET3VETO_HIGHMJJ_Tag1"] = ['qqH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','WH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','ZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25']
target_procs["RECO_VBFTOPO_JET3_LOWMJJ_Tag0"] = ['qqH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','WH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','ZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25']
target_procs["RECO_VBFTOPO_JET3_LOWMJJ_Tag1"] = ['qqH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','WH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','ZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25']
target_procs["RECO_VBFTOPO_JET3_HIGHMJJ_Tag0"] = ['qqH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25','WH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25','ZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25']
target_procs["RECO_VBFTOPO_JET3_HIGHMJJ_Tag1"] = ['qqH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25','WH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25','ZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25']
target_procs["RECO_VBFTOPO_BSM_Tag0"] = ['qqH_GE2J_MJJ_GT350_PTH_GT200','WH_had_GE2J_MJJ_GT350_PTH_GT200','ZH_had_GE2J_MJJ_GT350_PTH_GT200']
target_procs["RECO_VBFTOPO_BSM_Tag1"] = ['qqH_GE2J_MJJ_GT350_PTH_GT200','WH_had_GE2J_MJJ_GT350_PTH_GT200','ZH_had_GE2J_MJJ_GT350_PTH_GT200']
target_procs["RECO_VBFTOPO_VHHAD_Tag0"] = ['qqH_GE2J_MJJ_60_120','WH_had_GE2J_MJJ_60_120','ZH_had_GE2J_MJJ_60_120']
target_procs["RECO_VBFTOPO_VHHAD_Tag1"] = ['qqH_GE2J_MJJ_60_120','WH_had_GE2J_MJJ_60_120','ZH_had_GE2J_MJJ_60_120']



def get_options():
  parser = OptionParser()
  parser.add_option("--inputPkl", dest="inputPkl", default='', help="Input pickle file")
  parser.add_option("--loadCatInfo", dest="loadCatInfo", default='', help="Load eff sigma, B and S/S+B from pickle file")
  parser.add_option("--ext", dest="ext", default='', help="Extension for saving")
  parser.add_option("--translateCats", dest="translateCats", default=None, help="JSON to store cat translations")
  parser.add_option("--translateTargets", dest="translateTargets", default=None, help="JSON to store target proc translations")
  return parser.parse_args()
(opt,args) = get_options()

def Translate(name, ndict):
    return ndict[name] if name in ndict else name
def LoadTranslations(jsonfilename):
    with open(jsonfilename) as jsonfile:
        return json.load(jsonfile)
translateCats = {} if opt.translateCats is None else LoadTranslations(opt.translateCats)
translateTargets = {} if opt.translateTargets is None else LoadTranslations(opt.translateTargets)

# Load input dataFrame from pickle file
if not os.path.exists( opt.inputPkl ): 
  print " --> [ERROR] Input pickle file does not exist. Leaving"
  leave()
with open( opt.inputPkl, "rb" ) as fin: data = pickle.load(fin)
# Load cat info dataframe
if opt.loadCatInfo != '':
  if not os.path.exists( opt.loadCatInfo ):
    print " --> [ERROR] Cat info pickle file does not exist. Leaving"
    leave()
  with open( opt.loadCatInfo, "rb" ) as fin: catinfo_data = pickle.load(fin)

# Initiate pandas dataframe
_columns = ['cat','target_bins_str','nominal_yield','target_yield']
for s0 in stage0: _columns.append( "%s_yield"%s0 )
if opt.loadCatInfo != '': _columns.extend( ['effSigma','bkg','SoverSplusB'] )
tab_data = pd.DataFrame(columns=_columns)

# Fill frame
for cat in target_procs:
  _target_bins_str = Translate(cat,translateTargets)
  mask = data['cat']==cat
  _nominal_yield = data[mask].nominal_yield.sum()
  _target_yield = data[mask][data[mask].apply(lambda x: "_".join(x['proc'].split("_")[:-2]) in target_procs[cat], axis=1)].nominal_yield.sum()
  _s0_yields = od()
  for s0 in stage0: _s0_yields[s0] = data[mask][data[mask].apply(lambda x: "_".join(x['proc'].split("_")[:-2]) in stage0[s0], axis=1)].nominal_yield.sum()

  if opt.loadCatInfo != '':
    catdata_mask = catinfo_data['cat']==cat
    _effSigma = catinfo_data[catdata_mask]['effSigma'].values[0]
    _bkg = catinfo_data[catdata_mask]['bkg_per_GeV'].values[0]
    _SoverSplusB = catinfo_data[catdata_mask]['SoverSplusB'].values[0]

  # Add values to dataframe
  vals = [cat,_target_bins_str,_nominal_yield,_target_yield]
  for _ys0 in _s0_yields.itervalues(): vals.append(_ys0)
  if opt.loadCatInfo != '': vals.extend( [_effSigma,_bkg,_SoverSplusB] )
  tab_data.loc[len(tab_data)] = vals

# Make table
fout = open("./yields_table%s.txt"%opt.ext,"w")
fout.write("\\begin{table}[htb]\n")
fout.write("    \\centering\n")
fout.write("    \\setlength{\\tabcolsep}{4pt}\n")
fout.write("    \\scriptsize\n")
fout.write("    \\begin{tabular}{%s}\n"%("|"+"c|"*17))
fout.write("        \\hline \\hline \n")
fout.write("        \\multirow{3}{*}{Analysis categories} & \\multirow{3}{*}{\\begin{tabular}[c]{@{}c@{}}Target STXS\\\\bins, units in GeV\\end{tabular}} & \\multicolumn{13}{c|}{SM 125 GeV Higgs boson expected signal} & \\multirow{3}{*}{\\begin{tabular}[c]{@{}c@{}}Bkg\\\\(GeV$^{\\rm{-1}}$)\\end{tabular}} & \\multirow{3}{*}{S/S+B} \\\\ \\cline{3-15}\n")
fout.write("         & & \\multirow{2}{*}{\\begin{tabular}[c]{@{}c@{}}Total\\\\Yield\\end{tabular}} & \\multirow{2}{*}{\\begin{tabular}[c]{@{}c@{}}Target\\\\fraction\\end{tabular}} & \\multicolumn{10}{|c|}{STXS stage 0 fractions} & \\multirow{2}{*}{\\begin{tabular}[c]{@{}c@{}}$\\sigma_{\\rm{eff}}$\\\\(GeV)\\end{tabular}} & & \\\\ \\cline{5-14}\n")
fout.write("         & & & & ggH & VBF & VH had & WH lep & ZH lep & ggZH lep & ttH & bbH & tHq & tHW & & & \\\\ \\hline \\hline \n")
# Add numbers
tag_itr = -1
for ir,r in tab_data.iterrows():
  if tag_itr == -1: 
    tag_itr = len(tab_data[tab_data['cat'].str.contains(r['cat'].split("_Tag")[0])])-1
    doRow = True
  else: doRow = False
  if doRow: catline = "         \\tiny{%s} & \\multirow{%g}{*}{\\tiny{%s}} & %.1f & %.1f\\%%"%(Translate(r['cat'],translateCats),(tag_itr+1),r['target_bins_str'],r['nominal_yield'],100*(r['target_yield']/r['nominal_yield']))
  else: catline = "         \\tiny{%s} & & %.1f & %.1f\\%%"%(Translate(r['cat'],translateCats),r['nominal_yield'],100*(r['target_yield']/r['nominal_yield']))
  for s0 in stage0:
    pcs0 = 100*(r['%s_yield'%s0]/r['nominal_yield'])
    #if pcs0 < 0.1: catline += " & $<$0.1\\%"
    if pcs0 == 0.: catline += " & -"
    else: catline += " & %.1f\\%%"%pcs0
  catline += " & %.2f & %.1f & %.2f"%(r['effSigma'],r['bkg'],r['SoverSplusB'])
  fout.write("%s \\\\ \n"%catline)
  if tag_itr == 0: fout.write("         \\hline\n")
  tag_itr -= 1
fout.write("    \\hline \\hline \n")
fout.write("    \\end{tabular}\n")
fout.write("\\end{table}\n")


