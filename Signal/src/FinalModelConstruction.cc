#include <fstream>
#include <sstream>
#include <iostream>

#include "TVectorT.h"
#include "TMatrixTSym.h"
#include "TCanvas.h"
#include "TF1.h"
#include "RooPlot.h"
#include "TLatex.h"
#include "TColor.h"
#include "TPaveText.h"
#include "TMultiGraph.h"
#include "RooVoigtian.h"
#include "RooProduct.h"
#include "RooAddition.h"
#include "RooConstVar.h"
#include "RooFormulaVar.h"

#include "boost/algorithm/string/split.hpp"
#include "boost/algorithm/string/classification.hpp"
#include "boost/algorithm/string/predicate.hpp"
#include "boost/lexical_cast.hpp"
#include "boost/algorithm/string/replace.hpp"
#include "boost/algorithm/string/erase.hpp"

#include "../interface/FinalModelConstruction.h"
#include "../../tdrStyle/tdrstyle.C"
#include "../../tdrStyle/CMS_lumi.C"

using namespace std;
using namespace RooFit;
using namespace boost;

template<class ResultT, class SourceT, class PredicateT> typename ResultT::iterator split_append(ResultT & dst, const SourceT & src, PredicateT pred)
{
	ResultT tmp;
	split( tmp, src, pred );
	size_t orig_size = dst.size();
	copy(tmp.begin(), tmp.end(), back_inserter(dst));	
	return dst.begin()+orig_size;
}

FinalModelConstruction::FinalModelConstruction( std::vector<int> massList, RooRealVar *massVar, RooRealVar *MHvar, RooRealVar *intL,int mhLow, int mhHigh, string proc, string cat, bool doSecMods, string systematicsFileName, vector<int> skipMasses, int verbosity,std::vector<std::string> procList, std::vector<std::string> flashggCats , string outDir, bool isProblemCategory ,bool isCB, int sqrts, bool quadraticSigmaSum)	:
  mass(massVar),
  MH(MHvar),
  intLumi(intL),
  mhLow_(mhLow),
  mhHigh_(mhHigh),
  proc_(proc),
  cat_(cat),
  outDir_(outDir),
  isProblemCategory_(isProblemCategory),
  doSecondaryModels(doSecMods),
  isCutBased_(isCB),
	sqrts_(sqrts),
	quadraticSigmaSum_(quadraticSigmaSum),
	skipMasses_(skipMasses),
  flashggCats_(flashggCats),
  verbosity_(verbosity),
  systematicsSet_(false),
  rvFractionSet_(false),
	procs_(procList)
{
  setTDRStyle();
  writeExtraText = true;       // if extra text
  extraText  = "";  // default extra text is "Preliminary"
  lumi_8TeV  = "19.1 fb^{-1}"; // default is "19.7 fb^{-1}"
  lumi_7TeV  = "4.9 fb^{-1}";  // default is "5.1 fb^{-1}"
  lumi_sqrtS = "13 TeV";       // used with iPeriod = 0, e.g. for simulation-only plots (default is an empty string)
  if (massList.size()==0){
    allMH_ = getAllMH();
  }else{
    allMH_ = massList;
  }

	if (sqrts_ ==7) is2011_=1;
	if (sqrts_ ==8) is2012_=1;
	if (sqrts_ ==13) isFlashgg_=1;
  // load xs and br info from Normalization_8TeV
  norm = new Normalization_8TeV();
  if(!norm->Init(sqrts_)){
	std::cout << "[ERROR] Normalization Initiation failed, exit." << std::endl;
	exit(1);
	}
  TGraph *brGraph = norm->GetBrGraph();
	brSpline = graphToSpline(Form("fbr_%dTeV",sqrts_),brGraph);

 // string procs[8] = {"ggh","vbf","wzh","wh","zh","tth","gg_grav","qq_grav"} ;//Don't want this hard-coded.
  for (unsigned int i=0; i<procs_.size(); i++){
    TGraph *xsGraph = norm->GetSigmaGraph(procs_[i].c_str());
    RooSpline1D *xsSpline = graphToSpline(Form("fxs_%s_%dTeV",procs_[i].c_str(),sqrts_),xsGraph);
    xsSplines.insert(pair<string,RooSpline1D*>(procs_[i],xsSpline));
  }
  
  paramDump_.open (Form("%s/paramDump_%s_%stxt",outDir.c_str(),proc_.c_str(),cat_.c_str()));
  vector<string> files;
  split( files, systematicsFileName, boost::is_any_of(",") );
  for(vector<string>::iterator fi=files.begin(); fi!=files.end(); ++fi ) {
	  loadSignalSystematics(*fi);
  }
  if (verbosity_) printSignalSystematics();
}

FinalModelConstruction::~FinalModelConstruction(){}

void FinalModelConstruction::addToSystematicsList(vector<string>::iterator begin, vector<string>::iterator end){
	for (vector<string>::iterator it=begin; it!=end; it++){
		string name = *it;
		float corr = 0.;
		int index = -1;
		if( it->find(":") != string::npos ) {
			vector<string> toks;
			split(toks,*it,boost::is_any_of(":"));
			name = toks[0];
			corr = boost::lexical_cast<float>(toks[1]);
			index = boost::lexical_cast<int>(toks[2]); 
			/// *it = Form("%dTeV%s",sqrts_,name.c_str());
			*it = name;
		}
		if (find(systematicsList.begin(),systematicsList.end(),name)!=systematicsList.end()) {
			cout << "[ERROR] - duplicate systematic names! " << *it << " already found in systematics list." << endl;
			exit(1);
		}
		else {
			systematicsList.push_back(name);
			systematicsCorr.push_back(corr);
			systematicsIdx.push_back(index);
		}
	}
}

void FinalModelConstruction::addToSystematicsList(vector<string> systs){
	addToSystematicsList( systs.begin(), systs.end() );
}

bool FinalModelConstruction::isGlobalSyst(string name){
	for (vector<string>::iterator it=globalScales.begin(); it!=globalScales.end(); it++){
		if (*it==name) return true;
	}
	for (vector<string>::iterator it=globalScalesCorr.begin(); it!=globalScalesCorr.end(); it++){
		if (*it==name) return true;
	}
	return false;
}

bool FinalModelConstruction::isPerCatSyst(string name){
	for (vector<string>::iterator it=photonCatScales.begin(); it!=photonCatScales.end(); it++){
		if (*it==name) return true;
	}
	for (vector<string>::iterator it=photonCatScalesCorr.begin(); it!=photonCatScalesCorr.end(); it++){
		if (*it==name) return true;
	}
	for (vector<string>::iterator it=photonCatSmears.begin(); it!=photonCatSmears.end(); it++){
		if (*it==name) return true;
	}
	for (vector<string>::iterator it=photonCatSmearsCorr.begin(); it!=photonCatSmearsCorr.end(); it++){
		if (*it==name) return true;
	}
	return false;
}

float FinalModelConstruction::getRequiredAddtionalGlobalScaleFactor(string name){
	float retVal=-999;
	// check non correlated
	if (globalScalesOpts.find(name)!=globalScalesOpts.end()) {
		for (vector<pair<string,float> >::iterator it=globalScalesOpts[name].begin(); it!=globalScalesOpts[name].end(); it++){
			//if (cat_.compare(flashggCats_[it->first])==0) return it->second;
			if (cat_.compare(it->first)==0) return it->second;
		}
	}
	// check correlated
	if (globalScalesCorrOpts.find(name)!=globalScalesCorrOpts.end()) {
		for (vector<pair<string,float> >::iterator it=globalScalesCorrOpts[name].begin(); it!=globalScalesCorrOpts[name].end(); it++){
			//if (cat_.compare(flashggCats_[it->first])==0) return it->second;
			if (cat_.compare(it->first)==0) return it->second;
		}
	}
	return retVal;
}

void FinalModelConstruction::setHighR9cats(string catString){
	vector<string> cats;
	split(cats,catString,boost::is_any_of(","));
	for (unsigned int i=0; i<cats.size(); i++){
		highR9cats.push_back(boost::lexical_cast<int>(cats[i]));
	}
}

void FinalModelConstruction::setLowR9cats(string catString){
	vector<string> cats;
	split(cats,catString,boost::is_any_of(","));
	for (unsigned int i=0; i<cats.size(); i++){
		lowR9cats.push_back(boost::lexical_cast<int>(cats[i]));
	}
}

bool FinalModelConstruction::isHighR9cat(){
	for (vector<int>::iterator it=highR9cats.begin(); it!=highR9cats.end(); it++){
		if (*it==cat_) return true;
	}
	return false;
}

bool FinalModelConstruction::isLowR9cat(){
	for (vector<int>::iterator it=lowR9cats.begin(); it!=lowR9cats.end(); it++){
		if (*it==cat_) return true;
	}
	return false;
}

void FinalModelConstruction::printSignalSystematics(){

	cout << "[INFO] Signal systematics info..." << endl;
	// names in systematicsList
	cout << "[INFO] The following systematic names are stored" << endl;
	for (vector<string>::iterator sys=systematicsList.begin(); sys!=systematicsList.end(); sys++){
		if (isGlobalSyst(*sys)) cout << "\t " << Form("%-50s -- global",sys->c_str()) << endl;
		if (isPerCatSyst(*sys)) cout << "\t " << Form("%-50s -- photon cat",sys->c_str()) << endl;
	}
	// nuisance parameters
	cout << "[INFO] Implementing the following floating nuisance parameters" << endl;
	for (map<string,RooAbsReal*>::iterator sys=photonSystematics.begin(); sys!=photonSystematics.end(); sys++){
		cout << "\t " << Form("%-50s",sys->first.c_str()) << " -- "; sys->second->Print();
	}
	// const parameters
	cout << "[INFO] Implementing the following constant parameters" << endl;
	for (map<string,RooConstVar*>::iterator sys=photonSystematicConsts.begin(); sys!=photonSystematicConsts.end(); sys++){
		cout << "\t " << Form("%-50s",sys->first.c_str()) << " -- "; sys->second->Print();
	}
}

void FinalModelConstruction::loadSignalSystematics(string filename){
	
	int diphotonCat=-1;
	string proc;
	ifstream datfile;
	datfile.open(filename.c_str());
	if (datfile.fail()) {
		cout << "[ERROR] Failed to load " << filename.c_str();
		exit(1);
	}
	while (datfile.good()){
		
		string line;
		getline(datfile,line);
		
		// The input file needs correct ordering
		if (line=="\n" || line.substr(0,1)=="#" || line==" " || line.empty()) continue;
		
		// First read the various categories and names
		if (starts_with(line,"photonCatScales=")){
			line = line.substr(line.find("=")+1,string::npos);
			if (line.empty()) continue;
			vector<string>::iterator beg = split_append(photonCatScales,line,boost::is_any_of(","));
			addToSystematicsList(beg,photonCatScales.end());
			if (verbosity_){
				cout << "[INFO] PhotonCatScales: ";
				if (verbosity_) printVec(photonCatScales);
			}
		}
		else if (starts_with(line,"photonCatScalesCorr=")){
			line = line.substr(line.find("=")+1,string::npos);
			if (line.empty()) continue;
			vector<string>::iterator beg = split_append(photonCatScalesCorr,line,boost::is_any_of(","));
			addToSystematicsList(beg,photonCatScalesCorr.end());
			if (verbosity_){
				cout << "[INFO] PhotonCatScalesCorr: ";
				if (verbosity_) printVec(photonCatScalesCorr);
			}
		}
		else if (starts_with(line,"photonCatSmears=")){
			line = line.substr(line.find("=")+1,string::npos);
			if (line.empty()) continue;
			vector<string>::iterator beg = split_append(photonCatSmears,line,boost::is_any_of(","));
			addToSystematicsList(beg,photonCatSmears.end());
			if (verbosity_){
				cout << "[INFO] PhotonCatSmears: ";
				if (verbosity_) printVec(photonCatSmears);
			}
		}
		else if (starts_with(line,"photonCatSmearsCorr=")){
			line = line.substr(line.find("=")+1,string::npos);
			if (line.empty()) continue;
			vector<string>::iterator beg = split_append(photonCatSmearsCorr,line,boost::is_any_of(","));
			addToSystematicsList(beg,photonCatSmearsCorr.end());
			if (verbosity_){
				cout << "[INFO] PhotonCatSmearsCorr: ";
				if (verbosity_) printVec(photonCatSmearsCorr);
			}
		}
		else if (starts_with(line,"globalScales=")){
			line = line.substr(line.find("=")+1,string::npos);
			if (line.empty()) continue;
			// split first by comma and then by colon for specific options
			vector<string> temp;
			split(temp,line,boost::is_any_of(","));
			if (verbosity_) cout << " [INFO] GlobalScales: ";
			for (vector<string>::iterator strIt=temp.begin(); strIt!=temp.end(); strIt++){
				vector<string> opts;
				vector<pair<string,float> > optDetails;
				split(opts,*strIt,boost::is_any_of(":"));
				globalScales.push_back(opts[0]);
				assert((opts.size()-1)%2==0);
				if (verbosity_) cout << "[" << opts[0] << ":";
				for (unsigned int i=1; i<opts.size(); i+=2) {
					//optDetails.push_back(make_pair(boost::lexical_cast<int>(opts[i]),boost::lexical_cast<float>(opts[i+1])));
					optDetails.push_back(make_pair((opts[i]),boost::lexical_cast<float>(opts[i+1])));
					if (verbosity_) cout << "(" << opts[i] << "," << opts[i+1] << ")";
				}
				globalScalesOpts.insert(make_pair(opts[0],optDetails));
			}
			if (verbosity_) cout << "]" << endl;
			addToSystematicsList(globalScales);
		}
		else if (starts_with(line,"globalScalesCorr=")){
			line = line.substr(line.find("=")+1,string::npos);
			if (line.empty()) continue;
			// split first by comma and then by colon for specific options
			vector<string> temp;
			split(temp,line,boost::is_any_of(","));
			if (verbosity_) cout << "[INFO] GlobalScalesCorr: ";
			for (vector<string>::iterator strIt=temp.begin(); strIt!=temp.end(); strIt++){
				vector<string> opts;
				vector<pair<string,float> > optDetails;
				split(opts,*strIt,boost::is_any_of(":"));
				globalScalesCorr.push_back(opts[0]);
				assert((opts.size()-1)%2==0);
				if (verbosity_) cout << "[" << opts[0] << ": ";
				for (unsigned int i=1; i<opts.size(); i+=2) {
					//optDetails.push_back(make_pair(boost::lexical_cast<int>(opts[i]),boost::lexical_cast<float>(opts[i+1])));
					optDetails.push_back(make_pair((opts[i]),boost::lexical_cast<float>(opts[i+1])));
					if (verbosity_) cout << "(" << opts[i] << "," << opts[i+1] << ")";
				}
				globalScalesCorrOpts.insert(make_pair(opts[0],optDetails));
			}
			addToSystematicsList(globalScalesCorr);
			if (verbosity_) cout << "]" << endl;
		}
		// Then read diphoton cat
		else if (starts_with(line,"diphotonCat")){
			diphotonCat = boost::lexical_cast<int>(line.substr(line.find("=")+1,string::npos));
		}
		// And the process
		else if (starts_with(line,"proc")){
			proc = line.substr(line.find('=')+1,string::npos);
			if (verbosity_) cout << "[INFO] Process:  " << proc << "  DiphoCat: " << diphotonCat << endl;
		}
		// Then read values
		else {
			stripSpace(line);
			vector<string> els;
			split(els,line,boost::is_any_of(" "));
			if (verbosity_) {cout << "\t"; printVec(els);}
			if (els.size()!=4) {
				cout << "[ERROR] I cant read this datfile " << line << endl;
				exit(1);
			}
			string phoSystName = els[0];
			double meanCh = lexical_cast<double>(els[1]);
			// round up scale syst if less than 1.e-4
			if( fabs(meanCh)<1.e-4 && fabs(meanCh)>=5.e-5 && phoSystName.find("scale")!=string::npos ) { 
				meanCh=( meanCh>0. ? 1.e-4 : -1.e-4 ); 
			} else if( fabs(meanCh)<1.e-4 && phoSystName.find("smear")!=string::npos ) { 
				meanCh = 0.;
			}
			if( meanCh != 0. ) { 
	string catname;
	if (sqrts_==8 || sqrts_==7) catname=Form("cat%d",diphotonCat);
	if (sqrts_ ==13) catname = Form("%s",flashggCats_[diphotonCat].c_str());
			
				addToSystMap(meanSysts,proc,diphotonCat,phoSystName,meanCh);
		
				RooConstVar *meanChVar = new RooConstVar(Form("const_%s_%s_%dTeV_mean_%s",proc.c_str(),catname.c_str(),sqrts_,phoSystName.c_str()),Form("const_%s_%s_%dTeV_mean_%s",proc.c_str(),catname.c_str(),sqrts_,phoSystName.c_str()),meanCh);
				photonSystematicConsts.insert(make_pair(meanChVar->GetName(),meanChVar));
			}
			double sigmaCh = lexical_cast<double>(els[2]);
			if( sigmaCh != 0. ) {
	string catname;
	if (sqrts_==8 || sqrts_==7) catname=Form("cat%d",diphotonCat);
	if (sqrts_ ==13) catname = Form("%s",flashggCats_[diphotonCat].c_str());
				addToSystMap(sigmaSysts,proc,diphotonCat,phoSystName,sigmaCh);
				RooConstVar *sigmaChVar = new RooConstVar(Form("const_%s_%s_%dTeV_sigma_%s",proc.c_str(),catname.c_str(),sqrts_,phoSystName.c_str()),Form("const_%s_%s_%dTeV_sigma_%s",proc.c_str(),catname.c_str(),sqrts_,phoSystName.c_str()),sigmaCh);
				photonSystematicConsts.insert(make_pair(sigmaChVar->GetName(),sigmaChVar));
			}
			double rateCh = lexical_cast<double>(els[3]);
			if( rateCh != 0. ) {
	string catname;
	if (sqrts_==8 || sqrts_==7) catname=Form("cat%d",diphotonCat);
	if (sqrts_ ==13) catname = Form("%s",flashggCats_[diphotonCat].c_str());
				addToSystMap(rateSysts,proc,diphotonCat,phoSystName,rateCh);
				RooConstVar *rateChVar = new RooConstVar(Form("const_%s_%s_%dTeV_rate_%s",proc.c_str(),catname.c_str(),sqrts_,phoSystName.c_str()),Form("const_%s_%s_%dTeV_rate_%s",proc.c_str(),catname.c_str(),sqrts_,phoSystName.c_str()),rateCh);
				photonSystematicConsts.insert(make_pair(rateChVar->GetName(),rateChVar));
			}
		}
	}
	datfile.close();

	// now make the actual systematics
	// for (vector<string>::iterator it=systematicsList.begin(); it!=systematicsList.end(); it++){
	for (size_t is=0; is<systematicsList.size(); ++is) {
		std::string & name = systematicsList[is];
		float & corr = systematicsCorr[is];
		int   & idx = systematicsIdx[is];
		if( corr != 0. ) {
			TString nuname = name;
			nuname = nuname.ReplaceAll(Form("%dTeV",sqrts_),"");
			RooRealVar *var1 = new RooRealVar(Form("CMS_hgg_nuisance_eigen1_%s",nuname.Data()),Form("CMS_hgg_nuisance_eigen1_%s",nuname.Data()),0.,-5.,5.);
			var1->setConstant(true);
			photonSystematics.insert(make_pair(var1->GetName(),var1));
			RooRealVar *var2 = new RooRealVar(Form("CMS_hgg_nuisance_eigen2_%s",nuname.Data()),Form("CMS_hgg_nuisance_eigen2_%s",nuname.Data()),0.,-5.,5.);
			var2->setConstant(true);
			photonSystematics.insert(make_pair(var2->GetName(),var2));
			
			TMatrixTSym<double> varmat(2);
			varmat[0][0] = 1.;//sigmaX*sigmaX;
			varmat[0][1] = corr;//*sigmaX*sigmaY;
			varmat[1][0] = corr;//*sigmaX*sigmaY;
			varmat[1][1] = 1.;//sigmaY*sigmaY;

			//// // Print Matrix 
			//// std::cout << "Covariance Matrix" << std::endl;
			//// varmat.Print();
			//// std::cout << "-----------------" << std::endl;
			//// 
			//// // 2 Get the eigenvalues/eigenvectors 
			TVectorT<double> eval;
			TMatrixT<double> evec = varmat.EigenVectors(eval);
			//// std::cout << "Matrix of Eigenvectors" << std::endl;
			//// evec.Print();
			//// std::cout << "----------------------" << std::endl;
			double cs = evec[idx][0]*sqrt(eval[0]) , ss = evec[idx][1]*sqrt(eval[1]);
			//// double tot = sqrt( cs*cs + ss*ss );
			//// std::cout << "size of eigenvec " << tot << std::endl;
			/// cs /= tot; ss /= tot;
			
			RooFormulaVar *var = new RooFormulaVar(Form("CMS_hgg_nuisance_%s",name.c_str()),
							       Form("CMS_hgg_nuisance_%s",name.c_str()),
							       Form("%1.3g * @0 + %1.3g * @1",cs,ss), RooArgList(*var1,*var2) );
			photonSystematics.insert(make_pair(var->GetName(),var));
			// var->Print("V");
		} else { 
			RooRealVar *var = new RooRealVar(Form("CMS_hgg_nuisance_%s",name.c_str()),Form("CMS_hgg_nuisance_%s",name.c_str()),0.,-5.,5.);
			var->setConstant(true);
			photonSystematics.insert(make_pair(var->GetName(),var));
		}
	}
}

void FinalModelConstruction::stripSpace(string &line){
	stringstream lineSt(line);
	line="";
	string word;
	while (lineSt >> word) {
		line.append(word).append(" ");
	}
	line = line.substr(0,line.size()-1);
}

void FinalModelConstruction::printVec(vector<string> vec){

	cout << "[";
	for (unsigned i=0; i<vec.size()-1;i++){
		cout << vec[i] << ",";
	}
	cout << vec[vec.size()-1] << "]" << endl;
}

void FinalModelConstruction::printSystMap(map<string,map<int,map<string,double> > > &theMap){

	for (map<string,map<int,map<string,double> > >::iterator p = theMap.begin(); p != theMap.end(); p++) {
		for (map<int,map<string,double> >::iterator c = p->second.begin(); c != p->second.end(); c++){
			cout << "Proc = " << p->first << "  DiphotonCat: " << c->first << endl;
			for (map<string,double>::iterator m = c->second.begin(); m != c->second.end(); m++){
				cout << "\t " << m->first << " : " << m->second << endl;
			}
		}
	}
}

void FinalModelConstruction::addToSystMap(map<string,map<int,map<string,double> > > &theMap, string proc, int diphotonCat, string phoSystName, double var){
	// does proc map exist?
	if (theMap.find(proc)!=theMap.end()) {
		// does the cat map exist?
		if (theMap[proc].find(diphotonCat)!=theMap[proc].end()){
			theMap[proc][diphotonCat].insert(make_pair(phoSystName,var));
		}
		else{
			map<string,double> temp;
			temp.insert(make_pair(phoSystName,var));
			theMap[proc].insert(make_pair(diphotonCat,temp));
		}
	}
	else {
		map<string,double> temp;
		map<int,map<string,double> > cTemp;
		temp.insert(make_pair(phoSystName,var));
		cTemp.insert(make_pair(diphotonCat,temp));
		theMap.insert(make_pair(proc,cTemp));
	}
}

bool FinalModelConstruction::skipMass(int mh){
	for (vector<int>::iterator it=skipMasses_.begin(); it!=skipMasses_.end(); it++) {
		if (*it==mh) return true;
	}
	return false;
}

vector<int> FinalModelConstruction::getAllMH(){
  vector<int> result;
  for (int m=mhLow_; m<=mhHigh_; m+=5){
		if (skipMass(m)) continue;
    if (verbosity_>=1) cout << "[INFO] FinalModelConstruction - Adding mass: " << m << endl;
    result.push_back(m);
  }
  return result;
}

void FinalModelConstruction::setSecondaryModelVars(RooRealVar *mh_sm, RooRealVar *deltam, RooAddition *mh_2, RooRealVar *width){
  MH_SM = mh_sm;
  DeltaM = deltam;
  MH_2 = mh_2;
  higgsDecayWidth = width;
  
  TGraph *brGraph = norm->GetBrGraph();
	brSpline_SM = graphToSpline(Form("fbr_%dTeV_SM",sqrts_),brGraph,MH_SM);
	brSpline_2 = graphToSpline(Form("fbr_%dTeV_2",sqrts_),brGraph,MH_2);
	brSpline_NW = graphToSpline(Form("fbr_%dTeV_NW",sqrts_),brGraph,MH);
  
  for (unsigned int i=0; i<procs_.size(); i++){
    TGraph *xsGraph = norm->GetSigmaGraph(procs_[i].c_str());
    RooSpline1D *xsSpline_SM = graphToSpline(Form("fxs_%s_%dTeV_SM",procs_[i].c_str(),sqrts_),xsGraph,MH_SM);
    RooSpline1D *xsSpline_2 = graphToSpline(Form("fxs_%s_%dTeV_2",procs_[i].c_str(),sqrts_),xsGraph,MH_2); 
    RooSpline1D *xsSpline_NW = graphToSpline(Form("fxs_%s_%dTeV_NW",procs_[i].c_str(),sqrts_),xsGraph,MH);
    xsSplines_SM.insert(pair<string,RooSpline1D*>(procs_[i],xsSpline_SM));
    xsSplines_2.insert(pair<string,RooSpline1D*>(procs_[i],xsSpline_2));
    xsSplines_NW.insert(pair<string,RooSpline1D*>(procs_[i],xsSpline_NW));
  }
  secondaryModelVarsSet=true;
}

void FinalModelConstruction::getRvFractionFunc(string name){
  assert(allMH_.size()==rvDatasets.size());
  assert(allMH_.size()==wvDatasets.size());
  vector<double> mhValues, rvFracValues;

  TF1 *pol = new TF1("pol","pol1",120,130); // set to straight line fit for RV fraction
  TGraph *temp = new TGraph();

  for (unsigned int i=0; i<allMH_.size(); i++){
    int mh = allMH_[i];
    mhValues.push_back(mh);
    double rvN = rvDatasets[mh]->sumEntries();
    double wvN = wvDatasets[mh]->sumEntries();
    if (rvN<0) rvN =0.;
    if (wvN<0) wvN =0.;
		double rvF = rvN/(rvN+wvN);
		//assert(rvF!=0) ; // i hope this never happens..
    // ^  it did..
    if (rvN< 0.001 && wvN < 0.001 )  rvF=1.; //stupid edge case caused by negative weights can cause a situation where rvFrac is 1,0,1 at 120, 125 and 130.... 
    if (rvF != rvF) rvF=1.; // incase nan when no entries
    rvFracValues.push_back(rvF);
    temp->SetPoint(i,mh,rvF);
    if (verbosity_) std::cout << "[INFO] RV/WV fraction for datasets " << *(rvDatasets[mh]) << " and " << *(wvDatasets[mh]) << " --- " << rvF << std::endl;
  }

  temp->Fit(pol,"Q");
  
  //turn this fit to rvFrac into a spline.
  TGraph *rvFGraph = new TGraph(pol);
  rvFracFunc = graphToSpline(name.c_str(),rvFGraph);
  
  //draw a debug/validation plot
  TMultiGraph *MG_rvFrac = new TMultiGraph();
  TCanvas *c = new TCanvas("rvF","rvF",500,500);
  vector < RooAbsReal *> rvFrac_vect; 
  int point =0;
  TGraph *  rvFracGraph = new TGraph();
  for (int m =120; m<131; m++){
    MH->setVal(m);
    if(verbosity_) std::cout << " [INFO] Interpolation of  rvFraction  m = " << m << " , rvFrac " << rvFracFunc->getVal() << std::endl;
    rvFracGraph->SetPoint(point,m,rvFracFunc->getVal());
    point++;
   }
  MG_rvFrac->Add(temp);
  MG_rvFrac->Add(rvFracGraph);
  MG_rvFrac->SetMinimum(0.5);
  MG_rvFrac->SetMaximum(1.2);
  TPaveText *pt = new TPaveText(.1,.9,.9,1.0,"NDC");
  pt->SetTextSize(0.045);
  pt->AddText(Form("%s %s RV Fraction",proc_.c_str(),cat_.c_str()));
  MG_rvFrac->Draw("ALP");
  pt->Draw();
  c->SaveAs(Form("%s/%s_%s_rvFrac_debug.pdf",outDir_.c_str(),proc_.c_str(),cat_.c_str()));
	
  // secondary models... 
  if (doSecondaryModels){
		rvFracFunc_SM = new RooSpline1D(Form("%s_SM",name.c_str()),name.c_str(),*MH_SM,mhValues.size(),&(mhValues[0]),&(rvFracValues[0]));
		rvFracFunc_2 = new RooSpline1D(Form("%s_2",name.c_str()),name.c_str(),*MH_2,mhValues.size(),&(mhValues[0]),&(rvFracValues[0]));
		rvFracFunc_NW = new RooSpline1D(Form("%s_NW",name.c_str()),name.c_str(),*MH,mhValues.size(),&(mhValues[0]),&(rvFracValues[0]));
	}
  rvFractionSet_=true;
}

RooAbsReal* FinalModelConstruction::getMeanWithPhotonSyst(RooAbsReal *dm, string name, bool isMH2, bool isMHSM){
	string catname;
	if (sqrts_==8 || sqrts_==7) catname=Form("cat%s",cat_.c_str());
	if (sqrts_ ==13) catname = Form("%s",cat_.c_str());

	if (!doSecondaryModels && (isMH2 || isMHSM)) {
		cout << "[ERROR] -- for some reason your asking for a dependence on MH_2 or MH_SM but are not running secondary models" << endl;
		exit(1);
	}
	if (isMH2 && isMHSM) {
		cout << "[ERROR] -- for some reason your asking for a dependence on MH_2 and MH_SM but both cannot be true" << endl;
		exit(1);
	}

	string formula="(@0+@1)*(1.";
	RooArgList *dependents = new RooArgList();
	if (isMH2) dependents->add(*MH_2);
	else if (isMHSM) dependents->add(*MH_SM);
	else dependents->add(*MH); // MH sits at @0
	dependents->add(*dm); // dm sits at @1

	// check for global scales first
	for (unsigned int i=0; i<systematicsList.size(); i++){
		string syst = systematicsList[i];
		int formPlace = dependents->getSize();
		if (isGlobalSyst(syst)) {
			RooAbsReal *nuisScale = photonSystematics[Form("CMS_hgg_nuisance_%s",syst.c_str())];
			formula += Form("+@%d",formPlace);
			// should check special extras 
			float additionalFactor = getRequiredAddtionalGlobalScaleFactor(syst);
			if (additionalFactor>-999) formula += Form("*%3.1f",additionalFactor);
			dependents->add(*nuisScale);
		}
	}
	// then do per photon scales
	for (unsigned int i=0; i<systematicsList.size(); i++){
		string syst = systematicsList[i];
		int formPlace = dependents->getSize();
		bool hasEffect = false;
		if (isPerCatSyst(syst)) {

			if (photonSystematicConsts.find(Form("const_%s_%s_%dTeV_mean_%s",proc_.c_str(),catname.c_str(),sqrts_,syst.c_str())) != photonSystematicConsts.end() ) {
				RooConstVar *constVar = photonSystematicConsts[Form("const_%s_%s_%dTeV_mean_%s",proc_.c_str(),catname.c_str(),sqrts_,syst.c_str())];
				RooAbsReal *nuisVar = photonSystematics[Form("CMS_hgg_nuisance_%s",syst.c_str())];
				if( verbosity_ ) { 
					std::cout << "[INFO] Systematic " << syst << std::endl;
					//nuisVar->Print("V");
				}
				if ( fabs(constVar->getVal())>=5.e-5) { 
					hasEffect = true;
					formula += Form("+@%d*@%d",formPlace,formPlace+1);
					dependents->add(*constVar);
					dependents->add(*nuisVar);
				}
			}
			if (verbosity_ && !hasEffect) {
				cout << "[WARNING] -- systematic " << syst << " is found to have no effect on the scale for category " << catname.c_str() << " and process " << proc_ << " so it is being skipped." << endl;
			}
		}
	}
	formula+=")";
	RooFormulaVar *formVar = new RooFormulaVar(name.c_str(),name.c_str(),formula.c_str(),*dependents);
	return formVar;
}

RooAbsReal* FinalModelConstruction::getSigmaWithPhotonSyst(RooAbsReal *sig_fit, string name){
	string catname;
	if (sqrts_==8 || sqrts_==7) catname=Form("cat%s",cat_.c_str());
	if (sqrts_ ==13) catname = Form("%s",cat_.c_str());
  
	string formula="@0*";
	RooArgList *dependents = new RooArgList();
	dependents->add(*sig_fit); // sig_fit sits at @0
	if (quadraticSigmaSum_) formula += "TMath::Sqrt(TMath::Max(1.e-4,1.";
	else formula += "TMath::Max(1.e-2,(1.";
	
	for (unsigned int i=0; i<systematicsList.size(); i++){
		string syst = systematicsList[i];
		int formPlace = dependents->getSize();
		bool hasEffect = false;
		if (isPerCatSyst(syst)) {
			if (photonSystematicConsts.find(Form("const_%s_%s_%dTeV_sigma_%s",proc_.c_str(),catname.c_str(),sqrts_,syst.c_str())) != photonSystematicConsts.end() ) {
				RooConstVar *constVar = photonSystematicConsts[Form("const_%s_%s_%dTeV_sigma_%s",proc_.c_str(),catname.c_str(),sqrts_,syst.c_str())];
				RooAbsReal *nuisVar = photonSystematics[Form("CMS_hgg_nuisance_%s",syst.c_str())];
      //constVar->Print(); //std::cout
      //nuisVar->Print(); //std::cout
				if (constVar->getVal()>=1.e-4) {
					hasEffect = true;
					if( quadraticSigmaSum_ ) { 
						formula += Form("+@%d*@%d*(2.+@%d)",formPlace,formPlace+1,formPlace+1);
					} else {
						formula += Form("+@%d*@%d",formPlace,formPlace+1);
					}
					dependents->add(*nuisVar);
					dependents->add(*constVar);
				}
			}
			if (verbosity_ && !hasEffect) {
				cout << "[WARNING] -- systematic " << syst << " is found to have no effect on the resolution for category " << catname.c_str() << " and process " << proc_ << " so it is being skipped." << endl;
			}
		}
	}
	formula+="))";
	RooFormulaVar *formVar = new RooFormulaVar(name.c_str(),name.c_str(),formula.c_str(),*dependents);
  //dependents->Print() ;//std::cout
    
	return formVar;
}

RooAbsReal* FinalModelConstruction::getRateWithPhotonSyst(string name){
	string catname;
	if (sqrts_==8 || sqrts_==7) catname=Form("cat%s",cat_.c_str());
	if (sqrts_ ==13) catname = Form("%s",cat_.c_str());
	
	string formula="(1.";
	RooArgList *dependents = new RooArgList();

	for (unsigned int i=0; i<systematicsList.size(); i++){
		string syst = systematicsList[i];
		int formPlace = dependents->getSize();
		bool hasEffect = false;
		if (isPerCatSyst(syst)) {
			if (photonSystematicConsts.find(Form("const_%s_%s_%dTeV_rate_%s",proc_.c_str(),catname.c_str(),sqrts_,syst.c_str())) != photonSystematicConsts.end() ) {
				RooConstVar *constVar = photonSystematicConsts[Form("const_%s_%s_%dTeV_rate_%s",proc_.c_str(),catname.c_str(),sqrts_,syst.c_str())];
				RooAbsReal *nuisVar = photonSystematics[Form("CMS_hgg_nuisance_%s",syst.c_str())];
				if (constVar->getVal()>=5.e-4) {
					hasEffect = true;
					formula += Form("+@%d*@%d",formPlace,formPlace+1);
					dependents->add(*constVar);
					dependents->add(*nuisVar);
				}
			}
			if (verbosity_ && !hasEffect) {
				cout << "[WARNING] -- systematic " << syst << " is found to have no effect on the rate for category " << catname.c_str() << " and process " << proc_ << " so it is being skipped." << endl;
			}
		}
	}

	formula+=")";	
	if (isCutBased_){
		if (isHighR9cat()) {
			formula += Form("*(1.+@%d)",dependents->getSize());
			dependents->add(*r9barrelNuisance);
		}
		if (isLowR9cat()) {
			formula += Form("*(1.+@%d)",dependents->getSize());
			dependents->add(*r9mixedNuisance);
		}
	}
	RooFormulaVar *formVar = new RooFormulaVar(name.c_str(),name.c_str(),formula.c_str(),*dependents);
	return formVar;
}

void FinalModelConstruction::setupSystematics(){
  
	vertexNuisance = new RooRealVar(Form("CMS_hgg_nuisance_deltafracright"),Form("CMS_hgg_nuisance_deltafracright"),0.,-1.,1.);
	vertexNuisance->setConstant(true);
	if (isCutBased_) {
		r9barrelNuisance = new RooRealVar(Form("CMS_hgg_nuisance_%dTeVdeltar9barrel",sqrts_),Form("CMS_hgg_nuisance_%dTeVdeltar9barrel",sqrts_),0.,-1.,1.);
		r9mixedNuisance = new RooRealVar(Form("CMS_hgg_nuisance_%dTeVdeltar9mixed",sqrts_),Form("CMS_hgg_nuisance_%dTeVdeltar9mixed",sqrts_),0.,-1.,1.);
		r9barrelNuisance->setConstant(true);
		r9mixedNuisance->setConstant(true);
	}
  systematicsSet_=true;
}

void FinalModelConstruction::buildStdPdf(string name, int nGaussians, bool recursive){

  if (!systematicsSet_) setupSystematics();
  vector<RooAddPdf*> pdfs;
  pdfs = buildPdf(name.c_str(),nGaussians,recursive,stdSplines);
  finalPdf = pdfs[0];
  if (doSecondaryModels){
    assert(secondaryModelVarsSet);
    finalPdf_SM = pdfs[1];
    finalPdf_2 = pdfs[2];
    finalPdf_NW = pdfs[3];
  }
}

void FinalModelConstruction::buildRvWvPdf(string name, int nGrv, int nGwv, bool recursive){
	string catname;
	if (sqrts_==8 || sqrts_==7) catname=Form("cat%s",cat_.c_str());
	if (sqrts_ ==13) catname = Form("%s",cat_.c_str());

  if (!rvFractionSet_) getRvFractionFunc(Form("%s_%s_%s_rvFracFunc",name.c_str(),proc_.c_str(),catname.c_str()));
  if (!systematicsSet_) setupSystematics();
  RooFormulaVar *rvFraction = new RooFormulaVar(Form("%s_%s_%s_rvFrac",name.c_str(),proc_.c_str(),catname.c_str()),Form("%s_%s_%s_rvFrac",name.c_str(),proc_.c_str(),catname.c_str()),"TMath::Min(@0+@1,1.0)",RooArgList(*vertexNuisance,*rvFracFunc));
  vector<RooAddPdf*> rvPdfs = buildPdf(name,nGrv,recursive,rvSplines,Form("_rv_%dTeV",sqrts_)); 
  vector<RooAddPdf*> wvPdfs = buildPdf(name,nGwv,recursive,wvSplines,Form("_wv_%dTeV",sqrts_)); 
  finalPdf = new RooAddPdf(Form("%s_%s_%s",name.c_str(),proc_.c_str(),catname.c_str()),Form("%s_%s_%s",name.c_str(),proc_.c_str(),catname.c_str()),RooArgList(*rvPdfs[0],*wvPdfs[0]),RooArgList(*rvFraction));
  if (doSecondaryModels){
    assert(secondaryModelVarsSet);
		RooFormulaVar *rvFraction_SM = new RooFormulaVar(Form("%s_%s_%s_rvFrac_SM",name.c_str(),proc_.c_str(),catname.c_str()),Form("%s_%s_%s_rvFrac",name.c_str(),proc_.c_str(),catname.c_str()),"TMath::Min(@0+@1,1.0)",RooArgList(*vertexNuisance,*rvFracFunc_SM));
		RooFormulaVar *rvFraction_2 = new RooFormulaVar(Form("%s_%s_%s_rvFrac_2",name.c_str(),proc_.c_str(),catname.c_str()),Form("%s_%s_%s_rvFrac",name.c_str(),proc_.c_str(),catname.c_str()),"TMath::Min(@0+@1,1.0)",RooArgList(*vertexNuisance,*rvFracFunc_2));
		RooFormulaVar *rvFraction_NW = new RooFormulaVar(Form("%s_%s_%s_rvFrac_NW",name.c_str(),proc_.c_str(),catname.c_str()),Form("%s_%s_%s_rvFrac",name.c_str(),proc_.c_str(),catname.c_str()),"TMath::Min(@0+@1,1.0)",RooArgList(*vertexNuisance,*rvFracFunc_NW));
		// buildNew Pdfs
    finalPdf_SM = new RooAddPdf(Form("%s_%s_%s_SM",name.c_str(),proc_.c_str(),catname.c_str()),Form("%s_%s_%s_SM",name.c_str(),proc_.c_str(),catname.c_str()),RooArgList(*rvPdfs[1],*wvPdfs[1]),RooArgList(*rvFraction_SM));
    finalPdf_2 = new RooAddPdf(Form("%s_%s_%s_2",name.c_str(),proc_.c_str(),catname.c_str()),Form("%s_%s_%s_2",name.c_str(),proc_.c_str(),catname.c_str()),RooArgList(*rvPdfs[2],*wvPdfs[2]),RooArgList(*rvFraction_2));
    finalPdf_NW = new RooAddPdf(Form("%s_%s_%s_NW",name.c_str(),proc_.c_str(),catname.c_str()),Form("%s_%s_%s_NW",name.c_str(),proc_.c_str(),catname.c_str()),RooArgList(*rvPdfs[3],*wvPdfs[3]),RooArgList(*rvFraction_NW));
  }
}

vector<RooAddPdf*> FinalModelConstruction::buildPdf(string name, int nGaussians, bool recursive, map<string,RooSpline1D*> splines, string rvwv){
  
  vector<RooAddPdf*> result;
	string catname;
	if (sqrts_==8 || sqrts_==7) catname=Form("cat%s",cat_.c_str());
	if (sqrts_ ==13) catname = Form("%s",cat_.c_str());

  RooArgList *gaussians = new RooArgList();
  RooArgList *coeffs = new RooArgList();
  string ext = Form("%s_%s%s",proc_.c_str(),catname.c_str(),rvwv.c_str());
  
  // for SM Higgs as Background
  RooArgList *gaussians_SM = new RooArgList();
  RooArgList *coeffs_SM = new RooArgList();
  
  // for Second Higgs
  RooArgList *gaussians_2 = new RooArgList();
  RooArgList *coeffs_2 = new RooArgList();

  // for Natural Width
  RooArgList *voigtians_NW = new RooArgList();
  RooArgList *coeffs_NW = new RooArgList();
  
  //loads of debug/validation plots and holders for the data
  TMultiGraph *MG_dm = new TMultiGraph();
  TMultiGraph *MG_coeffs = new TMultiGraph();
  TMultiGraph *MG_mean = new TMultiGraph();
  TMultiGraph *MG_sigma = new TMultiGraph();
  TCanvas *c = new TCanvas();
  vector < RooAbsReal *> dm_vect; 
  vector < RooAbsReal *> coeffs_vect; 
  vector < RooAbsReal *> mean_vect; 
  vector < RooAbsReal *> sigma_vect; 
  vector <TGraph * > dmGraphs;
  vector <TGraph * > coeffsGraphs;
  vector <TGraph * > meanGraphs;
  vector <TGraph * > sigmaGraphs;

  for (int g=0; g<nGaussians; g++){
    RooAbsReal *dm = splines[Form("dm_g%d",g)];
    dm->SetName(Form("dm_g%d_%s",g,ext.c_str()));
    RooAbsReal *mean = getMeanWithPhotonSyst(dm,Form("mean_g%d_%s",g,ext.c_str()));
    RooAbsReal *sig_fit = splines[Form("sigma_g%d",g)];
    sig_fit->SetName(Form("sigma_g%d_%s",g,ext.c_str()));
    RooAbsReal *sigma = getSigmaWithPhotonSyst(sig_fit,Form("sig_g%d_%s",g,ext.c_str()));
		RooGaussian *gaus = new RooGaussian(Form("gaus_g%d_%s",g,ext.c_str()),Form("gaus_g%d_%s",g,ext.c_str()),*mass,*mean,*sigma);
    dm_vect.push_back(dm);
    mean_vect.push_back(mean);
    sigma_vect.push_back(sigma);
    TGraph* this_dmGraph = new TGraph();
    this_dmGraph->SetName(Form("dm_g%d",g));
    dmGraphs.push_back(this_dmGraph);
    TGraph* this_sigmaGraph = new TGraph();
    this_sigmaGraph->SetName(Form("sigma_g%d",g));
    sigmaGraphs.push_back(this_sigmaGraph);
    TGraph* this_meanGraph = new TGraph();
    this_meanGraph->SetName(Form("mean_g%d",g));
    meanGraphs.push_back(this_meanGraph);
    
    gaussians->add(*gaus);
    // add secondary models as well
    if (doSecondaryModels){
      assert(secondaryModelVarsSet);
      // sm higgs as background
      RooAbsReal *dmSM = splines[Form("dm_g%d_SM",g)];
      dmSM->SetName(Form("dm_g%d_%s_SM",g,ext.c_str()));
			RooAbsReal *meanSM = getMeanWithPhotonSyst(dmSM,Form("mean_g%d_%s_SM",g,ext.c_str()),false,true);
      RooAbsReal *sig_fitSM = splines[Form("sigma_g%d_SM",g)];
      sig_fitSM->SetName(Form("sigma_g%d_%s_SM",g,ext.c_str()));
			RooAbsReal *sigmaSM = getSigmaWithPhotonSyst(sig_fitSM,Form("sig_g%d_%s_SM",g,ext.c_str()));
      RooGaussian *gausSM = new RooGaussian(Form("gaus_g%d_%s_SM",g,ext.c_str()),Form("gaus_g%d_%s_SM",g,ext.c_str()),*mass,*meanSM,*sigmaSM);
      gaussians_SM->add(*gausSM);
      // second degen higgs
      RooAbsReal *dm2 = splines[Form("dm_g%d_2",g)];
      dm2->SetName(Form("dm_g%d_%s_2",g,ext.c_str()));
			RooAbsReal *mean2 = getMeanWithPhotonSyst(dm2,Form("mean_g%d_%s_2",g,ext.c_str()),true,false);
      RooAbsReal *sig_fit2 = splines[Form("sigma_g%d_2",g)];
      sig_fit2->SetName(Form("sigma_g%d_%s_2",g,ext.c_str()));
			RooAbsReal *sigma2 = getSigmaWithPhotonSyst(sig_fit2,Form("sig_g%d_%s_2",g,ext.c_str()));
      RooGaussian *gaus2 = new RooGaussian(Form("gaus_g%d_%s_2",g,ext.c_str()),Form("gaus_g%d_%s_2",g,ext.c_str()),*mass,*mean2,*sigma2);
      gaussians_2->add(*gaus2);
      // natural width
      RooVoigtian *voigNW = new RooVoigtian(Form("voig_g%d_%s_NW",g,ext.c_str()),Form("voig_g%d_%s_NW",g,ext.c_str()),*mass,*mean,*higgsDecayWidth,*sigma);
      voigtians_NW->add(*voigNW);
    }
    if (g<nGaussians-1) {
      RooAbsReal *frac = splines[Form("frac_g%d",g)];
      frac->SetName(Form("frac_g%d_%s",g,ext.c_str()));
      coeffs->add(*frac);
      coeffs_vect.push_back(frac);
      TGraph* this_coeffsGraph = new TGraph();
      this_coeffsGraph->SetName(Form("frac_g%d_%s",g,ext.c_str()));
      coeffsGraphs.push_back(this_coeffsGraph);
      // add secondary models as well
      if (doSecondaryModels){
        assert(secondaryModelVarsSet);
        // sm higgs as background
        RooAbsReal *fracSM = splines[Form("frac_g%d_SM",g)];
        fracSM->SetName(Form("frac_g%d_%s_SM",g,ext.c_str()));
        coeffs_SM->add(*fracSM);
        // second degen higgs
        RooAbsReal *frac2 = splines[Form("frac_g%d_2",g)];
        frac2->SetName(Form("frac_g%d_%s_2",g,ext.c_str()));
        coeffs_2->add(*frac2);
        // natural width
        coeffs_NW->add(*frac);
      }
    }
  }
  
  //make those debug/validation plots!
	TLegend *legdm = new TLegend(0.15,0.55,0.5,0.89);
	TLegend *legmean = new TLegend(0.15,0.55,0.5,0.89);
	TLegend *legsigma = new TLegend(0.15,0.55,0.5,0.89);
	TLegend *legcoeffs = new TLegend(0.15,0.55,0.5,0.89);
	legdm->SetFillStyle(0);
	legdm->SetLineColor(0);
	legdm->SetTextSize(0.03);
	legmean->SetFillStyle(0);
	legmean->SetLineColor(0);
	legmean->SetTextSize(0.03);
	legsigma->SetFillStyle(0);
	legsigma->SetLineColor(0);
	legsigma->SetTextSize(0.03);
	legcoeffs->SetFillStyle(0);
	legcoeffs->SetLineColor(0);
	legcoeffs->SetTextSize(0.03);
  assert(dm_vect.size() == sigma_vect.size()); //otherwise we are in trouble!
  assert(dm_vect.size() == mean_vect.size()); //otherwise we are in trouble!
  assert(coeffs_vect.size() == mean_vect.size()-1); //otherwise we are in trouble!
  paramDump_ <<proc_ <<"_"<< cat_ << "_" << rvwv <<" --> & mh 120 & mh 125 & mh 130 \\ " << std::endl;
  for (unsigned int g =0 ; g< dm_vect.size() ; g++){
    
    int point=0;
    if (g>0){
      coeffsGraphs[g-1]->SetMarkerStyle(21);
      coeffsGraphs[g-1]->SetMarkerColor(kBlue+10*(g-1));
      legcoeffs->AddEntry(coeffsGraphs[g-1],coeffsGraphs[g-1]->GetName(),"lep");
    }
    dmGraphs[g]->SetMarkerStyle(21+g);
    dmGraphs[g]->SetMarkerColor(kBlue+10*g);
    meanGraphs[g]->SetMarkerStyle(21+g);
    meanGraphs[g]->SetMarkerColor(kBlue+10*g);
    sigmaGraphs[g]->SetMarkerStyle(21+g);
    sigmaGraphs[g]->SetMarkerColor(kBlue+10*g);
    legdm->AddEntry(dmGraphs[g],dmGraphs[g]->GetName(),"lep");
    legmean->AddEntry(meanGraphs[g],meanGraphs[g]->GetName(),"lep");
    legsigma->AddEntry(sigmaGraphs[g],sigmaGraphs[g]->GetName(),"lep");
    
    paramDump_  <<proc_ <<"_"<< cat_ << "_" << rvwv<< " dm" << g ;
    for (int m =120; m<131; m++){
    bool print = (m==120 || m==125 || m==130);
      MH->setVal(m);
      if(verbosity_) std::cout << "[INFO] interpolation of gaussian  " << g << " at mH = " << m << " , dm " << dm_vect[g]->getVal() << std::endl;
      dmGraphs[g]->SetPoint(point,m,dm_vect[g]->getVal());
        point++;
      if (print) paramDump_ << " & " << dm_vect[g]->getVal() ;  
     }
     paramDump_ << " \\ " <<std::endl;

    point=0;
    paramDump_  <<proc_ <<"_"<< cat_ << "_" << rvwv<< " sigma" << g ;
    for (int m =120; m<131; m++){
    bool print = (m==120 || m==125 || m==130);
      MH->setVal(m);
      if(verbosity_) std::cout << "[INFO] interpolation of gaussian  " << g << " at mH = " << m << " , sigma " << sigma_vect[g]->getVal() << std::endl;
      meanGraphs[g]->SetPoint(point,m,mean_vect[g]->getVal());
      sigmaGraphs[g]->SetPoint(point,m,sigma_vect[g]->getVal());
        point++;
      if (print) paramDump_ << " & " << sigma_vect[g]->getVal() ;  
      }
     paramDump_ << " \\ " <<std::endl;

    point=0;
    if (g>0) paramDump_  <<proc_ <<"_"<< cat_ << "_" << rvwv<< "coeff" << (g-1) ;
    for (int m =120; m<131; m++){
    bool print = (m==120 || m==125 || m==130);
      MH->setVal(m);
      if (g>0){
        coeffsGraphs[g-1]->SetPoint(point-1,m,coeffs_vect[g-1]->getVal());
       if(verbosity_) std::cout << "[INFO] interpolation of gaussian  " << g << " at mH = " << m << " , coeff " << sigma_vect[g-1]->getVal() << std::endl;
      if (print) paramDump_ << " & " << coeffs_vect[g-1]->getVal() ;  
      }
    point++;
    }
   if (g>0) paramDump_ << " \\ " <<std::endl;
    point++;
    MG_dm->Add(dmGraphs[g]);
    MG_mean->Add(meanGraphs[g]);
    MG_sigma->Add(sigmaGraphs[g]);
    if (g>0)  MG_coeffs->Add(coeffsGraphs[g-1]);
  }
  c->SetName(Form("%s %s %s ",proc_.c_str(),cat_.c_str(),rvwv.c_str()));
  c->SetTitle(Form("%s %s %s ",proc_.c_str(),cat_.c_str(),rvwv.c_str()));
  TPaveText *pt = new TPaveText(.1,.4,.9,.8,"NDC");
  pt->AddText(Form("%s %s %s",proc_.c_str(),catname.c_str(),rvwv.c_str()));
  pt->AddText("delta m -  top right");
  pt->AddText("sigma -  bottom left");
  pt->AddText("recursive coeffs -  bottom right");
  c->Divide(2,2);
  c->cd(1);
  pt->Draw();
  c->cd(2);
  MG_dm->SetTitle(Form("%s %s %s",proc_.c_str(),catname.c_str(),rvwv.c_str()));
  MG_dm->Draw("ALP");
  legdm->Draw();
  c->cd(3);
  MG_sigma->Draw("ALP");
  legsigma->Draw();
  c->cd(4);
  MG_coeffs->Draw("ALP");
  legcoeffs->Draw();
  c->SaveAs(Form("%s/%s_%s_%s_interpolation_debug.pdf",outDir_.c_str(),proc_.c_str(),cat_.c_str(),rvwv.c_str()));
  assert(gaussians->getSize()==nGaussians && coeffs->getSize()==nGaussians-1);
  RooAddPdf *pdf = new RooAddPdf(Form("%s_%s",name.c_str(),ext.c_str()),Form("%s_%s",name.c_str(),ext.c_str()),*gaussians,*coeffs,recursive);
  result.push_back(pdf);
  
  // add secondary models as well
  if (doSecondaryModels){
    assert(secondaryModelVarsSet);
    // sm higgs as background
    RooAddPdf *pdf_SM = new RooAddPdf(Form("%s_%s_SM",name.c_str(),ext.c_str()),Form("%s_%s_SM",name.c_str(),ext.c_str()),*gaussians_SM,*coeffs_SM,recursive);
    result.push_back(pdf_SM);
    // second degen higgs
    RooAddPdf *pdf_2 = new RooAddPdf(Form("%s_%s_2",name.c_str(),ext.c_str()),Form("%s_%s_2",name.c_str(),ext.c_str()),*gaussians_2,*coeffs_2,recursive);
    result.push_back(pdf_2);
    // natural width
    RooAddPdf *pdf_NW = new RooAddPdf(Form("%s_%s_NW",name.c_str(),ext.c_str()),Form("%s_%s_NW",name.c_str(),ext.c_str()),*voigtians_NW,*coeffs_NW,recursive);
    result.push_back(pdf_NW);
  }

  return result;
}

void FinalModelConstruction::setRVsplines(map<string,RooSpline1D*> splines){
  rvSplines = splines;
}

void FinalModelConstruction::setWVsplines(map<string,RooSpline1D*> splines){
  wvSplines = splines;
}

void FinalModelConstruction::setSTDsplines(map<string,RooSpline1D*> splines){
  stdSplines = splines;
}

void FinalModelConstruction::setRVdatasets(map<int,RooDataSet*> data){
  rvDatasets = data;
}

void FinalModelConstruction::setFITWVdatasets(map<int,RooDataSet*> data){
  wvFITDatasets = data;
}

void FinalModelConstruction::setFITRVdatasets(map<int,RooDataSet*> data){
  rvFITDatasets = data;
}

void FinalModelConstruction::setWVdatasets(map<int,RooDataSet*> data){
  wvDatasets = data;
}


void FinalModelConstruction::setSTDdatasets(map<int,RooDataSet*> data){
  stdDatasets = data;
}

void FinalModelConstruction::setFITdatasets(map<int,RooDataSet*> data){
  fitDatasets = data;
}
void FinalModelConstruction::makeSTDdatasets(){
	string catname;
	if (sqrts_==8 || sqrts_==7) catname=Form("cat%s",cat_.c_str());
	if (sqrts_ ==13) catname = Form("%s",cat_.c_str());
  for (unsigned int i=0; i<allMH_.size(); i++){
    int mh=allMH_[i];
		RooDataSet *data = (RooDataSet*)rvDatasets[mh]->Clone(Form("sig_%s_mass_m%d_%s",proc_.c_str(),mh,catname.c_str()));
		data->append(*wvDatasets[mh]);
		stdDatasets.insert(pair<int,RooDataSet*>(mh,data));
	}	
}

void FinalModelConstruction::makeFITdatasets(){
	string catname;
	if (sqrts_==8 || sqrts_==7) catname=Form("cat%s",cat_.c_str());
	if (sqrts_ ==13) catname = Form("%s",cat_.c_str());
  for (unsigned int i=0; i<allMH_.size(); i++){
    int mh=allMH_[i];
		RooDataSet *data = (RooDataSet*)rvFITDatasets[mh]->Clone(Form("sig_%s_mass_m%d_%s",proc_.c_str(),mh,catname.c_str()));
		data->append(*wvFITDatasets[mh]);
		fitDatasets.insert(pair<int,RooDataSet*>(mh,data));
	}	
}

void FinalModelConstruction::plotPdf(string outDir){
	string catname;
	if (sqrts_==8 || sqrts_==7) catname=Form("cat%s",cat_.c_str());
	if (sqrts_ ==13) catname = Form("%s",cat_.c_str());
  system(Form("mkdir -p %s",outDir.c_str()));
  
  TCanvas *canv = new TCanvas();
  RooPlot *dataPlot = mass->frame(Title(Form("%s_%s",proc_.c_str(),catname.c_str())),Range(110,140));
  TPaveText *pt = new TPaveText(.7,.5,.95,.8,"NDC");
  //TH1F * dummy = new TH1F("d","d",1,0,1);
  //dummy->SetMarkerColor(kWhite);
  //pt->AddText(Form("Fit using PDF from :"); 
  std::vector<int> colorList ={7,9,4,2,8,5,1,14};//kCyan,kMagenta,kBlue, kRed,kGreen,kYellow,kBlack, kGray};
  for (unsigned int i=0; i<allMH_.size(); i++){
    int mh=allMH_[i];
    stdDatasets[mh]->plotOn(dataPlot,Binning(160),MarkerColor(colorList[i]));
    MH->setVal(mh);
    extendPdf->plotOn(dataPlot,LineColor(colorList[i]));
    pt->AddText(Form("RV %d: %s",mh,rvFITDatasets[mh]->GetName())); 
    pt->AddText(Form("WV %d: %s",mh,wvFITDatasets[mh]->GetName())); 
   // extendPdf->Print("V");
  }
  dataPlot->SetTitle(Form("combined RV WV fits for %s %s",proc_.c_str(),catname.c_str()));
  dataPlot->Draw();
  pt->Draw("same");
  canv->Print(Form("%s/%s_%s_fits.pdf",outDir.c_str(),proc_.c_str(),catname.c_str()));
  canv->Print(Form("%s/%s_%s_fits.png",outDir.c_str(),proc_.c_str(),catname.c_str()));
  
  RooPlot *pdfPlot = mass->frame(Title(Form("%s_%s",proc_.c_str(),catname.c_str())),Range(100,160));
	pdfPlot->GetYaxis()->SetTitle(Form("Pdf projection per %2.1f GeV",(mass->getMax()-mass->getMin())/160.));
  for (int mh=mhLow_; mh<=mhHigh_; mh++){
    MH->setVal(mh);
		// to get correct normlization need to manipulate with bins and range
    extendPdf->plotOn(pdfPlot,Normalization(mass->getBins()/160.*(mass->getMax()-mass->getMin())/60.,RooAbsReal::RelativeExpected));
  }
  string sim="Simulation Preliminary";
  pdfPlot->Draw();
  CMS_lumi( canv, 0,0, sim );
  TLatex *latex = new TLatex();	
  latex->SetTextSize(0.045);
  latex->SetNDC();
  latex->DrawLatex(0.6,0.78,Form("#splitline{%s}{%s}",proc_.c_str(),catname.c_str()));
  canv->Print(Form("%s/%s_%s_interp.pdf",outDir.c_str(),proc_.c_str(),catname.c_str()));
  canv->Print(Form("%s/%s_%s_interp.png",outDir.c_str(),proc_.c_str(),catname.c_str()));
  delete canv;

}

RooSpline1D* FinalModelConstruction::graphToSpline(string name, TGraph *graph){
  
  vector<double> xValues, yValues;
  for (double mh=mhLow_; mh<(mhHigh_+0.25); mh+=0.5){
    xValues.push_back(mh);
    yValues.push_back(graph->Eval(mh));
  }
  RooSpline1D *res = new RooSpline1D(name.c_str(),name.c_str(),*MH,xValues.size(),&(xValues[0]),&(yValues[0]));
  return res;
}

RooSpline1D* FinalModelConstruction::graphToSpline(string name, TGraph *graph, RooAbsReal *var){
  
  vector<double> xValues, yValues;
  for (double mh=mhLow_; mh<(mhHigh_+0.25); mh+=0.5){
    xValues.push_back(mh);
    yValues.push_back(graph->Eval(mh));
  }
  RooSpline1D *res = new RooSpline1D(name.c_str(),name.c_str(),*var,xValues.size(),&(xValues[0]),&(yValues[0]));
  return res;
}

void FinalModelConstruction::getNormalization(){
	string catname;
	if (sqrts_==8 || sqrts_==7) catname=Form("cat%s",cat_.c_str());
	if (sqrts_ ==13) catname = Form("%s",cat_.c_str());
	
	std::string procLowerCase_ = proc_;
  std::transform(procLowerCase_.begin(), procLowerCase_.end(), procLowerCase_.begin(), ::tolower); 
  TGraph *temp = new TGraph();
  bool fitToConstant=0; //if low-stats category, don;t try to fit to polynomial
  for (unsigned int i=0; i<allMH_.size(); i++){
    double mh = double(allMH_[i]);
    RooDataSet *data = stdDatasets[mh];

	double effAcc =0.;
	if (intLumi) {
    // calcu eA as sumEntries / totalxs * totalbr * intL
    float sumEntries = data->sumEntries(); 
    if (sumEntries <0 ) {
    sumEntries =0; //negative eff*acc makes no sense...
    fitToConstant=1;
    }
    effAcc = (sumEntries/(intLumi->getVal()*norm->GetXsection(mh,procLowerCase_)*norm->GetBR(mh)));
		if(verbosity_)std::cout << "[INFO] (FinalModelConstruction) intLumi " << intLumi->getVal() <<", effAcc " << effAcc << std::endl;
		if(verbosity_)std::cout << "[INFO] (FinalModelConstruction) data " << *data << std::endl;
		if(verbosity_)std::cout << "[INFO] (FinalModelConstruction) sumEntries " << sumEntries <<", norm->GetXsection(mh,procLowerCase_) " << norm->GetXsection(mh,procLowerCase_) << " norm->GetBR(mh) " << norm->GetBR(mh)<< std::endl;
		} else {
		std::cout << "[ERROR] IntLumi rooRealVar is not in this workspace. exit." << std::endl;
		return ;
		//double intLumiVal =19700.;
    
    //effAcc = (data->sumEntries()/(intLumiVal*norm->GetXsection(mh,procLowerCase_)*norm->GetBR(mh)));
		}
    temp->SetPoint(i,mh,effAcc);
  }

  //this bit defines how we turnt he eff*acc into a spline
  //if it is a problem category (ie we have had to subsitute even the RV dataset
  //or if the dataset has negative sumWeights at any mass point, then fit to a constant pol0
  //if not, fit to a pol2, but make sure that the min/max is noit in the range 120->130
  //because we don;t expect a drastic change in that range...
  TCanvas *tc_lc = new TCanvas("c","c",500,500);
  if (isProblemCategory_) fitToConstant=1;
  TF1 *pol;
  if (!fitToConstant){
    TF1 *pol2= new TF1("pol","pol2",120,130); // set to y= ax^2+bx+c
    pol=pol2;
    //temp->Fit(pol2,"EMFEX0") :
    //temp->Fit(pol2,"QEMFEX0");
    //pol->SetParLimits(2,0.01,999); // want a in y=ax^2 +bx+c to not be 0!
    temp->Fit(pol,"Q");
    float b=pol->GetParameter(1) ;// y = [0] + [1]*x + [2]*x*x
    float a=pol->GetParameter(2) ;// y = [0] + [1]*x + [2]*x*x
    float parabola_extremum_x = -b/(2*a);
    if (verbosity_>1) std::cout << "[INFO] e*a fit to pol2 has vertex at " <<  parabola_extremum_x << std::endl;
    if ( parabola_extremum_x  > 120. && parabola_extremum_x < 130){
      TF1 *pol1= new TF1("pol","pol1",120,130); // set to constant
      pol=pol1;
      temp->Fit(pol,"Q");
    }
  } else {
    TF1 *pol0= new TF1("pol","pol0",120,130); //  problem dataset, set to constant fit
     pol=pol0;
     temp->Fit(pol,"Q");
  }
  //temp->SetMinimum(0.);
  //temp->SetMinimum(0.66*temp->GetHistogram()->GetMaximum());
  //temp->SetMaximum(1.5*temp->GetHistogram()->GetMaximum());
  temp->Draw();
  temp->Fit(pol,"Q");
  TPaveText *pt = new TPaveText(.25,.9,.9,1.0,"NDC");
  pt->SetTextSize(0.045);
  pt->AddText(Form("%s %s eff*acc",proc_.c_str(),cat_.c_str()));
  pt->Draw() ;
  tc_lc->Print(Form("%s/%s_%s_ea_fit_to_pol2.png",outDir_.c_str(),proc_.c_str(),catname.c_str()));
  tc_lc->Print(Form("%s/%s_%s_ea_fit_to_pol2.pdf",outDir_.c_str(),proc_.c_str(),catname.c_str()));

  //turn that graph into a spline!
  TGraph *eaGraph = new TGraph(pol);
  RooSpline1D *eaSpline = graphToSpline(Form("fea_%s_%s_%dTeV",proc_.c_str(),catname.c_str(),sqrts_),eaGraph);
  RooSpline1D *xs = xsSplines[proc_];
  TGraph *  xsGraph = new TGraph();
  TGraph *  brGraph = new TGraph();
  int point=0;
  for (float m =120; m<131; m=m+0.5){
    MH->setVal(m);
    xsGraph->SetPoint(point,m,xs->getVal());
    brGraph->SetPoint(point,m,brSpline->getVal());
    point++;
  }

  //more validation/debug plots!
  TCanvas *c = new TCanvas();
  TPaveText *pt2 = new TPaveText(.6,.85,.9,1.0,"NDC");
  pt2->AddText(Form("%s XS Spline",proc_.c_str()));
  xsGraph->Draw("ALP");
  pt2->Draw();
  c->SaveAs(Form("%s/%s_xs_spline.pdf",outDir_.c_str(),proc_.c_str()));
  
  TPaveText *pt1 = new TPaveText(.6,.85,.9,.8,"NDC");
  pt1->AddText(Form("BR Spline"));
  brGraph->Draw("ALP");
  pt1->Draw();
  c->SaveAs(Form("%s/br_spline.pdf",outDir_.c_str()));
  

	RooAbsReal *rateNuisTerm = getRateWithPhotonSyst(Form("rate_%s_%s_%dTeV",proc_.c_str(),catname.c_str(),sqrts_));
	if (!(xs && brSpline && eaSpline && rateNuisTerm && intLumi)){
  	std::cout << "[ERROR] some of the following are not set properly. exit." << std::endl;
    std::cout << "[ERROR] xs " << xs << ", brSpline " << brSpline << ", eaSpline " << eaSpline << ", rateNuisTerm " << rateNuisTerm << ", intLumi " << intLumi << std::endl;
  	if( verbosity_) std::cout << "[INFO] xs " << xs << ", brSpline " << brSpline << ", eaSpline " << eaSpline << ", rateNuisTerm " << rateNuisTerm << ", intLumi " << intLumi << std::endl;
  	exit(1);
	} else {
     if (verbosity_>1) std::cout << "[INFO] xs " << xs->getVal() << ", brSpline " << brSpline->getVal() << ", eaSpline " << eaSpline->getVal() << ", rateNuisTerm " << rateNuisTerm->getVal() << ", intLumi " << intLumi->getVal() << std::endl;
  }

	finalNorm = new RooFormulaVar(Form("%s_norm",finalPdf->GetName()),Form("%s_norm",finalPdf->GetName()),"@0*@1*@2*@3",RooArgList(*xs,*brSpline,*eaSpline,*rateNuisTerm));
        for (int m =120; m<131; m=m+5){
				  MH->setVal(m); 
          if(verbosity_ <1) std::cout << "[INFO] MH " << m <<  " -- br " << (brSpline->getVal()) << " - ea "  <<  (eaSpline->getVal()) << " intL= " << intLumi->getVal() << " xs " << xs->getVal() << "norm " << (brSpline->getVal())*(eaSpline->getVal())*(xs->getVal()) << "predicted events " <<  (brSpline->getVal())*(eaSpline->getVal())*(xs->getVal())*intLumi->getVal() <<  std::endl;
        }
	
  //
  // these are for plotting
  finalNormThisLum = new RooFormulaVar(Form("%s_normThisLumi",finalPdf->GetName()),Form("%s_normThisLumi",finalPdf->GetName()),"@0*@1*@2*@3*@4",RooArgList(*xs,*brSpline,*eaSpline,*rateNuisTerm,*intLumi));
	extendPdfRel = new RooExtendPdf(Form("extend%s",finalPdf->GetName()),Form("extend%s",finalPdf->GetName()),*finalPdf,*finalNorm);
  extendPdf = new RooExtendPdf(Form("extend%sThisLumi",finalPdf->GetName()),Form("extend%sThisLumi",finalPdf->GetName()),*finalPdf,*finalNormThisLum);
  // do secondary models
  if (doSecondaryModels){
    assert(secondaryModelVarsSet);
    // sm higgs as bkg
    RooSpline1D *eaSpline_SM = graphToSpline(Form("fea_%s_%s_%dTeV_SM",proc_.c_str(),catname.c_str(),sqrts_),eaGraph,MH_SM);
    RooSpline1D *xs_SM = xsSplines_SM[proc_];
    finalNorm_SM = new RooFormulaVar(Form("%s_norm",finalPdf_SM->GetName()),Form("%s_norm",finalPdf_SM->GetName()),"@0*@1*@2*@3",RooArgList(*xs_SM,*brSpline_SM,*eaSpline_SM,*rateNuisTerm));
    // second degen higgs
    RooSpline1D *eaSpline_2 = graphToSpline(Form("fea_%s_%s_%dTeV_2",proc_.c_str(),catname.c_str(),sqrts_),eaGraph,MH_2);
    RooSpline1D *xs_2 = xsSplines_2[proc_];
    finalNorm_2 = new RooFormulaVar(Form("%s_norm",finalPdf_2->GetName()),Form("%s_norm",finalPdf_2->GetName()),"@0*@1*@2*@3",RooArgList(*xs_2,*brSpline_2,*eaSpline_2,*rateNuisTerm));
    // natural width
    RooSpline1D *eaSpline_NW = graphToSpline(Form("fea_%s_%s_%dTeV_NW",proc_.c_str(),catname.c_str(),sqrts_),eaGraph,MH);
    RooSpline1D *xs_NW = xsSplines_NW[proc_];
    finalNorm_NW = new RooFormulaVar(Form("%s_norm",finalPdf_NW->GetName()),Form("%s_norm",finalPdf_NW->GetName()),"@0*@1*@2*@3",RooArgList(*xs_NW,*brSpline_NW,*eaSpline_NW,*rateNuisTerm));
  }
}

void FinalModelConstruction::save(RooWorkspace *work){
  work->import(*finalPdf,RecycleConflictNodes());
  work->import(*finalNorm,RecycleConflictNodes());
  work->import(*finalNormThisLum,RecycleConflictNodes());
  work->import(*extendPdf,RecycleConflictNodes());
  work->import(*extendPdfRel,RecycleConflictNodes());
  for (map<int,RooDataSet*>::iterator it=stdDatasets.begin(); it!=stdDatasets.end(); it++){
    work->import(*(it->second));
  }

  // do secondary models
	if (doSecondaryModels){
		work->import(*finalPdf_SM,RecycleConflictNodes());
		work->import(*finalPdf_2,RecycleConflictNodes());
		work->import(*finalPdf_NW,RecycleConflictNodes());
		work->import(*finalNorm_SM,RecycleConflictNodes());
		work->import(*finalNorm_2,RecycleConflictNodes());
		work->import(*finalNorm_NW,RecycleConflictNodes());
	}
}
