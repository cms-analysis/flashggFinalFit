# Python plot to correct impacts with shifted best-fit value
import os, sys
import re
from optparse import OptionParser
import json
from collections import OrderedDict as od

def get_options():
  parser = OptionParser()
  parser.add_option('--impactsJson', dest='impactsJson', default='impacts.json', help="Input json file")
  parser.add_option('--frozenParam', dest='frozenParam', default='STXS_constrain_THU_qqH_JET01', help="Frozen parameter from which to extract true values of pois")
  parser.add_option('--dropBkgModelParams', dest='dropBkgModelParams', default=False, action="store_true", help="Drop parameters related to bkg model (statistical uncertainties)")
  return parser.parse_args()
(opt,args) = get_options()

# Open impacts json
with open( opt.impactsJson, "r" ) as fj: data = json.load(fj)


# Extract list of pois
pois = []
for poi in data['POIs']: pois.append( poi['name'] )

# Extract midpoint values of pois from frozen parameter
poisCorrected = od()
for param in data['params']:
  p = param['name']
  if p == opt.frozenParam:
    for poi in pois:
      poivals = param[poi]
      poisCorrected[poi] = 0.5*( poivals[0]+poivals[2] ) # Midpoint of up and down variation

# Correct values in json
POICorrected = []
for poi in data['POIs']:
  pInfo = {}
  pInfo['name'] = poi['name']
  pInfo['fit'] = []
  # Extract fit list
  _fit = poi['fit']
  for iv, v in enumerate(_fit):
    if iv in [0,2]: pInfo['fit'].append(v)
    else: pInfo['fit'].append( poisCorrected[poi['name']] )
  # Push correct POI back
  POICorrected.append(pInfo)
    
MethodCorrected = data['method']

ParamsCorrected = []
for param in data['params']:
  if(opt.dropBkgModelParams)&( ("shapeBkg" in param['name'])|("env_pdf" in param['name']) ): continue
  pInfo = {}
  pInfo['fit'] = param['fit']
  pInfo['prefit'] = param['prefit']
  pInfo['groups'] = param['groups']
  pInfo['name'] = param['name']
  pInfo['type'] = param['type']
  # Correct central values
  for poi in pois:
    _poi = param[poi]
    pInfo[poi] = []
    for iv, v in enumerate(_poi):
      if iv in [0,2]: pInfo[poi].append(v)
      else: 
        # If bkg model parameter: expect these to be one sided
        if( "shapeBkg" in param['name'] )|( "env_pdf" in param['name'] ): 
          pInfo[poi].append( poisCorrected[poi] )
        else:
          # Check if in midpoint: if not then re-define as midpoint
          if ( (poisCorrected[poi]-_poi[0])*(poisCorrected[poi]-_poi[2]) <= 0 ):
            pInfo[poi].append( poisCorrected[poi] )
          else:
            pInfo[poi].append( 0.5*(_poi[0]+_poi[2]) )
      
  # Correct impact values
  for poi in pois:
    pInfo["impacts_%s"%poi] = max( abs(pInfo[poi][0]-pInfo[poi][1]), abs(pInfo[poi][2]-pInfo[poi][1]) )
  # Push correct param back
  ParamsCorrected.append(pInfo)
# Corrected Impacts json
ImpactsCorrected = {}
ImpactsCorrected['POIs'] = POICorrected
ImpactsCorrected['method'] = MethodCorrected
ImpactsCorrected['ParamsCorrected'] = ParamsCorrected

# Print out corrected json file: in same format
extStr = "_dropBkgModelParams" if opt.dropBkgModelParams else ""
outImpacts = re.sub(".json","_corrected%s.json"%extStr,opt.impactsJson)
with open(outImpacts,"w") as jf:
  jf.write("{\n")
  # POIS
  jf.write("  \"POIs\": [\n")
  for ip, poi in enumerate(pois):
    jf.write("    {\n")
    jf.write("      \"fit\": [\n")
    for iv, v in enumerate( POICorrected[ip]['fit'] ):
      if iv == (len(POICorrected[ip]['fit'])-1): jf.write("        %.16f\n"%v)
      else: jf.write("        %.16f,\n"%v)
    jf.write("      ],\n")
    jf.write("      \"name\": \"%s\"\n"%poi)
    if ip == (len(pois)-1): jf.write("    }\n")
    else: jf.write("    },\n")
  jf.write("  ],\n")

  # METHOD
  jf.write("  \"method\": \"%s\",\n"%MethodCorrected)

  # PARAMS
  jf.write("  \"params\": [\n")
  for iparam, param in enumerate(ParamsCorrected):
    jf.write("    {\n")
    jf.write("      \"fit\": [\n")
    for iv, v in enumerate( param['fit'] ):
      if iv == (len(param['fit'])-1): jf.write("        %.16f\n"%v)
      else: jf.write("        %.16f,\n"%v)
    jf.write("      ],\n")
    jf.write("      \"groups\": %s,\n"%param['groups'])
    for poi in pois: jf.write("      \"impact_%s\": %.16f,\n"%(poi,param['impacts_%s'%poi]))
    jf.write("      \"name\": \"%s\",\n"%param['name'])
    jf.write("      \"prefit\": [\n")
    for iv, v in enumerate( param['prefit'] ):
      if iv == (len(param['prefit'])-1): jf.write("        %.16f\n"%v)
      else: jf.write("        %.16f,\n"%v)
    jf.write("      ],\n")
    for poi in pois:
      jf.write("      \"%s\": [\n"%poi)
      for iv,v in enumerate( param[poi] ):
        if iv == (len(param[poi])-1): jf.write("        %.16f\n"%v)
        else: jf.write("        %.16f,\n"%v)
      jf.write("      ],\n")
    jf.write("      \"type\": \"%s\"\n"%param['type'])
    if iparam == (len(ParamsCorrected)-1): jf.write("    }\n")
    else: jf.write("    },\n")
  jf.write("  ]\n")
  jf.write("}")
