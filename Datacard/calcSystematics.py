# Hold defs of functions for calculating systematics and adding to dataframe
import os, sys, re, json
import ROOT

# sd = "systematics dataframe"

# For constant systematics: FIXME add functionality to choose only some procs
def addConstantSyst(sd,_syst,options):

  # Read json file into dict and set flag
  fromJson = False
  if "json" in _syst['value']:
    fromJson = True
    with open( _syst['value'], "r" ) as jsonfile: uval = json.load(jsonfile)

  # Add column to dataFrame with default value
  if _syst['correlateAcrossYears'] == 1: 
    sd[_syst['name']] = '-'
    if fromJson:
      sd.loc[(sd['type']=='sig'),_syst['name']] = sd[(sd['type']=='sig')].apply(lambda x: getValueFromJson(x,uval,_syst['name']), axis=1)
    else:
      # If signal and not NOTAG then set value
      sd.loc[(sd['type']=='sig')&(~sd['cat'].str.contains("NOTAG")), _syst['name']] = _syst['value']

  # Partial correlation
  elif _syst['correlateAcrossYears'] == -1:
    sd[_syst['name']] = '-'
    # Loop over years and set value for each year
    for year in options.years.split(","):
      mask = (sd['type']=='sig')&(~sd['cat'].str.contains("NOTAG"))&(sd['year']==year)
      sd.loc[mask,_syst['name']] = _syst['value'][year]

  # If not correlate across years then create separate columns for each year and fill separately
  else:
    for year in options.years.split(","):
      sd["%s_%s"%(_syst['name'],year)] = '-'
      sd.loc[(sd['type']=='sig')&(sd['year']==year)&(~sd['cat'].str.contains("NOTAG")), "%s_%s"%(_syst['name'],year)] = _syst['value'][year]

  return sd

def getValueFromJson(row,uncertainties,sname):
  # uncertainties is a dict of the form proc:{sname:X}
  p = re.sub("_2016_hgg","",row['proc'])
  p = re.sub("_2017_hgg","",p)
  p = re.sub("_2018_hgg","",p)
  if p in uncertainties: 
    if type(uncertainties[p][sname])==list: return uncertainties[p][sname]
    else: return [uncertainties[p][sname]]
  else: return '-'

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Function to return type of systematic: to be used by factory functions
# a) Anti-symmetric weight in nominal RooDataSet: "a_w"
# b) Symmetric weight in nominal RooDataSet: "s_w"
# c) Anti-symmetric shifts in RooDataHist: "a_h"
def factoryType(d,s):

  #Fix for pdfWeight (as > 10)
  if('pdfWeight' in s['name'])|('alphaSWeight' in s['name']): return "s_w"

  # Extract first signal entry of dataFrame
  r0 = d[d['type']=='sig'].iloc[0]
  # Extract workspace
  f = ROOT.TFile(r0.inputWSFile)
  ws = f.Get("tagsDumper/cms_hgg_13TeV")
  f.Close()
  # Check if syst is var (weight) in workspace
  if ws.allVars().selectByName("%s*"%(s['name'])).getSize():
    nWeights = ws.allVars().selectByName("%s*"%(s['name'])).getSize()
    ws.Delete()
    if nWeights == 2: return "a_w"
    elif nWeights == 1: return "s_w"
    else:
      print " --> [ERROR] systematic %s: > 2 weights in workspace. Leaving..."%s['name']
      sys.exit(1)
  
  # Else: check if RooDataHist exist
  dataHistUp = "%s_%sUp01sigma"%(r0.nominalDataName,s['name'])
  dataHistDown = "%s_%sDown01sigma"%(r0.nominalDataName,s['name'])
  if(ws.data(dataHistUp)!=None)&(ws.data(dataHistDown)!=None): 
    ws.Delete()
    return "a_h"

  
  print " --> [ERROR] systematic %s: cannot extract type in factoryType function. Doesn't match requirement for (anti)-symmetric weights or anti-symmetric histograms. Leaving..."
  sys.exit(1)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Function to extract yield variations for signal row in dataFrame
def calcSystYields(_nominalDataName,_inputWS,_systFactoryTypes,skipCOWCorr=True):

  # Define dictionary to store systematic yield counters
  systYields = {}
  # Loop over systematics and create counter in dict
  for s, f in _systFactoryTypes.iteritems():
    if f in ["a_h","a_w"]:
      for direction in ['up','down']: 
        systYields["%s_%s"%(s,direction)] = 0
        if not skipCOWCorr: systYields["%s_%s_COWCorr"%(s,direction)] = 0
    else: 
      systYields[s] = 0
      if not skipCOWCorr: systYields["%s_COWCorr"%s] = 0

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
        centralWeightStr = "centralObjectWeight"
        f_central = p.getRealValue(centralWeightStr)
        f_up, f_down = p.getRealValue("%sUp01sigma"%s), p.getRealValue("%sDown01sigma"%s)
        # Checks:
        # 1) if central weights are zero then skip event
        if f_central == 0: continue
        # 2) if up weight is equal to down weight (=1) then set to nominal
        elif f_up == f_down: w_up, w_down = w, w
        else:
          w_up, w_down = w*(f_up/f_central), w*(f_down/f_central)
        # Add weights to counters
        systYields["%s_up"%s] += w_up        
        systYields["%s_down"%s] += w_down
        if not skipCOWCorr:
          f_COWCorr, f_NNLOPS = p.getRealValue("centralObjectWeight"), abs(p.getRealValue("NNLOPSweight"))
          if f_COWCorr == 0: continue
          else: 
            systYields["%s_up_COWCorr"%s] += w_up*(f_NNLOPS/f_COWCorr)
            systYields["%s_down_COWCorr"%s] += w_down*(f_NNLOPS/f_COWCorr)

      # If symmetric weights
      else:
        if "scaleWeight" in s: centralWeightStr = "scaleWeight_0"
        elif "alphaSWeight" in s: centralWeightStr = "scaleWeight_0" 
        elif "pdfWeight" in s: centralWeightStr = "pdfWeight_0"
        else: centralWeightStr = "centralObjectWeight"

        # No theory weights for tH, bbH
        # FIXME: all for ttH in this iteration (being fixed)
        if("tth" in _nominalDataName)|("thq" in _nominalDataName)|("thw" in _nominalDataName)|("bbh" in _nominalDataName): 
          systYields[s] += w
          if not skipCOWCorr: 
            f_COWCorr, f_NNLOPS = p.getRealValue("centralObjectWeight"), abs(p.getRealValue("NNLOPSweight"))
            if f_COWCorr == 0: continue
            else: systYields["%s_COWCorr"%s] += w*(f_NNLOPS/f_COWCorr)
        else:
	  f_central = p.getRealValue(centralWeightStr)
	  f = p.getRealValue(s)
	  # Check: if central weight is zero then skip event
	  if f_central == 0: continue
	  else:
	    # Add weights to counter
	    systYields[s] += w*(f/f_central)
	    if not skipCOWCorr:
              f_COWCorr, f_NNLOPS = p.getRealValue("centralObjectWeight"), abs(p.getRealValue("NNLOPSweight"))
              if f_COWCorr == 0: continue
              else: systYields["%s_COWCorr"%s] += w*(f_NNLOPS/f_COWCorr)*(f/f_central)

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
def experimentalSystFactory(d,systs,ftype,options,_removal=False):

  # Loop over systematics and add new column in dataFrame
  for s in systs:
    if s['type'] == 'constant': continue
    if s['correlateAcrossYears']: d[s['name']] = '-'
    else:
      for year in options.years.split(","): d['%s_%s'%(s['name'],year)] = '-'

  # Loop over systematics and fill entries for rows which satisfy mask
  for s in systs:
    if s['type'] == 'constant': continue
    # Extract factory type
    f = ftype[s['name']]
    if s['correlateAcrossYears']:
      mask = (d['type']=='sig')&(~d['cat'].str.contains("NOTAG"))
      d.loc[mask,s['name']] = d[mask].apply(lambda x: compareYield(x,f,s['name']), axis=1)
    else:
      for year in options.years.split(","):
        mask = (d['type']=='sig')&(~d['cat'].str.contains("NOTAG"))&(d['year']==year)
        d.loc[mask,'%s_%s'%(s['name'],year)] = d[mask].apply(lambda x: compareYield(x,f,s['name']), axis=1)

    # Remove yield columns from dataFrame
    if _removal:
      if f in ['a_h','a_w']: 
	for direction in ['up','down']: d.drop(['%s_%s_yield'%(s['name'],direction)], axis=1, inplace=True)
      else: d.drop(['%s_yield'%s['name']], axis=1, inplace=True)

  return d

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# THEORY SYSTEMATICS FACTORY:
def theorySystFactory(d,systs,ftype,options,stxsMergeScheme=None,_removal=False):

  # For process yields: sum central object weight corrected (remove experimental effects)
  corrExt = "_COWCorr" if not options.skipCOWCorr else ''
   
  # Calculate the per-production mode (per-year) yield variation: add as column in dataFrame
  for proc_s0 in d[d['type']=='sig'].proc_s0.unique():
    for year in options.years.split(","):
      mask = (d['proc_s0']==proc_s0)&(d['year']==year)
      d.loc[mask,'proc_s0_nominal_yield'] = d[mask]['nominal_yield%s'%corrExt].sum()
      for s in systs:
	if s['type'] == 'constant': continue
	f = ftype[s['name']]
	if f in ['a_w','a_h']: 
	  for direction in ['up','down']: 
            d.loc[mask,'proc_s0_%s_%s_yield'%(s['name'],direction)] = d[mask]['%s_%s_yield%s'%(s['name'],direction,corrExt)].sum()
	else: 
          d.loc[mask,'proc_s0_%s_yield'%s['name']] = d[mask]['%s_yield%s'%(s['name'],corrExt)].sum()
  # Calculate the per-STXS bin (per-year already in proc name) yield variations: add as column in dataFrame
  for proc in d[d['type']=='sig'].proc.unique():
    mask = (d['proc']==proc)
    d.loc[mask,'proc_nominal_yield'] = d[mask]['nominal_yield%s'%corrExt].sum() 
    for s in systs:
      if s['type'] == 'constant': continue
      mask = (d['proc']==proc)
      f = ftype[s['name']]
      if f in ['a_w','a_h']: 
        for direction in ['up','down']: 
          d.loc[mask,'proc_%s_%s_yield'%(s['name'],direction)] = d[mask]['%s_%s_yield%s'%(s['name'],direction,corrExt)].sum()
      else: 
	d.loc[mask,'proc_%s_yield'%s['name']] = d[mask]['%s_yield%s'%(s['name'],corrExt)].sum()

  # For merging STXS bins in parameter scheme:
  if options.doSTXSBinMerging:
    for mergeName, mergeBins in stxsMergeScheme.iteritems():
      for year in options.years.split(","):
        mBins = [] # add full name (inc year and and decay)
        for mb in mergeBins: mBins.append("%s_%s_hgg"%(mb,year)) 
	mask = (d['type']=='sig')&(d.apply(lambda x: x['proc'] in mBins, axis=1))
        d.loc[mask,'merge_%s_nominal_yield'%mergeName] = d[mask]['nominal_yield%s'%corrExt].sum()
        # Loop over systematics
        for s in systs:
          if s['type'] == 'constant': continue
          elif 'mnorm' not in s['tiers']: continue
          f = ftype[s['name']]
          if f in ['a_w','a_h']:
            for direction in ['up','down']:
              d.loc[mask,'merge_%s_%s_%s_yield'%(mergeName,s['name'],direction)] = d[mask]['%s_%s_yield%s'%(s['name'],direction,corrExt)].sum()
          else:
            d.loc[mask,'merge_%s_%s_yield'%(mergeName,s['name'])] = d[mask]['%s_yield%s'%(s['name'],corrExt)].sum()

  # Loop over systematics and add new column in dataFrame for each tier
  for s in systs:
    if s['type'] == 'constant': continue
    for tier in s['tiers']: 
      if tier == 'mnorm': 
        if options.doSTXSBinMerging:
          for mergeName in stxsMergeScheme: d["%s_%s_mnorm"%(s['name'],mergeName)] = '-'
      else: d["%s_%s"%(s['name'],tier)] = '-'

  # Loop over systematics and fill entries for rows which satisfy mask
  for s in systs:
    if s['type'] == 'constant': continue
    # Extract factory type
    f = ftype[s['name']]
    # For ggH theory uncertainties: require proc contains "ggH"
    if "THU_ggH" in s['name']: mask = (d['type']=='sig')&(d['nominal_yield']!=0)&(d['proc'].str.contains('ggH'))
    else: mask = (d['type']=='sig')&(d['nominal_yield']!=0)
    # Loop over tiers and use appropriate mode for compareYield function: skip mnorm as treated separately below
    for tier in s['tiers']: 
      if tier == 'mnorm': continue
      d.loc[mask,"%s_%s"%(s['name'],tier)] = d[mask].apply(lambda x: compareYield(x,f,s['name'],mode=tier), axis=1)

  # For merging STXS bins in parameter scheme: calculate mnorm systematics (merged-STXS-normalisation)
  # One nuisance per merge
  if options.doSTXSBinMerging:
    for mergeName in stxsMergeScheme:
      for s in systs:
	if s['type'] == 'constant': continue
        elif 'mnorm' not in s['tiers']: continue
	for year in options.years.split(","):
	  # Remove NaN entries and require specific year
	  mask = (d['merge_%s_nominal_yield'%mergeName]==d['merge_%s_nominal_yield'%mergeName])&(d['year']==year)&(d['nominal_yield']!=0)
	  d.loc[mask,"%s_%s_mnorm"%(s['name'],mergeName)] = d[mask].apply(lambda x: compareYield(x,f,s['name'],mode='mnorm',mname=mergeName), axis=1)

  # Removal: remove yield columns from dataFrame
  if _removal:
    ids_ = ['','proc_','proc_s0_']
    if options.doSTXSBinMerging:
      for mergeName in stxsMergeScheme: ids_.append("merge_%s_"%mergeName)
    # Loop over systematics
    for s in systs:
      if s['type'] == 'constant': continue
      # Extract factory type
      f = ftype[s['name']]
      if f in ['a_h','a_w']: 
	for direction in ['up','down']: 
	  for id_ in ids_:
	    d.drop(['%s%s_%s_yield'%(id_,s['name'],direction)], axis=1, inplace=True)
      else: 
	for id_ in ids_: 
	  d.drop(['%s%s_yield'%(id_,s['name'])], axis=1, inplace=True)

    # Remove also nominal yields for all combinations
    ids_.remove('')
    for id_ in ids_: d.drop(['%snominal_yield'%id_], axis=1, inplace=True)

  return d
  
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Function for comparing yields:
#   * mode == treatment of theory systematic  
def compareYield(row,factoryType,sname,mode='default',mname=None):

  # Catch: if any yields in denominators are zero: return 1
  if row['nominal_yield']==0:
    if factoryType in ["a_w","a_h"]: return [1.,1.]
    else: return [1.]
  if mode != 'default': #only for theory uncertainties...
    if row['proc_nominal_yield']==0:
      if factoryType in ["a_w","a_h"]: return [1.,1.]
      else: return [1.]
    if factoryType in ["a_w","a_h"]:
      for direction in ['up','down']: 
	if row["proc_%s_%s_yield"%(sname,direction)] == 0: return [1.,1.]
    else:
      if row["proc_%s_yield"%sname] == 0: return [1.]

  if( mode == 'default' )|( mode == 'ishape' ):
    # FIXME: some a_h variations are not centred around nominal_yield, take symmetric
    if factoryType == "a_h":
      midpoint_yield = 0.5*(row["%s_down_yield"%sname]+row["%s_up_yield"%sname])
      if midpoint_yield == 0: return [1.,1.]
      else: return [(row["%s_down_yield"%sname]/midpoint_yield),(row["%s_up_yield"%sname]/midpoint_yield)]
    elif factoryType == "a_w": return [(row["%s_down_yield"%sname]/row['nominal_yield']),(row["%s_up_yield"%sname]/row['nominal_yield'])]
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

  elif mode == 'mnorm':
    if factoryType in ["a_w","a_h"]:
      mnorm_up = (row["proc_%s_up_yield"%sname]/row["proc_nominal_yield"])/(row["merge_%s_%s_up_yield"%(mname,sname)]/row["merge_%s_nominal_yield"%mname])
      mnorm_down = (row["proc_%s_down_yield"%sname]/row["proc_nominal_yield"])/(row["merge_%s_%s_down_yield"%(mname,sname)]/row["merge_%s_nominal_yield"%mname])
      return [mnorm_down,mnorm_up]
    else:
      mnorm = (row["proc_%s_yield"%sname]/row["proc_nominal_yield"])/(row["merge_%s_%s_yield"%(mname,sname)]/row["merge_%s_nominal_yield"%mname])
      return [mnorm]
 
  elif mode == 'inorm':
    if factoryType in ["a_w","a_h"]:
      inorm_up = (row["proc_%s_up_yield"%sname]/row["proc_nominal_yield"])
      inorm_down = (row["proc_%s_down_yield"%sname]/row["proc_nominal_yield"])
      return [inorm_down,inorm_up]
    else:
      inorm = (row["proc_%s_yield"%sname]/row[proc_yield_str])
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
def groupSystematics(d,systs,options,prefix="scaleWeight",groupings=[],stxsMergeScheme=None,_removal=True):
  
  # Loop over groupings
  for group_idx in range(len(groupings)): 
    gr = groupings[group_idx]

    # Extract systematic from systs
    for s in systs:
      if s['name'] == "%s_%g"%(prefix,gr[0]): s0 = s
      elif s['name'] == "%s_%g"%(prefix,gr[1]): s1 = s

    # Loop over systematic tiers
    for tier in s0['tiers']:
      if tier == 'mnorm':
        if options.doSTXSBinMerging:
          # Loop over merging schemes
          for mergeName in stxsMergeScheme:
            s0_name = "%s_%s_%s"%(s0['name'],mergeName,tier)
            s1_name = "%s_%s_%s"%(s1['name'],mergeName,tier)
            gr_name = "%s_gr%g_%s_%s"%(prefix,group_idx,mergeName,tier)
            d[gr_name] = '-'
            # Define mask as all entries where d[s0_name]!='-'
            mask = (d[s0_name]!='-')&(d[s1_name]!='-')
            d.loc[mask,gr_name] = d[mask].apply(lambda x: [x[s0_name][0],x[s1_name][0]],axis=1)
            # Remove original columns from dataFrame
            if _removal:
              for i in gr: d.drop( ['%s_%g_%s_%s'%(prefix,i,mergeName,tier)], axis=1, inplace=True )
        else: continue
      else:
        s0_name = "%s_%s"%(s0['name'],tier)
        s1_name = "%s_%s"%(s1['name'],tier)
        gr_name = "%s_gr%g_%s"%(prefix,group_idx,tier)
        d[gr_name] = '-'
        # Define mask as all entries where d[s0_name]!='-' and d[s1_name]!='-'
        mask = (d[s0_name]!='-')&(d[s1_name]!='-')
        d.loc[mask,gr_name] = d[mask].apply(lambda x: [x[s0_name][0],x[s1_name][0]],axis=1)
        # Remove columns from dataFrame
        if _removal:
          for i in gr: d.drop( ['%s_%g_%s'%(prefix,i,tier)], axis=1, inplace=True )

    # Replace individual systs in dict with grouped syst
    for s in systs:
      # Change w0_name and remove w1_name
      if s['name'] == "%s_%g"%(prefix,gr[0]):
        s['name'] = re.sub("%s_%g"%(prefix,gr[0]),"%s_gr%g"%(prefix,group_idx),s['name'])
        s['title'] = re.sub("%s_%g"%(prefix,gr[0]),"%s_gr%g"%(prefix,group_idx),s['title'])
      elif s['name'] == "%s_%g"%(prefix,gr[1]): systs.remove(s)

  return d,systs
      
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Function to calculate the envelope of systematics with a regexp
def envelopeSystematics(d,systs,options,regexp=None,stxsMergeScheme=None,_removal=False):

  if regexp is None:
    print " --> [WARNING] No systematics with regexp (None). Cannot form envelope"
    return d, systs

  # Extract systematics with regexp
  s_regexp = []
  for s in systs:
    if regexp in s['name']: s_regexp.append(s)
  if len(s_regexp) == 0:
    print " --> [WARNING] No systematics with regexp (%s). Cannot form envelope"%regexp
    return d, systs

  # Determine properties of envelope from first entry: remove "group" tag if in name
  env = {}
  env['name'] = "%s_env"%("_".join(s_regexp[0]['name'].split("_")[:-1]))
  env['title'] = "%s_env"%("_".join(s_regexp[0]['title'].split("_")[:-1]))
  env['tiers'] = s_regexp[0]['tiers'] 
  env['prior'] = s_regexp[0]['prior'] 
  env['correlateAcrossYears'] = s_regexp[0]['correlateAcrossYears'] 
  env['type'] = s_regexp[0]['type'] 

  # Loop over systematic tiers: all enveloped systematics must have the same tiers
  for s in s_regexp:
    if s['tiers'] != env['tiers']:
      print " --> [WARNING] Systematics in envelope have different tiers. Cannot form envelope"
  for tier in env['tiers']:
    if tier == 'mnorm':
      if options.doSTXSBinMerging:
        # Loop over merging schemes
        for mergeName in stxsMergeScheme:
          env_name = "%s_%s_%s"%(env['name'],mergeName,tier)
          d[env_name] = '-'      
          # Define mask as all entries when first entry in envelope is set
          mask = (d['%s_%s_%s'%(s_regexp[0]['name'],mergeName,tier)]!='-')
          d.loc[mask,env_name] = d[mask].apply(lambda x: compareSystForEnvelope(x,s_regexp,tier,mname=mergeName) ,axis=1)
          # Remove original columns from dataFrame
          if _removal:
            for s in s_regexp: d.drop( ["%s_%s_%s"%(s['name'],mergeName,tier)], axis=1, inplace=True ) 
      else: continue
    else:
     env_name = "%s_%s"%(env['name'],tier)
     d[env_name] = '-'      
     # Define mask as all entries when first entry in envelope is set
     mask = (d['%s_%s'%(s_regexp[0]['name'],tier)]!='-') 
     d.loc[mask,env_name] = d[mask].apply(lambda x: compareSystForEnvelope(x,s_regexp,tier) ,axis=1)
     # Remove original columns from dataFrame
     if _removal:
       for s in s_regexp: d.drop( ["%s_%s"%(s['name'],tier)], axis=1, inplace=True ) 
 
  # Add envelope to syst dictionary
  systs.append(env)
  if _removal:
    for s in s_regexp: systs.remove(s)
 
  return d, systs

# Function to compare systematic variation for envelope
def compareSystForEnvelope(row,systs,stier,mname=None):
  e_symm_max = 0.
  env_idx = 0
  for sidx in range(len(systs)):
    s = systs[sidx]
    if mname is not None: sname = "%s_%s_%s"%(s['name'],mname,stier)
    else: sname = "%s_%s"%(s['name'],stier)
    if len(row[sname]) == 2: e_symm = 0.5*(abs(row[sname][0]-1)+abs(row[sname][1]-1))
    else: e_symm = abs(row[sname][0]-1)
    if e_symm > e_symm_max: 
      e_symm_max = e_symm
      env_idx = sidx
  env_s = systs[env_idx]
  if mname is not None: env_sname = "%s_%s_%s"%(env_s['name'],mname,stier)
  else: env_sname = "%s_%s"%(env_s['name'],stier)
  return row[env_sname]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Function to change syst title
def renameSyst(t,oldexp,newexp): return re.sub(oldexp,newexp,t)

