#include <fstream>

#include "TCanvas.h"
#include "TH2.h"
#include "TMath.h"
#include "RooPlot.h"
#include "TColor.h"
#include "RooFormulaVar.h"
#include "RooMsgService.h"
#include "TPaveText.h"
#include <RooCBShape.h>
#include "HiggsAnalysis/GBRLikelihood/interface/RooDoubleCBFast.h" 

#include "boost/lexical_cast.hpp"

#include "../interface/InitialFit.h"

using namespace std;
using namespace RooFit;

InitialFit::InitialFit(RooRealVar *massVar, RooRealVar *MHvar, int mhLow, int mhHigh, vector<int> skipMasses, bool binnedFit, int bins, std::vector<int> massList):
  mass(massVar),
  MH(MHvar),
  mhLow_(mhLow),
  mhHigh_(mhHigh),
	skipMasses_(skipMasses),
  verbosity_(0),
  binnedFit_(binnedFit),
  bins_(bins)
{ 
  if (massList.size()==0){
    allMH_ = getAllMH();
  }else{
    allMH_ = massList;
  }
}

InitialFit::~InitialFit(){}

bool InitialFit::skipMass(int mh){
	for (vector<int>::iterator it=skipMasses_.begin(); it!=skipMasses_.end(); it++) {
		if (*it==mh) return true;
	}
	return false;
}

vector<int> InitialFit::getAllMH(){
  vector<int> result;
  for (int m=mhLow_; m<=mhHigh_; m+=5){
		if (skipMass(m)) continue;
    if (verbosity_>=1) cout << "[INFO] LinearInterp - Adding mass: " << m << endl;
    result.push_back(m);
  }
  return result;
}

void InitialFit::setVerbosity(int v){
  if (v<2) {
    RooMsgService::instance().setGlobalKillBelow(RooFit::ERROR);
    RooMsgService::instance().setSilentMode(true);
  }
  verbosity_=v;
}

void InitialFit::setDatasets(map<int,RooDataSet*> data){
  datasets = data; // original dataset or a replacement one if needed.
}

void InitialFit::setDatasetsSTD(map<int,RooDataSet*> data){
  datasetsSTD = data; //original dataset, not the replacement one!!
}

void InitialFit::addDataset(int mh, RooDataSet *data){
  assert(data);
  datasets.insert(pair<int,RooDataSet*>(mh,data));
}

// this method builds the DCB plus 1 Gaussian with same mean
void InitialFit::buildDCBplusGaussian(string name){
  
  for (unsigned int i=0; i<allMH_.size(); i++){
    int mh = allMH_[i];
    MH->setConstant(false);
    MH->setVal(mh);
    MH->setConstant(true);
    map<string,RooRealVar*> tempFitParams;
    map<string,RooAbsReal*> tempFitUtils;
    map<string,RooAbsPdf*> tempGaussians;
    RooRealVar*dm_dcb = new RooRealVar(Form("dm_mh%d_dcb",mh),Form("dm_mh%d_dcb",mh), 0.,-5.,5.);
    RooAbsReal *mean_dcb = new RooFormulaVar(Form("mean_mh%d_dcb",mh),Form("mean_mh%d_dcb",mh),"@0+@1",RooArgList(*MH,*dm_dcb));
    RooRealVar *sigma_dcb = new RooRealVar(Form("sigma_mh%d_dcb",mh),Form("sigma_mh%d_dcb",mh), 2., 1.0, 20.);
    RooRealVar *a1_dcb = new RooRealVar(Form("a1_mh%d_dcb",mh),Form("a1_mh%d_dcb",mh), 5., 0.01, 100.);   
    RooRealVar *a2_dcb = new RooRealVar(Form("a2_mh%d_dcb",mh),Form("a2_mh%d_dcb",mh), 5., 0.01, 100.);   
    RooRealVar *n1_dcb = new RooRealVar(Form("n1_mh%d_dcb",mh),Form("n1_mh%d_dcb",mh), 20.,2.0001,500.);
    RooRealVar *n2_dcb = new RooRealVar(Form("n2_mh%d_dcb",mh),Form("n2_mh%d_dcb",mh), 20.,2.0001,500);
    RooAbsPdf *pdf_dcb = new RooDoubleCBFast(Form("dcb_mh%d",mh),Form("dcb_mh%d",mh), *mass,*mean_dcb,*sigma_dcb, *a1_dcb, *n1_dcb, *a2_dcb, *n2_dcb);
    //RooRealVar*dm_gaus = new RooRealVar(Form("dm_mh%d_gaus",mh),Form("dm_mh%d_gaus",mh), 0.,-5.,5.);
    //RooAbsReal *mean_gaus = new RooFormulaVar(Form("mean_mh%d_gaus%d",mh,g),Form("mean_mh%d_gaus%d",mh,g),"@0+@1",RooArgList(*MH,*dm_gaus));
    RooRealVar *sigma_gaus = new RooRealVar(Form("sigma_mh%d_gaus",mh),Form("sigma_mh%d_gaus",mh),2.,1.0,3.); 
    RooGaussian *pdf_gaus = new RooGaussian(Form("gaus_mh%d",mh),Form("gaus_mh%d",mh),*mass,*mean_dcb,*sigma_gaus);// use same mean as for DCB
    RooRealVar *frac_gaus = new RooRealVar(Form("frac_mh%d",mh),Form("frac_mh%d",mh),0.5,0.01,0.99);
    RooAddPdf *pdf = new RooAddPdf(Form("%s_mh%d",name.c_str(),mh),Form("%s_mh%d",name.c_str(),mh),*pdf_dcb,*pdf_gaus,*frac_gaus);
    
    //tempFitParams.insert(pair<string,RooRealVar*>(string(dm_gaus->GetName()),dm_gaus));
    tempFitParams.insert(pair<string,RooRealVar*>(string(sigma_gaus->GetName()),sigma_gaus));
    tempFitParams.insert(pair<string,RooRealVar*>(string(dm_dcb->GetName()),dm_dcb));
    tempFitParams.insert(pair<string,RooRealVar*>(string(sigma_dcb->GetName()),sigma_dcb));
    tempFitParams.insert(pair<string,RooRealVar*>(string(frac_gaus->GetName()),frac_gaus));
    tempFitParams.insert(pair<string,RooRealVar*>(string(n1_dcb->GetName()),n1_dcb));
    tempFitParams.insert(pair<string,RooRealVar*>(string(n2_dcb->GetName()),n2_dcb));
    tempFitParams.insert(pair<string,RooRealVar*>(string(a1_dcb->GetName()),a1_dcb));
    tempFitParams.insert(pair<string,RooRealVar*>(string(a2_dcb->GetName()),a2_dcb));
    
    fitPdfs.insert(pair<int,RooAbsPdf*>(mh,pdf));
    fitParams.insert(pair<int,map<string,RooRealVar*> >(mh,tempFitParams));
  }
}


void InitialFit::buildSumOfGaussians(string name, int nGaussians, bool recursive, bool forceFracUnity){

  for (unsigned int i=0; i<allMH_.size(); i++){
    int mh = allMH_[i];
    MH->setConstant(false);
    MH->setVal(mh);
    MH->setConstant(true);
    RooArgList *gaussians = new RooArgList();
    RooArgList *coeffs = new RooArgList();
    map<string,RooRealVar*> tempFitParams;
    map<string,RooAbsReal*> tempFitUtils;
    map<string,RooGaussian*> tempGaussians;
    
    for (int g=0; g<nGaussians; g++){
      //RooRealVar *dm = new RooRealVar(Form("dm_mh%d_g%d",mh,g),Form("dm_mh%d_g%d",mh,g),0.1,-8.,8.);
      float dmRange =3.;
      if (g>3) dmRange=3.;
      RooRealVar *dm = new RooRealVar(Form("dm_mh%d_g%d",mh,g),Form("dm_mh%d_g%d",mh,g),0.1,-dmRange,dmRange);
      RooAbsReal *mean = new RooFormulaVar(Form("mean_mh%d_g%d",mh,g),Form("mean_mh%d_g%d",mh,g),"@0+@1",RooArgList(*MH,*dm));
      //RooRealVar *sigma = new RooRealVar(Form("sigma_mh%d_g%d",mh,g),Form("sigma_mh%d_g%d",mh,g),2.,0.4,20.);
      RooRealVar *sigma = new RooRealVar(Form("sigma_mh%d_g%d",mh,g),Form("sigma_mh%d_g%d",mh,g),1.*(g+1),0.4,20.);
      RooGaussian *gaus = new RooGaussian(Form("gaus_mh%d_g%d",mh,g),Form("gaus_mh%d_g%d",mh,g),*mass,*mean,*sigma);
      tempFitParams.insert(pair<string,RooRealVar*>(string(dm->GetName()),dm));
      tempFitParams.insert(pair<string,RooRealVar*>(string(sigma->GetName()),sigma));
      tempFitUtils.insert(pair<string,RooAbsReal*>(string(mean->GetName()),mean));
      tempGaussians.insert(pair<string,RooGaussian*>(string(gaus->GetName()),gaus));
      gaussians->add(*gaus);
      if (g<nGaussians-1) {
        RooRealVar *frac = new RooRealVar(Form("frac_mh%d_g%d",mh,g),Form("frac_mh%d_g%d",mh,g),0.1,0.01,0.99);
        tempFitParams.insert(pair<string,RooRealVar*>(string(frac->GetName()),frac));
        coeffs->add(*frac);
      }
      if (g==nGaussians-1 && forceFracUnity){
        string formula="1.";
        for (int i=0; i<nGaussians-1; i++) formula += Form("-@%d",i);
        RooAbsReal *recFrac = new RooFormulaVar(Form("frac_mh%d_g%d",mh,g),Form("frac_mh%d_g%d",mh,g),formula.c_str(),*coeffs);
        tempFitUtils.insert(pair<string,RooAbsReal*>(string(recFrac->GetName()),recFrac));
        coeffs->add(*recFrac);
      }
    }
    assert(gaussians->getSize()==nGaussians && coeffs->getSize()==nGaussians-(1*!forceFracUnity));
    RooAbsPdf *tempSumOfGaussians = new RooAddPdf(Form("%s_mh%d",name.c_str(),mh),Form("%s_mh%d",name.c_str(),mh),*gaussians,*coeffs,recursive);
    fitPdfs.insert(pair<int,RooAbsPdf*>(mh,tempSumOfGaussians));
    fitParams.insert(pair<int,map<string,RooRealVar*> >(mh,tempFitParams));
    fitUtils.insert(pair<int,map<string,RooAbsReal*> >(mh,tempFitUtils));
    initialGaussians.insert(pair<int,map<string,RooGaussian*> >(mh,tempGaussians));
  }
}

void InitialFit::loadPriorConstraints(string filename, float constraintValue){

  ifstream datfile;
  std::cout << "LC DEBUG  InitialFit::loadPriorConstraints a" << std::endl; 
  datfile.open(filename.c_str());
  std::cout << "LC DEBUG  InitialFit::loadPriorConstraints b" << std::endl; 
  if (datfile.fail()) return;
  std::cout << "LC DEBUG  InitialFit::loadPriorConstraints c" << std::endl; 
  while (datfile.good()) {
  std::cout << "LC DEBUG  InitialFit::loadPriorConstraints d" << std::endl; 
    string line;
  std::cout << "LC DEBUG  InitialFit::loadPriorConstraints e" << std::endl; 
    getline(datfile,line);
  std::cout << "LC DEBUG  InitialFit::loadPriorConstraints f" << std::endl; 
    if (line=="\n" || line.substr(0,1)=="#" || line==" " || line.empty()) continue;
  std::cout << "LC DEBUG  InitialFit::loadPriorConstraints g" << std::endl; 
    string name = line.substr(0,line.find_first_of(" "));
  std::cout << "LC DEBUG  InitialFit::loadPriorConstraints h" << std::endl; 
    double val = boost::lexical_cast<double>(line.substr(line.find_first_of(" ")+1,string::npos));
  std::cout << "LC DEBUG  InitialFit::loadPriorConstraints i" << name.substr(name.find("_mh")+3,name.find("_g")-name.find("_mh")-3) << std::endl; 
    int mhS = boost::lexical_cast<int>(name.substr(name.find("_mh")+3,name.find("_g")-name.find("_mh")-3));
  std::cout << "LC DEBUG  InitialFit::loadPriorConstraints j" << std::endl; 
    if (verbosity_>=2) cout << "[INFO] "<< name << " " << mhS << " " << val << endl;
  std::cout << "LC DEBUG  InitialFit::loadPriorConstraints k" << std::endl; 
    assert(fitParams.find(mhS)!=fitParams.end());
  std::cout << "LC DEBUG  InitialFit::loadPriorConstraints l" << std::endl; 
    assert(fitParams[mhS].find(name)!=fitParams[mhS].end());
  std::cout << "LC DEBUG  InitialFit::loadPriorConstraints m" << std::endl; 
    fitParams[mhS][name]->setVal(val);
  std::cout << "LC DEBUG  InitialFit::loadPriorConstraints n" << std::endl; 
    if (val>0.) fitParams[mhS][name]->setRange((1.-constraintValue)*val,(1.+constraintValue)*val);
    else fitParams[mhS][name]->setRange((1.+constraintValue)*val,(1.-constraintValue)*val);
  }
  datfile.close();
}

void InitialFit::saveParamsToFile(string filename){
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

void InitialFit::saveParamsToFileAtMH(string filename, int setMH){
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

map<int,map<string,RooRealVar*> > InitialFit::getFitParams(){
  return fitParams;
}

void InitialFit::printFitParams(){
	cout << "[INFO] Printing fit param map: " << endl;
	for (map<int,map<string,RooRealVar*> >::iterator it = fitParams.begin(); it != fitParams.end(); it++){
		for (map<string,RooRealVar*>::iterator it2 = it->second.begin(); it2 != it->second.end(); it2++){
			cout << it->first << " : " << it2->first << " -- " << it2->second->getVal() << endl; 
		}
	}
}

void InitialFit::runFits(int ncpu){

  int ngausmax = 10; //we assume that we never use more than 10 (very safe) gaussians for a single dataset
    float n_sigma_constraint = 2.; //constrain sigmas of gaussians at mh!=125 to the values fitted at mh=125, within n_sigma_constraint times the fit uncertainty
    //middle point is assumed to be 125 GeV
    int mh = allMH_[(allMH_.size()+1)/2 - 1];
    //  int mh = 125;
    std::cout<<"RUNNING FITS for mh = "<<mh<<std::endl;
    MH->setConstant(false);
    MH->setVal(mh);
    MH->setConstant(true);
    assert(fitPdfs.find(mh)!=fitPdfs.end());
    assert(datasets.find(mh)!=datasets.end());
    RooAbsPdf *fitModel125 = fitPdfs[mh];
    //RooDataSet *data125 = datasets[mh];
    RooAbsData *data125;
    if (binnedFit_){
       data125 = datasets[mh]->binnedClone();
     } else {
         data125 = datasets[mh];
       }
    // help when dataset has no entries
     if (data125->sumEntries()<1.e-5) {
         mass->setVal(mh);
         data125->add(RooArgSet(*mass),1.e-5);
       }
    //fitModel125->Print();
    //data125->Print();
    
    RooFitResult *fitRes125;
    mass->setBins(bins_);
    verbosity_ >=3 ?
       fitRes125 = fitModel125->fitTo(*data125,NumCPU(ncpu),RooFit::Minimizer("Minuit","minimize"),SumW2Error(true),Save(true)) :
       verbosity_ >=2 ?
       fitRes125 = fitModel125->fitTo(*data125,NumCPU(ncpu),RooFit::Minimizer("Minuit","minimize"),SumW2Error(true),Save(true),PrintLevel(-1)) :
       fitRes125 = fitModel125->fitTo(*data125,NumCPU(ncpu),RooFit::Minimizer("Minuit","minimize"),SumW2Error(true),Save(true),PrintLevel(-1),PrintEvalErrors(-1));
    fitResults.insert(pair<int,RooFitResult*>(mh,fitRes125));
    mass->setBins(160); //return to default 

    //fitRes125->floatParsFinal().Print("V");

    for (unsigned int i=0; i<allMH_.size(); i++){
      //int mh = allMH_[i];
      if( i == (allMH_.size()+1)/2 -1 ) continue;
      // if( allMH_[i] == 125 ) continue;
      mh = allMH_[i];
      std::cout<<"RUNNING FITS for mh = "<<mh<<std::endl;
      MH->setConstant(false);
      MH->setVal(mh);
      MH->setConstant(true);
      assert(fitPdfs.find(mh)!=fitPdfs.end());
      assert(datasets.find(mh)!=datasets.end());
      RooAbsPdf *fitModel = fitPdfs[mh];
      //RooDataSet *data = datasets[mh];



         //fitModel->Print();
         RooArgSet* comps = fitModel->getComponents();
         TIterator* iter = comps->createIterator();
         RooGaussian* nextg = (RooGaussian*)iter->Next();
         //    while(nextg){
            //std::cout<<"Print:"<<std::endl;
           //nextg->Print();
           RooArgSet* formulaMean = nextg->getParameters(*mass);
          // std::cout<<"Print formulamean:"<<std::endl;
          // formulaMean->Print();
           for(int ng=0; ng<ngausmax; ng++){
      
        //  RooAbsArg* dm = formulaMean->find(Form("dm_mh%d_g%d",mh,ng ));
      // if(dm!=NULL){
        //    dm->Print();
      // }
       RooRealVar* sigma = (RooRealVar*)formulaMean->find(Form("sigma_mh%d_g%d",mh,ng ));
      if(sigma!=NULL){
          //sigma->Print();
         float mh125_sigma_val = ((RooRealVar*)fitRes125->floatParsFinal().find(  Form("sigma_mh125_g%d",ng )  ))->getVal();
         float mh125_sigmaerr =((RooRealVar*)fitRes125->floatParsFinal().find(  Form("sigma_mh125_g%d",ng ))) ->getError() ;
         sigma->setVal( mh125_sigma_val );
         float allowedRange = n_sigma_constraint*mh125_sigmaerr;
         if (n_sigma_constraint*mh125_sigmaerr > 0.05* mh125_sigma_val) {allowedRange= 0.05* mh125_sigma_val;}

         sigma->setRange( TMath::Max(mh125_sigma_val - allowedRange,sigma->getMin()) ,TMath::Min(mh125_sigma_val + allowedRange,sigma->getMax()));
         // std::cout <<"[INFO] MH " << mh << ": fit params sigma for gaussian_"<< ng << " set to be 125 value " << mh125_sigma_val << " + "<< mh125_sigmaerr << " - "<< mh125_sigmaerr  << std::endl;   
         //sigma->Print();
        }
      else{
          std::cout<<"Constraints set on sigmas of "<<ng-1<<" gaussians of this model"<<std::endl;
         break;
        }
       std::cout <<  "LC DEBUG DEBUG DEBUG A" << std::endl;
       RooRealVar* dm = (RooRealVar*)formulaMean->find(Form("dm_mh%d_g%d",mh,ng ));
      if(dm!=NULL){
         //dm->Print();
         float mh125_dm_val = ((RooRealVar*)fitRes125->floatParsFinal().find(  Form("dm_mh125_g%d",ng )  ))->getVal();
         float mh125_dmerr =((RooRealVar*)fitRes125->floatParsFinal().find(  Form("dm_mh125_g%d",ng ))) ->getError() ;
         //if (mh125_dmerr >3.0) { mh125_dmerr=3.0 ;}
         dm->setVal( mh125_dm_val );
         //dm->setRange( mh125_dm_val - n_sigma_constraint*mh125_dmerr ,  mh125_dm_val + n_sigma_constraint*mh125_dmerr);
         float allowedRange = n_sigma_constraint*mh125_dmerr;
         if (n_sigma_constraint*mh125_dmerr > 0.05* mh125_dm_val) {allowedRange= 0.05* mh125_dm_val;}

         dm->setRange( TMath::Max(mh125_dm_val - allowedRange,dm->getMin()) ,TMath::Min(mh125_dm_val + allowedRange,dm->getMax()));
         // std::cout <<" [INFO] MH " << mh << ": fit params dm for gaussian_"<< ng << " set to be 125 value " << mh125_dm_val << " + "<< mh125_dmerr << " - "<< mh125_dmerr  << std::endl;   
         //dm->Print();
        }
      else{
          std::cout<<"Constraints set on dms of "<<ng-1<<" gaussians of this model"<<std::endl;
         break;
        }
       
       
       std::cout <<  "LC DEBUG DEBUG DEBUG B" << std::endl;
       RooRealVar* frac = (RooRealVar*)formulaMean->find(Form("frac_mh%d_g%d",mh,ng ));
      if(frac!=NULL){
          //frac->Print();
         float mh125_frac_val = ((RooRealVar*)fitRes125->floatParsFinal().find(  Form("frac_mh125_g%d",ng )  ))->getVal();
         float mh125_fracerr =((RooRealVar*)fitRes125->floatParsFinal().find(  Form("frac_mh125_g%d",ng ))) ->getError() ;
         if (mh125_fracerr >0.5) { mh125_fracerr=.5 ;}
         frac->setVal( mh125_frac_val );
         //frac->setRange( mh125_frac_val - n_sigma_constraint*mh125_fracerr ,  mh125_frac_val + n_sigma_constraint*mh125_fracerr);
         float allowedRange = n_sigma_constraint*mh125_fracerr;
         if (n_sigma_constraint*mh125_fracerr > 0.05* mh125_frac_val) {allowedRange= 0.05* mh125_frac_val;}
         frac->setRange( TMath::Max(mh125_frac_val - allowedRange,frac->getMin()) ,TMath::Min(mh125_frac_val + allowedRange,frac->getMax()));
          //std::cout <<"[INFO] MH " << mh << ": fit params frac for gaussian_"<< ng << " set to be 125 value " << mh125_frac_val << " + "<< mh125_fracerr << " - "<< mh125_fracerr  << std::endl;   
         //frac->Print();
        }
      else{
          std::cout<<"Constraints set on fracs of "<<ng-1<<" gaussians of this model"<<std::endl;
         break;
        }
       std::cout <<  "LC DEBUG DEBUG DEBUG C" << std::endl;
           }
       std::cout <<  "LC DEBUG DEBUG DEBUG D" << std::endl;
     
            
      //      RooArgSet* actualvars = formulaMean->getComponents();
     //      TIterator* iterFormula = actualvars->createIterator();
     //      RooAbsReal* nextVar = (RooAbsReal*)iterFormula->Next();
     //      while(nextVar){
      //  nextVar->Print();
     // nextVar = (RooAbsReal*)iterFormula->Next();
     //  
        //      }
    //      nextg = (RooGaussian*)iter->Next();
    //    }



    RooAbsData *data;
    if (binnedFit_){
      data = datasets[mh]->binnedClone();
    } else {
      data = datasets[mh];
    }
    // help when dataset has no entries
    if (data->sumEntries()<1.e-5) {
      mass->setVal(mh);
      data->add(RooArgSet(*mass),1.e-5);
    }
       std::cout <<  "LC DEBUG DEBUG DEBUG E" << std::endl;
    //fitModel->Print();
    //data->Print();
    RooFitResult *fitRes;
    mass->setBins(bins_);
    verbosity_ >=3 ?
      fitRes = fitModel->fitTo(*data,NumCPU(ncpu),RooFit::Minimizer("Minuit","minimize"),SumW2Error(true),Save(true)) :
      verbosity_ >=2 ?
      fitRes = fitModel->fitTo(*data,NumCPU(ncpu),RooFit::Minimizer("Minuit","minimize"),SumW2Error(true),Save(true),PrintLevel(-1)) :
      fitRes = fitModel->fitTo(*data,NumCPU(ncpu),RooFit::Minimizer("Minuit","minimize"),SumW2Error(true),Save(true),PrintLevel(-1),PrintEvalErrors(-1));
    fitResults.insert(pair<int,RooFitResult*>(mh,fitRes));
    mass->setBins(160); //return to default 
    }
    std::cout <<  "LC DEBUG DEBUG DEBUG F" << std::endl;
}

void InitialFit::setFitParams(std::map<int,std::map<std::string,RooRealVar*> >& pars )
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


void InitialFit::plotFits(string name, string rvwv){

  TCanvas *canv = new TCanvas();
  RooPlot *plot = mass->frame(Range(mhLow_-10,mhHigh_+10));
  TPaveText *pt = new TPaveText(.65,.6,.97,.95,"NDC");
  std::vector<int> colorList ={7,9,4,2,8,5,1,14};//kCyan,kMagenta,kBlue, kRed,kGreen,kYellow,kBlack, kGray};
  for (unsigned int i=0; i<allMH_.size(); i++){
    int mh = allMH_[i];
    MH->setConstant(false);
    MH->setVal(mh);
    MH->setConstant(true);
    assert(fitPdfs.find(mh)!=fitPdfs.end());
    assert(datasets.find(mh)!=datasets.end());
    RooAbsPdf *fitModel = fitPdfs[mh];
    //RooDataSet *data = datasets[mh];
    mass->setBins(bins_);
    RooDataHist *data = new RooDataHist(datasets[mh]->GetName(),datasets[mh]->GetName(), RooArgSet(*mass),*datasets[mh]);
    //RooDataHist *data = datasets[mh]->binnedClone();
    //data->plotOn(plot,Binning(160),MarkerColor(kBlue+10*i));
    if (i>  colorList.size() ){
    std::cout << "ERROR you need to add more colors in InitialFit::plotFits because you have a lot of mH points!" << std::endl;
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

void InitialFit::printCorrMatrix( int mh ) {
  fitResults[mh]->correlationHist()->Print("ALL");
}
