# Script to calculate photon systematics from parquet files
# Run script once per category, loops over signal processes
# Output is pandas dataframe with systematic variations

print(" ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HGG PHOTON SYST CALCULATOR ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ")
import os
import re
from optparse import OptionParser

import pandas as pd
import numpy as np
import pickle

import matplotlib.pyplot as plt
import mplhep as hep
hep.style.use(hep.style.CMS)

# From tools
from commonTools import *
from commonObjects import *

def leave():
  print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HGG PHOTON SYST CALCULATOR (END) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ")
  exit(0)

# # Function to extract effSigma from binned data
# def get_eff_sigma_binned(data, weights, fraction, bins=80):
#   hist, bin_edges = np.histogram(data, bins=bins, range=(100, 180), weights=weights)
#   # Find shortest interval containing 68.3% of data
#   total_counts = np.sum(hist)
#   target_counts = fraction * total_counts
#   min_width = np.inf
#   for i in range(len(hist)):
#     cumulative_counts = np.sum(hist[i:])
#     if cumulative_counts >= target_counts:
#       width = bin_edges[i + np.argmax(np.cumsum(hist[i:]) >= target_counts)] - bin_edges[i]
#       if width < min_width:
#         min_width = width
#   return min_width / 2.0

# # Function to calculate effSigma from unbinned data
# # Defined as the shortest interval containing 68.3% of the data
# def get_eff_sigma_unbinned(data, fraction):
#   sorted_data = np.sort(data)
#   n_data = len(sorted_data)
#   n_in_interval = int(np.floor(fraction * n_data))
#   min_width = np.inf
#   for i in range(n_data - n_in_interval):
#     width = sorted_data[i + n_in_interval] - sorted_data[i]
#     if width < min_width:
#       min_width = width
#   return min_width / 2.0

# Function to calculate effSigma from unbinned data with weights
def get_eff_sigma_unbinned_weighted(data, weights, fraction):
  sorted_indices = np.argsort(data)
  sorted_data = data[sorted_indices]
  sorted_weights = weights[sorted_indices]
  cumulative_weights = np.cumsum(sorted_weights)
  total_weight = cumulative_weights[-1]
  target_weight = fraction * total_weight
  min_width = np.inf
  for i in range(len(sorted_data)):
    j = np.searchsorted(cumulative_weights, cumulative_weights[i] + target_weight)
    if j < len(sorted_data):
      width = sorted_data[j] - sorted_data[i]
      if width < min_width:
        min_width = width
  return min_width / 2.0

# Function to extract mean, effSigma and rate from a pandas dataframe
def extract_info(df, xvar, weight_var, fraction=0.683):
  mean = np.average(df[xvar], weights=df[weight_var])
  eff_sigma = get_eff_sigma_unbinned_weighted(df[xvar].values, df[weight_var].values, fraction)
  rate = df[weight_var].sum()
  return mean, eff_sigma, rate

def get_mean_var(mean_nominal, mean_up, mean_down, threshold_mean=0.05):
  mean_up_var = (mean_up - mean_nominal)/mean_nominal
  mean_down_var = (mean_down - mean_nominal)/mean_nominal
  mean_var = (abs(mean_up_var) + abs(mean_down_var))/2
  return min(mean_var, threshold_mean)

def get_sigma_var(sigma_nominal, sigma_up, sigma_down, threshold_sigma=0.5):
  sigma_up_var = (sigma_up - sigma_nominal)/sigma_nominal
  sigma_down_var = (sigma_down - sigma_nominal)/sigma_nominal
  sigma_var = (abs(sigma_up_var) + abs(sigma_down_var))/2
  return min(sigma_var, threshold_sigma)

#TODO: should we use midpoint treatment
def get_rate_var(rate_nominal, rate_up, rate_down, threshold_rate=0.05):
  rate_up_var = (rate_up - rate_nominal)/rate_nominal
  rate_down_var = (rate_down - rate_nominal)/rate_nominal
  rate_var = (abs(rate_up_var) + abs(rate_down_var))/2
  return min(rate_var, threshold_rate)

def get_options():
  parser = OptionParser()
  parser.add_option("--xvar", dest='xvar', default='CMS_hgg_mass', help="Observable")
  parser.add_option("--cat", dest='cat', default='', help="RECO category")
  parser.add_option("--procs", dest='procs', default='', help="Signal processes")
  parser.add_option("--ext", dest='ext', default='', help="Extension")
  parser.add_option("--inputDir", dest='inputDir', default='', help="Input parquet directory")
  parser.add_option("--scales", dest='scales', default='', help="Photon shape systematics: scales")
  parser.add_option("--scalesCorr", dest='scalesCorr', default='', help='Photon shape systematics: scalesCorr')
  parser.add_option("--scalesGlobal", dest='scalesGlobal', default='', help='Photon shape systematics: scalesGlobal')
  parser.add_option("--smears", dest='smears', default='', help='Photon shape systematics: smears')
  parser.add_option("--nBins", dest='nBins', default=160, type='int', help='Number of bins in histograms')
  parser.add_option("--thresholdMean", dest='thresholdMean', default=0.05, type='float', help='Reject mean variations if larger than thresholdMean')
  parser.add_option("--thresholdSigma", dest='thresholdSigma', default=0.5, type='float', help='Reject mean variations if larger than thresholdSigma')
  parser.add_option("--thresholdRate", dest='thresholdRate', default=0.05, type='float', help='Reject mean variations if larger than thresholdRate')
  return parser.parse_args()
(opt,args) = get_options()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Define dataFrame
columns_data = ['proc','cat']
for stype in ['scales','scalesCorr','smears']:
  systs = getattr( opt, stype )
  for s in systs.split(","):
    if s == '': continue
    for x in ['mean','sigma','rate']: 
      outputNuisanceExt = "_%s"%outputNuisanceExtMap[stype] if outputNuisanceExtMap[stype] != "" else ""
      columns_data.append("%s%s_%s"%(s,outputNuisanceExt,x))
data = pd.DataFrame( columns=columns_data ) 

# Loop over processes
for proc in opt.procs.split(","):

  # Open nominal parquet file and extract mean, sigma and rate
  input_file = "%s/events__%s.parquet"%(opt.inputDir,proc)
  nominal_df = pd.read_parquet(input_file)

  # Extract events for the given category
  mask = nominal_df['category'] == opt.cat

  # Extract numbers of events
  n_nominal = len(nominal_df[mask])

  if n_nominal <= 0: continue

  # Instantiate row for the current process and category
  row = [proc, opt.cat]

  # Extract weighted mean
  mean_nominal, eff_sigma_nominal, rate_nominal = extract_info(nominal_df[mask], opt.xvar, 'weight', 0.683)

  print(" --> Processing (%s, %s)"%(proc,opt.cat))
  print("   * Nominal: mean = %.3f, effSigma = %.3f, rate = %.5f"%(mean_nominal,eff_sigma_nominal,rate_nominal))

  # Extract mean, sigma and rate variations for each systematic
  i = 0
  for stype in ['scales','scalesCorr','smears']:
    systs = getattr( opt, stype )
    for s in systs.split(","):
      if s == '': continue
      # Open systematic parquet file and extract mean, sigma and rate

      # Up variation
      input_dir_syst_up = re.sub("nominal", "%s/up"%s, opt.inputDir)
      input_file_syst_up = "%s/events__%s.parquet"%(input_dir_syst_up,proc)
      syst_up_df = pd.read_parquet(input_file_syst_up)
      mask_syst_up = syst_up_df['category'] == opt.cat
      n_syst_up = len(syst_up_df[mask_syst_up])
      if n_syst_up <= 0:
        mean_syst_up = mean_nominal
        eff_sigma_syst_up = eff_sigma_nominal
        rate_syst_up = rate_nominal
      else:
        mean_syst_up, eff_sigma_syst_up, rate_syst_up = extract_info(syst_up_df[mask_syst_up], opt.xvar, 'weight', 0.683)

      # Down variation
      input_dir_syst_down = re.sub("nominal", "%s/down"%s, opt.inputDir)
      input_file_syst_down = "%s/events__%s.parquet"%(input_dir_syst_down,proc)
      syst_down_df = pd.read_parquet(input_file_syst_down)
      mask_syst_down = syst_down_df['category'] == opt.cat
      n_syst_down = len(syst_down_df[mask_syst_down])
      if n_syst_down <= 0:
        mean_syst_down = mean_nominal
        eff_sigma_syst_down = eff_sigma_nominal
        rate_syst_down = rate_nominal
      else:
        mean_syst_down, eff_sigma_syst_down, rate_syst_down = extract_info(syst_down_df[mask_syst_down], opt.xvar, 'weight', 0.683)

      # Extract variations
      mean_var = get_mean_var(mean_nominal, mean_syst_up, mean_syst_down, threshold_mean=opt.thresholdMean)
      sigma_var = get_sigma_var(eff_sigma_nominal, eff_sigma_syst_up, eff_sigma_syst_down, threshold_sigma=opt.thresholdSigma)
      rate_var = get_rate_var(rate_nominal, rate_syst_up, rate_syst_down, threshold_rate=opt.thresholdRate)
      row.append(mean_var)
      row.append(sigma_var)
      row.append(rate_var)


      print("   * Systematic: %s"%(s))
      print("     - Up: mean = %.3f, effSigma = %.3f, rate = %.5f"%(mean_syst_up,eff_sigma_syst_up,rate_syst_up))
      print("     - Down: mean = %.3f, effSigma = %.3f, rate = %.5f"%(mean_syst_down,eff_sigma_syst_down,rate_syst_down))

  # Append to dataframe
  data = pd.concat([data,pd.DataFrame([row], columns=columns_data)], ignore_index=True, sort=False)

# Save dataframe to parquet file
if not os.path.isdir("%s/outdir_%s"%(swd__,opt.ext)): os.system("mkdir %s/outdir_%s"%(swd__,opt.ext))
if not os.path.isdir("%s/outdir_%s/calcPhotonSyst"%(swd__,opt.ext)): os.system("mkdir %s/outdir_%s/calcPhotonSyst"%(swd__,opt.ext))
if not os.path.isdir("%s/outdir_%s/calcPhotonSyst/pkl"%(swd__,opt.ext)): os.system("mkdir %s/outdir_%s/calcPhotonSyst/pkl"%(swd__,opt.ext))
with open("%s/outdir_%s/calcPhotonSyst/pkl/%s.pkl"%(swd__,opt.ext,opt.cat),"wb") as f: pickle.dump(data,f) 
print(" --> Successfully saved photon systematics as pkl file: %s/outdir_%s/calcPhotonSyst/pkl/%s.pkl"%(swd__,opt.ext,opt.cat))

