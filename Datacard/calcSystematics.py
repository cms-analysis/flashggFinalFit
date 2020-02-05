# Hold defs of functions for calculating systematics and adding to dataframe
import os, sys, re
import ROOT

# sd = "systematics dataframe"

# For constant systematics: FIXME add functionality to choose only some procs
def addConstantSyst(sd,_syst,options):

  # Add column to dataFrame with default value
  if _syst['merge']: 
    sd[_syst['name']] = '-'
    # If signal and not NOTAG then set value
    sd.loc[(sd['type']=='sig')&(~sd['cat'].str.contains("NOTAG")), _syst['name']] = _syst['value']

  # If not merged across years then create separate columns for each year and fill separately
  else:
    for year in options.years.split(","):
      sd["%s_%s"%(_syst['name'],year)] = '-'
      sd.loc[(sd['type']=='sig')&(sd['year']==year)&(~sd['cat'].str.contains("NOTAG")), "%s_%s"%(_syst['name'],year)] = _syst['value'][year]
  return sd

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Function to return type of systematic: to be used by factory functions
# a) Anti-symmetric weight in nominal RooDataSet: "a_w"
# b) Symmetric weight in nominal RooDataSet: "s_w"
# c) Anti-symmetric shifts in RooDataHist: "a_h"
def factoryType(d,s):
  # Extract first signal entry of dataFrame
  r0 = d[d['type']=='sig'].iloc[0]
  # Extract workspace
  f = ROOT.TFile(r0.inputWSFile)
  ws = f.Get("tagsDumper/cms_hgg_13TeV")
  f.Close()
  # Check if syst is var (weight) in workspace
  if ws.allVars().selectByName("%s*"%(s['name'])).getSize():
    nWeights = ws.allVars().selectByName("%s*"%(s['name'])).getSize()
    if nWeights == 2: return "a_w"
    elif nWeights == 1: return "s_w"
    else:
      print " --> [ERROR] systematic %s: > 2 weights in workspace. Leaving..."%s['name']
      sys.exit(1)
  
  # Else: check if RooDataHist exist
  dataHistUp = "%s_%sUp01sigma"%(r0.nominalDataName,s['name'])
  dataHistDown = "%s_%sDown01sigma"%(r0.nominalDataName,s['name'])
  if(ws.data(dataHistUp)!=None)&(ws.data(dataHistDown)!=None): return "a_h"
  
  print " --> [ERROR] systematic %s: cannot extract type in factoryType function. Doesn't match requirement for (anti)-symmetric weights or anti-symmetric histograms. Leaving..."
  sys.exit(1)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Function to extract yield variations for signal row in dataFrame
def calcSystYields(_nominalDataName,_inputWS,_systFactoryTypes):

  # Define dictionary to store systematic yield counters
  systYields = {}
  # Loop over systematics and create counter in dict
  for s, f in _systFactoryTypes.iteritems():
    if f in ["a_h","a_w"]:
      for direction in ['up','down']: systYields["%s_%s"%(s,direction)] = 0
    else: systYields[s] = 0

  # For systematics stored as weights (a_w,s_w)...
  # Extract nominal dataset
  rdata_nominal = _inputWS.data(_nominalDataName)
  # Loop over events and extract reweighted yields
  for i in range(0,rdata_nominal.numEntries()):
    p = rdata_nominal.get(i)
    w = rdata_nominal.weight()
    # Loop over systematics:
    for s, f in _systFactoryTypes.iteritems():
      if f == "a_h": continue

      # If asymmetric weights:
      elif f == "a_w":
        centralWeightStr = "scaleWeight_0" if "scaleWeight" in s else "centralObjectWeight"
        f_central = p.getRealValue(centralWeightStr)
        f_up, f_down = p.getRealValue("%sUp01sigma"%s), p.getRealValue("%sDown01sigma"%s)
        # Checks:
        # 1) if central weights are zero then skip event
        if f_central == 0: continue
        # 2) if up weight is equal to down weight then set to nominal
        elif f_up == f_down: w_up, w_down = w, w
        else:
          w_up, w_down = w*(f_up/f_central), w*(f_down/f_central)
        # Add weights to counters
        systYields["%s_up"%s] += w_up        
        systYields["%s_down"%s] += w_down

      # If symmetric weights
      else:
        centralWeightStr = "scaleWeight_0" if "scaleWeight" in s else "centralObjectWeight"
        f_central = p.getRealValue(centralWeightStr)
        f = p.getRealValue(s)
        # Check: if central weight is zero then skip event
        if f_central == 0: continue
        else:
          # Add weights to counter
          systYields[s] += w*(f/f_central)

  # For systematics stored as RooDataHist
  for s, f in _systFactoryTypes.iteritems():
    if f == "a_h":
      systYields["%s_up"%s] = _inputWS.data("%s_%sUp01sigma"%(_nominalDataName,s)).sumEntries()
      systYields["%s_down"%s] = _inputWS.data("%s_%sDown01sigma"%(_nominalDataName,s)).sumEntries()

  # Add variations to dataFrame
  return systYields
  

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXPERIMENTAL SYSTEMATICS FACTORY:
# d - dataFrame, systs - dict of systematics, ftype - dict of factoryTypes
def experimentalSystFactory(d,systs,ftype,options):

  # Loop over systematics and add new column in dataFrame
  for s in systs:
    if s['type'] == 'constant': continue
    if s['merge']: d[s['name']] = '-'
    else:
      for year in options.years.split(","): d['%s_%s'%(s['name'],year)] = '-'

  # Loop over systematics and fill entries for rows which satisfy mask
  for s in systs:
    if s['type'] == 'constant': continue
    # Extract factory type
    f = ftype[s['name']]
    if s['merge']:
      mask = (d['type']=='sig')&(~d['cat'].str.contains("NOTAG"))
      d.loc[mask,s['name']] = d[mask].apply(lambda x: compareYield(x,f,s['name']), axis=1)
    else:
      for year in options.years.split(","):
        mask = (d['type']=='sig')&(~d['cat'].str.contains("NOTAG"))&(d['year']==year)
        d.loc[mask,'%s_%s'%(s['name'],year)] = d[mask].apply(lambda x: compareYield(x,f,s['name']), axis=1)

    # Remove yield columns from dataFrame
    if f in ['a_h','a_w']: 
      for direction in ['up','down']: d.drop(['%s_%s_yield'%(s['name'],direction)], axis=1, inplace=True)
    else: d.drop(['%s_yield'%s['name']], axis=1, inplace=True)

  return d

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# THEORY SYSTEMATICS FACTORY:
def theorySystFactory(d,systs,ftype,options):
   
  # Calculate the per-production mode (per-year) yield variation: add as column in dataFrame
  for proc_s0 in d[d['type']=='sig'].proc_s0.unique():
    for year in options.years.split(","):
      key = "%s_%s"%(proc_s0,year)
      mask = (d['proc_s0']==proc_s0)&(d['year']==year)
      d.loc[mask,'proc_s0_nominal_yield'] = d[mask]['nominal_yield'].sum()
      for s in systs:
	if s['type'] == 'constant': continue
	f = ftype[s['name']]
	if f in ['a_w','a_h']: 
	  for direction in ['up','down']: 
            d.loc[mask,'proc_s0_%s_%s_yield'%(s['name'],direction)] = d[mask]['%s_%s_yield'%(s['name'],direction)].sum()
	else: 
          d.loc[mask,'proc_s0_%s_yield'%s['name']] = d[mask]['%s_yield'%s['name']].sum()
  # Calculate the per-STXS bin (per-year already in proc name) yield variations: add as column in dataFrame
  for proc in d[d['type']=='sig'].proc.unique():
    key = proc
    mask = (d['proc']==proc)
    d.loc[mask,'proc_nominal_yield'] = d[mask]['nominal_yield'].sum() 
    for s in systs:
      if s['type'] == 'constant': continue
      f = ftype[s['name']]
      if f in ['a_w','a_h']: 
        for direction in ['up','down']: 
          d.loc[mask,'proc_%s_%s_yield'%(s['name'],direction)] = d[mask]['%s_%s_yield'%(s['name'],direction)].sum()
      else: 
	d.loc[mask,'proc_%s_yield'%s['name']] = d[mask]['%s_yield'%s['name']].sum()

  # Loop over systematics and add new column in dataFrame for each tier
  for s in systs:
    if s['type'] == 'constant': continue
    for tier in s['tiers']: d["%s_%s"%(s['name'],tier)] = '-'

  # Loop over systematics and fill entries for rows which satisfy mask
  for s in systs:
    if s['type'] == 'constant': continue
    # Extract factory type
    f = ftype[s['name']]
    mask = (d['type']=='sig')
    # Loop over tiers and use appropriate mode for compareYield function
    for tier in s['tiers']: 
      d.loc[mask,"%s_%s"%(s['name'],tier)] = d[mask].apply(lambda x: compareYield(x,f,s['name'],mode=tier), axis=1)

    # Remove yield columns from dataFrame
    if f in ['a_h','a_w']: 
      for direction in ['up','down']: 
        for id_ in ['','proc_','proc_s0_']:
          d.drop(['%s%s_%s_yield'%(id_,s['name'],direction)], axis=1, inplace=True)
    else: 
      for id_ in ['','proc_','proc_s0_']: 
        d.drop(['%s%s_yield'%(id_,s['name'])], axis=1, inplace=True)

  # Remove nominal proc and proc_s0 yield columns
  for id_ in ['proc_','proc_s0_']: d.drop(['%snominal_yield'%id_], axis=1, inplace=True)

  return d
  
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Function for comparing yields:
#   * mode == treatment of theory systematic  
def compareYield(row,factoryType,sname,mode='default'):

  # if nominal yield is zero: return 1
  if row['nominal_yield']==0:
    if factoryType in ["a_w","a_h"]: return [1.,1.]
    else: return [1.]

  if( mode == 'default' )|( mode == 'ishape' ):
    if factoryType in ["a_w","a_h"]: return [(row["%s_down_yield"%sname]/row['nominal_yield']),(row["%s_up_yield"%sname]/row['nominal_yield'])]
    else: return [row["%s_yield"%sname]/row['nominal_yield']]

  elif mode=='shape':
    if factoryType in ["a_w","a_h"]: 
      shape_up = (row["%s_up_yield"%sname]/row['nominal_yield'])/(row["proc_%s_up_yield"%sname]/row["proc_nominal_yield"])
      shape_down = (row["%s_down_yield"%sname]/row['nominal_yield'])/(row["proc_%s_down_yield"%sname]/row["proc_nominal_yield"])
      return [shape_down,shape_up]
    else:
      shape = (row["%s_yield"%sname]/row['nominal_yield'])/(row["proc_%s_yield"%sname]/row["proc_nominal_yield"])
      return [shape]

  elif mode == 'norm':
    if factoryType in ["a_w","a_h"]:
      norm_up = (row["proc_%s_up_yield"%sname]/row["proc_nominal_yield"])/(row["proc_s0_%s_up_yield"%sname]/row["proc_s0_nominal_yield"])
      norm_down = (row["proc_%s_down_yield"%sname]/row["proc_nominal_yield"])/(row["proc_s0_%s_down_yield"%sname]/row["proc_s0_nominal_yield"])
      return [norm_down,norm_up]
    else:
      norm = (row["proc_%s_yield"%sname]/row["proc_nominal_yield"])/(row["proc_s0_%s_yield"%sname]/row["proc_s0_nominal_yield"])
      return [norm]
 
  elif mode == 'inorm':
    if factoryType in ["a_w","a_h"]:
      inorm_up = (row["proc_%s_up_yield"%sname]/row["proc_nominal_yield"])
      inorm_down = (row["proc_%s_down_yield"%sname]/row["proc_nominal_yield"])
      return [inorm_down,inorm_up]
    else:
      inorm = (row["proc_%s_yield"%sname]/row["proc_nominal_yield"])
      return [inorm]  

  elif mode == 'inc':
    if factoryType in ["a_w","a_h"]:
      inc_up = (row["proc_s0_%s_up_yield"%sname]/row["proc_s0_nominal_yield"])
      inc_down = (row["proc_s0_%s_down_yield"%sname]/row["proc_s0_nominal_yield"])
      return [inc_down,inc_up]
    else:
      inc = (row["proc_s0_%s_yield"%sname]/row["proc_s0_nominal_yield"])
      return [inc]  

  else: 
    print " --> [ERROR] theory systematic tier %s is not supported. Leaving"%mode
    sys.exit(1) 

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Function to group systematics: e.g. for scaleWeight where up/down = [1,2],[3,6] etc
def groupSystematics(d,systs,prefix="scaleWeight",suffix="shape",groupings=[]):
  
  # Define mask: i.e. only signal rows
  mask = (d['type']=='sig')

  # Loop over groupings
  for group_idx in range(len(groupings)): 
    # Extract names of weights to be grouped
    gr = groupings[group_idx]
    w0_name = '%s_%g_%s'%(prefix,gr[0],suffix)
    w1_name = '%s_%g_%s'%(prefix,gr[1],suffix)

    # Add new column to dataframe
    grname = '%s_gr%g_%s'%(prefix,group_idx,suffix)
    d[grname] = '-'

    # For rows which satisfy mask: set grouped value
    d.loc[mask,grname] = d[mask].apply(lambda x: [x[w1_name][0],x[w0_name][0]], axis=1)

    # Drop original columns from dataFrame 
    for i in gr: d.drop( ['%s_%g_%s'%(prefix,i,suffix)], axis=1, inplace=True )

    # Replace individual systs in dict with grouped syst
    for s in systs:
      # Change w0_name and remove w1_name
      if s['name'] == "%s_%g"%(prefix,gr[0]):
        s['name'] = re.sub("%s_%g"%(prefix,gr[0]),"%s_gr%g"%(prefix,group_idx),s['name'])
        s['title'] = re.sub("%s_%g"%(prefix,gr[0]),"%s_gr%g"%(prefix,group_idx),s['title'])
      elif s['name'] == "%s_%g"%(prefix,gr[1]): systs.remove(s)

  return d,systs
      
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
