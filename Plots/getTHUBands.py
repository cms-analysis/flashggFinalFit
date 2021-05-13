import os, sys
import math
import re
from optparse import OptionParser
import ROOT
import pandas as pd
import glob
import pickle
import json
from collections import OrderedDict as od

print " ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HGG THU BANDS RUN II ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ "
def leave():
  print " ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HGG THU BANDS RUN II (END) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ "
  sys.exit(1)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# List of parameter merging schemes
paramMergingScheme_stage0 = od()
paramMergingScheme_stage0["r_ggH"] = ['bbH','ggH_0J_PTH_0_10','ggZH_had_0J_PTH_0_10','ggH_0J_PTH_GT10','ggZH_had_0J_PTH_GT10','ggH_1J_PTH_0_60','ggZH_had_1J_PTH_0_60','ggH_1J_PTH_60_120','ggZH_had_1J_PTH_60_120','ggH_1J_PTH_120_200','ggZH_had_1J_PTH_120_200','ggH_GE2J_MJJ_0_350_PTH_0_60','ggZH_had_GE2J_MJJ_0_350_PTH_0_60','ggH_GE2J_MJJ_0_350_PTH_60_120','ggZH_had_GE2J_MJJ_0_350_PTH_60_120','ggH_GE2J_MJJ_0_350_PTH_120_200','ggZH_had_GE2J_MJJ_0_350_PTH_120_200','ggH_PTH_200_300','ggZH_had_PTH_200_300','ggH_PTH_300_450','ggH_PTH_450_650','ggH_PTH_GT650','ggZH_had_PTH_300_450','ggZH_had_PTH_450_650','ggZH_had_PTH_GT650','ggH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','ggZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','ggH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','ggZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','ggH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','ggZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','ggH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25','ggZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25']
paramMergingScheme_stage0["r_qqH"] = ['qqH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','WH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','ZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','qqH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','WH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','ZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','qqH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','WH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','ZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','qqH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25','WH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25','ZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25','qqH_GE2J_MJJ_60_120','WH_had_GE2J_MJJ_60_120','ZH_had_GE2J_MJJ_60_120','qqH_GE2J_MJJ_GT350_PTH_GT200','WH_had_GE2J_MJJ_GT350_PTH_GT200','ZH_had_GE2J_MJJ_GT350_PTH_GT200']
paramMergingScheme_stage0["r_WH_lep"] = ['WH_lep_PTV_0_75','WH_lep_PTV_75_150','WH_lep_PTV_150_250_0J','WH_lep_PTV_150_250_GE1J','WH_lep_PTV_GT250']
paramMergingScheme_stage0["r_ZH_lep"] = ['ZH_lep_PTV_0_75','ZH_lep_PTV_75_150','ZH_lep_PTV_150_250_0J','ZH_lep_PTV_150_250_GE1J','ZH_lep_PTV_GT250','ggZH_ll_PTV_0_75','ggZH_ll_PTV_75_150','ggZH_ll_PTV_150_250_0J','ggZH_ll_PTV_150_250_GE1J','ggZH_ll_PTV_GT250','ggZH_nunu_PTV_0_75','ggZH_nunu_PTV_75_150','ggZH_nunu_PTV_150_250_0J','ggZH_nunu_PTV_150_250_GE1J','ggZH_nunu_PTV_GT250']
paramMergingScheme_stage0["r_ttH"] = ['ttH_PTH_0_60','ttH_PTH_60_120','ttH_PTH_120_200','ttH_PTH_200_300','ttH_PTH_GT300']
paramMergingScheme_stage0["r_tH"] = ['tHq','tHW']

paramMergingScheme_maximal = od()
paramMergingScheme_maximal["r_ggH_0J_low"] = ['ggH_0J_PTH_0_10','ggZH_had_0J_PTH_0_10']
paramMergingScheme_maximal["r_ggH_0J_high"] = ['ggH_0J_PTH_GT10','ggZH_had_0J_PTH_GT10','bbH']
paramMergingScheme_maximal["r_ggH_1J_low"] = ['ggH_1J_PTH_0_60','ggZH_had_1J_PTH_0_60']
paramMergingScheme_maximal["r_ggH_1J_med"] = ['ggH_1J_PTH_60_120','ggZH_had_1J_PTH_60_120']
paramMergingScheme_maximal["r_ggH_1J_high"] = ['ggH_1J_PTH_120_200','ggZH_had_1J_PTH_120_200']
paramMergingScheme_maximal["r_ggH_2J_low"] = ['ggH_GE2J_MJJ_0_350_PTH_0_60','ggZH_had_GE2J_MJJ_0_350_PTH_0_60']
paramMergingScheme_maximal["r_ggH_2J_med"] = ['ggH_GE2J_MJJ_0_350_PTH_60_120','ggZH_had_GE2J_MJJ_0_350_PTH_60_120']
paramMergingScheme_maximal["r_ggH_2J_high"] = ['ggH_GE2J_MJJ_0_350_PTH_120_200','ggZH_had_GE2J_MJJ_0_350_PTH_120_200']
paramMergingScheme_maximal["r_ggH_VBFlike"] = ['ggH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','ggH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','ggH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','ggH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25','ggZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','ggZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','ggZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','ggZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25']
paramMergingScheme_maximal["r_ggH_BSM"] = ['ggH_PTH_200_300','ggZH_had_PTH_200_300','ggH_PTH_300_450','ggH_PTH_450_650','ggH_PTH_GT650','ggZH_had_PTH_300_450','ggZH_had_PTH_450_650','ggZH_had_PTH_GT650']
paramMergingScheme_maximal["r_qqH_VBFlike"] = ['qqH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','WH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','ZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','qqH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','WH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','ZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','qqH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','WH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','ZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','qqH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25','WH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25','ZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25']
paramMergingScheme_maximal["r_qqH_VHhad"] = ['qqH_GE2J_MJJ_60_120','WH_had_GE2J_MJJ_60_120','ZH_had_GE2J_MJJ_60_120']
paramMergingScheme_maximal["r_qqH_BSM"] = ['qqH_GE2J_MJJ_GT350_PTH_GT200','WH_had_GE2J_MJJ_GT350_PTH_GT200','ZH_had_GE2J_MJJ_GT350_PTH_GT200']
paramMergingScheme_maximal["r_WH_lep"] = ['WH_lep_PTV_0_75','WH_lep_PTV_75_150','WH_lep_PTV_150_250_0J','WH_lep_PTV_150_250_GE1J','WH_lep_PTV_GT250']
paramMergingScheme_maximal["r_ZH_lep"] = ['ZH_lep_PTV_0_75','ZH_lep_PTV_75_150','ZH_lep_PTV_150_250_0J','ZH_lep_PTV_150_250_GE1J','ZH_lep_PTV_GT250','ggZH_ll_PTV_0_75','ggZH_ll_PTV_75_150','ggZH_ll_PTV_150_250_0J','ggZH_ll_PTV_150_250_GE1J','ggZH_ll_PTV_GT250','ggZH_nunu_PTV_0_75','ggZH_nunu_PTV_75_150','ggZH_nunu_PTV_150_250_0J','ggZH_nunu_PTV_150_250_GE1J','ggZH_nunu_PTV_GT250']
paramMergingScheme_maximal["r_ttH"] = ['ttH_PTH_0_60','ttH_PTH_60_120','ttH_PTH_120_200','ttH_PTH_200_300','ttH_PTH_GT300']
paramMergingScheme_maximal["r_tH"] = ['tHq','tHW']

paramMergingScheme_minimal = od()
paramMergingScheme_minimal["r_ggH_0J_low"] = ['ggH_0J_PTH_0_10','ggZH_had_0J_PTH_0_10']
paramMergingScheme_minimal["r_ggH_0J_high"] = ['ggH_0J_PTH_GT10','ggZH_had_0J_PTH_GT10','bbH']
paramMergingScheme_minimal["r_ggH_1J_low"] = ['ggH_1J_PTH_0_60','ggZH_had_1J_PTH_0_60']
paramMergingScheme_minimal["r_ggH_1J_med"] = ['ggH_1J_PTH_60_120','ggZH_had_1J_PTH_60_120']
paramMergingScheme_minimal["r_ggH_1J_high"] = ['ggH_1J_PTH_120_200','ggZH_had_1J_PTH_120_200']
paramMergingScheme_minimal["r_ggH_2J_low"] = ['ggH_GE2J_MJJ_0_350_PTH_0_60','ggZH_had_GE2J_MJJ_0_350_PTH_0_60']
paramMergingScheme_minimal["r_ggH_2J_med"] = ['ggH_GE2J_MJJ_0_350_PTH_60_120','ggZH_had_GE2J_MJJ_0_350_PTH_60_120']
paramMergingScheme_minimal["r_ggH_2J_high"] = ['ggH_GE2J_MJJ_0_350_PTH_120_200','ggZH_had_GE2J_MJJ_0_350_PTH_120_200']
paramMergingScheme_minimal["r_ggH_BSM_low"] = ['ggH_PTH_200_300','ggZH_had_PTH_200_300']
paramMergingScheme_minimal["r_ggH_BSM_high"] = ['ggH_PTH_300_450','ggH_PTH_450_650','ggH_PTH_GT650','ggZH_had_PTH_300_450','ggZH_had_PTH_450_650','ggZH_had_PTH_GT650']
paramMergingScheme_minimal["r_qqH_low_mjj_low_pthjj"] = ['qqH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','WH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','ZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','ggH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','ggZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25']
paramMergingScheme_minimal["r_qqH_low_mjj_high_pthjj"] = ['qqH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','WH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','ZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','ggH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','ggZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25']
paramMergingScheme_minimal["r_qqH_high_mjj_low_pthjj"] = ['qqH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','WH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','ZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','ggH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','ggZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25']
paramMergingScheme_minimal["r_qqH_high_mjj_high_pthjj"] = ['qqH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25','WH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25','ZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25','ggH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25','ggZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25']
paramMergingScheme_minimal["r_qqH_VHhad"] = ['qqH_GE2J_MJJ_60_120','WH_had_GE2J_MJJ_60_120','ZH_had_GE2J_MJJ_60_120']
paramMergingScheme_minimal["r_qqH_BSM"] = ['qqH_GE2J_MJJ_GT350_PTH_GT200','WH_had_GE2J_MJJ_GT350_PTH_GT200','ZH_had_GE2J_MJJ_GT350_PTH_GT200']
paramMergingScheme_minimal["r_WH_lep_low"] = ['WH_lep_PTV_0_75']
paramMergingScheme_minimal["r_WH_lep_high"] = ['WH_lep_PTV_75_150','WH_lep_PTV_150_250_0J','WH_lep_PTV_150_250_GE1J','WH_lep_PTV_GT250']
paramMergingScheme_minimal["r_ZH_lep"] = ['ZH_lep_PTV_0_75','ZH_lep_PTV_75_150','ZH_lep_PTV_150_250_0J','ZH_lep_PTV_150_250_GE1J','ZH_lep_PTV_GT250','ggZH_ll_PTV_0_75','ggZH_ll_PTV_75_150','ggZH_ll_PTV_150_250_0J','ggZH_ll_PTV_150_250_GE1J','ggZH_ll_PTV_GT250','ggZH_nunu_PTV_0_75','ggZH_nunu_PTV_75_150','ggZH_nunu_PTV_150_250_0J','ggZH_nunu_PTV_150_250_GE1J','ggZH_nunu_PTV_GT250']
paramMergingScheme_minimal["r_ttH_low"] = ['ttH_PTH_0_60']
paramMergingScheme_minimal["r_ttH_medlow"] = ['ttH_PTH_60_120']
paramMergingScheme_minimal["r_ttH_medhigh"] = ['ttH_PTH_120_200']
paramMergingScheme_minimal["r_ttH_high"] = ['ttH_PTH_200_300','ttH_PTH_GT300']
paramMergingScheme_minimal["r_tH"] = ['tHq','tHW']

paramMergingScheme_extended = od()
paramMergingScheme_extended["r_ggH_0J_low"] = ['ggH_0J_PTH_0_10','ggZH_had_0J_PTH_0_10']
paramMergingScheme_extended["r_ggH_0J_high"] = ['ggH_0J_PTH_GT10','ggZH_had_0J_PTH_GT10','bbH']
paramMergingScheme_extended["r_ggH_1J_low"] = ['ggH_1J_PTH_0_60','ggZH_had_1J_PTH_0_60']
paramMergingScheme_extended["r_ggH_1J_med"] = ['ggH_1J_PTH_60_120','ggZH_had_1J_PTH_60_120']
paramMergingScheme_extended["r_ggH_1J_high"] = ['ggH_1J_PTH_120_200','ggZH_had_1J_PTH_120_200']
paramMergingScheme_extended["r_ggH_2J_low"] = ['ggH_GE2J_MJJ_0_350_PTH_0_60','ggZH_had_GE2J_MJJ_0_350_PTH_0_60']
paramMergingScheme_extended["r_ggH_2J_med"] = ['ggH_GE2J_MJJ_0_350_PTH_60_120','ggZH_had_GE2J_MJJ_0_350_PTH_60_120']
paramMergingScheme_extended["r_ggH_2J_high"] = ['ggH_GE2J_MJJ_0_350_PTH_120_200','ggZH_had_GE2J_MJJ_0_350_PTH_120_200']
paramMergingScheme_extended["r_ggH_BSM_low"] = ['ggH_PTH_200_300','ggZH_had_PTH_200_300']
paramMergingScheme_extended["r_ggH_BSM_med"] = ['ggH_PTH_300_450','ggZH_had_PTH_300_450']
paramMergingScheme_extended["r_ggH_BSM_high"] = ['ggH_PTH_450_650','ggH_PTH_GT650','ggZH_had_PTH_450_650','ggZH_had_PTH_GT650']
paramMergingScheme_extended["r_qqH_low_mjj_low_pthjj"] = ['qqH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','WH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','ZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','ggH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','ggZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25']
paramMergingScheme_extended["r_qqH_low_mjj_high_pthjj"] = ['qqH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','WH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','ZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','ggH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','ggZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25']
paramMergingScheme_extended["r_qqH_high_mjj_low_pthjj"] = ['qqH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','WH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','ZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','ggH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','ggZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25']
paramMergingScheme_extended["r_qqH_high_mjj_high_pthjj"] = ['qqH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25','WH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25','ZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25','ggH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25','ggZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25']
paramMergingScheme_extended["r_qqH_VHhad"] = ['qqH_GE2J_MJJ_60_120','WH_had_GE2J_MJJ_60_120','ZH_had_GE2J_MJJ_60_120']
paramMergingScheme_extended["r_qqH_BSM"] = ['qqH_GE2J_MJJ_GT350_PTH_GT200','WH_had_GE2J_MJJ_GT350_PTH_GT200','ZH_had_GE2J_MJJ_GT350_PTH_GT200']
paramMergingScheme_extended["r_WH_lep_low"] = ['WH_lep_PTV_0_75']
paramMergingScheme_extended["r_WH_lep_med"] = ['WH_lep_PTV_75_150']
paramMergingScheme_extended["r_WH_lep_high"] = ['WH_lep_PTV_150_250_0J','WH_lep_PTV_150_250_GE1J','WH_lep_PTV_GT250']
paramMergingScheme_extended["r_ZH_lep"] = ['ZH_lep_PTV_0_75','ZH_lep_PTV_75_150','ZH_lep_PTV_150_250_0J','ZH_lep_PTV_150_250_GE1J','ZH_lep_PTV_GT250','ggZH_ll_PTV_0_75','ggZH_ll_PTV_75_150','ggZH_ll_PTV_150_250_0J','ggZH_ll_PTV_150_250_GE1J','ggZH_ll_PTV_GT250','ggZH_nunu_PTV_0_75','ggZH_nunu_PTV_75_150','ggZH_nunu_PTV_150_250_0J','ggZH_nunu_PTV_150_250_GE1J','ggZH_nunu_PTV_GT250']
paramMergingScheme_extended["r_ttH_low"] = ['ttH_PTH_0_60']
paramMergingScheme_extended["r_ttH_medlow"] = ['ttH_PTH_60_120']
paramMergingScheme_extended["r_ttH_medhigh"] = ['ttH_PTH_120_200']
paramMergingScheme_extended["r_ttH_high"] = ['ttH_PTH_200_300']
paramMergingScheme_extended["r_ttH_veryhigh"] = ['ttH_PTH_GT300']
paramMergingScheme_extended["r_tH"] = ['tHq','tHW']


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# List of theory systematics to include
theory_systematics = od()
theory_systematics['stage0'] = ['BR_hgg', 'THU_ggH_stxs_Yield', 'THU_ggH_stxs_Res', 'THU_ggH_stxs_Boosted','THU_qqH_Yield','THU_WH_inc', 'THU_ZH_inc', 'THU_ggZH_inc', 'THU_ttH_Yield','QCDscale_ggZH_had','QCDscale_tHq','QCDscale_tHW','QCDscale_bbH','pdf_Higgs_ggH','pdf_Higgs_qqH','pdf_Higgs_VH','pdf_Higgs_ggZH','pdf_Higgs_ttH','pdf_Higgs_tHq','pdf_Higgs_tHW','alphaS_ggH','alphaS_qqH','alphaS_VH','alphaS_ggZH','alphaS_ttH','alphaS_tHq','alphaS_tHW','UnderlyingEvent_norm','PartonShower_norm']
theory_systematics['stage1p2_maximal'] = ['BR_hgg', 'THU_ggH_stxs_Yield', 'THU_ggH_stxs_Res', 'THU_ggH_stxs_Boosted','THU_ggH_stxs_Mig01', 'THU_ggH_stxs_Mig12', 'THU_ggH_stxs_0J_PTH10', 'THU_ggH_stxs_1J_PTH60', 'THU_ggH_stxs_1J_PTH120', 'THU_ggH_stxs_GE2J_PTH60', 'THU_ggH_stxs_GE2J_PTH120', 'THU_ggH_stxs_GE2J_MJJ350', 'THU_ggH_stxs_PTH200', 'THU_qqH_Yield', 'THU_qqH_PTH200', 'THU_qqH_MJJ60', 'THU_qqH_MJJ120', 'THU_qqH_MJJ350', 'THU_qqH_JET01', 'THU_WH_inc', 'THU_ZH_inc', 'THU_ggZH_inc', 'THU_ttH_Yield','QCDscale_ggZH_had','QCDscale_tHq','QCDscale_tHW','QCDscale_bbH','pdf_Higgs_ggH','pdf_Higgs_qqH','pdf_Higgs_VH','pdf_Higgs_ggZH','pdf_Higgs_ttH','pdf_Higgs_tHq','pdf_Higgs_tHW','alphaS_ggH','alphaS_qqH','alphaS_VH','alphaS_ggZH','alphaS_ttH','alphaS_tHq','alphaS_tHW','UnderlyingEvent_norm','PartonShower_norm']
theory_systematics['stage1p2_minimal'] = ['BR_hgg', 'THU_ggH_stxs_Yield', 'THU_ggH_stxs_Res', 'THU_ggH_stxs_Boosted','THU_ggH_stxs_Mig01', 'THU_ggH_stxs_Mig12', 'THU_ggH_stxs_0J_PTH10', 'THU_ggH_stxs_1J_PTH60', 'THU_ggH_stxs_1J_PTH120', 'THU_ggH_stxs_GE2J_PTH60', 'THU_ggH_stxs_GE2J_PTH120', 'THU_ggH_stxs_GE2J_MJJ350', 'THU_ggH_stxs_GE2J_MJJ700', 'THU_ggH_stxs_GE2J_LOWMJJ_PTHJJ25', 'THU_ggH_stxs_GE2J_HIGHMJJ_PTHJJ25', 'THU_ggH_stxs_PTH200', 'THU_ggH_stxs_PTH300','THU_qqH_Yield','THU_qqH_PTH200', 'THU_qqH_MJJ60', 'THU_qqH_MJJ120', 'THU_qqH_MJJ350', 'THU_qqH_MJJ700', 'THU_qqH_PTHJJ25', 'THU_qqH_JET01','THU_WH_inc', 'THU_WH_mig75', 'THU_ZH_inc', 'THU_ggZH_inc', 'THU_ttH_Yield', 'THU_ttH_mig60', 'THU_ttH_mig120', 'THU_ttH_mig200', 'QCDscale_ggZH_had','QCDscale_tHq','QCDscale_tHW','QCDscale_bbH','pdf_Higgs_ggH','pdf_Higgs_qqH','pdf_Higgs_VH','pdf_Higgs_ggZH','pdf_Higgs_ttH','pdf_Higgs_tHq','pdf_Higgs_tHW','alphaS_ggH','alphaS_qqH','alphaS_VH','alphaS_ggZH','alphaS_ttH','alphaS_tHq','alphaS_tHW','UnderlyingEvent_norm','PartonShower_norm']
theory_systematics['stage1p2_extended'] = ['BR_hgg', 'THU_ggH_stxs_Yield', 'THU_ggH_stxs_Res', 'THU_ggH_stxs_Boosted','THU_ggH_stxs_Mig01', 'THU_ggH_stxs_Mig12', 'THU_ggH_stxs_0J_PTH10', 'THU_ggH_stxs_1J_PTH60', 'THU_ggH_stxs_1J_PTH120', 'THU_ggH_stxs_GE2J_PTH60', 'THU_ggH_stxs_GE2J_PTH120', 'THU_ggH_stxs_GE2J_MJJ350', 'THU_ggH_stxs_GE2J_MJJ700', 'THU_ggH_stxs_GE2J_LOWMJJ_PTHJJ25', 'THU_ggH_stxs_GE2J_HIGHMJJ_PTHJJ25', 'THU_ggH_stxs_PTH200', 'THU_ggH_stxs_PTH300','THU_ggH_stxs_PTH450','THU_qqH_Yield','THU_qqH_PTH200', 'THU_qqH_MJJ60', 'THU_qqH_MJJ120', 'THU_qqH_MJJ350', 'THU_qqH_MJJ700', 'THU_qqH_PTHJJ25', 'THU_qqH_JET01','THU_WH_inc', 'THU_WH_mig75', 'THU_WH_mig150', 'THU_ZH_inc', 'THU_ggZH_inc', 'THU_ttH_Yield', 'THU_ttH_mig60', 'THU_ttH_mig120', 'THU_ttH_mig200', 'THU_ttH_mig300', 'QCDscale_ggZH_had','QCDscale_tHq','QCDscale_tHW','QCDscale_bbH','pdf_Higgs_ggH','pdf_Higgs_qqH','pdf_Higgs_VH','pdf_Higgs_ggZH','pdf_Higgs_ttH','pdf_Higgs_tHq','pdf_Higgs_tHW','alphaS_ggH','alphaS_qqH','alphaS_VH','alphaS_ggZH','alphaS_ttH','alphaS_tHq','alphaS_tHW','UnderlyingEvent_norm','PartonShower_norm']

proc_map = {"GG2H":"ggH","VBF":"qqH","WH2HQQ":"WH_had","ZH2HQQ":"ZH_had","GG2HQQ":"ggZH_had","QQ2HLNU":"WH_lep","QQ2HLL":"ZH_lep","GG2HLL":"ggZH_ll","GG2HNUNU":"ggZH_nunu","TTH":"ttH","BBH":"bbH","THQ":"tHq","THW":"tHW","TH":"tHq"}

def get_options():
  parser = OptionParser()
  parser.add_option('--mode', dest='mode', default='maximal', help="Parameter merging scenario e.g. maximal")
  parser.add_option("--inputWS", dest="inputWS", default='', help="Input workspace")
  parser.add_option('--loadSnapshot', dest='loadSnapshot', default='', help="Load snapshot")
  parser.add_option('--setParameter', dest='setParameter', default='', help="Set parameter e.g. MH=125.38,r=1.10")
  parser.add_option("--year", dest="year", default='2018', help="Year to extract THU from")
  return parser.parse_args()
(opt,args) = get_options()

def rooiter(x):
  iter = x.iterator()
  ret = iter.Next()
  while ret:
    yield ret
    ret = iter.Next()

if opt.mode == "maximal": pms, th_systs = paramMergingScheme_maximal, theory_systematics['stage1p2_maximal']
elif opt.mode == "minimal": pms, th_systs = paramMergingScheme_minimal, theory_systematics['stage1p2_minimal']
elif opt.mode == "extended": pms, th_systs = paramMergingScheme_extended, theory_systematics['stage1p2_extended']
elif opt.mode == "stage0": pms, th_systs = paramMergingScheme_stage0, theory_systematics['stage0']
else:
  print " --> [ERROR] %s mode not supported. Leaving"%mode
  sys.exit(1)

# Extract pois
pois = pms.keys()

# Open ROOT file and extract workspace
f = ROOT.TFile(opt.inputWS)
w = f.Get("w")
if opt.loadSnapshot != '': w.loadSnapshot("MultiDimFit")
if opt.setParameter != '':
  for paramMap in opt.setParameter.split(","):
    p, val = paramMap.split("=")
    w.var(p).setVal(float(val))
    print " --> Setting value of %s in workspace to be %s"%(p,val)
print " --> Extracting cross sections for best fit mH = %.2f GeV"%w.var("MH").getVal()
# Extract all XS x BR
br_hgg = w.function("fbr_13TeV").getVal()
xsbr = {}
print " --> Extracting XS from input workspace"
for fxs in rooiter(w.allFunctions().selectByName("fxs_*")):
  # Extract process
  fname = fxs.GetName()
  proc = fname.split("fxs_")[-1].split("_13TeV")[0]
  pm = proc.split("_")[0]
  proc = re.sub(pm,proc_map[pm],proc)
  xsbr[proc] = fxs.getVal()*br_hgg*1000

# Loop over params in merging scheme
poi_xsbr = {}
poi_xsbr_var = {}
for poi, procs in pms.iteritems():
  if poi not in pois: continue
  print " --> For parameter of interest: %s"%poi 
  poi_xsbr[poi] = 0
  poi_xsbr_var[poi] = {}
  for ts in th_systs: 
    if not w.var(ts): continue #If var not in workspace
    poi_xsbr_var[poi]['%s_Up01Sigma'%ts], poi_xsbr_var[poi]['%s_Down01Sigma'%ts] = 0, 0

  # Loop over STXS bins in poi: calculate variations in XS due to syst
  for proc in procs:

    # If removed by pruning...
    if not proc in xsbr: continue

    # Add nominal cross section
    poi_xsbr[poi] += xsbr[proc]

    print "    * process: %s"%proc
    syst_var = {}
    nominal_yield = 0
    # Extract relevant normalisation for proc
    allNorms = w.allFunctions().selectByName("n_exp_final*%s_%s_hgg"%(proc,opt.year))
    for norm in rooiter(allNorms): nominal_yield += norm.getVal()
    for ts in th_systs:
      if not w.var(ts): continue #If var not in workspace
      syst_var['%s_Up01Sigma'%ts] = 0
      w.var(ts).setVal(1.)
      if nominal_yield == 0.: syst_var['%s_Up01Sigma'%ts] = 1.
      else: 
        for norm in rooiter(allNorms): syst_var['%s_Up01Sigma'%ts] += (norm.getVal()/nominal_yield)
      w.var(ts).setVal(0)
      syst_var['%s_Down01Sigma'%ts] = 0
      w.var(ts).setVal(-1.)
      if nominal_yield == 0.: syst_var['%s_Up01Sigma'%ts] = 1.
      else:
        for norm in rooiter(allNorms): syst_var['%s_Down01Sigma'%ts] += (norm.getVal()/nominal_yield)
      w.var(ts).setVal(0)
      # Changes to cross section
      print " --> [DEBUG] (%s): poi = %s, proc = %s, nominal = %.5f, syst_var_up = %.5f, syst_var_down = %.5f"%(ts,poi,proc,xsbr[proc],syst_var['%s_Up01Sigma'%ts],syst_var['%s_Down01Sigma'%ts])
      poi_xsbr_var[poi]['%s_Up01Sigma'%ts] += xsbr[proc]*syst_var['%s_Up01Sigma'%ts]
      poi_xsbr_var[poi]['%s_Down01Sigma'%ts] += xsbr[proc]*syst_var['%s_Down01Sigma'%ts]

# Loop over pois and save xsbr with uncertainties
xsbr_theory = {}
for poi in pois:
  xsbr_theory[poi] = {}
  print " --> Calculating theory uncertainty: %s"%poi
  FracHigh01Sigma2, FracLow01Sigma2 = 0,0
  # Loop over systematics:
  for ts in th_systs:
    if not w.var(ts): continue #If var not in workspace
    up_fracvar, down_fracvar = (poi_xsbr_var[poi]['%s_Up01Sigma'%ts]/poi_xsbr[poi]-1), (poi_xsbr_var[poi]['%s_Down01Sigma'%ts]/poi_xsbr[poi]-1)
    print "    * %s: (upfracvar,downfracvar) = (%.3f,%.3f)"%(ts,up_fracvar,down_fracvar)
    if up_fracvar >= 0: 
      FracHigh01Sigma2 += up_fracvar*up_fracvar
      FracLow01Sigma2 += down_fracvar*down_fracvar
    else: 
      FracHigh01Sigma2 += down_fracvar*down_fracvar
      FracLow01Sigma2 += up_fracvar*up_fracvar
  FracHigh01Sigma = math.sqrt(FracHigh01Sigma2)
  FracLow01Sigma = math.sqrt(FracLow01Sigma2)
  xsbr_theory[poi]['nominal'] = poi_xsbr[poi]
  xsbr_theory[poi]['High01Sigma'] = poi_xsbr[poi]*FracHigh01Sigma
  xsbr_theory[poi]['Low01Sigma'] = poi_xsbr[poi]*FracLow01Sigma
  xsbr_theory[poi]['FracHigh01Sigma'] = FracHigh01Sigma
  xsbr_theory[poi]['FracLow01Sigma'] = FracLow01Sigma

# Write to json file
print " --> Writing to json file: xsbr_theory_%s.json"%opt.mode
if not os.path.isdir("./jsons"): os.system("mkdir ./jsons")
mH_str = "mH_"+re.sub("\.","p","%.2f"%w.var("MH").getVal())
with open("./jsons/xsbr_theory_%s_%s.json"%(opt.mode,mH_str),'w') as jsonfile: json.dump(xsbr_theory,jsonfile)
