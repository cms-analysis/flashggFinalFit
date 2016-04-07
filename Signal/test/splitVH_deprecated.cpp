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
int verbose_;

void OptionParser(int argc, char *argv[]){
	po::options_description desc1("Allowed options");
	desc1.add_options()
		("help,h",                                                                                "Show help")
		("infilename,i", po::value<string>(&infilenamesStr_),                                           "Input file name")
		("outdir,o", po::value<string>(&outdir_),                                           "output dir")
		("verbose,v", po::value<string>(&outdir_),                                           "output dir")
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
    const char * env = gSystem->Getenv("CMSSW_BASE") ; 
      std::string globeRt = env;
      TPython::Exec(Form("buildSMHiggsSignalXSBR = imp.load_source('*', '%s/src/flashggFinalFit/Signal/python/buildSMHiggsSignalXSBR.py')",globeRt.c_str()));
      TPython::Eval(Form("buildSMHiggsSignalXSBR.Init%dTeV()", 13));
   for (unsigned int i =0 ; i<infilenames_.size() ; i++){
	    int mH  =(int) TPython::Eval(Form("int(re.search('_M(.+?)_','%s').group(1))",infilenames_[i].c_str())); 
	   double WH_XS  =  (double)TPython::Eval(Form("buildSMHiggsSignalXSBR.getXS(%d,'%s')",mH,"WH"));
	   double ZH_XS  =  (double)TPython::Eval(Form("buildSMHiggsSignalXSBR.getXS(%d,'%s')",mH,"ZH"));
     float tot_XS = WH_XS + ZH_XS;
     float wFrac=  WH_XS /tot_XS ;
     float zFrac=  ZH_XS /tot_XS ;
      std::cout << "mass "<< mH << " wh fraction "<< WH_XS /tot_XS << ", zh fraction "<< ZH_XS /tot_XS <<std::endl; 
     TFile *infile =  TFile::Open(infilenames_[i].c_str());
	   string outname  =(string) TPython::Eval(Form("'%s'.split(\"/\")[-1].replace(\"VH\",\"WH_VH\")",infilenames_[i].c_str())); 
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
	            string zhname  =(string) TPython::Eval(Form("'%s'.replace(\"wzh\",\"zh\")",dataset->GetName())); 
	            string whname  =(string) TPython::Eval(Form("'%s'.replace(\"wzh\",\"wh\")",dataset->GetName())); 
              RooDataSet *datasetZH = (RooDataSet*) dataset->emptyClone(zhname.c_str(),zhname.c_str());
              RooDataSet *datasetWH = (RooDataSet*) dataset->emptyClone(whname.c_str(),whname.c_str());
                TRandom3 r;
                r.Rndm();
                double x[dataset->numEntries()];
                r.RndmArray(dataset->numEntries(),x);
                for (int j =0; j < dataset->numEntries() ; j++){
                    
                    if( x[j] < wFrac){
                    dataset->get(j);
                    datasetWH->add(*(dataset->get(j)),dataset->weight());
                    } else{
                    dataset->get(j);
                    datasetZH->add(*(dataset->get(j)),dataset->weight());
                    }
                }
              float w =datasetWH->sumEntries();
              float z =datasetZH->sumEntries();
           if(verbose_){
              std::cout << "Original dataset " << *dataset <<std::endl;
              std::cout << "WH       dataset " << *datasetWH <<std::endl;
              std::cout << "ZH       dataset " << *datasetZH <<std::endl;
              std::cout << "********************************************" <<std::endl;
              std::cout << "WH fraction (obs) : WH " << w/(w+z) <<",   ZH "<< z/(w+z) << std::endl;
              std::cout << "WH fraction (exp) : WH " << wFrac <<",   ZH "<< zFrac << std::endl;
              std::cout << "********************************************" <<std::endl;
              std::cout << "" <<std::endl;
              std::cout << "" <<std::endl;
              std::cout << "" <<std::endl;
              std::cout << "********************************************" <<std::endl;
              }
               outWS->import(*datasetWH);
               outWS->import(*datasetZH);
                }
             RooDataHist *datahist = dynamic_cast<RooDataHist *>( *iterator );

              if (datahist) {
	            string zhname  =(string) TPython::Eval(Form("'%s'.replace(\"wzh\",\"zh\")",datahist->GetName())); 
	            string whname  =(string) TPython::Eval(Form("'%s'.replace(\"wzh\",\"wh\")",datahist->GetName())); 
              RooDataHist *datahistZH = (RooDataHist*) datahist->emptyClone(zhname.c_str(),zhname.c_str());
              RooDataHist *datahistWH = (RooDataHist*) datahist->emptyClone(whname.c_str(),whname.c_str());
                TRandom3 r;
                r.Rndm();
                double x[datahist->numEntries()];
                r.RndmArray(datahist->numEntries(),x);
                for (int j =0; j < datahist->numEntries() ; j++){
                    
                    datahistWH->add(*(datahist->get(j)),datahist->weight()*wFrac);
                    datahistZH->add(*(datahist->get(j)),datahist->weight()*zFrac);
                }
              float w =datahistWH->sumEntries();
              float z =datahistZH->sumEntries();
           if(verbose_){
              std::cout << "Original datahist " << *datahist <<std::endl;
              std::cout << "WH       datahist " << *datahistWH <<std::endl;
              std::cout << "ZH       datahist " << *datahistZH <<std::endl;
              std::cout << "********************************************" <<std::endl;
              std::cout << "WH fraction (obs) : WH " << w/(w+z) <<",   ZH "<< z/(w+z) << std::endl;
              std::cout << "WH fraction (exp) : WH " << wFrac <<",   ZH "<< zFrac << std::endl;
              std::cout << "********************************************" <<std::endl;
              std::cout << "" <<std::endl;
              std::cout << "" <<std::endl;
              std::cout << "" <<std::endl;
              std::cout << "********************************************" <<std::endl;
              }
               outWS->import(*datahistWH);
               outWS->import(*datahistZH);
                }
                  }
   saveDir->cd();
   outWS->Write();
   outfile->Close();
   infile->Close();
   }
}
