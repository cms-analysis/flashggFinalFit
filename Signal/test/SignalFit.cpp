#include <iostream>
#include <fstream>
#include <string>
#include <map>
#include <vector>
#include <typeinfo>

#include "TROOT.h"
#include "TFile.h"
#include "TStopwatch.h"
#include "RooWorkspace.h"
#include "RooDataSet.h"
#include "TKey.h"
#include "TMacro.h"
#include "TClass.h"
#include "TIterator.h"
#include "TRandom3.h"
#include "HiggsAnalysis/CombinedLimit/interface/RooSpline1D.h"

#include "../interface/InitialFit.h"
#include "../interface/LinearInterp.h"
#include "../interface/FinalModelConstruction.h"
#include "../interface/Packager.h"

#include "boost/program_options.hpp"
#include "boost/algorithm/string/split.hpp"
#include "boost/algorithm/string/classification.hpp"
#include "boost/algorithm/string/predicate.hpp"

using namespace std;
using namespace RooFit;
using namespace boost;
namespace po = boost::program_options;

typedef map<int,map<string,RooRealVar*> > parlist_t;
typedef map<pair<string,int>, std::pair<parlist_t,parlist_t> > parmap_t;
typedef map<pair<string,int>,map<string,RooSpline1D*> > clonemap_t;

string filenameStr_;
vector<string> filename_;

string outfilename_;
string mergefilename_;
string datfilename_;
string systfilename_;
string plotDir_;
bool skipPlots_=false;
int mhLow_=110;
int mhHigh_=150;
int nCats_;
float constraintValue_;
int constraintValueMass_;
bool spin_=false;
vector<string> procs_;
string procStr_;
bool isCutBased_=false;
bool is2011_=false;
bool is2012_=false;
string massesToSkip_;
vector<int> skipMasses_;
bool splitRVWV_=true;
bool doSecondaryModels_=true;
bool doQuadraticSigmaSum_=false;
bool runInitialFitsOnly_=false;
bool cloneFits_=false;
string cloneFitFile_;
bool recursive_=true;
string highR9cats_;
string lowR9cats_;
int verbose_=0;
int ncpu_=1;
int sqrts_=13;
vector<int> cats_;
string catsStr_;
bool isFlashgg_;
string flashggCatsStr_;
vector<string> flashggCats_;
bool check_;

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
		("mhLow,L", po::value<int>(&mhLow_)->default_value(110),                                  			"Low mass point")
    ("nThreads,t", po::value<int>(&ncpu_)->default_value(ncpu_),                               			"Number of threads to be used for the fits")
    ("mhHigh,H", po::value<int>(&mhHigh_)->default_value(150),                                			"High mass point")
   // ("nCats,n", po::value<int>(&nCats_)->default_value(9),                                    			"Number of total categories")
    ("constraintValue,C", po::value<float>(&constraintValue_)->default_value(0.1),            			"Constraint value")
    ("constraintValueMass,M", po::value<int>(&constraintValueMass_)->default_value(125),                        "Constraint value mass")
    ("skipSecondaryModels",                                                                   			"Turn off creation of all additional models")
    ("doQuadraticSigmaSum",  										        "Add sigma systematic terms in quadrature")
    ("procs", po::value<string>(&procStr_)->default_value("ggh,vbf,wh,zh,tth"),					"Processes (comma sep)")
    ("skipMasses", po::value<string>(&massesToSkip_)->default_value(""),					"Skip these mass points - used eg for the 7TeV where there's no mc at 145")
    ("runInitialFitsOnly",                                                                                      "Just fit gaussians - no interpolation, no systematics - useful for testing nGaussians")
		("cloneFits", po::value<string>(&cloneFitFile_),															"Do not redo the fits but load the fit parameters from this workspace. Pass as fileName:wsName.")
    ("nonRecursive",                                                                             		"Do not recursively calculate gaussian fractions")
    ("verbose,v", po::value<int>(&verbose_)->default_value(0),                                			"Verbosity level: 0 (lowest) - 3 (highest)")
		("isFlashgg",	po::value<bool>(&isFlashgg_)->default_value(true),														"Use flashgg format")
		("check",	po::value<bool>(&check_)->default_value(false),														"Use flashgg format (default false)")
    ("flashggCats,f", po::value<string>(&flashggCatsStr_)->default_value("UntaggedTag_0,UntaggedTag_1,UntaggedTag_2,UntaggedTag_3,UntaggedTag_4,VBFTag_0,VBFTag_1,VBFTag_2,TTHHadronicTag,TTHLeptonicTag,VHHadronicTag,VHTightTag,VHLooseTag,VHEtTag"),       "Flashgg categories if used") 
  ;                                                                                             		
	po::options_description desc2("Options kept for backward compatibility");
	desc2.add_options()
  ("cats,c", po::value<string>(&catsStr_)->default_value(""),                                   			"Comma-separated list of cats to process")
	("nCats,n", po::value<int>(&nCats_)->default_value(9),																			"Number of cats (Set Automatically if using --isFlashgg 1)")
    ("highR9cats", po::value<string>(&highR9cats_)->default_value("0,1,4,5"),					"For cut based only - pass over which categories are inclusive high R9 cats (comma sep string)")
    ("lowR9cats", po::value<string>(&lowR9cats_)->default_value("2,3,6,7"),              			"For cut based only - pass over which categories are inclusive low R9 cats (comma sep string)")
    ("isCutBased",                                                                               		"Is this the cut based analysis")
    ("is2011",                                                                         				"Is this the 7TeV analysis")
    ("is2012",                                                                         				"Is this the 8TeV analysis")
		;
	po::options_description desc("Allowed options");
	desc.add(desc1).add(desc2);
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
  if (vm.count("recursive"))                recursive_=false;
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
  split(procs_,procStr_,boost::is_any_of(","));
	split(flashggCats_,flashggCatsStr_,boost::is_any_of(","));
	split(filename_,filenameStr_,boost::is_any_of(","));

}

void transferMacros(TFile *inFile, TDirectory *outFile){
  
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

void addToCloneMap(clonemap_t &cloneMap, string proc, int cat, string name, RooSpline1D *spline){
	
	pair<string,int> mapKey = make_pair(proc,cat);
	if (cloneMap.find(mapKey)==cloneMap.end()){
		map<string,RooSpline1D*> tempMap;
		tempMap.insert(make_pair(name,spline));
		cloneMap.insert(make_pair(mapKey,tempMap));
	}
	else {
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
		int cat = it->first.second;
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

void fillCloneSplinesMap(clonemap_t &mapRV, clonemap_t &mapWV, string fileName, string wsName){
	
	TFile *cloneFile = TFile::Open(fileName.c_str());
	RooWorkspace *cloneWS = (RooWorkspace*)cloneFile->Get(wsName.c_str());

	RooAbsReal *arg;
	RooArgSet funcs(cloneWS->allFunctions());
	TIterator *iter = funcs.createIterator();

	while ((arg=(RooAbsReal*)iter->Next())){
		if (arg->IsA()->InheritsFrom(RooSpline1D::Class())){
			vector<string> els;
			string s(arg->GetName());
			split(els,s,boost::is_any_of("_"));
			if (els[0]=="frac" || els[0]=="sigma" || els[0]=="dm"){
				string proc = els[2];
				int cat = boost::lexical_cast<int>(els[3].substr(els[3].find("cat")+3,string::npos));
				string rvwv = els[4]; 
				string name = els[0]+"_"+els[1];
				if (els[els.size()-1]=="SM" || els[els.size()-1]=="2" || els[els.size()-1]=="NW"){
					name += "_"+els[els.size()-1];
				}
				RooSpline1D *spline = (RooSpline1D*)cloneWS->function(arg->GetName());
				if (!spline) {
					std::cerr << "Spline is null: " << arg->GetName() << endl;
					exit(1);
				}
				if (rvwv=="rv") {
					addToCloneMap(mapRV,proc,cat,name,spline);
				}
				else if (rvwv=="wv"){
					addToCloneMap(mapWV,proc,cat,name,spline);
				}
				else {
					std::cerr << "Problem: " << rvwv << " is not a valid vertex hypothesis. Bailing" << std::endl;
					exit(1);
				}
			}
		}
	}
	cloneFile->Close();
}

bool skipMass(int mh){
	for (vector<int>::iterator it=skipMasses_.begin(); it!=skipMasses_.end(); it++) {
		if (*it==mh) return true;
	}
	return false;
}

int main(int argc, char *argv[]){


	gROOT->SetBatch();

	OptionParser(argc,argv);

	TStopwatch sw;
	sw.Start();

	if (isFlashgg_){ nCats_= flashggCats_.size();
	}

	TFile *inFile = TFile::Open(filename_[0].c_str());
	if (check_){
		//RooWorkspace *	inWS0 = (RooWorkspace*)inFile->Get(Form("wsig_8TeV"));
		RooWorkspace *	inWS0 = (RooWorkspace*)inFile->Get(Form("diphotonDumper/cms_hgg_13TeV"));
		std::list<RooAbsData*> data =  (inWS0->allData()) ;
		for (std::list<RooAbsData*>::const_iterator iterator = data.begin(), end = data.end(); iterator != end; ++iterator) {
			if(verbose_) std::cout << "[INFO] " <<**iterator << std::endl;
		}
		return 1;
	}
	RooWorkspace *inWS;
	if (isFlashgg_){
		inWS = (RooWorkspace*)inFile->Get("diphotonDumper/cms_hgg_13TeV");
		std::list<RooAbsData*> test =  (inWS->allData()) ;
		if (verbose_) {
			std::cout << " [INFO] WS contains " << std::endl;
			for (std::list<RooAbsData*>::const_iterator iterator = test.begin(), end = test.end(); iterator != end; ++iterator) {
				std::cout << **iterator << std::endl;
			}
		}
	} else {
		inWS = (RooWorkspace*)inFile->Get("cms_hgg_workspace");
		std::list<RooAbsData*> test =  (inWS->allData()) ;
		if (verbose_) {
			std::cout << " [INFO] WS contains " << std::endl;
			for (std::list<RooAbsData*>::const_iterator iterator = test.begin(), end = test.end(); iterator != end; ++iterator) {
				std::cout << **iterator << std::endl
					;}
			//std::cout << " WS contains " << *inWS->allData() << std::endl;
		}
	}
	if (inWS) { std::cout << "[INFO] workspace opened correctly" << std::endl;}
	else { std::cout << "[EXIT] Workspace is null pointer. exit" << std::endl; return 0;}

	RooRealVar *mass = (RooRealVar*)inWS->var("CMS_hgg_mass");
	RooRealVar *weight = (RooRealVar*)inWS->var("weight:weight");
	RooRealVar *weight0 = (RooRealVar*)inWS->var("weight");
	if (verbose_) std::cout << "[INFO] RooRealVars mass and weight found ? " << mass << ", " << weight << ", " << weight0 << std::endl;
	//	if ((!mass) || (!weight) || (!weight0)) return 0;
	mass->SetTitle("m_{#gamma#gamma}");
	mass->setUnit("GeV");
	RooRealVar *intLumi = (RooRealVar*)inWS->var("IntLumi");
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

	TFile *outFile = new TFile(outfilename_.c_str(),"RECREATE");
	RooWorkspace *outWS;
	if (is2011_) outWS = new RooWorkspace("wsig_7TeV");
	if (is2012_) outWS = new RooWorkspace("wsig_8TeV");
	if (isFlashgg_) outWS = new RooWorkspace("wsig_13TeV");
	RooWorkspace *mergeWS = 0;
	TFile *mergeFile = 0;
	if(!mergefilename_.empty()) {
		mergeFile = TFile::Open(mergefilename_.c_str());
		if (is2011_) mergeWS = (RooWorkspace*)mergeFile->Get("wsig_7TeV");
		else  mergeWS = (RooWorkspace*)mergeFile->Get("wsig_8TeV");
	}

	transferMacros(inFile,outFile);

	clonemap_t cloneSplinesMapRV;
	clonemap_t cloneSplinesMapWV;
	if (cloneFits_) {
		TRandom3 rand;
		rand.SetSeed(0);
		string newdatfilename = Form("tmp/config_%d.dat",rand.Integer(1.e6));
		string cloneWSname = outWS->GetName();
		cout << "[WARNING] Requested clone of fit parameters from file: " << cloneFitFile_ << " workspace: " << cloneWSname << endl;
		cout << "[WARNING] This means the configuration of nGaussians given in the datfile: " << datfilename_ << " WILL BE IGNORED" << endl;
		cout << "[WARNING] Instead the configuration will be picked up from the file: " << cloneFitFile_ << " and dumped in a tempory location: " << newdatfilename << endl;
		fillCloneSplinesMap(cloneSplinesMapRV,cloneSplinesMapWV,cloneFitFile_,cloneWSname);
		makeCloneConfig(cloneSplinesMapRV,cloneSplinesMapWV,newdatfilename);
		datfilename_ = newdatfilename;
		cout << "[INFO] Loaded splines from reference file: " << cloneFitFile_ << endl;

	}

	system(Form("mkdir -p %s/initialFits",plotDir_.c_str()));
	system("mkdir -p dat/in");
	parmap_t allParameters;

	// run fits for each line in datfile
	ifstream datfile;
	datfile.open(datfilename_.c_str());
	if (datfile.fail()) {
		std::cerr << "[ERROR] Could not open " << datfilename_ <<std::endl;
		exit(1);
	}
	while (datfile.good()){
		string line;
		getline(datfile,line);
		if (line=="\n" || line.substr(0,1)=="#" || line==" " || line.empty()) continue;
		vector<string> els;
		split(els,line,boost::is_any_of(" "));
		if( els.size()!=4 && els.size()!=6 ) {
			cerr << "Malformed line " << line << " " << els.size() <<endl;
			assert(0);
		}
		string proc = els[0];
		int cat = boost::lexical_cast<int>(els[1]);
		int nGaussiansRV = boost::lexical_cast<int>(els[2]);
		int nGaussiansWV = boost::lexical_cast<int>(els[3]);
		bool replace = false;
		pair<string,int> replaceWith;
		if( els.size()==6 ) {
			replaceWith = make_pair(els[4],boost::lexical_cast<int>(els[5]));
			replace = true;
		}

		cout << "-----------------------------------------------------------------" << endl;
		cout << Form("[INFO] Running fits for proc:%s - cat:%d with nGausRV:%d nGausWV:%d",proc.c_str(),cat,nGaussiansRV,nGaussiansWV) << endl;
		if( replace ) { cout << Form("Will replace parameters using  proc:%s - cat:%d",replaceWith.first.c_str(),replaceWith.second) << endl; }
		cout << "-----------------------------------------------------------------" << endl;
		// get datasets for each MH here
		map<int,RooDataSet*> datasetsRV;
		map<int,RooDataSet*> datasetsWV;
		map<int,RooDataSet*> datasets;

		for (int mh=mhLow_; mh<=mhHigh_; mh+=5){
			if (skipMass(mh)) continue;
			RooDataSet *dataRV; 
			RooDataSet *dataWV; 
			RooDataSet *data;  

			if (isFlashgg_){
				//	dataRV = (RooDataSet*)inWS->data(Form("%s_%d_13TeV_flashgg%s",proc.c_str(),mh,flashggCats_[cat].c_str())); //FIXME
				//	dataWV = (RooDataSet*)inWS->data(Form("%s_%d_13TeV_flashgg%s",proc.c_str(),mh,flashggCats_[cat].c_str())); // FIXME
				//std::cout << "[WARNING] FIXME - Artificially adding weight 0.085 (~correct weight for hgg events with 9000 MC events, 20/fb of data and e*a of 0.5) to signal sample events. Should eventually be included in workspace by default " << std::endl;
				if (verbose_)std::cout << "[INFO] opening dataset called "<< Form("%s_%d_13TeV_flashgg%s_",proc.c_str(),mh,flashggCats_[cat].c_str()) << " in in WS " << inWS << std::endl;
				RooDataSet *data0   = (RooDataSet*)inWS->data(Form("%s_%d_13TeV_flashgg%s_",proc.c_str(),mh,flashggCats_[cat].c_str()));
				//		if (verbose_) std::cout << "[INFO] dataset "<<  Form("%s_%d_13TeV_flashgg%s_",proc.c_str(),mh,flashggCats_[cat].c_str()) << " for RV+WV open ? " << *data0 <<  " with weight " << data0->weight() << std::endl;
				//		RooDataSet *dataRV0 = new RooDataSet("dataRV","dataRV",&*data0,*(data0->get()),"(dZ<1)*(weight:weight)","weight:weight");
				//		if (verbose_) std::cout << "[INFO] dataset RV open ? " << dataRV0 << std::endl;
				//		RooDataSet *dataWV0 = new RooDataSet("dataWV","dataWV",&*data0,*(data0->get()),"(dZ>=1)","weight");
				//		if (verbose_) std::cout << "[INFO] dataset WV open ? " << dataWV0 << std::endl;

				//   RooRealVar *w0 = new RooRealVar("weight:weight","weight:weight",0,30); //FIXME
				//		RooFormulaVar wFunc("w","event weight","@0",RooArgList(*w0));
				//		RooRealVar* w = (RooRealVar*) data0->addColumn(wFunc); 
				//		RooRealVar* wrv = (RooRealVar*) dataRV0->addColumn(wFunc); 
				//		RooRealVar* wwv = (RooRealVar*) dataWV0->addColumn(wFunc);
				data = (RooDataSet*) data0->Clone();
				dataRV = (RooDataSet*) data->reduce(Cut("dZ<1."));
				dataWV = (RooDataSet*) data->reduce(Cut("dZ>=1."));

				if (verbose_) std::cout << "[INFO] datasets? " << *data << std::endl;
				if (verbose_) std::cout << "[INFO] datasets? " << *dataRV << std::endl;
				if (verbose_) std::cout << "[INFO] datasets? " << *dataWV << std::endl;

				//FIXME above I artificially add in a weight to the 

				//	std::cout << "Data histos: " << std::endl;
				//	std::cout << Form("%s_%d_13TeV_flashgg%s",proc.c_str(),mh,flashggCats_[cat].c_str())  << std::endl;
				//	std::cout << "data open ?  data " << data << ", dataWV " << dataWV << ", data RV " << dataRV << std::endl;
				//	if (data ) {std :: cout << "data OK! " << std::endl; 
				//	} else { std::cout << "data not ok :( " << std::endl; return 0 ;}
			} else {
				dataRV = (RooDataSet*)inWS->data(Form("sig_%s_mass_m%d_rv_cat%d",proc.c_str(),mh,cat));
				dataWV = (RooDataSet*)inWS->data(Form("sig_%s_mass_m%d_wv_cat%d",proc.c_str(),mh,cat));
				data   = (RooDataSet*)inWS->data(Form("sig_%s_mass_m%d_cat%d",proc.c_str(),mh,cat));
			}
			datasetsRV.insert(pair<int,RooDataSet*>(mh,dataRV));
			datasetsWV.insert(pair<int,RooDataSet*>(mh,dataWV));
			datasets.insert(pair<int,RooDataSet*>(mh,data));
			if (verbose_) std::cout << "[INFO] Dataset: "<< *data << std::endl;
		}

		// these guys do the fitting
		// right vertex
		InitialFit initFitRV(mass,MH,mhLow_,mhHigh_,skipMasses_);
		initFitRV.setVerbosity(verbose_);
		if (!cloneFits_) {
			initFitRV.buildSumOfGaussians(Form("%s_cat%d",proc.c_str(),cat),nGaussiansRV,recursive_);
			initFitRV.setDatasets(datasetsRV);
			initFitRV.runFits(ncpu_);
			if (!runInitialFitsOnly_ && !replace) {
				initFitRV.saveParamsToFileAtMH(Form("dat/in/%s_cat%d_rv.dat",proc.c_str(),cat),constraintValueMass_);
				initFitRV.loadPriorConstraints(Form("dat/in/%s_cat%d_rv.dat",proc.c_str(),cat),constraintValue_);
				initFitRV.runFits(ncpu_);
			}
			if( replace ) {
				initFitRV.setFitParams(allParameters[replaceWith].first); 
			}
			if (!skipPlots_) initFitRV.plotFits(Form("%s/initialFits/%s_cat%d_rv",plotDir_.c_str(),proc.c_str(),cat));
		}
		parlist_t fitParamsRV = initFitRV.getFitParams();

		// wrong vertex
		InitialFit initFitWV(mass,MH,mhLow_,mhHigh_,skipMasses_);
		initFitWV.setVerbosity(verbose_);
		if (!cloneFits_) {
			initFitWV.buildSumOfGaussians(Form("%s_cat%d",proc.c_str(),cat),nGaussiansWV,recursive_);
			initFitWV.setDatasets(datasetsWV);
			initFitWV.runFits(ncpu_);
			if (!runInitialFitsOnly_ && !replace) {
				initFitWV.saveParamsToFileAtMH(Form("dat/in/%s_cat%d_wv.dat",proc.c_str(),cat),constraintValueMass_);
				initFitWV.loadPriorConstraints(Form("dat/in/%s_cat%d_wv.dat",proc.c_str(),cat),constraintValue_);
				initFitWV.runFits(ncpu_);
			}
			if( replace ) {
				initFitWV.setFitParams(allParameters[replaceWith].second); 
			}
			if (!skipPlots_) initFitWV.plotFits(Form("%s/initialFits/%s_cat%d_wv",plotDir_.c_str(),proc.c_str(),cat));
		}
		parlist_t fitParamsWV = initFitWV.getFitParams();

		allParameters[ make_pair(proc,cat) ] = make_pair(fitParamsRV,fitParamsWV);

		if (!runInitialFitsOnly_) {
			//these guys do the interpolation
			map<string,RooSpline1D*> splinesRV;
			map<string,RooSpline1D*> splinesWV;

			if (!cloneFits_){
				// right vertex
				LinearInterp linInterpRV(MH,mhLow_,mhHigh_,fitParamsRV,doSecondaryModels_,skipMasses_);
				linInterpRV.setVerbosity(verbose_);
				linInterpRV.setSecondaryModelVars(MH_SM,DeltaM,MH_2,higgsDecayWidth);
				linInterpRV.interpolate(nGaussiansRV);
				splinesRV = linInterpRV.getSplines();

				// wrong vertex
				LinearInterp linInterpWV(MH,mhLow_,mhHigh_,fitParamsWV,doSecondaryModels_,skipMasses_);
				linInterpWV.setVerbosity(verbose_);
				linInterpWV.setSecondaryModelVars(MH_SM,DeltaM,MH_2,higgsDecayWidth);
				linInterpWV.interpolate(nGaussiansWV);
				splinesWV = linInterpWV.getSplines();
			}
			else {
				splinesRV = cloneSplinesMapRV[make_pair(proc,cat)];
				splinesWV = cloneSplinesMapWV[make_pair(proc,cat)];
			}
			// this guy constructs the final model with systematics, eff*acc etc.

			if (isFlashgg_){
				intLumi = new RooRealVar("IntLumi","IntLumi",0,3000000); //FIXME
				//	intLumi->setVal(1000);
				//	std::cout << "[INFO] Artificially setting intLumi to " << intLumi->getVal() << ". FIXME before using on data"<< std::endl;
				//	outWS->import(*intLumi);
				FinalModelConstruction finalModel(mass,MH,intLumi,mhLow_,mhHigh_,proc,cat,doSecondaryModels_,systfilename_,skipMasses_,verbose_,procs_, flashggCats_,isCutBased_,sqrts_,doQuadraticSigmaSum_);
				if (isCutBased_){
					finalModel.setHighR9cats(highR9cats_);
					finalModel.setLowR9cats(lowR9cats_);
				}
				finalModel.setSecondaryModelVars(MH_SM,DeltaM,MH_2,higgsDecayWidth);
				finalModel.setRVsplines(splinesRV);
				finalModel.setWVsplines(splinesWV);
				finalModel.setRVdatasets(datasetsRV);
				finalModel.setWVdatasets(datasetsWV);
				//finalModel.setSTDdatasets(datasets);
				finalModel.makeSTDdatasets();
				if (is2011_) {
					finalModel.buildRvWvPdf("hggpdfsmrel_7TeV",nGaussiansRV,nGaussiansWV,recursive_);
				} 
				if (is2012_){
					finalModel.buildRvWvPdf("hggpdfsmrel_8TeV",nGaussiansRV,nGaussiansWV,recursive_);
				}
				if( isFlashgg_){
					finalModel.buildRvWvPdf("hggpdfsmrel_13TeV",nGaussiansRV,nGaussiansWV,recursive_);
				}
				finalModel.getNormalization();
				if (!skipPlots_) finalModel.plotPdf(plotDir_);
				finalModel.save(outWS);

			} else {

				FinalModelConstruction finalModel(mass,MH,intLumi,mhLow_,mhHigh_,proc,cat,doSecondaryModels_,systfilename_,skipMasses_,verbose_,procs_, flashggCats_,isCutBased_,sqrts_,doQuadraticSigmaSum_);
				if (isCutBased_){
					finalModel.setHighR9cats(highR9cats_);
					finalModel.setLowR9cats(lowR9cats_);
				}
				finalModel.setSecondaryModelVars(MH_SM,DeltaM,MH_2,higgsDecayWidth);
				finalModel.setRVsplines(splinesRV);
				finalModel.setWVsplines(splinesWV);
				finalModel.setRVdatasets(datasetsRV);
				finalModel.setWVdatasets(datasetsWV);
				//finalModel.setSTDdatasets(datasets);
				finalModel.makeSTDdatasets();
				if (is2011_) {
					finalModel.buildRvWvPdf("hggpdfsmrel_7TeV",nGaussiansRV,nGaussiansWV,recursive_);
				} 
				if (is2012_){
					finalModel.buildRvWvPdf("hggpdfsmrel_8TeV",nGaussiansRV,nGaussiansWV,recursive_);
				}
				if (isFlashgg_){
					finalModel.buildRvWvPdf("hggpdfsmrel_13TeV",nGaussiansRV,nGaussiansWV,recursive_);
				}
				finalModel.getNormalization();
				if (!skipPlots_) finalModel.plotPdf(plotDir_);
				finalModel.save(outWS);
			}
		}
	}

	datfile.close();

	sw.Stop();
	cout << "[INFO] Whole fitting process took..." << endl;
	cout << "\t";
	sw.Print();

	if (!runInitialFitsOnly_) { 
		sw.Start();
		cout << "[INFO] Starting to combine fits..." << endl;
		// this guy packages everything up
		Packager packager(outWS,procs_,nCats_,mhLow_,mhHigh_,skipMasses_,sqrts_,skipPlots_,plotDir_,mergeWS,cats_,flashggCats_);
		packager.packageOutput();
		sw.Stop();
		cout << "[INFO] Combination complete." << endl;
		cout << "[INFO ]Whole process took..." << endl;
		cout << "\t";
		sw.Print();
	}

	cout << "[INFO] Writing to file..." << endl;
	outFile->cd();
	outWS->Write();
	outFile->Close();
	inFile->Close();
	cout << "[INFO] Done." << endl;

	return 0;
}
