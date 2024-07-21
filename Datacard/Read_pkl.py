import pandas as pd
import pickle
import glob
import numpy as np
from optparse import OptionParser
from collections import OrderedDict as od
import os, sys


def add_spaces(string):
    while len(string) < 14:
        string += ' '
    return string




def get_options():
  parser = OptionParser()
  # Input details
  parser.add_option('--cat', dest='cat', default='RECO_WH_LEP_Tag1', help="Category ")
  parser.add_option('--dir', dest='dir', default='yields_2024-02-14_ALT_0M', help="Directory from wich read pkl")
  parser.add_option('--doFile', dest='doFile', default='Yes', help="Do you want to have the output file? Yes or No")
  return parser.parse_args()
(opt,args) = get_options()

cat = opt.cat

if opt.cat == 'all' : pkl_files = glob.glob(opt.dir+'/*.pkl') 
else : pkl_files = glob.glob(opt.dir+'/'+cat+'.pkl') 


pkl_files = sorted(pkl_files)

result = []

for pkl_file in pkl_files:
    result_dict = {}

    file_name= os.path.basename(pkl_file)
    data = []

   
    with open(pkl_file) as f:  
        data.append(pickle.load(f))

    
    dataFrame = pd.DataFrame()

    lumiMap = {'2016':36.33, '2016preVFP': 19.52, '2016postVFP': 16.81, '2017':41.48, '2018':59.35, 'combined':138, 'merged':138}

    for d in data:
        df = pd.DataFrame()
        
        df=df.append(d["year"] )
        df=df.append(d["cat"])
        df=df.append(d["procOriginal"])
        df=df.append(d["proc"])
        df=df.append(d["proc_s0"])
        df=df.append(d["nominal_yield"] )
        dataFrame = pd.concat([dataFrame, df.T], ignore_index=True)

    dataFrame["lumi"] = dataFrame["year"].map(lumiMap)

    dataFrame["nominal_yield"] = pd.to_numeric(dataFrame["nominal_yield"], errors='coerce')
    dataFrame["nominal_yield_lumi"] = dataFrame["lumi"] * dataFrame["nominal_yield"].astype(float)

    dataFrame = dataFrame.drop_duplicates()

    if opt.doFile == 'Yes':
        file_path = 'YIELD_'+cat+'.txt'  
        with open(file_path, 'w') as file:
            #file.write((d.T).to_string())    
            file.write(dataFrame.to_string())



    S = dataFrame[dataFrame["procOriginal"]=="wh_ALT_0M"]["nominal_yield_lumi"].sum()
    BKG =  dataFrame[~dataFrame['procOriginal'].str.contains('ALT')]["nominal_yield_lumi"].sum()
    result_dict['CAT'] = file_name
    result_dict['S'] =  dataFrame[dataFrame["procOriginal"]=="wh_ALT_0M"]["nominal_yield_lumi"].sum()
    result_dict['BKG']  = dataFrame[~dataFrame['procOriginal'].str.contains('ALT')]["nominal_yield_lumi"].sum()
    result_dict['SoBKG'] = dataFrame[dataFrame["procOriginal"]=="wh_ALT_0M"]["nominal_yield_lumi"].sum()/ dataFrame[~dataFrame['procOriginal'].str.contains('ALT')]["nominal_yield_lumi"].sum()
    print(result_dict)
    result.append(result_dict)
   

max_element = max(result, key=lambda x: x['SoBKG'])
for r in result: print(r)
print "VALORE MASSIMO = "+ str(max_element)


    #print dataFrame[~dataFrame['procOriginal'].str.contains('ALT')]["nominal_yield_lumi"].sum()
    # Write DataFrame to a text file

    


