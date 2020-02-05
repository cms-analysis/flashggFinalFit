# Hold defs of functions for calculating systematics and adding to dataframe
import os, sys, re
import ROOT

# sd = "systematics dataframe"

# CONSTANT: for all signal processes
def calcSyst_constant(sd,_syst,options):

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

# EXPERIMENTAL
def calcSyst_experiment(sd,_syst,_options):

  # Extract type of systematic: specified by string
  _factoryType = factoryType(sd,_syst)
  print " --> [DEBUG] %s (experiment): will treat as %s"%(_syst['name'],_factoryType)

  # Add columns to dataFrame with default value: if unmerged one for each year
  if _syst['merge']:
    sd[_syst['name']] = '-'
    sd = experimentalSystFactory(sd,_syst,_factoryType,_options)
  else:
    for _year in _options.years.split(","):
      sd["%s_%s"%(_syst['name'],_year)] = '-'
      sd = experimentalSystFactory(sd, _syst, _factoryType,_options,year=_year)

  return sd    

# THEORY
def calcSyst_theory(sd,_systs,_options):
  # Uses list of systematics as input
  sd, pmy, stxsbiny, stxsshapey = theoreticalSystFactory(sd,_systs,_options)
  return sd, pmy, stxsbiny, stxsshapey

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Function to return type of systematic: to be used by factory function
# a) Anti-symmetric weight in nominal RooDataSet: "a_w"
# b) Symmetric weight in nominal RooDataSet: "s_w"
# c) Anti-symmetric shifts in RooDataHist: "a_h"
def factoryType(d,s):
  # Look at first entry in signal
  ws0 = d[d['type']=='sig'].iloc[0].inputWS
  # Check if syst is var (weight) in workspace
  if ws0.allVars().selectByName("%s*"%(s['name'])).getSize():
    nWeights = ws0.allVars().selectByName("%s*"%(s['name'])).getSize()
    if nWeights == 2: return "a_w"
    elif nWeights == 1: return "s_w"
    else:
      print " --> [ERROR] systematic %s: > 2 weights in workspace. Leaving..."%s['name']
      sys.exit(1)
  
  # Else: check if RooDataHist exist
  # First drop year tag on category if present
  cat0_dropYearTag = re.sub( "_%s"%d[d['type']=='sig'].iloc[0]['year'], "", d[d['type']=='sig'].iloc[0]['cat'] )
  dataHistUp = "%s_125_13TeV_%s_%sUp01sigma"%(d[d['type']=='sig'].iloc[0].proc_s0,cat0_dropYearTag,s['name'])
  dataHistDown = "%s_125_13TeV_%s_%sDown01sigma"%(d[d['type']=='sig'].iloc[0].proc_s0,cat0_dropYearTag,s['name'])
  if(ws0.data(dataHistUp)!=None)&(ws0.data(dataHistDown)!=None): return "a_h"

  print " --> [ERROR] systematic %s: cannot extract type in factoryType function. Doesn't match requirement for (anti)-symmetric weights or anti-symmetric histograms. Leaving..."
  sys.exit(1)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXPERIMENTAL SYSTEMATICS FACTORY: use input workspace to calculate shifts from systematic variations
# d - dataFrame, s - systematic (entry in dict in makeDatacard.py LX) 


# Function to calculate shifts from systematics
def experimentalSystFactory(d,s,factoryType,options,year=None):

  # Systematics: ony signal elements in dataFrame (not NOTAG) and split by year (if required)
  d_slice = d[(d['type']=='sig')&(d['year']==year)&(~d['cat'].str.contains("NOTAG"))] if year!=None else d[(d['type']=='sig')&(~d['cat'].str.contains("NOTAG"))]

  # For asymmetric weights...
  if factoryType == "a_w":

    # Define weight strings for central and up/down fluctuation
    w_str = {}
    w_str['central'] = "centralObjectWeight"
    w_str['up'] = "%sUp01sigma"%s['name']
    w_str['down'] = "%sDown01sigma"%s['name']

    # Iterate over proc x cat combinations in dataFrame
    for ir,r in d_slice.iterrows():

      # If nominal yield is empty then skip
      if r['sumEntries'] == 0: continue

      # Extract nominal RooDataSet: includes weights as args
      cat_dropYearTag = re.sub("_%s"%r['year'],"",r['cat'])
      rdata_nominal = r['inputWS'].data("%s_125_13TeV_%s"%(r['proc_s0'],cat_dropYearTag)) # RooDataSet
 
      # Loop over events and calculate sum of reweighted events
      yield_up, yield_down = 0, 0
      for i in range(0,rdata_nominal.numEntries()):
        p = rdata_nominal.get(i)
        w = rdata_nominal.weight()
        # Extract up/down weight
        wfactor = {}
        for wkey in w_str: wfactor[wkey] = p.getRealValue(w_str[wkey])
        # Catch 1: if central weight = 0 --> math error. Skip event
        if wfactor['central'] == 0: 
          print " --> [WARNING] systematic %s: event in (%s,%s) with identically 0 central weight. Skipping event..."%(s['name'],r['proc'],r['cat'])
          continue
        # Catch 2: if up/down weight are equal --> Set up/down to nominal
        elif wfactor['up']==wfactor['down']: 
          wup = w
          wdown = w
        else:
          # Calculate up and down weights
          wup  = w*(wfactor['up']/wfactor['central'])
          wdown  = w*(wfactor['down']/wfactor['central'])

        # Add up/down weights
        yield_up += wup
        yield_down += wdown

      # Calculate yield variations
      frac_up, frac_down = yield_up/r['sumEntries'], yield_down/r['sumEntries']

      # Update relevant cells in dataFrame
      if year == None: d.at[ir,s['name']] = [frac_down,frac_up] #"%.3f/%.3f"%(frac_down,frac_up)
      else: d.at[ir,"%s_%s"%(s['name'],year)] = [frac_down,frac_up] #]"%.3f/%.3f"%(frac_down,frac_up)

  # For symmetric weights
  
  # For asymmetric hists
  elif factoryType == "a_h":
    # Iterate over rows in dataFrame: extract RooDataHist for up/down fluctuations and extract yields
    for ir,r in d_slice.iterrows():

      # if nominal yield is zero then skip
      if r['sumEntries'] == 0: continue

      cat_dropYearTag = re.sub("_%s"%r['year'],"",r['cat'])
      rdatahist_up = r['inputWS'].data("%s_125_13TeV_%s_%sUp01sigma"%(r['proc_s0'],cat_dropYearTag,s['name']))
      rdatahist_down = r['inputWS'].data("%s_125_13TeV_%s_%sDown01sigma"%(r['proc_s0'],cat_dropYearTag,s['name']))
      
      # Calculate up and down fluctuations for current proc x cat (row)
      yield_up, yield_down = rdatahist_up.sumEntries(), rdatahist_down.sumEntries()
      frac_up, frac_down = yield_up/r['sumEntries'], yield_down/r['sumEntries']

      # Update relevant cells in dataFrame
      if year == None: d.at[ir,s['name']] = [frac_down,frac_up] #"%.3f/%.3f"%(frac_up,frac_down)
      else: d.at[ir,"%s_%s"%(s['name'],year)] = [frac_down,frac_up] #"%.3f/%.3f"%(frac_up,frac_down)
      
  # Return dataframe with updated systematic values
  return d

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# THEORETICAL SYSTEMATICS FACTORY
def theoreticalSystFactory(d,ts,options):

  # Takes list of systematics (ts) as input (unlike experimental systematics)
  # For each systematic fill a dictionary with name and type from factoryType function
  ts_factoryType = {}
  for s in ts: 
    ts_factoryType[s['name']] = factoryType(d,s)
    print " --> [DEBUG] %s (theory): will treat as %s"%(s['name'],factoryType(d,s))

  # Step 1: extract inclusive per-production mode yield and set up counters for each systematic variation
  productionModeYields = {}
  for proc_s0 in d[d['type']=='sig'].proc_s0.unique():
    productionModeYields[proc_s0] = {}
    productionModeYields[proc_s0]['nominal'] = d[(d['type']=='sig')&(d['proc_s0']==proc_s0)]['sumEntries'].sum()
    for s in ts:
      if ts_factoryType[s['name']] == "a_w":
        for var in ['up','down']: productionModeYields[proc_s0]['%s_%s'%(s['name'],var)] = 0
      elif ts_factoryType[s['name']] == "s_w": productionModeYields[proc_s0][s['name']] = 0
      else:
        print " --> [ERROR] type %s not supported for theory systematic %s. Leaving..."%(ts_factoryType[s['name']],s['name'])
        sys.exit(1)

  # Step 2: extract STXS normalization yields and per-prod mode yields for each systematic source
  stxsBinYields = {}
  # Loop over unique processes in dataframe
  for proc in d[d['type']=='sig'].proc.unique():
    print "    --> [VERBOSE] Calculating the norm variations for STXS bin: %s"%proc
    stxsBinYields[proc] = {}
    # Create a counter for each systematic variation and nominal
    stxsBinYields[proc]['nominal'] = 0
    for s in ts:
      if ts_factoryType[s['name']] == "a_w":
        for var in ['up','down']: stxsBinYields[proc]['%s_%s'%(s['name'],var)] = 0
      elif ts_factoryType[s['name']] == "s_w": stxsBinYields[proc][s['name']] = 0
      else: 
        print " --> [ERROR] type %s not supported for theory systematic %s. Leaving..."%(ts_factoryType[s['name']],s['name'])
        sys.exit(1)
          
    # Iterate over rows for given proc
    for ir,r in d[d['proc']==proc].iterrows():
      # Extract nominal RooDataset: includes weights as args
      cat_dropYearTag = re.sub("_%s"%r['year'],"",r['cat'])
      rdata_nominal = r['inputWS'].data("%s_125_13TeV_%s"%(r['proc_s0'],cat_dropYearTag))
      # Add nominal yield to yields container
      stxsBinYields[proc]['nominal'] += rdata_nominal.sumEntries()

      # Loop over events in dataset and sum weights for different syst variations
      for i in range(0,rdata_nominal.numEntries()):
        p = rdata_nominal.get(i)
        w = rdata_nominal.weight()
        # For each systematic: extract new weight(s) and add to yields container
        for s in ts:
          # For asymmetric weights:
          if ts_factoryType[s['name']] == "a_w":
            f_central = p.getRealValue("centralObjectWeight")
            f_up, f_down = p.getRealValue("%sUp01sigma"%s['name']), p.getRealValue("%sDown01sigma"%s['name'])
            # Checks:
            # 1) if central weights are zero then skip event
            if f_central == 0:
              print " --> [WARNING] theory systematic %s: event %g in (%s,%s) with identically 0 central weight. Skipping event..."%(s['name'],i,r['proc'],r['cat'])
              continue
            # 2) if up weight is equal to down weight: set equal to nominal weight
            elif f_up == f_down: w_up, w_down = w, w
            # Calculate up and down weights
            else:
              w_up, w_down = w*(f_up/f_central), w*(f_down/f_central)
            
            # Add to yields containers: per production mode and per STXS bin
            productionModeYields[r['proc_s0']]["%s_up"%s['name']] += w_up
            productionModeYields[r['proc_s0']]["%s_down"%s['name']] += w_down
            stxsBinYields[proc]["%s_up"%s['name']] += w_up
            stxsBinYields[proc]["%s_down"%s['name']] += w_down

          # For symmetric weights
          if ts_factoryType[s['name']] == "s_w":
            if "scaleWeight" in s['name']: f_central = p.getRealValue("scaleWeight_0")
            else: f_central = p.getRealValue("centralObjectWeight")
            f = p.getRealValue("%s"%s['name'])
            # Check: if centra weight is zero then skip event
            if f_central == 0:
              print " --> [WARNING] theory systematic %s: event %g in (%s,%s) with identically 0 central weight. Skipping event..."%(s['name'],i,r['proc'],r['cat'])
              continue
            else:
              # Add to yields containers: per production mode and per STXS bin
              productionModeYields[r['proc_s0']][s['name']] += w*(f/f_central)
              stxsBinYields[proc][s['name']] += w*(f/f_central)

  # Step 3: calculate STXS shape variations i.e. change of shape within STXS bin
  #         > normalize integral for each STXS bin to the same value (stxsBinYields)
  #         > extract relative yield changes in given proc x cat

  # i) add column to dataFrame to store shape uncertainties (if require shape uncertainties)
  for s in ts: 
    if 'shape' in s['tiers']: d["%s_shape"%s['name']] = '-'
    if 'ishape' in s['tiers']: d["%s_ishape"%s['name']] = '-' # Inclusive shift at proc x cat level

  # ii) loop over signal rows in dataframe (i.e each proc x cat combination, including NoTag)
  for ir,r in d[d['type']=='sig'].iterrows():

    # If nominal yield for a proc x cat is zero then skip
    if r['sumEntries'] == 0: continue

    print "    --> [VERBOSE] Calculating the shape variations for (STXS bin,RECO category) = (%s,%s)"%(r['proc'],r['cat'])

    # Store yields for given proc x cat in tmp container
    stxsShapeYields = {}
    stxsShapeYields['nominal'] = r['sumEntries']
    for s in ts:
      if('shape' not in s['tiers'])&('ishape' not in s['tiers']): continue
      if ts_factoryType[s['name']] == "a_w":
        for var in ['up','down']: stxsShapeYields['%s_%s'%(s['name'],var)] = 0
      elif ts_factoryType[s['name']] == "s_w": stxsShapeYields[s['name']] = 0
      else: 
        print " --> [ERROR] type %s not supported for theory systematic %s. Leaving..."%(ts_factoryType[s['name']],s['name'])

    # Extract nominal RooDataSet
    cat_dropYearTag = re.sub("_%s"%r['year'],"",r['cat'])
    rdata_nominal = r['inputWS'].data("%s_125_13TeV_%s"%(r['proc_s0'],cat_dropYearTag))
    # Loop over events and calculate effect of systematics: sum yields
    for i in range(0,rdata_nominal.numEntries()):
      p = rdata_nominal.get(i)
      w = rdata_nominal.weight()
      # Loop over systematics
      for s in ts:
        # If do not require shape uncertainties then skip...
        if('shape' not in s['tiers'])&('ishape' not in s['tiers']): continue
        # If asymmetric weights
        if ts_factoryType[s['name']] == "a_w":
	  f_central = p.getRealValue("centralObjectWeight")
	  f_up, f_down = p.getRealValue("%sUp01sigma"%s['name']), p.getRealValue("%sDown01sigma"%s['name'])
	  # Checks:
	  # 1) if central weights are zero then skip event
	  if f_central == 0:
	    print " --> [WARNING] theory systematic %s: event %g in (%s,%s) with identically 0 central weight. Skipping event..."%(s['name'],i,r['proc'],r['cat'])
	    continue
	  # 2) if up weight is equal to down weight: set equal to nominal weight
	  elif f_up == f_down: w_up, w_down = w, w
	  # Calculate up and down weights
	  else:
	    w_up, w_down = w*(f_up/f_central), w*(f_down/f_central)
	  
	  # Add to tmp yields container
	  stxsShapeYields["%s_up"%s['name']] += w_up
	  stxsShapeYields["%s_down"%s['name']] += w_down

	# For symmetric weights
	if ts_factoryType[s['name']] == "s_w":
          if "scaleWeight" in s['name']: f_central = p.getRealValue("scaleWeight_0")
          else: f_central = p.getRealValue("centralObjectWeight")
	  f = p.getRealValue(s['name'])
	  # Check: if central weight is zero then skip event
	  if f_central == 0:
	    print " --> [WARNING] theory systematic %s: event %g in (%s,%s) with identically 0 central weight. Skipping event..."%(s['name'],i,r['proc'],r['cat'])
	    continue
	  else:
	    # Add to tmp yields container
	    stxsShapeYields[s['name']] += w*(f/f_central)

    # Calculate the STXS shape variation by dividing out the STXS bin variation and add to dataFrame
    for s in ts:
      # If do not require shape uncertainties then skip...
      if('shape' not in s['tiers'])&('ishape' not in s['tiers']): continue
      # If ggH systematic for non ggH process
      if ("ggH" in s['name'])&("ggH" not in r['proc']): continue 
      else:
	if ts_factoryType[s['name']] == "a_w":
	  shape_frac_up = (stxsShapeYields["%s_up"%s['name']]/stxsShapeYields["nominal"])/(stxsBinYields[r['proc']]["%s_up"%s['name']]/stxsBinYields[r['proc']]['nominal'])
	  shape_frac_down = (stxsShapeYields["%s_down"%s['name']]/stxsShapeYields["nominal"])/(stxsBinYields[r['proc']]["%s_down"%s['name']]/stxsBinYields[r['proc']]['nominal'])
          ishape_frac_up = stxsShapeYields["%s_up"%s['name']]/stxsShapeYields["nominal"]
          ishape_frac_down = stxsShapeYields["%s_down"%s['name']]/stxsShapeYields["nominal"]
	  if 'shape' in s['tiers']: d.at[ir,"%s_shape"%s['name']] = [shape_frac_down,shape_frac_up] 
          if 'ishape' in s['tiers']: d.at[ir,"%s_ishape"%s['name']] = [ishape_frac_down,ishape_frac_up]
	elif ts_factoryType[s['name']] == "s_w":
	  shape_frac = (stxsShapeYields[s['name']]/stxsShapeYields["nominal"])/(stxsBinYields[r['proc']][s['name']]/stxsBinYields[r['proc']]['nominal'])
          ishape_frac = stxsShapeYields[s['name']]/stxsShapeYields["nominal"]
	  if 'shape' in s['tiers']: d.at[ir,"%s_shape"%s['name']] = [shape_frac]
	  if 'ishape' in s['tiers']: d.at[ir,"%s_ishape"%s['name']] = [ishape_frac]

  # Step 4: add STXS bin normalisation uncertainties to dataFrame
  for s in ts:
    if('norm' not in s['tiers'])&('inorm' not in s['tiers'])&('inc' not in s['tiers']): continue
    if 'norm' in s['tiers']: d["%s_norm"%s['name']] = '-' 
    if 'inorm' in s['tiers']: d["%s_inorm"%s['name']] = '-' # check: inclusive shifts in STXS bin
    if 'inc' in s['tiers']: d["%s_inc"%s['name']] = '-' # check: inclusive shift in production mode

  # Loop over rows in dataFrame and add relevant uncertainties
  for ir,r in d[d['type']=='sig'].iterrows():
    # If nominal yield for process is 0 then skip
    if r['sumEntries'] == 0: continue

    # Loop over systematics
    for s in ts:

      # Skip ggH systematics for non ggH processes
      if("ggH" in s['name'])&("ggH" not in r['proc']): continue

      # For asymmetric weights:
      if ts_factoryType[s['name']] == "a_w":
	norm_frac_up = (stxsBinYields[r['proc']]["%s_up"%s['name']]/stxsBinYields[r['proc']]['nominal'])/(productionModeYields[r['proc_s0']]["%s_up"%s['name']]/productionModeYields[r['proc_s0']]['nominal'])
	norm_frac_down = (stxsBinYields[r['proc']]["%s_down"%s['name']]/stxsBinYields[r['proc']]['nominal'])/(productionModeYields[r['proc_s0']]["%s_down"%s['name']]/productionModeYields[r['proc_s0']]['nominal'])
	inorm_frac_up = stxsBinYields[r['proc']]["%s_up"%s['name']]/stxsBinYields[r['proc']]['nominal']
	inorm_frac_down = stxsBinYields[r['proc']]["%s_down"%s['name']]/stxsBinYields[r['proc']]['nominal']
	inc_frac_up = productionModeYields[r['proc_s0']]["%s_up"%s['name']]/productionModeYields[r['proc_s0']]['nominal']
	inc_frac_down = productionModeYields[r['proc_s0']]["%s_down"%s['name']]/productionModeYields[r['proc_s0']]['nominal']
	if 'norm' in s['tiers']: d.at[ir,"%s_norm"%s['name']] = [norm_frac_down,norm_frac_up]
	if 'inorm' in s['tiers']: d.at[ir,"%s_inorm"%s['name']] = [inorm_frac_down,inorm_frac_up]
	if 'inc' in s['tiers']: d.at[ir,"%s_inc"%s['name']] = [inc_frac_down,inc_frac_up]
      # For symmetric weights
      elif ts_factoryType[s['name']] == "s_w":
	norm_frac = (stxsBinYields[r['proc']][s['name']]/stxsBinYields[r['proc']]['nominal'])/(productionModeYields[r['proc_s0']][s['name']]/productionModeYields[r['proc_s0']]['nominal'])
	inorm_frac = stxsBinYields[r['proc']][s['name']]/stxsBinYields[r['proc']]['nominal']
	inc_frac = productionModeYields[r['proc_s0']][s['name']]/productionModeYields[r['proc_s0']]['nominal']
	if 'norm' in s['tiers']: d.at[ir,"%s_norm"%s['name']] = [norm_frac]
	if 'inorm' in s['tiers']: d.at[ir,"%s_inorm"%s['name']] = [inorm_frac]
	if 'inc' in s['tiers']: d.at[ir,"%s_inc"%s['name']] = [inc_frac]

  # Return dataFrame with added components
  return d, productionModeYields, stxsBinYields, stxsShapeYields

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Function to group systematics: e.g. for scaleWeight where up/down = [1,2],[3,6] etc
def groupSyst(d,ts,prefix="scaleWeight",suffix="shape",groupings=[]):
  
  # Run over groupings and add new columns to dataFrame 
  for group_idx in range(len(groupings)):
    grouping = groupings[group_idx]
    # Add column to dataFrame
    d['%s_group%g_%s'%(prefix,group_idx,suffix)] = '-'
    # Loop over rows in dataFrame
    for ir,r in d[d['type']=='sig'].iterrows():
      # Check if they are lists of len(1)
      if type(r['%s_%g_%s'%(prefix,grouping[0],suffix)]) is not list:
        print " --> [ERROR] in grouping systematic %s_%g_%s. Not saved as symmetric uncertainty (list length 0). Leaving"%(prefix,grouping[0],suffix)
      if type(r['%s_%g_%s'%(prefix,grouping[1],suffix)]) is not list:
        print " --> [ERROR] in grouping systematic %s_%g_%s. Not saved as symmetric uncertainty (list length 0). Leaving"%(prefix,grouping[1],suffix)

      # Extract up/down variations from group
      frac_up = r['%s_%g_%s'%(prefix,grouping[0],suffix)][0]
      frac_down = r['%s_%g_%s'%(prefix,grouping[1],suffix)][0]

      # Add as new columns in dataFrame
      d.at[ir,'%s_group%g_%s'%(prefix,group_idx,suffix)] = [frac_down,frac_up]

    # Drop original columns from dataFrame 
    for g in grouping: d.drop( ['%s_%g_%s'%(prefix,g,suffix)], axis=1, inplace=True )

  # Replace individual systematics from dict and add grouping
  for group_idx in range(len(groupings)):
    grouping = groupings[group_idx]
    for s in ts:
      # Change 1st to group and delete 2nd
      if s['name'] == "%s_%g"%(prefix,grouping[0]):
        s['name'] = re.sub("%s_%g"%(prefix,grouping[0]),"%s_group%g"%(prefix,group_idx),s['name'])
        s['title'] = re.sub("%s_%g"%(prefix,grouping[0]),"%s_group%g"%(prefix,group_idx),s['title']) 
      elif s['name'] == "%s_%g"%(prefix,grouping[1]): ts.remove(s)

  return d,ts
      
    
    

