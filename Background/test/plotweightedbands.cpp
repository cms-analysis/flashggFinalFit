#include "TFile.h"
#include "RooWorkspace.h"
#include "RooRealVar.h"
#include "RooFormulaVar.h"
#include "TSystem.h"
#include "RooPlot.h"
#include "RooAbsData.h"
#include "RooCategory.h"
#include "RooAbsPdf.h"
#include "RooSimultaneous.h"
#include "RooDataSet.h"
#include "TCanvas.h"
#include "TSystem.h"
#include "TStyle.h"
#include "TROOT.h"
#include "RooFitResult.h"
#include "RooMinimizer.h"
#include "RooExtendPdf.h"
#include "RooDataHist.h"
#include "RooProduct.h"
#include "RooAddition.h"
#include "RooConstVar.h"
#include "TAxis.h"
#include "TGraphErrors.h"
#include "TH1D.h"
#include "TMath.h"
#include "TLegend.h"
#include "TLatex.h"
#include "TPad.h"
#include "TAttMarker.h"
#include "TExec.h"
#include "TGraphAsymmErrors.h"
#include "TChain.h"
#include "TChainElement.h"
#include "TEnv.h"
#include "TLine.h"
#include "RooHist.h"

#include "boost/program_options.hpp"
#include "boost/algorithm/string/split.hpp"
#include "boost/algorithm/string/classification.hpp"
#include "boost/algorithm/string/predicate.hpp"


using namespace RooFit;
using namespace std;
using namespace boost;
namespace po = boost::program_options;


string filenameStr_;
vector<string> filename_;
string name_;
string flashggCatsStr_;
vector<string> flashggCats_;
bool verbose_;
bool drawZeroBins_ ;

void OptionParser(int argc, char *argv[]){
	po::options_description desc1("Allowed options");
	desc1.add_options()
		("help,h",                                                                                			"Show help")
		("infilename,i", po::value<string>(&filenameStr_),                                           			"Input file name")
		("name", po::value<string>(&name_)->default_value("CMS-HGG_hgg_"), 			"Output file name")
		("flashggCats,f", po::value<string>(&flashggCatsStr_)->default_value("UntaggedTag_0,UntaggedTag_1,UntaggedTag_2,UntaggedTag_3,UntaggedTag_4,VBFTag_0,VBFTag_1,VBFTag_2,TTHHadronicTag,TTHLeptonicTag,VHHadronicTag,VHTightTag,VHLooseTag,VHEtTag"),       "Flashgg categories if used")
		("verbose,v", po::value<bool>(&verbose_)->default_value(0),       "verbose")
		("drawZeroBins", po::value<bool>(&drawZeroBins_)->default_value(1),       "Draw data points if zero events in that bin?")
		;                                                                                             		
	po::options_description desc("Allowed options");
	desc.add(desc1);

	po::variables_map vm;
	po::store(po::parse_command_line(argc,argv,desc),vm);
	po::notify(vm);
	if (vm.count("help")){ cout << desc << endl; exit(1);}
	
  // split options which are fiven as lists
  //split(procs_,procStr_,boost::is_any_of(","));
	split(flashggCats_,flashggCatsStr_,boost::is_any_of(","));
	split(filename_,filenameStr_,boost::is_any_of(","));

}






Double_t fwhm(TH1 * hist, double ratio=2*sqrt(2.0*log(2.0))) {
 
  double max = hist->GetMaximum();
  
  double left = 0.;
  for (int ibin=1; ibin<=hist->GetNbinsX(); ++ibin) {
    if (hist->GetBinContent(ibin)>(0.5*max)) {
      left = hist->GetBinCenter(ibin);
      break;
    }
  }
  
  double right = 0;
  for (int ibin=hist->GetNbinsX(); ibin>=1; --ibin) {
    if (hist->GetBinContent(ibin)>(0.5*max)) {
      right = hist->GetBinCenter(ibin);
      break;
    }
  }  
  
  return (right-left)/ratio;
  
}


//effsigma function from Chris
Double_t effSigma(TH1 * hist, double quantile=TMath::Erf(1.0/sqrt(2.0)))
{

  TAxis *xaxis = hist->GetXaxis();
  Int_t nb = xaxis->GetNbins();
  if(nb < 10) {
    cout << "effsigma: Not a valid histo. nbins = " << nb << endl;
    return 0.;
  }
  
  Double_t bwid = xaxis->GetBinWidth(1);
  if(bwid == 0) {
    cout << "effsigma: Not a valid histo. bwid = " << bwid << endl;
    return 0.;
  }
  Double_t xmax = xaxis->GetXmax();
  Double_t xmin = xaxis->GetXmin();
  Double_t ave = hist->GetMean();
  Double_t rms = hist->GetRMS();

  Double_t total=0.;
  for(Int_t i=0; i<nb+2; i++) {
    total+=hist->GetBinContent(i);
  }
//   if(total < 100.) {
//     cout << "effsigma: Too few entries " << total << endl;
//     return 0.;
//   }
  Int_t ierr=0;
  Int_t ismin=999;
  
  Double_t rlim=quantile*total;
  Int_t nrms=rms/(bwid);    // Set scan size to +/- rms
  if(nrms > nb/10) nrms=nb/10; // Could be tuned...

  Double_t widmin=9999999.;
  for(Int_t iscan=-nrms;iscan<nrms+1;iscan++) { // Scan window centre
    Int_t ibm=(ave-xmin)/bwid+1+iscan;
    Double_t x=(ibm-0.5)*bwid+xmin;
    Double_t xj=x;
    Double_t xk=x;
    Int_t jbm=ibm;
    Int_t kbm=ibm;
    Double_t bin=hist->GetBinContent(ibm);
    total=bin;
    for(Int_t j=1;j<nb;j++){
      if(jbm < nb) {
        jbm++;
        xj+=bwid;
        bin=hist->GetBinContent(jbm);
        total+=bin;
        if(total > rlim) break;
      }
      else ierr=1;
      if(kbm > 0) {
        kbm--;
        xk-=bwid;
        bin=hist->GetBinContent(kbm);
        total+=bin;
        if(total > rlim) break;
      }
      else ierr=1;
    }
    Double_t dxf=(total-rlim)*bwid/bin;
    Double_t wid=(xj-xk+bwid-dxf)*0.5;
    if(wid < widmin) {
      widmin=wid;
      ismin=iscan;
    }   
  }
  if(ismin == nrms || ismin == -nrms) ierr=3;
  if(ierr != 0) cout << "effsigma: Error of type " << ierr << endl;
  
  return widmin;
  
}



int main(int argc, char *argv[]) {
  
  gROOT->Macro("$CMSSW_BASE/src/flashggFinalFit/tdrStyle/hggPaperStyle.C");
  name_ = "Hgg_290216_";
  OptionParser(argc,argv);
  if (verbose_) std::cout << "[INFO] parsed arguments" << std::endl; 
  
  gStyle->SetOptStat(0);
  gStyle->SetPadTickX(1);  
  gStyle->SetPadTickY(1);   
  gROOT->ForceStyle();    
  
  
  if (verbose_) std::cout << "[INFO] Set plot prefix to " << name_ << std::endl; 
  TString prefix = name_;
  
  TString dirname = ".";
  gSystem->mkdir(dirname,true);
  gSystem->cd(dirname);
  
  const double leftpos = 102.0;
   
   
  //TFile *fin = TFile::Open("cms_hgg_datacard_FiducialRDiffXsScan_postFit.root");
  TFile *fin = TFile::Open(filename_[0].c_str());
  if (verbose_) std::cout << "[INFO] Opened file " << fin << std::endl; 
  
  RooWorkspace *win = (RooWorkspace*)fin->Get("w");  
  RooWorkspace *win2 = win;    
  RooAbsData *datain = win2->data("data_obs");
  
  RooRealVar *weightVar = new RooRealVar("weightvar","",1.);
  if (verbose_) std::cout << "[INFO] Loading  workspace "<< win2 << ", dataobs " << datain << " and weight"  << weightVar<< std::endl;  
  
  
  RooDataSet *data = new RooDataSet("data_obs_unbinned","",*datain->get());
  
  if (verbose_) std::cout << "[INFO]  make roodataset and FILL IT " << std::endl; 
  
  for (int idat=0; idat<datain->numEntries(); ++idat) {
    const RooArgSet *dset = datain->get(idat);
    int nent = int(datain->weight());
    for (int ient=0; ient<nent; ++ient) {
      data->add(*dset);
    }
  }
  
  win->loadSnapshot("MultiDimFit"); // needed ??
  
  RooFitResult *fit_s = 0;
  
  
  TFile *ftmp = new TFile("tmpfile.root","RECREATE");
  
  RooRealVar *MH = win->var("MH");
  RooRealVar *r = win->var("r");

  RooSimultaneous *sbpdf = (RooSimultaneous*)win->pdf("model_s");
  RooSimultaneous *bpdf = (RooSimultaneous*)win->pdf("model_b");
  if (verbose_) std::cout << "[INFO]  get pdfs " << sbpdf << " " << bpdf << std::endl; 
  
  RooRealVar *mass = win->var("CMS_hgg_mass");
  mass->SetTitle("#m_{#gamma#gamma}");
  mass->setUnit("GeV");
  RooCategory *chan = win->cat("CMS_channel");
  

  
  RooRealVar *massrel = new RooRealVar("massrel","",1.0,0.0,10.0);
  massrel->removeRange();
  
  RooRealVar *sigmaeff = new RooRealVar("sigmaeff","",1.0,0.0,10.0);
  RooRealVar *sob = new RooRealVar("sob","",1.0,0.0,10.0);
  sob->removeRange();

  RooRealVar *sobres = new RooRealVar("sobres","",1.0,0.0,10.0);
  sobres->removeRange();  
  
  RooRealVar *llrweight = new RooRealVar("llrweight","",1.0,0.0,10.0);
  llrweight->removeRange();  
  
  RooFormulaVar *massrelf = new RooFormulaVar("massrel","","(@0-@1)/@2",RooArgList(*mass,*MH,*sigmaeff));
  
  std::vector<double> sigmaeffs;
  
  RooDataSet *wdata = new RooDataSet("wdata","",RooArgSet(*chan,*mass,*sobres),"sobres");
  RooDataSet *wdatarel = new RooDataSet("wdata","",RooArgSet(*chan,*massrel,*sob),"sob");  
  RooDataSet *wdatallr = new RooDataSet("wdata","",RooArgSet(*chan,*mass,*llrweight),"llrweight");
  
  
  double nbweight = 0;
  double nsbweight = 0;
  double nsweight = 0;
  
  double stotal = 0;
  double btotal = 0;
  double sbtotal = 0;

  std::vector<TString> catdesc;
  std::vector<TString> catnames;  

  //for (int i=0; i<chan->numTypes(); ++i) {
   // chan->setIndex(i);
  //  printf("[INFO] Channel %i: %s\n",i,chan->getLabel());
  //}
  for (int i=0; i<chan->numTypes(); ++i) {
    chan->setIndex(i);
    printf("[INFO] Channel %i: %s\n",i,chan->getLabel());
    catnames.push_back(std::string(chan->getLabel()));
    TString desc = Form("#splitline{%s}{}",chan->getLabel());
    desc.ReplaceAll("_"," ");
    desc.ReplaceAll("13TeV","");
    desc.ReplaceAll("UntaggedTag","Untagged");
    desc.ReplaceAll("VBFTag","VBF Tag");
    desc.ReplaceAll("TTHLeptonicTag","TTH Leptonic Tag");
    desc.ReplaceAll("TTHHadronicTag","TTH Hadronic Tag");
    catdesc.push_back(desc);
    std::cout << "[INFO] --> description :" << desc << std::endl;
  }

  printf("[INFO] Channel %d  : combcat_unweighted",chan->numTypes()+1);
  std::cout << "[INFO] --> description :" << "#splitline{fiducial phase space}{All classes summed} "<< std::endl;
  catnames.push_back("combcat_unweighted");
  catdesc.push_back("#splitline{All categories summed}{}");
  
  printf("[INFO] Channel %d  : combcat_weighted",chan->numTypes()+2);
  std::cout << "[INFO] --> description :" << "#splitline{fiducial phase space}{S/(S+B) weighted sum}" << std::endl;
  catnames.push_back("combcat_weighted");
  catdesc.push_back("#splitline{All categories summed}{S/(S+B) weighted sum}");
  

  //catdesc.push_back("#splitline{fiducial phase space}{1.28\% < #sigma_{m}/m_{#gamma#gamma} < 1.83\%}");


  if (verbose_) std::cout << "[INFO] preparing weights verctor.." << std::endl; 
  std::vector<double> catweights;
  RooArgList wcatnorms;
  std::vector<RooAbsData*> catdatams;
  std::vector<RooAbsData*> bcatdatams; 
  
  double sigeffmin = 999;
  
  for (int i=0; i<chan->numTypes(); ++i) {
    chan->setIndex(i);
    
    printf("[INFO] Loop Through Channels, Channel %i\n",i);
    
    //std::cout << "debug getting bpdf bpdf->getpdf(chan->getlabel()) " << bpdf << " " << bpdf->getPdf(chan->getLabel()) << std::endl; 
    RooAbsPdf *bcatpdf = bpdf->getPdf(chan->getLabel());
    //std::cout << "debug getting bpdf bpdf->getpdf(chan->getlabel()) got it " << bcatpdf<< std::endl; 
    //std::cout << "DEBUG GETTING SBPDF sbpdf->getPdf(chan->getLabel()) " << sbpdf << " " << sbpdf->getPdf(chan->getLabel()) << std::endl; 
    RooAbsPdf *sbcatpdf = sbpdf->getPdf(chan->getLabel());
    //std::cout << "debug getting sbpdf sbpdf->getpdf(chan->getlabel()) got it " << sbcatpdf<< std::endl; 
    //printf("catdata = %5f\n",catdata->sumEntries());
    //catnorms.add(win->var(TString::Format("shapeBkg_bkg_mass_%s__norm",chan->getLabel())));
    
    std::cout << "[INFO] got background and sig + bkg pdfs "<< bcatpdf << " " << sbcatpdf << std::endl;

    double sbevents = sbcatpdf->expectedEvents(*mass);    
    double bevents = bcatpdf->expectedEvents(*mass);
    double sevents = sbevents - bevents;
    
    std::cout << "[INFO] number of events  sbevents  " << sbevents << " bevents " << bevents << " sevents " << std::endl;
 
    TH1D *hsbtmp = (TH1D*)sbcatpdf->createHistogram("hsbtmp",*mass,Binning(3200));
    TH1D *hbtmp = (TH1D*) bcatpdf->createHistogram("hbtmp",*mass,Binning(3200));
    
    TH1 *hstmp = new TH1D ( sbevents*(*hsbtmp) - bevents*(*hbtmp) );    
    
    std::cout << "[INFO] create correct histograms hsbtmp " << hsbtmp->Integral() << " hbtmp " << hbtmp->Integral() << " hstmp " << hstmp->Integral() << std::endl;
    
    double sigeffval = effSigma(hstmp);
    std::cout << "[INFO] got effsigma for hstmp " << sigeffval << std::endl;

    sigmaeffs.push_back(sigeffval);
    if (sigeffval<sigeffmin) sigeffmin = sigeffval;
    
    delete hsbtmp;
    delete hbtmp;
    delete hstmp;  
    
    
    TString rangename = TString::Format("sigeffrange_%s",chan->getLabel());
    mass->setRange(rangename,MH->getVal()-sigeffval,MH->getVal()+sigeffval);
    
    double bdiff = bcatpdf->createIntegral(*mass,*mass,rangename)->getVal()*bevents;
    std::cout << "[INFO] Get backgnd under +/- 1 sigeff   "<<  bcatpdf->createIntegral(*mass,*mass,rangename)->getVal()  << " *  " << bevents << " = " << bdiff << std::endl;
    double sdiff = TMath::Erf(1.0/sqrt(2.0))*sevents;
    std::cout << "[INFO] Get bdiff  "<< bdiff  << " sdiff " << sdiff << std::endl;
    
    double catweight = (sdiff)/(sdiff+bdiff);
    catweights.push_back(catweight);
    std::cout << "[INFO] Get catweight " << std::endl;
    
    nbweight += catweight*bevents;
    nsbweight += catweight*sbevents;
    nsweight += catweight*sevents;
    stotal += sevents;
    btotal += bevents;
    sbtotal += sbevents;
    
    std::cout << "[INFO] Running totals nbweight   " << nbweight  << " nsbweight " << nsbweight << "  nsweight " << nsweight << " stotal " << stotal<< " btotal " << btotal << " sbtotal " << sbtotal <<  std::endl;
    
      
  }

  
  
  double weightscale = stotal/nsweight;
  nsweight*=weightscale;
  nbweight*=weightscale;
  nsbweight*=weightscale;
  std::cout << "[INFO] weightscale " << weightscale << std::endl; 
  double lowedge = 100.;
  double highedge = 180;
  int nbins = 80;
  
  
  TH1D *hsig = new TH1D("hsig","",3200,100.,180.);
  TH1D *hwsig = new TH1D("hwsig","",3200,100.,180.);
  
  TH1D *hbkg = new TH1D("hbkg","",3200,100.,180.);
  TH1D *hwbkg = new TH1D("hwbkg","",3200,100.,180.);

  TH1D *hbkgplot = new TH1D("hbkgplot","",nbins,lowedge,highedge);
  TH1D *hwbkgplot = new TH1D("hwbkgplot","",nbins,lowedge,highedge);
  
  TH1D *hsigbkg = new TH1D("hsigbkg","",3200,100.,180.);
  TH1D *hwsigbkg = new TH1D("hwsigbkg","",3200,100.,180.);   
  
  int nbinsfine = 40*(highedge-lowedge);
  TH1D *hbkgplotfine = new TH1D("hbkgplotfine","",nbinsfine,lowedge,highedge);
  TH1D *hwbkgplotfine = new TH1D("hwbkgplotfine","",nbinsfine,lowedge,highedge);
  TH1D *hsigbkgplotfine = new TH1D("hsigbkgplotfine","",nbinsfine,lowedge,highedge);
  TH1D *hwsigbkgplotfine = new TH1D("hwsigbkgplotfine","",nbinsfine,lowedge,highedge);
  
  std::vector<TH1D*> hbkgplots;
  std::vector<TH1D*> hsigplotsfine;
  
  for (int i=0; i<chan->numTypes(); ++i) {
    
    printf("[INFO] Loop Through Channels, Channel %i --  %s \n",i,chan->getLabel());
    chan->setIndex(i);
    RooAbsPdf *bcatpdf = bpdf->getPdf(chan->getLabel());
    RooAbsPdf *sbcatpdf = sbpdf->getPdf(chan->getLabel());    
    
    std::cout << "[INFO]  -- formulaC " << TString::Format("CMS_channel==CMS_channel::%d",chan->getIndex()) << std::endl; 
    RooDataSet *catdata = (RooDataSet*)data->reduce(TString::Format("CMS_channel==CMS_channel::%d",chan->getIndex()));
    //RooDataSet *catdata = (RooDataSet*)data->reduce(TString::Format("CMS_channel==CMS_channel::%s",chan->getLabel()));
    //RooDataSet *catdata = (RooDataSet*)data->reduce(TString::Format("CMS_channel=='%s",chan->getLabel()));
    printf("[INFO] %s -- catdata entries = %5f\n",chan->getLabel(),catdata->sumEntries());
    //RooDataSet *catdatac = new RooDataSet(TString::Format("catdatac_%i",i),"",catdata,*catdata->get());

    RooAbsData *catdatam = catdata->reduce(*mass);
    RooDataHist *bcatdatam = new RooDataHist(TString::Format("bcatdatam_%i",i),"",*catdatam->get(),*catdatam);
    
    catdatams.push_back(catdatam);
    bcatdatams.push_back(bcatdatam);
    
    
    double catweight = weightscale*catweights[i];

    double sbevents = sbcatpdf->expectedEvents(*mass);    
    double bevents = bcatpdf->expectedEvents(*mass);
    double sevents = sbevents - bevents;
    std::cout << "[INFO] expected events before scaling  sbevents " <<  sbevents  <<  " bevents " << bevents << " sevents " << sevents << std::endl;
    std::cout << "[INFO] expected events after scaling  sbevents " <<  catweight*sbevents  <<  " bevents " << catweight*bevents << " sevents " << catweight*sevents << std::endl;
    
    TH1D *hsbtmp = (TH1D*)sbcatpdf->createHistogram("hsbtmp",*mass,Binning(3200));
    TH1D *hbtmp = (TH1D*) bcatpdf->createHistogram("hbtmp",*mass,Binning(3200));
    TH1D *hbplottmp = (TH1D*) bcatpdf->createHistogram("hbplottmp",*mass,Binning(nbins,lowedge,highedge));
    
    hsbtmp->Scale(1/hsbtmp->Integral());
    hbtmp->Scale(1/hbtmp->Integral());
    hbplottmp->Scale(1/hbplottmp->Integral());

    TH1D *hsbplotfinetmp = (TH1D*) sbcatpdf->createHistogram("hsbplotfinetmp",*mass,Binning(nbinsfine,lowedge,highedge));
    TH1D *hbplotfinetmp = (TH1D*) bcatpdf->createHistogram("hbplotfinetmp",*mass,Binning(nbinsfine,lowedge,highedge));
    hsbplotfinetmp->Scale(1/hsbplotfinetmp->Integral());
    hbplotfinetmp->Scale(1/hbplotfinetmp->Integral());

   //std::cout << " LC DEBUG hsbtmp " << hsbtmp->Integral() << " hbtmp " << hbtmp->Integral() << " hbplottmp " << hbplottmp->Integral() << " hsbplotfinetmp " << hsbplotfinetmp->Integral() << " hbplotfinetmp " << hbplotfinetmp->Integral() << std::endl;     
   /*   TCanvas *lc_debug_0 =  new TCanvas();
      hbplottmp->Draw();
      hsbtmp->Draw("SAME");
      hbtmp->Draw("SAME");
      lc_debug_0->SaveAs(Form("lc_debug_A_%d.pdf",i));*/
    
    hsigbkg->Add(hsbtmp,sbevents);
    hwsigbkg->Add(hsbtmp,catweight*sbevents);
    
    //std::cout << " LC DEBUG hsigbkg " << hsigbkg->Integral() << " hsbtmp " << hsbtmp->Integral() << "  sbevents " << sbevents << std::endl;
    //std::cout << " LC DEBUG hwsigbkg " << hwsigbkg->Integral() << " hsbtmp " << hsbtmp->Integral() << " catweight " << catweight << " sbevents " << sbevents << std::endl;

    hbkg->Add(hbtmp,bevents);
    hwbkg->Add(hbtmp,catweight*bevents);
    //std::cout << " LC DEBUG hbkg " << hbkg->Integral() << " hsbtmp " << hsbtmp->Integral() << "  sbevents " << sbevents << std::endl;
    //std::cout << " LC DEBUG hwbkg " << hwbkg->Integral() << " hsbtmp " << hsbtmp->Integral() << " catweight " << catweight << " sbevents " << sbevents << std::endl;
    
    hbkgplot->Add(hbplottmp,bevents);
    hwbkgplot->Add(hbplottmp,catweight*bevents);
    
    hbkgplotfine->Add(hbplotfinetmp,bevents);
    hwbkgplotfine->Add(hbplotfinetmp,catweight*bevents);    
    hsigbkgplotfine->Add(hsbplotfinetmp,sbevents);
    hwsigbkgplotfine->Add(hsbplotfinetmp,catweight*sbevents);    
    
    
    TH1 *hstmp = new TH1D ( sbevents*(*hsbtmp) - bevents*(*hbtmp) );
    hsig->Add(hstmp);
    
    TH1 *hwstmp = new TH1D ( catweight*(sbevents*(*hsbtmp) - bevents*(*hbtmp)) );
    hwsig->Add(hwstmp);

    TH1D *hbkgplot_cat = new TH1D(TString::Format("hbkgplot_%s",catnames[i].Data()),"",nbins,lowedge,highedge);
    //std::cout << "LC DEBUG hbkgplot_cat nbins " << nbins <<  " lowedge " << lowedge << " highedge " << highedge << " bevents " << bevents << " hbplottmp->Integral() " << hbplottmp->Integral() << std::endl;
    hbkgplot_cat->Add(hbplottmp,bevents);
    /*  TCanvas *lc_debug_AB =  new TCanvas();
      hbkgplot_cat->Draw();
      lc_debug_AB->SaveAs(Form("lc_debug_AB_%d.pdf",i));*/
    //std::cout << "LC DEBUG hbkgplot_cat sumEntries " <<  hbkgplot_cat->Integral() << std::endl; 
    hbkgplots.push_back(hbkgplot_cat);
    
    TH1D *hsigplot_cat = new TH1D(TString::Format("hsigplot_cat%s",catnames[i].Data()),"",3200,100.,180.);
    hsigplot_cat->Add(hstmp);
    hsigplotsfine.push_back(hsigplot_cat);

   /*   TCanvas *lc_debug =  new TCanvas();
      hbkgplot_cat->Draw();
      hsigplot_cat->Draw("SAME");
      lc_debug->SaveAs(Form("lc_debug_B_%d.pdf",i));*/
    
    delete hsbtmp;
    delete hbtmp;
    delete hbplottmp;
    delete hstmp;    
    delete hwstmp;    
    
    delete hsbplotfinetmp;
    delete hbplotfinetmp;
    
    RooAbsReal *catnorm = win->var(TString::Format("shapeBkg_bkg_mass_%s__norm",chan->getLabel()));
    //catnorm->Print("V");
    RooProduct *wcatnorm = new RooProduct(TString::Format("%s_wcatnorm",chan->getLabel()),"",RooArgSet(RooConst(catweight),*catnorm));
    wcatnorms.add(*wcatnorm);
        
    sobres->setVal(catweight);

    
    //printf("adding column\n");
    //sobres->Print("V");
    catdata->addColumn(*sobres);
    //catdata->addColumn(*sobres);
    //printf("added column\n");
    RooDataSet *wcatdata = new RooDataSet("wcatdata","",catdata,RooArgSet(*chan,*mass,*sobres),0,"sobres");
    wdata->append(*wcatdata);
        
    delete wcatdata;
    
    
  }
  
  hbkgplots.push_back(hbkgplot);
  hbkgplots.push_back(hwbkgplot);
  
  hsigplotsfine.push_back(hsig);
  hsigplotsfine.push_back(hwsig);
  
  RooAddition *wnorm = new RooAddition("wnorm","", wcatnorms);
  
  printf("wnorm = %5f, nbweight = %5f, nsbweight = %5f\n",wnorm->getVal(),nbweight,nsbweight);
  
//   new TCanvas;
//   RooPlot *plot3 = mass->frame(100.5,179.5,79);  
//   wdatallr->plotOn(plot3);
//   plot3->Draw();
//   
//   return;
  
  
  printf("wdata = %5f, wdatarel = %5f\n",wdata->sumEntries(),wdatarel->sumEntries());
  
  
  mass->setRange("binrange",124.5,125.5);
  mass->setRange("fullrange",124.5,125.5);  
 
  new TCanvas;
  hsig->Draw();
  
  
  
  double sigmaeffall = effSigma(hsig);
  double sigmaeffw = effSigma(hwsig);
  double iqr = 2.0*effSigma(hsig,0.5);
 
  //double fitmass = 124.5;
  double optbinwidth = 1.; 
  
  
  
  //double optbinwidth = 1.17;
  //double optbinwidth = sigmaeffall;
  //double optbinwidth = 2.0;
  //double optbinwidth = sigeffmin;
//   int nbinsplus = int((156.-fitmass-0.5*optbinwidth)/optbinwidth);
//   int nbinsminus = int((fitmass-0.5*optbinwidth-104.)/optbinwidth);
//   
//   int nbins = 1+nbinsplus+nbinsminus;
//   double lowedge = fitmass - 0.5*optbinwidth - nbinsminus*optbinwidth;
//   double highedge = fitmass + 0.5*optbinwidth + nbinsplus*optbinwidth;

//   lowedge = 100.25;
//   highedge = 179.75;
//   nbins = 53;  
  
  
  

  
  //vector(icat, ibin, itoy)
  std::cout << "[INFO] beginning systematics " << std::endl; 
  const int ncats = chan->numTypes();
  
  std::vector<std::vector<std::vector<double> > > errquants(ncats+2); 
  for (int icat=0; icat<(ncats+2); ++icat) {
    errquants[icat].resize(nbins);
  }
  
  
  TH1 *hwdata = wdata->createHistogram("hwdata",*mass,Binning(nbins,lowedge,highedge));
  TH1D *hsubdata = new TH1D("hsubdata","",nbins,lowedge,highedge);
  
  double curvescale = hsubdata->GetXaxis()->GetBinWidth(1)/hwsig->GetXaxis()->GetBinWidth(1);
  hsigbkg->Scale(curvescale);
  hwsigbkg->Scale(curvescale);
  hbkg->Scale(curvescale);
  hwbkg->Scale(curvescale);
  
  double curvescaleplotfine = hsubdata->GetXaxis()->GetBinWidth(1)/hwsigbkgplotfine->GetXaxis()->GetBinWidth(1);
  hsigbkgplotfine->Scale(curvescaleplotfine);
  hwsigbkgplotfine->Scale(curvescaleplotfine);
  hbkgplotfine->Scale(curvescaleplotfine);
  hwbkgplotfine->Scale(curvescaleplotfine);
  
/*  hsig->Scale(curvescale);
  hwsig->Scale(curvescale); */ 
  
  for (int isig=0; isig<hsigplotsfine.size(); ++isig) {
    hsigplotsfine[isig]->Scale(curvescale);
  }
  
  TGraphAsymmErrors *errgraph = new TGraphAsymmErrors;
  TGraphAsymmErrors *errgraph2 = new TGraphAsymmErrors;

  TGraphAsymmErrors *errgraphsub = new TGraphAsymmErrors;
  TGraphAsymmErrors *errgraphsub2 = new TGraphAsymmErrors;  
  
  TGraphAsymmErrors *errgraphcomb = new TGraphAsymmErrors;
  TGraphAsymmErrors *errgraphcomb2 = new TGraphAsymmErrors;  
  
  std::vector<TGraphAsymmErrors*> onesigmas;
  std::vector<TGraphAsymmErrors*> twosigmas;
  
  std::vector<TGraphAsymmErrors*> resonesigmas;
  std::vector<TGraphAsymmErrors*> restwosigmas;  
  
  for (int i=0; i<(chan->numTypes()+2); ++i) {
    onesigmas.push_back(new TGraphAsymmErrors);
    twosigmas.push_back(new TGraphAsymmErrors);
    resonesigmas.push_back(new TGraphAsymmErrors);
    restwosigmas.push_back(new TGraphAsymmErrors);
  }  
  
  int ntoys = 0;
  
  TH1 *hdummyweight = new TH1D("hdummyweight","",nbins,lowedge,highedge);
  
  printf("creating chain\n");
  //loop over toy files
  gEnv->SetValue("TFile.Recover", 0);
  TChain *chain = new TChain("limit");
  //chain->Add("/afs/cern.ch/user/b/bendavid/work/CMSSWcomb/CMSSW_6_1_2/src/globecardsJan30/results/freqtoys_rvrfmh_mva_comb_multipdf/*step2_99*.root");
//   chain->Add("/afs/cern.ch/user/b/bendavid/work/CMSSWcomb/CMSSW_6_1_2/src/bare/fiducial/lsf/output/*step2_99*.root");
  //chain->Add("*higgsCombinecombout_step2_done_1*.root");
  chain->Add("*higgsCombinecombout_step2_done*.root");

  
  TObjArray *fileElements=chain->GetListOfFiles();
  TIter next(fileElements);
  TChainElement *chEl=0;
  while (( chEl=(TChainElement*)next() )) {
    printf("[INFO] opening file %s \n", chEl->GetTitle() );
    TFile f(chEl->GetTitle());
    printf("[INFO] reading toy\n");
    RooAbsData *toy = (RooAbsData*)f.FindObjectAny("toy_asimov");
    
    if (!toy) { 
      printf("skipping\n");
      continue;
    }

    printf("[INFO] proceeding\n");
    
    ++ntoys;
    
    for (int icat=0; icat<ncats; ++icat) {
      chan->setIndex(icat);       
      std::cout << "[INFO]  " << chan->getLabel() << " -- formula  " << TString::Format("CMS_channel==CMS_channel::%d",chan->getIndex()) << std::endl; 
      RooAbsData *catdata = (RooAbsData*)toy->reduce(TString::Format("CMS_channel==CMS_channel::%d",chan->getIndex()));    
      //RooAbsData *catdata = (RooAbsData*)toy->reduce(TString::Format("CMS_channel==CMS_channel::%s",chan->getLabel()));    
      //RooAbsData *catdata = (RooAbsData*)toy->reduce(TString::Format("CMS_channel=='%s'",chan->getLabel()));    
      
      TH1D *hsbtmp = (TH1D*)catdata->createHistogram("hsbtmp",*mass,Binning(nbins,lowedge,highedge));
      for (int ibin=1; ibin<=hdummyweight->GetXaxis()->GetNbins(); ++ibin) {
        if(hsbtmp->GetBinContent(ibin) < 1.e10){ 
        errquants[icat][ibin-1].push_back(hsbtmp->GetBinContent(ibin));
        }
      }
      delete hsbtmp;    
      delete catdata;
    }
    
    
    delete toy;
    
    
    //delete wtoy;
    //wtoy->Print("V");
    //return;
  }  
  
  const double quantmed = 0.5;
  const double quantminusone = 0.5*(1.0+ TMath::Erf(-1.0/sqrt(2)));
  const double quantplusone = 0.5*(1.0+ TMath::Erf(1.0/sqrt(2)));
  const double quantminustwo = 0.5*(1.0+ TMath::Erf(-2.0/sqrt(2)));
  const double quantplustwo = 0.5*(1.0+ TMath::Erf(2.0/sqrt(2)));  
  
  
  
  
  
  for (int ibin=0; ibin<nbins; ++ibin) {
    std::vector<double> &errquantcomb = errquants[ncats][ibin];
    std::vector<double> &errquantcombw = errquants[ncats+1][ibin];
    errquantcomb.resize(ntoys);
    errquantcombw.resize(ntoys);
    
    for (int icat=0; icat<ncats; ++icat) {
      double catweight = weightscale*catweights[icat];
      for (int itoy=0; itoy<ntoys; ++itoy) {
        errquantcomb[itoy] += errquants[icat][ibin][itoy];
        errquantcombw[itoy] += catweight*errquants[icat][ibin][itoy];
      }
    }
    
 } 
  
  
  for (int icat=0; icat<(ncats+2); ++icat) {
    for (int ibin=0; ibin<nbins; ++ibin) {
    std::cout << "########################################################################" << std::endl;
    std::cout << "################### Toys for uncertainties debug for bin " << ibin <<  " and channel " << icat << "  ####################" << std::endl;
    std::cout << "########################################################################" << std::endl;
    std::cout << "errquants[ncats][ibin] size " << errquants[ncats][ibin].size() << " vs ntous " << ntoys << std::endl;
      std::vector<double> &entries = errquants[icat][ibin];
      std::sort(entries.begin(),entries.end());
      for (int ientry =0 ; ientry < entries.size() ; ientry++){
      std::cout << "entry " << ientry << " value " << entries[ientry] << std::endl;
      if (ientry == int(quantmed*entries.size())) std::cout << "** ^ median ^ ** "<< std::endl;  
      if (ientry == int(quantminusone*entries.size())) std::cout << "** ^ -1 sig ^ ** "<< std::endl;  
      if (ientry == int(quantplusone*entries.size())) std::cout << "** ^ +1 sig ^ ** "<< std::endl;  
      if (ientry == int(quantminustwo*entries.size())) std::cout << "** ^ -2 sig ^ ** "<< std::endl;  
      if (ientry == int(quantplustwo*entries.size())) std::cout << "** ^ +2 sig ^ ** "<< std::endl;  
      }
      double median = entries[int(quantmed*entries.size())];
      double minusone = entries[int(quantminusone*entries.size())];
      double plusone = entries[int(quantplusone*entries.size())];
      double minustwo = entries[int(quantminustwo*entries.size())];
      double plustwo = entries[int(quantplustwo*entries.size())];      
      
      double xval = hdummyweight->GetXaxis()->GetBinCenter(ibin+1);
      double xerr = hdummyweight->GetXaxis()->GetBinWidth(ibin+1)/2.0;
      
      double bkgval = hbkgplots[icat]->GetBinContent(ibin+1);      
      
      onesigmas[icat]->SetPoint(ibin,xval,median);
      twosigmas[icat]->SetPoint(ibin,xval,median);
      resonesigmas[icat]->SetPoint(ibin,xval,median-bkgval);
      restwosigmas[icat]->SetPoint(ibin,xval,median-bkgval);
      

      
      onesigmas[icat]->SetPointError(ibin,xerr,xerr,median-minusone,plusone-median);
      twosigmas[icat]->SetPointError(ibin,xerr,xerr,median-minustwo,plustwo-median);
      resonesigmas[icat]->SetPointError(ibin,xerr,xerr,median-minusone,plusone-median);
      restwosigmas[icat]->SetPointError(ibin,xerr,xerr,median-minustwo,plustwo-median);

      
      printf("[INFO] icat = %i, ibin = %i, median = %5f, minusone = %5f, plusone = %5f, minustwo = %5f, plustwo = %5f\n",icat,ibin,median,minusone,plusone,minustwo,plustwo);
      std::cout << "[INFO] ---> icat " << icat << " ibin  "<<  ibin << " median-bkgva " << median-bkgval  << " median-minusone  "   << median-minusone << " median-minustwo " <<  " plusone-median " << plusone-median << " median-minustwo "<<  median-minustwo << std::endl;
     }
  }
  
  
  
  
//   cres->SaveAs("sbweightedmassres.root");
//   cres->SaveAs("sbweightedmassres.C");
  
  //printf("[INFO] sigmaeffw = %5f, fitmass = %5f\n",sigmaeffw,fitmass);
  
  //return;
  std::cout << "[INFO] done calculatign systematics" << std::endl;
  

  
  std::cout << "[INFO] time to plot stuff..." << std::endl;
  //RooPlot *plot = mass->frame(100.,180.,80);
  RooPlot *plot = mass->frame(lowedge,highedge,nbins); 
  
  TH1D *hdummyunweight = new TH1D("hdummyunweight","",nbins,lowedge,highedge);
  
  TH1F *hdummy = new TH1F("hdummy","",nbins,lowedge,highedge);

  
  
  double deflinewidth = 3.0;
  double defmarkersize = 0.8;
  int defmarkerstyle = 20;
  double errlinewidth = 1.0;
  
  hsigbkg->SetLineWidth(deflinewidth);
  hwsigbkg->SetLineWidth(deflinewidth);
  hbkg->SetLineWidth(deflinewidth);
  hwbkg->SetLineWidth(deflinewidth);
  hsig->SetLineWidth(deflinewidth);
  hwsig->SetLineWidth(deflinewidth);
  
  hsigbkgplotfine->SetLineWidth(deflinewidth);
  hwsigbkgplotfine->SetLineWidth(deflinewidth);
  hbkgplotfine->SetLineWidth(deflinewidth);
  hwbkgplotfine->SetLineWidth(deflinewidth);
  
  hsig->SetLineColor(kRed);
  hwsig->SetLineColor(kRed);
  
  hsigbkg->SetLineColor(kRed);
  hwsigbkg->SetLineColor(kRed);
  hsigbkgplotfine->SetLineColor(kRed);
  hwsigbkgplotfine->SetLineColor(kRed);  
  
  hbkg->SetLineColor(kRed);
  hbkg->SetLineStyle(kDashed);
  hwbkg->SetLineColor(kRed);
  hwbkg->SetLineStyle(kDashed);

  hbkgplotfine->SetLineColor(kRed);
  hbkgplotfine->SetLineStyle(kDashed);
  hwbkgplotfine->SetLineColor(kRed);
  hwbkgplotfine->SetLineStyle(kDashed);  
  
  for (int isig=0; isig<hsigplotsfine.size(); ++isig) {
    hsigplotsfine[isig]->SetLineColor(kRed);
    hsigplotsfine[isig]->SetLineWidth(deflinewidth);
  }  
  
  hdummy->GetYaxis()->SetTitleOffset(0.5*hdummy->GetYaxis()->GetTitleOffset());
  hdummy->GetXaxis()->SetTitleSize(2.0*hdummy->GetXaxis()->GetTitleSize());
  hdummy->GetXaxis()->SetLabelSize(2.0*hdummy->GetXaxis()->GetLabelSize());
  hdummy->GetYaxis()->SetTitleSize(1.5*hdummy->GetYaxis()->GetTitleSize());
  hdummy->GetYaxis()->SetLabelSize(2.0*hdummy->GetYaxis()->GetLabelSize());
  
  for (int i=0; i<(chan->numTypes()+2); ++i) {
    bool iscombcat = !(i<chan->numTypes());
    
    if (i<ncats) chan->setIndex(i);
    
    RooAbsPdf *catbpdf = i>=ncats ? bpdf : bpdf->getPdf(chan->getLabel());
    RooAbsPdf *sbcatpdf = i>=ncats ? sbpdf : sbpdf->getPdf(chan->getLabel());
    
    RooAbsData *catdatam = 0;
    
    if (i<ncats) {
      //RooDataSet *catdata = (RooDataSet*)data->reduce(TString::Format("CMS_channel==CMS_channel::%s",chan->getLabel()));
      std::cout << "[INFO]  " << chan->getLabel() << " -- formula to gte data " << TString::Format("CMS_channel==CMS_channel::%d",chan->getIndex()) << std::endl; 
      RooDataSet *catdata = (RooDataSet*)data->reduce(TString::Format("CMS_channel==CMS_channel::%d",chan->getIndex()));
     // RooDataSet *catdata = (RooDataSet*)data->reduce(TString::Format("CMS_channel=='%s'",chan->getLabel()));
      catdatam = catdata->reduce(*mass);  
      printf("[INFO] catdata -- %d --  entries = %5f\n",i,catdata->sumEntries());
    }
    else if (i==ncats) {
      catdatam = data;
      printf("[INFO] catdata -- Unweighted data --  entries = %5f\n",i,catdatam->sumEntries());
    }
    else if (i==(ncats+1)) {
      catdatam = wdata;
      printf("[INFO] catdata -- Weighted data --  entries = %5f\n",i,catdatam->sumEntries());
    }
    
    
   std::cout << "[INFO] make canvas " << std::endl; 
   

    TCanvas *ccat = new TCanvas;


    TPad *pad1 = new TPad("pad1","pad1",0,0.25,1,1);
    TPad *pad2 = new TPad("pad2","pad2",0,0,1,0.35);
    pad1->SetBottomMargin(0.18);
//     pad1->SetBorderMode(0);
//     //pad1->SetLogy();
    pad2->SetTopMargin(0.00001);
    pad2->SetBottomMargin(0.25);
//     pad2->SetBorderMode(0);
    pad1->Draw();
    pad2->Draw();
    pad1->cd();

        
    
    
    //RooPlot *catplot = mass->frame(100.,180.,80);
    std::cout << "[INFO] make RooPLot" << std::endl; 
    RooPlot *catplot = mass->frame(lowedge,highedge,nbins);
    
    
    std::cout << "[info] --> invisibly plot data" << std::endl; 
    catdatam->plotOn(catplot,Invisible());
    catplot->Draw();
    
    TGraphAsymmErrors *twosigma = twosigmas[i];
    twosigma->SetFillColor(kYellow);
    twosigma->SetFillStyle(1001);
    twosigma->Draw("LE3SAME");  
    
    TGraphAsymmErrors *onesigma = onesigmas[i];
    onesigma->SetFillColor(kGreen);
    onesigma->SetFillStyle(1001);
    onesigma->Draw("LE3SAME");   
    std::cout << "[INFO] drew bands on main plot" << std::endl; 
    

    if (i<ncats) {
    std::cout << "[INFO] draw " << chan->getLabel() << " s and b pdfs" << std::endl; 
      catbpdf->plotOn(catplot,Normalization(catbpdf->expectedEvents(catdatam->get()),RooAbsPdf::NumEvent),LineColor(kRed),LineStyle(kDashed),LineWidth(deflinewidth));  
      sbcatpdf->plotOn(catplot,Normalization(sbcatpdf->expectedEvents(catdatam->get()),RooAbsPdf::NumEvent),LineColor(kRed),LineWidth(deflinewidth));      
    }
    else if (i==ncats) {
    std::cout << "[INFO] draw " << "unweighted " << " s and b pdfs" << std::endl; 
      hbkgplotfine->Draw("LSAME");
      hbkgplot->Draw("LSAME");
      hsigbkgplotfine->Draw("LSAME");
      //catbpdf->plotOn(catplot,ProjWData(*catdatam),Normalization(catbpdf->expectedEvents(catdatam->get()),RooAbsPdf::NumEvent),LineColor(kRed),LineStyle(kDashed));  
      //sbcatpdf->plotOn(catplot,ProjWData(*catdatam),Normalization(sbcatpdf->expectedEvents(catdatam->get()),RooAbsPdf::NumEvent),LineColor(kRed));
    }
    else if (i==(ncats+1)) {
    std::cout << "[INFO] draw " << "weighted " << " s and b pdfs" << std::endl; 
      hwbkgplotfine->Draw("LSAME");
      hwsigbkgplotfine->Draw("LSAME");      
//       catbpdf->plotOn(catplot,ProjWData(*catdatam),Normalization(nbweight,RooAbsPdf::NumEvent),LineColor(kRed),LineStyle(kDashed));  
//       sbcatpdf->plotOn(catplot,ProjWData(*catdatam),Normalization(nsbweight,RooAbsPdf::NumEvent),LineColor(kRed));
    }
    
    //catdatam->plotOn(catplot,XErrorSize(0),MarkerSize(1.0));
    catdatam->plotOn(catplot,XErrorSize(0),MarkerSize(defmarkersize),MarkerStyle(defmarkerstyle),LineWidth(errlinewidth));
     
    RooHist *plotdata = (RooHist*)catplot->getObject(catplot->numItems()-1);


/////////////////// ALTERNATIVE UNCERTINATY CALC ///////////////
/*

	TGraphAsymmErrors *oneSigmaBandAlt = new TGraphAsymmErrors();
	oneSigmaBandAlt->SetName(Form("onesigmaAlt_%s",catname.c_str()));
	TGraphAsymmErrors *twoSigmaBandAlt = new TGraphAsymmErrors();
	twoSigmaBandAlt->SetName(Form("twosigmaAlt_%s",catname.c_str()));
	TGraphAsymmErrors *oneSigmaBandResAlt = new TGraphAsymmErrors();
	oneSigmaBandResAlt->SetName(Form("onesigmaResAlt_%s",catname.c_str()));
	TGraphAsymmErrors *twoSigmaBandAlt = new TGraphAsymmErrors();
	twoSigmaBandResAlt->SetName(Form("twosigmaresAlt_%s",catname.c_str()));

		int p=0;

    double xtmp, ytmp;
    int npoints = plotdata->GetN();
    
    assert(npoints==nbins);
    
    TGraphAsymmErrors *hdatasub = new TGraphAsymmErrors(npoints);
    hdatasub->SetMarkerSize(defmarkersize);
    //hdatasub->SetHistogram(hdummy);
    for (int ipoint=0; ipoint<npoints; ++ipoint) {

    plotdata->GetPoint(ipoint, xtmp,ytmp);
			double lowedge = xtmp-0.5;
			double upedge = xtmp+0.5;
			double center = xmtp;
			double nomBkg = nomBkgCurve->interpolate(center);

      double nllBest = getNormTermNll(mass,catdatam,mpdf,mcat,nomBkg,lowedge,upedge);
    }
*/
/////////////////// END of  ALTERNATIVE UNCERTINATY CALC ///////////////
    /* TCanvas *lc_debug_2 =  new TCanvas();
    hbkgplots[i]->Draw();
    plotdata->Draw("same");
    std::cout << "DEBUG DEBUG catdatam " << catdatam->numEntries() << "("<<catdatam->numEntries() << ") hbkgplots[i]->Integral" << hbkgplots[i]->Integral() << std::endl; 
    float tally1=0;
    float tally2=0;
    for (int j =0 ; j<plotdata->GetN(); j++){
    double x1=0;
    double y1=0;
    plotdata->GetPoint(j,x1,y1);
    tally1 =tally1  + y1;
    float y2 =0;
    y2 = (float) hbkgplots[i]->GetBinContent(j);
    tally2 = tally2 +y2;
    std::cout << "DEBUG point " << j << " tally1 " << tally1 <<" (+ " << y1 << ")  tally 2 " << tally2  << " (+" << y2 << ")" << std::endl;

    }
    lc_debug_2->SaveAs(Form("lc_debug_C_%d.pdf",i));*/
    
    //catplot->GetYaxis()->
    catplot->GetYaxis()->SetTitleSize(0.056);
    if (catplot->GetXaxis()->GetBinWidth(1) !=1){
      catplot->GetYaxis()->SetTitle(TString::Format("Events / %.3g GeV",catplot->GetXaxis()->GetBinWidth(1)));
    } else {
      catplot->GetYaxis()->SetTitle(TString::Format("Events / GeV"));
    }
    //catplot->GetYaxis()->SetTitleOffset(1.015*catplot->GetYaxis()->GetTitleOffset());
    catplot->GetYaxis()->SetTitleOffset(0.9*catplot->GetYaxis()->GetTitleOffset());
    catplot->SetTitle("");
    
    if (catplot->GetXaxis()->GetBinWidth(1) !=1){
      if (i==(ncats+1)) catplot->GetYaxis()->SetTitle(TString::Format("S/(S+B) Weighted Events / %.3g GeV",catplot->GetXaxis()->GetBinWidth(1)));
    } else {
      if (i==(ncats+1)) catplot->GetYaxis()->SetTitle(TString::Format("S/(S+B) Weighted Events / GeV",catplot->GetXaxis()->GetBinWidth(1)));
    }
    
    float offset =-999;
    if (i==(ncats+1)) {
      offset=0;
    } else {
      offset=0.05;
    }

    catplot->GetXaxis()->SetTitle("");
    catplot->GetXaxis()->SetLabelOffset(999);
    
    catplot->Draw("SAME");  
    
    
    catplot->SetMaximum(1.2*catplot->GetMaximum());
    if (!drawZeroBins_) catplot->SetMinimum(1e-5);
    
//     TLegend *leg2 = new TLegend(0.60,0.70,0.95,0.90);  
    //TLegend *leg2 = new TLegend(0.56,0.53,0.87,0.87);  
    TLegend *leg2 = new TLegend(0.529,0.46+offset,0.860,0.749+offset);  
    leg2->AddEntry(plotdata,"Data","PE");  
//     leg2->AddEntry(plot2->getObject(2),"S+B Fit","L");  
//     leg2->AddEntry(plot2->getObject(1),"Bkg Fit Component","L");  
    leg2->AddEntry(hsigbkg,"S+B fit sum","L");  
    leg2->AddEntry(hbkg,"B component","L");  
    leg2->AddEntry(onesigma,"#pm1 #sigma","F");  
    leg2->AddEntry(twosigma,"#pm2 #sigma","F");       
/*    leg2->AddEntry(errgraph,"#pm1 #sigma","F");  
    leg2->AddEntry(errgraph2,"#pm2 #sigma","F");   */   
    leg2->SetBorderSize(0);
    leg2->SetFillStyle(0);
    leg2->Draw();      
    
    
    TLatex *lat2 = new TLatex();
    lat2->SetNDC();
    lat2->SetTextSize(0.045);
//     lat2->DrawLatex(0.2,0.85,TString::Format("#scale[0.8]{%s}",catdesc.at(i).Data()));
    //lat2->DrawLatex(0.25,0.82,TString::Format("#scale[1.0]{%s}",catdesc.at(i).Data()));
    lat2->DrawLatex(0.535,0.800,TString::Format("#scale[1.0]{%s}",catdesc.at(i).Data()));
    //lat2->DrawLatex(0.25,0.72,"m_{H}=125.09 GeV, #hat{#mu}=0.7");
    lat2->DrawLatex(0.159,0.8,"m_{H}=125.09 GeV, #hat{#mu}=0.7");
    //lat2->DrawLatex(0.587,0.717,"-");
    lat2->DrawLatex(0.56585,0.727+offset,"-"); // top
    
    TLatex *lat2b = new TLatex();
    lat2b->SetNDC();
    lat2b->SetTextSize(0.045);
    lat2b->SetTextAngle(180);
    //lat2->DrawLatex(0.597,0.701,"-");
    //lat2b->DrawLatex(0.578855,0.701,"-"); //bottom;
    lat2b->DrawLatex(0.577,0.711+offset,"-"); //bottom;
    //lat2b->DrawLatex(0.56585,0.701,"-"); //bottom;
    
    TLatex *lat3 = new TLatex();
    lat3->SetNDC();
    lat3->SetTextSize(0.057);
    lat3->DrawLatex(0.13,0.93,"#bf{CMS} #scale[0.75]{#it{Preliminary}}");    
    
    TLatex *mytext = new TLatex();
    mytext->SetTextSize(0.055);
    mytext->SetNDC();
//     mytext->DrawLatex(0.15,0.93,"CMS #sqrt{s} = 7 TeV, L = 5.1 fb^{-1}, #sqrt{s} = 8 TeV, L = 19.7 fb^{-1}");
//     mytext->DrawLatex(0.15,0.93,"CMS #sqrt{s} = 8 TeV, L = 19.7 fb^{-1}");
    mytext->DrawLatex(0.64,0.93,"2.7 fb^{-1} (13#scale[0.75]{ }TeV)");        
    mytext->DrawLatex(0.129+0.03,0.85,"H#rightarrow#gamma#gamma");
    
    

    

    std::cout << "[INFO]  now do lower ratio plot " << std::endl; 
    double xtmp, ytmp;
    int npoints = plotdata->GetN();
    
    assert(npoints==nbins);
    int point =0;
    TGraphAsymmErrors *hdatasub = new TGraphAsymmErrors(npoints);
    hdatasub->SetMarkerSize(defmarkersize);
    //hdatasub->SetHistogram(hdummy);
    for (int ipoint=0; ipoint<npoints; ++ipoint) {
      double bkgval = hbkgplots[i]->GetBinContent(ipoint+1);      
      
      plotdata->GetPoint(ipoint, xtmp,ytmp);
      std::cout << "[INFO] plotdata->Integral() " <<  plotdata->Integral() << " ( bins " << npoints  << ") hbkgplots[i]->Integral() " <<  hbkgplots[i]->Integral() << " (bins " << hbkgplots[i]->GetNbinsX() << std::endl; 
      //std::cout << "LC  DEBUG batdatam->suMEnties() " << bcatdatam->sumEntries() << " batdatam->nuMEnties() " << bcatdatam->numEntries() << std::endl;
      double errhi = plotdata->GetErrorYhigh(ipoint);
      double errlow = plotdata->GetErrorYlow(ipoint);
      
      std::cout << "[INFO]  Channel " << chan->getLabel() << " errhi " << errhi << " errlow " << errlow  << std::endl;
      //rintf("ipoint = %i, xtmp = %5f, ytmp = %5f, bkgval = %5f\n",ipoint, xtmp,ytmp,bkgval);
      std::cout << "[INFO] Channel  " << chan->getLabel() << " ytmp " << ytmp << " bkgval  " << bkgval << " ytmp-bkgval " << ytmp-bkgval << std::endl;
      if (!drawZeroBins_) if(fabs(ytmp)<1e-5) continue; 
      hdatasub->SetPoint(point,xtmp,ytmp-bkgval);
      //hdatasub->SetPoint(ipoint,xtmp,1);
      hdatasub->SetPointError(point,0.,0.,errlow,errhi );
      point++;
    }

    
    pad2->cd();
    
    hdatasub->SetMarkerStyle(defmarkerstyle);
    hdatasub->SetLineWidth(errlinewidth);
    
 //   hdummy->GetXaxis()->SetTitle("m_{#gamma#gamma} (GeV)");
    
//     hdatasub->Draw("APE");
// 
//     hdummy->SetMaximum(hdatasub->GetMaximum());
//     hdummy->SetMinimum(hdatasub->GetMinimum());
    
   // hdummy->Draw("HIST");
    
//     hdatasub->SetTitle();
    //hdatasub->GetXaxis()->SetTitle("m_{#gamma#gamma} (GeV)");
    hdatasub->Draw("APE");
    
    
    hdummy->SetMaximum(hdatasub->GetHistogram()->GetMaximum()+1);
    hdummy->SetMinimum(hdatasub->GetHistogram()->GetMinimum()-1);
    hdummy->GetXaxis()->SetTitle("m_{#gamma#gamma} (GeV)");
    hdummy->GetXaxis()->SetTitleSize(0.12);
//     hdummy->GetYaxis()->SetTitle(TString::Format("Events /  %.3g GeV",hdummy->GetXaxis()->GetBinWidth(1)));
//     if (i==(ncats+1)) hdummy->GetYaxis()->SetTitle(TString::Format("Weighted Events / %.3g GeV",hdummy->GetXaxis()->GetBinWidth(1)));

    
    hdummy->Draw("HIST");
    hdummy->GetYaxis()->SetNdivisions(808);

    
    TGraphAsymmErrors *restwosigma = restwosigmas[i];
    restwosigma->SetFillColor(kYellow);
    restwosigma->SetFillStyle(1001);
    restwosigma->Draw("LE3SAME");  
    
    TGraphAsymmErrors *resonesigma = resonesigmas[i];
    resonesigma->SetFillColor(kGreen);
    resonesigma->SetFillStyle(1001);
    resonesigma->Draw("LE3SAME");       
    
    TLine *line3 = new TLine(lowedge,0.,highedge,0.);
    line3->SetLineColor(kRed);
    line3->SetLineStyle(kDashed);
    line3->SetLineWidth(deflinewidth);
    line3->Draw();
    
    TH1D *hsigplotfine = hsigplotsfine[i];
    hsigplotfine->SetLineColor(kRed);
    hsigplotfine->SetLineWidth(deflinewidth);
    
    hsigplotfine->Draw("HISTSAME");
    
    hdatasub->Draw("PESAME");
    
    TLatex *lat4 = new TLatex();
    lat4->SetNDC();
    lat4->SetTextSize(0.1);
//     lat2->DrawLatex(0.2,0.85,TString::Format("#scale[0.8]{%s}",catdesc.at(i).Data()));
    lat4->DrawLatex(0.535,0.90,TString::Format("B component subtracted"));
    
//     hdummy->SetMaximum(hdatasub->GetMaximum());
//     hdummy->SetMinimum(hdatasub->GetMinimum());
    
    ccat->cd();

    
    ccat->SaveAs(prefix+catnames[i]+".pdf");
    ccat->SaveAs(prefix+catnames[i]+".png");
    ccat->SaveAs(prefix+catnames[i]+".C");
    //ccat->SaveAs(catnames[i]+".C");
    ccat->SaveAs(prefix+catnames[i]+".root");


  } 
  
  
  for (int icat=0; icat<catweights.size(); ++icat) {
    printf("%i: weight = %5f\n",icat,weightscale*catweights.at(icat));
  }


  
}
