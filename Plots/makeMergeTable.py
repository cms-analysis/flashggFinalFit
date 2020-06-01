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

print " ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HGG RESULTS TABLES RUN II ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ "
def leave():
  print " ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HGG RESULTS TABLES RUN II (END) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ "
  sys.exit(1)

params = od()
params['stage1p2_maximal'] = ['r_ggH_0J_low', 'r_ggH_0J_high', 'r_ggH_1J_low', 'r_ggH_1J_med', 'r_ggH_1J_high', 'r_ggH_2J_low', 'r_ggH_2J_med', 'r_ggH_2J_high', 'r_ggH_VBFlike', 'r_ggH_BSM', 'r_qqH_VBFlike', 'r_qqH_VHhad', 'r_qqH_BSM', 'r_WH_lep', 'r_ZH_lep', 'r_ttH', 'r_tH']
params['stage1p2_minimal'] = ['r_ggH_0J_low', 'r_ggH_0J_high', 'r_ggH_1J_low', 'r_ggH_1J_med', 'r_ggH_1J_high', 'r_ggH_2J_low', 'r_ggH_2J_med', 'r_ggH_2J_high', 'r_ggH_BSM_low', 'r_ggH_BSM_high', 'r_qqH_low_mjj_low_pthjj', 'r_qqH_low_mjj_high_pthjj', 'r_qqH_high_mjj_low_pthjj', 'r_qqH_high_mjj_high_pthjj', 'r_qqH_VHhad', 'r_qqH_BSM', 'r_WH_lep_low', 'r_WH_lep_high', 'r_ZH_lep', 'r_ttH_low', 'r_ttH_medlow', 'r_ttH_medhigh', 'r_ttH_high', 'r_tH']

def Translate(name, ndict):
    return ndict[name] if name in ndict else name
def LoadTranslations(jsonfilename):
    with open(jsonfilename) as jsonfile:
        return json.load(jsonfile)
translatePOIs_maximal = LoadTranslations("pois_maximal_latex.json")
translatePOIs_minimal = LoadTranslations("pois_minimal_latex.json")

fout = open("./merging_scheme_table.txt","w")
fout.write("\\begin{table}[htb]\n")
fout.write("    \\centering\n")
fout.write("    \\scriptsize\n")
fout.write("    \\renewcommand{\\arraystretch}{1.5}\n")
fout.write("    \\begin{tabular}{c|c|c}\n")
fout.write("      \\hline \n")
fout.write("      \\multicolumn{3}{c}{\\textbf{STXS stage 1.2: parameter merging schemes}} \\\\ \\hline \n")
fout.write("      & Parameters & STXS bins (number) \\\\ \\hline \n")
fout.write("      \\multirow{17}{*}{Maximal} & %s & - \\\\ \n"%(Translate(params['stage1p2_maximal'][0],translatePOIs_maximal)))
for poi in params['stage1p2_maximal'][1:]: fout.write("       & %s & - \\\\ \n"%(Translate(poi,translatePOIs_maximal)))
fout.write("      \\hline\n")
fout.write("      \\multirow{24}{*}{Minimal} & %s & - \\\\ \n"%(Translate(params['stage1p2_minimal'][0],translatePOIs_minimal)))
for poi in params['stage1p2_minimal'][1:]: fout.write("       & %s & - \\\\ \n"%(Translate(poi,translatePOIs_minimal)))
fout.write("      \\hline\n")
fout.write("    \\end{tabular}\n")
fout.write("\\end{table}\n")
fout.close()
