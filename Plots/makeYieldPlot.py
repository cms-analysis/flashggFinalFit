
import os, sys
import re
from optparse import OptionParser
import ROOT
import pandas as pd
import glob
import pickle
import json
from collections import OrderedDict as od
import mplhep as hep
hep.style.use("CMS")
# Scripts for plotting
from usefulStyle import setCanvas, drawCMS, drawEnPu, drawEnYear, formatHisto
from shanePalette import set_color_palette





def get_options():
  parser = OptionParser()
  parser.add_option("--inputSeffJsonSM", dest="inputSeffJsonSM", default='jsons/catsSeff_sospbfa3_CMS_hgg_mass.json', help="")
  parser.add_option("--inputSeffBSMJsonSM", dest="inputSeffBSMJsonSM", default='jsons/catsSeff_sospbfa3_1_CMS_hgg_mass.json', help="")
  parser.add_option("--inputBeffJsonSM", dest="inputBeffJsonSM", default='jsons/catsBeff_sospbfa3_CMS_hgg_mass.json', help="")
  parser.add_option("--inputSeffJsonBSM", dest="inputSeffJsonBSM", default='jsons/catsSeff_sospbfa3_1_CMS_hgg_mass.json', help="Group of cats")
  parser.add_option("--inputJsondataratio", dest="inputJsondataratio", default='jsons/catsDataRatioWeighteff_sospbfa3_CMS_hgg_mass.json', help="Extension for saving")
  parser.add_option("--inputJsonDataErrRatio", dest="inputJsonDataErrRatio", default='jsons/catsDataRatioWeightErr_sospbfa3_CMS_hgg_mass.json', help="Extension for saving")
  parser.add_option("--inputJsondata", dest="inputJsondata", default='jsons/catsDataeff_sospbfa3_CMS_hgg_mass.json', help="Extension for saving")
  parser.add_option("--inputJsonweight", dest="inputJsonweight", default='jsons/catsWeights_sospbfa3_CMS_hgg_mass.json', help="Extension for saving")
  parser.add_option("--cats", dest="cats", default='all', help="cats")
  parser.add_option("--translateCats", dest="translateCats", default='cats.json', help="JSON to store cat translations")
  parser.add_option("--out", dest="out", default='VBF', help="type of cat")

  return parser.parse_args()
(opt,args) = get_options()


import json
import numpy as np
import matplotlib.pyplot as plt

# Carica i file JSON
with open(opt.inputSeffJsonSM) as f:
    S = json.load(f) 

with open(opt.inputSeffBSMJsonSM) as f:
    SBSM = json.load(f) 

with open(opt.inputBeffJsonSM) as f:
    B = json.load(f) 

with open(opt.inputJsondataratio) as f:
    D = json.load(f)  

with open(opt.inputJsonDataErrRatio) as f:
    D_err = json.load(f)  


with open(opt.inputJsondata) as f:
    D_tot = json.load(f)  


with open(opt.inputJsonweight) as f:
    W = json.load(f)  

with open(opt.translateCats) as f:
    cats_latex = json.load(f)  

# Estrai le categorie in ordine
if opt.cats=='all': categories = list(S.keys()) 
else:  categories = opt.cats.split(',')

#os.system('export PYTHONPATH=$HOME/.local/lib/python3.11/site-packages:$PYTHONPATH')
labels_latex = [cats_latex[cat] for cat in categories]
#signal_weighted = [S[cat]  for cat in categories] 
signal_weighted = [S[cat] * W[cat] for cat in categories] 
#signal_bsm_weighted = [SBSM[cat] for cat in categories] 
signal_bsm_weighted = [SBSM[cat] * W[cat] for cat in categories] 
weight2 = sum(signal_weighted)/sum(signal_bsm_weighted)
signal_bsm_weighted = [SBSM[cat] * W[cat]* weight2 for cat in categories] 


#data_points =[D[cat]* W[cat]  for cat in categories]
data_points =[D[cat] for cat in categories]
#data_tot_points =[D_tot[cat]* W[cat]  for cat in categories] 
data_err =[D_err[cat] for cat in categories] 
cats_latex =[cats_latex[cat]  for cat in categories] 

fig, ax = plt.subplots(figsize=(15, 10))
hep.cms.label(loc=0)
hep.cms.label(data=True, lumi=137.6)
# Istogramma per il segnale MC moltiplicato per il peso
ax.bar(
    range(len(categories)),
    signal_weighted,
    width=1,
    linewidth=1.5,  
    align='center',
    label=r"$f_{a3}=0$"

)

ax.bar(
    range(len(categories)),
    signal_bsm_weighted,
    width=1,
    linewidth=1.5,  
    align='center',
    alpha = 0.2,
    edgecolor='orange',
    color='orange'
)

ax.bar(
    range(len(categories)),
    signal_bsm_weighted,
    width=1,
    linewidth=6,  
    align='center',
    label=r"$f_{a3}=1$",
    edgecolor='orange',
    color='orange',
    facecolor='none'
)

ax.set_xticks(range(len(categories)))
ax.set_xticklabels(labels_latex, rotation=45, ha="right")
ax.scatter(range(len(categories)),data_points, color='black', label="Data", zorder=3)
print()
ax.errorbar(range(len(categories)), data_points, yerr=data_err ,xerr=0.5, fmt='none', ecolor='black', capsize=5, zorder=2)

ax.set_ylabel("Entries")
ax.set_xlabel("Category")
plt.legend(fontsize=25)
ax.set_xticklabels(cats_latex, rotation=45, ha="right")
#ax.legend()
ax.grid(axis="y", linestyle="--", alpha=0.7)


plt.tight_layout()
plt.savefig('plots/fa3_%s.pdf'%opt.out)

