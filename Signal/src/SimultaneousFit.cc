#include <fstream>

#include "TCanvas.h"
#include "TMath.h"
#include "RooPlot.h"
#include "RooPolyVar.h"
#include "TColor.h"
#include "RooFormulaVar.h"
#include "RooMsgService.h"
#include "TPaveText.h"

#include "boost/lexical_cast.hpp"

#include "../interface/SimultaneousFit.h"

using namespace std;
using namespace RooFit;

SimultaneousFit::SimultaneousFit(RooRealVar *massVar, RooRealVar *MHvar, int mhLow, int mhHigh, vector<int> skipMasses, bool binnedFit, int bins, std::vector<int> massList):
  mass(massVar),
  MH(MHvar),
  mhLow_(mhLow),
  mhHigh_(mhHigh),
	skipMasses_(skipMasses),
  verbosity_(0),
  binnedFit_(binnedFit),
  bins_(bins)
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


RooDataSet* SimultaneousFit::mergeDatasets(map<int,RooDataSet*> data){
  
  // prepare the holder for the merged data, which is a 2D dataset of mass and MH
  RooDataSet* result = new RooDataSet("mergedDataset","mergedDataset",RooArgSet(*mass,*MH));
  
  //loop over vector of datasets for different MH values
  for (map<int,RooDataSet*>::iterator dataIt=data.begin(); dataIt!=data.end(); dataIt++){
    
    //for each mass point, loop through the entries in the dataset
    for (int iEntry=0; iEntry<dataIt->second->numEntries() ; iEntry++){
      
      //set the mass to the value of the entry in the dataset
      mass->setVal(dataIt->second->get(iEntry)->getRealValue(mass->GetName()));
      
      //set the MH to the relevant value for this dataste
      MH->setVal(dataIt->first);
      
      if (iEntry%100==0) std::cout << "LC DEBUG SimultaneousFit::mergeDatasets adding entry MH=" << MH->getVal() << " mass=" << mass->getVal() << std::endl;
      // add a row to the dataset for this entry
      result->add(RooArgSet(*mass,*MH));
    }
  }
  //and simpyl return the merged dataset
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

void SimultaneousFit::buildSumOfGaussians(string name, int nGaussians, bool recursive, bool forceFracUnity){

    RooArgList *gaussians = new RooArgList();
    RooArgList *coeffs = new RooArgList();
    map<string,RooRealVar*> tempFitParams;
    map<string,RooAbsReal*> tempFitUtils;
    map<string,RooGaussian*> tempGaussians;
    
    for (int g=0; g<nGaussians; g++){
      //RooRealVar *dm = new RooRealVar(Form("dm_mh%d_g%d",mh,g),Form("dm_mh%d_g%d",mh,g),0.1,-8.,8.);
      float dmRange =3.;
      if (g>3) dmRange=3.;
      RooFormulaVar *dMH = new RooFormulaVar(Form("dMH"),Form("dMH",g),"@0-125.0",RooArgList(*MH));
      //RooRealVar *mean_p0 = new RooRealVar(Form("mean_p0_g%d",g),Form("mean_p0_g%d",g),124.2,35,214);
      //RooRealVar *mean_p1 = new RooRealVar(Form("mean_p1_g%d",g),Form("mean_p1_g%d",g),0.01,-0.7,0.7);
      //ooPolyVar *mean = new RooPolyVar(Form("mean_g%d",g),Form("mean_g%d",g),*MH,RooArgList(*mean_p0,*mean_p1));
      RooRealVar *dm_p0 = new RooRealVar(Form("dm_p0_g%d",g),Form("dm_p0_g%d",g),-0.25,-24.0,24.0);
      RooRealVar *dm_p1 = new RooRealVar(Form("dm_p1_g%d",g),Form("dm_p1_g%d",g),0.001,-0.1,0.1);
      RooPolyVar *dm = new RooPolyVar(Form("dm_g%d",g),Form("dm_g%d",g),*MH,RooArgList(*dm_p0,*dm_p1));
      //RooRealVar *dm = new RooRealVar(Form("dm_mh%d_g%d",mh,g),Form("dm_mh%d_g%d",mh,g),0.1,-dmRange,dmRange);
      RooFormulaVar *mean = new RooFormulaVar(Form("mean_g%d",g),Form("mean_g%d",g),"((@0+@1))",RooArgList(*MH,*dm));
      RooRealVar *sigma_p0 = new RooRealVar(Form("sigma_p0_g%d",g),Form("sigma_p0_g%d",g),1.6,-1.5,4.5);
      RooRealVar *sigma_p1 = new RooRealVar(Form("sigma_p1_g%d",g),Form("sigma_p1_g%d",g),0.001,-0.03,0.03);
      //RooFormulaVar *sigma = new RooFormulaVar(Form("sigma_g%d",g),Form("sigma_g%d",g),"((@0-125.0)*@1+@2)",RooArgList(*MH,*sigma_p1,*sigma_p0));
      //RooRealVar *sigma = new RooRealVar(Form("sigma_g%d",g),Form("sigma_g%d",g),-5);
      RooPolyVar *sigma = new RooPolyVar(Form("sigma_g%d",g),Form("sigma_g%d",g),*MH,RooArgList(*sigma_p0,*sigma_p1));
      RooGaussian *gaus = new RooGaussian(Form("gaus_g%d",g),Form("gaus_g%d",g),*mass,*mean,*sigma);
      //tempFitParams.insert(pair<string,RooRealVar*>(string(dm->GetName()),dm));
      //tempFitParams.insert(pair<string,RooRealVar*>(string(sigma->GetName()),sigma));
      //tempFitUtils.insert(pair<string,RooAbsReal*>(string(mean->GetName()),mean));
      tempGaussians.insert(pair<string,RooGaussian*>(string(gaus->GetName()),gaus));
      gaussians->add(*gaus);
      listOfPolyVars_->add(*mean);
      listOfPolyVars_->add(*sigma);
      if (g<nGaussians-1) {
      RooRealVar *frac_p0 = new RooRealVar(Form("frac_p0_g%d",g),Form("frac_p0_g%d",g),0.4,-2.5,3.3);
      RooRealVar *frac_p1 = new RooRealVar(Form("frac_p1_g%d",g),Form("frac_p1_g%d",g),-0.001,-0.02,0.02);
      //RooFormulaVar *frac = new RooFormulaVar(Form("frac_g%d",g),Form("frac_g%d",g),"abs((@0-125.0)*@1+@2)",RooArgList(*MH,*frac_p1,*frac_p0));
      RooPolyVar *frac = new RooPolyVar(Form("frac_g%d",g),Form("frac_g%d",g),*MH,RooArgList(*frac_p0,*frac_p1));
      // RooPolyVar *frac = new RooPolyVar(Form("frac_g%d",g),Form("frac_g%d",g),*MH,RooArgList(*frac_p0));
        //tempFitParams.insert(pair<string,RooRealVar*>(string(frac->GetName()),frac));
        listOfPolyVars_->add(*frac);
      //RooRealVar *frac = new RooRealVar(Form("frac_g%d",g),Form("frac_g%d",g),0.3);
      coeffs->add(*frac);
      }
      if (g==nGaussians-1 && forceFracUnity){
        string formula="1.";
        for (int i=0; i<nGaussians-1; i++) formula += Form("-@%d",i);
        RooAbsReal *recFrac = new RooFormulaVar(Form("frac_rec_g%d",g),Form("frac_rec_g%d",g),formula.c_str(),*coeffs);
        //tempFitUtils.insert(pair<string,RooAbsReal*>(string(recFrac->GetName()),recFrac));
        coeffs->add(*recFrac);
      }
    }
    assert(gaussians->getSize()==nGaussians && coeffs->getSize()==nGaussians-(1*!forceFracUnity));
    RooAddPdf *tempSumOfGaussians = new RooAddPdf(Form("%s",name.c_str()),Form("%s",name.c_str()),*gaussians,*coeffs,recursive);
    std::cout << "LC DEBUG final sumGaus params"<< std::endl;
    coeffs->Print("V");
    sumOfGaussians.insert(pair<int,RooAddPdf*>(0,tempSumOfGaussians));
    //fitParams.insert(pair<int,map<string,RooRealVar*> >(0,tempFitParams));
    //fitUtils.insert(pair<int,map<string,RooAbsReal*> >(0,tempFitUtils));
    initialGaussians.insert(pair<int,map<string,RooGaussian*> >(0,tempGaussians));
  
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

void SimultaneousFit::runFits(int ncpu){

    MH->setConstant(false);
    RooAddPdf *fitModel = sumOfGaussians[0];
    RooDataSet *dataRaw = mergeDatasets(datasets);
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
    RooFitResult *fitRes;
    mass->setBins(bins_);
    verbosity_ >=3 ?
       fitRes = fitModel->fitTo(*data,NumCPU(ncpu),RooFit::Minimizer("Minuit","minimize"),SumW2Error(true),Save(true),RooFit::ConditionalObservables(*MH)) :
       verbosity_ >=2 ?
       fitRes = fitModel->fitTo(*data,NumCPU(ncpu),RooFit::Minimizer("Minuit","minimize"),SumW2Error(true),Save(true),PrintLevel(-1),RooFit::ConditionalObservables(*MH)) :
       fitRes = fitModel->fitTo(*data,NumCPU(ncpu),RooFit::Minimizer("Minuit","minimize"),SumW2Error(true),Save(true),PrintLevel(-1),PrintEvalErrors(-1),RooFit::ConditionalObservables(*MH));
    fitResults.insert(pair<int,RooFitResult*>(0,fitRes));
    mass->setBins(160); //return to default 

    fitRes->floatParsFinal().Print("V");
    
     TCanvas *testlc = new TCanvas("c","c",500,500);
    //just for debug for now
     std::vector<int> colorList ={7,9,4,2,8,5,1,14};//kCyan,kMagenta,kBlue, kRed,kGreen,kYellow,kBlack, kGray};
    int index=0;
    RooPlot *frame = mass->frame();
    for (map<int,RooDataSet*>::iterator dataIt=datasets.begin(); dataIt!=datasets.end(); dataIt++){
    int mh=dataIt->first;
    std::cout << "LC DEBUG values of polyvars at mh=" << mh << std::endl;
    RooAbsData* plotData;
    if (binnedFit_){
       plotData = datasets[mh]->binnedClone();
     } else {
         plotData = datasets[mh];
     }
    MH->setVal(mh);
    listOfPolyVars_->Print("V");
    plotData->plotOn(frame,RooFit::MarkerColor(colorList[index]));
    fitModel->plotOn(frame,RooFit::ProjWData(*plotData),RooFit::LineColor(colorList[index]));
    //MH->setRange(Form("range%d",mh),mh-1,mh+1);
    index++;
    }
    frame->Draw();
    testlc->SaveAs("SimultenousFitDebug.pdf");
    exit(1);

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
  std::vector<int> colorList ={7,9,4,2,8,5,1,14};//kCyan,kMagenta,kBlue, kRed,kGreen,kYellow,kBlack, kGray};
  for (unsigned int i=0; i<allMH_.size(); i++){
    int mh = allMH_[i];
    MH->setConstant(false);
    MH->setVal(mh);
    MH->setConstant(true);
    assert(sumOfGaussians.find(mh)!=sumOfGaussians.end());
    assert(datasets.find(mh)!=datasets.end());
    RooAddPdf *fitModel = sumOfGaussians[mh];
    //RooDataSet *data = datasets[mh];
    mass->setBins(bins_);
    RooDataHist *data = new RooDataHist(datasets[mh]->GetName(),datasets[mh]->GetName(), RooArgSet(*mass),*datasets[mh]);
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
