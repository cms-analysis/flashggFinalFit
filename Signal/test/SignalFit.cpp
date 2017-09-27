#include <iostream>
#include <fstream>
#include <string>
#include <map>
#include <vector>
#include <typeinfo>

#include "TROOT.h"
#include <TStyle.h>
#include "TFile.h"
#include "TMath.h"
#include "TH2.h"
#include "TStopwatch.h"
#include "RooWorkspace.h"
#include "RooDataSet.h"
#include "RooDataHist.h"
#include "TKey.h"
#include "TMacro.h"
#include "TClass.h"
#include "TIterator.h"
#include "TRandom3.h"
#include "HiggsAnalysis/CombinedLimit/interface/RooSpline1D.h"

#include "../interface/SimultaneousFit.h"
#include "../interface/InitialFit.h"
#include "../interface/LinearInterp.h"
#include "../interface/FinalModelConstruction.h"
#include "../interface/Packager.h"
#include "../interface/WSTFileWrapper.h"

#include "boost/program_options.hpp"
#include "boost/algorithm/string/split.hpp"
#include "boost/algorithm/string/classification.hpp"
#include "boost/algorithm/string/predicate.hpp"

using namespace std;
using namespace RooFit;
using namespace boost;
namespace po = boost::program_options;

typedef map<int,map<string,RooRealVar*> > parlist_t;
typedef map<pair<string,string>, std::pair<parlist_t,parlist_t> > parmap_t;
typedef map<pair<string,string>,map<string,RooSpline1D*> > clonemap_t;

string filenameStr_;
vector<string> filename_;

string outfilename_;
string mergefilename_;
string datfilename_;
string systfilename_;
string plotDir_;
//bool skipPlots_=false;
bool skipPlots_=true;
int mhLow_=115;
int mhHigh_=135;
int nCats_;
float constraintValue_;
float iterativeFitConstraint_;
int constraintValueMass_;
bool spin_=false;
vector<string> procs_;
string procStr_;
bool isCutBased_=false;
bool is2011_=false;
bool is2012_=false;
string massesToSkip_;
vector<int> skipMasses_;
string massListStr_;
vector<int> massList_;
bool splitRVWV_=true;
bool doSecondaryModels_=false;
bool useSSF_=false;
bool doQuadraticSigmaSum_=false;
bool runInitialFitsOnly_=false;
bool cloneFits_=false;
bool replace_=false;
//pair<string,string> replaceWith_RV_;
//pair<string,string> replaceWith_WV_;
string cloneFitFile_;
bool recursive_=true;
string highR9cats_;
string lowR9cats_;
int verbose_=0;
int ncpu_=1;
int sqrts_=13;
int pdfWeights_=26;
vector<int> cats_;
string catsStr_;
bool isFlashgg_;
bool binnedFit_;
int  nBins_;
string flashggCatsStr_;
vector<string> flashggCats_;
bool checkYields_;
bool useMerged_;
vector<string>  split_;
string  splitStr_;
float newIntLumi_;
float originalIntLumi_;
float mcBeamSpotWidth_=5.14; //cm // the beamspot has a certain width in MC which is not necessarily the same in data. for the data/MC to agree, we reweight the MC to match the data Beamspot width, using dZ as a proxy (they have a factor of sqrt(2) because you are subtracting one gaussain distributed quantity from another)
//float dataBeamSpotWidth_=4.24; //cm
float dataBeamSpotWidth_=3.5; //cm
//string referenceProc_="ggh";
string referenceProc_="GG2H";
//string referenceProcWV_="ggh";
string referenceProcWV_="GG2H";
//string referenceProcTTH_="tth";
string referenceProcTTH_="TTH";
string referenceTagWV_="UntaggedTag_2";
string referenceTagRV_="UntaggedTag_2";
vector<string> map_proc_;
vector<string> map_cat_;
vector<string> map_replacement_proc_RV_;
vector<string> map_replacement_cat_RV_;
vector<string> map_replacement_proc_WV_;
vector<string> map_replacement_cat_WV_;
vector<int> map_nG_rv_;
vector<int> map_nG_wv_;
RooRealVar *mass_;
RooRealVar *dZ_;
RooRealVar *intLumi_;
bool beamSpotReweigh_ = false;
bool useDCBplusGaus_ = false;

void OptionParser(int argc, char *argv[]){
	po::options_description desc1("Allowed options");
	desc1.add_options()
		("help,h",                                                                                			"Show help")
		("infilename,i", po::value<string>(&filenameStr_),                                           			"Input file name")
		("outfilename,o", po::value<string>(&outfilename_)->default_value("CMS-HGG_sigfit.root"), 			"Output file name")
		("merge,m", po::value<string>(&mergefilename_)->default_value(""),                               	        "Merge the output with the given workspace")
		("datfilename,d", po::value<string>(&datfilename_)->default_value("dat/newConfig.dat"),      			"Configuration file")
		("systfilename,s", po::value<string>(&systfilename_)->default_value("dat/photonCatSyst.dat"),		"Systematic model numbers")
		("plotDir,p", po::value<string>(&plotDir_)->default_value("plots"),						"Put plots in this directory")
		("skipPlots", 																																									"Do not make any plots")
		("mhLow,L", po::value<int>(&mhLow_)->default_value(115),                                  			"Low mass point")
		("mcBeamSpotWidth", po::value<float>(&mcBeamSpotWidth_)->default_value(5.14),                                  			"Default width of MC beamspot")
		("dataBeamSpotWidth", po::value<float>(&dataBeamSpotWidth_)->default_value(3.50),                                  			"Default width of data beamspot")
		("nThreads,t", po::value<int>(&ncpu_)->default_value(ncpu_),                               			"Number of threads to be used for the fits")
		("mhHigh,H", po::value<int>(&mhHigh_)->default_value(135),                                			"High mass point")
		("iterativeFitConstraint_,C", po::value<float>(&iterativeFitConstraint_)->default_value(0.1),            			"Constraint value for iterative fit (for SSF)(0.1 is +/- 10%)")
		("useSSF", po::value<bool>(&useSSF_)->default_value(false),"Use a simulatenous fit of all mass points where the params of the functional form are functions of MH")
		("constraintValueMass,M", po::value<int>(&constraintValueMass_)->default_value(125),                        "Constraint value mass")
		("pdfWeights", po::value<int>(&pdfWeights_)->default_value(0),                        "If pdf systematics should be considered, say how many (default 0 = off)")
		("skipSecondaryModels",                                                                   			"Turn off creation of all additional models")
		("doQuadraticSigmaSum",  										        "Add sigma systematic terms in quadrature")
		("procs", po::value<string>(&procStr_)->default_value("ggh,vbf,wh,zh,tth"),					"Processes (comma sep)")
		("massList", po::value<string>(&massListStr_)->default_value("120,125,130"),					"Masses to process.")
		("skipMasses", po::value<string>(&massesToSkip_)->default_value(""),					"Skip these mass points - used eg for the 7TeV where there's no mc at 145")
		("runInitialFitsOnly",                                                                                      "Just fit gaussians - no interpolation, no systematics - useful for testing nGaussians")
		("cloneFits", po::value<string>(&cloneFitFile_),															"Do not redo the fits but load the fit parameters from this workspace. Pass as fileName:wsName.")
		("nonRecursive",                                                                             		"Do not recursively calculate gaussian fractions")
		("verbose,v", po::value<int>(&verbose_)->default_value(0),                                			"Verbosity level: 0 (lowest) - 3 (highest)")
		("isFlashgg",	po::value<bool>(&isFlashgg_)->default_value(true),														"Use flashgg format")
		("binnedFit",	po::value<bool>(&binnedFit_)->default_value(true),														"Binned Signal fit")
		("nBins",	po::value<int>(&nBins_)->default_value(80),														"If using binned signal for fit, how many bins in 100-180?")
		("checkYields",	po::value<bool>(&checkYields_)->default_value(false),														"Use flashgg format (default false)")
		("beamSpotReweigh",	po::value<bool>(&beamSpotReweigh_)->default_value(false),														"Reweight events to  discrepancy in width of beamspot between data and MC")
		("useDCBplusGaus",	po::value<bool>(&useDCBplusGaus_)->default_value(false),														"Use Double Crystal Ball plus 1 Gaussian to do fits instead of a sum of Gaussians")
      ("split", po::value<string>(&splitStr_)->default_value(""), "do just one tag,proc ")
		("changeIntLumi",	po::value<float>(&newIntLumi_)->default_value(0),														"If you want to specify an intLumi other than the one in the file. The event weights and rooRealVar IntLumi are both changed accordingly. (Specify new intlumi in fb^{-1})")
		("flashggCats,f", po::value<string>(&flashggCatsStr_)->default_value("UntaggedTag_0,UntaggedTag_1,UntaggedTag_2,UntaggedTag_3,UntaggedTag_4,VBFTag_0,VBFTag_1,VBFTag_2,TTHHadronicTag,TTHLeptonicTag,VHHadronicTag,VHTightTag,VHLooseTag,VHEtTag"),       "Flashgg categories if used")
		;                                                                                             		
	po::options_description desc("Allowed options");
	desc.add(desc1);

	po::variables_map vm;
	po::store(po::parse_command_line(argc,argv,desc),vm);
	po::notify(vm);
	if (vm.count("help")){ cout << desc << endl; exit(1);}
	if (vm.count("skipPlots"))								skipPlots_=true;
	if (vm.count("spin"))                     spin_=true;
	if (vm.count("isCutBased"))               isCutBased_=true;
	if (vm.count("is2011"))               		is2011_=true;
	if (vm.count("is2011"))               		sqrts_=7;
	if (vm.count("is2012"))               		is2012_=true;
	if (vm.count("is2012"))               		sqrts_=8;
	if (vm.count("runInitialFitsOnly"))       runInitialFitsOnly_=true;
	if (vm.count("cloneFits"))								cloneFits_=true;
	if (vm.count("nosplitRVWV"))              splitRVWV_=false;
	if (vm.count("doQuadraticSigmaSum"))			doQuadraticSigmaSum_=true;
	if (vm.count("skipSecondaryModels"))      doSecondaryModels_=false;
	if (vm.count("nonRecursive"))                recursive_=false;
	if (vm.count("skipMasses")) {
		cout << "[INFO] Masses to skip... " << endl;
		vector<string> els;

    // if you want to skip masses for some reason...
		split(els,massesToSkip_,boost::is_any_of(","));
		if (els.size()>0 && massesToSkip_!="") {
			for (vector<string>::iterator it=els.begin(); it!=els.end(); it++) {
				skipMasses_.push_back(boost::lexical_cast<int>(*it));
			}
		}
		cout << "\t";
		for (vector<int>::iterator it=skipMasses_.begin(); it!=skipMasses_.end(); it++) cout << *it << " ";
		cout << endl;
	}
	if (vm.count("massList")) {
		cout << "[INFO] Masses to process... " << endl;
		vector<string> els;

    // if you want to skip masses for some reason...
		split(els,massListStr_,boost::is_any_of(","));
		if (els.size()>0 && massListStr_!="") {
			for (vector<string>::iterator it=els.begin(); it!=els.end(); it++) {
				massList_.push_back(boost::lexical_cast<int>(*it));
			}
		}
		cout << "\t";
		for (vector<int>::iterator it=massList_.begin(); it!=massList_.end(); it++) cout << *it << " ";
		cout << endl;
	}
	
  // split options which are fiven as lists
  split(procs_,procStr_,boost::is_any_of(","));
	split(flashggCats_,flashggCatsStr_,boost::is_any_of(","));
	split(filename_,filenameStr_,boost::is_any_of(","));
  split(split_,splitStr_,boost::is_any_of(",")); // proc,cat

}

// used to get index of the reference dataset in the list of requried guassians.
unsigned int getIndexOfReferenceDataset(string proc, string cat){
  int iLine =-1;
  for(unsigned int i =0 ; i < map_proc_.size() ; i++){
    string this_process = map_proc_[i];
    string this_cat = map_cat_[i];
    if (this_process.compare(proc) ==0 ){
      if ( this_cat.compare(cat)==0 ){ 
        iLine=i;
        break;
      }
    }
  }
  
  if (iLine==-1 ) {
    std::cout << "[ERROR] could not find the index of the category " << proc << ", " << cat << "you wished to look up. Exit!" << std::endl;
     exit(1);
  }
  return iLine;
}


void addToCloneMap(clonemap_t &cloneMap, string proc, string cat, string name, RooSpline1D *spline){

	pair<string,string> mapKey = make_pair(proc,cat);
	if (cloneMap.find(mapKey)==cloneMap.end()){
		map<string,RooSpline1D*> tempMap;
		tempMap.insert(make_pair(name,spline));
		cloneMap.insert(make_pair(mapKey,tempMap));
	} else {
		cloneMap[mapKey].insert(make_pair(name,spline));
	}
}


void makeCloneConfig(clonemap_t mapRV, clonemap_t mapWV, string newdatfilename){

	system("mkdir -p tmp");
	ofstream datfile;
	datfile.open(newdatfilename.c_str());
	if (datfile.fail()) {
		std::cerr << "Could not open " << newdatfilename << std::endl;
		exit(1);
	}
	for (clonemap_t::iterator it=mapRV.begin(); it!=mapRV.end(); it++){
		string proc = it->first.first;
		string cat = it->first.second;
		map<string,RooSpline1D*> paramsRV = it->second;
		map<string,RooSpline1D*> paramsWV = mapWV[make_pair(proc,cat)];
		int countRV=0;
		int countWV=0;
		for (map<string,RooSpline1D*>::iterator pIt=paramsRV.begin(); pIt!=paramsRV.end(); pIt++){
			if (pIt->first.find("dm_g")!=string::npos && pIt->first.find("_SM")==string::npos && pIt->first.find("_2")==string::npos && pIt->first.find("_NW")==string::npos){
				countRV++;
			}
		}
		for (map<string,RooSpline1D*>::iterator pIt=paramsWV.begin(); pIt!=paramsWV.end(); pIt++){
			if (pIt->first.find("dm_g")!=string::npos && pIt->first.find("_SM")==string::npos && pIt->first.find("_2")==string::npos && pIt->first.find("_NW")==string::npos){
				countWV++;
			}
		}
		if (verbose_) cout << "[INFO] "<< proc << " " << cat << " " << countRV << " " << countWV << endl;
		datfile << proc << " " << cat << " " << countRV << " " << countWV << endl;
	}
	datfile.close();

}

RooDataSet * reduceDataset(RooDataSet *data0){

  RooDataSet *data = (RooDataSet*) data0->emptyClone()->reduce(RooArgSet(*mass_, *dZ_));
	RooRealVar *weight0 = new RooRealVar("weight","weight",-100000,1000000);
  for (unsigned int i=0 ; i < data0->numEntries() ; i++){
    mass_->setVal(data0->get(i)->getRealValue("CMS_hgg_mass"));
    weight0->setVal(data0->weight() ); // <--- is this correct?
    dZ_->setVal(data0->get(i)->getRealValue("dZ"));
    data->add( RooArgList(*mass_, *dZ_, *weight0), weight0->getVal() );
    }
return data;
}

// this is where we reweight the DZ distribution as a proxy for the beamspot.
void plotBeamSpotDZdist(RooDataSet *data0, string suffix=""){
  gStyle->SetOptFit(1111);
	RooRealVar *weight0 = new RooRealVar("weight","weight",-100000,1000000);
	TH1F *histSmallDZ = new TH1F ("h1sdz","h1sdz",20,-0.1,0.1);
	TH1F *histLargeDZ = new TH1F ("h1ldz","h1ldz",20,-25,25);

  for (unsigned int i=0 ; i < data0->numEntries() ; i++){
    mass_->setVal(data0->get(i)->getRealValue("CMS_hgg_mass"));
    weight0->setVal(data0->weight() ); // <--- is this correct?
    dZ_->setVal(data0->get(i)->getRealValue("dZ"));
    if (fabs(dZ_->getVal()) <0.1){
		histSmallDZ->Fill( dZ_->getVal(),data0->weight());
		} else {
		histLargeDZ->Fill( dZ_->getVal(),data0->weight());
		}
  }
	TCanvas *c = new TCanvas("c","c",500,500);
	string extra="";
	if (beamSpotReweigh_){
  extra="BS_reweigh";
	}
	histSmallDZ->Draw();
  histSmallDZ->Fit("gaus","Q");
	c->Print(Form("/vols/build/cms/es811/FreshStart/Pass1/AllTags/CMSSW_7_4_7/src/flashggFinalFit/Signal/debug-%s_smallDz_%s_%s.pdf",data0->GetName(),extra.c_str(),suffix.c_str()));
	c->Print(Form("/vols/build/cms/es811/FreshStart/Pass1/AllTags/CMSSW_7_4_7/src/flashggFinalFit/Signal/debug-%s_smallDz_%s_%s.png",data0->GetName(),extra.c_str(),suffix.c_str()));
	histLargeDZ->Draw();
  histLargeDZ->Fit("gaus","Q");
	c->Print(Form("/vols/build/cms/es811/FreshStart/Pass1/AllTags/CMSSW_7_4_7/src/flashggFinalFit/Signal/debug-%s_largeDz_%s_%s.pdf",data0->GetName(),extra.c_str(),suffix.c_str()));
	c->Print(Form("/vols/build/cms/es811/FreshStart/Pass1/AllTags/CMSSW_7_4_7/src/flashggFinalFit/Signal/debug-%s_largeDz_%s_%s.png",data0->GetName(),extra.c_str(),suffix.c_str()));
//	delete c;
	histLargeDZ->Add(histSmallDZ);
	histLargeDZ->Draw();
  histLargeDZ->Fit("gaus","Q");
	c->Print(Form("/vols/build/cms/es811/FreshStart/Pass1/AllTags/CMSSW_7_4_7/src/flashggFinalFit/Signal/debug-%s_totalDz_%s_%s.pdf",data0->GetName(),extra.c_str(),suffix.c_str()));
	c->Print(Form("/vols/build/cms/es811/FreshStart/Pass1/AllTags/CMSSW_7_4_7/src/flashggFinalFit/Signal/debug-%s_totalDz_%s_%s.png",data0->GetName(),extra.c_str(),suffix.c_str()));
	delete histSmallDZ;
	delete histLargeDZ;
  gStyle->SetOptFit();
}

// split a dataset between right vertex (dZ <1cm ) and wrogn vertex (dZ >1cm)
RooDataSet * rvwvDataset(RooDataSet *data0, string rvwv){

  RooDataSet *dataRV = (RooDataSet*) data0->emptyClone()->reduce(RooArgSet(*mass_, *dZ_));
  RooDataSet *dataWV = (RooDataSet*) data0->emptyClone()->reduce(RooArgSet(*mass_, *dZ_));
	RooRealVar *weight0 = new RooRealVar("weight","weight",-100000,1000000);
  for (unsigned int i=0 ; i < data0->numEntries() ; i++){
    mass_->setVal(data0->get(i)->getRealValue("CMS_hgg_mass"));
    weight0->setVal(data0->weight() ); 
		dZ_->setVal(data0->get(i)->getRealValue("dZ"));
    if (fabs(dZ_->getVal() )<1.){
      dataRV->add( RooArgList(*mass_, *dZ_, *weight0), weight0->getVal() );
    } else{
      dataWV->add( RooArgList(*mass_, *dZ_, *weight0), weight0->getVal() );
    }
  }
  if (rvwv.compare("RV") ==0){
    return dataRV;
  } else if (rvwv.compare("WV") ==0){
    return dataWV;
  } else {
    std::cout << "[ERROR] (rvwvDataset) please specific second argument as 'RV' or 'WV'. Exit (1); " << std::endl;
    exit (1);
  }
}

// reweight events according to a specified beamspot distribution width
RooDataSet * beamSpotReweigh(RooDataSet *data0 /*original dataset*/){
  RooDataSet *data = (RooDataSet*) data0->emptyClone();
	RooRealVar *weight0 = new RooRealVar("weight","weight",-100000,1000000);
	//data0->Print();
	//plotBeamSpotDZdist(data0,"before");
  for (int i = 0; i < data0->numEntries(); i++) {
    mass_->setVal(data0->get(i)->getRealValue("CMS_hgg_mass"));
    dZ_->setVal(data0->get(i)->getRealValue("dZ"));
   double factor =1.0;
    
		if (fabs(dZ_->getVal()) < 0.1 ){
    factor =1;
		} else {
    double mcBeamSpot=TMath::Gaus(dZ_->getVal(),0,TMath::Sqrt(2)*mcBeamSpotWidth_,true); 
    double dataBeamSpot=TMath::Gaus(dZ_->getVal(),0,TMath::Sqrt(2)*dataBeamSpotWidth_,true); 
		factor = dataBeamSpot/mcBeamSpot; 
		}
    
		weight0->setVal(factor * data0->weight() ); // <--- is this correct?
    data->add( RooArgList(*mass_, *dZ_, *weight0), weight0->getVal() );
  }
	//data->Print();
	//plotBeamSpotDZdist(data,"after");
  
	if (verbose_) std::cout << "[INFO] Old dataset (before beamSpot  reweight): " << *data0 << std::endl;
  if (verbose_) std::cout << "[INFO] New dataset (after beamSpot reweight):  " << *data << std::endl;
  
  return data;
}

// reweight the events to get a particular intL.
RooDataSet * intLumiReweigh(RooDataSet *data0 /*original dataset*/){
		
  double factor = newIntLumi_/originalIntLumi_; // newIntLumi expressed in 1/fb

  if (verbose_) std::cout << "[INFO] Was able to access IntLumi directlly from WS. IntLumi " << intLumi_->getVal() << "pb^{-1}" << std::endl;
	
  if (verbose_) std::cout << "[INFO] Old int lumi " << originalIntLumi_  <<", new int lumi " << newIntLumi_<< std::endl;
  if (verbose_) std::cout << "[INFO] Changing weights of dataset by a factor " << factor << " as per newIntLumi option" << std::endl;
  
  RooDataSet *data = (RooDataSet*) data0->emptyClone();
	RooRealVar *weight0 = new RooRealVar("weight","weight",-100000,1000000);
  for (int i = 0; i < data0->numEntries(); i++) {
    mass_->setVal(data0->get(i)->getRealValue("CMS_hgg_mass"));
    dZ_->setVal(data0->get(i)->getRealValue("dZ"));
    weight0->setVal(factor * data0->weight() ); // <--- is this correct?
    data->add( RooArgList(*mass_, *dZ_, *weight0), weight0->getVal() );
  }
  if (verbose_) std::cout << "[INFO] Old dataset (before intLumi change): " << *data0 << std::endl;
  if (verbose_) std::cout << "[INFO] New dataset (intLumi change x"<< factor <<"): " << *data << std::endl;
  
  return data;
}

bool skipMass(int mh){
	for (vector<int>::iterator it=skipMasses_.begin(); it!=skipMasses_.end(); it++) {
		if (*it==mh) return true;
	}
	return false;
}

//main code
int main(int argc, char *argv[]){

	gROOT->SetBatch();

	OptionParser(argc,argv);

	TStopwatch sw;
	sw.Start();

  // reference details for low stats cats
  // need to make this configurable ?! -LC
  //referenceProc_="ggh";
  referenceProc_="GG2H";
  //referenceProcTTH_="tth";
  referenceProcTTH_="TTH";
  referenceTagWV_="UntaggedTag_2"; // histest stats WV is ggh Untagged 3. 
  referenceTagRV_="UntaggedTag_2"; // fairly low resolution tag even for ggh, more approprioate as te default than re-using the original tag.
  // are WV which needs to borrow should be taken from here
  
  // isFlashgg should now be the only option.
	if (isFlashgg_){ 
    nCats_= flashggCats_.size();
	} else {
    std::cout << "[ERROR] script is only compatible with flashgg! exit(1)." << std::endl;
    exit(1);
  }
	
  if (useDCBplusGaus_){ 
    std::cout << "[INFO] Using functional form: Double Crystal Ball + 1 Gaussian (same mean)" << std::endl;
  } else {
    std::cout << "[INFO] Using functional form: Sum of N Gaussians " << std::endl;
  }
  
  if (useSSF_){ 
    std::cout << "[INFO] Using fitting strategy: Simultaneous Signal Fitting (Simultaneous fit of all mass points, where functional form parameters are themselves functions of MH) " << std::endl;
  } else {
    std::cout << "[INFO] Using fitting strategy: Fit each mass point and perform linear interpolation of parameters " << std::endl;
  }
  
  // open sig file
	//TFile *inFile = TFile::Open(filename_[0].c_str());

  // extract nEvents per proc/tag etc...
	if (checkYields_){
	  
    WSTFileWrapper * inWS0 = new WSTFileWrapper(filenameStr_,"tagsDumper/cms_hgg_13TeV");
		std::list<RooAbsData*> data =  (inWS0->allData()) ;
		for (std::list<RooAbsData*>::const_iterator iterator = data.begin(), end = data.end();
      iterator != end;
      ++iterator) {
        RooDataSet *dataset = dynamic_cast<RooDataSet *>( *iterator );
        if (dataset) {
	        std::cout <<  dataset->GetName() << "," << dataset->sumEntries() << std::endl;
        }
		}
		return 1;
	}

  //time to open the signal file for the main script!
	WSTFileWrapper *inWS;
	if (isFlashgg_){
    inWS = new WSTFileWrapper(filenameStr_,"tagsDumper/cms_hgg_13TeV");
		std::list<RooAbsData*> test =  (inWS->allData()) ;
		if (verbose_) {
			std::cout << " [INFO] WS contains " << std::endl;
			for (std::list<RooAbsData*>::const_iterator iterator = test.begin(), end = test.end(); iterator != end; ++iterator) {
		//		std::cout << **iterator << std::endl;
			}
		}
	} else {
    std::cout << "[ERROR] script is only compatible with flashgg! exit(1)." << std::endl;
    exit(1);
  }
	
	if (inWS) { 
   if (verbose_)  std::cout << "[INFO] Workspace opened correctly" << std::endl;
  } else { 
    std::cout << "[EXIT] Workspace is null pointer. exit" << std::endl; 
    exit(1);
  }
  
  // get the required variables from the WS
	mass_ = (RooRealVar*)inWS->var("CMS_hgg_mass");
  mass_->SetTitle("m_{#gamma#gamma}");
	mass_->setUnit("GeV");
	dZ_ = (RooRealVar*)inWS->var("dZ");
	dZ_->setMin(-25.0);
	dZ_->setMax(25.0);
	dZ_->setBins(100);
  intLumi_ = (RooRealVar*)inWS->var("IntLumi");
  if (!intLumi_) {
     intLumi_ = new RooRealVar("IntLumi","hacked int lumi", 1000.);
     std::cout << "WARNING THIS IS A DUMMY INTLUMI MAKE SURE TO REMOVE ONCE NORMALISATION BUG IS FIXED " << std::endl;
  }
  originalIntLumi_ =(intLumi_->getVal());// specify in 1/pb
  newIntLumi_ = newIntLumi_*1000; // specify in 1/pb instead of 1/fb.
  intLumi_->setVal(newIntLumi_); 

	//RooRealVar *weight = (RooRealVar*)inWS->var("weight:weight");
  if( mass_ && dZ_ && intLumi_){
	  if (verbose_) std::cout << "[INFO] RooRealVars mass, intL and dZ, found ? " << mass_ << ", " << intLumi_  << ", "<< dZ_<<  std::endl;
  } else {
    std::cout << "[ERROR] could not find some of these RooRealVars in WS: mass_ " << mass_ << " dZ " << dZ_ << " intLumi " << intLumi_<< ".  exit(1) "<< std::endl;
    exit(1);
  }
  
  if (verbose_) std::cout << "[INFO] setting RoorealVars used for fitting."<< std::endl;
  RooRealVar *MH = new RooRealVar("MH","m_{H}",mhLow_,mhHigh_);
	MH->setUnit("GeV");
	MH->setConstant(true);
	RooRealVar *MH_SM = new RooRealVar("MH_SM","m_{H} (SM)",mhLow_,mhHigh_);
	MH_SM->setConstant(true);
	RooRealVar *DeltaM = new RooRealVar("DeltaM","#Delta m_{H}",0.,-10.,10.);
	DeltaM->setUnit("GeV");
	DeltaM->setConstant(true);
	RooAddition *MH_2 = new RooAddition("MH_2","m_{H} (2)",RooArgList(*MH,*DeltaM));
	RooRealVar *higgsDecayWidth = new RooRealVar("HiggsDecayWidth","#Gamma m_{H}",0.,0.,10.);
	higgsDecayWidth->setConstant(true);
  
  //prepare teh output file!
  if (verbose_) std::cout << "[INFO] preparing outfile "<< outfilename_<< std::endl;
	TFile *outFile = new TFile(outfilename_.c_str(),"RECREATE");
	RooWorkspace *outWS;

	if (isFlashgg_) outWS = new RooWorkspace("wsig_13TeV");
	
  RooWorkspace *mergeWS = 0;
	TFile *mergeFile = 0;
	
  // maybe this is no longer needed ? -LC
  if(!mergefilename_.empty()) {
		mergeFile = TFile::Open(mergefilename_.c_str());
		if (is2011_) mergeWS = (RooWorkspace*)mergeFile->Get("wsig_7TeV");
		else  mergeWS = (RooWorkspace*)mergeFile->Get("wsig_8TeV");
	}
  
  // i'm gonna comemnt this otu and see if anythign breaks... -LC
	//transferMacros(inFile,outFile);
  
  //splines for RV/WV
	clonemap_t cloneSplinesMapRV;
	clonemap_t cloneSplinesMapWV;

  // make the output dir
	system(Form("mkdir -p %s/initialFits",plotDir_.c_str()));
	system("mkdir -p dat/in");
	parmap_t allParameters;

	// Prepare the list of <proc> <tag> <nRV> <nWV> entries
	ifstream datfile;
	datfile.open(datfilename_.c_str());
	if (datfile.fail()) {
		std::cerr << "[ERROR] Could not open " << datfilename_ <<std::endl;
		exit(1);
	}
  
  if (0){// not actually used since DCB still needs to know which cat/procs to use a repalcement for
    for (int iproc =0 ; iproc < procs_.size() ; iproc++){
      for (int itag =0 ; itag < flashggCats_.size() ; itag++){
        map_proc_.push_back(procs_[iproc]);
        map_cat_.push_back(flashggCats_[itag]);
        map_nG_rv_.push_back(-1);
        map_nG_wv_.push_back(-1); //this info is not needed for DCB+1G shape, but keep format to maintain compatibility;
      }
    }
  } else {
    if (verbose_) std::cout << "[INFO] openign dat file "<< datfile<< std::endl;
    //loop over it 
	  while (datfile.good()){
		  string line;
		  getline(datfile,line);
		  if (line=="\n" || line.substr(0,1)=="#" || line==" " || line.empty()) continue;
		  vector<string> els;
		  split(els,line,boost::is_any_of(" "));
		  if( els.size()!=4 && els.size()!=6 && els.size()!=8) {
			  cerr << "Malformed line " << line << " " << els.size() <<endl;
			  assert(0);
		  }

      // the defaukt info need: proc, tag, nRv, nrWV
      string proc = els[0];
		  string cat = els[1]; // used to be an int, string directly now...
		  int nGaussiansRV = boost::lexical_cast<int>(els[2]);
		  int nGaussiansWV = boost::lexical_cast<int>(els[3]);

      // have a different appraoch now but could re-use machinery.
      //std::cout << " LC DEBUG here is your line " << line << " els.size()==6 " << (els.size()==6) <<  std::endl;
		  if( els.size()==6 ) { // in this case you have specified a replacement tag for RV!
			  //replaceWith_RV_ = make_pair(els[4],els[5]); // proc, cat
        map_replacement_proc_RV_.push_back(els[4]);
        map_replacement_cat_RV_.push_back(els[5]);
        map_replacement_proc_WV_.push_back(referenceProc_); //use defaults for replacement WV if they are needed
        map_replacement_cat_WV_.push_back(referenceTagWV_);//use defaults for replacement WV if they are needed
		  } else if( els.size()==8 ) { // in this case you have specified a replacement tag for RV and WV!
			  //replaceWithRV_ = make_pair(els[4],els[5]); // proc, cat
			  //replaceWithWV_ = make_pair(els[6],els[7]); // proc, cat
		   	//replace_ = true;
        map_replacement_proc_RV_.push_back(els[4]);
        map_replacement_cat_RV_.push_back(els[5]);
        map_replacement_proc_WV_.push_back(els[6]);
        map_replacement_cat_WV_.push_back(els[7]);
      } else {
        // if no replacement is speficied, use defaults
        if (cat.compare(0,3,"TTH") ==0){
          // if the cat starts with TTH, use TTH reference process.
          // howwver this is over-riden later if the WV needs to be replaced
          // as even teh TTH tags in WV has limited stats
          map_replacement_proc_RV_.push_back(referenceProcTTH_);
          map_replacement_cat_RV_.push_back(cat);
          map_replacement_proc_WV_.push_back(referenceProc_); //use defaults for replacement WV if they are needed
          map_replacement_cat_WV_.push_back(referenceTagWV_);//use defaults for replacement WV if they are needed
        } else {
         // else use the ggh
         map_replacement_proc_RV_.push_back(referenceProc_);
         map_replacement_cat_RV_.push_back(referenceTagRV_); //deflaut is ggh UntaggedTag3
         map_replacement_proc_WV_.push_back(referenceProc_); //use defaults for replacement WV if they are needed
         map_replacement_cat_WV_.push_back(referenceTagWV_);//use defaults for replacement WV if they are needed
        }
      }
      if (verbose_) std::cout << "[INFO] dat file listing: "<< proc << " " << cat << " " << nGaussiansRV << " " << nGaussiansWV <<  " " << std::endl;
      if (verbose_) std::cout << "[INFO] dat file listing: ----> selected replacements (RV) if needed " <<  map_replacement_proc_RV_[map_replacement_proc_RV_.size() -1] << " " <<  map_replacement_cat_RV_[map_replacement_cat_RV_.size() -1] << std::endl;
      if (verbose_) std::cout << "[INFO] dat file listing: ----> selected replacements (WV) if needed " <<  map_replacement_proc_WV_[map_replacement_proc_WV_.size() -1] << " " <<  map_replacement_cat_WV_[map_replacement_cat_WV_.size() -1] << std::endl;

      map_proc_.push_back(proc);
      map_cat_.push_back(cat);
      map_nG_rv_.push_back(nGaussiansRV);
      map_nG_wv_.push_back(nGaussiansWV);
    }
    datfile.close();
  }
  
  // now start the proper loop, so loop over teh maps we filled above.
  for (unsigned int iLine = 0 ; iLine < map_proc_.size() ; iLine++){
    string proc = map_proc_[iLine] ;
    string cat = map_cat_[iLine];
    int nGaussiansRV = map_nG_rv_[iLine];
    int nGaussiansWV = map_nG_wv_[iLine];
    
    // continueFlag use din job splitting to allow you to just look at once proc/tag at a time
    bool continueFlag =0;
    if (split_.size()==2){
      continueFlag=1;
      string splitProc = split_[0];
      string  splitCat = split_[1];
      if (verbose_) std::cout << " [INFO] check if this proc " << proc << " matches splitProc " << splitProc << ": "<< (proc.compare(splitProc)==0) << std::endl; 
      if ( proc.compare(splitProc) == 0 ) {
        if (verbose_) std::cout << " [INFO] --> proc matches! Check if this cat " << cat  << " matches splitCat " << splitCat<< ": " << (cat.compare(splitCat)==0) <<  std::endl; 
        if ( cat.compare(splitCat) == 0 ) {
        if (verbose_) std::cout << " [INFO]     --> cat matches too ! so we process it "<<  std::endl; 
          continueFlag =0; 
        }
      }
    }
    
    //if no match found, then skip this cat/proc
    if(continueFlag) {
      if(verbose_) std::cout << "[INFO] skipping "<< Form(" fits for proc:%s - cat:%s with nGausRV:%d nGausWV:%d",proc.c_str(),cat.c_str(),nGaussiansRV,nGaussiansWV) << endl;
      continue;
    }
    bool userSkipRV = (nGaussiansRV==-1);
    bool userSkipWV = (nGaussiansWV==-1);

    cout << "-----------------------------------------------------------------" << endl;
    cout << Form("[INFO] Running fits for proc:%s - cat:%s with nGausRV:%d nGausWV:%d",proc.c_str(),cat.c_str(),nGaussiansRV,nGaussiansWV) << endl;
    //if( replace_ ) { cout << Form("Will replace parameters using  proc:%s - cat:%d",replaceWith_.first.c_str(),replaceWith_.second.c_str()) << endl; }

    cout << "-----------------------------------------------------------------" << endl;
    // get datasets for each MH here
    map<int,RooDataSet*> datasetsRV;
    map<int,RooDataSet*> datasetsWV;
    map<int,RooDataSet*> FITdatasetsRV;// if catgeory has low stats, may use a different category dataset to make the fits
    map<int,RooDataSet*> FITdatasetsWV;// if catgeory has low stats, may use a different category dataset to make the fits

    map<int,RooDataSet*> datasets; // not used ?

    bool isProblemCategory =false;

    for (int mhIndex=0; mhIndex< massList_.size() ; mhIndex++){
      int mh=massList_[mhIndex];
      if (skipMass(mh)) continue;
      if( (mh!=125) && (proc=="testBBH" || proc=="testTHQ" || proc=="testTHW") ) continue;
      RooDataSet *dataRV; 
      RooDataSet *dataWV; 
      RooDataSet *dataRVRef; 
      RooDataSet *dataWVRef; 
      RooDataSet *dataRef;  
      RooDataSet *data0Ref;  
      RooDataSet *data;  
      RooDataHist *dataH;  

        if (verbose_)std::cout << "[INFO] Opening dataset called "<< Form("%s_%d_13TeV_%s",proc.c_str(),mh,cat.c_str()) << " in in WS " << inWS << std::endl;
        RooDataSet *data0   = reduceDataset((RooDataSet*)inWS->data(Form("%s_%d_13TeV_%s",proc.c_str(),mh,cat.c_str())));
				if (beamSpotReweigh_){
        data = beamSpotReweigh(intLumiReweigh(data0));
				} else {
        data = intLumiReweigh(data0);
				}
        if (verbose_) std::cout << "[INFO] Old dataset (before intLumi change): " << *data0 << std::endl;

	//plotBeamSpotDZdist(data,"VHdebug");

        dataRV = rvwvDataset(data,"RV"); 
        dataWV = rvwvDataset(data,"WV"); 

        if (verbose_) std::cout << "[INFO] Datasets ? " << *data << std::endl;
        if (verbose_) std::cout << "[INFO] Datasets (right vertex) ? " << *dataRV << std::endl;
        if (verbose_) std::cout << "[INFO] Datasets (wrong vertex) ? " << *dataWV << std::endl;
        
        float nEntriesRV =dataRV->numEntries();
        float sEntriesRV= dataRV->sumEntries();
        float nEntriesWV =dataWV->numEntries();
        float sEntriesWV= dataWV->sumEntries(); // count the number of entries and total weight on the RV/WV datasets
        
        // if there are few atcual entries or if there is an  overall negative sum of weights...
        // or if it was specified that one should use the replacement dataset, then need to replace!
        if (nEntriesRV < 200 || sEntriesRV < 0 || ( userSkipRV)){
          std::cout << "[INFO] too few entries to use for fits in RV! nEntries " << nEntriesRV << " sumEntries " << sEntriesRV << "userSkipRV " << userSkipRV<< std::endl;
          isProblemCategory=true;
          
          int thisProcCatIndex = getIndexOfReferenceDataset(proc,cat);
          
          string replancementProc = map_replacement_proc_RV_[thisProcCatIndex];
          string replancementCat = map_replacement_cat_RV_[thisProcCatIndex];
          int replacementIndex = getIndexOfReferenceDataset(replancementProc,replancementCat);
          nGaussiansRV= map_nG_rv_[replacementIndex]; // if ==-1, want it to stay that way!
          std::cout << "[INFO] try to use  dataset for " << replancementProc << ", " << replancementCat << " instead."<< std::endl;
          
          //pick the dataset for the replacement proc and cat, reduce it (ie remove pdfWeights etc) ,
          //reweight for lumi, and then get the RV events only.
					if(beamSpotReweigh_){
          data0Ref   = beamSpotReweigh(
													rvwvDataset(
                        		intLumiReweigh(
                          		reduceDataset(
                          			(RooDataSet*)inWS->data(Form("%s_%d_13TeV_%s",replancementProc.c_str(),mh,replancementCat.c_str()))
                              )
                            ), "RV"
                          )
											 );

					} else {
          data0Ref   = rvwvDataset(
                        intLumiReweigh(
                          reduceDataset(
                          (RooDataSet*)inWS->data(Form("%s_%d_13TeV_%s",replancementProc.c_str(),mh,replancementCat.c_str()))
                         )
                       ), "RV"
                      );
					}
          if (data0Ref) {
           std::cout << "[INFO] Found replacement dataset for RV:" << *data0Ref<< std::endl;
          } else {
           std::cout << "[ERROR] could not find replacement dataset for RV... " <<  std::endl;
           exit(1);
          }

          dataRVRef=(RooDataSet*) data0Ref->Clone();
          std::cout << "[INFO] RV: replacing dataset for FITTING with new one ("<< *dataRVRef <<"), but keeping name of "<< *data0 << std::endl;
        //  dataRVRef->SetName(data0->GetName());
        } else { // if the dataset was fine to begin with, make the reference dataset the original
          dataRVRef=(RooDataSet*) dataRV->Clone();
        }
        
      
        // if there are few atcual entries or if there is an  overall negative sum of weights...
        // or if it was specified that one should use the replacement dataset, then need to replace!
        if (nEntriesWV < 200 || sEntriesWV < 0 || (userSkipWV)){
          std::cout << "[INFO] too few entries to use for fits in WV! nEntries " << nEntriesWV << " sumEntries " << sEntriesWV << "userSkipWV " << userSkipWV << std::endl;
        
          //things are simpler this time, since almost all WV are bad aside from ggh-UntaggedTag3
         //and anyway the shape of mgg in the WV shoudl be IDENTICAL across all Tags.
         //int replacementIndex = getIndexOfReferenceDataset(referenceProcWV_,referenceTagWV_);
         int thisProcCatIndex = getIndexOfReferenceDataset(proc,cat);
          
          string replancementProc = map_replacement_proc_WV_[thisProcCatIndex];
          string replancementCat = map_replacement_cat_WV_[thisProcCatIndex];
          int replacementIndex = getIndexOfReferenceDataset(replancementProc,replancementCat);
          nGaussiansWV= map_nG_wv_[replacementIndex]; 
        
         //pick the dataset for the replacement proc and cat, reduce it (ie remove pdfWeights etc) ,
         //reweight for lumi and then get the WV events only.
				 if (beamSpotReweigh_){
         data0Ref   = beamSpotReweigh( 
				               rvwvDataset(
                        intLumiReweigh(
                          reduceDataset(
                          //(RooDataSet*)inWS->data(Form("%s_%d_13TeV_%s",referenceProcWV_.c_str(),mh,referenceTagWV_.c_str()))
                            (RooDataSet*)inWS->data(Form("%s_%d_13TeV_%s",replancementProc.c_str(),mh,replancementCat.c_str()))
                         )
                       ), "WV"
                      )
										);
				 } else {
         data0Ref   = rvwvDataset(
                        intLumiReweigh(
                          reduceDataset(
                          //(RooDataSet*)inWS->data(Form("%s_%d_13TeV_%s",referenceProcWV_.c_str(),mh,referenceTagWV_.c_str()))
                          	(RooDataSet*)inWS->data(Form("%s_%d_13TeV_%s",replancementProc.c_str(),mh,replancementCat.c_str()))
                         )
                       ), "WV"
                      );
					}
          if (data0Ref) {
           std::cout << "[INFO] Found replacement dataset for WV:" << *data0Ref<< std::endl;
          } else { // if the dataset was fine to begin with, make the reference dataset the original
           std::cout << "[ERROR] could not find replacement dataset for WV... " <<  std::endl;
           exit(1);
          }

          dataWVRef = (RooDataSet*) data0Ref->Clone();
          std::cout << "[INFO] WV: replacing dataset for FITTING with new one ("<< *dataWVRef <<"), but keeping name of "<< *data0 << std::endl;
         // dataWVRef->SetName(data0->GetName());
        } else {
          dataWVRef=(RooDataSet*) dataWV->Clone();
        }


      if (verbose_) std::cout << "[INFO] inserting regular RV dataset " << *dataRV<< std::endl;
      datasetsRV.insert(pair<int,RooDataSet*>(mh,dataRV));
      if (verbose_) std::cout << "[INFO] inserting regular WV datasets " << *dataWV<< std::endl;
      datasetsWV.insert(pair<int,RooDataSet*>(mh,dataWV));
      if (verbose_) std::cout << "[INFO] inserting FIT RVdatasets " << *dataRVRef << std::endl;
      FITdatasetsRV.insert(pair<int,RooDataSet*>(mh,dataRVRef));
      if (verbose_) std::cout << "[INFO] inserting FIT WVdatasets" << *dataWVRef << std::endl;
      FITdatasetsWV.insert(pair<int,RooDataSet*>(mh,dataWVRef));
      if (verbose_)std::cout << "[INFO] inserting regular RV+WV " << *data << std::endl;
      datasets.insert(pair<int,RooDataSet*>(mh,data));
      if (verbose_) std::cout << "[INFO] Original Dataset: "<< *data << std::endl;
    }
    
    //check consistency of the three datasets!!
    TString check="";
    for (std::map<int,RooDataSet*>::iterator it=FITdatasetsRV.begin(); it!=FITdatasetsRV.end(); ++it){
      if (check=="") {
       TString name=it->second->GetName();
        check = name.ReplaceAll(TString(Form("%d",it->first)),TString(""));
       } else {
       TString name=it->second->GetName();
       assert (check ==name.ReplaceAll(TString(Form("%d",it->first)),TString("")) );
       }
    }
    check="";
    for (std::map<int,RooDataSet*>::iterator it=FITdatasetsWV.begin(); it!=FITdatasetsWV.end(); ++it){
      if (check=="") {
       TString name=it->second->GetName();
        check = name.ReplaceAll(TString(Form("%d",it->first)),TString(""));
       } else {
       TString name=it->second->GetName();
       assert (check ==name.ReplaceAll(TString(Form("%d",it->first)),TString("")) );
       }
    }
      
      
    //these guys do the interpolation
    //declare them in advnace of the fitting
    map<string,RooSpline1D*> splinesRV;
    map<string,RooSpline1D*> splinesWV;

    // these guys do the fitting
    if(useSSF_){
    // right vertex
    if (verbose_) std::cout << "[INFO] preapraing initialfit RV, massList size "<< massList_.size() << std::endl;
    int maxOrder = 1;
    if( (proc=="testBBH" || proc=="testTHQ" || proc=="testTHW") ) maxOrder=0;
    SimultaneousFit simultaneousFitRV(mass_,MH,mhLow_,mhHigh_,skipMasses_,binnedFit_,nBins_,massList_,cat,proc,Form("%s/rv",plotDir_.c_str()), /*maxOrder of MH depende of RooPolyVars*/ maxOrder);
    simultaneousFitRV.setVerbosity(verbose_);
    if (!cloneFits_) {
      if (verbose_) std::cout << "[INFO] RV building sum of gaussians with nGaussiansRV " << nGaussiansRV << std::endl;
      if(useDCBplusGaus_) {
        simultaneousFitRV.buildDCBplusGaussian(Form("%s_%s",proc.c_str(),cat.c_str()),recursive_);
      } else {
        simultaneousFitRV.buildSumOfGaussians(Form("%s_%s",proc.c_str(),cat.c_str()),nGaussiansRV,recursive_);
      }
      if (verbose_) std::cout << "[INFO] RV setting datasets in initialFIT " << std::endl;
      simultaneousFitRV.setDatasets(FITdatasetsRV);
      simultaneousFitRV.setDatasetsSTD(datasetsRV);
      if (verbose_) std::cout << "[INFO] RV running fits" << std::endl;
      simultaneousFitRV.runFits(ncpu_,Form("%s/initialFits/rv_%s_%s",plotDir_.c_str(),proc.c_str(),cat.c_str()),iterativeFitConstraint_);
      if (!skipPlots_) simultaneousFitRV.plotFits(Form("%s/initialFits/%s_%s_rv",plotDir_.c_str(),proc.c_str(),cat.c_str()),"RV");
    }
    parlist_t fitParamsRV = simultaneousFitRV.getFitParams();

    // wrong vertex
    if (verbose_) std::cout << "[INFO] preparing initialfit WV, masList size "<< massList_.size() << std::endl;
    SimultaneousFit simultaneousFitWV(mass_,MH,mhLow_,mhHigh_,skipMasses_,binnedFit_,nBins_,massList_,cat,proc,Form("%s/wv",plotDir_.c_str()), /*maxOrder of MH depende of RooPolyVars*/ maxOrder);
    simultaneousFitWV.setVerbosity(verbose_);
    if (!cloneFits_) {
      if (verbose_) std::cout << "[INFO] WV building sum of gaussians wth nGaussiansWV "<< nGaussiansWV << std::endl;
      if(useDCBplusGaus_) {
        simultaneousFitWV.buildDCBplusGaussian(Form("%s_cat%s",proc.c_str(),cat.c_str()),recursive_);
      } else {
        simultaneousFitWV.buildSumOfGaussians(Form("%s_cat%s",proc.c_str(),cat.c_str()),nGaussiansWV,recursive_);
      }
      if (verbose_) std::cout << "[INFO] WV setting datasets in initial FIT " << std::endl;
      simultaneousFitWV.setDatasets(FITdatasetsWV);
      simultaneousFitWV.setDatasetsSTD(datasetsWV);
      if (verbose_) std::cout << "[INFO] WV running fits" << std::endl;
      simultaneousFitWV.runFits(ncpu_,Form("%s/initialFits/wv_%s_%s",plotDir_.c_str(),proc.c_str(),cat.c_str()),iterativeFitConstraint_);
      if (!skipPlots_) simultaneousFitWV.plotFits(Form("%s/initialFits/%s_%s_wv",plotDir_.c_str(),proc.c_str(),cat.c_str()),"WV");
    }
    parlist_t fitParamsWV = simultaneousFitWV.getFitParams();
    allParameters[ make_pair(proc,cat) ] = make_pair(fitParamsRV,fitParamsWV);
    
    //Ok, now that we have made the fit parameters eitehr with the regular dataset or the replacement one.
    // Now we should be using the ORIGINAL dataset
    if (!runInitialFitsOnly_) {
      if (!cloneFits_){
        // right vertex
        splinesRV =  simultaneousFitRV.getSplines();
        // wrong vertex
        splinesWV =  simultaneousFitWV.getSplines();
      } else {
        splinesRV = cloneSplinesMapRV[make_pair(proc,cat)];
        splinesWV = cloneSplinesMapWV[make_pair(proc,cat)];
      }
     }
    } else {
    // right vertex
    if (verbose_) std::cout << "[INFO] preapraing initialfit RV, massList size "<< massList_.size() << std::endl;
    InitialFit initFitRV(mass_,MH,mhLow_,mhHigh_,skipMasses_,binnedFit_,nBins_,massList_);
    initFitRV.setVerbosity(verbose_);
    if (!cloneFits_) {
      if (verbose_) std::cout << "[INFO] RV building sum of gaussians with nGaussiansRV " << nGaussiansRV << std::endl;
      if(useDCBplusGaus_) {
        initFitRV.buildDCBplusGaussian(Form("%s_%s",proc.c_str(),cat.c_str()));
      } else {
        initFitRV.buildSumOfGaussians(Form("%s_%s",proc.c_str(),cat.c_str()),nGaussiansRV,recursive_);
      }
      if (verbose_) std::cout << "[INFO] RV setting datasets in initialFIT " << std::endl;
      initFitRV.setDatasets(FITdatasetsRV);
      initFitRV.setDatasetsSTD(datasetsRV);
      if (verbose_) std::cout << "[INFO] RV running fits" << std::endl;
      initFitRV.runFits(ncpu_);
      if (!skipPlots_) initFitRV.plotFits(Form("%s/initialFits/%s_%s_rv",plotDir_.c_str(),proc.c_str(),cat.c_str()),"RV");
      }
      parlist_t fitParamsRV = initFitRV.getFitParams();

      // wrong vertex
      if (verbose_) std::cout << "[INFO] preparing initialfit WV, masList size "<< massList_.size() << std::endl;
      InitialFit initFitWV(mass_,MH,mhLow_,mhHigh_,skipMasses_,binnedFit_,nBins_,massList_);
      initFitWV.setVerbosity(verbose_);
      if (!cloneFits_) {
        if (verbose_) std::cout << "[INFO] WV building sum of gaussians wth nGaussiansWV "<< nGaussiansWV << std::endl;
        if(useDCBplusGaus_) {
          initFitWV.buildDCBplusGaussian(Form("%s_%s",proc.c_str(),cat.c_str()));
        } else {
          initFitWV.buildSumOfGaussians(Form("%s_cat%s",proc.c_str(),cat.c_str()),nGaussiansWV,recursive_);
        }
        if (verbose_) std::cout << "[INFO] WV setting datasets in initial FIT " << std::endl;
        initFitWV.setDatasets(FITdatasetsWV);
        initFitWV.setDatasetsSTD(datasetsWV);
        if (verbose_) std::cout << "[INFO] WV running fits" << std::endl;
        initFitWV.runFits(ncpu_);
       // if (!runInitialFitsOnly_ && !replace_) {
        //  initFitWV.saveParamsToFileAtMH(Form("dat/in/%s_%s_wv.dat",proc.c_str(),cat.c_str()),constraintValueMass_);
        //  initFitWV.loadPriorConstraints(Form("dat/in/%s_%s_wv.dat",proc.c_str(),cat.c_str()),constraintValue_);
        //  initFitWV.runFits(ncpu_);
      //  }
       // if( replace_ ) {
        //  initFitWV.setFitParams(allParameters[replaceWith_].second); 
      //  }
        if (!skipPlots_) initFitWV.plotFits(Form("%s/initialFits/%s_%s_wv",plotDir_.c_str(),proc.c_str(),cat.c_str()),"WV");
      }
      parlist_t fitParamsWV = initFitWV.getFitParams();
    
      allParameters[ make_pair(proc,cat) ] = make_pair(fitParamsRV,fitParamsWV);
    
      //Ok, now that we have made the fit parameters eitehr with the regular dataset or the replacement one.
      // Now we should be using the ORIGINAL dataset
      if (!runInitialFitsOnly_) {
        if (!cloneFits_){
          // right vertex
          LinearInterp linInterpRV(MH,massList_,fitParamsRV,doSecondaryModels_,skipMasses_);
          linInterpRV.setVerbosity(verbose_);
          linInterpRV.setSecondaryModelVars(MH_SM,DeltaM,MH_2,higgsDecayWidth);
          linInterpRV.interpolate(); //nGaussians no longer need to be provided since re-implementation of the interpolate class to be functional-form-agnostic
          splinesRV = linInterpRV.getSplines();

          // wrong vertex
          LinearInterp linInterpWV(MH,massList_,fitParamsWV,doSecondaryModels_,skipMasses_);
          linInterpWV.setVerbosity(verbose_);
          linInterpWV.setSecondaryModelVars(MH_SM,DeltaM,MH_2,higgsDecayWidth);
          linInterpWV.interpolate();//nGaussians no longer need to be provided since re-implementation of the interpolate class to be functional-form-agnostic

          splinesWV = linInterpWV.getSplines();
        } else {
          splinesRV = cloneSplinesMapRV[make_pair(proc,cat)];
          splinesWV = cloneSplinesMapWV[make_pair(proc,cat)];
        }
      }
    }
    // this guy constructs the final model with systematics, eff*acc etc.
    if (isFlashgg_){
        
      outWS->import(*intLumi_);
      FinalModelConstruction finalModel(massList_, mass_,MH,intLumi_,mhLow_,mhHigh_,proc,cat,doSecondaryModels_,systfilename_,skipMasses_,verbose_,procs_, flashggCats_,plotDir_, isProblemCategory,isCutBased_,sqrts_,doQuadraticSigmaSum_);
    
      finalModel.setSecondaryModelVars(MH_SM,DeltaM,MH_2,higgsDecayWidth);
      finalModel.setRVsplines(splinesRV);
      finalModel.setWVsplines(splinesWV);
      finalModel.setRVdatasets(datasetsRV);
      finalModel.setWVdatasets(datasetsWV);
      finalModel.setFITRVdatasets(FITdatasetsRV);
      finalModel.setFITWVdatasets(FITdatasetsWV);
      //finalModel.setSTDdatasets(datasets);
      finalModel.makeSTDdatasets();
      finalModel.makeFITdatasets();
      if( isFlashgg_){
        if (verbose_>1) std::cout << "[INFO] About to do Final Model Construction with useDCBplusGaus_=" << useDCBplusGaus_ << std::endl;
        finalModel.buildRvWvPdf("hggpdfsmrel_13TeV",nGaussiansRV,nGaussiansWV,recursive_,useDCBplusGaus_);
      }
      finalModel.getNormalization();
      //if (!skipPlots_) finalModel.plotPdf(plotDir_);
      finalModel.plotPdf(plotDir_);
      finalModel.save(outWS);
    }
  }

  sw.Stop();
  cout << "[INFO] Whole fitting process took..." << endl;
  cout << "\t";
  sw.Print();

  if (!runInitialFitsOnly_) { 
    sw.Start();
    cout << "[INFO] Starting to combine fits..." << endl;
    // this guy packages everything up
    WSTFileWrapper *outWSWrapper = new WSTFileWrapper(outFile, outWS);
    Packager packager(outWSWrapper, outWS,procs_,nCats_,mhLow_,mhHigh_,skipMasses_,sqrts_,skipPlots_,plotDir_,mergeWS,cats_,flashggCats_);
    
    // if we are doing jobs for each proc/tag, want to do the split.
    bool split =0;
    if (split_.size() > 0) split=1; 
    packager.packageOutput(/*split*/split, /*proc*/split_[0], /*tag*/ split_[1] );
    sw.Stop();
    cout << "[INFO] Combination complete." << endl;
    cout << "[INFO] Whole process took..." << endl;
    cout << "\t";
    sw.Print();
  }

  cout << "[INFO] Writing to file..." << endl;
  outFile->cd();
  outWS->Write();
  outFile->Close();
  //	inFile->Close();
  inWS->Close();
  cout << "[INFO] Done." << endl;

  return 0;
}
