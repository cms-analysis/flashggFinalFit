// exectubale adapted from root Macro by M. Kenzie adapted from P. Meridiani.
// L. Corpe 07/2015


#include <iostream>
#include <string>
#include <map>
#include <vector>

#include "TFile.h"
#include "TMath.h"
#include "TCanvas.h"
#include "TH1F.h"
#include "TLegend.h"

#include "TStopwatch.h"
#include "RooWorkspace.h"
#include "RooDataSet.h"
#include "RooDataHist.h"
#include "RooAddPdf.h"
#include "RooGaussian.h"
#include "RooRealVar.h"
#include "RooFormulaVar.h"
#include "RooFitResult.h"
#include "RooPlot.h"
#include "RooMsgService.h"
#include "RooMinuit.h"

#include "boost/program_options.hpp"
#include "boost/algorithm/string/split.hpp"
#include "boost/algorithm/string/classification.hpp"
#include "boost/algorithm/string/predicate.hpp"

#include "TROOT.h"
#include "TStyle.h"
#include "TLatex.h"
#include "TPaveText.h"
#include "TArrow.h"

#ifndef TDRSTYLE_C
#define TDRSTYLE_C
#include "../../tdrStyle/tdrstyle.C"
#include "../../tdrStyle/CMS_lumi.C"
#endif

using namespace std;
using namespace RooFit;
using namespace boost;
namespace po = boost::program_options;

string filename_;
string outfilename_;
string datfilename_;
int m_hyp_;
string procString_;
int ncats_;
int binning_;
string flashggCatsStr_;
vector<string> flashggCats_;
vector<string> procs_;
bool isFlashgg_;
bool blind_;
int sqrts_;
bool doTable_;
bool verbose_;
bool doCrossCheck_;
bool markNegativeBins_;

void OptionParser(int argc, char *argv[]){
  po::options_description desc1("Allowed options");
  desc1.add_options()
    ("help,h",                                                                                "Show help")
    ("infilename,i", po::value<string>(&filename_),                                           "Input file name")
    ("outfilename,o", po::value<string>(&outfilename_),                                           "Output file name")
    ("mass,m", po::value<int>(&m_hyp_)->default_value(125),                                    "Mass to run at")
    ("sqrts", po::value<int>(&sqrts_)->default_value(13),                                    "CoM energy")
    ("binning", po::value<int>(&binning_)->default_value(70),                                    "CoM energy")
    ("procs,p", po::value<string>(&procString_)->default_value("ggh,vbf,wh,zh,tth"),          "Processes")
    ("isFlashgg",  po::value<bool>(&isFlashgg_)->default_value(true),                          "Use flashgg format")
    ("blind",  po::value<bool>(&blind_)->default_value(true),                          "blind analysis")
    ("doTable",  po::value<bool>(&doTable_)->default_value(false),                          "doTable analysis")
    ("doCrossCheck",  po::value<bool>(&doCrossCheck_)->default_value(false),                          "output additional details")
    ("verbose",  po::value<bool>(&verbose_)->default_value(false),                          "output additional details")
    ("markNegativeBins",  po::value<bool>(&markNegativeBins_)->default_value(false),                          " show with red arrow if a bin has a negative total value")
    ("flashggCats,f", po::value<string>(&flashggCatsStr_)->default_value("DiPhotonUntaggedCategory_0,DiPhotonUntaggedCategory_1,DiPhotonUntaggedCategory_2,DiPhotonUntaggedCategory_3,DiPhotonUntaggedCategory_4,VBFTag_0,VBFTag_1,VBFTag_2"),       "Flashgg category names to consider")
    ;

  po::options_description desc2("Options kept for backward compatibility");
  desc2.add_options()
    ("ncats,n", po::value<int>(&ncats_)->default_value(9),                                      "Number of cats (Set Automatically if using --isFlashgg 1)")
    ;
  po::options_description desc("Allowed options");
  desc.add(desc1).add(desc2);

  po::variables_map vm;
  po::store(po::parse_command_line(argc,argv,desc),vm);
  po::notify(vm);
  if (vm.count("help")){ cout << desc << endl; exit(1);}
}

map<string,RooDataSet*> getGlobeData(RooWorkspace *work, int ncats, int m_hyp){

  map<string,RooDataSet*> result;

  for (int cat=0; cat<ncats; cat++){
    result.insert(pair<string,RooDataSet*>(Form("cat%d",cat),(RooDataSet*)work->data(Form("sig_mass_m%3d_cat%d",m_hyp,cat))));
  }
  result.insert(pair<string,RooDataSet*>("all",(RooDataSet*)work->data(Form("sig_mass_m%3d_AllCats",m_hyp))));

  return result;
}
map<string,RooDataSet*> getFlashggData(RooWorkspace *work, int ncats, int m_hyp){

  map<string,RooDataSet*> result;

  for (int cat=0; cat<ncats; cat++){
    result.insert(pair<string,RooDataSet*>(Form("%s",flashggCats_[cat].c_str()),(RooDataSet*)work->data(Form("sig_mass_m%3d_%s",m_hyp,flashggCats_[cat].c_str()))));
  }
  result.insert(pair<string,RooDataSet*>("all",(RooDataSet*)work->data(Form("sig_mass_m%3d_AllCats",m_hyp))));

  return result;
}

map<string,RooDataSet*> getFlashggDataGranular(RooWorkspace *work, int ncats, int m_hyp){

  map<string,RooDataSet*> result;

  for (int cat=0; cat<ncats; cat++){
    for (int proc=0; proc < procs_.size() ; proc++){
     if (verbose_) std::cout << "INFO looking for this workspace: " << Form("sig_%s_mass_m%3d_%s",procs_[proc].c_str(),m_hyp,flashggCats_[cat].c_str()) << std::endl;
     std::cerr << "INFO looking for this workspace: " << Form("sig_%s_mass_m%3d_%s",procs_[proc].c_str(),m_hyp,flashggCats_[cat].c_str()) << std::endl;
     result.insert(pair<string,RooDataSet*>(Form("%s_%s",procs_[proc].c_str(),flashggCats_[cat].c_str()),(RooDataSet*)work->data(Form("sig_%s_mass_m%3d_%s",procs_[proc].c_str(),m_hyp,flashggCats_[cat].c_str()))));
      assert(work->data(Form("sig_%s_mass_m%3d_%s",procs_[proc].c_str(),m_hyp,flashggCats_[cat].c_str())));
    }
  }

  return result;
}

map<string,RooAddPdf*> getGlobePdfs(RooWorkspace *work, int ncats){

  map<string,RooAddPdf*> result;
  for (int cat=0; cat<ncats; cat++){
    result.insert(pair<string,RooAddPdf*>(Form("cat%d",cat),(RooAddPdf*)work->pdf(Form("sigpdfrelcat%d_allProcs",cat))));
  }
  result.insert(pair<string,RooAddPdf*>("all",(RooAddPdf*)work->pdf("sigpdfrelAllCats_allProcs")));

  return result;
}

map<string,RooAddPdf*> getFlashggPdfs(RooWorkspace *work, int ncats){

  map<string,RooAddPdf*> result;
  for (int cat=0; cat<ncats; cat++){
    result.insert(pair<string,RooAddPdf*>(Form("%s",flashggCats_[cat].c_str()),(RooAddPdf*)work->pdf(Form("sigpdfrel%s_allProcs",flashggCats_[cat].c_str()))));
  }
  result.insert(pair<string,RooAddPdf*>("all",(RooAddPdf*)work->pdf("sigpdfrelAllCats_allProcs")));

  return result;
}

map<string,RooAddPdf*> getFlashggPdfsGranular(RooWorkspace *work, int ncats){

  map<string,RooAddPdf*> result;
  for (int cat=0; cat<ncats; cat++){
    for (int proc=0; proc< procs_.size() ; proc++){
      result.insert(pair<string,RooAddPdf*>(Form("%s_%s",procs_[proc].c_str(),flashggCats_[cat].c_str()),(RooAddPdf*)work->pdf((Form("extendhggpdfsmrel_13TeV_%s_%sThisLumi",procs_[proc].c_str(),flashggCats_[cat].c_str())))));
      assert(work->pdf((Form("extendhggpdfsmrel_13TeV_%s_%sThisLumi",procs_[proc].c_str(),flashggCats_[cat].c_str()))));
  }
  }

  return result;
}

void printInfo(map<string,RooDataSet*> data, map<string,RooAddPdf*> pdfs){

  for (map<string,RooDataSet*>::iterator dat=data.begin(); dat!=data.end(); dat++){
    if (!dat->second) {
      cout << "dataset for " << dat->first << " not found" << endl;
      exit(1);
    }
    cout << dat->first << " : ";
    dat->second->Print();
  }
  for (map<string,RooAddPdf*>::iterator pdf=pdfs.begin(); pdf!=pdfs.end(); pdf++){
    if (!pdf->second) {
      cout << "pdf for " << pdf->first << " not found" << endl;
      exit(1);
    }
    cout << pdf->first << " : ";
    pdf->second->Print();
  }
}

pair<double,double> getEffSigmaData(RooRealVar *mass, RooDataHist *dataHist, double wmin=110., double wmax=130., double step=0.002, double epsilon=1.e-4){

  //RooAbsReal *cdf = pdf->createCdf(RooArgList(*mass));
  //RooDataHist *cumulativeHistogram = (RooDataHist*) dataHist->emptyClone();
  //cout << "Computing effSigma FOR DATA...." << endl;
  TStopwatch sw;
  sw.Start();
  double point=wmin;
  double weight=0; 
  vector<pair<double,double> > points;
  //std::cout << " dataHist " << *dataHist << std::endl;
  double thesum = dataHist->sumEntries();
  for (int i=0 ; i<dataHist->numEntries() ; i++){
    double mass = dataHist->get(i)->getRealValue("CMS_hgg_mass");
    weight += dataHist->weight(); 
    //std::cout << " mass " << mass << " cumulative weight " << weight/thesum << std::endl;
    if (weight > epsilon){
      points.push_back(pair<double,double>(mass,weight/thesum)); 
    }
  }
  //while (point <= wmax){
    //mass->setVal(point);
    //if (pdf->getVal() > epsilon){
    //  points.push_back(pair<double,double>(point,cdf->getVal())); 
    //}
    //point+=step;
  //}
  double low = wmin;
  double high = wmax;
  double width = wmax-wmin;
  for (unsigned int i=0; i<points.size(); i++){
    for (unsigned int j=i; j<points.size(); j++){
      double wy = points[j].second - points[i].second;
      if (TMath::Abs(wy-0.683) < epsilon){
        double wx = points[j].first - points[i].first;
        if (wx < width){
          low = points[i].first;
          high = points[j].first;
          width=wx;
        }
      }
    }
  }
  sw.Stop();
  //cout << "FILTER effSigma: [" << low << "-" << high << "] = " << width/2. << endl;
  //cout << "\tTook: "; sw.Print();
  pair<double,double> result(low,high);
  return result;
}

pair<double,double> getEffSigma(RooRealVar *mass, RooAbsPdf *pdf, double wmin=110., double wmax=130., double step=0.002, double epsilon=1.e-4){

  RooAbsReal *cdf = pdf->createCdf(RooArgList(*mass));
  cout << "Computing effSigma...." << endl;
  TStopwatch sw;
  sw.Start();
  double point=wmin;
  vector<pair<double,double> > points;

  while (point <= wmax){
    mass->setVal(point);
    if (pdf->getVal() > epsilon){
      points.push_back(pair<double,double>(point,cdf->getVal())); 
    }
    point+=step;
  }
  double low = wmin;
  double high = wmax;
  double width = wmax-wmin;
  for (unsigned int i=0; i<points.size(); i++){
    for (unsigned int j=i; j<points.size(); j++){
      double wy = points[j].second - points[i].second;
      if (TMath::Abs(wy-0.683) < epsilon){
        double wx = points[j].first - points[i].first;
        if (wx < width){
          low = points[i].first;
          high = points[j].first;
          width=wx;
        }
      }
    }
  }
  sw.Stop();
  cout << "effSigma: [" << low << "-" << high << "] = " << width/2. << endl;
  //cout << "\tTook: "; sw.Print();
  pair<double,double> result(low,high);
  return result;
}

// get effective sigma from finely binned histogram
pair<double,double> getEffSigBinned(RooRealVar *mass, RooAbsPdf *pdf, double wmin=110., double wmax=130.,int stepsize=1 ){

  int nbins = int((wmax-wmin)/0.001/double(stepsize));
  TH1F *h = new TH1F("h","h",nbins,wmin,wmax);
  pdf->fillHistogram(h,RooArgList(*mass));

  double narrowest=1000.;
  double bestInt;
  int lowbin;
  int highbin;

  double oneSigma=1.-TMath::Prob(1,1);

  TStopwatch sw;
  sw.Start();
  // get first guess
  cout << "Getting first guess info. stepsize (MeV) = " << stepsize*100 << endl;
  for (int i=0; i<h->GetNbinsX(); i+=(stepsize*100)){
    for (int j=i; j<h->GetNbinsX(); j+=(stepsize*100)){
      double integral = h->Integral(i,j)/h->Integral();
      if (integral<oneSigma) continue;
      double width = h->GetBinCenter(j)-h->GetBinCenter(i);
      if (width<narrowest){
        narrowest=width;
        bestInt=integral;
        lowbin=i;
        highbin=j;
        i++;
      }
    }
  }
  cout << "Took: "; sw.Print(); 
  // narrow down result
  int thisStepSize=32;
  cout << "Narrowing....." << endl;
  while (thisStepSize>stepsize) {
    cout << "\tstepsize (MeV) = " << thisStepSize << endl;
    for (int i=(lowbin-10*thisStepSize); i<(lowbin+10*thisStepSize); i+=thisStepSize){
      for (int j=(highbin-10*thisStepSize); j<(highbin+10*thisStepSize); j+=thisStepSize){
        double integral = h->Integral(i,j)/h->Integral();
        if (integral<oneSigma) continue;
        double width = h->GetBinCenter(j)-h->GetBinCenter(i);
        if (width<narrowest){
          narrowest=width;
          bestInt=integral;
          lowbin=i;
          highbin=j;
          i++;
        }
      }
    }
    thisStepSize/=2;
  }

  sw.Stop();
  cout << narrowest/2. << " " << bestInt << " [" << h->GetBinCenter(lowbin) << "," << h->GetBinCenter(highbin) << "]" << endl;
  cout << "Took:"; sw.Print();
  pair<double,double> result(h->GetBinCenter(lowbin),h->GetBinCenter(highbin));
  delete h;
  return result;
}

// get FWHHM
vector<double> getFWHM(RooRealVar *mass, RooAbsPdf *pdf, RooDataSet *data, double wmin=110., double wmax=130., double step=0.025) {

  cout << "Computing FWHM...." << endl;
  double nbins = (wmax-wmin)/step;
  TH1F *h = new TH1F("h","h",int(floor(nbins+0.5)),wmin,wmax);
  if (data){
    pdf->fillHistogram(h,RooArgList(*mass),data->sumEntries());
  }
  else {
    pdf->fillHistogram(h,RooArgList(*mass));
  }

  double hm = h->GetMaximum()*0.5;
  double low = h->GetBinCenter(h->FindFirstBinAbove(hm));
  double high = h->GetBinCenter(h->FindLastBinAbove(hm));

  cout << "FWHM: [" << low << "-" << high << " = " << high-low <<"] Max = " << hm << endl;
  vector<double> result;
  result.push_back(low);
  result.push_back(high);
  result.push_back(hm);
  result.push_back(h->GetBinWidth(1));

  delete h;
  return result;
}

void performClosure(RooRealVar *mass, RooAbsPdf *pdf, RooDataSet *data, string closurename, double wmin=110., double wmax=130., double slow=110., double shigh=130., double step=0.002) {

  // plot to perform closure test
  cout << "Performing closure test... for " << closurename << endl; 
  double nbins = (wmax-wmin)/step;
  TH1F *h = new TH1F("h","h",int(floor(nbins+0.5)),wmin,wmax);
  if (data){
    pdf->fillHistogram(h,RooArgList(*mass),data->sumEntries());
    h->Scale(2*h->GetNbinsX()/double(binning_));
  }
  else {
    pdf->fillHistogram(h,RooArgList(*mass));
  }
  int binLow = h->FindBin(slow);
  int binHigh = h->FindBin(shigh)-1;
  TH1F *copy = new TH1F("copy","c",binHigh-binLow,h->GetBinLowEdge(binLow),h->GetBinLowEdge(binHigh+1));
  for (int b=0; b<copy->GetNbinsX(); b++) copy->SetBinContent(b+1,h->GetBinContent(b+1+binLow));
  double areaCov = 100*h->Integral(binLow,binHigh)/h->Integral();

  // style
  h->SetLineColor(kBlue);
  h->SetLineWidth(3);
  h->SetLineStyle(7);
  copy->SetLineWidth(3);
  copy->SetFillColor(kGray);

  RooPlot *plot;
  TCanvas *ca = new TCanvas();
  ca->SetTickx(); ca->SetTicky();
  if (data){
    plot = (mass->frame(Bins(binning_),Range("higgsRange")));
    plot->addTH1(h,"hist"); 
    plot->addTH1(copy,"same f");
    if (data) data->plotOn(plot);
    pdf->plotOn(plot,Normalization(h->Integral(),RooAbsReal::NumEvent),NormRange("higgsRange"),Range("higgsRange"),LineWidth(1),LineColor(kRed),LineStyle(kDashed));
    plot->Draw();
    ca->Print(closurename.c_str());
  }
  else {
    plot = mass->frame(Bins(binning_),Range("higgsRange"));
    h->Scale(plot->getFitRangeBinW()/h->GetBinWidth(1));
    copy->Scale(plot->getFitRangeBinW()/h->GetBinWidth(1));
    pdf->plotOn(plot,LineColor(kRed),LineWidth(3));
    plot->Draw();
    h->Draw("hist same");
    copy->Draw("same f");
    ca->Print(closurename.c_str());
  }
  cout << "IntH: [" << h->GetBinLowEdge(binLow) << "-" << h->GetBinLowEdge(binHigh+1) << "] Area = " << areaCov << endl;
  delete ca;
  //  delete copy;
  // delete h;
  delete plot;
}

void Plot(RooRealVar *mass, RooDataSet *data, RooAbsPdf *pdf, pair<double,double> sigRange, vector<double> fwhmRange, string title, string savename){

  double semin=sigRange.first;
  double semax=sigRange.second;
  double fwmin=fwhmRange[0];
  double fwmax=fwhmRange[1];
  double halfmax=fwhmRange[2];
  double binwidth=fwhmRange[3];
  vector<double> negWeightBins;
  vector<double> negWeightBinsValues;
  RooPlot *plot = mass->frame(Bins(binning_),Range("higgsRange"));
  RooPlot *plotchi2 = mass->frame(Bins(binning_),Range("higgsRange"));
  plot->SetMinimum(0.0);
  plotchi2->SetMinimum(0.0);
  if (markNegativeBins_){
  TH1F *rdh = (TH1F*) data->createHistogram("CMS_hgg_mass",*mass,Binning(binning_,105,140));
    for(unsigned int iBin =0 ; iBin < rdh->GetNbinsX() ; iBin++){
      float content = rdh->GetBinContent(iBin);
      float center = rdh->GetBinCenter(iBin);
      if(content <0) {
        std::cout <<" BIN "<< iBin << " has negative weight : " << content << " at " << center << std::endl;
        negWeightBins.push_back(center);
        negWeightBinsValues.push_back(content);
      }
    }
  }
  double offset =0.05;
  if (data) data->plotOn(plot,Invisible());
  if (data) data->plotOn(plotchi2,Invisible());
  std::cout << " LC DEBIG A : data content: " << data->sumEntries() << std::endl;
  data->Print();

  pdf->plotOn(plot,NormRange("higgsRange"),Range(semin,semax),FillColor(19),DrawOption("F"),LineWidth(2),FillStyle(1001),VLines(),LineColor(15));
  TObject *seffLeg = plot->getObject(int(plot->numItems()-1));
  pdf->plotOn(plot,NormRange("higgsRange"),Range(semin,semax),LineColor(15),LineWidth(2),FillStyle(1001),VLines());
  pdf->plotOn(plot,NormRange("higgsRange"),Range("higgsRange"),LineColor(kBlue),LineWidth(2),FillStyle(0));
  pdf->plotOn(plotchi2,NormRange("higgsRange"),Range("higgsRange"),LineColor(kBlue),LineWidth(2),FillStyle(0));
  float chi2_bis= (plotchi2->chiSquare());
  //int ndof= (pdf->getParameters(*mass))->getSize();
  RooArgSet *allComponents = pdf->getComponents();
  TIterator *vIter = allComponents->createIterator();
  RooAbsReal * datavar;
  int ndof =0;
  while((datavar=(RooAbsReal*)vIter->Next())) {
    if (datavar) {
    if (!datavar->InheritsFrom("RooSpline1D")) {
    
    std::cout << " This datavar was skipped " << datavar->GetName() << std::endl;
    continue;
    }
    if (TString(datavar->GetName()).Contains("ea")) continue;
    if (TString(datavar->GetName()).Contains("xs")) continue;
    if (TString(datavar->GetName()).Contains("br")) continue;
    std::cout << " ** This datavar was counted " << datavar->GetName() << " ( " << datavar->IsA()->GetName()<< " ) " <<  std::endl;
    ndof++;
    }
  }
  //pdf->getObservables(*mh)->Print("V");
  //pdf->plotOn(plot,NormRange("higgsRange"),Range("higgsRange"),LineColor(kBlue),LineWidth(2),FillStyle(0));
  //pdf->plotOn(plot,Range("higgsRange"),LineColor(kBlue),LineWidth(2),FillStyle(0));

  TObject *pdfLeg = plot->getObject(int(plot->numItems()-1));
  if (data) data->plotOn(plot,MarkerStyle(kOpenSquare));
  TObject *dataLeg = plot->getObject(int(plot->numItems()-1));
  //TLegend *leg = new TLegend(0.15,0.89,0.5,0.55);
  TLegend *leg = new TLegend(0.15+offset,0.40,0.5+offset,0.82);
  leg->SetFillStyle(0);
  leg->SetLineColor(0);
  leg->SetTextSize(0.037);
  if (data) leg->AddEntry(dataLeg,"#bf{Simulation}","lep");
  leg->AddEntry(pdfLeg,"#splitline{#bf{Parametric}}{#bf{model}}","l");
  leg->AddEntry(seffLeg,Form("#bf{#sigma_{eff} = %1.2f GeV}",0.5*(semax-semin)),"fl");
  plot->GetXaxis()->SetNdivisions(509);
  halfmax*=(plot->getFitRangeBinW()/binwidth);
  TArrow *fwhmArrow = new TArrow(fwmin,halfmax,fwmax,halfmax,0.02,"<>");
  fwhmArrow->SetLineWidth(2.);
  TPaveText *fwhmText = new TPaveText(0.17+offset,0.3,0.45+offset,0.40,"brNDC");
  fwhmText->SetFillColor(0);
  fwhmText->SetLineColor(kWhite);
  fwhmText->SetTextSize(0.037);
  fwhmText->AddText(Form("FWHM = %1.2f GeV",(fwmax-fwmin)));
  std::cout << " [FOR TABLE] Tag " << data->GetName() << "=, Mass " << mass->getVal() << " sigmaEff=" << 0.5*(semax-semin) << "= , FWMH=" << (fwmax-fwmin)/2.35 << "=" << std::endl;
  //std::cout << " [RESOLUTION CHECK] Ta/Procg " << data->GetName() << ", Mass " << mass->getVal() << " sigmaEff=" << 0.5*(semax-semin) << " , FWMH=" << (fwmax-fwmin)/2.35 << "" << std::endl;

  //TLatex lat1(0.65,0.85,"#splitline{CMS Simulation}{}");
  TLatex  lat1(.129+0.03+offset,0.85,"H#rightarrow#gamma#gamma");
  lat1.SetNDC(1);
  lat1.SetTextSize(0.047);

  TString catLabel_humanReadable  = title;
  catLabel_humanReadable.ReplaceAll("_"," ");
  catLabel_humanReadable.ReplaceAll("UntaggedTag","Untagged");
  catLabel_humanReadable.ReplaceAll("VBFTag","VBF Tag");
  catLabel_humanReadable.ReplaceAll("TTHLeptonicTag","TTH Leptonic Tag");
  catLabel_humanReadable.ReplaceAll("TTHHadronicTag","TTH Hadronic Tag");
  catLabel_humanReadable.ReplaceAll("all","All Categories");

  TLatex lat2(0.93,0.88,catLabel_humanReadable);
  lat2.SetTextAlign(33);
  lat2.SetNDC(1);
  lat2.SetTextSize(0.045);

  TCanvas *canv = new TCanvas("canv","canv",650,600);
  canv->SetLeftMargin(0.16);
  canv->SetTickx(); canv->SetTicky();
  plot->SetTitle("");
  plot->GetXaxis()->SetTitle("m_{#gamma#gamma} (GeV)");
  plot->GetXaxis()->SetTitleSize(0.05);
  plot->GetYaxis()->SetTitleSize(0.05);
  plot->GetYaxis()->SetTitleOffset(1.5);
  plot->SetMinimum(0.0);
  plot->Draw();
  fwhmArrow->Draw("same <>");
  fwhmText->Draw("same");
  //lat1.Draw("same");
  lat2.Draw("same");
  lat1.Draw("same");
  leg->Draw("same");
  TLatex *chi2ndof_latex = new TLatex();	
  chi2ndof_latex->SetTextSize(0.035);
  chi2ndof_latex->SetTextAlign(33);
  chi2ndof_latex->SetNDC();
  //chi2ndof_latex->DrawLatex(0.93,0.83,Form("#chi^{2}/n_{d.o.f.}=%.3f/%d",chi2_bis,ndof));
  for (unsigned int i =0 ; i < negWeightBins.size() ; i++){
    TArrow *negBinsArrow = new TArrow(negWeightBins[i],0.0,negWeightBins[i],halfmax/2,0.02,"<>");
    negBinsArrow->SetLineWidth(2.);
    negBinsArrow->SetLineColor(kRed);
    negBinsArrow->Draw("same <>");

  }
  string sim="Simulation Preliminary";
  //string sim="Simulation"; //for the paper
  CMS_lumi( canv, 0,0,sim);
  canv->Print(Form("%s.pdf",savename.c_str()));
  canv->Print(Form("%s.png",savename.c_str()));
  //string path = savename.substr(0,savename.find('/'));
  //canv->Print(Form("%s/animation.gif+100",path.c_str()));

  delete canv;

}

int main(int argc, char *argv[]){

  OptionParser(argc,argv);
  TStopwatch sw;
  sw.Start();
  RooMsgService::instance().setGlobalKillBelow(RooFit::ERROR);
  RooMsgService::instance().setSilentMode(true);
  system("mkdir -p plots/SignalPlots/");
  setTDRStyle();
  writeExtraText = true;       // if extra text
  extraText  = "";  // default extra text is "Preliminary"
  lumi_13TeV  = "2.7 fb^{-1}"; // default is "19.7 fb^{-1}"
  lumi_8TeV  = "19.1 fb^{-1}"; // default is "19.7 fb^{-1}"
  lumi_7TeV  = "4.9 fb^{-1}";  // default is "5.1 fb^{-1}"
  lumi_sqrtS = "13 TeV";       // used with iPeriod = 0, e.g. for simulation-only plots (default is an empty string)

  split(procs_,procString_,boost::is_any_of(","));
  split(flashggCats_,flashggCatsStr_,boost::is_any_of(","));
  if (isFlashgg_){
    ncats_ =flashggCats_.size();
    // Ensure that the loop over the categories does not go out of scope. 
    std::cout << "[INFO] consider "<< ncats_ <<" tags/categories" << std::endl;
  }


  gROOT->SetBatch();
  gStyle->SetTextFont(42);


  TFile *hggFile = TFile::Open(filename_.c_str());
  RooWorkspace *hggWS;
  hggWS = (RooWorkspace*)hggFile->Get(Form("wsig_%dTeV",sqrts_));

  if (!hggWS) {
    cerr << "Workspace is null" << endl;
    exit(1);
  }

  RooRealVar *mass= (RooRealVar*)hggWS->var("CMS_hgg_mass");

  RooRealVar *mh = (RooRealVar*)hggWS->var("MH");
  mh->setVal(m_hyp_);
  mass->setRange("higgsRange",m_hyp_-20.,m_hyp_+15.);

  map<string,RooDataSet*> dataSets;
  map<string,RooDataSet*> dataSetsGranular;
  map<string,RooAddPdf*> pdfs;
  map<string,RooAddPdf*> pdfsGranular;

  if (isFlashgg_){
    dataSets = getFlashggData(hggWS,ncats_,m_hyp_);
    dataSetsGranular = getFlashggDataGranular(hggWS,ncats_,m_hyp_);
    pdfs = getFlashggPdfs(hggWS,ncats_);
    pdfsGranular = getFlashggPdfsGranular(hggWS,ncats_);
  }
  else {
    dataSets = getGlobeData(hggWS,ncats_,m_hyp_);
    pdfs = getGlobePdfs(hggWS,ncats_); 
  }

  //  printInfo(dataSets,pdfs);

  map<string,double> sigEffs;
  map<string,double> fwhms;


  system(Form("mkdir -p %s",outfilename_.c_str()));
  system(Form("rm -f %s/animation.gif",outfilename_.c_str()));


  for (map<string,RooDataSet*>::iterator dataIt=dataSets.begin(); dataIt!=dataSets.end(); dataIt++){
    pair<double,double> thisSigRange;
    if(dataIt->first!="all") thisSigRange = getEffSigma(mass,pdfs[dataIt->first],m_hyp_-10.,m_hyp_+10.);
    else {
      thisSigRange = getEffSigBinned(mass,pdfs[dataIt->first],m_hyp_-10.,m_hyp_+10);
      //RooDataHist *binned = new RooDataHist("test","test",*mass, (dataIt->second)->createHistogram("test",*mass,RooFit::Binning(1000,m_hyp_-10.,m_hyp_+10.)));
      //thisSigRange = getEffSigmaData(mass,binned,m_hyp_-10.,m_hyp_+10.);
    }

    vector<double> thisFWHMRange = getFWHM(mass,pdfs[dataIt->first],dataIt->second,m_hyp_-10.,m_hyp_+10.);

    sigEffs.insert(pair<string,double>(dataIt->first,(thisSigRange.second-thisSigRange.first)/2.));
    fwhms.insert(pair<string,double>(dataIt->first,thisFWHMRange[1]-thisFWHMRange[0]));
    if (doCrossCheck_) performClosure(mass,pdfs[dataIt->first],dataIt->second,Form("%s/closure_%s.pdf",outfilename_.c_str(),dataIt->first.c_str()),m_hyp_-10.,m_hyp_+10.,thisSigRange.first,thisSigRange.second);
    Plot(mass,dataIt->second,pdfs[dataIt->first],thisSigRange,thisFWHMRange,dataIt->first,Form("%s/%s",outfilename_.c_str(),dataIt->first.c_str()));
  }

  for (map<string,RooDataSet*>::iterator dataIt=dataSetsGranular.begin(); dataIt!=dataSetsGranular.end(); dataIt++){
    //RooDataHist *binned = new RooDataHist("test","test",*mass, (dataIt->second)->createHistogram("test",*mass,RooFit::Binning(1000,m_hyp_-10.,m_hyp_+10.)));
    //RooDataHist *binned = new RooDataHist("test1","test1",*mass, (dataIt->second)->createHistogram("tes1t",*mass,RooFit::Binning(1,100,140)));

    //pair<double,double> thisSigRange = getEffSigmaData(mass,binned,m_hyp_-10.,m_hyp_+10.);
    pair<double,double> thisSigRange = getEffSigma(mass,pdfsGranular[dataIt->first],m_hyp_-10.,m_hyp_+10.);
    //pair<double,double> thisSigRange = getEffSigBinned(mass,pdf[dataIt->first],m_hyp_-10.,m_hyp_+10);
    vector<double> thisFWHMRange = getFWHM(mass,pdfsGranular[dataIt->first],dataIt->second,m_hyp_-10.,m_hyp_+10.);
    sigEffs.insert(pair<string,double>(dataIt->first,(thisSigRange.second-thisSigRange.first)/2.));
    fwhms.insert(pair<string,double>(dataIt->first,thisFWHMRange[1]-thisFWHMRange[0]));
    if (doCrossCheck_) performClosure(mass,pdfsGranular[dataIt->first],dataIt->second,Form("%s/closure_%s.pdf",outfilename_.c_str(),dataIt->first.c_str()),m_hyp_-10.,m_hyp_+10.,thisSigRange.first,thisSigRange.second);
    Plot(mass,dataIt->second,pdfsGranular[dataIt->first],thisSigRange,thisFWHMRange,dataIt->first,Form("%s/%s",outfilename_.c_str(),dataIt->first.c_str()));
  }

  map<string,pair<double,double> > bkgVals;
  map<string,vector<double> > sigVals;
  map<string,pair<double,double> > datVals;
  map<string,double> sobVals;

  hggFile->Close();

}

