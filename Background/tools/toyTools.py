import ROOT

# Function to run fTest and goodness of fit with tools
def probabilityFTestFromToys(_model,pdfInfoNull,pdfInfoTest,_mode='NLL',_outDir=".",nToys=1000,maxTries=3):

  print "\n #################################################################################################"
  print " --> Running F-test check with toys:"
  print "     * Null hypothesis: (%s,%s)"%(pdfInfoNull['family'],pdfInfoNull['order'])
  print "     * Test hypothesis: (%s,%s)\n"%(pdfInfoTest['family'],pdfInfoTest['order'])

  # Calculate observed pval with asymptotic assumption
  dchi2_observed = 2*(pdfInfoNull['NLL']-pdfInfoTest['NLL']) if pdfInfoNull['NLL']>pdfInfoTest['NLL'] else 0
  ndof = pdfInfoTest['order']-pdfInfoNull['order']
  prob_asymptotic = ROOT.TMath.Prob(dchi2_observed,ndof)

  # Extract bestfit and covariance matrix from fit to data
  cov_null, x0_null = _model.getCovariance(pdfInfoNull['pdf'],_mode=_mode)
  cov_test, x0_test = _model.getCovariance(pdfInfoTest['pdf'],_mode=_mode)

  # Store nominal RooDataHist
  DataHist_nominal = _model.DataHist.Clone()

  # Create histogram for chi2 + fit status
  hist_chi2 = ROOT.TH1F("hist_chi2","",60,-2,10)
  hist_status_null = ROOT.TH1F("hist_status_null","",3,-1,2)
  hist_status_test = ROOT.TH1F("hist_status_test","",3,-1,2)

  # Loop over toys
  nToys_success, nToys_pass = 0, 0
  for iToy in range(nToys):
    print " --> Running toy: (%g/%g)"%(iToy,nToys)
    # Reset null pdf vals to nominal
    _model.setFitPdf(pdfInfoNull['pdf'])
    _model.setX0(x0_null)

    # Create binned toy from null pdf and save as model DataHist
    #binnedToy = pdfInfoNull['pdf'].generateBinned(ROOT.RooArgSet(_model.xvar),pdfInfoNull['norm'],0,1)
    binnedToy = pdfInfoTest['pdf'].generateBinned(ROOT.RooArgSet(_model.xvar),pdfInfoTest['norm'],0,1)
    _model.DataHist = binnedToy

    # Fit NULL hypothesis
    status_null = 0
    nTries = 0
    while( status_null == 0 )&( nTries < maxTries ):
      NLL_null, fitStatus = _model.runFit(pdfInfoNull['pdf'],_mode=_mode,_verbose=False)
      status_null = fitStatus.status
      # Randomize fit parameters if status still == 0
      if status_null == 0: _model.setX0( _model.randomX0(x0_null,cov_null) )
      nTries += 1

    # Reset test pdf vals to nominal
    _model.setFitPdf(pdfInfoTest['pdf'])
    _model.setX0(x0_test)

    # Fit higher order (test) hypothesis
    status_test = 0
    nTries = 0
    while( status_test == 0 )&( nTries < maxTries ):
      NLL_test, fitStatus = _model.runFit(pdfInfoTest['pdf'],_mode=_mode,_verbose=False)
      status_test = fitStatus.status
      # Randomize fit parameters if status still == 0
      if status_test == 0: _model.setX0( _model.randomX0(x0_test,cov_test) )
      nTries += 1

    print "    * NLL(%s,%s) = %.4f, NLL(%s,%s) = %.4f"%(pdfInfoNull['family'],pdfInfoNull['order'],NLL_null,pdfInfoTest['family'],pdfInfoTest['order'],NLL_test)

    # Fill status histogram
    hist_status_null.Fill(status_null)
    hist_status_test.Fill(status_test)

    # If fit has been successful for both test and null
    if( status_null )&( status_test ):
      nToys_success += 1
      dchi2_toy = 2*(NLL_null-NLL_test) if _mode == "NLL" else NLL_null-NLL_test
      # If dchi2 is greater than observed chi2 the add to counter
      print "    * Toy fitted successfully: dChi2(toy) = %.4f"%dchi2_toy
      print "    * dChi2(observed) = %.4f"%dchi2_observed
      if dchi2_toy > dchi2_observed: 
        nToys_pass += 1
        print "    * Toy passed pval threshold: dChi2(toy) >= dChi2(observed)"
      else:
        print "    * Toy failed pval threshold: dChi2(toy) < dChi2(observed)"
      hist_chi2.Fill(dchi2_toy)
    else:
      print "    * Toy fit unsuccessful. Will not add to histogram"

  # Calculate prob for toys
  prob = float(nToys_pass)/float(nToys_success) if nToys_success!=0 else 0.

  # Plot histograms
  canv_chi2 = ROOT.TCanvas()
  #canv_chi2.SetLogy()
  # Draw histogram
  hist_chi2.Scale(1./(hist_chi2.GetBinWidth(1)*hist_chi2.Integral()))
  hist_chi2.SetLineColor(4)
  hist_chi2.Draw("HIST")
  # Draw chi2 graph with ndof
  gChi2 = ROOT.TGraph()
  gChi2.SetLineColor(2)
  iPoint = 0
  for iBin in range(0,hist_chi2.GetNbinsX()):
    x = hist_chi2.GetBinCenter(iBin+1)
    if x > 0:
      gChi2.SetPoint(iPoint,x,ROOT.Math.chisquared_pdf(x,ndof))
      iPoint += 1
  gChi2.Draw("L Same")
  # Add line and text
  lData = ROOT.TArrow(dchi2_observed,hist_chi2.GetMaximum(),dchi2_observed,0)
  lData.SetLineWidth(2)
  lData.Draw("Same")
  lat = ROOT.TLatex()
  lat.SetNDC()
  lat.SetTextFont(42)
  lat.DrawLatex(0.1,0.91,"Prob (asymptotic) = %.4f (%.4f)"%(prob,prob_asymptotic))
  # Save canvas
  canv_chi2.SaveAs("%s/fTest_toys_pval_%s_%s_vs_%s_%s.pdf"%(_outDir,pdfInfoNull['family'],pdfInfoNull['order'],pdfInfoTest['family'],pdfInfoTest['order']))
  canv_chi2.SaveAs("%s/fTest_toys_pval_%s_%s_vs_%s_%s.png"%(_outDir,pdfInfoNull['family'],pdfInfoNull['order'],pdfInfoTest['family'],pdfInfoTest['order']))

  # Status histogram
  canv_status = ROOT.TCanvas()
  hist_status_null.SetLineColor(2)
  hist_status_test.SetLineColor(1)
  leg = ROOT.TLegend(0.2,0.6,0.4,0.87)
  leg.SetFillColor(0)
  leg.SetTextFont(42)
  leg.AddEntry(hist_status_null,"Null Hyp: (%s,%s)"%(pdfInfoNull['family'],pdfInfoNull['order']),"L")
  leg.AddEntry(hist_status_test,"Test Hyp: (%s,%s)"%(pdfInfoTest['family'],pdfInfoTest['order']),"L")
  hist_status_null.Draw("HIST")
  hist_status_test.Draw("HIST SAME")
  leg.Draw("SAME")
  canv_status.SaveAs("%s/fTest_toys_status_%s_%s_vs_%s_%s.pdf"%(_outDir,pdfInfoNull['family'],pdfInfoNull['order'],pdfInfoTest['family'],pdfInfoTest['order']))
  canv_status.SaveAs("%s/fTest_toys_status_%s_%s_vs_%s_%s.png"%(_outDir,pdfInfoNull['family'],pdfInfoNull['order'],pdfInfoTest['family'],pdfInfoTest['order']))

  # Re-assign nominal fit parameter values and nominal data hist
  _model.DataHist = DataHist_nominal
  _model.setFitPdf(pdfInfoNull['pdf'])
  _model.setX0(x0_null)
  _model.setFitPdf(pdfInfoTest['pdf'])
  _model.setX0(x0_test)

  # Delete canvas, graphs and histogram
  #canv_status.Delete()
  #canv_chi2.Delete()
  hist_status_null.Delete()
  hist_status_test.Delete()
  hist_chi2.Delete()
  gChi2.Delete()
  leg.Delete()
  lat.Delete()

  print " --> Prob(toys) = %.4f, Prob(Asymptotic) = %.4f"%(prob,prob_asymptotic)
  print "\n #################################################################################################"
  return prob
