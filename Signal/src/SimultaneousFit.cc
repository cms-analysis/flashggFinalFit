#include <fstream>

#include "TCanvas.h"
#include "TH2.h"
#include "TMath.h"
#include "TLatex.h"
#include "RooPlot.h"
#include "RooChi2Var.h"
#include "RooMinuit.h"
#include "RooPolyVar.h"
#include "TColor.h"
#include "RooFormulaVar.h"
#include "RooAddition.h"
#include "RooMsgService.h"
#include "TPaveText.h"
#include "TGraphErrors.h"
#include "TAxis.h"
#include "TMultiGraph.h"

#include "boost/lexical_cast.hpp"

#include "../interface/SimultaneousFit.h"
#include "../interface/LCRooChi2Var.h"
#include "../interface/LCRooAddition.h"

using namespace std;
using namespace RooFit;

//This class is similar to the initialFit class but instead of doing each mass point separtely and then using teh LinearInterp class to interpoalte, it fits all the mass points at once assuming that the functional form's parameters are themsleves functions of MH
SimultaneousFit::SimultaneousFit(RooRealVar *massVar, RooRealVar *MHvar, int mhLow, int mhHigh, vector<int> skipMasses, bool binnedFit, int bins, std::vector<int> massList, string cat, string proc, string outdir, int maxOrder ):
  mass(massVar),
  MH(MHvar),
  mhLow_(mhLow),
  mhHigh_(mhHigh),
	skipMasses_(skipMasses),
  verbosity_(0),
  binnedFit_(binnedFit),
  bins_(bins),
  cat_(cat),
  proc_(proc),
  outdir_(outdir),
  maxOrder_(maxOrder)
{ 

  listOfPolyVars_ = new RooArgSet();
  if (massList.size()==0){
    allMH_ = getAllMH();
  }else{
    allMH_ = massList;
  }
}

SimultaneousFit::~SimultaneousFit(){}

bool SimultaneousFit::skipMass(int mh){
	for (vector<int>::iterator it=skipMasses_.begin(); it!=skipMasses_.end(); it++) {
		if (*it==mh) return true;
	}
	return false;
}

vector<int> SimultaneousFit::getAllMH(){
  vector<int> result;
  for (int m=mhLow_; m<=mhHigh_; m+=5){
		if (skipMass(m)) continue;
    if (verbosity_>=1) cout << "[INFO] Simulatenous Fit - Adding mass: " << m << endl;
    result.push_back(m);
  }
  return result;
}

void SimultaneousFit::setVerbosity(int v){
  if (v<2) {
    RooMsgService::instance().setGlobalKillBelow(RooFit::ERROR);
    RooMsgService::instance().setSilentMode(true);
  }
  verbosity_=v;
}

// this takes individual datasets and reweights them such that the sum of weights is 1
RooDataSet* SimultaneousFit::normaliseDatasets( RooDataSet* data){
   
  //prepare weight variables
  double weight =0;
  RooRealVar* weightVar = new RooRealVar("weight","weight",-10000,10000);
  RooRealVar* dZ = new RooRealVar("dZ","dZ",-10000,10000);
  double runningSum=0;
  double runningSum2=0;
  double factor = 1.0/data->sumEntries();
  // prepare the holder for the merged data, which is a 2D dataset of mass and MH
  RooDataSet* result = (RooDataSet*) data->emptyClone(); 
    
    //for each mass point, loop through the entries in the dataset
    for (int iEntry=0; iEntry <data->numEntries() ; iEntry++){
      
      //set the mass to the value of the entry in the dataset
      mass->setVal(data->get(iEntry)->getRealValue(mass->GetName()));
      dZ->setVal(data->get(iEntry)->getRealValue("dZ"));
      
      //want to normalise the datasets to 1 for the simulatenous fit.
      weight = ((float) data->weight())/((float) data->sumEntries()); 
      runningSum = runningSum + data->weight();
      runningSum2 = runningSum2 + weight;
      weightVar->setVal( factor *data->weight());
      
      // add a row to the dataset for this entry
      result->add(RooArgSet(*mass,*weightVar),weightVar->getVal());
    }
  
  //and simply return the merged dataset
  return result;
}

// similar to SimultaneousFit::normaliseDatasets but takes seevral datasets at different mass points and turns them into a 2D dataset in mgg vs MH where each dataset was normalised to 1.0
RooDataSet* SimultaneousFit::mergeNormalisedDatasets(map<int,RooDataSet*> data){
  
  // prepare the holder for the merged data, which is a 2D dataset of mass and MH
  RooRealVar* weightVar = new RooRealVar("weight","weight",-10000,10000);
  RooDataSet* result = new RooDataSet("mergedDataset","mergedDataset",RooArgSet(*mass,*MH,*weightVar),"weight");
  
  //loop over vector of datasets for different MH values
  for (map<int,RooDataSet*>::iterator dataIt=data.begin(); dataIt!=data.end(); dataIt++){
    
    double weight =0;
    double factor = 1.0/dataIt->second->sumEntries();
    
    //for each mass point, loop through the entries in the dataset
    for (int iEntry=0; iEntry<dataIt->second->numEntries() ; iEntry++){
      
      //set the mass to the value of the entry in the dataset
      mass->setVal(dataIt->second->get(iEntry)->getRealValue(mass->GetName()));
      
      //want to normalise the datasets to 1 for the simulatenous fit.
      weightVar->setVal( factor * dataIt->second->weight());

      //set the MH to the relevant value for this dataste
      MH->setVal(dataIt->first);
      
      // add a row to the dataset for this entry
      result->add(RooArgSet(*mass,*MH,*weightVar),weightVar->getVal());
    }
  }
  //and simply return the merged dataset
  return result;
}

void SimultaneousFit::setDatasets(map<int,RooDataSet*> data){
  datasets = data; // original dataset or a replacement one if needed.
}

void SimultaneousFit::setDatasetsSTD(map<int,RooDataSet*> data){
  datasetsSTD = data; //original dataset, not the replacement one!!
}

void SimultaneousFit::addDataset(int mh, RooDataSet *data){
  assert(data);
  datasets.insert(pair<int,RooDataSet*>(mh,data));
}

// build a signal model comprising of a DCB and 1 Guassian with the same mean
void SimultaneousFit::buildDCBplusGaussian(string name, bool recursive){
    // the "Order" refers to the order of the polynomial describing the dependence of the parameters on MH
    
    // holders for the various coeffs, params and PDFs
    RooArgList *pdfs_order0 = new RooArgList();
    RooArgList *pdfs_order1 = new RooArgList();
    RooArgList *pdfs_order2 = new RooArgList();
    RooArgList *coeffs_order0 = new RooArgList();
    RooArgList *coeffs_order1 = new RooArgList();
    RooArgList *coeffs_order2 = new RooArgList();
    map<string,RooRealVar*> tempFitParams;
    map<string,RooAbsReal*> tempFitUtils;
    map<string,RooAbsPdf*> tempPdfsMap_order0;
    map<string,RooAbsPdf*> tempPdfsMap_order1;
    map<string,RooAbsPdf*> tempPdfsMap_order2;

    // start defining params
    RooFormulaVar *dMH = new RooFormulaVar(Form("dMH"),Form("dMH"),"@0-125.0",RooArgList(*MH));
    // the parmas p0, p1, p2 are the params which codify the polynomial dependence of dm_dcb on dMH
    RooRealVar *dm_dcb_p0 = new RooRealVar(Form("dm_dcb_p0"),Form("dm_dcb_p0"),0.1,-5.0,5.0);
    RooRealVar *dm_dcb_p1 = new RooRealVar(Form("dm_dcb_p1"),Form("dm_dcb_p1"),0.0,-0.1,0.1);
    RooRealVar *dm_dcb_p2 = new RooRealVar(Form("dm_dcb_p2"),Form("dm_dcb_p2"),0.0,-0.001,0.001);
    RooPolyVar *dm_dcb_order0 = new RooPolyVar(Form("dm_dcb_order0"),Form("dm_dcb_order0"),*dMH,RooArgList(*dm_dcb_p0)); //y=a
    RooPolyVar *dm_dcb_order1 = new RooPolyVar(Form("dm_dcb_order1"),Form("dm_dcb_order1"),*dMH,RooArgList(*dm_dcb_p0,*dm_dcb_p1)); //y=a+bx
    RooPolyVar *dm_dcb_order2 = new RooPolyVar(Form("dm_dcb_order2"),Form("dm_dcb_order2"),*dMH,RooArgList(*dm_dcb_p0,*dm_dcb_p1,*dm_dcb_p2)); //y=a+bx+c*x*x
    RooFormulaVar *mean_dcb_order0 = new RooFormulaVar(Form("mean_dcb_order0"),Form("mean_dcb_order0"),"((@0+@1))",RooArgList(*MH,*dm_dcb_order0));
    RooFormulaVar *mean_dcb_order1 = new RooFormulaVar(Form("mean_dcb_order1"),Form("mean_dcb_order1"),"((@0+@1))",RooArgList(*MH,*dm_dcb_order1));
    RooFormulaVar *mean_dcb_order2 = new RooFormulaVar(Form("mean_dcb_order2"),Form("mean_dcb_order2"),"((@0+@1))",RooArgList(*MH,*dm_dcb_order2));
    RooRealVar *sigma_dcb_p0 = new RooRealVar(Form("sigma_dcb_p0"),Form("sigma_dcb_p0"),2.0,1.0,20.0);
    RooRealVar *sigma_dcb_p1 = new RooRealVar(Form("sigma_dcb_p1"),Form("sigma_dcb_p1"),0.0,-0.1,0.1);
    RooRealVar *sigma_dcb_p2 = new RooRealVar(Form("sigma_dcb_p2"),Form("sigma_dcb_p2"),0.0,-0.001,0.001);
    //RooFormulaVar *sigma = new RooFormulaVar(Form("sigma_dcb",g),Form("sigma_dcb",g),"((@0-125.0)*@1+@2)",RooArgList(*MH,*sigma_p1,*sigma_p0));
    //RooRealVar *sigma = new RooRealVar(Form("sigma_dcb",g),Form("sigma_dcb",g),-5);
    RooPolyVar *sigma_dcb_order0 = new RooPolyVar(Form("sigma_dcb_order0"),Form("sigma_dcb_order0"),*dMH,RooArgList(*sigma_dcb_p0));
    RooPolyVar *sigma_dcb_order1 = new RooPolyVar(Form("sigma_dcb_order1"),Form("sigma_dcb_order1"),*dMH,RooArgList(*sigma_dcb_p0,*sigma_dcb_p1));
    RooPolyVar *sigma_dcb_order2 = new RooPolyVar(Form("sigma_dcb_order2"),Form("sigma_dcb_order2"),*dMH,RooArgList(*sigma_dcb_p0,*sigma_dcb_p1,*sigma_dcb_p2));

    RooRealVar *n1_dcb_p0 = new RooRealVar(Form("n1_dcb_p0"),Form("n1_dcb_p0"),20.,2.00001,500);
    RooRealVar *n1_dcb_p1 = new RooRealVar(Form("n1_dcb_p1"),Form("n1_dcb_p1"),0.0,-0.1,0.1);
    RooRealVar *n1_dcb_p2 = new RooRealVar(Form("n1_dcb_p2"),Form("n1_dcb_p2"),0.0,-0.001,0.001);
    RooPolyVar *n1_dcb_order0 = new RooPolyVar(Form("n1_dcb_order0"),Form("n1_dcb_order0"),*dMH,RooArgList(*n1_dcb_p0));
    RooPolyVar *n1_dcb_order1 = new RooPolyVar(Form("n1_dcb_order1"),Form("n1_dcb_order1"),*dMH,RooArgList(*n1_dcb_p0,*n1_dcb_p1));
    RooPolyVar *n1_dcb_order2 = new RooPolyVar(Form("n1_dcb_order2"),Form("n1_dcb_order2"),*dMH,RooArgList(*n1_dcb_p0,*n1_dcb_p1,*n1_dcb_p2));

    RooRealVar *n2_dcb_p0 = new RooRealVar(Form("n2_dcb_p0"),Form("n2_dcb_p0"),20.,2.00001,500);
    RooRealVar *n2_dcb_p1 = new RooRealVar(Form("n2_dcb_p1"),Form("n2_dcb_p1"),0.0,-0.1,0.1);
    RooRealVar *n2_dcb_p2 = new RooRealVar(Form("n2_dcb_p2"),Form("n2_dcb_p2"),0.0,-0.001,0.001);
    RooPolyVar *n2_dcb_order0 = new RooPolyVar(Form("n2_dcb_order0"),Form("n2_dcb_order0"),*dMH,RooArgList(*n2_dcb_p0));
    RooPolyVar *n2_dcb_order1 = new RooPolyVar(Form("n2_dcb_order1"),Form("n2_dcb_order1"),*dMH,RooArgList(*n2_dcb_p0,*n2_dcb_p1));
    RooPolyVar *n2_dcb_order2 = new RooPolyVar(Form("n2_dcb_order2"),Form("n2_dcb_order2"),*dMH,RooArgList(*n2_dcb_p0,*n2_dcb_p1,*n2_dcb_p2));

    RooRealVar *a1_dcb_p0 = new RooRealVar(Form("a1_dcb_p0"),Form("a1_dcb_p0"),5.,1.0,100.0);
    RooRealVar *a1_dcb_p1 = new RooRealVar(Form("a1_dcb_p1"),Form("a1_dcb_p1"),0.0,-0.1,0.1);
    RooRealVar *a1_dcb_p2 = new RooRealVar(Form("a1_dcb_p2"),Form("a1_dcb_p2"),0.0,-0.001,0.001);
    RooPolyVar *a1_dcb_order0 = new RooPolyVar(Form("a1_dcb_order0"),Form("a1_dcb_order0"),*dMH,RooArgList(*a1_dcb_p0));
    RooPolyVar *a1_dcb_order1 = new RooPolyVar(Form("a1_dcb_order1"),Form("a1_dcb_order1"),*dMH,RooArgList(*a1_dcb_p0,*a1_dcb_p1));
    RooPolyVar *a1_dcb_order2 = new RooPolyVar(Form("a1_dcb_order2"),Form("a1_dcb_order2"),*dMH,RooArgList(*a1_dcb_p0,*a1_dcb_p1,*a1_dcb_p2));
    RooRealVar *a2_dcb_p0 = new RooRealVar(Form("a2_dcb_p0"),Form("a2_dcb_p0"),5.,1.0,20.0);
    RooRealVar *a2_dcb_p1 = new RooRealVar(Form("a2_dcb_p1"),Form("a2_dcb_p1"),0.0,-0.1,0.1);
    RooRealVar *a2_dcb_p2 = new RooRealVar(Form("a2_dcb_p2"),Form("a2_dcb_p2"),0.0,-0.001,0.001);
    RooPolyVar *a2_dcb_order0 = new RooPolyVar(Form("a2_dcb_order0"),Form("a2_dcb_order0"),*dMH,RooArgList(*a2_dcb_p0));
    RooPolyVar *a2_dcb_order1 = new RooPolyVar(Form("a2_dcb_order1"),Form("a2_dcb_order1"),*dMH,RooArgList(*a2_dcb_p0,*a2_dcb_p1));
    RooPolyVar *a2_dcb_order2 = new RooPolyVar(Form("a2_dcb_order2"),Form("a2_dcb_order2"),*dMH,RooArgList(*a2_dcb_p0,*a2_dcb_p1,*a2_dcb_p2));

    RooAbsPdf *dcb_order0 = new RooDoubleCBFast(Form("dcb_order0"),Form("dcb_order0"), *mass,*mean_dcb_order0,*sigma_dcb_order0, *a1_dcb_order0, *n1_dcb_order0, *a2_dcb_order0, *n2_dcb_order0);
    RooAbsPdf *dcb_order1 = new RooDoubleCBFast(Form("dcb_order1"),Form("dcb_order1"), *mass,*mean_dcb_order1,*sigma_dcb_order1, *a1_dcb_order1, *n1_dcb_order1, *a2_dcb_order1, *n2_dcb_order1);
    RooAbsPdf *dcb_order2 = new RooDoubleCBFast(Form("dcb_order2"),Form("dcb_order2"), *mass,*mean_dcb_order2,*sigma_dcb_order2, *a1_dcb_order2, *n1_dcb_order2, *a2_dcb_order2, *n2_dcb_order2);
    tempPdfsMap_order0.insert(pair<string,RooAbsPdf*>(string(dcb_order0->GetName()),dcb_order0));
    tempPdfsMap_order1.insert(pair<string,RooAbsPdf*>(string(dcb_order1->GetName()),dcb_order1));
    tempPdfsMap_order2.insert(pair<string,RooAbsPdf*>(string(dcb_order2->GetName()),dcb_order2));
    pdfs_order0->add(*dcb_order0);
    pdfs_order1->add(*dcb_order1);
    pdfs_order2->add(*dcb_order2);
    listOfPolyVars_->add(*dm_dcb_order0);
    listOfPolyVars_->add(*mean_dcb_order0);
    listOfPolyVars_->add(*sigma_dcb_order0);
    listOfPolyVars_->add(*a1_dcb_order0);
    listOfPolyVars_->add(*a2_dcb_order0);
    listOfPolyVars_->add(*n1_dcb_order0);
    listOfPolyVars_->add(*n2_dcb_order0);
    listOfPolyVars_->add(*dm_dcb_order1);
    listOfPolyVars_->add(*mean_dcb_order1);
    listOfPolyVars_->add(*sigma_dcb_order1);
    listOfPolyVars_->add(*a1_dcb_order1);
    listOfPolyVars_->add(*a2_dcb_order1);
    listOfPolyVars_->add(*n1_dcb_order1);
    listOfPolyVars_->add(*n2_dcb_order1);
    listOfPolyVars_->add(*dm_dcb_order2);
    listOfPolyVars_->add(*mean_dcb_order2);
    listOfPolyVars_->add(*sigma_dcb_order2);
    listOfPolyVars_->add(*a1_dcb_order2);
    listOfPolyVars_->add(*a2_dcb_order2);
    listOfPolyVars_->add(*n1_dcb_order2);
    listOfPolyVars_->add(*n2_dcb_order2);

    //RooRealVar *dm_gaus_p0 = new RooRealVar(Form("dm_gaus_p0"),Form("dm_gaus_p0"),0.1,-5.0,5.0);
    //RooRealVar *dm_gaus_p1 = new RooRealVar(Form("dm_gaus_p1"),Form("dm_gaus_p1"),0.0,-0.1,0.1);
    //RooRealVar *dm_gaus_p2 = new RooRealVar(Form("dm_gaus_p2"),Form("dm_gaus_p2"),0.0,-0.001,0.001);
    //RooPolyVar *dm_gaus_order0 = new RooPolyVar(Form("dm_gaus_order0"),Form("dm_gaus_order0"),*dMH,RooArgList(*dm_gaus_p0)); //y=a
    //RooPolyVar *dm_gaus_order1 = new RooPolyVar(Form("dm_gaus_order1"),Form("dm_gaus_order1"),*dMH,RooArgList(*dm_gaus_p0,*dm_gaus_p1)); //y=a+bx
    //RooPolyVar *dm_gaus_order2 = new RooPolyVar(Form("dm_gaus_order2"),Form("dm_gaus_order2"),*dMH,RooArgList(*dm_gaus_p0,*dm_gaus_p1,*dm_gaus_p2)); //y=a+bx+c*x*x
    //RooFormulaVar *mean_gaus_order0 = new RooFormulaVar(Form("mean_gaus_order0"),Form("mean_gaus_order0"),"((@0+@1))",RooArgList(*MH,*dm_gaus_order0));
    //RooFormulaVar *mean_gaus_order1 = new RooFormulaVar(Form("mean_gaus_order1"),Form("mean_gaus_order1"),"((@0+@1))",RooArgList(*MH,*dm_gaus_order1));
    //RooFormulaVar *mean_gaus_order2 = new RooFormulaVar(Form("mean_gaus_order2"),Form("mean_gaus_order2"),"((@0+@1))",RooArgList(*MH,*dm_gaus_order2));
    RooRealVar *sigma_gaus_p0 = new RooRealVar(Form("sigma_gaus_p0"),Form("sigma_gaus_p0"),2.0,1.0,3.0);
    RooRealVar *sigma_gaus_p1 = new RooRealVar(Form("sigma_gaus_p1"),Form("sigma_gaus_p1"),0.0,-0.1,0.1);
    RooRealVar *sigma_gaus_p2 = new RooRealVar(Form("sigma_gaus_p2"),Form("sigma_gaus_p2"),0.0,-0.001,0.001);
    RooPolyVar *sigma_gaus_order0 = new RooPolyVar(Form("sigma_gaus_order0"),Form("sigma_gaus_order0"),*dMH,RooArgList(*sigma_gaus_p0));
    RooPolyVar *sigma_gaus_order1 = new RooPolyVar(Form("sigma_gaus_order1"),Form("sigma_gaus_order1"),*dMH,RooArgList(*sigma_gaus_p0,*sigma_gaus_p1));
    RooPolyVar *sigma_gaus_order2 = new RooPolyVar(Form("sigma_gaus_order2"),Form("sigma_gaus_order2"),*dMH,RooArgList(*sigma_gaus_p0,*sigma_gaus_p1,*sigma_gaus_p2));
    RooAbsPdf *g_order0 = new RooGaussian(Form("gaus_order0"),Form("gaus_order0"),*mass,*mean_dcb_order0,*sigma_gaus_order0);
    RooAbsPdf *g_order1 = new RooGaussian(Form("gaus_order1"),Form("gaus_order1"),*mass,*mean_dcb_order1,*sigma_gaus_order1);
    RooAbsPdf *g_order2 = new RooGaussian(Form("gaus_order2"),Form("gaus_order2"),*mass,*mean_dcb_order2,*sigma_gaus_order2);
    
    tempPdfsMap_order0.insert(pair<string,RooAbsPdf*>(string(g_order0->GetName()),g_order0));
    tempPdfsMap_order1.insert(pair<string,RooAbsPdf*>(string(g_order1->GetName()),g_order1));
    tempPdfsMap_order2.insert(pair<string,RooAbsPdf*>(string(g_order2->GetName()),g_order2));
    pdfs_order0->add(*g_order0);
    pdfs_order1->add(*g_order1);
    pdfs_order2->add(*g_order2);

    //listOfPolyVars_->add(*dm_gaus_order0); // npt needed since DCB and Gaus have same mean
    //listOfPolyVars_->add(*dm_gaus_order1);
    //listOfPolyVars_->add(*dm_gaus_order2);
    listOfPolyVars_->add(*sigma_gaus_order0);
    listOfPolyVars_->add(*sigma_gaus_order1);
    listOfPolyVars_->add(*sigma_gaus_order2);
    RooRealVar *frac_p0 = new RooRealVar(Form("frac_p0"),Form("frac_p0"),0.5, 0.01,0.99);
    RooRealVar *frac_p1 = new RooRealVar(Form("frac_p1"),Form("frac_p1"),0.0,-0.05,0.05);
    RooRealVar *frac_p2 = new RooRealVar(Form("frac_p2"),Form("frac_p2"),0.0,-0.0001,0.0001);
    RooPolyVar *frac_order0 = new RooPolyVar(Form("frac_order0"),Form("frac_order0"),*dMH,RooArgList(*frac_p0));
    RooPolyVar *frac_order1 = new RooPolyVar(Form("frac_order1"),Form("frac_order1"),*dMH,RooArgList(*frac_p0,*frac_p1));
    RooPolyVar *frac_order2 = new RooPolyVar(Form("frac_order2"),Form("frac_order2"),*dMH,RooArgList(*frac_p0,*frac_p1,*frac_p2));
    
    // the frac is constrained to not be above 1 or below 0
    RooFormulaVar *frac_constrained_order0 = new RooFormulaVar(Form("frac_constrained_order0"),Form("frac_constrained_order0"),"(@0>0)*(@0<1)*@0+ (@0>1.0)*0.9999",RooArgList(*frac_order0));
    RooFormulaVar *frac_constrained_order1 = new RooFormulaVar(Form("frac_constrained_order1"),Form("frac_constrained_order1"),"(@0>0)*(@0<1)*@0+ (@0>1.0)*0.9999",RooArgList(*frac_order1));
    RooFormulaVar *frac_constrained_order2 = new RooFormulaVar(Form("frac_constrained_order2"),Form("frac_constrained_order2"),"(@0>0)*(@0<1)*@0+ (@0>1.0)*0.9999",RooArgList(*frac_order2));
    
    listOfPolyVars_->add(*frac_constrained_order0);
    listOfPolyVars_->add(*frac_constrained_order1);
    listOfPolyVars_->add(*frac_constrained_order2);
    coeffs_order0->add(*frac_constrained_order0);
    coeffs_order1->add(*frac_constrained_order1);
    coeffs_order2->add(*frac_constrained_order2);
    
    // in the end we have three possible PDFs - order 0, order 1 and order 2. The default is to use the order 1 but this can be changed at the runFits function
    RooAbsPdf *tempPdf_order0 = new RooAddPdf(Form("%s_order0",name.c_str()),Form("%s_order0",name.c_str()),*pdfs_order0,*coeffs_order0,recursive);
    RooAbsPdf *tempPdf_order1 = new RooAddPdf(Form("%s_order1",name.c_str()),Form("%s_order1",name.c_str()),*pdfs_order1,*coeffs_order1,recursive);
    RooAbsPdf *tempPdf_order2 = new RooAddPdf(Form("%s_order2",name.c_str()),Form("%s_order2",name.c_str()),*pdfs_order2,*coeffs_order2,recursive);
    
    allPdfs.insert(pair<int,RooAbsPdf*>(0,tempPdf_order0));
    allPdfs.insert(pair<int,RooAbsPdf*>(1,tempPdf_order1));
    allPdfs.insert(pair<int,RooAbsPdf*>(2,tempPdf_order2));
    initialGaussians.insert(pair<int,map<string,RooAbsPdf*> >(0,tempPdfsMap_order0));
    initialGaussians.insert(pair<int,map<string,RooAbsPdf*> >(1,tempPdfsMap_order1));
    initialGaussians.insert(pair<int,map<string,RooAbsPdf*> >(2,tempPdfsMap_order2));

}

// here we are building a sum of Gaussians where the params are functions of MH
void SimultaneousFit::buildSumOfGaussians(string name, int nGaussians, bool recursive, bool forceFracUnity){
  // the "Order" refers to the order of the polynomial describing the dependence of the parameters on MH
  
  // various holders for params and pdfs
  RooArgList *gaussians_order0 = new RooArgList();
  RooArgList *gaussians_order1 = new RooArgList();
  RooArgList *gaussians_order2 = new RooArgList();
  RooArgList *coeffs_order0 = new RooArgList();
  RooArgList *coeffs_order1 = new RooArgList();
  RooArgList *coeffs_order2 = new RooArgList();
  map<string,RooRealVar*> tempFitParams;
  map<string,RooAbsReal*> tempFitUtils;
  map<string,RooAbsPdf*> tempPdfsMap_order0;
  map<string,RooAbsPdf*> tempPdfsMap_order1;
  map<string,RooAbsPdf*> tempPdfsMap_order2;
  
  // start looping through the desired number of Gaussians
  for (int g=0; g<nGaussians; g++){
    float dmRange =3.;
    if (g>3) dmRange=6.;
    
    //start defining parameters
    RooFormulaVar *dMH = new RooFormulaVar(Form("dMH"),Form("dMH",g),"@0-125.0",RooArgList(*MH));
    RooRealVar *dm_p0 = new RooRealVar(Form("dm_g%d_p0",g),Form("dm_g%d_p0",g),0.1,-5.0,5.0);
    RooRealVar *dm_p1 = new RooRealVar(Form("dm_g%d_p1",g),Form("dm_g%d_p1",g),0.01,-0.01,0.01);
    RooRealVar *dm_p2 = new RooRealVar(Form("dm_g%d_p2",g),Form("dm_g%d_p2",g),0.01,-0.01,0.01);
    RooPolyVar *dm_order0 = new RooPolyVar(Form("dm_g%d_order0",g),Form("dm_g%d_order0",g),*dMH,RooArgList(*dm_p0)); //y=a
    RooPolyVar *dm_order1 = new RooPolyVar(Form("dm_g%d_order1",g),Form("dm_g%d_order1",g),*dMH,RooArgList(*dm_p0,*dm_p1)); //y=a+bx
    RooPolyVar *dm_order2 = new RooPolyVar(Form("dm_g%d_order2",g),Form("dm_g%d_order2",g),*dMH,RooArgList(*dm_p0,*dm_p1,*dm_p2)); //y=a+bx+c*x*x
    RooFormulaVar *mean_order0 = new RooFormulaVar(Form("mean_g%d_order0",g),Form("mean_g%d_order0",g),"((@0+@1))",RooArgList(*MH,*dm_order0));
    RooFormulaVar *mean_order1 = new RooFormulaVar(Form("mean_g%d_order1",g),Form("mean_g%d_order1",g),"((@0+@1))",RooArgList(*MH,*dm_order1));
    RooFormulaVar *mean_order2 = new RooFormulaVar(Form("mean_g%d_order2",g),Form("mean_g%d_order2",g),"((@0+@1))",RooArgList(*MH,*dm_order2));
    RooRealVar *sigma_p0 = new RooRealVar(Form("sigma_g%d_p0",g),Form("sigma_g%d_p0",g),(g+1)*1.0,0.5,10);
    RooRealVar *sigma_p1 = new RooRealVar(Form("sigma_g%d_p1",g),Form("sigma_g%d_p1",g),0.01,-0.01,0.01);
    RooRealVar *sigma_p2 = new RooRealVar(Form("sigma_g%d_p2",g),Form("sigma_g%d_p2",g),0.01,-0.01,0.01);
    RooPolyVar *sigma_order0 = new RooPolyVar(Form("sigma_g%d_order0",g),Form("sigma_g%d_order0",g),*dMH,RooArgList(*sigma_p0));
    RooPolyVar *sigma_order1 = new RooPolyVar(Form("sigma_g%d_order1",g),Form("sigma_g%d_order1",g),*dMH,RooArgList(*sigma_p0,*sigma_p1));
    RooPolyVar *sigma_order2 = new RooPolyVar(Form("sigma_g%d_order2",g),Form("sigma_g%d_order2",g),*dMH,RooArgList(*sigma_p0,*sigma_p1,*sigma_p2));
    RooAbsPdf *gaus_order0 = new RooGaussian(Form("gaus_g%d_order0",g),Form("gaus_g%d_order0",g),*mass,*mean_order0,*sigma_order0);
    RooAbsPdf *gaus_order1 = new RooGaussian(Form("gaus_g%d_order1",g),Form("gaus_g%d_order1",g),*mass,*mean_order1,*sigma_order1);
    RooAbsPdf *gaus_order2 = new RooGaussian(Form("gaus_g%d_order2",g),Form("gaus_g%d_order2",g),*mass,*mean_order2,*sigma_order2);
    tempPdfsMap_order0.insert(pair<string,RooAbsPdf*>(string(gaus_order0->GetName()),gaus_order0));
    tempPdfsMap_order1.insert(pair<string,RooAbsPdf*>(string(gaus_order1->GetName()),gaus_order1));
    tempPdfsMap_order2.insert(pair<string,RooAbsPdf*>(string(gaus_order2->GetName()),gaus_order2));
    gaussians_order0->add(*gaus_order0);
    gaussians_order1->add(*gaus_order1);
    gaussians_order2->add(*gaus_order2);
    listOfPolyVars_->add(*dm_order0);
    listOfPolyVars_->add(*dm_order1);
    listOfPolyVars_->add(*dm_order2);
    listOfPolyVars_->add(*mean_order0);
    listOfPolyVars_->add(*mean_order1);
    listOfPolyVars_->add(*mean_order2);
    listOfPolyVars_->add(*sigma_order0);
    listOfPolyVars_->add(*sigma_order1);
    listOfPolyVars_->add(*sigma_order2);
    
    if (g<nGaussians-1) { 
      RooRealVar *frac_p0 = new RooRealVar(Form("frac_g%d_p0",g),Form("frac_g%d_p0",g),0.5-0.05*g, 0.01,0.99);
      RooRealVar *frac_p1 = new RooRealVar(Form("frac_g%d_p1",g),Form("frac_g%d_p1",g),0.01,-0.005,0.005);
      RooRealVar *frac_p2 = new RooRealVar(Form("frac_g%d_p2",g),Form("frac_g%d_p2",g),0.00001,-0.00001,0.00001);
      RooPolyVar *frac_order0 = new RooPolyVar(Form("frac_g%d_order0",g),Form("frac_g%d_order0",g),*dMH,RooArgList(*frac_p0));
      RooPolyVar *frac_order1 = new RooPolyVar(Form("frac_g%d_order1",g),Form("frac_g%d_order1",g),*dMH,RooArgList(*frac_p0,*frac_p1));
      RooPolyVar *frac_order2 = new RooPolyVar(Form("frac_g%d_order2",g),Form("frac_g%d_order2",g),*dMH,RooArgList(*frac_p0,*frac_p1,*frac_p2));
      // constrain fractions to be below 1 and above 0
      RooFormulaVar *frac_constrained_order0 = new RooFormulaVar(Form("frac_g%d_constrained_order0",g),Form("frac_g%d_constrained_order0",g),"(@0>0)*(@0<1)*@0+ (@0>1.0)*0.9999",RooArgList(*frac_order0));
      RooFormulaVar *frac_constrained_order1 = new RooFormulaVar(Form("frac_g%d_constrained_order1",g),Form("frac_g%d_constrained_order1",g),"(@0>0)*(@0<1)*@0+ (@0>1.0)*0.9999",RooArgList(*frac_order1));
      RooFormulaVar *frac_constrained_order2 = new RooFormulaVar(Form("frac_g%d_constrained_order2",g),Form("frac_g%d_constrained_order2",g),"(@0>0)*(@0<1)*@0+ (@0>1.0)*0.9999",RooArgList(*frac_order2));
      listOfPolyVars_->add(*frac_constrained_order0);
      listOfPolyVars_->add(*frac_constrained_order1);
      listOfPolyVars_->add(*frac_constrained_order2);
      coeffs_order0->add(*frac_constrained_order0);
      coeffs_order1->add(*frac_constrained_order1);
      coeffs_order2->add(*frac_constrained_order2);
    }
    
    if (g==nGaussians-1 && forceFracUnity){
      string formula="1.";
      for (int i=0; i<nGaussians-1; i++) formula += Form("-@%d",i);
      RooAbsReal *recFrac_order0 = new RooFormulaVar(Form("frac_rec_g%d",g),Form("frac_rec_g%d",g),formula.c_str(),*coeffs_order0);
      RooAbsReal *recFrac_order1 = new RooFormulaVar(Form("frac_rec_g%d",g),Form("frac_rec_g%d",g),formula.c_str(),*coeffs_order1);
      RooAbsReal *recFrac_order2 = new RooFormulaVar(Form("frac_rec_g%d",g),Form("frac_rec_g%d",g),formula.c_str(),*coeffs_order2);
      coeffs_order0->add(*recFrac_order0);
      coeffs_order1->add(*recFrac_order1);
      coeffs_order2->add(*recFrac_order2);
      listOfPolyVars_->add(*recFrac_order0);
      listOfPolyVars_->add(*recFrac_order1);
      listOfPolyVars_->add(*recFrac_order2);
    }
  }
  
  //assert(gaussians->getSize()==nGaussians && coeffs->getSize()==nGaussians-(1*!forceFracUnity));
  // sumthe Gaussians together§
  RooAbsPdf *tempSumOfGaussians_order0 = new RooAddPdf(Form("%s_order0",name.c_str()),Form("%s_order0",name.c_str()),*gaussians_order0,*coeffs_order0,recursive);
  RooAbsPdf *tempSumOfGaussians_order1 = new RooAddPdf(Form("%s_order1",name.c_str()),Form("%s_order1",name.c_str()),*gaussians_order1,*coeffs_order1,recursive);
  RooAbsPdf *tempSumOfGaussians_order2 = new RooAddPdf(Form("%s_order2",name.c_str()),Form("%s_order2",name.c_str()),*gaussians_order2,*coeffs_order2,recursive);
  allPdfs.insert(pair<int,RooAbsPdf*>(0,tempSumOfGaussians_order0));
  allPdfs.insert(pair<int,RooAbsPdf*>(1,tempSumOfGaussians_order1));
  allPdfs.insert(pair<int,RooAbsPdf*>(2,tempSumOfGaussians_order2));
  initialGaussians.insert(pair<int,map<string,RooAbsPdf*> >(0,tempPdfsMap_order0));
  initialGaussians.insert(pair<int,map<string,RooAbsPdf*> >(1,tempPdfsMap_order1));
  initialGaussians.insert(pair<int,map<string,RooAbsPdf*> >(2,tempPdfsMap_order2));

}

map<int,map<string,RooRealVar*> > SimultaneousFit::getFitParams(){
  return fitParams;
}

void SimultaneousFit::printFitParams(){
  cout << "[INFO] Printing fit param map: " << endl;
  for (map<int,map<string,RooRealVar*> >::iterator it = fitParams.begin(); it != fitParams.end(); it++){
    for (map<string,RooRealVar*>::iterator it2 = it->second.begin(); it2 != it->second.end(); it2++){
      cout << it->first << " : " << it2->first << " -- " << it2->second->getVal() << endl; 
    }
  }
}

// actually run the fits
void SimultaneousFit::runFits(int ncpu,string outdir, float epsilon){
//epsilon represents the additional constraint on the fits when fitting order 0 first, constraining to +/- (1.+epsilon)*nominal, then fitting order 1 etc...
  
  //holder for chi2 values and fitrsults
  std::vector<std::string> chi2_values_str;
  std::vector<RooFitResult> vecFitRes;

  // we are doing a mgg MH fit, so don't leave this constant
  MH->setConstant(false);

  // canvas and stuff for debug plots
  TCanvas *canvas1 = new TCanvas("c","c",500,500);
  std::map<string,TMultiGraph*> graphs;
  std::map<string,TGraphErrors*> graphs_perOrder;
  std::vector<int> colorList ={7,9,4,2,8,5,1,14,15,16,17,18,19,20};
  
  // retrieve the 2D PDFS, where 0,1,2 represents the dependence of the params on MH (constatnt, linear, quadratic)
  RooAbsPdf *fitModel_order0 = allPdfs[0];
  RooAbsPdf *fitModel_order1 = allPdfs[1];
  RooAbsPdf *fitModel_order2 = allPdfs[2];
  std::vector<RooAbsPdf*> fitModel;
  fitModel.push_back(fitModel_order0);
  fitModel.push_back(fitModel_order1);
  fitModel.push_back(fitModel_order2);

  if (binnedFit_){
    MH->setVal(125);
    MH->setBins(10);
    mass->setBins(bins_);
    mass->setVal(125);
  } else {
    std::cout << "EROR unbinned fit not compatible with SSF. exit." << std::endl;
    exit(1);
  }
  
  // now loop through orders, and iteratively fit.
  // NB that here teh max order is hard coded. It might be nice to customize this in future
  // but in reality the maxorder made very little difference to final result (and negligible imporvement in terms of minNLL
  // so just picked a sensible value eg 2 --> this means that the iterative order stops at order 1
  for (int iOrder=0; iOrder <maxOrder_+1 ; iOrder++){
    

    //if you want to see the values of your PDF's params before the fit, you can
    if (verbosity_){ 
      RooRealVar *thisParamPreFit;
      TIterator *pdfParamsPreFit = fitModel[iOrder]->getParameters(RooArgSet(*mass,*MH))->selectByAttrib("Constant",kFALSE)->createIterator();
      std::cout << " [INFO] Values pdf PDF params pre-fit (order) "<< iOrder<< std::endl;
      while((thisParamPreFit=(RooRealVar*)pdfParamsPreFit->Next())){
          thisParamPreFit->Print("");
      }
    }
    
    //prepare the individual normalised datasets, and put them into a map which the lcChi2 can understand
    std::map<int, RooDataHist*> ourDatasets;
    for (int iMH =0 ; iMH<allMH_.size() ; iMH++){
    if( (proc_=="testBBH" || proc_=="testTHQ" || proc_=="testTHW") && allMH_[iMH]!=125 ) continue;
    ourDatasets.insert(pair<int, RooDataHist*>(allMH_[iMH], new RooDataHist(Form("%d_binned",allMH_[iMH]),Form("%d_binned",allMH_[iMH]),RooArgSet(*mass),*(normaliseDatasets(datasets[allMH_[iMH]])))));
    }
    
    // now add the datasets and the model into our special RooAddition class, which takes the datasets and the model evaluated at the corresponding MH, and then evaluates a chi2 for each MH before summing them and returning the total chi2
    LCRooAddition * lcChi2 = new LCRooAddition("lc_chi2",  "lc_chi2",(fitModel[iOrder]),  ourDatasets, MH, mass ) ;
    RooMinuit m(*lcChi2);
    m.migrad();
    m.hesse();
    RooFitResult* fitRes=m.save();
    
    // now go through the PDFs  sometimes the DCB is badly behaved, so check it does not have infinite values anywhere in the range
    for (int ipdf = 0 ; ipdf < ((RooAddPdf*)fitModel[iOrder])->pdfList().getSize() ; ipdf++){
      // check if the pdf in the RooAddPDf can be cast as a DCB
      RooDoubleCBFast * rdcb = dynamic_cast<RooDoubleCBFast*>(((RooAbsPdf*)&((RooAddPdf*)fitModel[iOrder])->pdfList()[ipdf]));
      if (rdcb) {
        int isSafe = isDCBsafe(rdcb);
        //if not safe,, randomize params and try again
        if (!isSafe){
          std::cout << "This DCB is not safe ! " << rdcb->GetName() << "is not safe!! these are the param values. Exit." << std::endl;
          rdcb->getParameters(RooArgSet(*mass,*MH));
          exit(1);
        }
      } else { std::cout << "pdf " << ipdf << " is not a dcb " << std::endl;}
    }
    // some fit details
    std::cout << Form("[INFO] Order %d, fit result minNLL to 2D dataset %.9f",iOrder,fitRes->minNll()) << std::endl;
    double minNll=fitRes->minNll();
    //vecFitRes.push_back(fitRes*);
    int thisNDOF=(fitModel[iOrder]->getParameters(RooArgSet(*mass,*MH)))->getSize();
    
    // print the parameter post-fit values if you like
    if(verbosity_>-1){
      std::cout << " [INFO] Values pdf PDF params -post fit"<< std::endl;
      RooRealVar *thisParamPostFit;
      TIterator *pdfParamsPostFit = fitModel[iOrder]->getParameters(RooArgSet(*mass,*MH))->selectByAttrib("Constant",kFALSE)->createIterator();
      while((thisParamPostFit=(RooRealVar*)pdfParamsPostFit->Next())){
        thisParamPostFit->Print("");
      }
    }

    //make some plots of the fits at each order
    int index=0;
    RooPlot *frame = mass->frame(Range(mhLow_-10,mhHigh_+10));
    float totalChi2=0; // summing the chi2 for each mass point
    int ndof=0;
    //loop through each dataset
    for (map<int,RooDataSet*>::iterator dataIt=datasets.begin(); dataIt!=datasets.end(); dataIt++){
      int mh=dataIt->first;

      //get the plotting datasets
      RooAbsData* plotData;
      if (binnedFit_){
        mass->setBins(bins_);
        RooDataSet * norm_data = normaliseDatasets(datasets[mh]);
        plotData = new RooDataHist(Form("%s_binned",norm_data->GetName()),Form("%s_binned",norm_data->GetName()),RooArgSet(*mass),*norm_data);
      } else {
        plotData = normaliseDatasets(datasets[mh]);
      }

      // and plot it with the pdf slide for that mass point
      MH->setVal(mh);
      plotData->plotOn(frame,RooFit::MarkerColor(colorList[index]));
      RooHist* thisHist = (RooHist*)frame->getObject(frame->numItems()-1);
      fitModel[iOrder]->plotOn(frame,RooFit::ProjWData(*plotData),RooFit::LineColor(colorList[index]));
      RooCurve* thisCurve = (RooCurve*)frame->getObject(frame->numItems()-1);
      ndof = (fitModel[iOrder]->getParameters(RooArgSet(*mass,*MH)))->getSize();
      float chi2= (frame->chiSquare(0));
      totalChi2 = totalChi2 +chi2;
      index++;
    }

    canvas1 = new TCanvas("c","c",500,500);
    //draw, put cosmetics on and save
    frame->Draw();
    TLatex *lat = new TLatex(); lat->SetTextSize(0.05); lat->SetNDC();
    lat->DrawLatex(0.14, 0.80,Form("order = %d",iOrder));
    lat->DrawLatex(0.14, 0.85,Form("#chi^{2}/N_{dof}=%.2f / %d",totalChi2,ndof));
    lat->DrawLatex(0.14, 0.75,Form("minNll=%.9f ",minNll));
    chi2_values_str.push_back(Form("%.2f / %d     ",totalChi2,ndof));
    canvas1->SaveAs(Form("%s_SimultaneousFitDebug_order%d.pdf",outdir.c_str(),iOrder));
    canvas1->SaveAs(Form("%s_SimultaneousFitDebug_order%d.png",outdir.c_str(),iOrder));
    
    //can also make some debug plots for the individual params (here plotted vs MH)
    // this is turned off by default but if --verbose then they will print
    if (verbosity_>0){
      TIterator *paramIter = listOfPolyVars_->createIterator();
      RooPolyVar *polyVar;
      // go through each polyvar
      while((polyVar=(RooPolyVar*)paramIter->Next())){
        if (!TString(polyVar->GetName()).Contains(Form("order%d",iOrder))) continue;
        TString ppName = TString(polyVar->GetName()).ReplaceAll(Form("_order%d",iOrder),"");
        if (graphs.find(ppName.Data())==graphs.end()) graphs[ppName.Data()]= new TMultiGraph();
        TGraphErrors *tg = new TGraphErrors(); int point=0;
        TLatex *latex = new TLatex(); latex->SetTextSize(0.05); latex->SetNDC();
        for (float thisMH=120; thisMH<130.1 ; thisMH=thisMH+1.0){
          
          MH->setVal(thisMH);
          if (thisMH==125.0) polyVar->Print(); 
          tg->SetPoint(point,thisMH,polyVar->getVal());
         // tg->SetPointError(point,0.0,polyVar->getPropagatedError(*fitResults[iOrder]));
          point++;
        }
        tg->Draw("ACE");
        tg->SetLineColor(colorList[iOrder+2]);
        tg->SetLineWidth(4);
        tg->SetMarkerColor(colorList[iOrder+2]);
        graphs[ppName.Data()]->Add(tg);
        latex->DrawLatex(0.16, 0.88,polyVar->GetName());
        TIterator *paramCoeffs = fitRes->floatParsFinal().createIterator();
        RooRealVar *thisParam;
        double offset =0.0;
        while((thisParam=(RooRealVar*)paramCoeffs->Next())){
          TString ppName = TString(polyVar->GetName()).ReplaceAll(Form("_order%d",iOrder),"");
          if (!TString(thisParam->GetName()).Contains(ppName)) continue;
          latex->DrawLatex(0.50, 0.88-offset,Form("%s = %.6f",thisParam->GetName(),thisParam->getVal()));
          offset=offset+0.07;
        }
        if(verbosity_>1){
          canvas1->SaveAs(Form("%s_polyvar_%s.pdf",outdir.c_str(),polyVar->GetName()));
          canvas1->SaveAs(Form("%s_polyvar_%s.png",outdir.c_str(),polyVar->GetName()));
        }
      }
    }
    
    //if using iterative fitting where the params are constrained between each order (size of constraint determined by epsilon) then it is applied here 
    //in pratcice this did not help - fits are already stable.
    //the code below makes a nice debug graph of the pulls of each parameter for the various orders
    TIterator *pdfParams = fitModel[iOrder]->getParameters(RooArgSet(*mass,*MH))->selectByAttrib("Constant",kFALSE)->createIterator();
    RooRealVar *thisParam;
    double smalloffset0=-0.12;
    double smalloffset1=-0.12;
    double smalloffset2=-0.12;
    double smalloffset=-0.12;
    while((thisParam=(RooRealVar*)pdfParams->Next())){
        TString ppName = TString(thisParam->GetName()).ReplaceAll(Form("_p0"),"").ReplaceAll(Form("_p1"),"").ReplaceAll(Form("_p2"),"");
        if (graphs_perOrder.find(ppName.Data())==graphs_perOrder.end()) graphs_perOrder[ppName.Data()]= new TGraphErrors();
        MH->setVal(125.0);
        float normalised_value=thisParam->getVal()/thisParam->getError();
        if (!TString(thisParam->GetName()).Contains("p0")){
        int paramOrder=999;
        if(TString(thisParam->GetName()).Contains("p1")) paramOrder=1;
        if(TString(thisParam->GetName()).Contains("p2")) paramOrder=2;

        if (iOrder==1 && paramOrder==1){ smalloffset=smalloffset0; smalloffset0=smalloffset0+0.02;}
        if (iOrder==2 && paramOrder==1){ smalloffset=smalloffset1; smalloffset1=smalloffset1+0.02;}
        if (iOrder==2 && paramOrder==2){ smalloffset=smalloffset2; smalloffset2=smalloffset2+0.02;}
        graphs_perOrder[ppName.Data()]->SetPoint(iOrder+paramOrder-2,iOrder+paramOrder-1-smalloffset,normalised_value);
        graphs_perOrder[ppName.Data()]->SetPointError(iOrder+paramOrder-2,0,1);
        }
      if (epsilon==-1) continue;
      double centralValue = thisParam->getVal(); 
      thisParam->setMin(min(thisParam->getVal()*(1-epsilon),(thisParam->getVal()*(1+epsilon))));
      thisParam->setMax(max(thisParam->getVal()*(1-epsilon),(thisParam->getVal()*(1+epsilon))));
      thisParam->setVal(centralValue);
    }
  
  }// end of the iOrder loop

  // make optional plots of the RooPolyVars cs MH for each order on the same plot
  TCanvas *canvas = new TCanvas("c","c",500,500);
  for (auto it = graphs.begin() ; it!=graphs.end(); ++it){
    it->second->Draw("apl");
    TLatex *latex = new TLatex(); latex->SetTextSize(0.05); latex->SetNDC();
    latex->DrawLatex(0.16, 0.85,it->first.c_str());
    latex->DrawLatex(0.6, 0.83,Form("#color[%d]{Order 0}",colorList[0+2]));
    latex->DrawLatex(0.6, 0.75,Form("#color[%d]{Order 1}",colorList[1+2]));
    latex->DrawLatex(0.6, 0.67,Form("#color[%d]{Order 2}",colorList[2+2]));
    if (verbosity_){
      canvas->SaveAs(Form("%s_multigraph_%s.pdf",outdir.c_str(),it->first.c_str()));
      canvas->SaveAs(Form("%s_multigraph_%s.png",outdir.c_str(),it->first.c_str()));
    }
  }
  TMultiGraph* mg_perOrder = new TMultiGraph();
  int iColor=0;
  string rvwv= (TString(outdir).Contains("rv")? "rv": TString(outdir).Contains("wv")? "wv" : "?");
  TLatex *latex = new TLatex(); latex->SetTextSize(0.03); latex->SetNDC();
  for (auto it = graphs_perOrder.begin() ; it!=graphs_perOrder.end(); ++it){
    it->second->SetMarkerColor(colorList[iColor]);
    it->second->SetLineColor(colorList[iColor]);
    it->second->SetMarkerStyle(21);
    it->second->SetMarkerSize(1);
    iColor++;
    mg_perOrder->Add((it->second));
    //latex->DrawLatex(0.6, 0.93-0.1*iColor,Form("#color[%d]{%s}",colorList[iColor],it->first.c_str()));
  }
  mg_perOrder->Draw("AP");
  mg_perOrder->GetYaxis()->SetTitle("number of standard deviations from 0");
  mg_perOrder->GetXaxis()->SetRangeUser(0,4);
  mg_perOrder->GetYaxis()->SetRangeUser(-5,5);
  mg_perOrder->GetXaxis()->SetLabelOffset(999);
  mg_perOrder->Draw("AP");
  latex->DrawLatex(0.1, 0.05,Form("order1, p0"));
  latex->DrawLatex(0.45, 0.05,Form("order2, p0"));
  latex->DrawLatex(0.8, 0.05,Form("order2, p1"));
  iColor=0;
  for (auto it = graphs_perOrder.begin() ; it!=graphs_perOrder.end(); ++it){
    latex->DrawLatex(0.6, 0.4-0.03*iColor,Form("#color[%d]{%s}",colorList[iColor],it->first.c_str()));
    iColor++;
  }
  TLine *line3 = new TLine(1,0.,3,0.);
  //line3->SetLineColor(bestcol);
  line3->SetLineStyle(kDashed);
  line3->SetLineWidth(5.0);
  line3->Draw();
  latex->DrawLatex(0.16, 0.85,Form("%s %s %s",proc_.c_str(), cat_.c_str(), rvwv.c_str()));
  canvas->SaveAs(Form("%s_paramsPulls.pdf",outdir.c_str()));
  canvas->SaveAs(Form("%s_paramsPulls.png",outdir.c_str()));
}

void SimultaneousFit::setFitParams(std::map<int,std::map<std::string,RooRealVar*> >& pars )
{
  for(map<int,map<string,RooRealVar*> >::iterator ipar = pars.begin(); ipar!=pars.end(); ++ipar ) {
    int mh = ipar->first;
    map<string,RooRealVar*>& vars = ipar->second;
    std::map<std::string,RooRealVar*> myParams = fitParams[mh];
    for(std::map<std::string,RooRealVar*>::iterator ivar=vars.begin(); ivar!=vars.end(); ++ivar){
      //// std::cout << "Setting " << ivar->first << " to " << ivar->second->getVal() << " " <<
      //// 	myParams[ivar->first]->getVal() << " " << myParams[ivar->first]->GetName() <<
      //// 	ivar->second->GetName() << std::endl;
      myParams[ivar->first]->setVal(ivar->second->getVal());
    }
  }
}

// soem extra plots of the fits
void SimultaneousFit::plotFits(string name, string rvwv){

  TCanvas *canv = new TCanvas();
  RooPlot *plot = mass->frame(Range(mhLow_-10,mhHigh_+10));
  TPaveText *pt = new TPaveText(.65,.6,.97,.95,"NDC");
  std::vector<int> colorList ={7,9,4,2,8,5,1,14};
  for (unsigned int i=0; i<allMH_.size(); i++){
    int mh = allMH_[i];
    MH->setConstant(false);
    MH->setVal(mh);
    MH->setConstant(true);
    //assert(allPdfs.find(mh)!=allPdfs.end());
    //assert(datasets.find(mh)!=datasets.end());
    RooAbsPdf *fitModel = allPdfs[maxOrder_];
    //RooDataSet *data = datasets[mh];
    //mass->setBins(320);
    mass->setBins(bins_);
    RooDataHist *data = new RooDataHist(datasets[mh]->GetName(),datasets[mh]->GetName(), RooArgSet(*mass),*normaliseDatasets(datasets[mh]));
    //RooDataHist *data = datasets[mh]->binnedClone();
    //data->plotOn(plot,Binning(160),MarkerColor(kBlue+10*i));
    if (i>  colorList.size() ){
      std::cout << "ERROR you need to add more colors in SimultaneousFit::plotFits because you have a lot of mH points!" << std::endl;
      exit(1);
    }
    data->plotOn(plot,MarkerColor(colorList[i]));
    fitModel->plotOn(plot,LineColor(colorList[i]));
    if( (TString(datasets[mh]->GetName()))!=(TString(datasetsSTD[mh]->GetName()))){
      pt->SetTextColor(kRed);
      pt->AddText(Form(" %d replacement :",mh));
      pt->AddText(Form(" %s",data->GetName())); 
    } else {
      pt->AddText(Form(" %d: %s",mh,data->GetName())); 
    }
  }
  plot->SetTitle(Form("%s %s Fits",(datasetsSTD[125]->GetName()),rvwv.c_str()));
  plot->Draw();
  pt->Draw();
  canv->Print(Form("%s.pdf",name.c_str()));
  canv->Print(Form("%s.png",name.c_str()));
  mass->setBins(160); //return to default
  delete canv;
}


// making the splines is now very easy !
std::map<std::string,RooSpline1D*> SimultaneousFit::getSplines(){
  
  // which order of fit are we using to make the splines
  int chosenOrder=maxOrder_;
  std::map<std::string,RooSpline1D*> splines;
  
  // loop through params and make a spline of each
  TIterator *paramIter = listOfPolyVars_->createIterator();
  RooPolyVar *polyVar;
  while((polyVar=(RooPolyVar*)paramIter->Next())){
    //change name to remove order
    TString pvName = TString(polyVar->GetName()).ReplaceAll(Form("_order%d",chosenOrder),"");
    polyVar->SetName(pvName);
    polyVar->SetTitle(pvName);
    if (verbosity_) std::cout << "[INFO] SSF: preparing spline for " << polyVar->GetName() << std::endl;
    //fill arrays which will be used to make a spline
    vector<double> xValues;
    vector<double> yValues;
    for (float thisMH=100; thisMH<180.1 ; thisMH=thisMH+0.1){
      MH->setVal(thisMH);
      xValues.push_back(thisMH);
      yValues.push_back(polyVar->getVal());
    }
    //make the spline
    RooSpline1D *thisSpline = new RooSpline1D(polyVar->GetName(),polyVar->GetName(),*MH,xValues.size(),&(xValues[0]),&(yValues[0]));
    splines.insert(pair<string,RooSpline1D*>(thisSpline->GetName(),thisSpline));
  }
  return splines;
}


// check if the DCB is safe ! ie does not go infinite anywhere in range or have a bonkers integral
int SimultaneousFit::isDCBsafe(RooDoubleCBFast* dcb){
  
  //checks if the DCB integral or value goes negative anywhere in range of interst
  for (double mh_var=100.0; mh_var<180.0; mh_var=mh_var+0.1){
    MH->setVal(mh_var);
    mass->setRange("lcRange",100,180);
    double val = ((RooDoubleCBFast*)dcb)->analyticalIntegral(1,"lcRange");
    if( !(fabs(val)<999)){ // 999 is "some reasonable value"
      std::cout << " ERROR, this p#df  has a NaN or 0 integral " << val <<"at MH =" << mh_var << " EXIT" << std::endl;
      return 0;
    }
  }
  for (double mh_var=100.0; mh_var<180.0; mh_var=mh_var+0.1){
    for (double mgg_var=100.0; mgg_var < 180.0 ; mgg_var=mgg_var+0.1){
      MH->setVal(mh_var);
      mass->setVal(mgg_var);
      
       /*double val = ((RooDoubleCBFast*)dcb)->evaluate(); // for some reason this is a private member in the RooDoubleCBFast implementation. If one wants to use this feature it is just a case of moving the evaluate() function from private to public in HiggsAnalysis/GBRLikelihood/inteface/RooDoubleCBFast.h
      if( !(fabs(val)<999)){ // 999 is "some reasonable value"
        std::cout << " ERROR, this pdf  has a NaN or 0 value " << val  << " at MH =" << mh_var << " mgg= " << mgg_var <<  " EXIT" << std::endl;
        listOfPolyVars_->Print("V");
        return 0;
      }*/
    }
  }
  return 1;
}
