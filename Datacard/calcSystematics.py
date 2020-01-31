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
def calcSyst_factory(sd,_syst,_options):

  # Extract type of systematic: specified by string
  _systFactoryType = systFactoryType(sd,_syst)
  print " --> [DEBUG] %s: will treat as %s"%(_syst['name'],_systFactoryType)

  # Add columns to dataFrame with default value: if unmerged one for each year
  if _syst['merge']:
    sd[_syst['name']] = '-'
    sd = systFactory(sd,_syst,_systFactoryType,_options)
  else:
    for _year in _options.years.split(","):
      sd["%s_%s"%(_syst['name'],_year)] = '-'
      sd = systFactory(sd, _syst, _systFactoryType,_options,year=_year)

  return sd

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# SYSTEMATICS FACTORY: use input workspace to calculate shifts from systematic variations
# d - dataFrame, s - systematic (entry in dict in makeDatacard.py LX) 

# Function to return the type of systematics:
# a) Anti-symmetric weight in nominal RooDataSet: "a_w"
# b) Symmetric weight in nominal RooDataSet: "s_w"
# c) Anti-symmetric shifts in RooDataHist: "a_h"
def systFactoryType(d,s):
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

  print " --> [ERROR] systematic %s: cannot extract type in systFactoryType function. Doesn't match requirement for (anti)-symmetric weights or anti-symmetric histograms. Leaving..."
  sys.exit(1)

# Function to calculate shifts from systematics
def systFactory(d,s,factoryType,options,year=None):

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
      # Extract nominal RooDataSet: includes weights as args
      cat_dropYearTag = re.sub("_%s"%r['year'],"",r['cat'])
      rdata_nominal = r['inputWS'].data("%s_125_13TeV_%s"%(r['proc_s0'],cat_dropYearTag)) # RooDataSet
      # Extract nominal sum of entries
      yield_nominal = rdata_nominal.sumEntries()
      
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

      # FIXME: is there a function for re-weighting RooDataSet based on function without looping over events
      # Extract observable (default for hgg = CMS_hgg_mass") from options, and nominal event weight
      #xobs = r['inputWS'].var( options.xobs )
      #w_nominal = ROOT.RooRealVar("weight","weight",0)
      # Make empty clones of datasets and define up/down weights
      #rdata_up = rdata_nominal.emptyClone()
      #rdata_down = rdata_nominal.emptyClone()
      #weight = {}
      #for wkey in ['up','down']: weight[wkey] = ROOT.RooRealVar( w_str[wkey], w_str[wkey], 0 )

      # Loop over points in dataset and fill new datasets with updated weights
      #for i in range(0,rdata_nominal.numEntries()):
      #  p = rdata_nominal.get(i)
      #  xobs.setVal(p.getRealValue(options.xobs))
      #  w_nominal = rdata_nominal.weight()
      #  # Get central/up/down weight factors for multiplying nominal weights
      #  wfactor = {}
      #  for wkey in w_str: wfactor[wkey] = p.getRealValue(w_str[wkey])
      #  # Catch 1: if central weight = 0 --> math error. Skip event
      #  if wfactor['central'] == 0: 
      #    print " --> [WARNING] systematic %s: event in (%s,%s) with identically 0 central weight. Skipping event..."%(s['name'],r['proc'],r['cat'])
      #    continue
      #  # Catch 2: if up/down weight are equal --> Set up/down to nominal
      #  elif wfactor['up']==wfactor['down']: 
      #    weight['up'].setVal(w_nominal)
      #    weight['down'].setVal(w_nominal)
      #  else:
      #    # Calculate up and down weights
      #    weight['up'].setVal(w_nominal*(wfactor['up']/wfactor['central']))
      #    weight['down'].setVal(w_nominal*(wfactor['down']/wfactor['central']))

      #  #Add datapoint to empty clones
      #  rdata_up.add(ROOT.RooArgSet(xobs),weight['up'].getVal())
      #  rdata_down.add(ROOT.RooArgSet(xobs),weight['down'].getVal())

      # Extract up and down fluctions in yield for current proc x cat (row)
      #yield_up, yield_down = rdata_up.sumEntries(), rdata_down.sumEntries()
      #frac_up, frac_down = yield_up/r['sumEntries'], yield_down/r['sumEntries']

      # Update relevant cells in dataFrame
      if year == None: d.at[ir,s['name']] = [frac_down,frac_up] #"%.3f/%.3f"%(frac_down,frac_up)
      else: d.at[ir,"%s_%s"%(s['name'],year)] = [frac_down,frac_up] #]"%.3f/%.3f"%(frac_down,frac_up)

  # For symmetric weights
  
  # For asymmetric hists
  elif factoryType == "a_h":
    # Iterate over rows in dataFrame: extract RooDataHist for up/down fluctuations and extract yields
    for ir,r in d_slice.iterrows():
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
