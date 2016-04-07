#include <iostream>
#include <string>
#include <map>
#include <vector>
#include <TRandom3.h>

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
#include "TSystem.h"
#include "TPython.h"
#include "TPython.h"

#include "boost/program_options.hpp"
#include "boost/algorithm/string/split.hpp"
#include "boost/algorithm/string/classification.hpp"
#include "boost/algorithm/string/predicate.hpp"

#include "../interface/WSTFileWrapper.h"

using namespace std;
using namespace RooFit;
using namespace boost;
namespace po = boost::program_options;

string infilenamesStr_;
vector<string> infilenames_;
string outdir_="data";
int verbose_=0.1;
float fraction_;

void OptionParser(int argc, char *argv[]){
	po::options_description desc1("Allowed options");
	desc1.add_options()
		("help,h",                                                                                "Show help")
		("infilename,i", po::value<string>(&infilenamesStr_),                                           "Input file name")
		("outdir,o", po::value<string>(&outdir_),                                           "output dir")
		("verbose,v", po::value<int>(&verbose_),                                           "more output text dir")
		("fraction,f", po::value<float>(&fraction_),                                           "how much smaller do you want your files? default 0.1")
    ;
	po::options_description desc("Allowed options");
	desc.add(desc1);

	po::variables_map vm;
	po::store(po::parse_command_line(argc,argv,desc),vm);
	po::notify(vm);
	if (vm.count("help")){ cout << desc << endl; exit(1);}
	if (vm.count("verbose")){verbose_=1;}
}

int main(int argc, char *argv[]){

	OptionParser(argc,argv);
	

	RooMsgService::instance().setGlobalKillBelow(RooFit::ERROR);
	RooMsgService::instance().setSilentMode(true);


  
	system(Form("mkdir -p %s",outdir_.c_str()));

	vector<string> procs;
	split(infilenames_,infilenamesStr_,boost::is_any_of(","));
  
   TPython::Exec("import os,imp,re");
   for (unsigned int i =0 ; i<infilenames_.size() ; i++){
     TFile *infile =  TFile::Open(infilenames_[i].c_str());
	   string outname  =(string) TPython::Eval(Form("'%s'.split(\"/\")[-1].replace('root','_reduced.root')",infilenames_[i].c_str())); 
     TFile *outfile = TFile::Open(outname.c_str(),"RECREATE") ;
    TDirectory* saveDir = outfile->mkdir("tagsDumper");
    saveDir->cd();

    RooWorkspace *inWS = (RooWorkspace*) infile->Get("tagsDumper/cms_hgg_13TeV");
    RooRealVar *intLumi = (RooRealVar*)inWS->var("IntLumi");
    RooWorkspace *outWS = new RooWorkspace("cms_hgg_13TeV");
    outWS->import(*intLumi);
    std::list<RooAbsData*> data =  (inWS->allData()) ;
    std::cout <<" [INFO] Reading WS dataset contents: "<< std::endl;
        for (std::list<RooAbsData*>::const_iterator iterator = data.begin(), end = data.end(); iterator != end; ++iterator )  {
              RooDataSet *dataset = dynamic_cast<RooDataSet *>( *iterator );
              if (dataset) {
              RooDataSet *datasetReduced = (RooDataSet*) dataset->emptyClone(dataset->GetName(),dataset->GetName());
                TRandom3 r;
                r.Rndm();
                double x[dataset->numEntries()];
                r.RndmArray(dataset->numEntries(),x);
                int desiredEntries = floor(0.5+ dataset->numEntries()*fraction_);
                int modFraction = floor(0.5+ 1/fraction_);
                int finalEventCount=0;
                for (int j =0; j < dataset->numEntries() ; j++){
                    if( j%modFraction==0){
                      finalEventCount++;
                    }
                 }
                float average_weight= dataset->sumEntries()/finalEventCount;
                for (int j =0; j < dataset->numEntries() ; j++){
                    if( j%modFraction==0){
                    dataset->get(j);
                    datasetReduced->add(*(dataset->get(j)),average_weight);
                    }
                }
              float entriesIN =dataset->sumEntries();
              float entriesOUT =datasetReduced->sumEntries();
           if(verbose_){
              std::cout << "Original dataset " << *dataset <<std::endl;
              std::cout << "Reduced       dataset " << *datasetReduced <<std::endl;
              std::cout << "********************************************" <<std::endl;
              std::cout << "fraction (obs) : " << entriesOUT/entriesIN << std::endl;
              std::cout << "fraction (exp) : " << fraction_ << std::endl;
              std::cout << "********************************************" <<std::endl;
              std::cout << "" <<std::endl;
              std::cout << "" <<std::endl;
              std::cout << "" <<std::endl;
              std::cout << "********************************************" <<std::endl;
              }
               outWS->import(*datasetReduced);
                }
                
             RooDataHist *datahist = dynamic_cast<RooDataHist *>( *iterator );

              if (datahist) {
              RooDataHist *datahistOUT = (RooDataHist*) datahist->emptyClone(datahist->GetName(),datahist->GetName());
                TRandom3 r;
                r.Rndm();
                for (int j =0; j < datahist->numEntries() ; j++){
                    
                    datahistOUT->add(*(datahist->get(j)),datahist->weight());
                }
              float w =datahistOUT->sumEntries();
              float z =datahist->sumEntries();
           if(verbose_){
              std::cout << "Original datahist " << *datahist <<std::endl;
              std::cout << "Reduced  datahist " << *datahistOUT<<std::endl;
              std::cout << "********************************************" <<std::endl;
              std::cout << "WH fraction (obs) : " << w/(z) <<std::endl;
              std::cout << "WH fraction (exp) : " << fraction_ << std::endl;
              std::cout << "********************************************" <<std::endl;
              std::cout << "" <<std::endl;
              std::cout << "" <<std::endl;
              std::cout << "" <<std::endl;
              std::cout << "********************************************" <<std::endl;
              }
               outWS->import(*datahistOUT);
                }
                  }
   saveDir->cd();
   outWS->Write();
   outfile->Close();
   infile->Close();
   }
}
