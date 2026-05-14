import ROOT

# Function to add vars to workspace
def add_vars_to_workspace(ws, list_of_vars=[]):

  # Add intLumi var
  intLumi = ROOT.RooRealVar("intLumi", "intLumi", 1000., 0., 999999999.)
  intLumi.setConstant(True)
  getattr(ws,'import')(intLumi)

  # Add vars specified by dataframe columns: skipping cat, stxsvar and type
  ws_vars = {}
  for var in list_of_vars:
    if var == "CMS_hgg_mass":
      ws_vars[var] = ROOT.RooRealVar(var, var, 125., 100., 180.)
      ws_vars[var].setBins(160)
    elif var == "dZ":
      ws_vars[var] = ROOT.RooRealVar(var, var, 0., -20., 20.)
      ws_vars[var].setBins(40)
    elif var == "weight":
      ws_vars[var] = ROOT.RooRealVar(var, var, 0.)
    else:
      ws_vars[var] = ROOT.RooRealVar(var, var, 1., -999999, 999999)
      ws_vars[var].setBins(1)

    getattr(ws,'import')(ws_vars[var], ROOT.RooFit.Silence())

  return ws_vars.keys()

# Function to make RooArgSet
def make_argset(ws, list_of_vars=[]):
  aset = ROOT.RooArgSet()
  for v in list_of_vars: aset.add(ws.var(v))
  return aset
