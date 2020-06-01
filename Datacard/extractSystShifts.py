# Script to calc syst shifts
import os, sys
import glob
import re
from optparse import OptionParser
import ROOT
import pandas
import uproot
import pickle

def get_options():
  parser = OptionParser()
  parser.add_option('--inputPkl',dest='inputPkl', default="", help="Input file")
  return parser.parse_args()
(opt,args) = get_options()

from systematics import theory_systematics, experimental_systematics

# Function to calc true yield for syst var
def calcSystYield(r,s,direction='up'):
  if s['correlateAcrossYears'] == 0: sn = "%s_%s"%(s['name'],r['year'])
  else: sn = s['name']
  if r[sn] == '-': return r['true_yield']
  if len(r[sn]) == 2: 
    if direction == 'up': 
      if(abs(float(r[sn][1])) < 0.5)|(abs(float(r[sn][1])) > 2.0): return r['true_yield']
      else: return r['true_yield']*float(r[sn][1])
    elif direction == 'down':
      if(abs(float(r[sn][0])) < 0.5)|(abs(float(r[sn][0])) > 2.0): return r['true_yield']
      else: return r['true_yield']*float(r[sn][0])   
    else:
      print " --> [ERROR] Direction %s not recognised. Leaving"%direction
      sys.exit(1)
  elif len(r[sn]) == 1: 
    if(abs(float(r[sn][0])) < 0.5)|(abs(float(r[sn][0])) > 2.0): return r['true_yield'] 
    else: return r['true_yield']*float(r[sn][0])
  else:
    print " --> [ERROR] Do not recognise syst type: %s --> %s"%(s,r[sn])
    sys.exit(1)
     
# Open pickle
with open( opt.inputPkl, "rb" ) as f: data = pickle.load(f)

# Loop over experimental systematics
ecols = ['cat']
for es in experimental_systematics:
  if es['type'] != 'factory': continue
  ecols.append( es['name'] )
edf = pandas.DataFrame(columns=ecols)
for cat in data[~data['cat'].str.contains("NOTAG")]['cat'].unique():
  print " --> Processing category: %s"%cat
  vals = [cat]
  mask = (data['cat']==cat)&(data['type']=='sig')
  true_yield = data[mask].true_yield.sum()
  for es in experimental_systematics:
    if es['type'] != 'factory': continue
    up_var = abs(1-(data[mask].apply(lambda x: calcSystYield(x,es,direction='up'), axis=1).sum()/true_yield))
    down_var = abs(1-(data[mask].apply(lambda x: calcSystYield(x,es,direction='down'), axis=1).sum()/true_yield))
    vals.append(100*max(up_var,down_var))
  edf.loc[len(edf)] = vals

for ecol in ecols[1:]: print "%s: %s = %.1f%%"%(ecol,edf.iloc[edf[ecol].idxmax()]['cat'],edf[ecol].max())
    
# Sort cats for each systematic
    
    
