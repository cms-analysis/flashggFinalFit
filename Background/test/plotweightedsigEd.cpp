#include "TFile.h"
#include "RooWorkspace.h"
#include "RooRealVar.h"
#include "RooFormulaVar.h"
#include "TSystem.h"
#include "RooPlot.h"
#include "RooAbsData.h"
#include "RooCategory.h"
#include "RooAbsPdf.h"
#include "RooAddPdf.h"
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
#include "TColor.h"
#include "TPaveText.h"
#include "TArrow.h"
#include "RooHist.h"

#include "boost/program_options.hpp"
#include "boost/algorithm/string/split.hpp"
#include "boost/algorithm/string/classification.hpp"
#include "boost/algorithm/string/predicate.hpp"

#ifndef TDRSTYLE_C
#define TDRSTYLE_C
#include "../../tdrStyle/tdrstyle.C"
#include "../../tdrStyle/CMS_lumi.C"
#endif 

using namespace RooFit;
using namespace std;
using namespace boost;
namespace po = boost::program_options;


string filenameStr_;
vector<string> filename_;
vector<string> filelabels_;
string name_="default";
string filelabelsStr_;
float intLumi_;
bool verbose_;
bool drawZeroBins_ ;
bool quoteMu_;

void OptionParser(int argc, char *argv[]){
	po::options_description desc1("Allowed options");
	desc1.add_options()
		("help,h",                                                                                			"Show help")
		("infilename,i", po::value<string>(&filenameStr_),                                           			"Input file name")
		("name", po::value<string>(&name_)->default_value("CMS-HGG_hgg_"), 			"Prefix for plots")
		("labels", po::value<string>(&filelabelsStr_)->default_value("file0,file1,file2"), 			"Labels for the individual files for the legend")
		("lumi", po::value<float>(&intLumi_)->default_value(12.9), 			"IntLumi")
		("verbose,v", po::value<bool>(&verbose_)->default_value(0),       "verbose")
		("quoteMu", po::value<bool>(&quoteMu_)->default_value(1),       "set 0 to not quote mu eg for fiducial XS result")
		("drawZeroBins", po::value<bool>(&drawZeroBins_)->default_value(1),       "Draw data points if zero events in that bin?")
		;                                                                                             		
	po::options_description desc("Allowed options");
	desc.add(desc1);

	po::variables_map vm;
	po::store(po::parse_command_line(argc,argv,desc),vm);
	po::notify(vm);
	if (vm.count("help")){ cout << desc << endl; exit(1);}
	
	split(filename_,filenameStr_,boost::is_any_of(","));
	split(filelabels_,filelabelsStr_,boost::is_any_of(","));

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
//Double_t effSigma(TH1 * hist, double quantile=TMath::Erf(1.0/sqrt(2.0)))
vector<float> effSigma(TH1 * hist, double quantile=TMath::Erf(1.0/sqrt(2.0)))
{

  vector<float> retvec(2,-1.);

  TAxis *xaxis = hist->GetXaxis();
  Int_t nb = xaxis->GetNbins();
  if(nb < 10) {
    cout << "effsigma: Not a valid histo. nbins = " << nb << endl;
    //return 0.;
    return retvec;
  }
  
  Double_t bwid = xaxis->GetBinWidth(1);
  if(bwid == 0) {
    cout << "effsigma: Not a valid histo. bwid = " << bwid << endl;
    //return 0.;
    return retvec;
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
  float sigeffmin=-1.;
  float sigeffmax=-1.;
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
      sigeffmin = xk+dxf;
      sigeffmax = xj+bwid;
    }   
  }
  if(ismin == nrms || ismin == -nrms) ierr=3;
  if(ierr != 0) cout << "effsigma: Error of type " << ierr << endl;
  
  //return widmin;
  retvec[0] = sigeffmin;
  retvec[1] = sigeffmax;
  return retvec;
}

//from original signal script
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


// colour assigment functions, adapted from S. Breeze
int ReturnColor(int pos, int max)
{
    double modifier(0.20), colorIndex;
    int colour(1);
    double fraction = (double)(pos)/(double)(max-1);

    if( pos > max-1 || pos < 0 || max < 0 ) colour = 1;
    else
    {
        colorIndex = (fraction * (1.0-2.0*modifier) + modifier) * gStyle->GetNumberOfColors();
        colour = gStyle->GetColorPalette(colorIndex);
    }
    return colour;
}
template<class T>
void SetColor(T * obj, int pos, int max)
{
    int colour = ReturnColor(pos, max);
    obj->SetLineColor(colour);
    obj->SetMarkerColor(colour);
}


// to get the MC data sets
map<string,RooDataSet*> getFlashggData(RooWorkspace *work, std::vector<TString> catNames, int m_hyp){
  map<string,RooDataSet*> result;

  for (int cat=0; cat<catNames.size(); cat++){
    catNames[cat].ReplaceAll("_13TeV","");
    if( catNames[cat].Contains("combcat") ) continue;
    result.insert(pair<string,RooDataSet*>(Form("%s",catNames[cat].Data()),(RooDataSet*)work->data(Form("sig_mass_m%3d_%s",m_hyp,catNames[cat].Data()))));
  }
  result.insert(pair<string,RooDataSet*>("all",(RooDataSet*)work->data(Form("sig_mass_m%3d_AllCats",m_hyp))));

  return result;
}


int main(int argc, char *argv[]) {
   
  vector<int> colorVector ={2,4,3,6,7,9};
   
  //load style
  gROOT->Macro("$CMSSW_BASE/src/flashggFinalFit/tdrStyle/hggPaperStyle.C");
  //gROOT->Macro("$CMSSW_BASE/src/flashggFinalFit/tdrStyle/tdrstyle.C");
  OptionParser(argc,argv);
  gStyle->SetOptStat(0);
  gStyle->SetPadTickX(1);  
  gStyle->SetPadTickY(1);   
  gROOT->ForceStyle();    

  
  // set output plot name prefix and set outpit dir
  if (verbose_) std::cout << "[INFO] Set plot prefix to " << name_ << std::endl; 
  TString prefix = name_;
  TString dirname = ".";
  gSystem->mkdir(dirname,true);
  gSystem->cd(dirname);
  const double leftpos = 102.0;
  
  //holder for the plots
  std::vector<std::map<TString,TH1D*> > histogramVector; //first vector is for files, second is for cats
  std::vector<std::vector<TString> > catdescVector; //first vector is for files, second is for cats
  std::vector<std::vector<TString> > catnamesVector; //first vector is for files, second is for cats
  //std::vector<TString> catdesc;
  //std::vector<TString> catnames;  
  std::vector<double> catweightsFinal;

  // now loop through the input files

  for (int iFile=0; iFile < filename_.size(); iFile++){
    
    //open the file 
    TFile *fin = TFile::Open(filename_[iFile].c_str());
    if (verbose_) std::cout << "[INFO] Opened file " << filename_[iFile].c_str() << " pointer "<<  fin << std::endl; 
    
    //get workspace and dataset, and vairoubles RooFit vairables
    RooWorkspace *win = (RooWorkspace*)fin->Get("w");  
    RooWorkspace *winbis = win;    
    RooAbsData *datain = winbis->data("data_obs");
    RooRealVar *weightVar = new RooRealVar("weightvar","",1.);
    if (verbose_) std::cout << "[INFO] Loading  workspace "<< winbis << ", dataobs " << datain << " and weight"  << weightVar<< std::endl;  
    RooDataSet *data = new RooDataSet("data_obs_unbinned","",*datain->get());
    RooRealVar *MH = win->var("MH");
    RooRealVar *r = win->var("r");
    if (verbose_) std::cout << " VALUES OF MH " << MH->getVal() << " and r " << r->getVal() <<std::endl;
    TFile *ftmp = new TFile("tmpfile.root","RECREATE");
    RooRealVar *mass = win->var("CMS_hgg_mass");
    mass->SetTitle("#m_{#gamma#gamma}");
    mass->setUnit("GeV");
    RooCategory *chan = win->cat("CMS_channel");
    

    // make a new dataset with the weights set to 1
    if (verbose_) std::cout << "[INFO]  make roodataset and FILL IT " << std::endl; 
    for (int idat=0; idat<datain->numEntries(); ++idat) {
      const RooArgSet *dset = datain->get(idat);
      int nent = int(datain->weight());
      for (int ient=0; ient<nent; ++ient) {
        data->add(*dset);
      }
    }
    
    //load sig/bkg pdf params from fit, and get PDFs
    //win->loadSnapshot("MultiDimFit"); 
    RooFitResult *fit_s = 0;
    RooSimultaneous *sbpdf = (RooSimultaneous*)win->pdf("model_s");
    RooSimultaneous *bpdf = (RooSimultaneous*)win->pdf("model_b");
    if (verbose_) std::cout << "[INFO]  get pdfs " << sbpdf << " " << bpdf << std::endl; 

    // define some of the new RooRealVars which we will need for calculations
    RooRealVar *massrel = new RooRealVar("massrel","",1.0,0.0,10.0); 
    massrel->removeRange();
    RooRealVar *sigmaeff = new RooRealVar("sigmaeff","",1.0,0.0,10.0); //effective sigma
    RooRealVar *sob = new RooRealVar("sob","",1.0,0.0,10.0); // signal over background
    sob->removeRange();
    RooRealVar *sobres = new RooRealVar("sobres","",1.0,0.0,10.0);
    sobres->removeRange();  
    RooRealVar *llrweight = new RooRealVar("llrweight","",1.0,0.0,10.0);
    llrweight->removeRange();  
    RooFormulaVar *massrelf = new RooFormulaVar("massrel","","(@0-@1)/@2",RooArgList(*mass,*MH,*sigmaeff));
    std::vector<double> sigmaeffs;
    
    //new datasets used for calculations
    RooDataSet *wdata = new RooDataSet("wdata","",RooArgSet(*chan,*mass,*sobres),"sobres");
    RooDataSet *wdatarel = new RooDataSet("wdata","",RooArgSet(*chan,*massrel,*sob),"sob");  
    RooDataSet *wdatallr = new RooDataSet("wdata","",RooArgSet(*chan,*mass,*llrweight),"llrweight");
    

    // some doubles and vectors needed for calculations
    double nbweight = 0;
    double nsbweight = 0;
    double nsweight = 0;
    double stotal = 0;
    double btotal = 0;
    double sbtotal = 0;
    if (verbose_) std::cout << "[INFO] preparing weights verctor.." << std::endl; 
    std::vector<double> catweights;
    RooArgList wcatnorms;
    std::vector<RooAbsData*> catdatams;
    std::vector<RooAbsData*> bcatdatams; 
    std::vector<TString> catdesc;
    std::vector<TString> catnames; 
    std::map<TString,TH1D*> histogramMap;
    double sigeffmin = 999;

    // set the names of the categories
    for (int i=0; i<chan->numTypes(); ++i) {
      chan->setIndex(i);
      printf("[INFO] Channel %i: %s\n",i,chan->getLabel());
      catnames.push_back(std::string(chan->getLabel()));
      TString desc = Form("#splitline{%s}{}",chan->getLabel());
      //make human readable labels
      desc.ReplaceAll("_"," ");
      desc.ReplaceAll("13TeV","");
      desc.ReplaceAll("UntaggedTag","Untagged");
      desc.ReplaceAll("VBFTag","VBF Tag");
      desc.ReplaceAll("TTHLeptonicTag","TTH Leptonic Tag");
      desc.ReplaceAll("TTHHadronicTag","TTH Hadronic Tag");
      desc.ReplaceAll("SigmaMpTTag","#sigma_{M}/M |_{decorr} category");
      catdesc.push_back(desc);
      std::cout << "[INFO] --> description :" << desc << std::endl;
    }
    printf("[INFO] Channel %d  : combcat_unweighted",chan->numTypes()+1);
    std::cout << "[INFO] --> description :" << "#splitline{fiducial phase space}{All classes} "<< std::endl;
    catnames.push_back("combcat_unweighted");
    catdesc.push_back("#splitline{All Categories}{}");
    printf("[INFO] Channel %d  : combcat_weighted",chan->numTypes()+2);
    std::cout << "[INFO] --> description :" << "#splitline{fiducial phase space}{S/(S+B) weighted}" << std::endl;
    catnames.push_back("combcat_weighted");
    catdesc.push_back("#splitline{All Categories}{S/(S+B) weighted}");
    
    // loop through categories and make calulcations for nEvents, etc 
    for (int i=0; i<chan->numTypes(); ++i) {
      
      //switch to the categgory
      chan->setIndex(i);
      printf("[INFO] Loop Through Channels, Channel %i\n",i);
      

      //grab the pdfs for that category
      RooAbsPdf *bcatpdf = bpdf->getPdf(chan->getLabel());
      RooAbsPdf *sbcatpdf = sbpdf->getPdf(chan->getLabel());
      std::cout << "[INFO] got background and sig + bkg pdfs "<< bcatpdf << " " << sbcatpdf << std::endl;
      

      //get the number of events for Sig and Bkg and sum
      double sbevents = sbcatpdf->expectedEvents(*mass);    
      double bevents = bcatpdf->expectedEvents(*mass);
      double sevents = sbevents - bevents;
      std::cout << "[INFO] number of events  sbevents  " << sbevents << " bevents " << bevents << " sevents " << std::endl;


      //make new signal only pdf
      RooArgList *pdfsForTheAddPdf = new RooArgList( *sbcatpdf, *bcatpdf );
      RooRealVar *sbvalForTheAddPdf = new RooRealVar("sbvalForTheAddPdf","sbvalForTheAddPdf",sbevents);
      RooRealVar *bvalForTheAddPdf = new RooRealVar("bvalForTheAddPdf","bvalForTheAddPdf",-1.*bevents);
      RooArgList *coeffsForTheAddPdf = new RooArgList( *sbvalForTheAddPdf, *bvalForTheAddPdf );
      RooAddPdf *scatpdf = new RooAddPdf( "scatpdf", "scatpdf", *pdfsForTheAddPdf, *coeffsForTheAddPdf );
      

      //make fine-binned histpograms from the PDFs, with the correct number of ecents
      TH1D *hsbtmp = (TH1D*)sbcatpdf->createHistogram("hsbtmp",*mass,Binning(3200));
      TH1D *hbtmp = (TH1D*) bcatpdf->createHistogram("hbtmp",*mass,Binning(3200));
      TH1 *hstmp = new TH1D ( sbevents*(*hsbtmp) - bevents*(*hbtmp) );    
      std::cout << "[INFO] create correct histograms hsbtmp " << hsbtmp->Integral() << " hbtmp " << hbtmp->Integral() << " hstmp " << hstmp->Integral() << std::endl;
      

      //get the effective sigma
      //double sigeffval = effSigma(hstmp);
      vector<float> vecsigeffval = effSigma(hstmp);
      double sigeffval = 0.5*(vecsigeffval[1]-vecsigeffval[0]);
      cout << endl;
      cout << endl;
      cout << endl;
      cout << endl;
      cout << endl;
      //std::pair<double,double> tempSigPair = getEffSigma(mass,scatpdf,115,135);
      std::cout << "[INFO] got effsigma for hstmp                   " << sigeffval << std::endl;
      //std::cout << "[INFO] got second opinion on effsigma for hstmp " << -0.5*(tempSigPair.first-tempSigPair.second) << std::endl;
      cout << endl;
      cout << endl;
      cout << endl;
      cout << endl;
      cout << endl;
      sigmaeffs.push_back(sigeffval);
      if (sigeffval<sigeffmin) sigeffmin = sigeffval;

      delete hsbtmp;
      delete hbtmp;
      delete hstmp;  

      //define range: +/- 1 eff_sigma around the nominal MH
      TString rangename = TString::Format("sigeffrange_%s",chan->getLabel());
      mass->setRange(rangename,MH->getVal()-sigeffval,MH->getVal()+sigeffval);
      
      // get the number of events in that range for Sig and Bkg
      double bdiff = bcatpdf->createIntegral(*mass,*mass,rangename)->getVal()*bevents;
      std::cout << "[INFO] Get backgnd under +/- 1 sigeff   "<<  bcatpdf->createIntegral(*mass,*mass,rangename)->getVal()  << " *  " << bevents << " = " << bdiff << std::endl;
      double sdiff = TMath::Erf(1.0/sqrt(2.0))*sevents;
      std::cout << "[INFO] Get bdiff  "<< bdiff  << " sdiff " << sdiff << std::endl;
      
      //Now calculate the S/(S+B) for this cat!
      double catweight = (sdiff)/(sdiff+bdiff);
      catweights.push_back(catweight);
      std::cout << "[INFO] Get catweight " << std::endl;
      
      // rewight the category by sensitivity in the running sum of events
      nbweight += catweight*bevents;
      nsbweight += catweight*sbevents;
      nsweight += catweight*sevents;
      stotal += sevents;
      btotal += bevents;
      sbtotal += sbevents;
      std::cout << "[INFO] Running totals nbweight   " << nbweight  << " nsbweight " << nsbweight << "  nsweight " << nsweight << " stotal " << stotal<< " btotal " << btotal << " sbtotal " << sbtotal <<  std::endl;

    }
    catweightsFinal = catweights;
    

    // defined total weighted signal and bkg
    double weightscale = stotal/nsweight;
    nsweight*=weightscale;
    nbweight*=weightscale;
    nsbweight*=weightscale;
    std::cout << "[INFO] weightscale " << weightscale << std::endl; 

    // binning
    double lowedge = 100.;
    double highedge = 180;
    int nbins = 80;
    //int nbins = 200000;
    //int nbins = highedge - lowedge;
    //int nbins = 320;
    std::cout << "[INFO] weightscale " << weightscale << std::endl; 

    // holder histograms for sum and weighted sum 
    TH1D *hsig = new TH1D("hsig","",3200,100.,180.);
    TH1D *hwsig = new TH1D("hwsig","",3200,100.,180.);
    TH1D *hbkg = new TH1D("hbkg","",3200,100.,180.);
    TH1D *hwbkg = new TH1D("hwbkg","",3200,100.,180.);
    TH1D *hbkgplot = new TH1D("hbkgplot","",nbins,lowedge,highedge);
    TH1D *hwbkgplot = new TH1D("hwbkgplot","",nbins,lowedge,highedge);
    TH1D *hsigbkg = new TH1D("hsigbkg","",3200,100.,180.);
    TH1D *hwsigbkg = new TH1D("hwsigbkg","",3200,100.,180.);   
    int nbinsfine = 40*(highedge-lowedge);
    //int nbinsfine = 200000;
    TH1D *hbkgplotfine = new TH1D("hbkgplotfine","",nbinsfine,lowedge,highedge);
    TH1D *hwbkgplotfine = new TH1D("hwbkgplotfine","",nbinsfine,lowedge,highedge);
    TH1D *hsigbkgplotfine = new TH1D("hsigbkgplotfine","",nbinsfine,lowedge,highedge);
    TH1D *hwsigbkgplotfine = new TH1D("hwsigbkgplotfine","",nbinsfine,lowedge,highedge);
    TH1D *hsigplotfine = new TH1D("hsigplotfine","",nbinsfine,lowedge,highedge);
    TH1D *hwsigplotfine = new TH1D("hwsigplotfine","",nbinsfine,lowedge,highedge);
    

    //vector of output histogramms
    std::vector<TH1D*> hbkgplots;
    std::vector<TH1D*> hsigplotsfine;
    

    // now loop through the categories again
    for (int i=0; i<chan->numTypes(); ++i) {
      
      //get the correct PDFS for this cat
      printf("[INFO] Loop Through Channels, Channel %i --  %s \n",i,chan->getLabel());
      chan->setIndex(i);
      RooAbsPdf *bcatpdf = bpdf->getPdf(chan->getLabel());
      RooAbsPdf *sbcatpdf = sbpdf->getPdf(chan->getLabel());    
      

      // get the dataset for the car
      RooDataSet *catdata = (RooDataSet*)data->reduce(TString::Format("CMS_channel==CMS_channel::%d",chan->getIndex()));
      printf("[INFO] %s -- catdata entries = %5f\n",chan->getLabel(),catdata->sumEntries());
      RooAbsData *catdatam = catdata->reduce(*mass);
      RooDataHist *bcatdatam = new RooDataHist(TString::Format("bcatdatam_%i",i),"",*catdatam->get(),*catdatam);
      catdatams.push_back(catdatam);
      bcatdatams.push_back(bcatdatam);

      //weights and numer of s and b events
      double catweight = weightscale*catweights[i];
      double sbevents = sbcatpdf->expectedEvents(*mass);    
      double bevents = bcatpdf->expectedEvents(*mass);
      double sevents = sbevents - bevents;

      //temp histograms for s+B, S and B, normalized
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
      
      //fill the histoprgams for the sum and weighted sum
      hsigbkg->Add(hsbtmp,sbevents);
      hwsigbkg->Add(hsbtmp,catweight*sbevents);
      hbkg->Add(hbtmp,bevents);
      hwbkg->Add(hbtmp,catweight*bevents);
      hbkgplot->Add(hbplottmp,bevents);
      hwbkgplot->Add(hbplottmp,catweight*bevents);
      hbkgplotfine->Add(hbplotfinetmp,bevents);
      hwbkgplotfine->Add(hbplotfinetmp,catweight*bevents);    
      hsigbkgplotfine->Add(hsbplotfinetmp,sbevents);
      hwsigbkgplotfine->Add(hsbplotfinetmp,catweight*sbevents);    
      hsigplotfine->Add(hsbplotfinetmp,sbevents);
      hwsigplotfine->Add(hsbplotfinetmp,catweight*sbevents);    
      TH1 *hstmp = new TH1D ( sbevents*(*hsbtmp) - bevents*(*hbtmp) );
      hsig->Add(hstmp);
      TH1 *hwstmp = new TH1D ( catweight*(sbevents*(*hsbtmp) - bevents*(*hbtmp)) );
      hwsig->Add(hwstmp);
      TH1D *hbkgplot_cat = new TH1D(TString::Format("hbkgplot_%s",catnames[i].Data()),"",nbins,lowedge,highedge);
      hbkgplot_cat->Add(hbplottmp,bevents);
      hbkgplots.push_back(hbkgplot_cat);
      TH1D *hsigplot_cat = new TH1D(TString::Format("hsigplot_cat%s",catnames[i].Data()),"",3200,100.,180.);
      hsigplot_cat->Add(hstmp);
      hsigplotsfine.push_back(hsigplot_cat);
      histogramMap[catnames[i].Data()]=hsigplot_cat;

      delete hsbtmp;
      delete hbtmp;
      delete hbplottmp;
      delete hstmp;    
      delete hwstmp;    
      delete hsbplotfinetmp;
      delete hbplotfinetmp;
      

      // get the normalization of the category in bkg
      RooAbsReal *catnorm = win->var(TString::Format("shapeBkg_bkg_mass_%s__norm",chan->getLabel()));
      RooProduct *wcatnorm = new RooProduct(TString::Format("%s_wcatnorm",chan->getLabel()),"",RooArgSet(RooConst(catweight),*catnorm));
      wcatnorms.add(*wcatnorm);
      sobres->setVal(catweight);
      catdata->addColumn(*sobres);
      RooDataSet *wcatdata = new RooDataSet("wcatdata","",catdata,RooArgSet(*chan,*mass,*sobres),0,"sobres");
      wdata->append(*wcatdata);

      delete wcatdata;
    }
    

    //add the plots to thevectors of TH1s
    hbkgplots.push_back(hbkgplot);
    hbkgplots.push_back(hwbkgplot);
    hsigplotsfine.push_back(hsig); // sum
    histogramMap[catnames[chan->numTypes()].Data()]=hsig;
    hsigplotsfine.push_back(hwsig); //weightedsum
    histogramMap[catnames[chan->numTypes()+1].Data()]=hwsig;

    // set mass range around the Higgs 
    mass->setRange("binrange",124.5,125.5);
    mass->setRange("fullrange",124.5,125.5);  
    


    //new TCanvas;
    //hsig->Draw();
    

    // get sigma_eff for direct sum and weighted sum
    //double sigmaeffall = effSigma(hsig);
    //double sigmaeffw = effSigma(hwsig);

    // get number of cats in this file
    const int ncats = chan->numTypes();
    

    // get the nomalisation and apply it to the datasets 
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
    for (int isig=0; isig<hsigplotsfine.size(); ++isig) {
      hsigplotsfine[isig]->Scale(curvescale);
    }

    // make the frame to plot the PDFs, and define some style parameters
    RooPlot *plot = mass->frame(lowedge,highedge,nbins); 
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


  histogramVector.push_back(histogramMap);
  catdescVector.push_back(catdesc);
  catnamesVector.push_back(catnames);
  } // end of loop over files


  //get MC datasets 
  //TFile *hggFile = TFile::Open("../../Signal/outdir_EdWeightTest/CMS-HGG_sigfit_EdWeightTest.root");
  TFile *hggFile = TFile::Open("/vols/build/cms/es811/FreshStart/Pass6/CMSSW_7_4_7/src/flashggFinalFit/Signal/outdir_ws919/CMS-HGG_sigfit_ws919.root");
  RooWorkspace *hggWS;
  int sqrts_ = 13;
  hggWS = (RooWorkspace*)hggFile->Get(Form("wsig_%dTeV",sqrts_));
  if (!hggWS) {
    cerr << "Workspace is null" << endl;
    exit(1);
  }
  RooRealVar *mcMass= (RooRealVar*)hggWS->var("CMS_hgg_mass");
  RooRealVar *mcMh = (RooRealVar*)hggWS->var("MH");
  mcMh->setVal(125);
  mcMass->setRange("higgsRange",105.,140.);
  map<string,RooDataSet*> dataSets;
  dataSets = getFlashggData( hggWS, catnamesVector[0], 125 );
  TH1* hWeightedMC =  new TH1F("hWeightedMC","desc",70,105.,140.);
  vector<TString> mcCatNames = catnamesVector[0];
  vector<TH1*> vecMChists;
  for( int icat=0; icat<mcCatNames.size(); icat++ ) {
    if( mcCatNames[icat].Contains("combcat") ) continue;
    mcCatNames[icat].ReplaceAll("_13TeV","");
    vecMChists.push_back( dataSets[mcCatNames[icat].Data()]->createHistogram(Form("hTempMC%i",icat), *mcMass, Binning(70,105.,140.)) );
    hWeightedMC->Add(vecMChists[icat],catweightsFinal[icat]);
  }
  vecMChists.push_back( dataSets["all"]->createHistogram("hAllUnweighted", *mcMass, Binning(70,105.,140.)) );
  vecMChists.push_back( hWeightedMC );


  //gStyle->SetPalette(57);
  for (int iCat=0 ; iCat < catnamesVector[0].size(); iCat++){
    TString thisCatName =catnamesVector[0][iCat] ; 
    TString thisCatDesc =catdescVector[0][iCat] ; 
    if(verbose_) std::cout << "now considering category " <<thisCatName <<std::endl;  
    //make a dummy histogram for plotting
    double lowedge = 105.;
    double highedge = 140;
    int nbins = 35;
    double deflinewidth = 3.0;
    double defmarkersize = 0.8;
    int defmarkerstyle = 20;
    double errlinewidth = 1.0;
    double offset=0.05;
    TH1F *hdummy = new TH1F("hdummy","",nbins,lowedge,highedge);
    //hdummy->SetMaximum(1.2*(histogramVector[0][thisCatName]->GetMaximum()/histogramVector[0][thisCatName]->Integral()));
    //hdummy->SetMaximum(1.1*(histogramVector[0][thisCatName]->GetMaximum()/histogramVector[0][thisCatName]->Integral()));
    hdummy->SetMaximum(1.15*(histogramVector[0][thisCatName]->GetMaximum()));
    hdummy->SetMinimum(0.);
    hdummy->GetXaxis()->SetTitle("m_{#gamma#gamma} (GeV)");
    hdummy->GetXaxis()->SetTitleSize(0.05);
    //hdummy->GetYaxis()->SetLabelSize(0.03);
    hdummy->GetYaxis()->SetTitle("a.u.");
    hdummy->GetYaxis()->SetTitleSize(0.05);
    //hdummy->GetYaxis()->SetLabelSize(0.03);
    hdummy->GetYaxis()->SetTitleOffset(1.5);
    hdummy->SetLineColor(kWhite);
    hdummy->GetYaxis()->SetNdivisions(808);

    TLatex  lat1(.129+0.03+offset,0.85,"H#rightarrow#gamma#gamma");
    lat1.SetNDC(1);
    lat1.SetTextSize(0.047);
    TLatex lat2(0.88,0.88,thisCatDesc);
    //TLatex lat2(0.95,0.88,TString::Format("#scale[1.0]{%s}",thisCatDesc.Data()));
    lat2.SetTextAlign(33);
    lat2.SetNDC(1);
    //lat2.SetTextSize(0.045);
    lat2.SetTextSize(0.04);
    //lat2.SetTextSize(0.035);
    //TLatex lat3(0.31,0.93,"#it{Simulation Preliminary}          13 TeV");
    TLatex lat3(0.31,0.93,"#it{Simulation}                             13 TeV"); // for the paper
    lat3.SetNDC(1);
    lat3.SetTextSize(0.045);

    TLegend *leg = new TLegend(0.15+offset,0.40,0.5+offset,0.82);
    leg->SetFillStyle(0);
    leg->SetLineColor(0);
    leg->SetTextSize(0.037);

    TCanvas *ccat = new TCanvas("canv","canv",650,600);
    ccat->SetLeftMargin(0.16);
    ccat->SetTickx();
    ccat->SetTicky();
    hdummy->Draw("HIST");

    TH1* hMChist = vecMChists[iCat];
    if (verbose_) cout << "hMChist = " << hMChist << endl;
    if (verbose_) cout << "hMChist entries = " << hMChist->GetEntries() << endl;

    float fwmin  = 0.;
    float fwmax = 0.;
    float halfmax = 0.;
    for (int iFile=0; iFile < filename_.size(); iFile++)
    {
      TH1D *hsigplotfine = histogramVector[iFile][thisCatName];
      //hsigplotfine->SetLineColor(colorVector[iFile]);
      hsigplotfine->SetLineColor(kBlue);
      hsigplotfine->SetLineWidth(1.5);
      TH1D *hsigplotfinesigmaeff = (TH1D*)hsigplotfine->Clone("hsigplotfinesigmaeff");
      vector<float> vecsigmaeff = effSigma( hsigplotfine );
      hsigplotfinesigmaeff->GetXaxis()->SetRangeUser(vecsigmaeff[0],vecsigmaeff[1]);
      hsigplotfinesigmaeff->SetLineColor(15);
      hsigplotfinesigmaeff->SetLineWidth(2);
      hsigplotfinesigmaeff->SetFillColor(19);
      hsigplotfinesigmaeff->SetFillStyle(1001);
      hsigplotfinesigmaeff->Draw("HISTSAME,F");
      hsigplotfine->Draw("HISTSAME");
      hMChist->SetMarkerStyle(kOpenSquare);
      float tempScale = hsigplotfine->Integral("width");
      float tempNorm  = hMChist->Integral("width");
      hMChist->Scale(tempScale/tempNorm);
      hMChist->Draw("SAME");

      leg->AddEntry(hMChist,"Simulation","lep");
      leg->AddEntry(hsigplotfine,"#splitline{Parametric}{model}","l");
      leg->AddEntry(hsigplotfinesigmaeff,Form("#sigma_{eff} = %1.2f GeV",0.5*(vecsigmaeff[1]-vecsigmaeff[0])),"fl");
      halfmax = 0.5*hsigplotfine->GetMaximum();
      fwmin = hsigplotfine->GetBinCenter(hsigplotfine->FindFirstBinAbove(halfmax));
      fwmax = hsigplotfine->GetBinCenter(hsigplotfine->FindLastBinAbove(halfmax));
      //halfmax = halfmax / hsigplotfine->Integral();

      //offset=offset+0.11;
    }

    TArrow *fwhmArrow = new TArrow(fwmin,halfmax,fwmax,halfmax,0.02,"<>");
    fwhmArrow->SetLineWidth(2.);
    TPaveText *fwhmText = new TPaveText(0.17+offset,0.3,0.45+offset,0.40,"brNDC");
    fwhmText->SetFillColor(0);
    fwhmText->SetLineColor(kWhite);
    fwhmText->SetTextSize(0.037);
    fwhmText->AddText(Form("FWHM = %1.2f GeV",(fwmax-fwmin)));

    //if (data) leg->AddEntry(dataLeg,"#bf{Simulation}","lep");
    fwhmArrow->Draw("same <>");
    fwhmText->Draw("same");
    lat2.Draw("same");
    lat1.Draw("same");
    lat3.Draw("same");
    leg->Draw("same");
    string sim="Simulation Preliminary";
    CMS_lumi(ccat,0,0,sim);
    ccat->SaveAs(prefix+thisCatName+".pdf");
    ccat->SaveAs(prefix+thisCatName+".png");
    ccat->SaveAs(prefix+thisCatName+".C");
    ccat->SaveAs(prefix+thisCatName+".root");
    delete ccat;
    delete hdummy;
  }
}
