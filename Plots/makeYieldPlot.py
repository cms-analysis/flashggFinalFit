
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


# Istogramma per il segnale MC moltiplicato per il peso
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.gridspec as gridspec



fig = plt.figure(constrained_layout=True)
gs = fig.add_gridspec(2, 1, height_ratios=[3, 1], hspace=0)
# Subplot principale


ax = plt.subplot(gs[0])
hep.cms.label(data=True, lumi=137.6, ax=ax, loc=0, label="Work in Progress")
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
    alpha=0.2,
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

ax.scatter(range(len(categories)), data_points, color='black', label="Data", zorder=3)
ax.errorbar(range(len(categories)), data_points, yerr=data_err ,xerr=0.5, fmt='none', ecolor='black', capsize=5, zorder=2)

ax.set_xticks(range(len(categories)))
ax.set_xticklabels([])
plt.setp(ax.get_xticklabels(), visible=False)
ax.set_ylabel("Entries/Bin")

ax.legend(fontsize=15)
ax.grid(axis="y", linestyle="--", alpha=0.7)

# Ratio plot
ax_ratio = plt.subplot(gs[1], sharex=ax)


ratio_fa3_0 = np.array(data_points)/ np.array(signal_weighted)
ratio_fa3_1 = np.array(data_points) / np.array(signal_bsm_weighted)
ratio_fa3_1_err = np.array(data_err) / np.array(signal_bsm_weighted)
ratio_fa3_0_err = np.array(data_err) / np.array(signal_weighted)

ax_ratio.scatter(range(len(categories)), ratio_fa3_0, color='#5790fc', zorder=3)
ax_ratio.scatter(range(len(categories)), ratio_fa3_1, color='#f89c20', zorder=3)
ax_ratio.errorbar(range(len(categories)), ratio_fa3_0, yerr=ratio_fa3_0_err, fmt='none', c='#5790fc', capsize=5, zorder=2,xerr=0.5)
ax_ratio.errorbar(range(len(categories)), ratio_fa3_1, yerr=ratio_fa3_1_err, fmt='none', c='#f89c20', capsize=5, zorder=2,xerr=0.5)
if opt.out == 'VHLEP':
    ax_ratio.set_yscale('symlog', linthresh=1)
  #  ax_ratio.set_ylim([0.00000001,150])

ax_ratio.axhline(1, color="black", linestyle="--", linewidth=1.5)  # Linea guida a y=1

ax_ratio.set_ylabel("Data/MC")
ax_ratio.set_xlabel("Bin")
#ax_ratio.legend(fontsize=12)
ax_ratio.grid(axis="y", linestyle="--", alpha=0.7)
ax_ratio.set_xticks(range(len(categories)))
ax_ratio.set_xticklabels(labels_latex, rotation=45, fontsize=15)

#plt.xticks(range(len(categories)), labels_latex, rotation=45, fontsize=15)

plt.savefig('plots/fa3_%s.pdf' % opt.out)

