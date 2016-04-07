#include <iostream>
#include <fstream>
#include <vector>
#include <string>

#include "boost/lexical_cast.hpp"
#include "boost/program_options.hpp"

#include "TFile.h"
#include "TROOT.h"
#include "TCanvas.h"
#include "TGraph.h"

#include "RooWorkspace.h"
#include "RooExtendPdf.h"
#include "RooDataSet.h"
#include "RooAddPdf.h"
#include "RooHistFunc.h"
#include "HiggsAnalysis/CombinedLimit/interface/RooSpline1D.h"
#include "RooRealVar.h"
#include "RooFormulaVar.h"
#include "RooArgList.h"
#include "../interface/Packager.h"
#include "RooAddition.h"

#include "../interface/Normalization_8TeV.h"

#include "boost/program_options.hpp"
#include "boost/algorithm/string/split.hpp"
#include "boost/algorithm/string/classification.hpp"
#include "boost/algorithm/string/predicate.hpp"

using namespace std;
using namespace RooFit;
using namespace boost;
namespace po = boost::program_options;

string infilename_;
string outfilename_;
float lumi_;
string wsname_;
int mhLow_=115;
int mhHigh_=135;
string plotDir_;
int ncats_;
vector<int> cats_;
string catsStr_;
string webdir_;
string massesToSkip_;
vector<int> skipMasses_;
bool web_;
bool spin_=false;
bool splitVH_=false;
bool makePlots_=false;
bool doSMHiggsAsBackground_=true;
bool doSecondHiggs_=true;
bool doNaturalWidth_=true;
bool skipSecondaryModels_=false;
vector<int> allMH_;
string flashggCatsStr_;
vector<string> flashggCats_;
vector<string> procs_;
string procStr_;

vector<int> getAllMH(){
  vector<int> result;
  for (int m=mhLow_; m<=mhHigh_; m+=5){
    cout << "Adding mass: " << m << endl;
    result.push_back(m);
  }
  return result;
}

void OptionParser(int argc, char *argv[]){

  po::options_description desc("Allowed options");

  desc.add_options()
    ("help,h",                                                                                "Show help")
    ("infilename,i", po::value<string>(&infilename_)->default_value("comma,separated,list"),"Input file name")
		("procs", po::value<string>(&procStr_)->default_value("ggh,vbf,wh,zh,tth"),					"Processes (comma sep)")
    ("outfilename,o", po::value<string>(&outfilename_)->default_value("CMS-HGG_sigfit.root"), "Output file name")
    ("lumi,l", po::value<float>(&lumi_)->default_value(19.620),                              "Luminosity")
		("plotDir,p", po::value<string>(&plotDir_)->default_value("plots"),						"Put plots in this directory")
    ("wsname,W", po::value<string>(&wsname_)->default_value("wsig_8TeV"),                     "Output workspace name")
		("skipMasses", po::value<string>(&massesToSkip_)->default_value(""),					"Skip these mass points - used eg for the 7TeV where there's no mc at 145")
    ("mhLow,L", po::value<int>(&mhLow_)->default_value(115),                                  "Low mass point")
    ("mhHigh,H", po::value<int>(&mhHigh_)->default_value(135),                                "High mass point")
		("flashggCats,f", po::value<string>(&flashggCatsStr_)->default_value("UntaggedTag_0,UntaggedTag_1,UntaggedTag_2,UntaggedTag_3,UntaggedTag_4,VBFTag_0,VBFTag_1,VBFTag_2,TTHHadronicTag,TTHLeptonicTag,VHHadronicTag,VHTightTag,VHLooseTag,VHEtTag"),       "Flashgg categories if used")
    ("ncats,n", po::value<int>(&ncats_)->default_value(9),                                    "Number of categories")
    ("html,w", po::value<string>(&webdir_),                                                   "Make html in this directory")
  ;

  po::variables_map vm;
  po::store(po::parse_command_line(argc,argv,desc),vm);
  po::notify(vm);
	split(procs_,procStr_,boost::is_any_of(","));
	split(flashggCats_,flashggCatsStr_,boost::is_any_of(","));
  if (vm.count("help")){ cout << desc << endl; exit(1);}
	if (vm.count("skipMasses")) {
		cout << "[INFO] Masses to skip... " << endl;
		vector<string> els;
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
	if(vm.count("cats")){
		vector<string> els;
		split(els,catsStr_,boost::is_any_of(","));
		if (els.size()>0 && catsStr_ !="") {
			for (vector<string>::iterator it=els.begin(); it!=els.end(); it++) {
				cats_.push_back(boost::lexical_cast<int>(*it));
			}
		}
	}
  allMH_ = getAllMH();
}
 
int main (int argc, char *argv[]){
 
  gROOT->SetBatch();
  OptionParser(argc,argv);
  
  TFile *outFile = new TFile(outfilename_.c_str(),"RECREATE");

  RooRealVar *intLumi = new RooRealVar("IntLumi","IntLumi",lumi_*1000,0.,10.e5);

  	
	  WSTFileWrapper * inWS = new WSTFileWrapper(infilename_,"wsig_13TeV");
	  RooWorkspace *saveWS = new RooWorkspace();
	  RooWorkspace *tmpWS = new RooWorkspace();
    //saveWS->import((inWS->allVars()),RecycleConflictNodes());
    //saveWS->import((inWS->allFunctions()),RecycleConflictNodes());
    for (int i=0 ; i < inWS->getWsList().size() ; i++){
    inWS->getWsList()[i]->Print();
    if (i==0) tmpWS = (RooWorkspace*) inWS->getWsList()[i]->Clone();
    if (!tmpWS){ std::cout << "EXIT" << std::endl;  exit(1);}
    if (i !=0) {
    //tmpWS->merge(*(inWS->getWsList()[i]));
    tmpWS->import(inWS->getWsList()[i]->allVars(),RecycleConflictNodes());
    tmpWS->import(inWS->getWsList()[i]->allFunctions(),RecycleConflictNodes());
    inWS->getWsList()[i]->allFunctions().Print();
    tmpWS->import(inWS->getWsList()[i]->allPdfs(),RecycleConflictNodes());
    inWS->getWsList()[i]->allPdfs().Print();
    std::list<RooAbsData*> data =  (inWS->getWsList()[i]->allData()) ;
    for (std::list<RooAbsData*>::const_iterator iterator = data.begin(), end = data.end(); iterator != end; ++iterator )  {
     tmpWS->import(**iterator);
    } 
    std::list<TObject*> stuff =  (inWS->getWsList()[i]->allGenericObjects()) ;
    for (std::list<TObject*>::const_iterator iterator = stuff.begin(), end = stuff.end(); iterator != end; ++iterator )  {
     tmpWS->import(**iterator);
    } 

    };

    }
    WSTFileWrapper *mergedWS = new WSTFileWrapper(tmpWS); 

    saveWS->SetName("wsig_13TeV");
    ncats_= flashggCats_.size();
    cout << "[INFO] Starting to combine fits..." << endl;
    // this guy packages everything up
	  RooWorkspace *mergeWS = 0;
    Packager packager(mergedWS, saveWS ,procs_,ncats_,mhLow_,mhHigh_,skipMasses_,/*sqrts*/13,/*skipPlots_*/false,plotDir_,mergeWS,cats_,flashggCats_);
    cout << "[INFO] Finished initalising packager." << endl;
    packager.packageOutput(/*split*/ false);
    cout << "[INFO] Combination complete." << endl;
    cout << "[INFO] cd to output file" << endl;
    outFile->cd();
    cout << "[INFO] write saveWS " << endl;
    saveWS->Write();
    cout << "[INFO] close output file  " << endl;
    outFile->Close();
  return 0;
}  

