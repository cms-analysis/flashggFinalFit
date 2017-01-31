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
#include "RooMinimizer.h"
#include "RooAbsPdf.h"
#include "RooHist.h"
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

#include <TSystem.h>

using namespace RooFit;
using namespace std;
using namespace boost;
namespace po = boost::program_options;

bool verbose_=false;

RooRealVar *intLumi_ = new RooRealVar("IntLumi","hacked int lumi", 1000.);

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

void plotAllPdfs(RooRealVar *mgg, RooAbsData *data, RooMultiPdf *mpdf, RooCategory *mcat, string name, int cat, bool unblind, int isFlashgg, std::vector<string> flashggCats){
	string catname;
	if (isFlashgg){
		catname = Form("%s",flashggCats[cat].c_str());
	} else {
		catname = Form("cat%d",cat);
	}
	RooPlot *plot = mgg->frame();
	plot->SetTitle(Form("Background functions profiled for category %s",catname.c_str()));
	plot->GetXaxis()->SetTitle("m_{#gamma#gamma} (GeV)");
	if (!unblind) {
		mgg->setRange("unblind_up",135,180);
		mgg->setRange("unblind_down",100,115);
		data->plotOn(plot,Binning(80),CutRange("unblind_down,unblind_up"));
	}
	else {
		data->plotOn(plot,Binning(80));
	}

	TLegend *leg = new TLegend(0.6,0.4,0.92,0.92);
	leg->SetFillColor(0);
	leg->SetLineColor(0);

	int color[10] = {kBlue,kOrange,kGreen,kRed,kMagenta,kPink,kViolet,kCyan,kYellow,kBlack};
	for (int pInd=0; pInd<mpdf->getNumPdfs(); pInd++){
		mcat->setIndex(pInd);
		// Always refit since we cannot be sure the best fit pdf is being fitted
		mpdf->getCurrentPdf()->fitTo(*data);
		mpdf->getCurrentPdf()->plotOn(plot,LineColor(color[pInd]),LineWidth(2));
		TObject *legObj = plot->getObject(plot->numItems()-1);
		leg->AddEntry(legObj,mpdf->getCurrentPdf()->GetName(),"L");
	}

	TCanvas *canv = new TCanvas();
	plot->Draw();
	if (!unblind) plot->SetMinimum(0.0001);
	leg->Draw();
	canv->Modified();
	canv->Update();
	canv->Print(Form("%s.pdf",name.c_str()));
	canv->Print(Form("%s.png",name.c_str()));
	canv->Print(Form("%s.C",name.c_str()));
	delete canv;
}

int main(int argc, char* argv[]){
  gSystem->Load("$CMSSW_BASE/lib/$SCRAM_ARCH/libHiggsAnalysisGBRLikelihood.so");
  
  setTDRStyle();
  writeExtraText = true;       // if extra text
  extraText  = "Preliminary";  // default extra text is "Preliminary"
  lumi_13TeV ="2.6 fb^{-1}";
  lumi_8TeV  = "19.1 fb^{-1}"; // default is "19.7 fb^{-1}"
  lumi_7TeV  = "4.9 fb^{-1}";  // default is "5.1 fb^{-1}"
  lumi_sqrtS = "13 TeV";       // used with iPeriod = 0, e.g. for simulation-only plots (default is an empty string)


	string bkgFileName;
	string sigFileName;
	string outFileName;
	string outDir;
	int cat;
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
	float intLumi;
	double mhvalue_;
	int isFlashgg_ =1;
	string flashggCatsStr_;
	vector<string> flashggCats_;
  double higgsResolution_=0.5;

	po::options_description desc("Allowed options");
	desc.add_options()
		("help,h", 																																		 			"Show help")
		("bkgFileName,b", po::value<string>(&bkgFileName), 																	"Input file name")
		("sigFileName,s", po::value<string>(&sigFileName), 																	"Input file name")
		("outFileName,o", po::value<string>(&outFileName)->default_value("BkgPlots.root"),	"Output file name")
		("outDir,d", po::value<string>(&outDir)->default_value("BkgPlots"),						 			"Output directory")
		("cat,c", po::value<int>(&cat),																								 			"Category")
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
		("intLumi", po::value<float>(&intLumi)->default_value(0.),																"What intLumi in fb^{-1}")
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
  lumi_13TeV =Form("%.1f fb^{-1}",intLumi);	
	system(Form("mkdir -p %s",outDir.c_str()));
	if (makeCrossCheckProfPlots) system(Form("mkdir -p %s/normProfs",outDir.c_str()));

	TFile *inFile = TFile::Open(bkgFileName.c_str());
	//RooWorkspace *inWS = (RooWorkspace*)inFile->Get("multipdf");
	WSTFileWrapper * inWS = new WSTFileWrapper(bkgFileName,"multipdf");
	//if (!inWS) inWS = (RooWorkspace*)inFile->Get("cms_hgg_workspace");
	if (!inWS) {
		cout << "[ERROR] "<< "Cant find the workspace" << endl;
		exit(0);
	}
	RooRealVar *mgg = (RooRealVar*)inWS->var("CMS_hgg_mass");
  string catname;
	if (isFlashgg_){
		catname = Form("%s",flashggCats_[cat].c_str());
	} else {
		catname = Form("cat%d",cat);
	}

	TFile *outFile = TFile::Open(outFileName.c_str(),"RECREATE");
	RooWorkspace *outWS = new RooWorkspace("bkgplotws","bkgplotws");

	RooAbsData *data = (RooDataSet*)inWS->data(Form("data_mass_%s",catname.c_str()));
	if (useBinnedData) data = (RooDataHist*)inWS->data(Form("roohist_data_mass_%s",catname.c_str()));

	RooAbsPdf *bpdf = 0;
	RooMultiPdf *mpdf = 0; 
	RooCategory *mcat = 0;
	if (isMultiPdf) {
		mpdf = (RooMultiPdf*)inWS->pdf(Form("CMS_hgg_%s_%dTeV_bkgshape",catname.c_str(),sqrts));
		mcat = (RooCategory*)inWS->cat(Form("pdfindex_%s_%dTeV",catname.c_str(),sqrts));
		if (!mpdf || !mcat){
			cout << "[ERROR] "<< "Can't find multipdfs (" << Form("CMS_hgg_%s_%dTeV_bkgshape",catname.c_str(),sqrts) << ") or multicat ("<< Form("pdfindex_%s_%dTeV",catname.c_str(),sqrts) <<")" << endl;
			exit(0);
		}
	}
	else {
		bpdf = (RooAbsPdf*)inWS->pdf(Form("pdf_data_pol_model_%dTeV_%s",sqrts,catname.c_str()));
		if (!bpdf){
			cout << "[ERROR] "<< "Cant't find background pdf " << Form("pdf_data_pol_model_%dTeV_%s",sqrts,catname.c_str()) << endl;
			exit(0);
		}
		mcat = new RooCategory(Form("pdfindex_%s_%dTeV",catname.c_str(),sqrts),"c");
		RooArgList temp;
		temp.add(*bpdf);
		mpdf = new RooMultiPdf(Form("tempmpdf_%s",catname.c_str()),"",*mcat,temp);
	}

	cout << "[INFO] "<< "Current PDF and data:" << endl;
	cout<< "[INFO] " << "\t"; mpdf->getCurrentPdf()->Print();
	cout << "[INFO] "<< "\t"; data->Print();

	// plot all the pdfs for reference
	if (isMultiPdf || verbose_) plotAllPdfs(mgg,data,mpdf,mcat,Form("%s/allPdfs_%s",outDir.c_str(),catname.c_str()),cat,unblind, isFlashgg_, flashggCats_);

	// include normalization hack RooBernsteinFast;
	/*
		 for (int pInd=0; pInd<mpdf->getNumPdfs(); pInd++){
		 mcat->setIndex(pInd);
		 if (mpdf->getCurrentPdf()->IsA()->InheritsFrom(RooBernsteinFast<1>::Class())) mpdf->getCurrentPdf()->forceNumInt();	
		 if (mpdf->getCurrentPdf()->IsA()->InheritsFrom(RooBernsteinFast<2>::Class())) mpdf->getCurrentPdf()->forceNumInt();	
		 if (mpdf->getCurrentPdf()->IsA()->InheritsFrom(RooBernsteinFast<3>::Class())) mpdf->getCurrentPdf()->forceNumInt();	
		 if (mpdf->getCurrentPdf()->IsA()->InheritsFrom(RooBernsteinFast<4>::Class())) mpdf->getCurrentPdf()->forceNumInt();	
		 if (mpdf->getCurrentPdf()->IsA()->InheritsFrom(RooBernsteinFast<5>::Class())) mpdf->getCurrentPdf()->forceNumInt();	
		 if (mpdf->getCurrentPdf()->IsA()->InheritsFrom(RooBernsteinFast<6>::Class())) mpdf->getCurrentPdf()->forceNumInt();	
		 if (mpdf->getCurrentPdf()->IsA()->InheritsFrom(RooBernsteinFast<7>::Class())) mpdf->getCurrentPdf()->forceNumInt();	
		 }
		 */

	// reset to best fit
	int bf = getBestFitFunction(mpdf,data,mcat,!verbose_);
	mcat->setIndex(bf);
	cout<< "[INFO] " << "Best fit PDF and data:" << endl;
	cout<< "[INFO] " << "\t"; mpdf->getCurrentPdf()->Print();
	cout<< "[INFO] " << "\t"; data->Print();

	// plot the data
	TLegend *leg = new TLegend(0.6,0.6,0.89,0.89);
	leg->SetFillColor(0);
	leg->SetLineColor(0);

	cout<< "[INFO] " << "Plotting data and nominal curve" << endl;
	RooPlot *plot = mgg->frame();
	RooPlot *plotLC = mgg->frame();
	plot->GetXaxis()->SetTitle("m_{#gamma#gamma} (GeV)");
	plot->SetTitle("");
	data->plotOn(plot,Binning(80),Invisible());
  ///start extra bit for ratio plot///
  RooHist *plotdata = (RooHist*)plot->getObject(plot->numItems()-1);
  // enf extra bit for ratio plot///
	TObject *dataLeg = (TObject*)plot->getObject(plot->numItems()-1);
	mpdf->getCurrentPdf()->plotOn(plot,LineColor(kRed),LineWidth(2));
	RooCurve *nomBkgCurve = (RooCurve*)plot->getObject(plot->numItems()-1);

	leg->AddEntry(dataLeg,"Data","LEP");
	leg->AddEntry(nomBkgCurve,"Bkg Fit","L");

	// Bands
	TGraphAsymmErrors *oneSigmaBand = new TGraphAsymmErrors();
	TGraphAsymmErrors *oneSigmaBand_r = new TGraphAsymmErrors();
	oneSigmaBand->SetName(Form("onesigma_%s",catname.c_str()));
	oneSigmaBand_r->SetName(Form("onesigma_%s_r",catname.c_str()));
	TGraphAsymmErrors *twoSigmaBand = new TGraphAsymmErrors();
	TGraphAsymmErrors *twoSigmaBand_r = new TGraphAsymmErrors();
	twoSigmaBand->SetName(Form("twosigma_%s",catname.c_str()));
	twoSigmaBand_r->SetName(Form("twosigma_%s_r",catname.c_str()));

	cout<< "[INFO] " << "Plot has " << plot->GetXaxis()->GetNbins() << " bins" << endl;
	if (doBands) {
		int p=0;
		for (double mass=double(mhLow); mass<double(mhHigh)+massStep; mass+=massStep) {
			//for (int i=1; i<(plot->GetXaxis()->GetNbins()+1); i++){
			double lowedge = mass-0.5;
			double upedge = mass+0.5;
			double center = mass;
			/*
				 double lowedge = plot->GetXaxis()->GetBinLowEdge(i);
				 double upedge = plot->GetXaxis()->GetBinUpEdge(i);
				 double center = plot->GetXaxis()->GetBinCenter(i);
				 */
			double nomBkg = nomBkgCurve->interpolate(center);
			//double nomBkg_perGeV = (nomBkgCurve->Integral(center-higgsResolution_,center+higgsResolution_))/2*higgsResolution_;
			double nomBkg_perGeV = (nomBkgCurve->average(center-higgsResolution_,center+higgsResolution_));
      double nllBest = getNormTermNll(mgg,data,mpdf,mcat,nomBkg,lowedge,upedge);

			// sensible range
			double lowRange = TMath::Max(0.,nomBkg - 3*TMath::Sqrt(nomBkg));
			double highRange = nomBkg + 3*TMath::Sqrt(nomBkg);
       std::cout << "[FOR TABLE] ,"<<flashggCats_[cat]<<","<< mass << ","<<nomBkg_perGeV<<", assuming resolution of " << higgsResolution_ << std::endl;
			if (verbose_) cout<< "[INFO] " << "mgg: " << center << " nomBkg: " << nomBkg << " lR: " << lowRange << " hR: " << highRange << endl;

			double errLow1Value,errHigh1Value,errLow2Value,errHigh2Value;
			// cant handle having 0 events
			if (nomBkg<1.e-5) {
				errLow1Value = 0.;
				errLow2Value = 0.;
				if (verbose_) cout << "[INFO] "<< "errHigh1" << endl;
				errHigh1Value = guessNew(mgg,mpdf,mcat,data,nomBkg,nllBest,highRange,lowedge,upedge,1.,nllTolerance);
				if (verbose_) cout << "[INFO] "<< "errHigh2" << endl;
				errHigh2Value = guessNew(mgg,mpdf,mcat,data,nomBkg,nllBest,highRange,lowedge,upedge,4.,nllTolerance);
			}
			else {
				// error calc algo
				if (verbose_) cout<< "[INFO] " << "errLow1" << endl;
				errLow1Value = guessNew(mgg,mpdf,mcat,data,nomBkg,nllBest,lowRange,lowedge,upedge,1.,nllTolerance);
				if (verbose_) cout<< "[INFO] " << "errLow2" << endl;
				errLow2Value = guessNew(mgg,mpdf,mcat,data,nomBkg,nllBest,lowRange,lowedge,upedge,4.,nllTolerance);
				if (verbose_) cout<< "[INFO] " << "errHigh1" << endl;
				errHigh1Value = guessNew(mgg,mpdf,mcat,data,nomBkg,nllBest,highRange,lowedge,upedge,1.,nllTolerance);
				if (verbose_) cout<< "[INFO] " << "errHigh2" << endl;
				errHigh2Value = guessNew(mgg,mpdf,mcat,data,nomBkg,nllBest,highRange,lowedge,upedge,4.,nllTolerance);
			}

			double errLow1 = nomBkg - errLow1Value;
			double errHigh1 = errHigh1Value - nomBkg;
			double errLow2 = nomBkg - errLow2Value;
			double errHigh2 = errHigh2Value - nomBkg;

			oneSigmaBand->SetPoint(p,center,nomBkg);
			oneSigmaBand_r->SetPoint(p,center,0);
			twoSigmaBand->SetPoint(p,center,nomBkg);
			twoSigmaBand_r->SetPoint(p,center,0);
			oneSigmaBand->SetPointError(p,0.,0.,errLow1,errHigh1);
			oneSigmaBand_r->SetPointError(p,0.,0.,errLow1,errHigh1);
			twoSigmaBand->SetPointError(p,0.,0.,errLow2,errHigh2);
			twoSigmaBand_r->SetPointError(p,0.,0.,errLow2,errHigh2);

			cout<< "[INFO] " << "mgg: " << center << " nomBkg: " << nomBkg << " +/- 1 (2) sig -- +" << errHigh1 << "(" << errHigh2 << ")" << " - " << errLow1 << "(" << errLow2 << ")" << endl;

			if (makeCrossCheckProfPlots) {
				// literal profile
				TCanvas *temp = new TCanvas();
        temp->SetTickx(); temp->SetTicky();
				TGraph *profCurve = new TGraph();
				int p2=0;
				for (double scanVal=0.9*errLow2Value; scanVal<1.1*errHigh2Value; scanVal+=1){
					double nll = getNormTermNll(mgg,data,mpdf,mcat,scanVal,lowedge,upedge)-nllBest;
					profCurve->SetPoint(p2,scanVal,nll);
					p2++;
				}
				profCurve->GetXaxis()->SetRangeUser(0.9*errLow2Value,1.1*errHigh2Value);
				profCurve->GetYaxis()->SetRangeUser(0.,5.);
				profCurve->Draw("ALP");
				TLine line;
				line.SetLineWidth(2);
				line.SetLineStyle(kDashed);
				line.SetLineColor(kRed);
				line.DrawLine(nomBkg-errLow1,0.,nomBkg-errLow1,1.);
				line.DrawLine(nomBkg+errHigh1,0.,nomBkg+errHigh1,1.);
				line.DrawLine(0.9*errLow2Value,1.,1.1*errHigh2Value,1.);
				line.SetLineColor(kBlue);
				line.DrawLine(nomBkg-errLow2,0.,nomBkg-errLow2,4.);
				line.DrawLine(nomBkg+errHigh2,0.,nomBkg+errHigh2,4.);
				line.DrawLine(0.9*errLow2Value,4.,1.1*errHigh2Value,4.);
				temp->Print(Form("%s/normProfs/%s_mass%6.2f.pdf",outDir.c_str(),catname.c_str(),center));
				delete profCurve;
				delete temp;
			}
			p++;
		}
		cout << endl;
		}

		outFile->cd();
		oneSigmaBand->Write();
		twoSigmaBand->Write();
		nomBkgCurve->Write();
		outWS->import(*mcat);
		outWS->import(*mpdf);
		outWS->import(*data);

		TCanvas *canv = new TCanvas("c","",800,800);
  ///start extra bit for ratio plot///
  bool doRatioPlot_=1;
  TPad *pad1 = new TPad("pad1","pad1",0,0.25,1,1);
  TPad *pad2 = new TPad("pad2","pad2",0,0,1,0.35);
  pad1->SetBottomMargin(0.18);
  pad2->SetTopMargin(0.00001);
  pad2->SetBottomMargin(0.25);
  pad1->Draw();
  pad2->Draw();
  pad1->cd();
  // enf extra bit for ratio plot///
    canv->SetTickx(); canv->SetTicky();
		//RooRealVar *lumi = (RooRealVar*)inWS->var("IntLumi");
		RooRealVar *lumi = intLumi_;
		plot->Draw();

		if (!unblind) {
			mgg->setRange("unblind_up",135,180);
			mgg->setRange("unblind_down",100,115);
			data->plotOn(plot,Binning(80),CutRange("unblind_down,unblind_up"));
		}
		else {
			data->plotOn(plot,Binning(80));
		}

		if (doBands) {
			twoSigmaBand->SetLineColor(kYellow);
			twoSigmaBand->SetFillColor(kYellow);
			twoSigmaBand->SetMarkerColor(kYellow);
			twoSigmaBand->Draw("L3 SAME");
			oneSigmaBand->SetLineColor(kGreen);
			oneSigmaBand->SetFillColor(kGreen);
			oneSigmaBand->SetMarkerColor(kGreen);
			oneSigmaBand->Draw("L3 SAME");
			leg->AddEntry(oneSigmaBand,"#pm1#sigma","F");
			leg->AddEntry(twoSigmaBand,"#pm2#sigma","F");
			twoSigmaBand_r->SetLineColor(kYellow);
			twoSigmaBand_r->SetFillColor(kYellow);
			twoSigmaBand_r->SetMarkerColor(kYellow);
			oneSigmaBand_r->SetLineColor(kGreen);
			oneSigmaBand_r->SetFillColor(kGreen);
			oneSigmaBand_r->SetMarkerColor(kGreen);
		}

		if (doSignal){
      int SignalType=0;
			TFile *sigFile = TFile::Open(sigFileName.c_str());
		//	RooWorkspace *w_sig = (RooWorkspace*)sigFile->Get("wsig_7TeV");
	    WSTFileWrapper *w_sig = new WSTFileWrapper(sigFileName,"wsig_13TeV");
	//		if (!w_sig) w_sig = (RooWorkspace*)sigFile->Get("wsig_8TeV");
	//		if (!w_sig) w_sig = (RooWorkspace*)sigFile->Get("wsig_13TeV");
			if (!w_sig) {
	    WSTFileWrapper *w_sig = new WSTFileWrapper(sigFileName,"cms_hgg_workspace");
      //w_sig = (RooWorkspace*)sigFile->Get("cms_hgg_workspace");
      if (w_sig) SignalType=1;
      }
			if (!w_sig) {
				cout << "[INFO] " << "Signal workspace not found" << endl;
				exit(0);
			}
			if (SignalType==1) {
				TH1F::SetDefaultSumw2();
				TH1F *gghHist = (TH1F*)sigFile->Get(Form("th1f_sig_ggh_mass_m125_%s",catname.c_str()));
				TH1F *vbfHist = (TH1F*)sigFile->Get(Form("th1f_sig_vbf_mass_m125_%s",catname.c_str()));
				TH1F *wzhHist = (TH1F*)sigFile->Get(Form("th1f_sig_wzh_mass_m125_%s",catname.c_str()));
				TH1F *tthHist = (TH1F*)sigFile->Get(Form("th1f_sig_tth_mass_m125_%s",catname.c_str()));
				TH1F *whHist = (TH1F*)sigFile->Get(Form("th1f_sig_wh_mass_m125_%s",catname.c_str()));
				TH1F *zhHist = (TH1F*)sigFile->Get(Form("th1f_sig_zh_mass_m125_%s",catname.c_str()));
				TH1F *sigHist = (TH1F*)gghHist->Clone(Form("th1f_sig_mass_m125_%s",catname.c_str()));
				sigHist->Add(gghHist);
				sigHist->Add(vbfHist);
				if (wzhHist) sigHist->Add(wzhHist);
				if (whHist) sigHist->Add(whHist);
				if (zhHist) sigHist->Add(zhHist);
				sigHist->Add(tthHist);
				sigHist->SetLineColor(kBlue);
				sigHist->SetLineWidth(3);
				sigHist->SetFillColor(38);
				sigHist->SetFillStyle(3001);
				sigHist->Draw("HISTsame");
				leg->AddEntry(sigHist,"Sig model m_{H}=125GeV","LF");
				outFile->cd();
				sigHist->Write();
				if (verbose_) cout<< "[INFO] "  << "Plotted binned signal with " << sigHist->Integral() << " entries" << endl;
				return (0); //FIXME
			}
			else {
				RooRealVar *MH = (RooRealVar*)w_sig->var("MH");
				if (!MH) MH = (RooRealVar*)w_sig->var("CMS_hgg_mass");
				RooAbsPdf *sigPDF = (RooAbsPdf*)w_sig->pdf(Form("sigpdfrel%s_allProcs",catname.c_str()));
				MH->setVal(mhvalue_);
				sigPDF->plotOn(plot,Normalization(1.0,RooAbsReal::RelativeExpected),LineColor(kBlue),LineWidth(3));
				sigPDF->plotOn(plot,Normalization(1.0,RooAbsReal::RelativeExpected),LineColor(kBlue),LineWidth(3),FillColor(38),FillStyle(3001),DrawOption("F"));
				std::cout << "[INFO] expected number of events in signal PDF " << sigPDF->expectedEvents(*MH) << std::endl;	
				//sigPDF->plotOn(plot,Normalization(0.001*lumi->getVal()/*get intlumi (/fb) from ws, and divide by 100 for /pb */,RooAbsReal::RelativeExpected),LineColor(kBlue),LineWidth(3));
				//sigPDF->plotOn(plot,Normalization(0.001*lumi->getVal(),RooAbsReal::RelativeExpected),LineColor(kBlue),LineWidth(3),FillColor(38),FillStyle(3001),DrawOption("F"));
				sigPDF->plotOn(plotLC,Normalization(1.0,RooAbsReal::RelativeExpected),LineColor(kBlue),LineWidth(3));
				TObject *sigLeg = (TObject*)plot->getObject(plot->numItems()-1);
				leg->AddEntry(sigLeg,Form("Sig model m_{H}=%.1fGeV",MH->getVal()),"L");
				outWS->import(*sigPDF);
			}
		}

		plot->Draw("same");
		leg->Draw("same");

		TLatex *latex = new TLatex();	
		latex->SetTextSize(0.045);
		latex->SetNDC();
		TLatex *cmslatex = new TLatex();
		cmslatex->SetTextSize(0.03);
		cmslatex->SetNDC();
		std::cout << "[INFO] intLumi " << intLumi << std::endl;
		//cmslatex->drawlatex(0.2,0.85,form("#splitline{cms preliminary}{#sqrt{s} = %dtev l = %2.3ffb^{-1}}",sqrts,intlumi));
		//cmslatex->DrawLatex(0.25,0.85,Form("#splitline{}{#sqrt{s} = %dTeV L = %2.1ffb^{-1}}",sqrts,intLumi));
    TString catLabel_humanReadable = catLabel;
    catLabel_humanReadable.ReplaceAll("_"," ");
    catLabel_humanReadable.ReplaceAll("UntaggedTag","Untagged");
    catLabel_humanReadable.ReplaceAll("VBFTag","VBF Tag");
    catLabel_humanReadable.ReplaceAll("TTHLeptonicTag","TTH Leptonic Tag");
    catLabel_humanReadable.ReplaceAll("TTHHadronicTag","TTH Hadronic Tag");
		latex->DrawLatex(0.15,0.85,catLabel_humanReadable);
		outWS->import(*lumi,RecycleConflictNodes());

		if (unblind) plot->SetMinimum(0.0001);
		plot->GetYaxis()->SetTitleOffset(1.3);
		canv->Modified();
		canv->Update();
  ///start extra bit for ratio plot///
  //TH1D *hbplottmp = (TH1D*) pdf->createHistogram("hbplottmp",*mass,Binning(80,100,180));
  //hbplottmp->Scale(plotdata->Integral());
  //hbplottmp->Draw("same");
  int npoints = plotdata->GetN();
  double xtmp,ytmp;//
  int point =0;
  TGraphAsymmErrors *hdatasub = new TGraphAsymmErrors(npoints);
  //hdatasub->SetMarkerSize(defmarkersize);
  for (int ipoint=0; ipoint<npoints; ++ipoint) {
  //double bkgval = hbplottmp->GetBinContent(ipoint+1);
  plotdata->GetPoint(ipoint, xtmp,ytmp);
  double bkgval = nomBkgCurve->interpolate(xtmp);
  if (!unblind) {
   if ((xtmp > 115 ) && ( xtmp < 135) ) continue;
  }
  //std::cout << "[INFO] plotdata->Integral() " <<  plotdata->Integral() << " ( bins " << npoints  << ") hbkgplots[i]->Integral() " << hbplottmp->Integral() << " (bins " << hbplottmp->GetNbinsX() << std::endl;
 double errhi = plotdata->GetErrorYhigh(ipoint);
 double errlow = plotdata->GetErrorYlow(ipoint);
       
 //std::cout << "[INFO]  Channel " << name  << " errhi " << errhi << " errlow " << errlow  << std::endl;
 std::cout << "[INFO] Channel  " << " setting point " << point <<" : xtmp "<< xtmp << "  ytmp " << ytmp << " bkgval  " << bkgval << " ytmp-bkgval " << ytmp-bkgval << std::endl;
 bool drawZeroBins_ =1;
 if (!drawZeroBins_) if(fabs(ytmp)<1e-5) continue; 
 hdatasub->SetPoint(point,xtmp,ytmp-bkgval);
 hdatasub->SetPointError(point,0.,0.,errlow,errhi );
 point++;
  } 
  pad2->cd();
  TH1 *hdummy = new TH1D("hdummyweight","",80,100,180);
  hdummy->SetMaximum(hdatasub->GetHistogram()->GetMaximum()+1);
  hdummy->SetMinimum(hdatasub->GetHistogram()->GetMinimum()-1);
  hdummy->GetYaxis()->SetTitle("data - best fit PDF");
  hdummy->GetYaxis()->SetTitleSize(0.12);
  hdummy->GetXaxis()->SetTitle("m_{#gamma#gamma} (GeV)");
  hdummy->GetXaxis()->SetTitleSize(0.12);
  hdummy->Draw("HIST");
	if (doBands) twoSigmaBand_r->Draw("L3 SAME");
	if (doBands) oneSigmaBand_r->Draw("L3 SAME");
  hdummy->GetYaxis()->SetNdivisions(808);

  TLine *line3 = new TLine(100,0.,180,0.);
  line3->SetLineColor(kRed);
  //line3->SetLineStyle(kDashed);
  line3->SetLineWidth(4.0);
  line3->Draw();
  hdatasub->Draw("PESAME");
  // enf extra bit for ratio plot///
    CMS_lumi( canv, 4, 0);
		canv->Print(Form("%s/bkgplot_%s.pdf",outDir.c_str(),catname.c_str()));
		canv->Print(Form("%s/bkgplot_%s.png",outDir.c_str(),catname.c_str()));
		canv->Print(Form("%s/bkgplot_%s.C",outDir.c_str(),catname.c_str()));
		canv->SetName(Form("bkgplot_%s",catname.c_str()));
		outFile->cd();
		canv->Write();
		outWS->Write();
		outFile->Close();

		inFile->Close();

		return 0;
	}

