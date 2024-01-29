"""
Script to create the workspaces for the control regions used in ABCD method.
We need the:
- RooDataHist
- Background model for cr (just an exp)
- DY signal model (DCB) which will be used in control and signal regions
"""

import sys
import ROOT
from commonObjects import inputWSName__,sqrts__
import os

def main(f_in, cat, f_out):
    ROOT.gROOT.SetBatch(ROOT.kTRUE)
    f = ROOT.TFile(f_in,"read")
    inputWS = f.Get(inputWSName__)
    f.Close()

    xvar = inputWS.var("CMS_hgg_mass")
    nBinsOutput = xvar.getBins()
    xvar.setBins(nBinsOutput/4)

    zoom = True
    if zoom:
        xvar.setRange(55, 180)
        xvar.setBins(125)
 
    # create data roohist
    #inputWS.Print()
    data = inputWS.data("Data_%s_%s"%(sqrts__,cat))
    data_zoom = data.reduce(ROOT.RooFit.CutRange("CMS_hgg_mass > 55 && CMS_hgg_mass < 180"))
    DataHistFit = ROOT.RooDataHist("datahistfit","datahistfit",ROOT.RooArgSet(xvar),data_zoom)

    frame = xvar.frame()
    DataHistFit.plotOn(frame)

    # bkg model
    pname="model_%s_combined_exp1_p0"%cat
    p0 = ROOT.RooRealVar(pname,pname,-0.1,-1., 0.)
    funcname="CMS_hgg_%s_combined_13TeV_bkgshape"%cat
    bkg = ROOT.RooExponential(funcname,funcname,xvar,p0)


    # signal model
    proc="dy"
    catnum = int(cat.split("cat")[1].split("cr")[0])
    suffix = "_%s_cat%d_%s"%("combined", catnum, proc)
    mean = ROOT.RooRealVar("mean"+suffix, "mean"+suffix, 90.,85.,95.)
    sigma = ROOT.RooRealVar("sigma"+suffix, "sigma"+suffix, 2.5,1.,4.)
    bkg_frac = ROOT.RooRealVar("gauss_frac", "gauss_frac", 0, 0.0, 1.0)

    gauss = ROOT.RooGaussian("bkg_gauss_"+suffix, "bkg_gauss"+suffix, xvar, mean, sigma)
    gauss_model = ROOT.RooAddPdf("gauss_model", "gauss_model", bkg, gauss, bkg_frac)
    gauss_model.fitTo(DataHistFit)
    gauss_model.plotOn(frame, ROOT.RooFit.LineColor(ROOT.kBlue))
    gauss_model.Print("t")
    gauss_chi2 = gauss_model.createChi2(DataHistFit).getVal()
    print(gauss_chi2, xvar.getBins())
    gauss_ndof = int(xvar.getBins() - (1 + 1 + 2))
    gauss_gof_pval = ROOT.TMath.Prob(gauss_chi2,gauss_ndof)
    print(gauss_gof_pval)

    if gauss_gof_pval < 0.01:       
    #if True:
      n1 = ROOT.RooRealVar("n1"+suffix, "n1"+suffix, 2.,0.1,50.)
      n2 = ROOT.RooRealVar("n2"+suffix, "n2"+suffix, 2.,0.1,50.)
      a1 = ROOT.RooRealVar("a1"+suffix, "a1"+suffix, 1.,0.5,5.0)
      a2 = ROOT.RooRealVar("a2"+suffix, "a2"+suffix, 1.,0.5,5.0)

      dcb = ROOT.RooDoubleCBFast("bkg_dcb"+suffix, "bkg_dcb"+suffix, xvar, mean, sigma, a1, n1, a2, n2)
      dcb_model = ROOT.RooAddPdf("dcb_model", "dcb_model", bkg, dcb, bkg_frac)
      dcb_model.fitTo(DataHistFit)
      dcb_model.plotOn(frame, ROOT.RooFit.LineColor(ROOT.kRed))
      dcb_model.Print("t")
      dcb_chi2 = dcb_model.createChi2(DataHistFit).getVal()
      print(dcb_chi2, xvar.getBins())
      dcb_ndof = int(xvar.getBins() - (1 + 1 + 4))
      dcb_gof_pval = ROOT.TMath.Prob(dcb_chi2,dcb_ndof)
      print(dcb_gof_pval)

      if dcb_gof_pval > gauss_gof_pval:
        dy = dcb
      else:
        dy = gauss
    else:
      dy = gauss

    norm_name = "CMS_hgg_%s_combined_13TeV_bkgshape_norm"%cat
    n_events = float(data.sumEntries())
    bkg_norm = ROOT.RooRealVar(norm_name,norm_name,n_events*bkg_frac.getVal(),0,n_events)
    #dy_norm = ROOT.RooRealVar("bkg"+suffix+"_norm","bkg"+suffix+"_norm",1-bkg_frac.getVal(),0,n_events)

    c = ROOT.TCanvas("canvas", "canvas", 600, 600)
    frame.Draw()
    if not os.path.exists("plots"):
      os.mkdir("plots")
    c.SaveAs("plots/dy_%s.pdf"%cat)

    dy.SetTitle("bkg"+suffix)
    dy.SetName("bkg"+suffix)

    # create and save workspace
    w_control_regions = ROOT.RooWorkspace("w_control_regions", "w_control_regions")

    xvar.setBins(nBinsOutput)
    DataHist = ROOT.RooDataHist("roohist_data_mass_%s"%cat,"data",ROOT.RooArgSet(xvar),data)

    imp = getattr(w_control_regions, "import")

    imp(DataHist)
    imp(bkg)
    imp(bkg_norm)
    imp(dy)
    #imp(dy_norm)
    #w_control_regions.var("CMS_hgg_mass").setBins(nBinsOutput)
    w_control_regions.var("CMS_hgg_mass").Print()
    w_control_regions.writeToFile(f_out)

if __name__=="__main__":
  main(sys.argv[1], sys.argv[2], sys.argv[3])
