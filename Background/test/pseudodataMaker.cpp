#include <sstream>
#include <string>
#include <vector>
#include <map>
#include <utility>
#include <math.h>

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
#include "RooPolynomial.h"
#include "RooRandom.h"

#include "boost/program_options.hpp"
#include "boost/algorithm/string/split.hpp"
#include "boost/algorithm/string/classification.hpp"
#include "boost/algorithm/string/predicate.hpp"
#include "../interface/RooPowerLaw.h"
#include "../interface/RooPowerLawSum.h"
#include "RooGenericPdf.h"
#include "../interface/PdfModelBuilder.h"
#include "HiggsAnalysis/CombinedLimit/interface/RooMultiPdf.h"

using namespace std;
using namespace RooFit;
using namespace boost;
namespace po = boost::program_options;

string filenameStr_;
string yieldfileStr_;
string plotDir_;
vector<string> yieldfile_;
vector<string> filename_;
vector<string> filetype_;
vector<string> shortname_;
int mass_;
int pseudodata_;
int append_;
int draw_;
float intlumi_;
float intlumiOLD_;
float lumifactor_;
int print_;
float seed_;
string procString_;
int ncats_;
bool recursive_=false;
string flashggCatsStr_;
vector<string> flashggCats_;
bool forceFracUnity_=false;
bool isFlashgg_;
bool verbose_;
std::map < string, RooDataSet*> mymap;
std::map < string, RooDataSet*> mymapsig;
std::map < string, RooDataSet*> mymapbkg;

void OptionParser(int argc, char *argv[]){
	po::options_description desc1("Allowed options");
	desc1.add_options()
		("help,h",                                                                                "Show help")
		("infilename,i", po::value<string>(&filenameStr_),                                           "Input file name")
		("yieldfile,y", po::value<string>(&yieldfileStr_),                                           "Output yields")
		("draw", po::value<int>(&draw_)->default_value(0),                                    "Draw some plots")
		("intLumi", po::value<float>(&intlumi_)->default_value(0),                                    "Specify hwo much pseudodata to generate (in fb^{-1}")
		("print", po::value<int>(&print_)->default_value(0),                                    "print contents of ws")
		("append", po::value<int>(&pseudodata_)->default_value(0),                                    "make pseudodata from inputfiles")
		("seed", po::value<float>(&seed_)->default_value(0.),                                    "seed for pseudodata gandom number generator")
		("pseudodata", po::value<int>(&pseudodata_)->default_value(0),                                    "make pseudodata from inputfiles")
		("procs,p", po::value<string>(&procString_)->default_value("ggh,vbf,wh,zh,tth"),          "Processes")
		("plotdir", po::value<string>(&plotDir_)->default_value("pseudodataplots"),          "PseudoData plots")
		("flashggCats,f", po::value<string>(&flashggCatsStr_)->default_value("UntaggedTag_0,UntaggedTag_1,UntaggedTag_2,UntaggedTag_3,UntaggedTag_4,VBFTag_0,VBFTag_1,VBFTag_2,VHHadronicTag,VHLooseTag,VHTightTag,VHEtTag,TTHLeptonicTag,TTHHadronicTag"),       "Flashgg category names to consider")
		("verbose", po::value<bool>(&verbose_)->default_value(0),                                    "Extra messages")
		;

	po::options_description desc2("Options kept for backward compatibility");
	desc2.add_options()
		("ncats,n", po::value<int>(&ncats_)->default_value(9),																			"Number of cats (Set Automatically if using --isFlashgg 1)")
		;
	po::options_description desc("Allowed options");
	desc.add(desc1).add(desc2);

	po::variables_map vm;
	po::store(po::parse_command_line(argc,argv,desc),vm);
	po::notify(vm);
	if (vm.count("help")){ cout << desc << endl; exit(1);}
	if (vm.count("recursive")) recursive_=true;
	if (vm.count("forceFracUnity")) forceFracUnity_=true;
}


/////////------------> Begin Main function <--------------/////////
int main(int argc, char *argv[]){
	
  int seedOffset =0;
	vector<string> tags;
	vector<string> processes;
	vector<float> yields;
	vector<float> weights;

	float progress=0;
	OptionParser(argc,argv);

	TStopwatch sw;
	sw.Start();

	RooMsgService::instance().setGlobalKillBelow(RooFit::ERROR);
	RooMsgService::instance().setSilentMode(true);

	// Split strings
	vector<string> procs;
	split(procs,procString_,boost::is_any_of(","));
	split(flashggCats_,flashggCatsStr_,boost::is_any_of(","));

	// Flashgg Categories considered.
	if (verbose_){
	std::cout << "FLASHgg categories " << flashggCats_.size() << std::endl;
	for( int i =0 ; i<flashggCats_.size() ; i++){
		std::cout << "FLASHgg categories  " << flashggCats_[i] << std::endl;
	}
	}
	 system(Form("mkdir -p %s/",plotDir_.c_str()));
	 system(Form("mkdir -p %s/gaussians",plotDir_.c_str()));
	 system(Form("mkdir -p %s/berns",plotDir_.c_str()));
	// check input file and push back datasets
	ifstream infile;
	ofstream yieldsOut;
	infile.open(filenameStr_.c_str());
	yieldsOut.open(yieldfileStr_.c_str());
	if (infile.fail()) {
		std::cout << "[ERROR] Could not open " << filenameStr_ <<std::endl;
		exit(1);
	}
	// push back list of files from input
	while (infile.good()){
		string line;
		vector<string> words;
		getline(infile,line);
		if (line=="\n" || line.substr(0,1)=="#" || line==" " || line.empty()) continue;
		split(words,line,boost::is_any_of(","));
		if (verbose_) std::cout << "[INFO] type  " <<  words[0] << ", file " << words[1] << std::endl;
		filename_.push_back(words[1]);
		filetype_.push_back(words[0]);
		if (words.size() >2 ) shortname_.push_back(words[2]);
	}

	// new workspace 
	RooWorkspace *outWS = new RooWorkspace();
	RooRealVar  newmass("CMS_hgg_mass","CMS_hgg_mass",100,180) ;
	RooRealVar  newweight("wCMS_hgg_mass","wCMS_hgg_mass",0,10) ;
	RooRealVar  sqrts("SqrtS","SqrtS",0,14) ;
	RooRealVar  intlumi("IntLumi","IntLumi",0,300000) ;
	sqrts.setVal(13);
	intlumi.setVal(intlumi_*1000);
	outWS->import(sqrts);
	outWS->import(intlumi);

	// new file for our workspace
	TFile *outFile = TFile::Open((plotDir_+"/pseudoWS.root").c_str(),"RECREATE");

	// loop over input files
	for (unsigned int ifile =0; ifile < filename_.size() ; ifile++){
		std::cout << "[INFO] filename " << filename_[ifile] <<", type " << filetype_[ifile]<< std::endl;
		if( verbose_){
		std::cout << "map size " << mymap.size() <<" and contents :"  << std::endl;
		for ( std::map<string,RooDataSet*>::iterator imap=mymap.begin(); imap!=mymap.end(); ++imap ){
		std::cout << "[DEBUG] Map entry " << imap->first << ", " << imap->second << std::endl;
		}
		}
		

		
		//progress tracker
		progress = (float) (ifile+1)/filename_.size();
		//outData is the list of output datasets extarcted from this file.
		vector<RooDataSet *> outData;
		// open file for this iteration
		TFile *inFile = TFile::Open(filename_[ifile].c_str());
		RooWorkspace *inWS;
		RooRealVar *mass;
		// workspace will probably have one of these names. pick the first oen that fits
		inWS = (RooWorkspace*)inFile->Get("cms_hgg_workspace");
		if (! inWS) inWS = (RooWorkspace*)inFile->Get("multipdf");
		if (! inWS) inWS = (RooWorkspace*)inFile->Get("wsig_8TeV");
		if (! inWS) inWS = (RooWorkspace*)inFile->Get("wsig_13TeV");
		if (! inWS) inWS = (RooWorkspace*)inFile->Get("tagsDumper/cms_hgg_13TeV");
		if (! inWS) return 0; // if not, quit.

		if( verbose_) std::cout << "[INFO] Workspace Open "<< inWS << std::endl;
		mass = (RooRealVar*)inWS->var("CMS_hgg_mass");
		if (verbose_) std::cout << "[INFO] Got mass var from ws"<<std::endl;

		outFile->cd();

		//set intLumi
		if (intlumi_){
	//		RooRealVar *lumi = (RooRealVar*)inWS->var("IntLumi");
	//		if (lumi){
	   //		inWS->import(intlumi);
		//		TDirectory *savdir = gDirectory;
		//		TDirectory *adir = savdir->mkdir("tagsDumper");
		//		adir->cd();
       //	inWS->Write("cms_hgg_13TeV");
				std::cout << "[INFO] Intlumi val "<< intlumi.getVal() << " pb ^{-1}" <<  std::endl;
	RooRealVar *intLumiREAD;
	intLumiREAD = (RooRealVar*)inWS->var("IntLumi");
	intlumiOLD_ = intLumiREAD->getVal();
	lumifactor_= intlumi_*1000/intlumiOLD_;
				std::cout << "[INFO] OLD intlumi val " << intlumiOLD_ << " pb ^{-1}" <<  std::endl;
				std::cout << "[INFO] factor " << lumifactor_ <<  std::endl;
			//	return 0;
			} else {
				std::cout << "[INFO] no IntLumi variable, exit." << std::endl;
				return 0;
			}
		

		// This will just append the required datasets together, throwing no toys..
		if (append_){
			// fetch all data in this input WS
			std::list<RooAbsData*> data =  (inWS->allData()) ; 
			// and loop over the workspaces
			//std::cout << "[debug] loop over datasets from this file " << std::endl;
			for (std::list<RooAbsData*>::const_iterator iterator = data.begin(), end = data.end(); iterator != end; ++iterator )  {
				std::ostringstream title;
				std::string determinedCategory;
				bool found=0;
				RooDataSet *dataset = dynamic_cast<RooDataSet *>( *iterator);
				if (verbose_) std::cout << "[INFO] datdaset " << dataset << std::endl;
				if (dataset) {
					if (verbose_) std::cout << "[INFO] datdaset " << *dataset << std::endl;
					title <<  (dataset)->GetTitle();
					if (verbose_) std::cout << "[INFO] considering dataset " << title.str() << std::endl;
					if(( ( title.str().find( "sigma" ) ) < title.str().size()) ){//ignore systmatics datasets 
						continue;
					}
					for (unsigned int ifc =0; ifc<flashggCats_.size() ; ifc++){ //ifc = iFlashggCategoryi
						if (verbose_) std::cout << " [INFO] title.str() " << title.str() << std::endl;
						if(( ( title.str().find( flashggCats_[ifc]) ) < title.str().size()) ){//ignore systmatics datasets 
							determinedCategory=flashggCats_[ifc];
							found=1;
							break;
						}
					}
					if (found){ 
						//		std::cout << " determined tha this is category " << determinedCategory<< std::endl;
					} else {
						//		std::cout << "could not determine category" << std::endl;
						return 0;
					}
					RooDataSet *wdata = (RooDataSet*) dataset->reduce(RooArgSet(*mass),"1");
					wdata->SetName(Form("data_mass_%s",(determinedCategory).c_str()));
					//	std::cout << ">>[DEBUG] wdata " << *wdata << std::endl;
					outData.push_back( (RooDataSet*) (wdata));
				}

			}
			// now we have accessed the datasets and put them into the right format, we want to store them.

			if (ifile==0){ // first iteration, we want to create a new list of datasets to store in the otuput file 
				for(unsigned int d =0 ; d<outData.size() ; d++){
					//save into map
					mymap.insert(std::pair<string,RooDataSet*>(outData[d]->GetName(), outData[d]));
				}
			} else{ // in all other iterations, fin the corresponding dataset in map and fill that.
				int counter =0;
				std::list<RooAbsData*> dataOut =  (outWS->allData()) ;  // not needed?
				for(unsigned int d =0 ; d<outData.size() ; d++){
					RooDataSet* iter =  mymap[(outData[d])->GetName()]; // find dataset in map from name.
					if (iter){ // if it exists, append new data
						iter->append(*(outData[d]) );
						//	std::cout << "-> sum" <<*iter<<", " << 100*progress << std::endl;//" %\r";

					}	else { // if not, make new entry to map
						//	std::cout << std::endl << "appending " << outData[d]->GetName() <<  std::endl;
						mymap.insert(std::pair<string,RooDataSet*>(outData[d]->GetName(), outData[d]));

					}
				}
			}
		}



		// Instead, generate pseudodata by fitting the dataset in each case and then throwing toys to mimic the number of weights.
		if (pseudodata_){
			bool isSig = (filetype_[ifile]=="sig");
			// fetch all data in this input WS
			std::list<RooAbsData*> data =  (inWS->allData()) ; 
			// and loop over the workspaces
			for (std::list<RooAbsData*>::const_iterator iterator = data.begin(), end = data.end(); iterator != end; ++iterator )  {
				std::ostringstream title;
				std::string determinedCategory;
				bool found=0;
				RooDataSet *dataset = dynamic_cast<RooDataSet *>( *iterator);
				if (dataset) {
					title <<  (dataset)->GetTitle();
					if(( ( title.str().find( "sigma" ) ) < title.str().size()) ){//ignore systmatics datasets 
						continue;
					}
					for (unsigned int ifc =0; ifc<flashggCats_.size() ; ifc++){ //ifc = iFlashggCategoryi

					//	std::cout << " [DEBUG] title.str() " << title.str() << std::endl;
						if(( ( title.str().find( flashggCats_[ifc]) ) < title.str().size()) ){//ignore systmatics datasets 
							determinedCategory=flashggCats_[ifc];
							found=1;
							break;
						}
					}
					if (found){ 
					} else {
						if (verbose_) std::cout << "[WARNING] could not determine category of "<<  title.str() << std::endl;
					//	return 0;
						continue;
					}
					RooDataSet *wdata = (RooDataSet*) dataset->reduce(RooArgSet(*mass),"1");
					wdata->SetName(Form("data_mass_%s",(determinedCategory).c_str()));
					outData.push_back( (RooDataSet*) (wdata));
				}
			}
			for (int i =0 ; i < outData.size() ; i++){
				RooDataSet *dataPlot = outData[i];
				TCanvas *c1 = new TCanvas("c","c",500,500);
				RooPlot* mframe = newmass.frame() ;
				int sumEntries = (int) round(dataPlot->sumEntries()*lumifactor_);
				float sumWeights =  dataPlot->sumEntries()*lumifactor_;
			//	if (shortname_.size() >0) yieldsOut << shortname_[i] << " " << dataPlot->GetName() << " " << sumEntries << " " << dataPlot->sumEntries() << std::endl;
				dataPlot->plotOn(mframe);

				PdfModelBuilder pdfsModel;
				int order =3;
				pdfsModel.setObsVar(&newmass);

				RooRealVar a1("a1","a1",125,123,126) ;
				RooRealVar b1("b1","b1",125,123,126) ;
				RooRealVar d1("c1","c1",125,123,126) ;
				RooRealVar a2("a2","a2",0,0.,10) ; 
				RooRealVar b2("b2","b2",0,0.,10) ; 
				RooRealVar d2("c2","c2",0,0.,10) ; 
				RooAbsPdf *p2 = pdfsModel.getBernstein(Form("bern%d",order),order);
				RooGaussian* gaussA = new RooGaussian("gaussa","gaussian PDF",newmass,a1,a2) ; 
				RooGaussian* gaussB = new RooGaussian("gaussb","gaussian PDF",newmass,b1,b2) ; 
				RooGaussian* gaussC = new RooGaussian("gaussc","gaussian PDF",newmass,d1,d2) ;
				RooRealVar sig1frac("sig1frac","fraction of component 1 in signal",0.8,0.,1.) ;
				RooRealVar sig2frac("sig1frac","fraction of component 2 in signal",0.8,0.,1.) ;
				RooAddPdf* gauss0 = new RooAddPdf("gaus0","gaus0",RooArgList(*gaussA,*gaussB),sig1frac);
				RooAddPdf* gauss = new RooAddPdf("gaus","gaus",RooArgList(*gauss0,*gaussC),sig2frac);
				//	std::cout << "try bernstein order 3 " << p2 << std::endl;
				//	std::cout <<" try also gaussian " << gauss << std::endl;


				RooDataSet* dataFit;
				//if (gausnll < bernsnll)
				RooRandom::randomGenerator()->SetSeed(seed_+100*seedOffset);
        seedOffset++;
        std::cout << "[INFO] RANDOM NUMBER SEED FOR " << dataPlot->GetName() << " IS " << RooRandom::randomGenerator()->GetSeed() << std::endl;
				if (isSig) {
				RooFitResult *fitTestGaus = gauss->fitTo(*dataPlot,RooFit::Save(1),RooFit::Verbose(0),RooFit::SumW2Error(kTRUE), RooFit::Minimizer("Minuit2","minimize")); //FIXME
				float gausnll = fitTestGaus->minNll();
					dataFit = gauss->generate(newmass,sumEntries)  ; //intLumi is in pb^-1. Use directly as mustiplicative factor since default is for 1 pb^-1
					gauss->plotOn(mframe) ;
					std::cout << " [INFO] sig - gaussian simgma" << a2.getVal() << ", gaussian mean " << a1.getVal() <<  ", nEvents in +/-1 sig " << dataFit->sumEntries() << std::endl;
				if (shortname_.size()>0) processes.push_back(shortname_[ifile]);
				else processes.push_back(filename_[ifile]);
				tags.push_back(dataPlot->GetName());
				yields.push_back(dataFit->sumEntries());
				weights.push_back(sumWeights);
				} else {
				RooFitResult *fitTest = p2->fitTo(*dataPlot,RooFit::Save(1),RooFit::Verbose(0),RooFit::SumW2Error(kTRUE), RooFit::Minimizer("Minuit2","minimize")); //FIXME
				float bernsnll = fitTest->minNll();
					dataFit = p2->generate(newmass,sumEntries)  ;
					p2->plotOn(mframe) ;
				if (shortname_.size()>0) processes.push_back(shortname_[ifile]);
				else processes.push_back(filename_[ifile]);
				tags.push_back(dataPlot->GetName());
				yields.push_back(dataFit->sumEntries());
				weights.push_back(sumWeights);
				}
				dataFit->plotOn(mframe,LineColor(kRed), FillColor(kRed), MarkerColor(kRed));
				dataFit->SetName(outData[i]->GetName());

				mframe->Draw();
				std::ostringstream name;
				if (isSig) {	
				name << plotDir_<<"/gaussians/testGaus"<<outData[i]->GetName()<<"_file"<<ifile<<".pdf";
				}
				else {
				name << plotDir_<<"/berns/testBern"<<outData[i]->GetName()<<"_file"<<ifile<<".pdf";
				}
					c1->SaveAs((name).str().c_str());


				//	if (ifile==0){ // first iteration, we want to create a new list of datasets to store in the otuput file 
				//		mymap.insert(std::pair<string,RooDataSet*>(outData[i]->GetName(), dataFit));
				/*			if (isSig){
								std::cout << "[INFO] creating sig dataset " << *dataFit << std::endl;
								mymapsig.insert(std::pair<string,RooDataSet*>(outData[i]->GetName(), dataFit));
								} else {
								std::cout << "[INFO] creating bkg dataset " << *dataFit << std::endl;
								mymapbkg.insert(std::pair<string,RooDataSet*>(outData[i]->GetName(), dataFit));
								}*/

				//		} else{ // in all other iterations, fin the corresponding dataset in map and fill that.*/
				RooDataSet* iter; 
				std::map<string,RooDataSet*>::iterator iter0 =  mymap.find((outData[i]->GetName())); // find dataset in map from name.
				if (iter0 == mymap.end()) {iter = 0; } else {iter = iter0->second;}

				RooDataSet* itersig;
				std::map<string,RooDataSet*>::iterator itersig0 =  mymapsig.find((outData[i]->GetName())); // find dataset in map from name.
				if (itersig0 == mymapsig.end()) {itersig = 0; } else {itersig = itersig0->second;}

				RooDataSet* iterbkg; 
				std::map<string,RooDataSet*>::iterator iterbkg0	=  mymapbkg.find((outData[i]->GetName())); // find dataset in map from name.
				if (iterbkg0 == mymapbkg.end()) {iterbkg = 0; } else {iterbkg = iterbkg0->second;}
			 	if (verbose_) std::cout << "[INFO] map size " << mymap.size() << ", iter " << iter << " (outData[i])->GetName() " << (outData[i])->GetName()<< std::endl;

				if (iter){ // if it exists, append new data
					iter->append(*dataFit);
				}	else { // if not, make new entry to map
					//			std::cout << std::endl << "appending " << outData[i]->GetName() <<  std::endl;
					mymap.insert(std::pair<string,RooDataSet*>(outData[i]->GetName(), dataFit));
					for ( std::map<string,RooDataSet*>::iterator imap=mymap.begin(); imap!=mymap.end(); ++imap ){
					if (verbose_)	std::cout << "[INFO] Map entry " << imap->first << ", " << imap->second << std::endl;
					}
					if (verbose_)std::cout << "[INFO] creating full dataset " << *dataFit << std::endl;
				}
				if(isSig){
					if (itersig){ // if it exists, append new data
						itersig->append(*dataFit);
					}	else { // if not, make new entry to map
						mymapsig.insert(std::pair<string,RooDataSet*>(outData[i]->GetName(), (RooDataSet*) dataFit->Clone()));
					}
				} else{
					if (iterbkg){ // if it exists, append new data
						iterbkg->append(*dataFit);
					}	else { // if not, make new entry to map
						mymapbkg.insert(std::pair<string,RooDataSet*>(outData[i]->GetName(), (RooDataSet*) dataFit->Clone()));
					}
				}

				//		}
			}
		}
	}

	// now fill and write
	outFile->cd();
	int counter =0;
	if (verbose_){
	std::cout << "[INFO] Total map size " << mymap.size() <<" and contents :"  << std::endl;
	for ( std::map<string,RooDataSet*>::iterator imap=mymap.begin(); imap!=mymap.end(); ++imap ){
		std::cout << "[INFO] Map entry " << imap->first << ", " << *(imap->second) << std::endl;
	}
	std::cout << "[INFO] mapsig size " << mymapsig.size() <<" and contents :"  << std::endl;
	for ( std::map<string,RooDataSet*>::iterator imap=mymapsig.begin(); imap!=mymapsig.end(); ++imap ){
		std::cout << "[INFO] Mapsig entry " << imap->first << ", " << *(imap->second) << std::endl;
	}
	std::cout << "[INFO] mapbkg size " << mymapbkg.size() <<" and contents :"  << std::endl;
	for ( std::map<string,RooDataSet*>::iterator imap=mymapbkg.begin(); imap!=mymapbkg.end(); ++imap ){
		std::cout << "[INFO] Mapbkg entry " << imap->first << ", " << *(imap->second) << std::endl;
	}
	}
	std::cout << "[INFO] write to file " << std::endl;
	for(unsigned int d =0 ; d<flashggCats_.size() ; d++){
		RooDataSet* iter =  mymap[Form("data_mass_%s",(flashggCats_[d]).c_str())]; // find dataset in map from name.
		RooDataSet* itersig =  mymapsig[Form("data_mass_%s",(flashggCats_[d]).c_str())]; // find dataset in map from name.
		RooDataSet* iterbkg =  mymapbkg[Form("data_mass_%s",(flashggCats_[d]).c_str())]; // find dataset in map from name.
		if (iter) {
			outWS->import(*iter);

			TCanvas *c1 = new TCanvas("c","c",500,500);
			RooPlot* mframe = newmass.frame() ;
			iter->plotOn(mframe);
			if (iterbkg) {
				iterbkg->plotOn(mframe,LineColor(kBlue),FillColor(kBlue), MarkerColor(kBlue));
			}
			if (itersig) {
				itersig->plotOn(mframe,LineColor(kRed),FillColor(kRed), MarkerColor(kRed));
			}
			mframe->Draw();
			std::ostringstream name;
			std::ostringstream namepng;
			name << plotDir_<< "/test"<<(flashggCats_[d])<<".pdf";
			namepng << plotDir_ << "/test"<<(flashggCats_[d])<<".png";
			c1->SaveAs((name).str().c_str());
			c1->SaveAs((namepng).str().c_str());
			counter++;
			//	std::cout << "debug importing " << *iter <<" into WS"<< std::endl;
		} else {
			RooDataSet* dummy = new RooDataSet (Form("data_mass_%s",(flashggCats_[d]).c_str()),Form("data_mass_%s",(flashggCats_[d]).c_str()),RooArgSet(newmass));
			outWS->import( *dummy);
		}
	}

	std::list<RooAbsData*> data =  (outWS->allData()) ; 
	for (std::list<RooAbsData*>::const_iterator iterator = data.begin(), end = data.end(); iterator != end; ++iterator )  {
		std::cout << "[INFO] final ws contents " << **iterator << std::endl;
	}

	outWS->Write("cms_hgg_workspace");
	std::cout << endl;
	outFile->Close();
		
	yieldsOut<< "PROCESS/SAMPLE " << "	"<< "TAG" << "	" << "YIELDS" << " " << "WEIGHTS" << std::endl;
	std::cerr << "PROCESS/SAMPLE " << "	"<< "TAG" << "	" << "YIELDS" << std::endl;
	std::cout << "PROCESS/SAMPLE " << "	"<< "TAG" << "	" << "YIELDS" << std::endl;
	for(int i =0; i < processes.size(); i++){

	std::cerr <<"YIELDS " <<  processes[i] << "	"<< tags[i] << "	" << yields[i] <<  " (" << weights[i] <<  ")" << std::endl;
  yieldsOut <<"YIELDS " <<  processes[i] << "	"<< tags[i] << "	" << yields[i] <<  " (" << weights[i] <<  ")" << std::endl;
	std::cout <<"YIELDS " <<  processes[i] << "	"<< tags[i] << "	" << yields[i] << std::endl;
	}


}

