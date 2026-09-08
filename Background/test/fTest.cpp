#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <map>

#include "boost/program_options.hpp"
#include "boost/lexical_cast.hpp"
#include <iomanip>
#include "TFile.h"
#include "TMath.h"
#include "TLegend.h"
#include "TCanvas.h"
#include "RooPlot.h"
#include "RooWorkspace.h"
#include "RooDataSet.h"
#include "RooHist.h"
#include "RooAbsData.h"
#include "RooBinning.h"
#include "RooAbsPdf.h"
#include "RooArgSet.h"
#include "RooFitResult.h"
#include "RooMinimizer.h"
#include "RooMsgService.h"
#include "RooDataHist.h"
#include "Roo1DTable.h"

#include "RooExtendPdf.h"
#include "TRandom3.h"
#include "TLatex.h"
#include "TMacro.h"
#include "TH1F.h"
#include "TH1I.h"
#include "TArrow.h"
#include "TKey.h"

#include "RooCategory.h"
#include "HiggsAnalysis/CombinedLimit/interface/RooMultiPdf.h"

#include "../interface/PdfModelBuilder.h"
#include <Math/PdfFuncMathCore.h>
#include <Math/ProbFunc.h>
#include <iomanip>
#include "boost/program_options.hpp"
#include "boost/algorithm/string/split.hpp"
#include "boost/algorithm/string/classification.hpp"
#include "boost/algorithm/string/predicate.hpp"

#include "../../tdrStyle/tdrstyle.C"
#include "../../tdrStyle/CMS_lumi.C"

#include "TColor.h"

const int kLightBrown = TColor::GetColor(205, 133, 63);
const int kDarkOrange = TColor::GetColor(0.5*255, 0.8*255, 0);
using namespace std;
using namespace RooFit;
using namespace boost;

namespace po = program_options;
bool data_by_fit = false;

int data_minus_fit_by_err = 1;

bool BLIND = false;
bool runFtestCheckWithToys=false;
int mgg_low = 500;
int mgg_high = 1000;
int nBinsForPlot = (mgg_high - mgg_low)/20 ; //4*(mgg_high-mgg_low);
int nBinsForMass =  mgg_high - mgg_low;
double binWidth = 1; //(mgg_high - mgg_low)/nBinsForMass;

RooRealVar *intLumi_ = new RooRealVar("IntLumi","hacked int lumi", 1000.);

TRandom3 *RandomGen = new TRandom3();

RooAbsPdf* getPdf(PdfModelBuilder &pdfsModel, string type, int order, const char* ext=""){

  if (type=="Bernstein")
    return pdfsModel.getBernstein(Form("%s_bern%d",ext,order),order);
  else if (type=="Chebychev")
    return pdfsModel.getChebychev(Form("%s_cheb%d",ext,order),order);
  else if (type=="Exponential")
    return pdfsModel.getExponentialSingle(Form("%s_exp%d",ext,order),order);
  else if (type=="PowerLaw")
    return pdfsModel.getPowerLawSingle(Form("%s_pow%d",ext,order),order);
  else if (type=="Laurent")
    return pdfsModel.getLaurentSeries(Form("%s_lau%d",ext,order),order);
  // Adding new functions here
  else if (type=="InvPow"){
    if (order != 1) {
        cerr << "[ERROR] InvPow requires order=1. Provided: " << order << endl;
        return nullptr;
    }
    return pdfsModel.getInvPow(Form("%s_invpow%d",ext,order),order);
  }
  else if (type=="InvPowLin"){
      if (order != 1) {
        cerr << "[ERROR] InvPowLin requires order=1. Provided: " << order << endl;
        return nullptr;
    }
    return pdfsModel.getInvPowLin(Form("%s_invpowlin%d",ext,order),order);
  }
  else if (type=="Expow"){
    if (order != 1) {
        cerr << "[ERROR] Expow requires order=1. Provided: " << order << endl;
        return nullptr;
    }
    return pdfsModel.getExpow(Form("%s_expow%d",ext,order),order);
  }
  else if (type=="Dijet"){
    if (order != 1) {
        cerr << "[ERROR] Dijet requires order=1. Provided: " << order << endl;
        return nullptr;
    }
    return pdfsModel.getDijet(Form("%s_dijet%d",ext,order),order);
  }
  else {
    cerr << "[ERROR] -- getPdf() -- type " << type << " not recognised." << endl;
    return NULL;
  }
}


void runFit(RooAbsPdf *pdf, RooDataSet *data, double *NLL, int *stat_t, int MaxTries){

	int ntries=0;
    //RooRealVar norm("norm", "norm", data->sumEntries(), 0, 1e8);
    //RooExtendPdf *extendedpdf = new RooExtendPdf("extPdf", "Extended PDF", *pdf, norm);
    RooArgSet *params_test = pdf->getParameters((const RooArgSet*)(0));
    std::cout << "params_test: "<<std::endl;
	params_test->Print("v");
	int stat=1;
	double minnll=10e8;
	while (stat!=0){
	  if (ntries>=MaxTries) {
          std::cout << "Ntries exceeded for pdf: " << pdf->GetName() << std::endl;
          break;}
	  RooFitResult *fitTest = pdf->fitTo(*data, RooFit::Save(1), RooFit::Minimizer("Minuit2", "migrad"), RooFit::Strategy(2), RooFit::SumW2Error(kTRUE), RooFit::PrintLevel(-1), RooFit::MaxCalls(100000),  RooFit::Optimize(0));
      stat = fitTest->status();
	  minnll = fitTest->minNll();
      if (stat==0) {std::cout << "Succeeded fit (status " << stat << ") for pdf: " << pdf->GetName() << std::endl;}
      if (stat!=0) {
          params_test->assignValueOnly(fitTest->randomizePars());
          std::cout << "Using Random Parameters now for pdf: " << pdf->GetName() << std::endl;
      }
	  ntries++;
	}
	*stat_t = stat;
	*NLL = minnll;
}

double getProbabilityFtest(double chi2, int ndof, RooAbsPdf *pdfNull, RooAbsPdf *pdfTest, RooRealVar *mass, RooDataSet *data, std::string name){

  double prob_asym = TMath::Prob(chi2,ndof);
  if (!runFtestCheckWithToys) return prob_asym;

  int ndata = data->sumEntries();

  // fit the pdfs to the data and keep this fit Result (for randomizing)
  RooFitResult *fitNullData = pdfNull->fitTo(*data, RooFit::Save(1), RooFit::Minimizer("Minuit2", "minimize"), RooFit::Strategy(2), RooFit::SumW2Error(kTRUE), RooFit::PrintLevel(-1), RooFit::MaxCalls(100000),  RooFit::Optimize(0));
  RooFitResult *fitTestData = pdfTest->fitTo(*data, RooFit::Save(1), RooFit::Minimizer("Minuit2", "minimize"), RooFit::Strategy(2), RooFit::SumW2Error(kTRUE), RooFit::PrintLevel(-1), RooFit::MaxCalls(100000),  RooFit::Optimize(0));

  // Ok we want to check the distribution in toys then
  // Step 1, cache the parameters of each pdf so as not to upset anything
  RooArgSet *params_null = pdfNull->getParameters((const RooArgSet*)(0));
  RooArgSet preParams_null;
  params_null->snapshot(preParams_null);
  RooArgSet *params_test = pdfTest->getParameters((const RooArgSet*)(0));
  RooArgSet preParams_test;
  params_test->snapshot(preParams_test);

  int ntoys =5000;
  TCanvas *can = new TCanvas();
  can->SetLogy();
  TH1F toyhist(Form("toys_fTest_%s.pdf",pdfNull->GetName()),";Chi2;",60,-2,10);
  TH1I toyhistStatN(Form("Status_%s.pdf",pdfNull->GetName()),";FitStatus;",8,-4,4);
  TH1I toyhistStatT(Form("Status_%s.pdf",pdfTest->GetName()),";FitStatus;",8,-4,4);

  TGraph *gChi2 = new TGraph();
  gChi2->SetLineColor(kGreen+2);
  double w = toyhist.GetBinWidth(1);

  int ipoint=0;

  for (int b=0;b<toyhist.GetNbinsX();b++){
	double x = toyhist.GetBinCenter(b+1);
	if (x>0){
	  gChi2->SetPoint(ipoint,x,(ROOT::Math::chisquared_pdf(x,ndof)));
	  ipoint++;
	}
  }

  int npass =0; int nsuccesst =0;
  mass->setBins(nBinsForMass);
  mass->setBins(10000,"cache");

  for (int itoy = 0 ; itoy < ntoys ; itoy++){
    params_null->assignValueOnly(preParams_null);
    params_test->assignValueOnly(preParams_test);
  	RooDataHist *binnedtoy = pdfNull->generateBinned(RooArgSet(*mass),ndata,0,1);

    int stat_n=1;
    int stat_t=1;
    int ntries = 0;
    double nllNull,nllTest;
    // Iterate on the fit
    int MaxTries = 2;
    while (stat_n!=0){
      if (ntries>=MaxTries) break;
	  RooFitResult *fitNull = pdfNull->fitTo(*binnedtoy,RooFit::Save(1),RooFit::Strategy(2),RooFit::SumW2Error(kTRUE) //FIXME
		,RooFit::Minimizer("Minuit2","minimize"),RooFit::Minos(0),RooFit::Hesse(0),RooFit::PrintLevel(-1), RooFit::MaxCalls(100000) );
		//,RooFit::Optimize(0));

      nllNull = fitNull->minNll();
      stat_n = fitNull->status();
      if (stat_n!=0) params_null->assignValueOnly(fitNullData->randomizePars());
      ntries++;
    }

    ntries = 0;
    while (stat_t!=0){
      if (ntries>=MaxTries) break;
	  RooFitResult *fitTest = pdfTest->fitTo(*binnedtoy,RooFit::Save(1),RooFit::Strategy(2),RooFit::SumW2Error(kTRUE) //FIXME
		,RooFit::Minimizer("Minuit2","minimize"),RooFit::Minos(0),RooFit::Hesse(0),RooFit::PrintLevel(-1), RooFit::MaxCalls(100000),  RooFit::Optimize(0));
        nllTest = fitTest->minNll();
      stat_t = fitTest->status();
      if (stat_t!=0) params_test->assignValueOnly(fitTestData->randomizePars());
      ntries++;
    }

    toyhistStatN.Fill(stat_n);
    toyhistStatT.Fill(stat_t);

    if (stat_t !=0 || stat_n !=0) continue;
    nsuccesst++;
    double chi2_t = 2*(nllNull-nllTest);
    if (chi2_t >= chi2) npass++;
    toyhist.Fill(chi2_t);
  }

  double prob=0;
  if (nsuccesst!=0)  prob = (double)npass / nsuccesst;
  toyhist.Scale(1./(w*toyhist.Integral()));
  toyhist.Draw();
  TArrow lData(chi2,toyhist.GetMaximum(),chi2,0);
  lData.SetLineWidth(2);
  lData.Draw();
  gChi2->Draw("L");
  TLatex *lat = new TLatex();
  lat->SetNDC();
  lat->SetTextFont(42);
  lat->DrawLatex(0.1,0.91,Form("Prob (asymptotic) = %.4f (%.4f)",prob,prob_asym));
  can->SaveAs(name.c_str());

  TCanvas *stas =new TCanvas();
  toyhistStatN.SetLineColor(2);
  toyhistStatT.SetLineColor(1);
  TLegend *leg = new TLegend(0.2,0.6,0.4,0.87); leg->SetFillColor(0);
  leg->SetTextFont(42);
  leg->AddEntry(&toyhistStatN,"Null Hyp","L");
  leg->AddEntry(&toyhistStatT,"Test Hyp","L");
  toyhistStatN.Draw();
  toyhistStatT.Draw("same");
  leg->Draw();
  stas->SaveAs(Form("%s_fitstatus.pdf",name.c_str()));
  //reassign params
  params_null->assignValueOnly(preParams_null);
  params_test->assignValueOnly(preParams_test);

  delete can; delete stas;
  delete gChi2;
  delete leg;
  delete lat;

  // Still return the asymptotic prob (usually its close to the toys one)
  return prob_asym;
}

double getGoodnessOfFit(RooRealVar *mass, RooAbsPdf *mpdf, RooDataSet *data, std::string name,double binWidth){

  double prob;
  int ntoys = 500;
  // Routine to calculate the goodness of fit.
  name+="_gofTest.pdf";
  RooRealVar norm("norm","norm",data->sumEntries(),0,10E8);
  //norm.removeRange();

  RooExtendPdf *pdf = new RooExtendPdf("ext","ext",*mpdf,norm);

  // get The Chi2 value from the data
  RooPlot *plot_chi2 = mass->frame();
  data->plotOn(plot_chi2,Binning(nBinsForMass),Name("data"));

  pdf->plotOn(plot_chi2,Name("pdf"));
  int np = pdf->getParameters(*data)->getSize();

  double chi2 = plot_chi2->chiSquare("pdf","data",np)/binWidth;
  std::cout << "[INFO] Calculating GOF for pdf " << pdf->GetName() << ", using " <<np << " fitted parameters" <<std::endl;

  // The first thing is to check if the number of entries in any bin is < 5
  // if so, we don't rely on asymptotic approximations
  TH1* histCheck = data->createHistogram("hcheck", *mass, Binning(nBinsForMass));
  bool lowStatBinFound = false;
  for (int i = 1; i <= histCheck->GetNbinsX(); ++i) {
      if (histCheck->GetBinContent(i) < 5) {
          lowStatBinFound = true;
          break;
      }
  }
  if (lowStatBinFound) {
  //if ((double)data->sumEntries()/nBinsForMass < 5 ){
    std::cout << "[INFO] Running toys for GOF test " << std::endl;
    // store pre-fit params
    RooArgSet *params = pdf->getParameters(*data);
    RooArgSet preParams;
    params->snapshot(preParams);
    int ndata = data->sumEntries();

    int npass =0;
    std::vector<double> toy_chi2;
    for (int itoy = 0 ; itoy < ntoys ; itoy++){
    //  std::cout << "[INFO] " <<Form("\t.. %.1f %% complete\r",100*float(itoy)/ntoys) << std::flush;
      params->assignValueOnly(preParams);
      int nToyEvents = RandomGen->Poisson(ndata);
      RooDataHist *binnedtoy = pdf->generateBinned(RooArgSet(*mass),nToyEvents,0,1);
      pdf->fitTo(*binnedtoy,RooFit::Minimizer("Minuit2","minimize"),RooFit::Minos(0),RooFit::Hesse(0),RooFit::PrintLevel(-1),RooFit::Strategy(2),RooFit::SumW2Error(kTRUE), RooFit::MaxCalls(100000) ); //FIXME

      RooPlot *plot_t = mass->frame();
      binnedtoy->plotOn(plot_t);
      pdf->plotOn(plot_t);//,RooFit::NormRange("fitdata_1,fitdata_2"));

      double chi2_t = plot_t->chiSquare(np);
      if( chi2_t>=chi2) npass++;
      toy_chi2.push_back(chi2_t*(nBinsForMass-np));
      delete plot_t;
    }
    std::cout << "[INFO] complete" << std::endl;
    prob = (double)npass / ntoys;

    TCanvas *can = new TCanvas();
    double medianChi2 = toy_chi2[(int)(((float)ntoys)/2)];
    double rms = TMath::Sqrt(medianChi2);

    TH1F toyhist(Form("gofTest_%s.pdf",pdf->GetName()),";Chi2;",50,medianChi2-5*rms,medianChi2+5*rms);
    for (std::vector<double>::iterator itx = toy_chi2.begin();itx!=toy_chi2.end();itx++){
      toyhist.Fill((*itx));
    }
    toyhist.Draw();

    TArrow lData(chi2*(nBinsForMass-np),toyhist.GetMaximum(),chi2*(nBinsForMass-np),0);
    lData.SetLineWidth(2);
    lData.Draw();
    can->SaveAs(name.c_str());

    // back to best fit
    params->assignValueOnly(preParams);
  } else {
    prob = TMath::Prob(chi2*(nBinsForMass-np),nBinsForMass-np);
  }
  std::cout << "[INFO] Reduced Chi2 in Observed =  " << chi2 << std::endl;
  std::cout << "[INFO] p-value  =  " << prob << std::endl;
  delete pdf;
  return prob;

}

void plot(RooRealVar *mass, RooAbsPdf *pdf, RooDataSet *data, string name,vector<string> flashggCats_, int status, double *prob, double binWidth, double NLL){
  /*
  for plotting single pdf fit plots
  but with an additional subplot plotting
  the ratio of data/fit, and error bars
  error_data/fit between range 0.95 to 1.05
  indicating an error range of +/- 5%
  */

  RooPlot *plot_chi2 = mass->frame();
  data->plotOn(plot_chi2,Binning(nBinsForMass));

  pdf->plotOn(plot_chi2);

  int np = pdf->getParameters(*data)->getSize() + 1; //using the same np as if it was an extend pdf
  double chi2 = plot_chi2->chiSquare(np);

  *prob = getGoodnessOfFit(mass,pdf,data,name, binWidth);
  RooPlot *plot = mass->frame();
  mass->setRange("unblindReg_1",mgg_low,115);
  mass->setRange("unblindReg_2",135,mgg_high);
  if (BLIND) {
    data->plotOn(plot,Binning(nBinsForPlot),CutRange("unblindReg_1"));
    data->plotOn(plot,Binning(nBinsForPlot),CutRange("unblindReg_2"));
    data->plotOn(plot,Binning(nBinsForPlot),Invisible());
    // data->plotOn(plot,Binning(mgg_high-mgg_low),CutRange("unblindReg_1"));
    // data->plotOn(plot,Binning(mgg_high-mgg_low),CutRange("unblindReg_2"));
    // data->plotOn(plot,Binning(mgg_high-mgg_low),Invisible());
    //ta->plotOn(plot,Binning(nBinsForMass),CutRange("unblindReg_1"));
    //ta->plotOn(plot,Binning(nBinsForMass),CutRange("unblindReg_2"));
    //ta->plotOn(plot,Binning(nBinsForMass),Invisible());
  }
  else data->plotOn(plot,Binning(nBinsForPlot));
 // data->plotOn(plot,Binning(mgg_high-mgg_low));

  TCanvas *canv = new TCanvas();
  RooHist *plotdata = (RooHist*)plot->getObject(plot->numItems()-1);
  TPad *pad1 = new TPad("pad1","pad1",0,0.25,1,1);
  TPad *pad2 = new TPad("pad2","pad2",0,0,1,0.35);
  pad1->SetBottomMargin(0.18);
  pad1->SetTopMargin(0.14);     // Increase top margin
  pad1->SetLeftMargin(0.12);    // Increase left margin

  pad2->SetTopMargin(0.08);
  pad2->SetBottomMargin(0.30);
  pad2->SetLeftMargin(0.12);

  pad1->Draw();
  pad2->Draw();
  pad1->cd();
  pdf->plotOn(plot);//,RooFit::NormRange("fitdata_1,fitdata_2"));
  pdf->paramOn(plot,RooFit::Layout(0.4,0.96,0.84),RooFit::Format("NEF",AutoPrecision(6)));
  plot->getAttText()->SetTextSize(0.025);
  if (BLIND) plot->SetMinimum(0.0001);
  //plot->GetYaxis()->SetTitleOffset(1);  // Increase space between y-axis and title
  plot->SetTitle("");                     // Already present
  plot->Draw();

  /// Start ratio and weighted-bin-center plots ///
  TH1D* hFineData = (TH1D*) data->createHistogram("hFineData", *mass, Binning(nBinsForMass, mgg_low, mgg_high));
  TH1D* hbplottmp = (TH1D*) pdf->createHistogram("hbplottmp", *mass, Binning(nBinsForPlot, mgg_low, mgg_high));
  hbplottmp->Scale(plotdata->Integral());

  int npoints = plotdata->GetN();

  RooCurve *nomBkgCurve = (RooCurve*)plot->getObject(plot->numItems() - 2);
  TGraphAsymmErrors *hdatasub = new TGraphAsymmErrors(npoints);
  // TGraphAsymmErrors *gModifiedData = new TGraphAsymmErrors(npoints); // to plot on pad1 at mean mass positions

  int point = 0;
  for (int ibin = 0; ibin < nBinsForPlot; ++ibin) {
    double binLow = mgg_low + ibin * (mgg_high - mgg_low) / nBinsForPlot;
    double binHigh = binLow + (mgg_high - mgg_low) / nBinsForPlot;

    double totalContent = 0.;
    double weightedSum = 0.;
    int fineBinLow = hFineData->FindBin(binLow);
    int fineBinHigh = hFineData->FindBin(binHigh) - 1;

    for (int j = fineBinLow; j <= fineBinHigh; ++j) {
      double binCenter = hFineData->GetBinCenter(j);
      double binContent = hFineData->GetBinContent(j);
      weightedSum += binCenter * binContent;
      totalContent += binContent;
    }

    if (totalContent <= 0) continue;
    double meanMass = weightedSum / totalContent;

    double xtmp, ytmp, errhi, errlow;
    plotdata->GetPoint(ibin, xtmp, ytmp);
    errhi = plotdata->GetErrorYhigh(ibin);
    errlow = plotdata->GetErrorYlow(ibin);

    if (BLIND && (meanMass > 115 && meanMass < 135)) continue;
    double bkgval = nomBkgCurve->interpolate(meanMass);
    if (bkgval <= 0) continue;

    if (data_by_fit==true){
    double rel_err_low = errlow / bkgval;
    double rel_err_high = errhi / bkgval;

    hdatasub->SetPoint(point, meanMass, ytmp / bkgval);
    hdatasub->SetPointError(point, 0., 0., rel_err_low, rel_err_high);

    // gModifiedData->SetPoint(point, meanMass, ytmp);
    // gModifiedData->SetPointError(point, 0., 0., errlow, errhi);
    }
    else if (data_minus_fit_by_err==1){
        // Choose the error pointing towards the background fit
        double pull_err = (ytmp >= bkgval) ? errlow : errhi;
        if (pull_err <= 0) pull_err = 1.0; // Protection against empty/zero-error bins

        // Set the normalized point: (data - fit) / error
        hdatasub->SetPoint(point, meanMass, (ytmp - bkgval) / pull_err);
        
        // Normalize the error bars as well
        hdatasub->SetPointError(point, 0., 0., errlow / pull_err, errhi / pull_err);
    }
    else{
    hdatasub->SetPoint(point, meanMass, ytmp - bkgval);
    hdatasub->SetPointError(point, 0., 0., errlow, errhi);

    // gModifiedData->SetPoint(point, meanMass, ytmp);
    // gModifiedData->SetPointError(point, 0., 0., errlow, errhi);
    }
    point++;
  }

  // gModifiedData->SetMarkerStyle(20);
  // gModifiedData->SetMarkerSize(1.0);
  // gModifiedData->SetLineWidth(1);
  // gModifiedData->Draw("PESAME");


  TLatex *lat = new TLatex();
  lat->SetNDC();
  lat->SetTextFont(42);  // Standard font (bold=62)
  lat->SetTextSize(0.04); // Increased from default 0.03
  lat->SetTextColor(kBlack);
  lat->SetTextAlign(31);
  lat->DrawLatex(0.973, 0.88, Form("#chi^{2}/ndof = %.3f | Prob = %.2f | NLL = %.1f | Status = %d", chi2, *prob, NLL, status));

  pad2->cd();
  TH1 *hdummy = new TH1D("hdummyweight", "", nBinsForPlot, mgg_low, mgg_high);
  if (data_by_fit == true) {
      hdummy->GetYaxis()->SetTitle("data/(best fit)");
      hdummy->SetMaximum(1.05);
      hdummy->SetMinimum(0.95);
 }
 else if(data_minus_fit_by_err==1){
      hdummy->GetYaxis()->SetTitle("(data - best_fit)/#sigma");
      hdummy->SetMaximum(5.0);  // Standard pull plot range
      hdummy->SetMinimum(-5.0);
 }
 
 else{
      hdummy->GetYaxis()->SetTitle("data - best_fit");
      hdummy->SetMaximum(hdatasub->GetHistogram()->GetMaximum()+1);
      hdummy->SetMinimum(hdatasub->GetHistogram()->GetMinimum()-1);
  }

  hdummy->GetYaxis()->SetTitleSize(0.09);
  hdummy->GetYaxis()->SetLabelSize(0.07);
  hdummy->GetYaxis()->SetTitleOffset(0.6);
  hdummy->GetXaxis()->SetTitle("m_{#gamma#gamma} [GeV]");
  hdummy->GetXaxis()->SetTitleSize(0.12);
  hdummy->GetXaxis()->SetLabelSize(0.08);
  hdummy->Draw("HIST");
  hdummy->GetYaxis()->SetNdivisions(808);

  if (data_by_fit == true) {
      TLine *line3 = new TLine(mgg_low, 1., mgg_high, 1.);
   line3->SetLineColor(kBlue);
  line3->SetLineWidth(5);
  line3->Draw();
  }
  else if(data_minus_fit_by_err==1){
      TLine *line3 = new TLine(mgg_low, 0., mgg_high, 0.);
      line3->SetLineColor(kBlue);
      line3->SetLineWidth(5);
      line3->Draw();

  }
  else {
      TLine *line3 = new TLine(mgg_low, 0., mgg_high, 0.);
       line3->SetLineColor(kBlue);
  line3->SetLineWidth(5);
  line3->Draw();
  }

  hdatasub->SetMarkerSize(1);
  hdatasub->Draw("PESAME");

  canv->SaveAs(Form("%s.pdf", name.c_str()));

  delete canv;
  delete lat;
}

void plot(RooRealVar *mass, RooMultiPdf *pdfs, RooCategory *catIndex, RooDataSet *data, string name, vector<string> flashggCats_, int cat, const std::vector<double>& nll_values, int bestFitPdf=-1){
  // multipdf plotting function
  int color[11] = { kOrange+2, kRed, kGreen+2, kMagenta, kGray, kOrange+7, kCyan, kOrange-3, kViolet, kSpring+2,  kBlue};
  TLegend *leg = new TLegend(0.5,0.4,0.95,0.85);

  leg->SetFillColor(0);
  leg->SetLineColor(1);
  RooPlot *plot = mass->frame();

  mass->setRange("unblindReg_1",mgg_low,115);
  mass->setRange("unblindReg_2",135,mgg_high);
  if (BLIND) {
    data->plotOn(plot,Binning(nBinsForPlot),CutRange("unblindReg_1"), RooFit::MarkerSize(1.5));
    data->plotOn(plot,Binning(nBinsForPlot),CutRange("unblindReg_2"), RooFit::MarkerSize(1.5));
    data->plotOn(plot,Binning(nBinsForPlot),Invisible());
    //ta->plotOn(plot,Binning(mgg_high-mgg_low),CutRange("unblindReg_1"));
    //ta->plotOn(plot,Binning(mgg_high-mgg_low),CutRange("unblindReg_2"));
    //ta->plotOn(plot,Binning(mgg_high-mgg_low),Invisible());
    // data->plotOn(plot,Binning(nBinsForMass),CutRange("unblindReg_1"));
    // data->plotOn(plot,Binning(nBinsForMass),CutRange("unblindReg_2"));
    // data->pln(plot,Binning(nBinsForMass),Invisible());
  }
  else data->plotOn(plot,Binning(nBinsForPlot), RooFit::MarkerSize(1.5));
  TCanvas *canv = new TCanvas();
  ///start extra bit for ratio plot///
  RooHist *plotdata = (RooHist*)plot->getObject(plot->numItems()-1);
  // bool doRatioPlot_=1;
  TPad *pad1 = new TPad("pad1","pad1",0,0.25,1,1);
  TPad *pad2 = new TPad("pad2","pad2",0,0,1,0.35);
  pad1->SetBottomMargin(0.18);
  pad1->SetTopMargin(0.14);     // Increase top margin
  pad1->SetLeftMargin(0.16);    // Increase left margin

  pad2->SetTopMargin(0.08);
  pad2->SetBottomMargin(0.30);
  pad2->SetLeftMargin(0.16);


  pad1->Draw();
  pad2->Draw();
  pad1->cd();
  // end extra bit for ratio plot///

  int currentIndex = catIndex->getIndex();
  TObject *datLeg = plot->getObject(int(plot->numItems()-1));
  leg->AddEntry(datLeg,Form("Data - %s",flashggCats_[cat].c_str()),"LEP");
  int style=1;
  RooAbsPdf *pdf;
  RooCurve *nomBkgCurve;
  int bestcol= -1;
  for (int icat=0;icat<catIndex->numTypes();icat++){
    int col;
    if (icat<=10) col=color[icat];
    else {col=kBlack; style++;}
    catIndex->setIndex(icat);
    RooAbsPdf* basepdf = pdfs->getCurrentPdf();
    //RooRealVar norm(Form("norm_cat%d_func%d", cat, icat), "norm", data->sumEntries(), 0, 1e8);
    //RooExtendPdf extended(Form("ext_%s", basepdf->GetName()), "", *basepdf, norm);

    basepdf->fitTo(*data, RooFit::Minimizer("Minuit2", "migrad"), RooFit::Strategy(2), RooFit::SumW2Error(kTRUE), RooFit::PrintLevel(-1), RooFit::MaxCalls(100000),  RooFit::Optimize(0));

    basepdf->plotOn(plot,LineColor(col),LineStyle(style), LineStyle(style));//, Normalization(data->sumEntries() * binWidth, RooAbsReal::NumEvent));//,RooFit::NormRange("fitdata_1,fitdata_2"));
    TObject *pdfLeg = plot->getObject(int(plot->numItems()-1));
    std::string ext = "";
    if (bestFitPdf==icat) {
    ext=" (Best Fit Pdf) ";
    pdf= pdfs->getCurrentPdf();
    nomBkgCurve = (RooCurve*)plot->getObject(plot->numItems()-1);
    bestcol = col;
    }
    //Calculating reduced chi square for adding in legends
    RooPlot *plot_chi2 = mass->frame();
    data->plotOn(plot_chi2,Binning(nBinsForMass));
    basepdf->plotOn(plot_chi2);
    int np = basepdf->getParameters(*data)->getSize() + 1; //using the same np as if it was an extend pdf
    double chi2 = plot_chi2->chiSquare(np);
    double nll_display = (icat < nll_values.size()) ? nll_values[icat] : -1.0;
    leg->AddEntry(pdfLeg,Form("%s%s(%.2f, %.1f)", pdfs->getCurrentPdf()->GetName(), ext.c_str(), chi2, nll_display), "L");

    // leg->AddEntry(pdfLeg,Form("%s%s(%.2f)",pdfs->getCurrentPdf()->GetName(),ext.c_str(),chi2),"L");}
  }
  // plot->SetTitle(Form("Category %s",flashggCats_[cat].c_str()));
  if (BLIND) plot->SetMinimum(0.0001);
  plot->Draw();
  // plot->GetYaxis()->SetTitle("Events / bin size [GeV^{ -1 }]");
  plot->GetYaxis()->SetNoExponent(kTRUE);
  plot->GetYaxis()->SetTitleOffset(2);
  leg->Draw("same");
  CMS_lumi( canv, 2022, 0);  // second argument is iperiod
  ///start extra bit for ratio plot///
  // TH1D *hbplottmp = (TH1D*) pdf->createHistogram("hbplottmp",*mass,Binning(mgg_high-mgg_low,mgg_low,mgg_high));
  TH1D *hbplottmp = (TH1D*) pdf->createHistogram("hbplottmp",*mass,Binning(nBinsForPlot,mgg_low,mgg_high));
  hbplottmp->Scale(plotdata->Integral());
  hbplottmp->Draw("same");

  int npoints = plotdata->GetN();
  double xtmp,ytmp;//
  int point =0;
  TGraphAsymmErrors *hdatasub = new TGraphAsymmErrors(npoints);
  //hdatasub->SetMarkerSize(defmarkersize);
  for (int ipoint=0; ipoint<npoints; ++ipoint) {
  //double bkgval = hbplottmp->GetBinContent(ipoint+1);
  plotdata->GetPoint(ipoint, xtmp,ytmp);
  double bkgval = nomBkgCurve->interpolate(xtmp);
  if (BLIND) {
   if ((xtmp > 115 ) && ( xtmp < 135) ) continue;
  }
  double errhi = plotdata->GetErrorYhigh(ipoint);
  double errlow = plotdata->GetErrorYlow(ipoint);
  if (data_by_fit == true) {
    double rel_err_low = errlow/bkgval;
    double rel_err_high = errhi/bkgval;
    hdatasub->SetPoint(point,xtmp,ytmp/bkgval);
    hdatasub->SetPointError(point,0.,0.,rel_err_low,rel_err_high );
  }
  else if(data_minus_fit_by_err==1){
        // Choose the error pointing towards the background fit
        double pull_err = (ytmp >= bkgval) ? errlow : errhi;
        if (pull_err <= 0) pull_err = 1.0; // Protection against empty/zero-error bins

        // Set the normalized point: (data - fit) / error
        hdatasub->SetPoint(point, xtmp, (ytmp - bkgval) / pull_err);
        
        // Normalize the error bars as well
        hdatasub->SetPointError(point, 0., 0., errlow / pull_err, errhi / pull_err);
  }
  else {
      hdatasub->SetPoint(point,xtmp,ytmp - bkgval);
      hdatasub->SetPointError(point,0.,0.,errlow,errhi );
  }


  bool drawZeroBins_ =1;
  if (!drawZeroBins_) if(fabs(ytmp)<1e-5) continue;
  point++;
  }
  pad2->cd();
  //TH1 *hdummy = new TH1D("hdummyweight","",mgg_high-mgg_low,mgg_low,mgg_high);
  TH1 *hdummy = new TH1D("hdummyweight","",nBinsForPlot,mgg_low,mgg_high);

  if (data_by_fit == true) {
      hdummy->GetYaxis()->SetTitle("data/(best fit)");
      hdummy->SetMaximum(1.05);
      hdummy->SetMinimum(0.95);
  }
  else if(data_minus_fit_by_err==1){
      hdummy->GetYaxis()->SetTitle("(data - best_fit)/#sigma");
      hdummy->SetMaximum(5.0);  // Standard pull plot range
      hdummy->SetMinimum(-5.0);
  }
  else {
      hdummy->GetYaxis()->SetTitle("data - best_fit");
      hdummy->SetMaximum(hdatasub->GetHistogram()->GetMaximum()+1);
      hdummy->SetMinimum(hdatasub->GetHistogram()->GetMinimum()-1);
  }

  hdummy->GetYaxis()->SetTitleSize(0.09);
  hdummy->GetYaxis()->SetLabelSize(0.07);
  hdummy->GetYaxis()->SetTitleOffset(0.6);
  hdummy->GetXaxis()->SetTitle("m_{#gamma#gamma} [GeV]");
  hdummy->GetXaxis()->SetTitleSize(0.12);
  hdummy->GetXaxis()->SetLabelSize(0.08);
  hdummy->Draw("HIST");
  hdummy->GetYaxis()->SetNdivisions(808);

    if (data_by_fit == true) {
      TLine *line3 = new TLine(mgg_low, 1., mgg_high, 1.);
   line3->SetLineColor(bestcol);
  line3->SetLineWidth(5);
  line3->Draw();
  }
  else if(data_minus_fit_by_err==1){
      TLine *line3 = new TLine(mgg_low, 0., mgg_high, 0.);
      line3->SetLineColor(bestcol);
      line3->SetLineWidth(5);
      line3->Draw();

  }
  else {
      TLine *line3 = new TLine(mgg_low, 0., mgg_high, 0.);
       line3->SetLineColor(bestcol);
  line3->SetLineWidth(5);
  line3->Draw();
  }

  hdatasub->SetMarkerSize(1.5);
  hdatasub->Draw("PESAME");
  // end extra bit for ratio plot///
  canv->SaveAs(Form("%s.pdf",name.c_str()));
  canv->SaveAs(Form("%s.png",name.c_str()));

  catIndex->setIndex(currentIndex);
  delete canv;
}

void plot(RooRealVar *mass, map<string,RooAbsPdf*> pdfs, RooDataSet *data, string name, vector<string> flashggCats_, int cat, int bestFitPdf=-1){
  // Truth plot function
  int color[8] = { kBlue, kRed, kGreen+2, kMagenta, kGray, kOrange, kCyan, kLightBrown};
  TCanvas *canv = new TCanvas();
  canv->SetLeftMargin(0.2);   // Increase left margin
  canv->SetRightMargin(0.05);   // Increase right margin
  canv->SetTopMargin(0.1);

  TLegend *leg = new TLegend(0.6,0.65,0.88,0.88);
  leg->SetFillColor(0);
  leg->SetLineColor(0);
  RooPlot *plot = mass->frame();
  if (!plot) {
    cerr << "[FATAL] Failed to create mass frame for plotting!" << endl;
    return;
  }

  mass->setRange("unblindReg_1",mgg_low,115);
  mass->setRange("unblindReg_2",135,mgg_high);
  if (!data || data->numEntries() == 0) {
    cerr << "[FATAL] Dataset is null or empty!" << endl;
    return;
  }
  if (BLIND) {
    data->plotOn(plot,Binning(nBinsForPlot),CutRange("unblindReg_1"), RooFit::MarkerSize(2));
    data->plotOn(plot,Binning(nBinsForPlot),CutRange("unblindReg_2"), RooFit::MarkerSize(2));
    data->plotOn(plot,Binning(nBinsForPlot),Invisible());
    //ta->plotOn(plot,Binning(mgg_high-mgg_low),CutRange("unblindReg_1"));
    //ta->plotOn(plot,Binning(mgg_high-mgg_low),CutRange("unblindReg_2"));
    //ta->plotOn(plot,Binning(mgg_high-mgg_low),Invisible());
    //ta->plotOn(plot,Binning(nBinsForMass),CutRange("unblindReg_1"));
    //ta->plotOn(plot,Binning(nBinsForMass),CutRange("unblindReg_2"));
    //ta->plotOn(plot,Binning(nBinsForMass),Invisible());
  }
  //se data->plotOn(plot,Binning(nBinsForMass));
  else data->plotOn(plot,Binning(nBinsForPlot), RooFit::MarkerSize(2));

  TObject *datLeg = plot->getObject(int(plot->numItems()-1));
	if(flashggCats_.size() >0){
  leg->AddEntry(datLeg,Form("Data - %s",flashggCats_[cat].c_str()),"LEP");
	} else {
  leg->AddEntry(datLeg,Form("Data - %d",cat),"LEP");
	}
  int i=0;
  int style=1;
  for (map<string,RooAbsPdf*>::iterator it=pdfs.begin(); it!=pdfs.end(); it++){
    int col;
    if (i<=7) col=color[i];
    else {col=kBlack; style++;}
    if (!it->second) {
        cerr << "[ERROR] PDF " << it->first << " is null! Skipping plot." << endl;
        continue;
    }
    it->second->plotOn(plot,LineColor(col),LineStyle(style));//, Normalization(data->sumEntries() * binWidth, RooAbsReal::NumEvent));//,RooFit::NormRange("fitdata_1,fitdata_2"));
    TObject *pdfLeg = plot->getObject(int(plot->numItems()-1));
    std::string ext = "";
    if (bestFitPdf==i) ext=" (Best Fit Pdf)";
    leg->AddEntry(pdfLeg,Form("%s%s",it->first.c_str(),ext.c_str()),"L");
    i++;
  }
  plot->SetTitle(Form(" %s",flashggCats_[cat].c_str()));
  // plot->GetYaxis()->SetTitle("Events / bin size [GeV^{ -1 }]");
  plot->GetXaxis()->SetTitle("m_{#gamma#gamma} [GeV]");
  if (BLIND) plot->SetMinimum(0.0001);
  plot->Draw();
  plot->GetYaxis()->SetNoExponent(kTRUE);
  plot->GetYaxis()->SetTitleOffset(2.4);

  leg->Draw("same");
  CMS_lumi( canv, 2022, 0);

  canv->SaveAs(Form("%s.pdf",name.c_str()));
  canv->SaveAs(Form("%s.png",name.c_str()));

  delete canv;
}

void transferMacros(TFile *inFile, TFile *outFile){

  TIter next(inFile->GetListOfKeys());
  TKey *key;
  while ((key = (TKey*)next())){
    if (string(key->ReadObj()->ClassName())=="TMacro") {
      //cout << key->ReadObj()->ClassName() << " : " << key->GetName() << endl;
      TMacro *macro = (TMacro*)inFile->Get(key->GetName());
      outFile->cd();
      macro->Write();
    }
  }
}
int getBestFitFunction(RooMultiPdf *bkg, RooDataSet *data, RooCategory *cat, std::vector<double> &nll_values, bool silent=false){


	double global_minNll = 1E10;
	int best_index = 0;
	int number_of_indices = cat->numTypes();

	RooArgSet snap,clean;
	RooArgSet *params = bkg->getParameters((const RooArgSet*)0);
	params->remove(*cat);
	params->snapshot(snap);
	params->snapshot(clean);
	if (!silent) {
		//params->Print("V");
	}

	//bkg->setDirtyInhibit(1);
	//RooAbsReal *nllm = bkg->createNLL(*data);
	//RooMinimizer minim(*nllm);
	//minim.setStrategy(1);

    nll_values.clear();
    nll_values.reserve(number_of_indices);

	for (int id=0;id<number_of_indices;id++){
		params->assignValueOnly(clean);
		cat->setIndex(id);

		//RooAbsReal *nllm = bkg->getCurrentPdf()->createNLL(*data);

		if (!silent) {
			/*
			std::cout << "BEFORE  MAKING FIT" << std::endl;
			params->Print("V");
			std::cout << "-----------------------" << std::endl;
			*/
		}

		//minim.minimize("Minuit2","minimize");
		double minNll=0; //(nllm->getVal())+bkg->getCorrection();
		int fitStatus=1;
		runFit(bkg->getCurrentPdf(),data,&minNll,&fitStatus,/*max iterations*/10);
		// Add the penalty

		minNll=minNll+bkg->getCorrection();
        nll_values.push_back(minNll);
		if (!silent) {
			/*
			std::cout << "After Minimization ------------------  " <<std::endl;
			std::cout << bkg->getCurrentPdf()->GetName() << " " << minNll <<std::endl;
			bkg->Print("v");
			bkg->getCurrentPdf()->getParameters(*data)->Print("V");
			std::cout << " ------------------------------------  " << std::endl;

			params->Print("V");
			*/
			std::cout << "[INFO] AFTER FITTING" << std::endl;
			std::cout << "[INFO] Function was " << bkg->getCurrentPdf()->GetName() <<std::endl;
			std::cout << "[INFO] Correction Applied is " << bkg->getCorrection() <<std::endl;
			std::ios oldState(nullptr);
            oldState.copyfmt(std::cout);

            // Set precision temporarily
            std::cout << std::fixed << std::setprecision(6);
            std::cout << "[INFO] NLL + c = " << minNll << std::endl;

            // Restore original formatting
            std::cout.copyfmt(oldState);
			std::cout << "-----------------------" << std::endl;
		}

		if (minNll <= global_minNll){
        		global_minNll = minNll;
			snap.assignValueOnly(*params);
        		best_index=id;
		}
	}
    	cat->setIndex(best_index);
	params->assignValueOnly(snap);

	if (!silent) {
		std::cout << "[INFO] Best fit Function -- " << bkg->getCurrentPdf()->GetName() << " " << cat->getIndex() <<std::endl;
		//bkg->getCurrentPdf()->getParameters(*data)->Print("v");
	}
	return best_index;
}


int main(int argc, char* argv[]){
setTDRStyle();
writeExtraText = true;       // if extra text
extraText  = "Work in Progress";//"Preliminary";  // default extra text is "Preliminary"
lumi_8TeV  = "19.1 fb^{-1}"; // default is "19.7 fb^{-1}"
lumi_7TeV  = "4.9 fb^{-1}";  // default is "5.1 fb^{-1}"
lumi_13p6TeV = "34.74 fb^{-1}";
// lumi_sqrtS = "13.6 TeV";       // used with iPeriod = 0, e.g. for simulation-only plots (default is an empty string)
lumi_sqrtS = "13 TeV";
string year_ = "2022";
//int year_ = 2017;
double binWidth = 1; // (mgg_high - mgg_low) / nBinsForMass;

string fileName;
int ncats;
int singleCategory;
int catOffset;
string datfile;
string outDir;
string outfilename;
bool is2011=false;
bool verbose=false;
bool saveMultiPdf=false;
int isFlashgg_ =1;
string flashggCatsStr_;
vector<string> flashggCats_;
bool isData_ =0;

po::options_description desc("Allowed options");
desc.add_options()
  ("help,h",                                                                                  "Show help")
  ("infilename,i", po::value<string>(&fileName),                                              "In file name")
  ("ncats,c", po::value<int>(&ncats)->default_value(5),                                       "Number of categories")
  ("singleCat", po::value<int>(&singleCategory)->default_value(-1),                           "Run A single Category")
  ("datfile,d", po::value<string>(&datfile)->default_value("dat/fTest.dat"),                  "Right results to datfile for BiasStudy")
  ("outDir,D", po::value<string>(&outDir)->default_value("plots/fTest"),                      "Out directory for plots")
  ("saveMultiPdf", po::value<string>(&outfilename),         					"Save a MultiPdf model with the appropriate pdfs")
  ("runFtestCheckWithToys", 									"When running the F-test, use toys to calculate pvals (and make plots) ")
  ("is2011",                                                                                  "Run 2011 config")
  ("is2012",                                                                                  "Run 2012 config")
  ("runBlind",  									        "Blind plots around the Higgs boson mass")
  ("plotRatio", po::bool_switch(&data_by_fit)->default_value(false), "Plot data / fit instead of data - fit")
  ("isFlashgg",  po::value<int>(&isFlashgg_)->default_value(1),  								    	        "Use Flashgg output ")
  ("isData",  po::value<bool>(&isData_)->default_value(0),  								    	        "Use Data not MC ")
  ("flashggCats,f", po::value<string>(&flashggCatsStr_)->default_value("UntaggedTag_0,UntaggedTag_1,UntaggedTag_2,UntaggedTag_3,UntaggedTag_4,VBFTag_0,VBFTag_1,VBFTag_2,TTHHadronicTag,TTHLeptonicTag,VHHadronicTag,VHTightTag,VHLooseTag,VHEtTag"),       "Flashgg category names to consider")
  ("year", po::value<string>(&year_)->default_value("2016"),       "Dataset year")
  ("catOffset", po::value<int>(&catOffset)->default_value(0),       "Category numbering scheme offset")
  ("verbose,v",                                                                               "Run with more output")
;
po::variables_map vm;
po::store(po::parse_command_line(argc,argv,desc),vm);
po::notify(vm);
if (vm.count("help")) { cout << desc << endl; exit(1); }
if (vm.count("is2011")) is2011=true;
if (vm.count("runBlind")) BLIND=true;
saveMultiPdf = vm.count("saveMultiPdf");

if (vm.count("verbose")) verbose=true;
if (vm.count("runFtestCheckWithToys")) runFtestCheckWithToys=true;

if (!verbose) {
  RooMsgService::instance().setGlobalKillBelow(RooFit::ERROR);
  RooMsgService::instance().setSilentMode(true);
  gErrorIgnoreLevel=kWarning;
}
split(flashggCats_,flashggCatsStr_,boost::is_any_of(","));

int startingCategory=0;
if (singleCategory >-1){
ncats=singleCategory+1;
startingCategory=singleCategory;
}
if (isFlashgg_==1){

ncats= flashggCats_.size();

}

if(verbose) std::cout << "[INFO] SaveMultiPdf? " << saveMultiPdf << std::endl;

TFile *outputfile;
RooWorkspace *outputws;

if (saveMultiPdf){
outputfile = new TFile(outfilename.c_str(),"RECREATE");
outputws = new RooWorkspace(); outputws->SetName("multipdf");
}

system(Form("mkdir -p %s",outDir.c_str()));
TFile *inFile = TFile::Open(fileName.c_str());
RooWorkspace *inWS;
if(isFlashgg_){
  if (isData_){
          inWS = (RooWorkspace*)inFile->Get("tagsDumper/cms_hgg_13TeV");
          // TString wsname = Form("tagsDumper/xgg_highmass_13p6TeV_m%d-%d", mgg_low, mgg_high);
    // inWS = (RooWorkspace*)inFile->Get("tagsDumper/xgg_highmass_13p6TeV_m130-300");
    // inWS = (RooWorkspace*)inFile->Get(wsname);
  } else {
    inWS = (RooWorkspace*)inFile->Get("cms_hgg_workspace");
  }
} else {
  inWS = (RooWorkspace*)inFile->Get("cms_hgg_workspace");//FIXME
}
if (verbose) std::cout << "[INFO]  inWS open " << inWS << std::endl;
if (saveMultiPdf){
  transferMacros(inFile,outputfile);

  RooRealVar *intL;
  RooRealVar *sqrts;

  if (isFlashgg_){
    //intL  = (RooRealVar*)inWS->var("IntLumi");
    intL  = intLumi_;
    sqrts = (RooRealVar*)inWS->var("SqrtS");
    if (!sqrts){ sqrts = new RooRealVar("SqrtS","SqrtS",13.6); }
    // std::cout << "[INFO] got intL and sqrts " << intL << ", " << sqrts << std::endl;

  } else {
    //intL  = (RooRealVar*)inWS->var("IntLumi");
    intL  = intLumi_;
    sqrts = (RooRealVar*)inWS->var("Sqrts");
  }
  outputws->import(*intL);
  outputws->import(*sqrts);

  std::cout << "[INFO] got intL and sqrts " << intL << ", " << sqrts << std::endl;
  std::cout << "[INFO] intL value: " << intL->getVal() << ", sqrts: " << sqrts->getVal() << std::endl;
}

vector<string> functionClasses;
functionClasses.push_back("Bernstein");
functionClasses.push_back("Exponential");
functionClasses.push_back("PowerLaw");
functionClasses.push_back("Laurent");
functionClasses.push_back("InvPow");
functionClasses.push_back("InvPowLin");
functionClasses.push_back("Expow");
functionClasses.push_back("Dijet");
map<string,string> namingMap;
namingMap.insert(pair<string,string>("Bernstein","pol"));
namingMap.insert(pair<string,string>("Exponential","exp"));
namingMap.insert(pair<string,string>("PowerLaw","pow"));
namingMap.insert(pair<string,string>("Laurent","lau"));
namingMap.insert(pair<string,string>("InvPow","invpow"));
namingMap.insert(pair<string,string>("InvPowLin","invpowlin"));
namingMap.insert(pair<string,string>("Expow","expow"));
namingMap.insert(pair<string,string>("Dijet","dijet"));

// store results here

FILE *resFile ;
if  (singleCategory >-1) resFile = fopen(Form("%s/fTestResults_%s.txt",outDir.c_str(),flashggCats_[singleCategory].c_str()),"w");
else resFile = fopen(Form("%s/fTestResults.txt",outDir.c_str()),"w");
vector<map<string,int> > choices_vec;
vector<map<string,std::vector<int> > > choices_envelope_vec;
vector<map<string,RooAbsPdf*> > pdfs_vec;

PdfModelBuilder pdfsModel;
//RooRealVar *mass = (RooRealVar*)inWS->var("mass");
RooRealVar *mass = (RooRealVar*)inWS->var("CMS_hgg_mass");
std:: cout << "[INFO] Got mass from ws " << mass << std::endl;
mgg_low = mass->getMin();
mgg_high = mass->getMax();
nBinsForPlot = (mgg_high - mgg_low)/20 ;
nBinsForMass =  mgg_high - mgg_low;

pdfsModel.setObsVar(mass);
double upperEnvThreshold = 0.1; // upper threshold on delta(chi2) to include function in envelope (looser than truth function)

fprintf(resFile,"Truth Model & d.o.f & $\\Delta NLL_{N+1}$ & $p(\\chi^{2}>\\chi^{2}_{(N\\rightarrow N+1)})$ \\\\\n");
fprintf(resFile,"\\hline\n");

std::string ext = is2011 ? "7TeV" : "8TeV";
      if( isFlashgg_ ){
        if( year_ == "all" ){ ext = "13TeV"; }
        //else{ ext = "13TeV"; } //FIXME
        else{ ext = Form("%s_13TeV",year_.c_str()); }
      }
//if (isFlashgg_) ext = "13TeV";
      //FIXME trying to remove duplicated names for 2016+2017 combination
//if (isFlashgg_) ext = Form("13TeV_%d",year_);

for (int cat=startingCategory; cat<ncats; cat++){

  map<string,int> choices;
  map<string,std::vector<int> > choices_envelope;
  map<string,RooAbsPdf*> pdfs;
  map<string,RooAbsPdf*> allPdfs;

  string catname;
  if (isFlashgg_){
    catname = Form("%s",flashggCats_[cat].c_str());
  } else {
    catname = Form("cat%d",cat);
  }
  RooDataSet *dataFull;
  // RooDataSet *dataFull0;
  if (isData_) {
  dataFull = (RooDataSet*)inWS->data(Form("Data_13TeV_%s",catname.c_str()));
  //dataFull = (RooDataSet*)inWS->data(Form("Data_13p6TeV_%s",catname.c_str()));
  /*dataFull= (RooDataSet*) dataFull0->emptyClone();
  for (int i =0 ; i < dataFull0->numEntries() ; i++){
  double m = dataFull0->get(i)->getRealValue("CMS_hgg_mass");
  //if (m <(mgg_low+0.01) or m > (mgg_high-0.01))

  if (m==mgg_low){
  std::cout << "dataset mass m="<< m << std::endl;
  continue;
  }
  dataFull->add(*dataFull0->get(),1.0);
  }*/
  if (verbose) std::cout << "[INFO] opened data for RooDataset: "  << Form("Data_13p6TeV_%s",catname.c_str()) <<" - " << dataFull <<std::endl;
  }
  else
  {dataFull = (RooDataSet*)inWS->data(Form("data_mass_%s",catname.c_str()));
  if (verbose) std::cout << "[INFO] opened data for RooDataset: "  << Form("data_mass_%s",catname.c_str()) <<" - " << dataFull <<std::endl;
  }

  if(!mass) {
        std::cerr << "[FATAL] Mass variable not found in workspace!" << std::endl;
        inWS->Print("v"); // Dump workspace contents
        exit(1);
  }
  if(mass) {
        mass->setBins(nBinsForMass);
        mass->setBins(10000,"cache");
        std::cout << "[DEBUG] Using " << nBinsForMass << " bins for ["
                << mass->getMin() << ", " << mass->getMax() << "]" << std::endl;
  } else {
      std::cerr << "[FATAL] Mass variable not initialized!" << std::endl;
      exit(1);
  }
  std::cout << "\n=== Bin Configuration ===" << std::endl;
  std::cout << "Number of bins: " << nBinsForMass << std::endl;
  std::cout << "Mass range: [" << mgg_low << ", " << mgg_high << "] GeV\n";
  const RooAbsBinning* binning = mass->getBinningPtr("");
  if (!binning) {
      std::cerr << "[ERROR] Binning not initialized!" << std::endl;
      exit(1);
  }

  // Print first 5 and last 5 bin edges
  std::cout << "\nBin edges (first 5 and last 5):" << std::endl;
  for (int i=0; i<=binning->numBins(); i++) {
      if (i < 5 || i > binning->numBins()-5) {
          std::cout << "Bin " << i << ": " << binning->binLow(i) << " GeV" << std::endl;
      }
      if (i == 5) std::cout << "...\n";
  }
  // mass->setBins(nBinsForMass);
  RooDataSet *data;
  //	RooDataHist thisdataBinned(Form("roohist_data_mass_cat%d",cat),"data",*mass,*dataFull);
  //	RooDataSet *data = (RooDataSet*)&thisdataBinned;
  string thisdataBinned_name;

  if ( isFlashgg_){
    thisdataBinned_name =Form("roohist_data_mass_%s",flashggCats_[cat].c_str());
    //	RooDataHist thisdataBinned(Form("roohist_data_mass_cat%d",cat),"data",*mass,*dataFull);
    //	data = (RooDataSet*)&thisdataBinned;
    //		std::cout << "debug " << thisdataBinned.GetName() << std::endl;

    //RooDataSet *data = (RooDataSet*)dataFull;
  } else {
    thisdataBinned_name= Form("roohist_data_mass_cat%d",cat);
    //RooDataSet *data = (RooDataSet*)dataFull;
  }

  if (!dataFull || !mass) {
      std::cerr << "[FATAL] Null dataset (" << dataFull << ") or mass variable (" << mass << ")" << std::endl;
      if(dataFull) {
          std::cout << "[DEBUG] Dataset entries: " << dataFull->numEntries()
                    << ", mass range: [" << mass->getMin() << ", " << mass->getMax() << "]" << std::endl;
      }
      exit(1);
  }

  RooDataHist thisdataBinned(thisdataBinned_name.c_str(),"data",*mass,*dataFull);
  data = (RooDataSet*)&thisdataBinned;

  RooArgList storedPdfs("store");

  fprintf(resFile,"\\multicolumn{4}{|c|}{\\textbf{Category %d}} \\\\\n",cat);
  fprintf(resFile,"\\hline\n");

  double MinimimNLLSoFar=1e10;
  int simplebestFitPdfIndex = 0;


  // Standard F-Test to find the truth functions
  for (vector<string>::iterator funcType=functionClasses.begin();
      funcType!=functionClasses.end(); funcType++){

    double thisNll=0.; double prevNll=0.; double chi2=0.; double prob=0.;
    int order=1; int prev_order=0; int cache_order=0;

    RooAbsPdf *prev_pdf=NULL;
    RooAbsPdf *cache_pdf=NULL;
    std::vector<int> pdforders;

    int counter =0;

    //	while (prob<0.05){

          // With:
          int max_order;
        if (*funcType == "InvPow" || *funcType == "InvPowLin" ||
            *funcType == "Expow" || *funcType == "Dijet") {
            max_order = 1; // Newer functions only allow order = 1
        } else if (*funcType == "Bernstein"){
            max_order = 7;
        }else{
            max_order = 5; // Old functions allow order up to 5
        }
        std::cout << "functype: " << *funcType << max_order <<std::endl;

        if (max_order == 1) {
            RooAbsPdf *bkgPdf = getPdf(pdfsModel, *funcType, 1, Form("ftest_pdf_%d_%s", (cat+catOffset), ext.c_str()));
            if (bkgPdf) {
                 std::cout << "[DEBUG] Printing binned dataset before fitting..." << std::endl;
                 std::cout << "[DEBUG] Dataset contains " << data->numEntries() << " entries" << std::endl;
                 data->printMultiline(std::cout, 15);

                int fitStatus = 0;
                runFit(bkgPdf, data, &thisNll, &fitStatus, 5);
                if (fitStatus != 0) std::cout << "[WARNING] Fit failed for " << bkgPdf->GetName() << std::endl;

                double gofProb = 0;
                if (!saveMultiPdf) plot(mass, bkgPdf, data, Form("%s/%s1_cat%d", outDir.c_str(), funcType->c_str(), (cat+catOffset)), flashggCats_, fitStatus, &gofProb, binWidth, thisNll);

                // Set name for multipdf plot
                std::string pdfname = Form("env_pdf_%d_%s1", (cat+catOffset), namingMap[*funcType].c_str());
                bkgPdf->SetName(pdfname.c_str());

                // Store for truth plotting
                //pdfs.insert({Form("%s1", funcType->c_str()), bkgPdf});



                double chi2 = 0;
                double prob = 0;
                prob = getGoodnessOfFit(mass, bkgPdf, data, Form("%s/Ftest_from_%s1_cat%d", outDir.c_str(), funcType->c_str(), (cat+catOffset)), binWidth); //fixme
                if (prev_pdf != nullptr) {
                    chi2 = 2. * (prevNll - thisNll);
                    if (chi2 < 0.) chi2 = 0.;
                    prob = getProbabilityFtest(chi2, 1, prev_pdf, bkgPdf, mass, data,
                        Form("%s/Ftest_from_%s1_cat%d", outDir.c_str(), funcType->c_str(), (cat+catOffset)));
                }
                std::cout << "[INFO]  F-test Prob(chi2>chi2(data)) == " << prob << std::endl;
                std::cout << "[INFO]\t " << *funcType << " order: 1 " <<"prevNLL: " << prevNll << " thisNLL: " << thisNll << " Reduced_chi^2: " << chi2 << " Prob : " << prob << std::endl;

                // Set prev_pdf for the next function
                prev_pdf = bkgPdf;
                prevNll = thisNll;
                prev_order = 1;
                cache_order = 1;
                cache_pdf = bkgPdf;
                // storedPdfs.add(*bkgPdf);
                // if ((2.*thisNll + bkgPdf->getVariables()->getSize()) < MinimimNLLSoFar) {
                //     simplebestFitPdfIndex = storedPdfs.getSize()-1;
                //     MinimimNLLSoFar = 2.*thisNll + bkgPdf->getVariables()->getSize();
                // }

                //std::cout << "[DEBUG] For " << *funcType << ", final cache_pdf is "
                //          << (bkgPdf ? bkgPdf->GetName() : "NULL") << std::endl;
              }
            //continue;
        }else{
    //	while (prob<0.05){
      while (prob<1 && order <= max_order){
          // while (prob<0.05 && order < 5){ //FIXME
      RooAbsPdf *bkgPdf = getPdf(pdfsModel,*funcType,order,Form("ftest_pdf_%d_%s",(cat+catOffset),ext.c_str()));
      if (!bkgPdf){
        // assume this order is not allowed
        order++;
      }
      else {
        //RooFitResult *fitRes = bkgPdf->fitTo(*data,Save(true),RooFit::Minimizer("Minuit2","minimize"));
        int fitStatus = 0;
        //thisNll = fitRes->minNll();
        std::cout << "\n"<<std::endl;
        bkgPdf->Print();
        runFit(bkgPdf,data,&thisNll,&fitStatus,/*max iterations*/10); //bkgPdf->fitTo(*data,Save(true),RooFit::Minimizer("Minuit2","minimize"));
        if (fitStatus!=0) std::cout << "[WARNING] -- Fit status for " << bkgPdf->GetName() << " at " << fitStatus <<std::endl;

        chi2 = 2.*(prevNll-thisNll);
        if (chi2<0. && order>1) chi2=0.;
        if (prev_pdf!=NULL){
          prob = getProbabilityFtest(chi2,order-prev_order,prev_pdf,bkgPdf,mass,data,
                                  Form("%s/Ftest_from_%s%d_cat%d",outDir.c_str(),funcType->c_str(),order,(cat+catOffset)));
          std::cout << "[INFO] F-test Prob(chi2>chi2(data)) == " << prob << std::endl;
        } else {
          prob = 0;
        }
        double gofProb=0;
        // otherwise we get it later ...
        if (!saveMultiPdf) plot(mass,bkgPdf,data,Form("%s/%s%d_cat%d",outDir.c_str(),funcType->c_str(),order,(cat+catOffset)),flashggCats_,fitStatus,&gofProb, binWidth, thisNll);
        cout << "[INFO]\t" << "FunctionType: " << *funcType << ", " << "Order: " << order << ", " << "PreviousNLL: " << prevNll << ", " << "CurrentNLL: " << thisNll << ", " << "Chi2: " << chi2 << ", " << "Prob: " << prob << endl;
        //fprintf(resFile,"%15s && %d && %10.2f && %10.2f && %10.2f \\\\\n",funcType->c_str(),order,thisNll,chi2,prob);
        prevNll=thisNll;
        cache_order=prev_order;
        cache_pdf=prev_pdf;
        prev_order=order;
        prev_pdf=bkgPdf;
        order++;
      }
      counter++;
    }}

        fprintf(resFile,"%15s & %d & %5.2f & %5.2f \\\\\n",funcType->c_str(),cache_order+1,chi2,prob);
        choices.insert(pair<string,int>(*funcType,cache_order));
        pdfs.insert(pair<string,RooAbsPdf*>(Form("%s%d",funcType->c_str(),cache_order),cache_pdf));

    int truthOrder = cache_order;

    // Now run loop to determine functions inside envelope
    if (saveMultiPdf){
          std::cout << " ------------------------------------------------------------------------------------------------- " << std::endl;
          std::cout << " -----------------------------------Multipdf plotting started------------------------------------- " << std::endl;
          std::cout << " ------------------------------------------------------------------------------------------------- " << std::endl;
            chi2=0.;
            thisNll=0.;
            prevNll=0.;
            prob=0.;
            order=1;
            prev_order=0;
            cache_order=0;
            std::cout << "[INFO] Determining Envelope Functions for Family " << *funcType << ", cat " << cat << std::endl;
            std::cout << "[INFO] Upper end Threshold for highest order function " << upperEnvThreshold <<std::endl;

            while (prob<=1){ //upperEnvThreshold){
                RooAbsPdf *bkgPdf = getPdf(pdfsModel,*funcType,order,Form("env_pdf_%d_%s",(cat+catOffset),ext.c_str()));
                if (!bkgPdf ){
                    // assume this order is not allowed
                    if (order > max_order) { std::cout << " [WARNING] could not add order: " << order << std::endl; break ;}
                    order++;
                }
                else {
                    //RooFitResult *fitRes;
                    if (order > max_order) { std::cout << " [WARNING] could not add order: " << order << std::endl; break ;}
                    int fitStatus=0;
                    runFit(bkgPdf,data,&thisNll,&fitStatus,/*max iterations*/10);//bkgPdf->fitTo(*data,Save(true),RooFit::Minimizer("Minuit2","minimize"));
                    //thisNll = fitRes->minNll();
                    if (fitStatus!=0) std::cout << "[WARNING] Warning -- Fit status for " << bkgPdf->GetName() << " at " << fitStatus <<std::endl;
                    double myNll = 2.*thisNll;
                    chi2 = 2.*(prevNll-thisNll);
                    if (chi2<0. && order>1) chi2=0.;
                    prob = TMath::Prob(chi2,order-prev_order);

                    cout << "[INFO] \t " << *funcType << " order: " << order << " prevNLL: " << prevNll << " thisnll: " << thisNll << " chi2: " << chi2 << " prob: " << prob << endl;
                    prevNll=thisNll;
                    cache_order=prev_order;
                    cache_pdf=prev_pdf;

                    // Calculate goodness of fit for the thing to be included (will use toys for lowstats)!
                    double gofProb =0;
                    plot(mass,bkgPdf,data,Form("%s/%s%d_cat%d",outDir.c_str(),funcType->c_str(),order,(cat+catOffset)),flashggCats_,fitStatus,&gofProb, binWidth, thisNll);

                    if ((prob <= 1)){//upperEnvThreshold) ) { // Looser requirements for the envelope

                        if (gofProb > 0.01 || order == truthOrder ) {  // Good looking fit or one of our regular truth functions
                            std::cout << "[INFO] Adding to Envelope " << bkgPdf->GetName() << " gofProb:  "<< gofProb
                                << " 2xNLL + c is " << myNll + bkgPdf->getVariables()->getSize() <<  std::endl;
                            allPdfs.insert(pair<string,RooAbsPdf*>(Form("%s%d",funcType->c_str(),order),bkgPdf));
                            std::cout << "[DEBUG] Considering for Envelope: " << bkgPdf->GetName() << " | p(GOF) = " << gofProb << ", p(Chi²) = " << prob << std::endl;


              storedPdfs.add(*bkgPdf);
              pdforders.push_back(order);

                            // Keep track but we shall redo this later
                            if ((myNll + bkgPdf->getVariables()->getSize()) < MinimimNLLSoFar) {
                                simplebestFitPdfIndex = storedPdfs.getSize()-1;
                                MinimimNLLSoFar = myNll + bkgPdf->getVariables()->getSize();
                            }
                        }
                    }

          prev_order=order;
          prev_pdf=bkgPdf;
          order++;
        }
      }

      fprintf(resFile,"%15s & %d & %5.2f & %5.2f \\\\\n",funcType->c_str(),cache_order+1,chi2,prob);
      choices_envelope.insert(pair<string,std::vector<int> >(*funcType,pdforders));
          std::cout << " ------------------------------------------------------------------------------------------------- " << std::endl;
          std::cout << " -----------------------------------Multipdf plotting finished------------------------------------ " << std::endl;
          std::cout << " ------------------------------------------------------------------------------------------------- " << std::endl;

    }
  }

  fprintf(resFile,"\\hline\n");
  choices_vec.push_back(choices);
  choices_envelope_vec.push_back(choices_envelope);
  pdfs_vec.push_back(pdfs);
      std::cout << "[DEBUG] Plotting truths_cat for cat=" << cat << std::endl;
      for (auto &it : pdfs) {
          std::cout << "[DEBUG]   " << it.first << " -> " << (it.second ? "OK" : "NULL") << std::endl;
      }
  plot(mass,pdfs,data,Form("%s/truths_cat%d",outDir.c_str(),(cat+catOffset)),flashggCats_,cat);

  if (saveMultiPdf){
    // Put selectedModels into a MultiPdf
    string catindexname;
    string catname;
    if (isFlashgg_){
      catindexname = Form("pdfindex_%s_%s",flashggCats_[cat].c_str(),ext.c_str());
      catname = Form("%s",flashggCats_[cat].c_str());
    } else {
      catindexname = Form("pdfindex_%d_%s",(cat+catOffset),ext.c_str());
      catname = Form("cat%d",(cat+catOffset));
    }
    RooCategory catIndex(catindexname.c_str(),"c");
    RooMultiPdf *pdf = new RooMultiPdf(Form("CMS_hgg_%s_%s_bkgshape",catname.c_str(),ext.c_str()),"all pdfs",catIndex,storedPdfs);
    //RooRealVar nBackground(Form("CMS_hgg_%s_%s_bkgshape_norm",catname.c_str(),ext.c_str()),"nbkg",data->sumEntries(),0,10E8);
    RooRealVar nBackground(Form("CMS_hgg_%s_%s_bkgshape_norm",catname.c_str(),ext.c_str()),"nbkg",data->sumEntries(),0,3*data->sumEntries());
    //nBackground.removeRange(); // bug in roofit will break combine until dev branch brought in
    //double check the best pdf!

        std::vector<double> nll_values;
        int bestFitPdfIndex = getBestFitFunction(pdf,data,&catIndex,nll_values,verbose);
    catIndex.setIndex(bestFitPdfIndex);
    std::cout << "// ------------------------------------------------------------------------- //" <<std::endl;
    std::cout << "[INFO] Created MultiPdf " << pdf->GetName() << ", in Category " << cat << " with a total of " << catIndex.numTypes() << " pdfs"<< std::endl;
    //storedPdfs.Print();
    pdf->Print();
    std::cout << "[INFO] Best Fit Pdf = " << bestFitPdfIndex << ", " << storedPdfs.at(bestFitPdfIndex)->GetName() << std::endl;
    std::cout << "// ------------------------------------------------------------------------- //" <<std::endl;
    std::cout << "[INFO] Simple check of index "<< simplebestFitPdfIndex <<std::endl;

        mass->setBins(nBinsForMass);
        mass->setBins(10000,"cache");
        outputws->import(*mass, RooFit::RecycleConflictNodes());
        RooDataHist dataBinned(Form("roohist_data_mass_%s",catname.c_str()),"data",*mass,*dataFull);

        // Save it (also a binned version of the dataset
        outputws->import(*pdf);
        outputws->import(nBackground);
        outputws->import(catIndex);
        outputws->import(dataBinned);
        outputws->import(*data);
        plot(mass,pdf,&catIndex,data,Form("%s/multipdf_%s",outDir.c_str(),catname.c_str()),flashggCats_,cat,nll_values,bestFitPdfIndex);

  }

  }
  if (saveMultiPdf){
    outputfile->cd();
    outputws->Write();
    outputfile->Close();
  }

  FILE *dfile = fopen(datfile.c_str(),"w");
  cout << "[RESULT] Recommended options" << endl;

  for (int cat=startingCategory; cat<ncats; cat++){
    cout << "Cat " << cat << endl;
    fprintf(dfile,"cat=%d\n",(cat+catOffset));
    for (map<string,int>::iterator it=choices_vec[cat-startingCategory].begin(); it!=choices_vec[cat-startingCategory].end(); it++){
      cout << "\t" << it->first << " - " << it->second << endl;
      fprintf(dfile,"truth=%s:%d:%s%d\n",it->first.c_str(),it->second,namingMap[it->first].c_str(),it->second);
    }
    for (map<string,std::vector<int> >::iterator it=choices_envelope_vec[cat-startingCategory].begin(); it!=choices_envelope_vec[cat-startingCategory].end(); it++){
      std::vector<int> ords = it->second;
      for (std::vector<int>::iterator ordit=ords.begin(); ordit!=ords.end(); ordit++){
        fprintf(dfile,"paul=%s:%d:%s%d\n",it->first.c_str(),*ordit,namingMap[it->first].c_str(),*ordit);
      }
    }
    fprintf(dfile,"\n");
  }
  inFile->Close();

  return 0;
}