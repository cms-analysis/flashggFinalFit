# Script to hold definitions of bkg functions
from collections import OrderedDict as od
import ROOT
import math
import ctypes
import numpy as np

def testPdf(pdf, model):
  original_value = model.xvar.getVal()
  getval = pdf.getVal(ROOT.RooArgSet(model.xvar))
  print(getval)
  assert np.isfinite(getval)

  model.xvar.setVal(model.xvar.getMax())
  getval = pdf.getVal(ROOT.RooArgSet(model.xvar))
  print(getval)
  assert np.isfinite(getval)

  model.xvar.setVal(model.xvar.getMin())
  getval = pdf.getVal(ROOT.RooArgSet(model.xvar))
  print(getval)
  assert np.isfinite(getval)

  model.xvar.setVal(original_value)

functionFamilies = od()

# Bernstein polynomial
functionFamilies['Bernstein'] = od()
functionFamilies['Bernstein']['name'] = ['Bernstein','bern']

# Exponential
functionFamilies['Exponential'] = od()
functionFamilies['Exponential']['name'] = ['Exponential','exp']

# # Power law
functionFamilies['PowerLaw'] = od()
functionFamilies['PowerLaw']['name'] = ['PowerLaw','pow']

# Laurent series
functionFamilies['Laurent'] = od()
functionFamilies['Laurent']['name'] = ['Laurent','lau']

# ExpPoly 
functionFamilies["ExpPoly"] = od()
functionFamilies['ExpPoly']['name'] = ['ExpPoly','exppoly']

#High Mass Functions
#Pow
# functionFamilies['HighMassPow'] = od()
# functionFamilies['HighMassPow']['name'] = ['HighMassPow','hmpow']

# functionFamilies['HighMassExppow'] = od()
# functionFamilies['HighMassExppow']['name'] = ['HighMassExppow','hmexppow']

# functionFamilies['HighMassInvpow'] = od()
# functionFamilies['HighMassInvpow']['name'] = ['HighMassInvpow','hminvpow']

# functionFamilies['HighMassInvpowlin'] = od()
# functionFamilies['HighMassInvpowlin']['name'] = ['HighMassInvpowlin','hminvpowlin']

# functionFamilies['HighMassModdijet'] = od()
# functionFamilies['HighMassModdijet']['name'] = ['HighMassModdijet','hmmoddijet']

# functionFamilies['HighMassDijet'] = od()
# functionFamilies['HighMassDijet']['name'] = ['HighMassDijet','hmdijet']
#del functionFamilies['HighMassDijet']

# Define function families
def getPdf(model,prefix,funcType,order):
 
  # For bernstein polynomial...
  if funcType == "Bernstein":
    paramList = ROOT.RooArgList()
    if order == 1: return False # remove bernstein-1

    for i in range(order):
      pname = "%s_p%g"%(prefix,i)
      p = ROOT.RooRealVar(pname,pname,0.1*(i+1),-15.,15.)
      f = ROOT.RooFormulaVar("%s_sq"%pname,"%s_sq"%pname,"@0*@0",ROOT.RooArgList(p))
      # Add params (and functions) to model
      model.params[pname] = p
      model.formulas["%s_sq"%pname] = f
      paramList.add(model.formulas["%s_sq"%pname])
    # Make Bernsteins
    return ROOT.RooBernsteinFast(order)(prefix,prefix,model.xvar,paramList)
      
  # For Exponential
  if funcType == "Exponential":
    # Only odd orders allowed
    if order%2==0: return False
    else:
      nFracs = (order-1)/2
      nExps = order-nFracs
      assert(nFracs==nExps-1)
      fracs = ROOT.RooArgList()
      exps = ROOT.RooArgList()
      for i in range(1,nFracs+1):
        fname = "%s_frac%g"%(prefix,i)
        model.params[fname] = ROOT.RooRealVar(fname,fname,0.9-float(i-1)*1./nFracs,0.0001,0.9999)
        fracs.add(model.params[fname])
      for i in range(1,nExps+1):
        pname = "%s_p%g"%(prefix,i)
        funcname = "%s_e%g"%(prefix,i)
        model.params[pname] = ROOT.RooRealVar(pname,pname,max(-1.,-0.04*(i+1)),-1.,0.)
        model.functions[funcname] = ROOT.RooExponential(funcname,funcname,model.xvar,model.params[pname])
        exps.add(model.functions[funcname])
      # Add up exponentials
      return ROOT.RooAddPdf(prefix,prefix,exps,fracs,True)

  # For Power Law
  elif funcType == "PowerLaw":
    # Only odd orders allowed
    if order%2==0: return False
    else:
      nFracs = (order-1)/2
      nPows = order-nFracs
      assert(nFracs==nPows-1)
      fracs = ROOT.RooArgList()
      pows = ROOT.RooArgList()
      for i in range(1,nFracs+1):
        fname = "%s_frac%g"%(prefix,i)
        model.params[fname] = ROOT.RooRealVar(fname,fname,0.9-float(i-1)*1./nFracs,0.0001,0.9999)
        fracs.add(model.params[fname])
      for i in range(1,nPows+1):
        pname = "%s_p%g"%(prefix,i)
        funcname = "%s_e%g"%(prefix,i)
        model.params[pname] = ROOT.RooRealVar(pname,pname,max(-9.,-1.*(i+1)),-9.,1.)
        model.functions[funcname] = ROOT.RooPower(funcname,funcname,model.xvar,model.params[pname])
        pows.add(model.functions[funcname])
      # Add up powers
      return ROOT.RooAddPdf(prefix,prefix,pows,fracs,True)

  # For Laurent series
  elif funcType == "Laurent":
    nLower = int(math.ceil(order/2.)) 
    nHigher = order-nLower
    pows = ROOT.RooArgList()
    plist = ROOT.RooArgList()
    # 0-th order
    funcname = "%s_pow0"%prefix
    model.functions[funcname] = ROOT.RooPower(funcname,funcname,model.xvar,ROOT.RooFit.RooConst(-4.))
    pows.add(model.functions[funcname])
    # Even terms
    for i in range(1,nLower+1):
      pname = "%s_l%g"%(prefix,i)
      model.params[pname] = ROOT.RooRealVar(pname,pname,0.25/order,0.000001,0.999999)
      plist.add(model.params[pname])
      funcname = "%s_powl%g"%(prefix,i)
      model.functions[funcname] = ROOT.RooPower(funcname,funcname,model.xvar,ROOT.RooFit.RooConst(-4.-i))
      pows.add(model.functions[funcname])
    # Odd terms
    for i in range(1,nHigher+1):
      pname = "%s_h%g"%(prefix,i)
      model.params[pname] = ROOT.RooRealVar(pname,pname,0.25/order,0.000001,0.999999)
      plist.add(model.params[pname])
      funcname = "%s_powh%g"%(prefix,i)
      model.functions[funcname] = ROOT.RooPower(funcname,funcname,model.xvar,ROOT.RooFit.RooConst(-4.+i))
      pows.add(model.functions[funcname])
    # Add up terms
    return ROOT.RooAddPdf(prefix,prefix,pows,plist,True)

  #High mass functions
  elif funcType == "HighMassPow":
    if order < 3: return False #starts with 3 d.o.f

    shift = ROOT.RooRealVar("%s_shift"%prefix,"%s_shift"%prefix,80.,0.,99.9)
    #x = ROOT.RooFormulaVar("%s_x"%prefix,"%s_x"%prefix,"@0-@1",ROOT.RooArgList(model.xvar,shift))
    model.params["%s_shift"%prefix] = shift
    #model.formulas["%s_x"%prefix] = x

    formula = "0"
    poly_coeffs = [shift]
    for i in range(1, order-1):
      pname = "%s_p%g"%(prefix,i)
      p = ROOT.RooRealVar(pname,pname,1,0,10.)
      model.params[pname] = p

      formula += "+@%d*(@0-@1)**%d"%(i+1,i) #+coeff * mgg**order where i = order
      poly_coeffs.append(p)
    formula = "abs(" + formula + ")"

    f = ROOT.RooFormulaVar("%s_poly"%prefix,"%s_poly"%prefix,formula,ROOT.RooArgList(model.xvar,*poly_coeffs))
    model.formulas["%s_poly"%prefix] = f
    
    a = ROOT.RooRealVar("%s_a"%prefix,"%s_a"%prefix,-0.5,-5.,-0.001)
    model.params["%s_a"%prefix] = a
    
    pdf = ROOT.RooPower(prefix,prefix,f,a)
    testPdf(pdf, model)
    return pdf

  elif funcType == "ExpPoly":
    if order == 1: return False # remove bernstein-1
    if order > 3: return False

    expr = "(@1*(@0/100))"
    for i in range(1, order):
      x_power = "*".join(["(@0/100)"]*(i+1))
      expr += "+(@%d*%s)"%((i+1),x_power)

    paramList = ROOT.RooArgList()
    paramList.add(model.xvar)
    for i in range(order):
      pname = "%s_p%g"%(prefix,i)
      p = ROOT.RooRealVar(pname,pname,0.1*(i+1),0.1,10.)
      model.params[pname] = p
      paramList.add(p)

    poly_name = "%s_exppolypoly"%prefix
    poly = ROOT.RooFormulaVar(poly_name,poly_name,expr,paramList)
    poly.Print()
    model.formulas[poly_name] = poly
    return ROOT.RooExponential(prefix,prefix,poly,ROOT.RooFit.RooConst(-1.0))

  # elif funcType == "HighMassExppow":
  #   if order < 3: return False

  #   shift = ROOT.RooRealVar("%s_shift"%prefix,"%s_shift"%prefix,80.,0.,99.)
  #   model.params["%s_shift"%prefix] = shift

  #   formula = "0"
  #   poly_coeffs = [shift]
  #   for i in range(1, order-1):
  #     pname = "%s_p%g"%(prefix,i)
  #     p = ROOT.RooRealVar(pname,pname,0.01,0.0,1.0)
  #     model.params[pname] = p

  #     formula += "+@%d*(@0-@1)**%d"%(i+1,i) #+coeff * mgg**order where i = order
  #     poly_coeffs.append(p)
  #   formula = "abs(" + formula + ")"
    
  #   f = ROOT.RooFormulaVar("%s_poly"%prefix,"%s_poly"%prefix,formula,ROOT.RooArgList(model.xvar,*poly_coeffs))
  #   model.formulas["%s_poly"%prefix] = f
    
  #   #a = ROOT.RooRealVar("%s_a"%prefix,"%s_a"%prefix,-0.5,-5.,1)
  #   a = ROOT.RooRealVar("%s_a"%prefix,"%s_a"%prefix,0.0,-1.0,1.0)
  #   model.params["%s_a"%prefix] = a
    
  #   pdf = ROOT.RooFormulaVar(prefix,prefix,"exp(-@0)*@1**@2",ROOT.RooArgList(f,model.xvar,a))
  #   testPdf(pdf, model)
  #   return pdf

  # elif funcType == "HighMassInvpow":
  #   if order < 3: return False

  #   shift = ROOT.RooRealVar("%s_shift"%prefix,"%s_shift"%prefix,80.,0.,99.9)
  #   model.params["%s_shift"%prefix] = shift

  #   formula = "0"
  #   poly_coeffs = [shift]
  #   for i in range(1, order-1):
  #     pname = "%s_p%g"%(prefix,i)
  #     p = ROOT.RooRealVar(pname,pname,-1.,-10.,0.)
  #     model.params[pname] = p

  #     formula += "+@%d*(@0-@1)**%d"%(i+1,i) #+coeff * mgg**order where i = order
  #     poly_coeffs.append(p)
    
  #   f = ROOT.RooFormulaVar("%s_poly"%prefix,"%s_poly"%prefix,formula,ROOT.RooArgList(model.xvar,*poly_coeffs))
  #   model.formulas["%s_poly"%prefix] = f
    
  #   power_coeff = ROOT.RooRealVar("%s_power_coeff"%prefix,"%s_power_coeff"%prefix,-0.1,-1.,-0.001)
  #   model.params["%s_power_coeff"%prefix] = power_coeff
  #   pdf = ROOT.RooFormulaVar(prefix,prefix,"(1-@0)**@1",ROOT.RooArgList(f,power_coeff))
  #   testPdf(pdf, model)
  #   return pdf

  # elif funcType == "HighMassInvpowlin":
  #   if order < 3: return False

  #   shift = ROOT.RooRealVar("%s_shift"%prefix,"%s_shift"%prefix,80.,-100.,99.9)
  #   model.params["%s_shift"%prefix] = shift

  #   formula = "0"
  #   poly_coeffs = [shift]
  #   for i in range(1, order-1):
  #     pname = "%s_p%g"%(prefix,i)
  #     p = ROOT.RooRealVar(pname,pname,1,0,10.)
  #     model.params[pname] = p

  #     formula += "+@%d*(@0-@1)**%d"%(i+1,i) #+coeff * mgg**order where i = order
  #     poly_coeffs.append(p)
    
  #   f = ROOT.RooFormulaVar("%s_poly"%prefix,"%s_poly"%prefix,formula,ROOT.RooArgList(model.xvar,*poly_coeffs))
  #   model.formulas["%s_poly"%prefix] = f
    
  #   power_coeff = ROOT.RooRealVar("%s_power_coeff"%prefix,"%s_power_coeff"%prefix,-0.5,-5.,-0.001)
  #   model.params["%s_power_coeff"%prefix] = power_coeff
  #   testPdf(pdf, model)
  #   pdf = ROOT.RooFormulaVar(prefix,prefix,"(1-@0)**@1",ROOT.RooArgList(model.xvar,f))
  #   return pdf

  # elif funcType == "HighMassModdijet":
  #   if order < 3: return False

  #   shift = ROOT.RooRealVar("%s_shift"%prefix,"%s_shift"%prefix,80.,-100.,99.9)
  #   model.params["%s_shift"%prefix] = shift

  #   formula = "0"
  #   poly_coeffs = [shift]
  #   for i in range(1, order-1):
  #     pname = "%s_p%g"%(prefix,i)
  #     p = ROOT.RooRealVar(pname,pname,1,0,10.)
  #     model.params[pname] = p

  #     formula += "+@%d*(1-@0-@1)**%d"%(i+1,i) #+coeff * mgg**order where i = order
  #     poly_coeffs.append(p)
    
  #   f = ROOT.RooFormulaVar("%s_poly"%prefix,"%s_poly"%prefix,formula,ROOT.RooArgList(model.xvar,*poly_coeffs))
  #   model.formulas["%s_poly"%prefix] = f
    
  #   a = ROOT.RooRealVar("%s_a"%prefix,"%s_a"%prefix,-0.5,-5.,-0.001)
  #   b = ROOT.RooRealVar("%s_b"%prefix,"%s_b"%prefix,-0.5,-5.,-0.001)
  #   c = ROOT.RooRealVar("%s_c"%prefix,"%s_c"%prefix,-0.5,-5.,-0.001)
  #   model.params["%s_a"%prefix] = a
  #   model.params["%s_b"%prefix] = b
  #   model.params["%s_c"%prefix] = c
  #   return ROOT.RooFormulaVar(prefix,prefix,"@0**(@1+@2*log(@0))*@3**@4",ROOT.RooArgList(model.xvar,a,b,f,c))

  elif funcType == "HighMassDijet":
    if order < 1: return False #starts with 2 d.o.f

    coeffs = []
    for i in range(order):
      pname = "%s_p%g"%(prefix,i)
      p = ROOT.RooRealVar(pname,pname,0.1,0.,20.)
      model.params[pname] = p

      coeffs.append(p)
    
    if order == 1:
      pdf = ROOT.RooGenericPdf(prefix, prefix, "1 / (@0/13000)**@1",ROOT.RooArgList(model.xvar,*coeffs))
    elif order == 2:
      pdf = ROOT.RooGenericPdf(prefix, prefix, "(1-(@0/13000))**@1 / (@0/13000)**@2",ROOT.RooArgList(model.xvar,*coeffs)) 
    elif order == 3:
      pdf = ROOT.RooGenericPdf(prefix, prefix, "(1-(@0/13000))**@1 / ( (@0/13000)**(@2 + @3*log(@0/13000)) )",ROOT.RooArgList(model.xvar,*coeffs))  
    elif order == 4:
      pdf = ROOT.RooGenericPdf(prefix, prefix, "(1-(@0/13000))**@1 / ( (@0/13000)**(@2 + @3*log(@0/13000) + @4*log(@0/13000)**2) )",ROOT.RooArgList(model.xvar,*coeffs))  
    elif order == 5:
      pdf = ROOT.RooGenericPdf(prefix, prefix, "(1-(@0/13000))**@1 / ( (@0/13000)**(@2 + @3*log(@0/13000) + @4*log(@0/13000)**2 + @5*log(@0/13000)**3) )",ROOT.RooArgList(model.xvar,*coeffs))  
    else:
      return False
        
    testPdf(pdf, model)
    return pdf