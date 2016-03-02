// Profiles normalisation in mass bins over multiple pdfs
// Author: M Kenzie
//
// There are a few different algorithms written, the default
// and most robust is guessNew() but it is very slow!!!
// If you would like to write something smarter that would be great!!


#include "TF1.h"
#include "TMatrixD.h"
#include "TFile.h"
#include "TMath.h"
#include "TLine.h"
#include "TDirectory.h"
#include "TH1F.h"
#include "TGraphAsymmErrors.h"
#include "RooDataSet.h"
#include "RooDataHist.h"
#include "RooMsgService.h"
#include "RooRandom.h"
#include "RooMinimizer.h"
#include "RooAbsPdf.h"
#include "RooExtendPdf.h"
#include "RooWorkspace.h"
#include "RooRealVar.h"
#include "TMath.h"
#include "TString.h"
#include "TCanvas.h"
#include "TMacro.h"
#include "TKey.h"
#include "TLegend.h"
#include "TLatex.h"
#include "TAxis.h"
#include "RooPlot.h"
#include "RooAddPdf.h"
#include "RooArgList.h"
#include "RooGaussian.h"
#include "TROOT.h"
#include "TStyle.h"
#include "RooFitResult.h"
#include "RooStats/NumberCountingUtils.h"
#include "RooStats/RooStatsUtils.h"
#include "RooCategory.h"
#include "../interface/WSTFileWrapper.h"

#include "boost/program_options.hpp"
#include "boost/algorithm/string/split.hpp"
#include "boost/algorithm/string/classification.hpp"
#include "boost/algorithm/string/predicate.hpp"
#include "../interface/ProfileMultiplePdfs.h"

#include "HiggsAnalysis/CombinedLimit/interface/RooMultiPdf.h"
#include "HiggsAnalysis/CombinedLimit/interface/RooBernsteinFast.h"

#include <iostream>

#include "../../tdrStyle/tdrstyle.C"
#include "../../tdrStyle/CMS_lumi.C"

using namespace RooFit;
using namespace std;
using namespace boost;
namespace po = boost::program_options;

//global vars
string bkgFileName;
//string bkgFileName100;
//string bkgFileName105;
//string bkgFileName110;
string sigFileName;
string outFileName;
string outDir;
string catLabel;
double massStep;
double nllTolerance;
bool doBands=false;
bool useBinnedData=false;
bool isMultiPdf=false;
bool doSignal=false;
bool unblind=false;
bool makeCrossCheckProfPlots=false;
int mhLow;
int mhHigh;
int sqrts;
float seed_;
float intLumi;
double mhvalue_;
int isFlashgg_ =1;
string flashggCatsStr_;
vector<string> flashggCats_;
double higgsResolution_=0.5;

bool verbose_=false;

int getBestFitFunction(RooMultiPdf *bkg, RooAbsData *data, RooCategory *cat, bool silent=false){

	double global_minNll = 1E10;
	int best_index = 0;
	int number_of_indeces = cat->numTypes();
	
	RooArgSet snap,clean;
	RooArgSet *params = bkg->getParameters(*data);
	params->snapshot(snap);
	params->snapshot(clean);
	if (!silent) {
		std::cout << "[INFO] CLEAN SET OF PARAMETERS" << std::endl;
		params->Print("V");
		std::cout << "-----------------------" << std::endl;
	}
	
	//bkg->setDirtyInhibit(1);
	RooAbsReal *nllm = bkg->createNLL(*data);
	RooMinimizer minim(*nllm);
	minim.setStrategy(2);
	
	for (int id=0;id<number_of_indeces;id++){		
		params->assignValueOnly(clean);
		cat->setIndex(id);

		//RooAbsReal *nllm = bkg->getCurrentPdf()->createNLL(*data);

		if (!silent) {
			std::cout << "[INFO] BEFORE FITTING" << std::endl;
			params->Print("V");
			std::cout << "-----------------------" << std::endl;
		}
		
		minim.minimize("Minuit2","simplex");
		double minNll = nllm->getVal()+bkg->getCorrection();
		if (!silent) {
			std::cout << "[INFO] After Minimization ------------------  " <<std::endl;
			std::cout << "[INFO] "<<bkg->getCurrentPdf()->GetName() << " " << minNll <<std::endl;
			bkg->Print("v");
			bkg->getCurrentPdf()->getParameters(*data)->Print("V");
			std::cout << " ------------------------------------  " << std::endl;
	
			std::cout << "[INFO] AFTER FITTING" << std::endl;
			params->Print("V");
			std::cout << "-----------------------" << std::endl;
		}
			
		if (minNll < global_minNll){
        		global_minNll = minNll;
			snap.assignValueOnly(*params);
        		best_index=id;
		}
	}
	params->assignValueOnly(snap);
    	cat->setIndex(best_index);
	
	if (!silent) {
		std::cout << "[INFO] Best fit Function -- " << bkg->getCurrentPdf()->GetName() << " " << cat->getIndex() <<std::endl;
		bkg->getCurrentPdf()->getParameters(*data)->Print("v");
	}
	return best_index;
}

RooMultiPdf* getExtendedMultiPdfs(RooMultiPdf* mpdf, RooCategory* mcat){

	RooArgList *newmPdfs = new RooArgList();
	for (int pInd=0; pInd<mpdf->getNumPdfs(); pInd++){
		mcat->setIndex(pInd);
		RooRealVar *normVar = new RooRealVar(Form("%snorm",mpdf->getCurrentPdf()->GetName()),"",0.,1.e6);
		RooExtendPdf *extPdf = new RooExtendPdf(Form("%sext",mpdf->getCurrentPdf()->GetName()),"",*(mpdf->getCurrentPdf()),*normVar);
		newmPdfs->add(*extPdf);
	}
	RooMultiPdf *empdf = new RooMultiPdf(Form("%sext",mpdf->GetName()),"",*mcat,*newmPdfs);
	return empdf;
}

pair<double,double> getNormTermNllAndRes(RooRealVar *mgg, RooAbsData *data, RooMultiPdf *mpdf, RooCategory *mcat, double normVal=-1., double massRangeLow=-1., double massRangeHigh=-1.){
	
	double bestFitNll=1.e8;
	double bestFitNorm;

	for (int pInd=0; pInd<mpdf->getNumPdfs(); pInd++){
		mcat->setIndex(pInd);
		RooRealVar *normVar = new RooRealVar(Form("%snorm",mpdf->getCurrentPdf()->GetName()),"",0.,1.e6);
		RooExtendPdf *extPdf;
		RooAbsReal *nll;
		if (massRangeLow>-1. && massRangeHigh>-1.){
			mgg->setRange("errRange",massRangeLow,massRangeHigh);
			extPdf = new RooExtendPdf(Form("%sext",mpdf->getCurrentPdf()->GetName()),"",*(mpdf->getCurrentPdf()),*normVar,"errRange");
			nll = extPdf->createNLL(*data,Extended()); //,Range(massRangeLow,massRangeHigh));//,Range("errRange"));
		}
		else {
			extPdf = new RooExtendPdf(Form("%sext",mpdf->getCurrentPdf()->GetName()),"",*(mpdf->getCurrentPdf()),*normVar);
			nll = extPdf->createNLL(*data,Extended());
		}
		
		if (normVal>-1.){
			normVar->setConstant(false);
			normVar->setVal(normVal);
			normVar->setConstant(true);
		}

		RooMinimizer minim(*nll);
		minim.setStrategy(0);
		//minim.minimize("Minuit2","simplex");
		minim.migrad();
		double corrNll = nll->getVal()+mpdf->getCorrection();

		//cout << "Found fit: " << mpdf->getCurrentPdf()->GetName() << " " << mpdf->getCorrection() << " " << normVar->getVal() << " " << corrNll << endl;

		if (corrNll<bestFitNll){
			bestFitNll=corrNll;
			bestFitNorm=normVar->getVal();
		}
		if (normVal>-1.) normVar->setConstant(false);
	}
	//cout << "CACHE: " << bestFitNorm << " -- " << bestFitNll << endl;
	return make_pair(2*bestFitNll,bestFitNorm);
}

double getNormTermNll(RooRealVar *mgg, RooAbsData *data, RooMultiPdf *mpdf, RooCategory *mcat, double normVal=-1., double massRangeLow=-1., double massRangeHigh=-1.){
	pair<double,double> temp = getNormTermNllAndRes(mgg,data,mpdf,mcat,normVal,massRangeLow,massRangeHigh);
	return temp.first;
}

double getNllThisVal(RooMultiPdf *mpdf, RooCategory *mcat, RooAbsData *data, RooRealVar *norm, double val, double doMinosErr=false){
	
	RooArgSet clean;
	RooArgSet *params = mpdf->getParameters(*data);
	params->snapshot(clean);

	RooAbsPdf *epdf=0;
	double bestFitNll=1.e8;
	for (int pIn=0; pIn<mpdf->getNumPdfs(); pIn++){
		params->assignValueOnly(clean);
		mcat->setIndex(pIn);
		epdf = new RooExtendPdf("epdf","",*(mpdf->getCurrentPdf()),*norm,"errRange");
		norm->setConstant(false);
		norm->setVal(val);
		norm->setConstant(true);
		RooAbsReal *nll = epdf->createNLL(*data,Extended());
		RooMinimizer minim(*nll);
		minim.setStrategy(0);
		//minim.setStrategy(2);
		//minim.setPrintLevel(-1);
		minim.migrad();
		//minim.minimize("Minuit2","simplex");
		if (doMinosErr) minim.minos(*norm);
		double corrNll = nll->getVal()+mpdf->getCorrection();
		if (corrNll<bestFitNll){
			bestFitNll=corrNll;
		}
		delete epdf;
	}
	return 2.*bestFitNll;
}

double quadInterpolate(double C, double X1,double X2,double X3,double Y1,double Y2,double Y3){

        gROOT->SetStyle("Plain");
        gROOT->SetBatch(true);
        gStyle->SetOptStat(0);
        // Use the 3 points to determine a,b,c
        TF1 func("f1","[0]*x*x+[1]*x+[2]",-5,5);

        TGraph g;
				g.SetPoint(0,X1,Y1);
				g.SetPoint(1,X2,Y2);
				g.SetPoint(2,X3,Y3);

				g.Fit(&func,"Q");

				/*	
				double entries[9];
        entries[0]=X1*X1; entries[1]=X1; entries[2]=1;
        entries[3]=X2*X2; entries[4]=X2; entries[5]=1;
        entries[6]=X3*X3; entries[7]=X3; entries[8]=1;

        //create the Matrix;
        TMatrixD M(3,3);
        M.SetMatrixArray(entries);
        M.Invert();

        double a = M(0,0)*Y1+M(0,1)*Y2+M(0,2)*Y3;
        double b = M(1,0)*Y1+M(1,1)*Y2+M(1,2)*Y3;
        double c = M(2,0)*Y1+M(2,1)*Y2+M(2,2)*Y3;

        func.SetParameter(0,a);
        func.SetParameter(1,b);
        func.SetParameter(2,c);
				*/

	// Check for Nan
	double RESULT = func.Eval(C);
	return RESULT;
	//if (RESULT != RESULT || fabs(1-RESULT/Y2) < 0.001 ) RESULT=Y2;

        //delete [] entries;
    //    return RESULT/Y2; // relative difference
}

double guessNew(RooRealVar *mgg, RooMultiPdf *mpdf, RooCategory *mcat, RooAbsData *data, double bestPoint, double nllBest, double boundary, double massRangeLow, double massRangeHigh, double crossing, double tolerance){
	
	bool isLowSide;
	double guess, guessNll, lowPoint,highPoint;
	if (boundary>bestPoint) {
		isLowSide=false;
		lowPoint = bestPoint;
		highPoint = boundary;
	}
	else {
		isLowSide=true;
		lowPoint = boundary;
		highPoint = bestPoint;
	}
	//double prevDistanceFromTruth = 1.e6;
	double distanceFromTruth = 1.e6;
	int nIts=0;
	while (TMath::Abs(distanceFromTruth/crossing)>tolerance) {
		
		//prevDistanceFromTruth=distanceFromTruth;
		guess = lowPoint+(highPoint-lowPoint)/2.;
		guessNll = getNormTermNll(mgg,data,mpdf,mcat,guess,massRangeLow,massRangeHigh)-nllBest;
    distanceFromTruth = crossing - guessNll;
	
		if (verbose_) {
			cout << "[INFO] "<< Form("\t lP: %7.3f hP: %7.3f xg: %7.3f yg: %7.3f",lowPoint,highPoint,guess,guessNll) << endl;;
			cout << "[INFO] \t ----------- " << distanceFromTruth/crossing << " -------------" << endl;
		}
		
		// for low side. if nll val is lower than target move right point left. if nll val is higher than target move left point right
		// vice versa for high side
		if (isLowSide){
			if (guessNll>crossing) lowPoint = guess;
			else highPoint=guess;
		}
		else {
			if (guessNll>crossing) highPoint = guess;
			else lowPoint=guess;
		}
		nIts++;
		// because these are envelope nll curves this algorithm can get stuck in local minima
		// hacked get out is just to start trying again
		if (nIts>20) {
			return guess;
			lowPoint = TMath::Max(0.,lowPoint-20);
			highPoint += 20;
			nIts=0;
			if (verbose_) cout << "[INFO] RESET:" << endl;
			// if it's a ridicolous value it wont converge so return value of bestGuess
			if (TMath::Abs(guessNll)>2e4) return 0.; 
		}
	}
	return guess;
}

double guess(RooMultiPdf *mpdf, RooCategory *mcat, RooAbsData *data, RooRealVar *norm, double bestPoint, double nllBest, double boundary, double crossing, double tolerance){
	
	bool isLowSide;
	double guess, guessNll, lowPoint,highPoint;
	if (boundary>bestPoint) {
		isLowSide=false;
		lowPoint = bestPoint;
		highPoint = boundary;
	}
	else {
		isLowSide=true;
		lowPoint = boundary;
		highPoint = bestPoint;
	}
	double distanceFromTruth = 1.e6;
	int nIts=0;
	while (TMath::Abs(distanceFromTruth/crossing)>tolerance) {
		
		guess = lowPoint+(highPoint-lowPoint)/2.;
		guessNll = getNllThisVal(mpdf,mcat,data,norm,guess)-nllBest;
		distanceFromTruth = crossing - guessNll;
	
		if (verbose_) {
			cout << "[INFO] "<< Form("\t lP: %7.3f hP: %7.3f xg: %7.3f yg: %7.3f",lowPoint,highPoint,guess,guessNll) << endl;;
			cout << "[INFO]" <<" \t ----------- " << distanceFromTruth/crossing << " -------------" << endl;
		}
		if (isLowSide){
			if (guessNll>crossing) lowPoint = guess;
			else highPoint=guess;
		}
		else {
			if (guessNll>crossing) highPoint = guess;
			else lowPoint=guess;
		}
		nIts++;
		if (nIts>20) {
			lowPoint = TMath::Min(0.,lowPoint-20);
			highPoint += 20;
			nIts=0;
			if (verbose_) cout << "[INFO] RESET:" << endl;
		}
	}
	return guess;
}

double quadInterpCoverageOnCrossingPoint(RooMultiPdf *mpdf, RooCategory *mcat, RooAbsData *data, RooRealVar *norm, double lowPoint, double highPoint, double bestPoint, double nllBest, double crossing, double tolerance){
	
	// x = 2NLL, y = nEvs
	double x1,x2,x3,y1,y2,y3;
  if (lowPoint<bestPoint){ // low side
		y1 = highPoint;
		y3 = lowPoint;
	}
	else { // high side}
		y1 = lowPoint;
		y3 = highPoint;
	}
	y2 = (lowPoint)+(highPoint-lowPoint)/2.;
	x1 = getNllThisVal(mpdf,mcat,data,norm,y1)-nllBest;
	x3 = getNllThisVal(mpdf,mcat,data,norm,y3)-nllBest;
	x2 = getNllThisVal(mpdf,mcat,data,norm,y2)-nllBest;
	
	double guess,guessNll;

	double distanceFromTruth = 1.e6;
	int nIts=0;
	while (TMath::Abs(distanceFromTruth/crossing)>tolerance) {
	
		guess = quadInterpolate(crossing,x1,x2,x3,y1,y2,y3);
		guessNll = getNllThisVal(mpdf,mcat,data,norm,guess)-nllBest;
		
		distanceFromTruth = crossing-guessNll;
		
		cout << "[INFO] " << Form("\t x1: %5.3f x2: %5.3f x3: %5.3f -> xg: %5.3f",x1,x2,x3,guessNll) << endl;;
		cout << "[INFO] " <<Form("\t y1: %5.3f y2: %5.3f y3: %5.3f -> yg: %5.3f",y1,y2,y3,guess) << endl;;
		cout << "[INFO] \t ----------- " << distanceFromTruth/crossing << " -------------" << endl;

		if (y1<y2) { // high side error
			if (guessNll<y2){
				x1=x2;
				y1=y2;
				x2=guessNll;
				y2=guess;
			}
			else {
				x3=x2;
				y3=y2;
				x2=guessNll;
				y2=guess;
			}
		} else { // low side error
			if (guessNll<y2){
				x3=x2;
				y3=y2;
				x2=guessNll;
				y2=guess;
			}
			else {
				x1=x2;
				y1=y2;
				x2=guessNll;
				y2=guess;
			}
		}
		nIts++;
	}
	cout << "[INFO] \t nIts = " << nIts << endl;
	return guess;
	
}

double convergeOnCrossingPoint(RooMultiPdf *mpdf, RooCategory *mcat, RooAbsData *data, RooRealVar *norm, double lowPoint, double highPoint, double nllBest, double crossing, double tolerance){

	// Assumes starting from best fit
	double lowPointNll; 
	double highPointNll;
	double guess;
	double guessNll;
	double distanceFromTruth = 1.e6;
	int nIts=0;
	while (TMath::Abs(distanceFromTruth/crossing)>tolerance) {
	
		lowPointNll = getNllThisVal(mpdf,mcat,data,norm,lowPoint)-nllBest;
		highPointNll = getNllThisVal(mpdf,mcat,data,norm,highPoint)-nllBest;

		if (lowPointNll>2.*crossing){
			lowPoint+=0.2;
			double temp = getNllThisVal(mpdf,mcat,data,norm,lowPoint)-nllBest;
			if (temp>crossing) lowPointNll = temp;
			else lowPoint-=0.2;
		}
		if (highPointNll>2.*crossing) {
			highPoint-=0.2;
			double temp = getNllThisVal(mpdf,mcat,data,norm,highPoint)-nllBest;
			if (temp>crossing) highPointNll = temp;
			else highPoint+=0.2;
		}

		TGraph *g = new TGraph();
		g->SetPoint(0,lowPointNll,lowPoint);
		g->SetPoint(1,highPointNll,highPoint);
		guess = TMath::Max(0.,g->Eval(crossing));
		delete g;

		// now figure out distance of guess from truth
		guessNll = getNllThisVal(mpdf,mcat,data,norm,guess)-nllBest;
		distanceFromTruth = crossing-guessNll;
		cout << "[INFO] "<< Form("\t xl: %5.3f xh: %5.3f -> xg: %5.3f",lowPointNll,highPointNll,guessNll) << endl;;
		cout << "[INFO] "<< Form("\t yl: %5.3f yh: %5.3f -> yg: %5.3f",lowPoint,highPoint,guess) << endl;;
		cout << "[INFO] "<< "\t ----------- " << distanceFromTruth/crossing << " -------------" << endl;
		if (lowPointNll>highPointNll) { // low side error
			if (crossing>guessNll) lowPoint = guess;
			else highPoint = guess;
		}
		else { // high side error
			if (crossing>guessNll) lowPoint = guess;
			else highPoint = guess;
		}
	nIts++;
	}
	cout << "[INFO] "<< "nIts = " << nIts << endl;
	return guess;
}

pair<double,double> asymmErr(RooMultiPdf *mpdf, RooCategory *mcat, RooAbsData *data, RooRealVar *mgg, double lowedge, double upedge, double nomBkg, double target, double tolerance=0.05){

	//RooRealVar *norm = new RooRealVar("norm","",0.0,0.0,1.e6);
	//mass->setRange("errRange",lowedge,upedge);
	
	//double nllBest = getNllThisVal(mpdf,mcat,data,norm,nomBkg);
	double nllBest = getNormTermNll(mgg,data,mpdf,mcat,-1,lowedge,upedge); // will return best fit
	double nllBestCheck = getNormTermNll(mgg,data,mpdf,mcat,nomBkg,lowedge,upedge); // should return same value
	double lowRange = TMath::Max(0.,nomBkg - TMath::Sqrt(target*nomBkg));
	double highRange = nomBkg + TMath::Sqrt(target*nomBkg);

	if (verbose_){
		cout << "[INFO] "<< "Best fit - " << nomBkg << "has nll " << nllBest << " check " << nllBestCheck << endl;
		cout << "[INFO] "<< "Scanning - " << lowRange << " -- " << highRange << endl;
	}
	
	return make_pair(1.,1.);
	/*
	double lowErr = guess(mpdf,mcat,data,norm,nomBkg,nllBest,lowRange,target,tolerance);
	double highErr = guess(mpdf,mcat,data,norm,nomBkg,nllBest,highRange,target,tolerance);
	if (verbose_) cout << "Found - lo:" << lowErr << " high: " << highErr << endl;
	delete norm;
	return make_pair(lowErr,highErr);
	*/
}

TGraph* profNorm(RooMultiPdf *mpdf, RooCategory *mcat, RooAbsData *data, RooRealVar *mass, double lowedge, double upedge, double nombkg, string name, double scanStep){

	double lowRange = double(floor(nombkg-2.*TMath::Sqrt(nombkg)+0.5));
	double highRange = double(floor(nombkg+2.*TMath::Sqrt(nombkg)+0.5));
	RooAbsPdf *epdf=0;

	RooRealVar *norm = new RooRealVar("norm","",0.0,0.0,1.e6);
	norm->setVal(nombkg);
	mass->setRange("errRange",lowedge,upedge);

	TGraph *envNll = new TGraph();
	TGraph *grNllPer[mpdf->getNumPdfs()];
	for (int i=0; i<mpdf->getNumPdfs(); i++) grNllPer[i] = new TGraph();
	
	int color[10] = {kBlue,kOrange,kGreen,kRed,kMagenta,kPink,kViolet,kCyan,kYellow,kBlack};
	int p=0;
	//for (double scanVal=80; scanVal<151; scanVal++){
	for (double scanVal=lowRange; scanVal<highRange+scanStep; scanVal+=scanStep){
		double minNllThisScan=1.e6;
		for (int pIn=0; pIn<mpdf->getNumPdfs(); pIn++){
			mcat->setIndex(pIn);
			epdf = new RooExtendPdf("epdf","",*(mpdf->getCurrentPdf()),*norm,"errRange");
			norm->setConstant(false);
			norm->setVal(scanVal);
			norm->setConstant(true);
			RooAbsReal *nll = epdf->createNLL(*data,Extended());
			RooMinimizer minim(*nll);
			minim.setStrategy(0);
			//minim.setPrintLevel(-1);
			minim.migrad();
			double corrNll = nll->getVal()+mpdf->getCorrection();
			//cout << norm->getVal() << " -- " << corrNll << endl;
			grNllPer[pIn]->SetPoint(p,norm->getVal(),2*corrNll);
			grNllPer[pIn]->SetName(mpdf->getCurrentPdf()->GetName());
			grNllPer[pIn]->SetLineWidth(2);
			grNllPer[pIn]->SetLineColor(color[pIn]);
			if (corrNll<minNllThisScan){
				minNllThisScan=corrNll;
			}
			delete epdf;
			delete nll;
		}
		//cout << "CACHE: " << scanVal << " -- " << minNllThisScan << endl;
		//double minNllThisScan = getNllThisVal(mpdf,mcat,data,norm,scanVal);
		envNll->SetPoint(p,scanVal,minNllThisScan);
		p++;
	}
	//dir->cd();
	envNll->SetName(name.c_str());
	double min=1.e8;
	double x,y;
	for (int p=0; p<envNll->GetN(); p++){
		envNll->GetPoint(p,x,y);
		if (y<min) min=y;
	}
	for (int p=0; p<envNll->GetN(); p++){
		envNll->GetPoint(p,x,y);
		envNll->SetPoint(p,x,y-min);
	}
	/*
	canv->cd();
	envNll->Draw("ALP");
	for (int i=0; i<mpdf->getNumPdfs(); i++) {
		
		for (int p=0; p<grNllPer[i]->GetN(); p++){
			grNllPer[i]->GetPoint(p,x,y);
			grNllPer[i]->SetPoint(p,x,y-min);
		}
		canv->cd();
		grNllPer[i]->Draw("LPsame");	
		grNllPer[i]->Write();
	}
	*/
	return envNll;
}

void profileExtendTerm(RooRealVar *mgg, RooAbsData *data, RooMultiPdf *mpdf, RooCategory *mcat, string name, double lowR, double highR, double massRangeLow=-1., double massRangeHigh=-1.){

	cout << "[INFO] "<< "Profiling extended term" << endl;
	int color[10] = {kBlue,kOrange,kGreen,kRed,kMagenta,kPink,kViolet,kCyan,kYellow,kBlack};
	double globMinNll=1.e8;
	double globMinVal;
	for (int pInd=0; pInd<mpdf->getNumPdfs(); pInd++){
		mcat->setIndex(pInd);
		if (TString(mpdf->getCurrentPdf()->GetName()).Contains("bern")) mpdf->getCurrentPdf()->forceNumInt();
		RooRealVar *normVar = new RooRealVar(Form("%snorm",mpdf->getCurrentPdf()->GetName()),"",0.,1.e6);
		RooExtendPdf *extPdf;
		RooAbsReal *nll;
		if (massRangeLow>-1. && massRangeHigh>-1.){
			mgg->setRange("errRange",massRangeLow,massRangeHigh);
			extPdf = new RooExtendPdf(Form("%sext",mpdf->getCurrentPdf()->GetName()),"",*(mpdf->getCurrentPdf()),*normVar,"errRange");
			nll = extPdf->createNLL(*data,Extended()); //,Range(massRangeLow,massRangeHigh));//,Range("errRange"));
		}
		else {
			extPdf = new RooExtendPdf(Form("%sext",mpdf->getCurrentPdf()->GetName()),"",*(mpdf->getCurrentPdf()),*normVar);
			nll = extPdf->createNLL(*data,Extended());
		}

		TGraph *prof = new TGraph();
		int p=0;
		for (double v=lowR; v<=highR; v+=5) {
			normVar->setConstant(false);
			normVar->setVal(v);
			normVar->setConstant(true);
			RooMinimizer minim(*nll);
			minim.setStrategy(2);
			minim.minimize("Minuit2","simplex");
			double corrNll = nll->getVal()+mpdf->getCorrection();
			prof->SetPoint(p,v,corrNll);
			cout << "[INFO] "<< v << " " << corrNll << endl;
			if (corrNll<globMinNll){
				globMinNll=corrNll;
				globMinVal=v;
			}
			p++;
		}
		cout << "[INFO] "<< "Best fit (approx) at " << globMinVal << " " << globMinNll << endl;
		prof->SetLineColor(color[pInd]);
		prof->SetName(Form("profExtTerm_%s",mpdf->getCurrentPdf()->GetName()));
		prof->Write();
		delete prof;
	}
}


int main(int argc, char* argv[]){
  
  // set up plots to be in TDR style
  setTDRStyle();
  writeExtraText = true;       // if extra text
  extraText  = "Preliminary";  // default extra text is "Preliminary"
  lumi_8TeV  = "19.1 fb^{-1}"; // default is "19.7 fb^{-1}"
  lumi_7TeV  = "4.9 fb^{-1}";  // default is "5.1 fb^{-1}"
  lumi_sqrtS = "13 TeV";       // used with iPeriod = 0, e.g. for simulation-only plots (default is an empty string)

  //parse options
	po::options_description desc("Allowed options");
	desc.add_options()
		("help,h", 																																		 			"Show help")
		("bkgFileName,b", po::value<string>(&bkgFileName), 																	"Input file name (for multipdf)")
		//("bkgFileName100", po::value<string>(&bkgFileName100), 																	"Input file name (for multipdf)")
		//("bkgFileName105", po::value<string>(&bkgFileName105), 																	"Input file name (for multipdf)")
		//("bkgFileName110", po::value<string>(&bkgFileName110), 																	"Input file name (for multipdf)")
		("seed", po::value<float>(&seed_)->default_value(0.),                                    "seed for pseudodata gandom number generator")
		("sigFileName,s", po::value<string>(&sigFileName), 																	"Input file name (for signal model)")
		("outFileName,o", po::value<string>(&outFileName)->default_value("BkgPlots.root"),	"Output file name")
		("outDir,D", po::value<string>(&outDir)->default_value("BkgPlots"),						 			"Output directory")
		("catLabel,l", po::value<string>(&catLabel),																	 			"Label category")
		("doBands",																																		 			"Do error bands")
		("isMultiPdf",																																			"Is this a multipdf ws?")
		("unblind",																																						"un blind central mass region")
		("useBinnedData",																															 			"Data binned")
		("makeCrossCheckProfPlots",																													"Make some cross check plots -- very slow!")
		("massStep,m", po::value<double>(&massStep)->default_value(0.5),						   			"Mass step for calculating bands. Use a large number like 5 for quick running")
		("nllTolerance,n", po::value<double>(&nllTolerance)->default_value(0.05),			 			"Tolerance for nll calc in %")
		("mhLow,L", po::value<int>(&mhLow)->default_value(100),															"Starting point for scan")
		("mhHigh,H", po::value<int>(&mhHigh)->default_value(180),														"End point for scan")
		("mhVal", po::value<double>(&mhvalue_)->default_value(125.),														"Choose the MH for the plots")
		("higgsResolution", po::value<double>(&higgsResolution_)->default_value(1.),															"Starting point for scan")
		("intLumi", po::value<float>(&intLumi)->default_value(2.61),																"What intLumi in fb^{-1}")
		("sqrts,S", po::value<int>(&sqrts)->default_value(8),																"Which centre of mass is this data from?")
		("isFlashgg",  po::value<int>(&isFlashgg_)->default_value(1),  								    	        "Use Flashgg output ")
		("flashggCats,f", po::value<string>(&flashggCatsStr_)->default_value("UntaggedTag_0,UntaggedTag_1,UntaggedTag_2,UntaggedTag_3,VBFTag_0,VBFTag_1,VBFTag_2,TTHHadronicTag,TTHLeptonicTag,VHHadronicTag,VHTightTag,VHLooseTag,VHEtTag"),       "Flashgg category names to consider")
		("verbose,v", 																																			"Verbose");
	;
	po::variables_map vm;
	po::store(po::parse_command_line(argc,argv,desc),vm);
	po::notify(vm);
	if (vm.count("help")) { cout << desc << endl; exit(1); }
	if (vm.count("doBands")) doBands=true;
	if (vm.count("isMultiPdf")) isMultiPdf=true;
	if (vm.count("makeCrossCheckProfPlots")) makeCrossCheckProfPlots=true;
	if (vm.count("unblind")) unblind=true;
	if (vm.count("useBinnedData")) useBinnedData=true;
	if (vm.count("sigFileName")) doSignal=true;
	if (vm.count("verbose")) verbose_=true;

	RooMsgService::instance().setGlobalKillBelow(RooFit::ERROR);
	RooMsgService::instance().setSilentMode(true);
	split(flashggCats_,flashggCatsStr_,boost::is_any_of(","));

  //make outdir for plots
	system(Form("mkdir -p %s",outDir.c_str()));

  // open bkg shapes workspace, this also contains the finely binned DATA in RooDataHists
	WSTFileWrapper * inWS = new WSTFileWrapper(bkgFileName,"multipdf");
	if (!inWS ) {
		cout << "[ERROR] "<< "Cant find the workspace" << endl;
		exit(0);
	}

  //output file to contain the new fake data
	TFile *outFile = TFile::Open(outFileName.c_str(),"RECREATE");
  TDirectory *cdtof = outFile->mkdir("tagsDumper");
  cdtof->cd();    // make the "tof" directory the current director
	RooWorkspace *outWS = new RooWorkspace("multipdf");

  for (int icat =0 ; icat < flashggCats_.size() ; icat ++){

  string catname;
  catname=flashggCats_[icat];
  

  RooRealVar *mass =0;
  mass =(RooRealVar*)inWS->var("CMS_hgg_mass");
	
  //this is the finely binned Data! 
  RooAbsData *data = inWS->data(Form("roohist_data_mass_%s",catname.c_str())); // get data ! 
  

  //open mutlipdfs
	RooMultiPdf *mpdf = 0; 
	RooCategory *mcat = 0;
	if (isMultiPdf) {
		mpdf = (RooMultiPdf*)inWS->pdf(Form("CMS_hgg_%s_%dTeV_bkgshape",catname.c_str(),sqrts));
		mcat = (RooCategory*)inWS->cat(Form("pdfindex_%s_%dTeV",catname.c_str(),sqrts));
		if (!mpdf || !mcat ){
			cout << "[ERROR] "<< "Can't find multipdfs (" << Form("CMS_hgg_%s_%dTeV_bkgshape",catname.c_str(),sqrts) << ") or multicat ("<< Form("pdfindex_%s_%dTeV",catname.c_str(),sqrts) <<")" << endl;
			exit(1);
		}
	} else {
    std::cout << "ERROR must provide mutlipdf . exit" << std::endl;
    exit(1);
  }
  

  //get current pdf from multipdf 
	cout << "[INFO] "<< "Current PDF and data:" << endl;
	cout<< "[INFO] " << "\t"; mpdf->getCurrentPdf()->Print();
	cout << "[INFO] "<< "\t"; data->Print();
  //copy it into the new ws
  std::cout << "[INFO] importing multicat" << mcat->GetName() <<std::endl;
  outWS->import(*mcat);
  std::cout << "[INFO] importing multipdf" << mpdf->GetName()<< std::endl;
  outWS->import(*mpdf);
  outWS->import(inWS->allVars(),RecycleConflictNodes());
  
  //we want to throw  fake data based on the best fit pdf
  //so figure out which ione that is 
	int bf = getBestFitFunction(mpdf,data,mcat,!verbose_);
	mcat->setIndex(bf);
	cout<< "[INFO] " << "Best fit PDF and data:" << endl;
	cout<< "[INFO] " << "\t"; mpdf->getCurrentPdf()->Print();
	cout<< "[INFO] " << "\t"; data->Print();
  
  // ok, make some holders for the new fake data 
  RooDataHist* fakedata = (RooDataHist*) data->emptyClone(); // will hold the real data outside the blinded region + generated data in blinded region
  RooDataHist* fakedataExtra = (RooDataHist*) data->emptyClone(); // will hold the fake data generated in blinded region 
  RooDataHist* fakedataExtraBkgOnly = (RooDataHist*) data->emptyClone(); // will hold the fake data without the signla in blinded region
  int  nEntriesInBlindRegion =0; // number of events need to generate in blinded region
  //int  nEntriesInIgnoredRegion =0;
 // int  nEntriesInIgnoredRegion0 =0;
  float  nEntriesFromSig = 0; 
  float  nEntriesFromBkg = 0;
  int nBins=0;
  //RooDataSet* dataGenerated = (RooDataSet*) data->emptyClone();
  float max=-999; //used to get min and max of range of mH... probs not needed anymore. 
  float min=+999;
  //now figure out how many events in blinded region we need to generate.
  for (int iEntry =0 ; iEntry < data->numEntries() ; iEntry ++){
     mass->setVal(data->get(iEntry)->getRealValue("CMS_hgg_mass"));
     if (mass->getVal()< mhLow) { /*nEntriesInIgnoredRegion+=data->weight(); */ continue;} //ignore events in overflow bins 
     if (mass->getVal()== mhLow) {/*nEntriesInIgnoredRegion0+=data->weight() ;*/ continue;} // ignore events in overflow bins
     if (mass->getVal() < min) min=mass->getVal(); // set min
     if (mass->getVal() > max) max=mass->getVal(); // set max
     if (mass->getVal() > 135 || mass->getVal() < 115){ // ok, if mass is outside of blinded region, add it to our fakedata holder
     fakedata->add( RooArgList(*mass),data->weight() );
     } else { // if not, get want to teh weight to the tally of nEvents to generated for the blind region
     nEntriesInBlindRegion+=data->weight();
     }
  }
  
  // little summary message and turn min/max into ints.
  min=floor(min+0.5);
  max=floor(max+0.5);
  nBins= max-min; // should always be 80 anyway, might remove this and just hard code for simplicity at a later date
  std::cout << "[INFO] for dataset " << data->GetName() << "  max " << max  << " min "<< min << " nBins " << nBins << " and nEventInblindRegion " << nEntriesInBlindRegion <<  std::endl;
  
	// prepare the frame
	TLegend *leg = new TLegend(0.6,0.6,0.89,0.89);
	leg->SetFillColor(0);
	leg->SetLineColor(0);
	cout<< "[INFO] " << "Plotting data and nominal curve" << endl;
  mass->setRange("fitRange",100,180);
  mass->setRange("fullRange",100,180);
  mass->setBins(80);
  RooPlot *plot = mass->frame();
	plot->GetXaxis()->SetTitle("m_{#gamma#gamma} (GeV)");
	plot->SetTitle("");
	
  // plot the full DATA but **invisibly** !!!
  // need the full data to do the fitting of the best-fit pdf and generate toys.
  data->plotOn(plot,CutRange("fullRange"),Invisible());
	// grab the RooCurve of best fit pdf fit ti invisible data
  TObject *dataLeg = (TObject*)plot->getObject(plot->numItems()-1);
	mpdf->getCurrentPdf()->plotOn(plot,LineColor(kRed),LineWidth(2),NormRange("fitRange"));
	RooCurve *nomBkgCurve = (RooCurve*)plot->getObject(plot->numItems()-1);

  // legend... wait for it...dary.  
	leg->AddEntry(dataLeg,"Data","LEP");
	leg->AddEntry(nomBkgCurve,"Bkg Fit","L");
  
  //show the values of that curve from best fit pdf fit to invisible data
  if (verbose_){
    std::cout << " DEBUG nomBkgCurve at 120 " << nomBkgCurve->interpolate(120) << std::endl;
    std::cout << " DEBUG nomBkgCurve at 130 " << nomBkgCurve->interpolate(130) << std::endl;
    std::cout << " DEBUG nomBkgCurve at 140 " << nomBkgCurve->interpolate(140) << std::endl;
    std::cout << " DEBUG nomBkgCurve at 150 " << nomBkgCurve->interpolate(150) << std::endl;
    std::cout << " DEBUG nomBkgCurve at 160 " << nomBkgCurve->interpolate(160) << std::endl;
    std::cout << " DEBUG nomBkgCurve at 170 " << nomBkgCurve->interpolate(170) << std::endl;
    std::cout << " DEBUG nomBkgCurve at 180 " << nomBkgCurve->interpolate(180) << std::endl;
  }

  cout<< "[INFO] " << "Plot has " << plot->GetXaxis()->GetNbins() << " bins" << endl;
	outFile->cd();
  
  //prepare the canvas and draw stuff on it.
	TCanvas *canv = new TCanvas("c","",800,800);
	RooRealVar *lumi = (RooRealVar*)inWS->var("IntLumi"); //do we need this guy??
  mass->setRange(100,180);
	plot->Draw();
  
  //set ranges corresponding to blinded regions.
  mass->setRange("unblind_up",135,180);
  mass->setRange("unblind_down",mhLow,115); 
  
  // and plot fake data in the unblinided region
  fakedata->plotOn(plot,CutRange("unblind_down,unblind_up"),Binning(nBins));
  
  // if unblind, plot the full data... if not, well, plot nothing
  if (!unblind) {
    //  data->plotOn(plot,Binning(nBins),CutRange("unblind_down,unblind_up"),MarkerColor(kBlack));
  }
  else {
    data->plotOn(plot,Binning(nBins),MarkerColor(kBlack));
  }

  //ok, now we are going to deal with the signal model
  if (doSignal){ // not really option, if this is false teh program will end
    // open that signal model!
    TFile *sigFile = TFile::Open(sigFileName.c_str());
    // from sigfit
    WSTFileWrapper *w_sig = new WSTFileWrapper(sigFileName,"wsig_13TeV");
    if (!w_sig) { //from workspaces directly... this probably will not work. shoudl delete this option #FIXME
       WSTFileWrapper *w_sig = new WSTFileWrapper(sigFileName,"cms_hgg_workspace");
    }
    if (!w_sig) {
      cout << "[INFO] " << "Signal workspace not found. exit" << endl;
      exit(1);
    }
    // mh is higgs mass
    RooRealVar *MH = (RooRealVar*)w_sig->var("MH");
    if (!MH) MH = (RooRealVar*)w_sig->var("CMS_hgg_mass"); // is this right ? Maybe this never happens.
    MH->setMin(mhvalue_); //probably always 125.
    //get signal model pdf
    RooAbsPdf *sigPDF = (RooAbsPdf*)w_sig->pdf(Form("sigpdfrel%s_allProcs",catname.c_str()));
    MH->setVal(mhvalue_);
    //plot our friend the signal model on the RooPlot
    sigPDF->plotOn(plot,Normalization(1.0,RooAbsReal::RelativeExpected),LineColor(kBlue),LineWidth(3));
    sigPDF->plotOn(plot,Normalization(1.0,RooAbsReal::RelativeExpected),LineColor(kBlue),LineWidth(3),FillColor(38),FillStyle(3001),DrawOption("F"));
    //now figure out how many events are expected from the signal model at this mH.
    nEntriesFromSig =sigPDF->expectedEvents(*MH);
    std::cout << "[INFO] expected number of events in signal PDF " << nEntriesFromSig << std::endl;	
    cout << "[INFO] " << " Genrate sig events"  <<  nEntriesFromSig << " ( "<< (int) nEntriesFromSig << ")"<< endl;
  
    // time to throw some toys!
    // throw 100* more than we need and select the ones we want in the for loop below.
    RooDataSet *tmpDatasetSig = sigPDF->generate(*mass,1+(int)nEntriesFromSig*100); 
    cout << "[INFO] " << " tmpDataset " << tmpDatasetSig << " - " << *tmpDatasetSig << endl;
  
    //now we fill the actual fakedataset with signal events in the right range picked from the above.
    int filledEntries =0;
   for (int iEntry =0 ; iEntry < tmpDatasetSig->numEntries() ; iEntry ++){
      mass->setVal(tmpDatasetSig->get(iEntry)->getRealValue("CMS_hgg_mass")); 
      if (iEntry%100==0) std::cout << "[DEBUG] mass value sig " << mass->getVal() << std::endl;
      if (mass->getVal() < 135 && mass->getVal() > 115){
        fakedataExtra->add( RooArgList(*mass),tmpDatasetSig->weight() );
        filledEntries++;
        if (filledEntries > (int)nEntriesFromSig ) {
          std::cout << "[INFO] reached required nEvents Sig = " << filledEntries << std::endl;
          break;
        }
      }
    }
    //dataGenerated->append(*tmpDatasetSig);
    //Now add the signal to the legend
    TObject *sigLeg = (TObject*)plot->getObject(plot->numItems()-1);
    leg->AddEntry(sigLeg,Form("Sig model m_{H}=%.1fGeV",MH->getVal()),"L");
    //outWS->import(*sigPDF);
  } else {
   std::cout << "[ERROR] Cannot generate fake data without ignal model... please specify one with option -s. exit" << std::endl;
   exit(1);
  }

  //remaining entries to generate shoudl come from bkg model
  nEntriesFromBkg=(nEntriesInBlindRegion-nEntriesFromSig);
  std::cout << "[INFO] nEntriesFromBkg " << nEntriesFromBkg << " nEntriesInBlindRegion " << nEntriesInBlindRegion << " nEntriesFromSig " << nEntriesFromSig << std::endl;
  cout << "[INFO] " << " Genrate bkg events " << nEntriesFromBkg << "(" << (int) nEntriesFromBkg << ")" <<endl;
  
  // once again generate 100* more events than needed so we can pick some in the range we want
	RooRandom::randomGenerator()->SetSeed(seed_);
  int generateNevnt = (int)(nEntriesFromBkg*100);
  RooDataSet *tmpDataset = mpdf->getCurrentPdf()->generate(*mass,generateNevnt);
  
  // now select events in the right range from those generated above
  int filledEntries =0;
  for (int iEntry =0 ; iEntry < tmpDataset->numEntries() ; iEntry ++){
    mass->setVal(tmpDataset->get(iEntry)->getRealValue("CMS_hgg_mass")); 
    //if (mass->getVal()<100) std::cout << "[DEBUG] mass value nkg LESS THAN  100 " << mass->getVal() << std::endl;
    if (iEntry%1000==0) std::cout << "[INFO] mass value bkg " << mass->getVal() << std::endl;
    if (mass->getVal() < 135 && mass->getVal() > 115){ // event in blinded region, so add it in!
      fakedataExtra->add( RooArgList(*mass),tmpDataset->weight() );
      fakedataExtraBkgOnly->add( RooArgList(*mass),tmpDataset->weight() );
      filledEntries++;
      if (filledEntries > (int)nEntriesFromBkg ) {
        std::cout << "DEBUG reached required nEvents Bkg = " << filledEntries << std::endl;
        break;
      }
    }
  }
  // now plot the bkg only and sig+bkg toys.
  fakedataExtra->plotOn(plot,Binning(nBins),MarkerColor(kOrange));
  fakedataExtraBkgOnly->plotOn(plot,Binning(nBins),MarkerColor(kBlue));

  //finally, add them to the final fakedata
  for (int iEntry =0 ; iEntry < fakedataExtra->numEntries() ; iEntry ++){
    mass->setVal(fakedataExtra->get(iEntry)->getRealValue("CMS_hgg_mass")); 
    fakedata->add( RooArgList(*mass),fakedataExtra->weight() );
  }
  
  //import this into the output workspace
  outWS->import(*fakedata);
  
  // make the plots and make 'em look nice etc
  plot->Draw("same");
  leg->Draw("same");

  TLatex *latex = new TLatex();	
  latex->SetTextSize(0.03);
  latex->SetNDC();
  TLatex *cmslatex = new TLatex();
  cmslatex->SetTextSize(0.03);
  cmslatex->SetNDC();
  cmslatex->DrawLatex(0.25,0.85,Form("#splitline{}{#sqrt{s} = %dTeV L = %2.3ffb^{-1}}",sqrts,intLumi));
  latex->DrawLatex(0.25,0.78,catLabel.c_str());
  outWS->import(*lumi,RecycleConflictNodes());

  if (unblind) plot->SetMinimum(0.0001); // not sure what this is for
  plot->GetYaxis()->SetTitleOffset(1.3);
  canv->Modified();
  canv->Update();
  CMS_lumi( canv, 0, 0);

  //save the plots
  canv->Print(Form("%s/fake_data_plot_%s.pdf",outDir.c_str(),catname.c_str()));
  canv->Print(Form("%s/fake_data_plot_%s.png",outDir.c_str(),catname.c_str()));
  canv->Print(Form("%s/fake_data_plot_%s.C",outDir.c_str(),catname.c_str()));
  canv->SetName(Form("fake_data_lot_%s",catname.c_str()));
  outFile->cd();
  canv->Write();

  }
  outFile->cd();
 // cdtof->cd();    // make the "tof" directory the current director
  outWS->Write();
  outFile->Close();


  return 0;
}

