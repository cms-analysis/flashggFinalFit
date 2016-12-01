#include <fstream>

#include "TCanvas.h"
#include "TMath.h"
#include "TLatex.h"
#include "RooPlot.h"
#include "RooPolyVar.h"
#include "TColor.h"
#include "RooFormulaVar.h"
#include "RooMsgService.h"
#include "TPaveText.h"
#include "TMultiGraph.h"

#include "boost/lexical_cast.hpp"

#include "../interface/SimultaneousFit.h"

using namespace std;
using namespace RooFit;

SimultaneousFit::SimultaneousFit(RooRealVar *massVar, RooRealVar *MHvar, int mhLow, int mhHigh, vector<int> skipMasses, bool binnedFit, int bins, std::vector<int> massList, string cat, string proc, string outdir ):
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
  outdir_(outdir)
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
    if (verbosity_>=1) cout << "[INFO] LinearInterp - Adding mass: " << m << endl;
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

RooDataSet* SimultaneousFit::normaliseDatasets( RooDataSet* data){
   
  //prepare weight variables
  double weight =0;
  RooRealVar* weightVar = new RooRealVar("weight","weight",-10000,10000);
  RooRealVar* dZ = new RooRealVar("dZ","dZ",-10000,10000);
  double runningSum=0;
  double runningSum2=0;
  double factor = 1.0/data->sumEntries();
  // prepare the holder for the merged data, which is a 2D dataset of mass and MH
  //RooDataSet* result = new RooDataSet(Form("%s_normalised",data->GetName()),Form("%s_normalised",data->GetName()),RooArgSet(*mass,*weightVar),"weight");
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
      //set the MH to the relevant value for this dataste
      //MH->setVal(dataIt->first);
      //if (iEntry%1000==0) std::cout << "LC DEBUG SimultaneousFit::normaliseDatasets adding entry "<< iEntry << " / " << data->numEntries() << " |  mass=" << mass->getVal() << " weight " << weight << std::endl;
      // add a row to the dataset for this entry
      result->add(RooArgSet(*mass,*weightVar),weightVar->getVal());
    }
  
  //and simpyl return the merged dataset
  return result;
}
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
      
      //if (iEntry%100==0) std::cout << "LC DEBUG SimultaneousFit::mergeDatasets adding entry MH=" << MH->getVal() << " mass=" << mass->getVal() << std::endl;
      // add a row to the dataset for this entry
      result->add(RooArgSet(*mass,*MH,*weightVar),weightVar->getVal());
    }
  std::cout << " LC DEBUG here is your old dataset for MH " << dataIt->first << "!" <<std::endl;
  dataIt->second->Print();
  }
  //and simpyl return the merged dataset
  std::cout << " LC DEBUG here is your brand new dataset !" <<std::endl;
  result->Print();
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

void SimultaneousFit::buildSumOfGaussians(string name, int nGaussians, bool recursive, bool forceFracUnity, int maxOrder){

    RooArgList *gaussians_order0 = new RooArgList();
    RooArgList *gaussians_order1 = new RooArgList();
    RooArgList *gaussians_order2 = new RooArgList();
    RooArgList *coeffs_order0 = new RooArgList();
    RooArgList *coeffs_order1 = new RooArgList();
    RooArgList *coeffs_order2 = new RooArgList();
    map<string,RooRealVar*> tempFitParams;
    map<string,RooAbsReal*> tempFitUtils;
    map<string,RooGaussian*> tempGaussians_order0;
    map<string,RooGaussian*> tempGaussians_order1;
    map<string,RooGaussian*> tempGaussians_order2;
    
    for (int g=0; g<nGaussians; g++){
      //RooRealVar *dm = new RooRealVar(Form("dm_mh%d_g%d",mh,g),Form("dm_mh%d_g%d",mh,g),0.1,-8.,8.);
      float dmRange =3.;
      if (g>3) dmRange=3.;
      RooFormulaVar *dMH = new RooFormulaVar(Form("dMH"),Form("dMH",g),"@0-125.0",RooArgList(*MH));
      //RooRealVar *mean_p0 = new RooRealVar(Form("mean_p0_g%d",g),Form("mean_p0_g%d",g),124.2,35,214);
      //RooRealVar *mean_p1 = new RooRealVar(Form("mean_p1_g%d",g),Form("mean_p1_g%d",g),0.01,-0.7,0.7);
      //ooPolyVar *mean = new RooPolyVar(Form("mean_g%d",g),Form("mean_g%d",g),*MH,RooArgList(*mean_p0,*mean_p1));
      RooRealVar *dm_p0 = new RooRealVar(Form("dm_g%d_p0",g),Form("dm_g%d_p0",g),0.1,-5.0,5.0);
      RooRealVar *dm_p1 = new RooRealVar(Form("dm_g%d_p1",g),Form("dm_g%d_p1",g),0.001,-0.01,0.01);
      RooRealVar *dm_p2 = new RooRealVar(Form("dm_g%d_p2",g),Form("dm_g%d_p2",g),0.00001,-0.0001,0.0001);
      RooPolyVar *dm_order0 = new RooPolyVar(Form("dm_g%d_order0",g),Form("dm_g%d_order0",g),*dMH,RooArgList(*dm_p0)); //y=a
      RooPolyVar *dm_order1 = new RooPolyVar(Form("dm_g%d_order1",g),Form("dm_g%d_order1",g),*dMH,RooArgList(*dm_p0,*dm_p1)); //y=a+bx
      RooPolyVar *dm_order2 = new RooPolyVar(Form("dm_g%d_order2",g),Form("dm_g%d_order2",g),*dMH,RooArgList(*dm_p0,*dm_p1,*dm_p2)); //y=a+bx+c*x*x
      //RooPolyVar *dm = new RooPolyVar(Form("dm_g%d",g),Form("dm_g%d",g),*MH,RooArgList(*dm_p0,*dm_p1));
      //RooRealVar *dm = new RooRealVar(Form("dm_mh%d_g%d",mh,g),Form("dm_mh%d_g%d",mh,g),0.1,-dmRange,dmRange);
      RooFormulaVar *mean_order0 = new RooFormulaVar(Form("mean_g%d_order0",g),Form("mean_g%d_order0",g),"((@0+@1))",RooArgList(*MH,*dm_order0));
      RooFormulaVar *mean_order1 = new RooFormulaVar(Form("mean_g%d_order1",g),Form("mean_g%d_order1",g),"((@0+@1))",RooArgList(*MH,*dm_order1));
      RooFormulaVar *mean_order2 = new RooFormulaVar(Form("mean_g%d_order2",g),Form("mean_g%d_order2",g),"((@0+@1))",RooArgList(*MH,*dm_order2));
      RooRealVar *sigma_p0 = new RooRealVar(Form("sigma_g%d_p0",g),Form("sigma_g%d_p0",g),1.6,0.0,4.5);
      RooRealVar *sigma_p1 = new RooRealVar(Form("sigma_g%d_p1",g),Form("sigma_g%d_p1",g),0.001,-0.01,0.01);
      RooRealVar *sigma_p2 = new RooRealVar(Form("sigma_g%d_p2",g),Form("sigma_g%d_p2",g),0.00001,-0.0001,0.0001);
      //RooFormulaVar *sigma = new RooFormulaVar(Form("sigma_g%d",g),Form("sigma_g%d",g),"((@0-125.0)*@1+@2)",RooArgList(*MH,*sigma_p1,*sigma_p0));
      //RooRealVar *sigma = new RooRealVar(Form("sigma_g%d",g),Form("sigma_g%d",g),-5);
      RooPolyVar *sigma_order0 = new RooPolyVar(Form("sigma_g%d_order0",g),Form("sigma_g%d_order0",g),*dMH,RooArgList(*sigma_p0));
      RooPolyVar *sigma_order1 = new RooPolyVar(Form("sigma_g%d_order1",g),Form("sigma_g%d_order1",g),*dMH,RooArgList(*sigma_p0,*sigma_p1));
      RooPolyVar *sigma_order2 = new RooPolyVar(Form("sigma_g%d_order2",g),Form("sigma_g%d_order2",g),*dMH,RooArgList(*sigma_p0,*sigma_p1,*sigma_p2));
      //RooPolyVar *sigma = new RooPolyVar(Form("sigma_g%d",g),Form("sigma_g%d",g),*MH,RooArgList(*sigma_p0,*sigma_p1));
      RooGaussian *gaus_order0 = new RooGaussian(Form("gaus_g%d_order0",g),Form("gaus_g%d_order0",g),*mass,*mean_order0,*sigma_order0);
      RooGaussian *gaus_order1 = new RooGaussian(Form("gaus_g%d_order1",g),Form("gaus_g%d_order1",g),*mass,*mean_order1,*sigma_order1);
      RooGaussian *gaus_order2 = new RooGaussian(Form("gaus_g%d_order2",g),Form("gaus_g%d_order2",g),*mass,*mean_order2,*sigma_order2);
      //tempFitParams.insert(pair<string,RooRealVar*>(string(dm->GetName()),dm));
      //tempFitParams.insert(pair<string,RooRealVar*>(string(sigma->GetName()),sigma));
      //tempFitUtils.insert(pair<string,RooAbsReal*>(string(mean->GetName()),mean));
      tempGaussians_order0.insert(pair<string,RooGaussian*>(string(gaus_order0->GetName()),gaus_order0));
      tempGaussians_order1.insert(pair<string,RooGaussian*>(string(gaus_order1->GetName()),gaus_order1));
      tempGaussians_order2.insert(pair<string,RooGaussian*>(string(gaus_order2->GetName()),gaus_order2));
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
      if (g<nGaussians) { //nGaussians-1
      RooRealVar *frac_p0 = new RooRealVar(Form("frac_g%d_p0",g),Form("frac_g%d_p0",g),0.5-0.05*g, 0.01,0.99);
      RooRealVar *frac_p1 = new RooRealVar(Form("frac_g%d_p1",g),Form("frac_g%d_p1",g),0.001,-0.005,0.005);
      RooRealVar *frac_p2 = new RooRealVar(Form("frac_g%d_p2",g),Form("frac_g%d_p2",g),0.00001,-0.00001,0.00001);
      //RooFormulaVar *frac = new RooFormulaVar(Form("frac_g%d",g),Form("frac_g%d",g),"abs((@0-125.0)*@1+@2)",RooArgList(*MH,*frac_p1,*frac_p0));
      RooPolyVar *frac_order0 = new RooPolyVar(Form("frac_g%d_order0",g),Form("frac_g%d_order0",g),*dMH,RooArgList(*frac_p0));
      RooPolyVar *frac_order1 = new RooPolyVar(Form("frac_g%d_order1",g),Form("frac_g%d_order1",g),*dMH,RooArgList(*frac_p0,*frac_p1));
      RooPolyVar *frac_order2 = new RooPolyVar(Form("frac_g%d_order2",g),Form("frac_g%d_order2",g),*dMH,RooArgList(*frac_p0,*frac_p1,*frac_p2));
      //RooFormulaVar *frac_constrained_order0 = new RooFormulaVar(Form("frac_g%d_constrained_order0",g),Form("frac_g%d_constrained_order0",g),"(@0>0)*(@0<1)*@0+ (@0>0.99)*0.99",RooArgList(*frac_order0));
      //RooFormulaVar *frac_constrained_order1 = new RooFormulaVar(Form("frac_g%d_constrained_order1",g),Form("frac_g%d_constrained_order1",g),"(@0>0)*(@0<1)*@0+ (@0>0.99)*0.99",RooArgList(*frac_order1));
      //RooFormulaVar *frac_constrained_order2 = new RooFormulaVar(Form("frac_g%d_constrained_order2",g),Form("frac_g%d_constrained_order2",g),"(@0>0)*(@0<1)*@0+ (@0>0.99)*0.99",RooArgList(*frac_order2));
      RooFormulaVar *frac_constrained_order0 = new RooFormulaVar(Form("frac_g%d_constrained_order0",g),Form("frac_g%d_constrained_order0",g),"(@0>0)*(@0<1)*@0+ (@0>1.0)*0.9999",RooArgList(*frac_order0));
      RooFormulaVar *frac_constrained_order1 = new RooFormulaVar(Form("frac_g%d_constrained_order1",g),Form("frac_g%d_constrained_order1",g),"(@0>0)*(@0<1)*@0+ (@0>1.0)*0.9999",RooArgList(*frac_order1));
      RooFormulaVar *frac_constrained_order2 = new RooFormulaVar(Form("frac_g%d_constrained_order2",g),Form("frac_g%d_constrained_order2",g),"(@0>0)*(@0<1)*@0+ (@0>1.0)*0.9999",RooArgList(*frac_order2));
      //RooPolyVar *frac = new RooPolyVar(Form("frac_g%d",g),Form("frac_g%d",g),*MH,RooArgList(*frac_p0,*frac_p1));
      // RooPolyVar *frac = new RooPolyVar(Form("frac_g%d",g),Form("frac_g%d",g),*MH,RooArgList(*frac_p0));
      //tempFitParams.insert(pair<string,RooRealVar*>(string(frac->GetName()),frac));
      listOfPolyVars_->add(*frac_constrained_order0);
      listOfPolyVars_->add(*frac_constrained_order1);
      listOfPolyVars_->add(*frac_constrained_order2);
      //RooRealVar *frac = new RooRealVar(Form("frac_g%d",g),Form("frac_g%d",g),0.3);
      coeffs_order0->add(*frac_constrained_order0);
      coeffs_order1->add(*frac_constrained_order1);
      coeffs_order2->add(*frac_constrained_order2);
      }
      if (g==nGaussians-1 && forceFracUnity){
        string formula="1.";
        std::cout << " DEBUG LC FORCE FRAC UNITY TRUE " << std::endl;
        for (int i=0; i<nGaussians-1; i++) formula += Form("-@%d",i);
        RooAbsReal *recFrac_order0 = new RooFormulaVar(Form("frac_rec_g%d",g),Form("frac_rec_g%d",g),formula.c_str(),*coeffs_order0);
        RooAbsReal *recFrac_order1 = new RooFormulaVar(Form("frac_rec_g%d",g),Form("frac_rec_g%d",g),formula.c_str(),*coeffs_order1);
        RooAbsReal *recFrac_order2 = new RooFormulaVar(Form("frac_rec_g%d",g),Form("frac_rec_g%d",g),formula.c_str(),*coeffs_order2);
        //tempFitUtils.insert(pair<string,RooAbsReal*>(string(recFrac->GetName()),recFrac));
        coeffs_order0->add(*recFrac_order0);
        coeffs_order1->add(*recFrac_order1);
        coeffs_order2->add(*recFrac_order2);
        listOfPolyVars_->add(*recFrac_order0);
        listOfPolyVars_->add(*recFrac_order1);
        listOfPolyVars_->add(*recFrac_order2);
      } else {

      std::cout << " DEBUG LC FORCE FRAC UNITY FALSE " << std::endl;
      }
    }
    //assert(gaussians->getSize()==nGaussians && coeffs->getSize()==nGaussians-(1*!forceFracUnity));
    RooAddPdf *tempSumOfGaussians_order0 = new RooAddPdf(Form("%s_order0",name.c_str()),Form("%s_order0",name.c_str()),*gaussians_order0,*coeffs_order0,recursive);
    RooAddPdf *tempSumOfGaussians_order1 = new RooAddPdf(Form("%s_order1",name.c_str()),Form("%s_order1",name.c_str()),*gaussians_order1,*coeffs_order1,recursive);
    RooAddPdf *tempSumOfGaussians_order2 = new RooAddPdf(Form("%s_order2",name.c_str()),Form("%s_order2",name.c_str()),*gaussians_order2,*coeffs_order2,recursive);
    //std::cout << "LC DEBUG final sumGaus params"<< std::endl;
    //coeffs->Print("V");
    sumOfGaussians.insert(pair<int,RooAddPdf*>(0,tempSumOfGaussians_order0));
    sumOfGaussians.insert(pair<int,RooAddPdf*>(1,tempSumOfGaussians_order1));
    sumOfGaussians.insert(pair<int,RooAddPdf*>(2,tempSumOfGaussians_order2));
    //fitParams.insert(pair<int,map<string,RooRealVar*> >(0,tempFitParams));
    //fitUtils.insert(pair<int,map<string,RooAbsReal*> >(0,tempFitUtils));
    initialGaussians.insert(pair<int,map<string,RooGaussian*> >(0,tempGaussians_order0));
    initialGaussians.insert(pair<int,map<string,RooGaussian*> >(1,tempGaussians_order1));
    initialGaussians.insert(pair<int,map<string,RooGaussian*> >(2,tempGaussians_order2));
  
}

void SimultaneousFit::loadPriorConstraints(string filename, float constraintValue){

  ifstream datfile;
  datfile.open(filename.c_str());
  if (datfile.fail()) return;
  while (datfile.good()) {
    string line;
    getline(datfile,line);
    if (line=="\n" || line.substr(0,1)=="#" || line==" " || line.empty()) continue;
    string name = line.substr(0,line.find_first_of(" "));
    double val = boost::lexical_cast<double>(line.substr(line.find_first_of(" ")+1,string::npos));
    int mhS = boost::lexical_cast<int>(name.substr(name.find("_mh")+3,name.find("_g")-name.find("_mh")-3));
    if (verbosity_>=2) cout << "[INFO] "<< name << " " << mhS << " " << val << endl;
    assert(fitParams.find(mhS)!=fitParams.end());
    assert(fitParams[mhS].find(name)!=fitParams[mhS].end());
    fitParams[mhS][name]->setVal(val);
    if (val>0.) fitParams[mhS][name]->setRange((1.-constraintValue)*val,(1.+constraintValue)*val);
    else fitParams[mhS][name]->setRange((1.+constraintValue)*val,(1.-constraintValue)*val);
  }
  datfile.close();
}

void SimultaneousFit::saveParamsToFile(string filename){
  ofstream datfile;
  datfile.open(filename.c_str());
  for (unsigned int i=0; i<allMH_.size(); i++){
    int mh = allMH_[i];
    for (map<string,RooRealVar*>::iterator it=fitParams[mh].begin(); it!=fitParams[mh].end(); it++){
      datfile << Form("%s %1.5f",it->first.c_str(),it->second->getVal()) << endl;
    }
  }
  datfile.close();
}

void SimultaneousFit::saveParamsToFileAtMH(string filename, int setMH){
  ofstream datfile;
  datfile.open(filename.c_str());
  for (unsigned int i=0; i<allMH_.size(); i++){
    int mh = allMH_[i];
    for (map<string,RooRealVar*>::iterator it=fitParams[setMH].begin(); it!=fitParams[setMH].end(); it++){
      string repName = it->first;
      repName = repName.replace(repName.find(Form("mh%d",setMH)),5,Form("mh%d",mh));
      datfile << Form("%s %1.5f",repName.c_str(),it->second->getVal()) << endl;
    }
  }
  datfile.close();
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

void SimultaneousFit::runFits(int ncpu,string outdir){
    
    double epsilon =0.1;
    MH->setConstant(false);
    std::map<string,TMultiGraph*> graphs;
    RooAddPdf *fitModel_order0 = sumOfGaussians[0];
    RooAddPdf *fitModel_order1 = sumOfGaussians[1];
    RooAddPdf *fitModel_order2 = sumOfGaussians[2];
    std::vector<RooAddPdf*> fitModel;
    fitModel.push_back(fitModel_order0);
    fitModel.push_back(fitModel_order1);
    fitModel.push_back(fitModel_order2);
    RooDataSet *dataRaw = mergeNormalisedDatasets(datasets);
    RooAbsData *data; 
    if (binnedFit_){
       data = dataRaw->binnedClone();
     } else {
         data = dataRaw;
     }
    // help when dataset has no entries
     if (data->sumEntries()<1.e-5) {
       //should never happen!
       assert(data->sumEntries()!=0.0);
       }
    TCanvas *testlc = new TCanvas("c","c",500,500);
    //just for debug for now
    std::vector<int> colorList ={7,9,4,2,8,5,1,14};
    for (int iOrder=0; iOrder <3 ; iOrder++){
      RooFitResult *fitRes;
      data->Print();
      mass->setBins(bins_);
      std::cout << "LC DEBUG fitting to order " << iOrder << std::endl;
      std::cout << " PARAM VALUES pre fit of order " << iOrder << std::endl;
      //fitModel[iOrder]->getParameters(RooArgSet(*mass,*MH))->selectByAttrib("Constant",kFALSE)->Print("V");
      RooRealVar *thisParamPreFit;
      TIterator *pdfParamsPreFit = fitModel[iOrder]->getParameters(RooArgSet(*mass,*MH))->selectByAttrib("Constant",kFALSE)->createIterator();
      std::cout << " Values pdf PDF params"<< std::endl;
      while((thisParamPreFit=(RooRealVar*)pdfParamsPreFit->Next())){
          thisParamPreFit->Print("");
      }
      verbosity_ >=3 ?
        fitRes = fitModel[iOrder]->fitTo(*data,NumCPU(ncpu),RooFit::Minimizer("Minuit","minimize"),SumW2Error(true),Save(true),RooFit::ConditionalObservables(*MH)) :
        verbosity_ >=2 ?
        fitRes = fitModel[iOrder]->fitTo(*data,NumCPU(ncpu),RooFit::Minimizer("Minuit","minimize"),SumW2Error(true),Save(true),PrintLevel(-1),RooFit::ConditionalObservables(*MH)) :
        fitRes = fitModel[iOrder]->fitTo(*data,NumCPU(ncpu),RooFit::Minimizer("Minuit","minimize"),SumW2Error(true),Save(true),PrintLevel(-1),PrintEvalErrors(-1),RooFit::ConditionalObservables(*MH));
      fitResults.insert(pair<int,RooFitResult*>(iOrder,fitRes));
      mass->setBins(160); //return to default 
      std::cout << " PARAM VALUES post fit of order " << iOrder << std::endl;
      RooRealVar *thisParamPostFit;
      TIterator *pdfParamsPostFit = fitModel[iOrder]->getParameters(RooArgSet(*mass,*MH))->selectByAttrib("Constant",kFALSE)->createIterator();
      std::cout << " Values pdf PDF params"<< std::endl;
      while((thisParamPostFit=(RooRealVar*)pdfParamsPostFit->Next())){
          thisParamPostFit->Print("");
      }
      int index=0;
      RooPlot *frame = mass->frame(Range(mhLow_-10,mhHigh_+10));
      for (map<int,RooDataSet*>::iterator dataIt=datasets.begin(); dataIt!=datasets.end(); dataIt++){
        int mh=dataIt->first;
        RooAbsData* plotData;
        if (binnedFit_){
          plotData = normaliseDatasets(datasets[mh])->binnedClone();
        } else {
          plotData = normaliseDatasets(datasets[mh]);
        }
        MH->setVal(mh);
        //listOfPolyVars_->Print("V");
        plotData->plotOn(frame,RooFit::MarkerColor(colorList[index]));
        //std::cout <<"DEBUG this is the dataset we are shwoing " << std::endl;
        //plotData->Print();
        fitModel[iOrder]->plotOn(frame,RooFit::ProjWData(*plotData),RooFit::LineColor(colorList[index]));
        //MH->setRange(Form("range%d",mh),mh-1,mh+1);
        index++;
      }
      frame->Draw();
      testlc->SaveAs(Form("%sSimultaneousFitDebug_order%d.pdf",outdir.c_str(),iOrder));
      testlc->SaveAs(Form("%sSimultaneousFitDebug_order%d.png",outdir.c_str(),iOrder));

      TIterator *paramIter = listOfPolyVars_->createIterator();
      RooPolyVar *polyVar;
      while((polyVar=(RooPolyVar*)paramIter->Next())){
        std::cout << " check if TString(polyvar->GetName() " <<polyVar->GetName() << " contains Form(rder%d,iOrder) " << Form("order%d",iOrder)  << " result = " << TString(polyVar->GetName()).Contains(Form("order%d",iOrder)) << std::endl;
        if (!TString(polyVar->GetName()).Contains(Form("order%d",iOrder))) continue;
        TString ppName = TString(polyVar->GetName()).ReplaceAll(Form("_order%d",iOrder),"");
        if (graphs.find(ppName.Data())==graphs.end()) graphs[ppName.Data()]= new TMultiGraph();
       
        TGraph *tg = new TGraph(); int point=0;
        TLatex *latex = new TLatex(); latex->SetTextSize(0.05); latex->SetNDC();
        for (float thisMH=120; thisMH<130.1 ; thisMH=thisMH+0.1){
          MH->setVal(thisMH);
          tg->SetPoint(point,thisMH,polyVar->getVal());
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
        //std::cout << " Check if TString(thisParam->GetName() " << thisParam->GetName() << " contains pName " << ppName << " result " << TString(thisParam->GetName()).Contains(ppName) << std::endl; 
        if (!TString(thisParam->GetName()).Contains(ppName)) continue;
        //std::cout << "Params for polyVar " << polyVar->GetName() << " are "<< Form("%s = %.4f",thisParam->GetName(),thisParam->getVal()) << std::endl;
        latex->DrawLatex(0.50, 0.88-offset,Form("%s = %.6f",thisParam->GetName(),thisParam->getVal()));
        offset=offset+0.07;
        }
        //testlc->SaveAs(Form("%s_polyvar_%s.pdf",outdir.c_str(),polyVar->GetName()));
        //testlc->SaveAs(Form("%s_polyvar_%s.png",outdir.c_str(),polyVar->GetName()));
        
      }
        TIterator *pdfParams = fitModel[iOrder]->getParameters(RooArgSet(*mass,*MH))->selectByAttrib("Constant",kFALSE)->createIterator();
        RooRealVar *thisParam;
        while((thisParam=(RooRealVar*)pdfParams->Next())){
          std::cout << "refining param values: old value "<< std::endl;
          thisParam->Print("");
          double centralValue = thisParam->getVal(); 
          thisParam->setMin(min(thisParam->getVal()*(1-epsilon),(thisParam->getVal()*(1+epsilon))));
          thisParam->setMax(max(thisParam->getVal()*(1-epsilon),(thisParam->getVal()*(1+epsilon))));
          std::cout << "refining param values: new value  to have min  "<< thisParam->getVal()*(1-epsilon) << " max " << thisParam->getVal()*(1+epsilon) << std::endl;
          thisParam->setVal(centralValue);
          thisParam->Print("");
        }
    }
TCanvas *canvas = new TCanvas("c","c",500,500);
for (auto it = graphs.begin() ; it!=graphs.end(); ++it){
it->second->Draw("apl");
TLatex *latex = new TLatex(); latex->SetTextSize(0.05); latex->SetNDC();
latex->DrawLatex(0.16, 0.85,it->first.c_str());
latex->DrawLatex(0.6, 0.83,Form("#color[%d]{Order 0}",colorList[0+2]));
latex->DrawLatex(0.6, 0.75,Form("#color[%d]{Order 1}",colorList[1+2]));
latex->DrawLatex(0.6, 0.67,Form("#color[%d]{Order 2}",colorList[2+2]));
canvas->SaveAs(Form("%s_multigraph_%s.pdf",outdir.c_str(),it->first.c_str()));
canvas->SaveAs(Form("%s_multigraph_%s.png",outdir.c_str(),it->first.c_str()));
}

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


void SimultaneousFit::plotFits(string name, string rvwv){

  TCanvas *canv = new TCanvas();
  RooPlot *plot = mass->frame(Range(mhLow_-10,mhHigh_+10));
  TPaveText *pt = new TPaveText(.65,.6,.97,.95,"NDC");
  std::vector<int> colorList ={7,9,4,2,8,5,1,14};
  for (unsigned int i=0; i<allMH_.size(); i++){
    int mh = allMH_[i];
    std::cout << "LC DEBUG what MH "<< mh << std::endl;
    MH->setConstant(false);
    MH->setVal(mh);
    MH->setConstant(true);
    //assert(sumOfGaussians.find(mh)!=sumOfGaussians.end());
    assert(datasets.find(mh)!=datasets.end());
    RooAddPdf *fitModel = sumOfGaussians[2];
    //RooDataSet *data = datasets[mh];
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
  /*
     TIterator *paramIter = listOfPolyVars_->createIterator();
     RooPolyVar *polyVar;
     while((polyVar=(RooPolyVar*)paramIter->Next())){
     TGraph *tg = new TGraph(); int point=0;
     TLatex *latex = new TLatex(); latex->SetTextSize(0.038); latex->SetNDC();
     for (float thisMH=120; thisMH<130.1 ; thisMH=thisMH+0.1){
     MH->setVal(thisMH);
     tg->SetPoint(point,thisMH,polyVar->getVal());
     point++;
     }
     latex->DrawLatex(0.16, 0.88,polyVar->GetName());
     tg->Draw("ACE");
     canv->SaveAs(Form("%s_polyvar_%s.pdf",name.c_str(),polyVar->GetName()));
     canv->SaveAs(Form("%s_polyvar_%s.png",name.c_str(),polyVar->GetName()));
     }*/
  delete canv;
}

std::map<std::string,RooSpline1D*> SimultaneousFit::getSplines(){

  int chosenOrder=2;
  std::map<std::string,RooSpline1D*> splines;

  TIterator *paramIter = listOfPolyVars_->createIterator();
  RooPolyVar *polyVar;
  while((polyVar=(RooPolyVar*)paramIter->Next())){
    TString pvName = TString(polyVar->GetName()).ReplaceAll(Form("_order%d",chosenOrder),"");
    polyVar->SetName(pvName);
    polyVar->SetTitle(pvName);
    vector<double> xValues;
    vector<double> yValues;
    for (float thisMH=120; thisMH<130.1 ; thisMH=thisMH+0.1){
      MH->setVal(thisMH);
      xValues.push_back(thisMH);
      yValues.push_back(polyVar->getVal());
    }
    RooSpline1D *thisSpline = new RooSpline1D(polyVar->GetName(),polyVar->GetName(),*MH,xValues.size(),&(xValues[0]),&(yValues[0]));
    splines.insert(pair<string,RooSpline1D*>(thisSpline->GetName(),thisSpline));
    std::cout << "DEBUG made spline for RooPolyVar " << thisSpline->GetName() << std::endl;
    TGraph * graph = new TGraph();
    TCanvas *c = new TCanvas("c","c",500,500);
    int index=0;
    for (float thisMH=120; thisMH<130.1 ; thisMH=thisMH+0.1){
    MH->setVal(thisMH);
    graph->SetPoint(index,thisMH,thisSpline->getVal());
    index++;
    }
    graph->Draw("ALP*");
    c->SaveAs(Form("%sssf_splines_%s_%s_%s.png",outdir_.c_str(),polyVar->GetName(),proc_.c_str(),cat_.c_str()));
    c->SaveAs(Form("%sssf_splines_%s_%s_%s.pdf",outdir_.c_str(),polyVar->GetName(),proc_.c_str(),cat_.c_str()));
  }
  return splines;
}
