#include <iostream>
#include <sstream>
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

using namespace std;
using namespace RooFit;
using namespace boost;
namespace po = boost::program_options;

string filename_;
string datfilename_;
int mass_;
int convert_;
int draw_;
int intlumi_;
int print_;
int pseudodata_;
string procString_;
int ncats_;
float factor_;
bool recursive_=false;
string flashggCatsStr_;
vector<string> flashggCats_;
bool forceFracUnity_=false;
bool isFlashgg_;
bool verbose_;

void OptionParser(int argc, char *argv[]){
	po::options_description desc1("Allowed options");
	desc1.add_options()
		("help,h",                                                                                "Show help")
		("infilename,i", po::value<string>(&filename_),                                           "Input file name")
		("convert", po::value<int>(&convert_)->default_value(0),                                    "Convertto flashgg ws")
		("draw", po::value<int>(&draw_)->default_value(0),                                    "Draw some plots")
		("intlumi", po::value<int>(&intlumi_)->default_value(0),                                    "Draw some plots")
		("print", po::value<int>(&print_)->default_value(0),                                    "print contents of ws")
		("pseudodata", po::value<int>(&pseudodata_)->default_value(0),                                    "make pseudodata from inputfiles")
		("factor", po::value<float>(&factor_)->default_value(1.05),                                    "factor to increase FLASHgg workspace by")
		("procs,p", po::value<string>(&procString_)->default_value("ggh,vbf,wh,zh,tth"),          "Processes")
		("flashggCats,f", po::value<string>(&flashggCatsStr_)->default_value("DiPhotonUntaggedCategory_0,DiPhotonUntaggedCategory_1,DiPhotonUntaggedCategory_2,DiPhotonUntaggedCategory_3,DiPhotonUntaggedCategory_4,VBFTag_0,VBFTag_1,VBFTag_2"),       "Flashgg category names to consider")
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
int main(int argc, char *argv[]){

	OptionParser(argc,argv);

	TStopwatch sw;
	sw.Start();

	RooMsgService::instance().setGlobalKillBelow(RooFit::ERROR);
	RooMsgService::instance().setSilentMode(true);


	vector<string> procs;
	split(procs,procString_,boost::is_any_of(","));
	split(flashggCats_,flashggCatsStr_,boost::is_any_of(","));
	std::cout << "FLASHgg categories " << flashggCats_.size() << std::endl;
	for( int i =0 ; i<flashggCats_.size() ; i++){

		std::cout << "FLASHgg categories  " << flashggCats_[i] << std::endl;

	}
	vector<RooDataSet *> inData;
	vector<RooDataSet *> outData;
	vector<RooDataHist *> outHist;


	TFile *inFile = TFile::Open(filename_.c_str());
	RooWorkspace *inWS;
	RooRealVar *mass;
	RooRealVar *intLumiREAD;
	inWS = (RooWorkspace*)inFile->Get("cms_hgg_workspace");
	if (! inWS) inWS = (RooWorkspace*)inFile->Get("w");
	if (! inWS) inWS = (RooWorkspace*)inFile->Get("multipdf");
	if (! inWS) inWS = (RooWorkspace*)inFile->Get("wsig_8TeV");
	if (! inWS) inWS = (RooWorkspace*)inFile->Get("wsig_13TeV");
	if (! inWS) inWS = (RooWorkspace*)inFile->Get("tagsDumper/cms_hgg_13TeV");
	if (! inWS) inWS = (RooWorkspace*)inFile->Get("diphotonDumper/cms_hgg_13TeV");
	if (! inWS) {std::cout << "ERROR could not find ws " << std::endl;return 0;}
	std::cout << "[INFO] Workspace Open "<< inWS << std::endl;
	mass = (RooRealVar*)inWS->var("CMS_hgg_mass");
	intLumiREAD = (RooRealVar*)inWS->var("IntLumi");
	std::cout << "[INFO] Got mass var from ws"<<std::endl;
	//std::cout << "[INFO] Got intLumi var from ws, value "<< intLumiREAD->getVal()<<std::endl;

	RooWorkspace *outWS = new RooWorkspace();
	RooRealVar  newmass("CMS_hgg_mass","CMS_hgg_mass",100,180) ;
	RooRealVar  newweight("wCMS_hgg_mass","wCMS_hgg_mass",0,10) ;
	RooRealVar  sqrts("SqrtS","SqrtS",0,14) ;
	RooRealVar  intlumi("IntLumi","IntLumi",0,300000) ;
	sqrts.setVal(13);
	outWS->import(sqrts);
	inWS->import(sqrts);
	//outWS->import(intlumi);
	//inWS->Write("cms_hgg_workspace");
	
	if (intlumi_){
	intlumi.setVal(intlumi_);
	inWS->import(intlumi);
	RooRealVar *lumi = (RooRealVar*)inWS->var("IntLumi");
	if (lumi){

std::cout << "[INFO] Intlumi val "<< lumi->getVal() << std::endl;
TFile *outFile0 = TFile::Open(("withIntLumi.root"),"RECREATE");
				TDirectory *savdir = gDirectory;
				TDirectory *adir = savdir->mkdir("diphotonDumper");
				adir->cd();
       	inWS->Write("cms_hgg_13TeV");
	outFile0->Close();
	std::cout << "[INFO] saved file withIntLumi.root. exit "<< std::endl; 

	} else {
std::cout << "[INFO] no IntLui variable, exit." << std::endl;
return 0;
	}



	}

	if (print_){
		std::list<RooAbsData*> data =  (inWS->allData()) ;
		std::cout <<" [INFO] Reading WS dataset contents: "<< std::endl;
		for (std::list<RooAbsData*>::const_iterator iterator = data.begin(), end = data.end(); iterator != end; ++iterator )  {
			std::cout << "it " <<  **iterator  << std::endl;

		}
		std::cout <<" [INFO] Reading WS roorealvar contents: "<< std::endl;
		inWS->Print("V");

	}



	if (convert_ || draw_){
		std::list<RooAbsData*> data =  (inWS->allData()) ;int catNum =-1;
		for (std::list<RooAbsData*>::const_iterator iterator = data.begin(), end = data.end(); iterator != end; ++iterator )  {
			std::ostringstream title;
			title <<  (*iterator)->GetName();
			if(!( ( title.str().find( "data" ) ) < title.str().size()) ){ //FIXME temp solution only
				continue;
			}
			if(( ( title.str().find( "cat10" ) ) < title.str().size()) ){//FIXME temp solution only
				continue;
			}
			if(( ( title.str().find( "cat11" ) ) < title.str().size()) ){//FIXME temp solution only
				continue;
			}
			if(( ( title.str().find( "cat12" ) ) < title.str().size()) ){//FIXME temp solution only
				continue;
			}
			if(( ( title.str().find( "cat13" ) ) < title.str().size()) ){//FIXME temp solution only
				continue;
			}
			catNum++;
			//if (catNum == flashggCats_.size() ) break;
			RooDataSet *dataset = dynamic_cast<RooDataSet *>( *iterator);
			RooDataHist *datahist = dynamic_cast<RooDataHist *>( *iterator);
			if (datahist) outHist.push_back( (RooDataHist*) datahist->Clone());
			std::cout << "it " <<  **iterator << ", catnum "<<  catNum << std::endl;
			if (!datahist && catNum <8) {
				RooDataSet *newdataset = new RooDataSet(Form("data_mass_%s",(flashggCats_[catNum]).c_str()),"newdataset",RooArgSet(newmass,newweight));
				//	RooDataSet *newdataset = new RooDataSet(Form("newdataset"),"newdataset",RooArgSet(newmass,newweight));
				for (int i=0 ; i<dataset->numEntries(); i++){
					RooArgSet *argset=(RooArgSet *)dataset->get(i);
					double w = dataset->weight();
					double m=argset->getRealValue("CMS_hgg_mass");
					//double w=argset->getRealValue("weight");
					//	if( i %1000==0) std::cout << "entry " << i  <<" -- invariant_mass=" << m << " , weight "<< w << std::endl;
					newmass=m;
					if (m >122 && m <128){
						newweight=factor_;
						newdataset->add(RooArgSet(newmass,newweight));

						//		std::cout << "adding extra entry, mass " << m << std::endl;
					} else {
						newweight=1;
						newdataset->add(RooArgSet(newmass,newweight));
					}

				}
				RooDataSet *wdata = new RooDataSet(newdataset->GetName(),newdataset->GetTitle(),newdataset,*newdataset->get(),0,newweight.GetName());
				/*		for (int i=0 ; i<newdataset->numEntries(); i++){
							RooArgSet *argset=(RooArgSet *) newdataset->get(i);
							double w = newdataset->weight();
							double m=argset->getRealValue("CMS_hgg_mass");
				//double w=argset->getRealValue("weight");
				//	if( i %1000==0) std::cout << " NEW entry " << i  <<" -- invariant_mass=" << m << " , weight "<< w << std::endl;
				//	newmass=m;
				}*/
				if ( outData.size()==1){
					TCanvas *c1 = new TCanvas("c","c",500,500);
					RooPlot* mframe = newmass.frame() ;
					//newdataset->plotOn(mframe);
					wdata->plotOn(mframe);
					mframe->Draw();
					c1->SaveAs("outdatasettest.pdf");
				}

				//	if (dataset) outData.push_back( (RooDataSet*) dataset->Clone());
				//	if (datahist) outHist.push_back( (RooDataHist*) datahist->Clone());
				if (dataset) outData.push_back( (RooDataSet*) (wdata));
				if (dataset) inData.push_back( (RooDataSet*) dataset->Clone());
			}

		}
	}
	if (convert_){
	 TFile *outFile = TFile::Open("outWS.root","RECREATE");
		std::cout << "importing " << std::endl;
		for(unsigned int d =0 ; d<outData.size() ; d++){
			outWS->import(*(outData[d]));
			//		outWS->import(*(outData[d])->binnedClone(Form("roohist_%s",(outData[d]->GetName()))));
			std::cout << *(outData[d]) << std::endl;
		}
		//		for(unsigned int h =0 ; h<outHist.size() ; h++){
		//			outWS->import(*(outHist[h]));
		//			std::cout <<*(outHist[h]) << std::endl;
		//		}
	outWS->Write("cms_hgg_workspace");
	outFile->Close();

	}

	if(draw_){
		TCanvas *c1 = new TCanvas("c","c",500,500);
		RooPlot* mframe = newmass.frame() ;
		//	std::cout <<" plot denut, outdtaat1 entrie s " <<  outData[1]->numEntries()<< std::endl;
		//	std::cout <<" plot debug " <<  *(outData[1])<< std::endl;

		outData[1]->plotOn(mframe);
		mframe->Draw();
		c1->SaveAs("outdataset.pdf");
		RooPlot* mframe2 = mass->frame() ;
		inData[1]->plotOn(mframe2);
		mframe2->Draw();
		c1->SaveAs("indataset.pdf");
	}
}


