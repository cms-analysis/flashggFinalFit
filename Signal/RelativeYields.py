
print " ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Pandas relative yields ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ "
import os, sys
import re
from optparse import OptionParser
import ROOT
import pandas as pd
import glob
import pickle

def get_options():
  parser = OptionParser()
  parser.add_option('--cat', dest='cat', default='VBFTag_7', help="category in wich we are interested in)")
  parser.add_option('--input', dest='inDir', default='outdir_2022-06-17_year2016/calcPhotonSyst/pkl/', help='Directiory input') 
  parser.add_option('--syst', dest='Syst', default='', help='Systematics to see') 
  return parser.parse_args()
(opt,args) = get_options()


pkl_files = glob.glob("./%s/*.pkl"%opt.inDir)
print pkl_files, "./%s/*.pkl"
for p in pkl_files:
	with open(p) as f:  data_new = pickle.load(f)
	print data_new.columns
	print data_new.T
