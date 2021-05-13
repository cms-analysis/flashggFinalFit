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
params['stage0'] = ['r_ggH', 'r_qqH', 'r_WH_lep', 'r_ZH_lep', 'r_ttH', 'r_tH']
params['stage1p2_maximal'] = ['r_ggH_0J_low', 'r_ggH_0J_high', 'r_ggH_1J_low', 'r_ggH_1J_med', 'r_ggH_1J_high', 'r_ggH_2J_low', 'r_ggH_2J_med', 'r_ggH_2J_high', 'r_ggH_VBFlike', 'r_ggH_BSM', 'r_qqH_VBFlike', 'r_qqH_VHhad', 'r_qqH_BSM', 'r_WH_lep', 'r_ZH_lep', 'r_ttH', 'r_tH']
params['stage1p2_minimal'] = ['r_ggH_0J_low', 'r_ggH_0J_high', 'r_ggH_1J_low', 'r_ggH_1J_med', 'r_ggH_1J_high', 'r_ggH_2J_low', 'r_ggH_2J_med', 'r_ggH_2J_high', 'r_ggH_BSM_low', 'r_ggH_BSM_high', 'r_qqH_low_mjj_low_pthjj', 'r_qqH_low_mjj_high_pthjj', 'r_qqH_high_mjj_low_pthjj', 'r_qqH_high_mjj_high_pthjj', 'r_qqH_VHhad', 'r_qqH_BSM', 'r_WH_lep_low', 'r_WH_lep_high', 'r_ZH_lep', 'r_ttH_low', 'r_ttH_medlow', 'r_ttH_medhigh', 'r_ttH_high', 'r_tH']
params['stage1p2_extended'] = ['r_ggH_0J_low', 'r_ggH_0J_high', 'r_ggH_1J_low', 'r_ggH_1J_med', 'r_ggH_1J_high', 'r_ggH_2J_low', 'r_ggH_2J_med', 'r_ggH_2J_high', 'r_ggH_BSM_low', 'r_ggH_BSM_med', 'r_ggH_BSM_high', 'r_qqH_low_mjj_low_pthjj', 'r_qqH_low_mjj_high_pthjj', 'r_qqH_high_mjj_low_pthjj', 'r_qqH_high_mjj_high_pthjj', 'r_qqH_VHhad', 'r_qqH_BSM', 'r_WH_lep_low', 'r_WH_lep_med', 'r_WH_lep_high', 'r_ZH_lep', 'r_ttH_low', 'r_ttH_medlow', 'r_ttH_medhigh', 'r_ttH_high', 'r_ttH_veryhigh', 'r_tH']

def get_options():
  parser = OptionParser()
  parser.add_option("--inputXSBRjson", dest="inputXSBRjson", default='', help="Input XSBR json file")
  parser.add_option("--mode", dest="mode", default='stage1p2_maximal', help="STXS fit")
  parser.add_option("--translatePOIs", dest="translatePOIs", default=None, help="JSON to store poi translations")
  return parser.parse_args()
(opt,args) = get_options()

def Translate(name, ndict):
    return ndict[name] if name in ndict else name
def LoadTranslations(jsonfilename):
    with open(jsonfilename) as jsonfile:
        return json.load(jsonfile)
translatePOIs = {} if opt.translatePOIs is None else LoadTranslations(opt.translatePOIs)

def CopyDataFromJsonFile(jsonfilename='observed.json', model=None, pois=[]):
  res = {}
  with open(jsonfilename) as jsonfile:
    full = json.load(jsonfile)[model]
    for poi in pois: res[poi] = dict(full[poi])
  return res

# Load xsbr values
with open(opt.inputXSBRjson,"r") as jsonfile: xsbr_theory = json.load(jsonfile)
observed = CopyDataFromJsonFile('observed_UL_redo.json',opt.mode,params[opt.mode])
expected = CopyDataFromJsonFile('expected_UL_redo.json',opt.mode,params[opt.mode])
mh = float(re.sub("p",".",opt.inputXSBRjson.split("_")[-1].split(".json")[0]))

fout = open("Tables/Summary_table_%s.txt"%opt.mode,"w")
fout.write("\\begin{table}[htb]\n")
fout.write("    \\centering\n")
fout.write("    \\footnotesize\n")
fout.write("    \\renewcommand{\\arraystretch}{1.8}\n")
fout.write("    \\setlength{\\tabcolsep}{3pt}\n")
fout.write("    \\begin{tabular}{c|c|ccc|c}\n")
fout.write("      \\hline \n")
if opt.mode == "stage0":
  fout.write("      \\multicolumn{6}{c}{\\textbf{STXS stage 0}} \\\\ \\hline \n")
else:
  fout.write("      \\multicolumn{6}{c}{\\textbf{STXS stage 1.2: %s merging scheme}} \\\\ \\hline \n"%opt.mode.split("_")[-1])
fout.write("      \\multirow{3}{*}{Parameters} & \\multicolumn{4}{c|}{$\\sigma\\mathcal{B}$~[fb]} & $\\sigma\\mathcal{B}$/$(\\sigma\\mathcal{B})_{\\rm{SM}}$ \\\\ \\cline{2-5} \n")
fout.write("      & SM prediction & \\multicolumn{3}{c|}{Observed (Expected)} & Observed (Expected) \\\\ \n")
fout.write("      & \\scriptsize{($m_H$~=~%.2f~GeV)} & Best fit & Stat unc. & Syst unc. & Best fit \\\\ \\hline \n"%mh)
for poi in params[opt.mode]:
  sm_pred = "\\begin{tabular}{r@{}l}$%.2f$ & {}$^{+%.2f}_{-%.2f}$\\end{tabular}"%(xsbr_theory[poi]['nominal'],xsbr_theory[poi]['High01Sigma'],xsbr_theory[poi]['Low01Sigma'])
  bf = "\\begin{tabular}{r@{}l@{}l}$%.2f$ & {}$^{+%.2f}_{-%.2f}$ & $\Big($$^{+%.2f}_{-%.2f}$$\Big)$ \\end{tabular}"%(xsbr_theory[poi]['nominal']*observed[poi]['Val'],abs(xsbr_theory[poi]['nominal']*observed[poi]['ErrorHi']),abs(xsbr_theory[poi]['nominal']*observed[poi]['ErrorLo']),abs(xsbr_theory[poi]['nominal']*expected[poi]['ErrorHi']),abs(xsbr_theory[poi]['nominal']*expected[poi]['ErrorLo']))
  stat = "\\begin{tabular}{@{}l@{}l}{}$^{+%.2f}_{-%.2f}$ & $\Big($$^{+%.2f}_{-%.2f}$$\Big)$ \\end{tabular}"%(abs(xsbr_theory[poi]['nominal']*observed[poi]['StatHi']),abs(xsbr_theory[poi]['nominal']*observed[poi]['StatLo']),abs(xsbr_theory[poi]['nominal']*expected[poi]['StatHi']),abs(xsbr_theory[poi]['nominal']*expected[poi]['StatLo']))
  syst = "\\begin{tabular}{@{}l@{}l}{}$^{+%.2f}_{-%.2f}$ & $\Big($$^{+%.2f}_{-%.2f}$$\Big)$ \\end{tabular}"%(abs(xsbr_theory[poi]['nominal']*observed[poi]['SystHi']),abs(xsbr_theory[poi]['nominal']*observed[poi]['SystLo']),abs(xsbr_theory[poi]['nominal']*expected[poi]['SystHi']),abs(xsbr_theory[poi]['nominal']*expected[poi]['SystLo']))
  #syst = "-"
  ratio = "\\begin{tabular}{r@{}l@{}l}$%.2f$ & {}$^{+%.2f}_{-%.2f}$ & $\Big($$^{+%.2f}_{-%.2f}$$\Big)$ \\end{tabular}"%(observed[poi]['Val'],abs(observed[poi]['ErrorHi']),abs(observed[poi]['ErrorLo']),abs(expected[poi]['ErrorHi']),abs(expected[poi]['ErrorLo']))
  row_str = "%s & %s & %s & %s & %s & %s"%(Translate(poi,translatePOIs),sm_pred,bf,stat,syst,ratio)
  fout.write("      %s \\\\ \n"%row_str)
fout.write("      \\hline \n")
fout.write("    \\end{tabular}\n")
fout.write("\\end{table}\n")
fout.close()
