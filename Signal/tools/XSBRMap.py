# Python script to hold XS * BR for normalisation of signal models
from collections import OrderedDict as od
from commonObjects import *
  
# Add analyses to globalReplacementMap. See "STXS" as an example
globalXSBRMap = od()


# For case of fixed xs/br Use 'mode':constant 'factor':X e.g.
# globalXSBRMap['example'] = od()
# globalXSBRMap['example']['decay'] = {'mode':'constant','factor':1}
# globalXSBRMap['example']['PROCNAME'] = {'mode':'constant','factor':0.001}

# For case of inclusive production mode then drop factor e.g.
# globalXSBRMap['example']['GG2H'] = {'mode':'ggH'}

# STXS analysis
globalXSBRMap['STXS'] = od()
globalXSBRMap['STXS']['decay'] = {'mode':'hgg'}
globalXSBRMap['STXS']['GG2H_0J_PTH_GT10'] = {'mode':'ggH','factor':0.3940}




