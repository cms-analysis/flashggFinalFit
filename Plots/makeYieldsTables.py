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
stage0_ggh = od()
stage0_ggh["ggH"] = ['ggH_0J_PTH_0_10','ggZH_had_0J_PTH_0_10','ggH_0J_PTH_GT10','ggZH_had_0J_PTH_GT10','ggH_1J_PTH_0_60','ggZH_had_1J_PTH_0_60','ggH_1J_PTH_60_120','ggZH_had_1J_PTH_60_120','ggH_1J_PTH_120_200','ggZH_had_1J_PTH_120_200','ggH_GE2J_MJJ_0_350_PTH_0_60','ggZH_had_GE2J_MJJ_0_350_PTH_0_60','ggH_GE2J_MJJ_0_350_PTH_60_120','ggZH_had_GE2J_MJJ_0_350_PTH_60_120','ggH_GE2J_MJJ_0_350_PTH_120_200','ggZH_had_GE2J_MJJ_0_350_PTH_120_200','ggH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','ggH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','ggH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','ggH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25','ggZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','ggZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','ggZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','ggZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25','ggH_PTH_200_300','ggZH_had_PTH_200_300','ggH_PTH_300_450','ggH_PTH_450_650','ggH_PTH_GT650','ggZH_had_PTH_300_450','ggZH_had_PTH_450_650','ggZH_had_PTH_GT650']
stage0_ggh["bbH"] = ['bbH']
stage0_ggh["qqH"] = ['qqH_0J','qqH_1J','qqH_GE2J_MJJ_0_60','qqH_GE2J_MJJ_60_120','qqH_GE2J_MJJ_120_350','qqH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','qqH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','qqH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','qqH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25','qqH_GE2J_MJJ_GT350_PTH_GT200','WH_had_0J','WH_had_1J','WH_had_GE2J_MJJ_0_60','WH_had_GE2J_MJJ_60_120','WH_had_GE2J_MJJ_120_350','WH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','WH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','WH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','WH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25','WH_had_GE2J_MJJ_GT350_PTH_GT200','ZH_had_0J','ZH_had_1J','ZH_had_GE2J_MJJ_0_60','ZH_had_GE2J_MJJ_60_120','ZH_had_GE2J_MJJ_120_350','ZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','ZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','ZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','ZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25','ZH_had_GE2J_MJJ_GT350_PTH_GT200']
stage0_ggh["VH_lep"] = ['WH_lep_PTV_0_75','WH_lep_PTV_75_150','WH_lep_PTV_150_250_0J','WH_lep_PTV_150_250_GE1J','WH_lep_PTV_GT250','ZH_lep_PTV_0_75','ZH_lep_PTV_75_150','ZH_lep_PTV_150_250_0J','ZH_lep_PTV_150_250_GE1J','ZH_lep_PTV_GT250','ggZH_ll_PTV_0_75','ggZH_ll_PTV_75_150','ggZH_ll_PTV_150_250_0J','ggZH_ll_PTV_150_250_GE1J','ggZH_ll_PTV_GT250','ggZH_nunu_PTV_0_75','ggZH_nunu_PTV_75_150','ggZH_nunu_PTV_150_250_0J','ggZH_nunu_PTV_150_250_GE1J','ggZH_nunu_PTV_GT250']
stage0_ggh["top"] = ['ttH_PTH_0_60','ttH_PTH_60_120','ttH_PTH_120_200','ttH_PTH_200_300','ttH_PTH_GT300','tHq','tHW']

stage0_qqh = od()
stage0_qqh["ggH"] = ['ggH_0J_PTH_0_10','ggZH_had_0J_PTH_0_10','ggH_0J_PTH_GT10','ggZH_had_0J_PTH_GT10','ggH_1J_PTH_0_60','ggZH_had_1J_PTH_0_60','ggH_1J_PTH_60_120','ggZH_had_1J_PTH_60_120','ggH_1J_PTH_120_200','ggZH_had_1J_PTH_120_200','ggH_GE2J_MJJ_0_350_PTH_0_60','ggZH_had_GE2J_MJJ_0_350_PTH_0_60','ggH_GE2J_MJJ_0_350_PTH_60_120','ggZH_had_GE2J_MJJ_0_350_PTH_60_120','ggH_GE2J_MJJ_0_350_PTH_120_200','ggZH_had_GE2J_MJJ_0_350_PTH_120_200','ggH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','ggH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','ggH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','ggH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25','ggZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','ggZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','ggZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','ggZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25','ggH_PTH_200_300','ggZH_had_PTH_200_300','ggH_PTH_300_450','ggH_PTH_450_650','ggH_PTH_GT650','ggZH_had_PTH_300_450','ggZH_had_PTH_450_650','ggZH_had_PTH_GT650','bbH']
stage0_qqh["VBF"] = ['qqH_0J','qqH_1J','qqH_GE2J_MJJ_0_60','qqH_GE2J_MJJ_60_120','qqH_GE2J_MJJ_120_350','qqH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','qqH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','qqH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','qqH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25','qqH_GE2J_MJJ_GT350_PTH_GT200']
stage0_qqh["VH_had"] = ['WH_had_0J','WH_had_1J','WH_had_GE2J_MJJ_0_60','WH_had_GE2J_MJJ_60_120','WH_had_GE2J_MJJ_120_350','WH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','WH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','WH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','WH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25','WH_had_GE2J_MJJ_GT350_PTH_GT200','ZH_had_0J','ZH_had_1J','ZH_had_GE2J_MJJ_0_60','ZH_had_GE2J_MJJ_60_120','ZH_had_GE2J_MJJ_120_350','ZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','ZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','ZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','ZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25','ZH_had_GE2J_MJJ_GT350_PTH_GT200']
stage0_qqh["VH_lep"] = ['WH_lep_PTV_0_75','WH_lep_PTV_75_150','WH_lep_PTV_150_250_0J','WH_lep_PTV_150_250_GE1J','WH_lep_PTV_GT250','ZH_lep_PTV_0_75','ZH_lep_PTV_75_150','ZH_lep_PTV_150_250_0J','ZH_lep_PTV_150_250_GE1J','ZH_lep_PTV_GT250','ggZH_ll_PTV_0_75','ggZH_ll_PTV_75_150','ggZH_ll_PTV_150_250_0J','ggZH_ll_PTV_150_250_GE1J','ggZH_ll_PTV_GT250','ggZH_nunu_PTV_0_75','ggZH_nunu_PTV_75_150','ggZH_nunu_PTV_150_250_0J','ggZH_nunu_PTV_150_250_GE1J','ggZH_nunu_PTV_GT250']
stage0_qqh["top"] = ['ttH_PTH_0_60','ttH_PTH_60_120','ttH_PTH_120_200','ttH_PTH_200_300','ttH_PTH_GT300','tHq','tHW']

stage0_vh = od()
stage0_vh["ggH"] = ['ggH_0J_PTH_0_10','ggZH_had_0J_PTH_0_10','ggH_0J_PTH_GT10','ggZH_had_0J_PTH_GT10','ggH_1J_PTH_0_60','ggZH_had_1J_PTH_0_60','ggH_1J_PTH_60_120','ggZH_had_1J_PTH_60_120','ggH_1J_PTH_120_200','ggZH_had_1J_PTH_120_200','ggH_GE2J_MJJ_0_350_PTH_0_60','ggZH_had_GE2J_MJJ_0_350_PTH_0_60','ggH_GE2J_MJJ_0_350_PTH_60_120','ggZH_had_GE2J_MJJ_0_350_PTH_60_120','ggH_GE2J_MJJ_0_350_PTH_120_200','ggZH_had_GE2J_MJJ_0_350_PTH_120_200','ggH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','ggH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','ggH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','ggH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25','ggZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','ggZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','ggZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','ggZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25','ggH_PTH_200_300','ggZH_had_PTH_200_300','ggH_PTH_300_450','ggH_PTH_450_650','ggH_PTH_GT650','ggZH_had_PTH_300_450','ggZH_had_PTH_450_650','ggZH_had_PTH_GT650','bbH']
stage0_vh["qqH"] = ['qqH_0J','qqH_1J','qqH_GE2J_MJJ_0_60','qqH_GE2J_MJJ_60_120','qqH_GE2J_MJJ_120_350','qqH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','qqH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','qqH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','qqH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25','qqH_GE2J_MJJ_GT350_PTH_GT200','WH_had_0J','WH_had_1J','WH_had_GE2J_MJJ_0_60','WH_had_GE2J_MJJ_60_120','WH_had_GE2J_MJJ_120_350','WH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','WH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','WH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','WH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25','WH_had_GE2J_MJJ_GT350_PTH_GT200','ZH_had_0J','ZH_had_1J','ZH_had_GE2J_MJJ_0_60','ZH_had_GE2J_MJJ_60_120','ZH_had_GE2J_MJJ_120_350','ZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','ZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','ZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','ZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25','ZH_had_GE2J_MJJ_GT350_PTH_GT200']
stage0_vh["WH_lep"] = ['WH_lep_PTV_0_75','WH_lep_PTV_75_150','WH_lep_PTV_150_250_0J','WH_lep_PTV_150_250_GE1J','WH_lep_PTV_GT250']
stage0_vh["ZH_lep"] = ['ZH_lep_PTV_0_75','ZH_lep_PTV_75_150','ZH_lep_PTV_150_250_0J','ZH_lep_PTV_150_250_GE1J','ZH_lep_PTV_GT250']
stage0_vh["ggZH_lep"] = ['ggZH_ll_PTV_0_75','ggZH_ll_PTV_75_150','ggZH_ll_PTV_150_250_0J','ggZH_ll_PTV_150_250_GE1J','ggZH_ll_PTV_GT250','ggZH_nunu_PTV_0_75','ggZH_nunu_PTV_75_150','ggZH_nunu_PTV_150_250_0J','ggZH_nunu_PTV_150_250_GE1J','ggZH_nunu_PTV_GT250']
stage0_vh["top"] = ['ttH_PTH_0_60','ttH_PTH_60_120','ttH_PTH_120_200','ttH_PTH_200_300','ttH_PTH_GT300','tHq','tHW']

stage0_top = od()
stage0_top["ggH"] = ['ggH_0J_PTH_0_10','ggZH_had_0J_PTH_0_10','ggH_0J_PTH_GT10','ggZH_had_0J_PTH_GT10','ggH_1J_PTH_0_60','ggZH_had_1J_PTH_0_60','ggH_1J_PTH_60_120','ggZH_had_1J_PTH_60_120','ggH_1J_PTH_120_200','ggZH_had_1J_PTH_120_200','ggH_GE2J_MJJ_0_350_PTH_0_60','ggZH_had_GE2J_MJJ_0_350_PTH_0_60','ggH_GE2J_MJJ_0_350_PTH_60_120','ggZH_had_GE2J_MJJ_0_350_PTH_60_120','ggH_GE2J_MJJ_0_350_PTH_120_200','ggZH_had_GE2J_MJJ_0_350_PTH_120_200','ggH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','ggH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','ggH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','ggH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25','ggZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','ggZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','ggZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','ggZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25','ggH_PTH_200_300','ggZH_had_PTH_200_300','ggH_PTH_300_450','ggH_PTH_450_650','ggH_PTH_GT650','ggZH_had_PTH_300_450','ggZH_had_PTH_450_650','ggZH_had_PTH_GT650','bbH']
stage0_top["qqH"] = ['qqH_0J','qqH_1J','qqH_GE2J_MJJ_0_60','qqH_GE2J_MJJ_60_120','qqH_GE2J_MJJ_120_350','qqH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','qqH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','qqH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','qqH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25','qqH_GE2J_MJJ_GT350_PTH_GT200','WH_had_0J','WH_had_1J','WH_had_GE2J_MJJ_0_60','WH_had_GE2J_MJJ_60_120','WH_had_GE2J_MJJ_120_350','WH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','WH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','WH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','WH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25','WH_had_GE2J_MJJ_GT350_PTH_GT200','ZH_had_0J','ZH_had_1J','ZH_had_GE2J_MJJ_0_60','ZH_had_GE2J_MJJ_60_120','ZH_had_GE2J_MJJ_120_350','ZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','ZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','ZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','ZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25','ZH_had_GE2J_MJJ_GT350_PTH_GT200']
stage0_top["VH_lep"] = ['WH_lep_PTV_0_75','WH_lep_PTV_75_150','WH_lep_PTV_150_250_0J','WH_lep_PTV_150_250_GE1J','WH_lep_PTV_GT250','ZH_lep_PTV_0_75','ZH_lep_PTV_75_150','ZH_lep_PTV_150_250_0J','ZH_lep_PTV_150_250_GE1J','ZH_lep_PTV_GT250','ggZH_ll_PTV_0_75','ggZH_ll_PTV_75_150','ggZH_ll_PTV_150_250_0J','ggZH_ll_PTV_150_250_GE1J','ggZH_ll_PTV_GT250','ggZH_nunu_PTV_0_75','ggZH_nunu_PTV_75_150','ggZH_nunu_PTV_150_250_0J','ggZH_nunu_PTV_150_250_GE1J','ggZH_nunu_PTV_GT250']
stage0_top["ttH"] = ['ttH_PTH_0_60','ttH_PTH_60_120','ttH_PTH_120_200','ttH_PTH_200_300','ttH_PTH_GT300']
stage0_top["tHq"] = ['tHq']
stage0_top["tHW"] = ['tHW']


# ggH tags
target_procs_ggh = od()
target_procs_ggh["RECO_0J_PTH_0_10_Tag0"] = ['ggH_0J_PTH_0_10','ggZH_had_0J_PTH_0_10']
target_procs_ggh["RECO_0J_PTH_0_10_Tag1"] = ['ggH_0J_PTH_0_10','ggZH_had_0J_PTH_0_10']
target_procs_ggh["RECO_0J_PTH_0_10_Tag2"] = ['ggH_0J_PTH_0_10','ggZH_had_0J_PTH_0_10']
target_procs_ggh["RECO_0J_PTH_GT10_Tag0"] = ['ggH_0J_PTH_GT10','ggZH_had_0J_PTH_GT10']
target_procs_ggh["RECO_0J_PTH_GT10_Tag1"] = ['ggH_0J_PTH_GT10','ggZH_had_0J_PTH_GT10']
target_procs_ggh["RECO_0J_PTH_GT10_Tag2"] = ['ggH_0J_PTH_GT10','ggZH_had_0J_PTH_GT10']
target_procs_ggh["RECO_1J_PTH_0_60_Tag0"] = ['ggH_1J_PTH_0_60','ggZH_had_1J_PTH_0_60']
target_procs_ggh["RECO_1J_PTH_0_60_Tag1"] = ['ggH_1J_PTH_0_60','ggZH_had_1J_PTH_0_60']
target_procs_ggh["RECO_1J_PTH_0_60_Tag2"] = ['ggH_1J_PTH_0_60','ggZH_had_1J_PTH_0_60']
target_procs_ggh["RECO_1J_PTH_60_120_Tag0"] = ['ggH_1J_PTH_60_120','ggZH_had_1J_PTH_60_120']
target_procs_ggh["RECO_1J_PTH_60_120_Tag1"] = ['ggH_1J_PTH_60_120','ggZH_had_1J_PTH_60_120']
target_procs_ggh["RECO_1J_PTH_60_120_Tag2"] = ['ggH_1J_PTH_60_120','ggZH_had_1J_PTH_60_120']
target_procs_ggh["RECO_1J_PTH_120_200_Tag0"] = ['ggH_1J_PTH_120_200','ggZH_had_1J_PTH_120_200']
target_procs_ggh["RECO_1J_PTH_120_200_Tag1"] = ['ggH_1J_PTH_120_200','ggZH_had_1J_PTH_120_200']
target_procs_ggh["RECO_1J_PTH_120_200_Tag2"] = ['ggH_1J_PTH_120_200','ggZH_had_1J_PTH_120_200']
target_procs_ggh["RECO_GE2J_PTH_0_60_Tag0"] = ['ggH_GE2J_MJJ_0_350_PTH_0_60','ggZH_had_GE2J_MJJ_0_350_PTH_0_60']
target_procs_ggh["RECO_GE2J_PTH_0_60_Tag1"] = ['ggH_GE2J_MJJ_0_350_PTH_0_60','ggZH_had_GE2J_MJJ_0_350_PTH_0_60']
target_procs_ggh["RECO_GE2J_PTH_0_60_Tag2"] = ['ggH_GE2J_MJJ_0_350_PTH_0_60','ggZH_had_GE2J_MJJ_0_350_PTH_0_60']
target_procs_ggh["RECO_GE2J_PTH_60_120_Tag0"] = ['ggH_GE2J_MJJ_0_350_PTH_60_120','ggZH_had_GE2J_MJJ_0_350_PTH_60_120']
target_procs_ggh["RECO_GE2J_PTH_60_120_Tag1"] = ['ggH_GE2J_MJJ_0_350_PTH_60_120','ggZH_had_GE2J_MJJ_0_350_PTH_60_120']
target_procs_ggh["RECO_GE2J_PTH_60_120_Tag2"] = ['ggH_GE2J_MJJ_0_350_PTH_60_120','ggZH_had_GE2J_MJJ_0_350_PTH_60_120']
target_procs_ggh["RECO_GE2J_PTH_120_200_Tag0"] = ['ggH_GE2J_MJJ_0_350_PTH_120_200','ggZH_had_GE2J_MJJ_0_350_PTH_120_200']
target_procs_ggh["RECO_GE2J_PTH_120_200_Tag1"] = ['ggH_GE2J_MJJ_0_350_PTH_120_200','ggZH_had_GE2J_MJJ_0_350_PTH_120_200']
target_procs_ggh["RECO_GE2J_PTH_120_200_Tag2"] = ['ggH_GE2J_MJJ_0_350_PTH_120_200','ggZH_had_GE2J_MJJ_0_350_PTH_120_200']
target_procs_ggh["RECO_PTH_200_300_Tag0"] = ['ggH_PTH_200_300','ggZH_had_PTH_200_300']
target_procs_ggh["RECO_PTH_200_300_Tag1"] = ['ggH_PTH_200_300','ggZH_had_PTH_200_300']
target_procs_ggh["RECO_PTH_300_450_Tag0"] = ['ggH_PTH_300_450','ggZH_had_PTH_300_450']
target_procs_ggh["RECO_PTH_300_450_Tag1"] = ['ggH_PTH_300_450','ggZH_had_PTH_300_450']
target_procs_ggh["RECO_PTH_450_650_Tag0"] = ['ggH_PTH_450_650','ggZH_had_PTH_450_650']
target_procs_ggh["RECO_PTH_GT650_Tag0"] = ['ggH_PTH_GT650','ggZH_had_PTH_GT650']

# Top tags
target_procs_top = od()
target_procs_top["RECO_THQ_LEP"] = ['tHq']
target_procs_top["RECO_TTH_LEP_PTH_0_60_Tag0"] = ['ttH_PTH_0_60']
target_procs_top["RECO_TTH_LEP_PTH_0_60_Tag1"] = ['ttH_PTH_0_60']
target_procs_top["RECO_TTH_LEP_PTH_0_60_Tag2"] = ['ttH_PTH_0_60']
target_procs_top["RECO_TTH_LEP_PTH_60_120_Tag0"] = ['ttH_PTH_60_120']
target_procs_top["RECO_TTH_LEP_PTH_60_120_Tag1"] = ['ttH_PTH_60_120']
target_procs_top["RECO_TTH_LEP_PTH_60_120_Tag2"] = ['ttH_PTH_60_120']
target_procs_top["RECO_TTH_LEP_PTH_120_200_Tag0"] = ['ttH_PTH_120_200']
target_procs_top["RECO_TTH_LEP_PTH_120_200_Tag1"] = ['ttH_PTH_120_200']
target_procs_top["RECO_TTH_LEP_PTH_200_300_Tag0"] = ['ttH_PTH_200_300']
target_procs_top["RECO_TTH_LEP_PTH_GT300_Tag0"] = ['ttH_PTH_GT300']
target_procs_top["RECO_TTH_HAD_PTH_0_60_Tag0"] = ['ttH_PTH_0_60']
target_procs_top["RECO_TTH_HAD_PTH_0_60_Tag1"] = ['ttH_PTH_0_60']
target_procs_top["RECO_TTH_HAD_PTH_0_60_Tag2"] = ['ttH_PTH_0_60']
target_procs_top["RECO_TTH_HAD_PTH_60_120_Tag0"] = ['ttH_PTH_60_120']
target_procs_top["RECO_TTH_HAD_PTH_60_120_Tag1"] = ['ttH_PTH_60_120']
target_procs_top["RECO_TTH_HAD_PTH_60_120_Tag2"] = ['ttH_PTH_60_120']
target_procs_top["RECO_TTH_HAD_PTH_120_200_Tag0"] = ['ttH_PTH_120_200']
target_procs_top["RECO_TTH_HAD_PTH_120_200_Tag1"] = ['ttH_PTH_120_200']
target_procs_top["RECO_TTH_HAD_PTH_120_200_Tag2"] = ['ttH_PTH_120_200']
target_procs_top["RECO_TTH_HAD_PTH_120_200_Tag3"] = ['ttH_PTH_120_200']
target_procs_top["RECO_TTH_HAD_PTH_200_300_Tag0"] = ['ttH_PTH_200_300']
target_procs_top["RECO_TTH_HAD_PTH_200_300_Tag1"] = ['ttH_PTH_200_300']
target_procs_top["RECO_TTH_HAD_PTH_200_300_Tag2"] = ['ttH_PTH_200_300']
target_procs_top["RECO_TTH_HAD_PTH_GT300_Tag0"] = ['ttH_PTH_GT300']
target_procs_top["RECO_TTH_HAD_PTH_GT300_Tag1"] = ['ttH_PTH_GT300']

# VH tags
target_procs_vh = od()
target_procs_vh["RECO_ZH_LEP_Tag0"] = ['ZH_lep_PTV_0_75','ZH_lep_PTV_75_150','ZH_lep_PTV_150_250_0J','ZH_lep_PTV_150_250_GE1J','ZH_lep_PTV_GT250','ggZH_ll_PTV_0_75','ggZH_ll_PTV_75_150','ggZH_ll_PTV_150_250_0J','ggZH_ll_PTV_150_250_GE1J','ggZH_ll_PTV_GT250','ggZH_nunu_PTV_0_75','ggZH_nunu_PTV_75_150','ggZH_nunu_PTV_150_250_0J','ggZH_nunu_PTV_150_250_GE1J','ggZH_nunu_PTV_GT250']
target_procs_vh["RECO_ZH_LEP_Tag1"] = ['ZH_lep_PTV_0_75','ZH_lep_PTV_75_150','ZH_lep_PTV_150_250_0J','ZH_lep_PTV_150_250_GE1J','ZH_lep_PTV_GT250','ggZH_ll_PTV_0_75','ggZH_ll_PTV_75_150','ggZH_ll_PTV_150_250_0J','ggZH_ll_PTV_150_250_GE1J','ggZH_ll_PTV_GT250','ggZH_nunu_PTV_0_75','ggZH_nunu_PTV_75_150','ggZH_nunu_PTV_150_250_0J','ggZH_nunu_PTV_150_250_GE1J','ggZH_nunu_PTV_GT250']
target_procs_vh["RECO_WH_LEP_PTV_0_75_Tag0"] = ['WH_lep_PTV_0_75']
target_procs_vh["RECO_WH_LEP_PTV_0_75_Tag1"] = ['WH_lep_PTV_0_75']
target_procs_vh["RECO_WH_LEP_PTV_75_150_Tag0"] = ['WH_lep_PTV_75_150']
target_procs_vh["RECO_WH_LEP_PTV_75_150_Tag1"] = ['WH_lep_PTV_75_150']
target_procs_vh["RECO_WH_LEP_PTV_GT150_Tag0"] = ['WH_lep_PTV_150_250_0J','WH_lep_PTV_150_250_GE1J','WH_lep_PTV_GT250']
target_procs_vh["RECO_VH_MET_Tag0"] = ['WH_lep_PTV_0_75','WH_lep_PTV_75_150','WH_lep_PTV_150_250_0J','WH_lep_PTV_150_250_GE1J','WH_lep_PTV_GT250','ZH_lep_PTV_0_75','ZH_lep_PTV_75_150','ZH_lep_PTV_150_250_0J','ZH_lep_PTV_150_250_GE1J','ZH_lep_PTV_GT250','ggZH_ll_PTV_0_75','ggZH_ll_PTV_75_150','ggZH_ll_PTV_150_250_0J','ggZH_ll_PTV_150_250_GE1J','ggZH_ll_PTV_GT250','ggZH_nunu_PTV_0_75','ggZH_nunu_PTV_75_150','ggZH_nunu_PTV_150_250_0J','ggZH_nunu_PTV_150_250_GE1J','ggZH_nunu_PTV_GT250']
target_procs_vh["RECO_VH_MET_Tag1"] = ['WH_lep_PTV_0_75','WH_lep_PTV_75_150','WH_lep_PTV_150_250_0J','WH_lep_PTV_150_250_GE1J','WH_lep_PTV_GT250','ZH_lep_PTV_0_75','ZH_lep_PTV_75_150','ZH_lep_PTV_150_250_0J','ZH_lep_PTV_150_250_GE1J','ZH_lep_PTV_GT250','ggZH_ll_PTV_0_75','ggZH_ll_PTV_75_150','ggZH_ll_PTV_150_250_0J','ggZH_ll_PTV_150_250_GE1J','ggZH_ll_PTV_GT250','ggZH_nunu_PTV_0_75','ggZH_nunu_PTV_75_150','ggZH_nunu_PTV_150_250_0J','ggZH_nunu_PTV_150_250_GE1J','ggZH_nunu_PTV_GT250']
target_procs_vh["RECO_VH_MET_Tag2"] = ['WH_lep_PTV_0_75','WH_lep_PTV_75_150','WH_lep_PTV_150_250_0J','WH_lep_PTV_150_250_GE1J','WH_lep_PTV_GT250','ZH_lep_PTV_0_75','ZH_lep_PTV_75_150','ZH_lep_PTV_150_250_0J','ZH_lep_PTV_150_250_GE1J','ZH_lep_PTV_GT250','ggZH_ll_PTV_0_75','ggZH_ll_PTV_75_150','ggZH_ll_PTV_150_250_0J','ggZH_ll_PTV_150_250_GE1J','ggZH_ll_PTV_GT250','ggZH_nunu_PTV_0_75','ggZH_nunu_PTV_75_150','ggZH_nunu_PTV_150_250_0J','ggZH_nunu_PTV_150_250_GE1J','ggZH_nunu_PTV_GT250']

# qqH tags
target_procs_qqh = od()
target_procs_qqh["RECO_VBFLIKEGGH_Tag0"] = ['ggH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','ggH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','ggH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','ggH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25','ggZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','ggZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','ggZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','ggZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25']
target_procs_qqh["RECO_VBFLIKEGGH_Tag1"] = ['ggH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','ggH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','ggH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','ggH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25','ggZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','ggZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','ggZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','ggZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25']
target_procs_qqh["RECO_VBFTOPO_JET3VETO_LOWMJJ_Tag0"] = ['qqH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','WH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','ZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25']
target_procs_qqh["RECO_VBFTOPO_JET3VETO_LOWMJJ_Tag1"] = ['qqH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','WH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','ZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25']
target_procs_qqh["RECO_VBFTOPO_JET3VETO_HIGHMJJ_Tag0"] = ['qqH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','WH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','ZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25']
target_procs_qqh["RECO_VBFTOPO_JET3VETO_HIGHMJJ_Tag1"] = ['qqH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','WH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','ZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25']
target_procs_qqh["RECO_VBFTOPO_JET3_LOWMJJ_Tag0"] = ['qqH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','WH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','ZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25']
target_procs_qqh["RECO_VBFTOPO_JET3_LOWMJJ_Tag1"] = ['qqH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','WH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','ZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25']
target_procs_qqh["RECO_VBFTOPO_JET3_HIGHMJJ_Tag0"] = ['qqH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25','WH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25','ZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25']
target_procs_qqh["RECO_VBFTOPO_JET3_HIGHMJJ_Tag1"] = ['qqH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25','WH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25','ZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25']
target_procs_qqh["RECO_VBFTOPO_BSM_Tag0"] = ['qqH_GE2J_MJJ_GT350_PTH_GT200','WH_had_GE2J_MJJ_GT350_PTH_GT200','ZH_had_GE2J_MJJ_GT350_PTH_GT200']
target_procs_qqh["RECO_VBFTOPO_BSM_Tag1"] = ['qqH_GE2J_MJJ_GT350_PTH_GT200','WH_had_GE2J_MJJ_GT350_PTH_GT200','ZH_had_GE2J_MJJ_GT350_PTH_GT200']
target_procs_qqh["RECO_VBFTOPO_VHHAD_Tag0"] = ['qqH_GE2J_MJJ_60_120','WH_had_GE2J_MJJ_60_120','ZH_had_GE2J_MJJ_60_120']
target_procs_qqh["RECO_VBFTOPO_VHHAD_Tag1"] = ['qqH_GE2J_MJJ_60_120','WH_had_GE2J_MJJ_60_120','ZH_had_GE2J_MJJ_60_120']

def get_options():
  parser = OptionParser()
  parser.add_option("--inputPkl", dest="inputPkl", default='', help="Input pickle file")
  parser.add_option("--loadCatInfo", dest="loadCatInfo", default='', help="Load eff sigma, B and S/S+B from pickle file")
  parser.add_option("--group", dest="group", default='ggh', help="Group of cats")
  parser.add_option("--ext", dest="ext", default='', help="Extension for saving")
  parser.add_option("--yieldVar", dest="yieldVar", default='nominal_yield', help="Name of yield column in dataframe")
  parser.add_option("--translateCats", dest="translateCats", default=None, help="JSON to store cat translations")
  parser.add_option("--translateStage0", dest="translateStage0", default=None, help="JSON to store stage 0 translations")
  return parser.parse_args()
(opt,args) = get_options()

def Translate(name, ndict):
    return ndict[name] if name in ndict else name
def LoadTranslations(jsonfilename):
    with open(jsonfilename) as jsonfile:
        return json.load(jsonfile)
translateCats = {} if opt.translateCats is None else LoadTranslations(opt.translateCats)
translateStage0 = {} if opt.translateStage0 is None else LoadTranslations(opt.translateStage0)

if opt.group == "ggh": 
  stage0 = stage0_ggh
  target_procs = target_procs_ggh
elif opt.group == "qqh": 
  stage0 = stage0_qqh
  target_procs = target_procs_qqh
elif opt.group == "vh": 
  stage0 = stage0_vh
  target_procs = target_procs_vh
elif opt.group == "top": 
  stage0 = stage0_top
  target_procs = target_procs_top
else:
  print " --> [ERROR] target group of categories %s does not exist"%opt.group
  leave()

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
  mask = (data['cat']==cat)&(data['type']=='sig')
  _nominal_yield = data[mask][opt.yieldVar].sum()
  _target_yield = data[mask][data[mask].apply(lambda x: "_".join(x['proc'].split("_")[:-2]) in target_procs[cat], axis=1)][opt.yieldVar].sum()
  _s0_yields = od()
  for s0 in stage0: _s0_yields[s0] = data[mask][data[mask].apply(lambda x: "_".join(x['proc'].split("_")[:-2]) in stage0[s0], axis=1)][opt.yieldVar].sum()

  if opt.loadCatInfo != '':
    catdata_mask = catinfo_data['cat']==cat
    _effSigma = catinfo_data[catdata_mask]['effSigma'].values[0]
    _bkg = catinfo_data[catdata_mask]['bkg_per_GeV'].values[0]
    _SoverSplusB = catinfo_data[catdata_mask]['SoverSplusB'].values[0]

  # Add values to dataframe
  _target_bins_str = '-'
  vals = [cat,_target_bins_str,_nominal_yield,_target_yield]
  for _ys0 in _s0_yields.itervalues(): vals.append(_ys0)
  if opt.loadCatInfo != '': vals.extend( [_effSigma,_bkg,_SoverSplusB] )
  tab_data.loc[len(tab_data)] = vals

# Make table
nColumns = 5+len(stage0.keys())
fout = open("Tables/yields_table_lite_%s%s.txt"%(opt.group,opt.ext),"w")
fout.write("\\begin{tabular}{%s}\n"%("l|"+("c"*(nColumns-1))))
#fout.write("    \\hline \\hline \n")
#fout.write("    \\multirow{3}{*}{Analysis categories} & \\multicolumn{%g}{c|}{SM 125 GeV Higgs boson expected signal} & \\multirow{3}{*}{S/S+B} \\\\ \\cline{2-%g}\n"%(3+len(stage0.keys()),nColumns-1))
fout.write("    \\multirow{3}{*}{Analysis categories} & \\multicolumn{%g}{c}{SM 125 GeV Higgs boson expected signal} & \\multirow{3}{*}{S/S+B} \\\\ \n"%(3+len(stage0.keys())))
#fout.write("     & \\multirow{2}{*}{\\begin{tabular}[c]{@{}c@{}}Total\\\\Yield\\end{tabular}} & \\multirow{2}{*}{\\begin{tabular}[c]{@{}c@{}}Target\\\\Fraction\\end{tabular}} & \\multicolumn{%g}{c|}{Production Mode Fractions} & \\multirow{2}{*}{\\begin{tabular}[c]{@{}c@{}}$\\sigma_{\\rm{eff}}$\\\\(GeV)\\end{tabular}} & \\\\ \\cline{4-%g}\n"%(len(stage0.keys()),nColumns-2))
fout.write("     & \\multirow{2}{*}{Total} & \\multirow{2}{*}{\\begin{tabular}[c]{@{}c@{}}Target\\\\STXS bin(s)\\end{tabular}} & \\multicolumn{%g}{c}{Production Mode Fractions} & \\multirow{2}{*}{\\begin{tabular}[c]{@{}c@{}}$\\sigma_{\\rm{eff}}$\\\\(GeV)\\end{tabular}} & \\\\ \n"%(len(stage0.keys())))
s0_str = Translate(stage0.keys()[0],translateStage0)
for s0 in stage0.keys()[1:]: s0_str += " & %s"%Translate(s0,translateStage0)
#fout.write("     & & & %s & & \\\\ \\hline \\hline \n"%s0_str)
fout.write("     & & & %s & & \\\\ \\hline \n"%s0_str)
# Add numbers
tag_itr = -1
for ir,r in tab_data.iterrows():
  if tag_itr == -1: 
    tag_itr = len(tab_data[tab_data['cat'].str.contains(r['cat'].split("_Tag")[0])])-1
    doRow = True
  else: doRow = False
  catline = "     %s & %.1f & %.1f\\%%"%(Translate(r['cat'],translateCats),r['nominal_yield'],100*(r['target_yield']/r['nominal_yield']))
  for s0 in stage0:
    pcs0 = 100*(r['%s_yield'%s0]/r['nominal_yield'])
    #if pcs0 < 0.1: catline += " & $<$0.1\\%"
    if pcs0 <= 0.: catline += " & -"
    else: catline += " & %.1f\\%%"%pcs0
  catline += " & %.2f & %.2f"%(r['effSigma'],r['SoverSplusB'])
  fout.write("%s \\\\ \n"%catline)
  #if tag_itr == 0: fout.write("     \\hline\n")
  if tag_itr == 0: fout.write("     [\\cmsTabSkip]\n")
  tag_itr -= 1
#fout.write("     \\hline \n")
fout.write("\\end{tabular}\n")
