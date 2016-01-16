#include "TCanvas.h"
#include "TGraph.h"

#include "RooAddition.h"
#include "RooAddPdf.h"
#include "RooDataSet.h"
#include "RooExtendPdf.h"
#include "RooArgList.h"
#include "RooRealVar.h"
#include "RooPlot.h"
#include "HiggsAnalysis/CombinedLimit/interface/RooSpline1D.h"

#include "../interface/Packager.h"

#include <algorithm>

using namespace std;
using namespace RooFit;

Packager::Packager(RooWorkspace *ws, vector<string> procs, int nCats, int mhLow, int mhHigh, vector<int> skipMasses, int sqrts, bool skipPlots, string outDir, 
		   RooWorkspace *wsMerge, const vector<int>& cats, const vector<string>& flashggCats ):
  outWS(ws),
  mergeWS(wsMerge),
  procs_(procs),
  nCats_(nCats),
  cats_(cats),
  flashggCats_(flashggCats),
  mhLow_(mhLow),
  mhHigh_(mhHigh),
	skipPlots_(skipPlots),
  outDir_(outDir),
  sqrts_(sqrts),
  skipMasses_(skipMasses)
{
	normalization = new Normalization_8TeV();
	normalization->Init(sqrts_);
}

Packager::~Packager(){}

bool Packager::skipMass(int mh){
	for (vector<int>::iterator it=skipMasses_.begin(); it!=skipMasses_.end(); it++) {
		if (*it==mh) return true;
	}
	return false;
}

void Packager::packageOutput(){

  vector<string> expectedObjectsNotFound;

	// sum datasets first
	for (int mh=mhLow_; mh<=mhHigh_; mh+=5){
		if (skipMass(mh)) continue;
		RooDataSet *allDataThisMass = 0;
		for (int cat=0; cat<nCats_; cat++) {
			string catname;
      std::cout << "DEBUG Packager::packageOutput() A" << std::endl;
			if (sqrts_==8 || sqrts_==7) catname=Form("cat%d",cat);
			if (sqrts_ ==13) catname = Form("%s",flashggCats_[cat].c_str());
      std::cout << "INFO catname " << catname<< std::endl;
			RooDataSet *allDataThisCat = NULL;
			bool merge = mergeWS != 0 && ( find(cats_.begin(),cats_.end(),cat) == cats_.end() );
			for (vector<string>::iterator proc=procs_.begin(); proc!=procs_.end(); proc++){
				RooDataSet *tempData = 0;
      std::cout << "DEBUG Packager::packageOutput() b" << std::endl;
				if( merge ) { 
      std::cout << "DEBUG Packager::packageOutput() c" << std::endl;
					tempData = (RooDataSet*)mergeWS->data(Form("sig_%s_mass_m%d_%s",proc->c_str(),mh,catname.c_str()));
					 //outWS->import(*tempData); //FIXME
				} else {
      std::cout << "DEBUG Packager::packageOutput() d" << std::endl;
					tempData = (RooDataSet*)outWS->data(Form("sig_%s_mass_m%d_%s",proc->c_str(),mh,catname.c_str()));
      std::cout << "DEBUG Packager::packageOutput() d.2" << std::endl;
				}
				if (!tempData) {
      std::cout << "DEBUG Packager::packageOutput() e" << std::endl;
					cerr << "[WARNING] -- dataset: " << Form("sig_%s_mass_m%d_%s",proc->c_str(),mh,catname.c_str()) << " not found. It will be skipped" << endl;
					expectedObjectsNotFound.push_back(Form("sig_%s_mass_m%d_%s",proc->c_str(),mh,catname.c_str()));
					continue;
				}
      std::cout << "DEBUG Packager::packageOutput() f.0 "<< std::endl;
      bool split_=1;
         if (!split_){
				if ( cat==0 && proc==procs_.begin()) allDataThisMass = (RooDataSet*)tempData->Clone(Form("sig_mass_m%d_AllCats",mh));
				else allDataThisMass->append(*tempData);
        }
      std::cout << "DEBUG Packager::packageOutput() f.1 "<< std::endl;
				//if (proc==procs_.begin()) allDataThisCat = (RooDataSet*)tempData->Clone(Form("sig_mass_m%d_%s",mh,catname.c_str()));
				if (!allDataThisCat) allDataThisCat = (RooDataSet*)tempData->Clone(Form("sig_mass_m%d_%s",mh,catname.c_str()));
				else allDataThisCat->append(*tempData);
      std::cout << "DEBUG Packager::packageOutput() f.2 "<< std::endl;
			}
			if (!allDataThisCat) {
      std::cout << "DEBUG Packager::packageOutput() g" << std::endl;
				cerr << "[WARNING] -- allData for cat " << catname.c_str() << " is NULL. Probably because the relevant datasets couldn't be found. Skipping.. " << endl;
				continue;
			}
      std::cout << "DEBUG Packager::packageOutput() h" << std::endl;
			outWS->import(*allDataThisCat);
      std::cout << "DEBUG Packager::packageOutput() i" << std::endl;
		}
		if (!allDataThisMass) {
      std::cout << "DEBUG Packager::packageOutput() j" << std::endl;
			cerr << "[WARNING] -- allData for mass " << mh << " is NULL. Probably because the relevant datasets couldn't be found. Skipping.. " << endl;
			continue;
		}
      std::cout << "DEBUG Packager::packageOutput() k" << std::endl;
		outWS->import(*allDataThisMass);
      std::cout << "DEBUG Packager::packageOutput() l" << std::endl;
	}

	// now create pdf sums (these don't the relative amounts as just used for plotting so can use ThisLum versions)
	RooArgList *sumPdfs = new RooArgList();
	RooArgList *runningNormSum = new RooArgList();
      std::cout << "DEBUG Packager::packageOutput() m" << std::endl;
	for (int cat=0; cat<nCats_; cat++){
      std::cout << "DEBUG Packager::packageOutput() n" << std::endl;
		string catname;
		if (sqrts_ == 13) catname=Form("%s",flashggCats_[cat].c_str());
		else if (sqrts_==7 || sqrts_==8) catname=Form("cat%d",cat);
		bool merge = mergeWS != 0 && ( find(cats_.begin(),cats_.end(),cat) == cats_.end() );
		RooWorkspace * inWS = ( merge ? mergeWS : outWS );
		RooArgList *sumPdfsThisCat = new RooArgList();
		for (vector<string>::iterator proc=procs_.begin(); proc!=procs_.end(); proc++){

      std::cout << "DEBUG Packager::packageOutput() o" << std::endl;
			// sum eA
			RooSpline1D *norm = (RooSpline1D*)inWS->function(Form("hggpdfsmrel_%dTeV_%s_%s_norm",sqrts_,proc->c_str(),catname.c_str()));
			if (!norm) {
				cerr << "[WARNING] -- ea: " << Form("hggpdfsmrel_%dTeV_%s_%s_norm",sqrts_,proc->c_str(),catname.c_str()) << " not found. It will be skipped" << endl;
			}
			else {
				runningNormSum->add(*norm);
			}

      std::cout << "DEBUG Packager::packageOutput() p" << std::endl;
			// sum pdf
			RooExtendPdf *tempPdf = (RooExtendPdf*)inWS->pdf(Form("extendhggpdfsmrel_%dTeV_%s_%sThisLumi",sqrts_,proc->c_str(),catname.c_str()));
			if (!tempPdf) {
				cerr << "[WARNING] -- pdf: " << Form("extendhggpdfsmrel_%dTeV_%s_%s",sqrts_,proc->c_str(),catname.c_str()) << " not found. It will be skipped" << endl;
				expectedObjectsNotFound.push_back(Form("extendhggpdfsmrel_%dTeV_%s_%s",sqrts_,proc->c_str(),catname.c_str()));
				continue;
			}
			if( merge ) {
      std::cout << "DEBUG Packager::packageOutput() q" << std::endl;
				outWS->import(*norm); //FIXME
				outWS->import(*tempPdf,RecycleConflictNodes()); //FIXME
			}
			sumPdfsThisCat->add(*tempPdf);
      std::cout << "DEBUG Packager::packageOutput() r" << std::endl;
			sumPdfs->add(*tempPdf);
		}
		if (sumPdfsThisCat->getSize()==0){
			cerr << "[WARNING] -- sumPdfs for cat " << catname.c_str() << " is EMPTY. Probably because the relevant pdfs couldn't be found. Skipping.. " << endl;
			continue;
		}
		// Dont put sqrts here as combine never uses this (but our plotting scripts do)
      std::cout << "DEBUG Packager::packageOutput() s" << std::endl;
		RooAddPdf *sumPdfsPerCat = new RooAddPdf(Form("sigpdfrel%s_allProcs",catname.c_str()),Form("sigpdfrel%s_allProcs",catname.c_str()),*sumPdfsThisCat);
		outWS->import(*sumPdfsPerCat,RecycleConflictNodes());
	}
	if (sumPdfs->getSize()==0){
		cerr << "[WARNING] -- sumAllPdfs is EMPTY. Probably because the relevant pdfs couldn't be found. Skipping.. " << endl;
	}
	else {
		// Dont put sqrts here as combine never uses this (but our plotting scripts do)
		RooAddPdf *sumPdfsAllCats = new RooAddPdf("sigpdfrelAllCats_allProcs","sigpdfrelAllCats_allProcs",*sumPdfs);
		outWS->import(*sumPdfsAllCats,RecycleConflictNodes());
	}

	if (runningNormSum->getSize()==0){
		cerr << "[WARNING] -- runningNormSum is EMPTY. Probably because the relevant normalizations couldn't be found. Skipping.. " << endl;
	}
	else {
		RooAddition *normSum = new RooAddition("normSum","normSum",*runningNormSum);
		outWS->import(*normSum,RecycleConflictNodes()); //FIXME

		if (!skipPlots_) {
      std::cout << "DEBUG Packager::packageOutput() u" << std::endl;
			RooRealVar *MH = (RooRealVar*)outWS->var("MH");
			RooRealVar *intLumi = (RooRealVar*)outWS->var("IntLumi");
			RooAddition *norm = (RooAddition*)outWS->function("normSum");
			TGraph *effAccGraph = new TGraph();
			TGraph *expEventsGraph = new TGraph();
			int p=0;
			for (double mh=mhLow_; mh<mhHigh_+0.5; mh+=1){
				double intLumiVal = 0.;
				if (intLumi){
					intLumiVal = intLumi->getVal();//FIXME
				//std::cout << "[INFO] (packager) intlumi value is " << intLumiVal << std::endl;
				} else {
					std::cout  << "[ERROR] IntLumi missing from workspace, exit "<< std::endl;
					//intLumiVal = 1000;
					return ;
				}
				MH->setVal(mh);
				expEventsGraph->SetPoint(p,mh,intLumiVal*norm->getVal());
				effAccGraph->SetPoint(p,mh,norm->getVal()/(normalization->GetXsection(mh)*normalization->GetBR(mh)));
				std::cout << " [INFO] eff*acc " << norm->getVal()/(normalization->GetXsection(mh)*normalization->GetBR(mh)) << std::endl;
				p++;
			}
      std::cout << "DEBUG Packager::packageOutput() v" << std::endl;
			TCanvas *canv = new TCanvas();
			effAccGraph->SetLineWidth(3);
			effAccGraph->GetXaxis()->SetTitle("m_{H} (GeV)");
			effAccGraph->GetYaxis()->SetTitle("efficiency #times acceptance");
			effAccGraph->Draw("AL");
			canv->Print(Form("%s/effAccCheck.pdf",outDir_.c_str()));
			canv->Print(Form("%s/effAccCheck.png",outDir_.c_str()));
			expEventsGraph->SetLineWidth(3);
			expEventsGraph->GetXaxis()->SetTitle("m_{H} (GeV)");
			double intLumiVal = 1000;
			if (intLumi){
				intLumiVal = intLumi->getVal();
				std::cout << "[INFO] intlumi value is " << intLumiVal << std::endl;
			} else {
				std::cout  << "[ERROR] could not find IntLumi var. Exit "<< std::endl;
				return ;
			}
      std::cout << "DEBUG Packager::packageOutput() w" << std::endl;
			expEventsGraph->GetYaxis()->SetTitle(Form("Expected Events for %4.1ffb^{-1}",intLumiVal/1000.));
			expEventsGraph->Draw("AL");
			canv->Print(Form("%s/expEventsCheck.pdf",outDir_.c_str()));
			canv->Print(Form("%s/expEventsCheck.png",outDir_.c_str()));
      std::cout << "DEBUG Packager::packageOutput() x" << std::endl;
			makePlots();
      std::cout << "DEBUG Packager::packageOutput() y" << std::endl;
		}
	}
      std::cout << "DEBUG Packager::packageOutput() z" << std::endl;
}

void Packager::makePlots(){
	RooRealVar *mass = (RooRealVar*)outWS->var("CMS_hgg_mass");
	RooRealVar *MH = (RooRealVar*)outWS->var("MH");
	RooAddPdf *sumPdfsAllCats = (RooAddPdf*)outWS->pdf("sigpdfrelAllCats_allProcs");
	map<int,RooDataSet*> dataSets;
	for (int m=mhLow_; m<=mhHigh_; m+=5){
		if (skipMass(m)) continue;
		RooDataSet *data = (RooDataSet*)outWS->data(Form("sig_mass_m%d_AllCats",m));
		if (data) {
    dataSets.insert(make_pair(m,data));
    }
	}
  if (sumPdfsAllCats){
	makePlot(mass,MH,sumPdfsAllCats,dataSets,"all");
  } else {
  std::cout << "[WARNING] sumPdfsAllCats missing or not generated, skipping it " <<std::endl;
  }

	for (int cat=0; cat<nCats_; cat++){
		string catname;
		if (sqrts_ == 13) catname=Form("%s",flashggCats_[cat].c_str());
		else if (sqrts_==7 || sqrts_==8) catname=Form("cat%d",cat);
		RooAddPdf *sumPdfsCat = (RooAddPdf*)outWS->pdf(Form("sigpdfrel%s_allProcs",catname.c_str()));
		map<int,RooDataSet*> dataSetsCat;
		for (int m=mhLow_; m<=mhHigh_; m+=5){
			if (skipMass(m)) continue;
			RooDataSet *data = (RooDataSet*)outWS->data(Form("sig_mass_m%d_%s",m,catname.c_str()));
			if (data) {
      dataSetsCat.insert(make_pair(m,data));
      }
		}
  if (sumPdfsCat){
		makePlot(mass,MH,sumPdfsCat,dataSetsCat,Form("%s",catname.c_str()));
    } else {
  std::cout << "[WARNING] sumPdfsCat missing or not generated, skipping it " <<std::endl;
    }
	}
}

void Packager::makePlot(RooRealVar *mass, RooRealVar *MH, RooAddPdf *pdf, map<int,RooDataSet*> data, string name){

	TCanvas *canv = new TCanvas();
	RooPlot *dataPlot = mass->frame(Title(name.c_str()),Range(100,160));
	for (map<int,RooDataSet*>::iterator it=data.begin(); it!=data.end(); it++){
		int mh = it->first;
		RooDataSet *dset = it->second;
		dset->plotOn(dataPlot,Binning(160));
		MH->setVal(mh);
		pdf->plotOn(dataPlot);
	}
	dataPlot->Draw();
	canv->Print(Form("%s/%s_fits.pdf",outDir_.c_str(),name.c_str()));
	canv->Print(Form("%s/%s_fits.png",outDir_.c_str(),name.c_str()));

	RooPlot *pdfPlot = mass->frame(Title(name.c_str()),Range(100,160));
	pdfPlot->GetYaxis()->SetTitle(Form("Pdf projection / %2.1f GeV",(mass->getMax()-mass->getMin())/160.));
	for (int mh=mhLow_; mh<=mhHigh_; mh++){
		MH->setVal(mh);
		// to get correct normlization need to manipulate with bins and range
		pdf->plotOn(pdfPlot,Normalization(mass->getBins()/160.*(mass->getMax()-mass->getMin())/60.,RooAbsReal::RelativeExpected));
	}
	pdfPlot->Draw();
	canv->Print(Form("%s/%s_interp.pdf",outDir_.c_str(),name.c_str()));
  std::cout << " DEBUG A " << std::endl;
	canv->Print(Form("%s/%s_interp.png",outDir_.c_str(),name.c_str()));
  std::cout << " DEBUG B " << std::endl;
	delete canv;
  std::cout << " DEBUG C " << std::endl;
}
