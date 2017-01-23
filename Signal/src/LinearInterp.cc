#include "RooMsgService.h"

#include "../interface/LinearInterp.h"

using namespace std;
using namespace RooFit;

LinearInterp::LinearInterp(RooRealVar *MHvar, vector<int> massList, map<int,map<string,RooRealVar*> > fitParamVals, bool doSecMods, vector<int> skipMasses):
  MH(MHvar),
  fitParams(fitParamVals),
  doSecondaryModels(doSecMods),
  secondaryModelVarsSet(false),
  skipMasses_(skipMasses),
  allMH_(massList),
  verbosity_(0)
{
 // allMH_ = getAllMH();
}

LinearInterp::~LinearInterp(){}

bool LinearInterp::skipMass(int mh){
	for (vector<int>::iterator it=skipMasses_.begin(); it!=skipMasses_.end(); it++) {
		if (*it==mh) return true;
	}
	return false;
}

void LinearInterp::setSecondaryModelVars(RooRealVar *mh_sm, RooRealVar *deltam, RooAddition *mh_2, RooRealVar *width){
  MH_SM = mh_sm;
  DeltaM = deltam;
  MH_2 = mh_2;
  higgsDecayWidth = width;
  secondaryModelVarsSet=true;
}

// new interpolation class which is simpler agnostic of the functional form used
// it just loops through the parameters of the functional form and makes a spline for each
// rather than beign hard coded to parameters of a Gaussian
void LinearInterp::interpolate(){

  vector<double> xValues;
  vector<double> dmValues;
  vector<double> sigmaValues;
  vector<TString> paramNameTemplates; //TStrings are better than cpp strings because they have an intuitive find and repalce function
    
  int mh0 = allMH_[0]; //pick the first MH to get param names. It doesn't really matter which to pick here/
    
  typedef map<string,RooRealVar* >::iterator it_map2;
    
  // here we get the names of the params at mh0, and then we will loop through this list in the next loop
  for(it_map2 iterator2 = fitParams[mh0].begin(); iterator2 != fitParams[mh0].end(); iterator2++) {
    paramNameTemplates.push_back(TString(iterator2->first));
   }
    
  // next loop through each param name template and for each MH, in order to make a spline.
  for (int iParam =0; iParam < paramNameTemplates.size() ; iParam++){
    //fill the x,y values of the parameter 
    vector<double> mhValues;
    vector<double> paramValues;
    for (unsigned int i=0; i<allMH_.size(); i++){
      int mh = allMH_[i];
      mhValues.push_back(double(mh)); 
      TString thisParamName = paramNameTemplates[iParam]; 
      thisParamName = thisParamName.ReplaceAll(TString(Form("mh%d",mh0)),TString(Form("mh%d",mh))); //name of equivalent param for this MH value.
      paramValues.push_back(fitParams[mh][thisParamName.Data()]->getVal()); // .Data() converts a TSTring into a regular string
    }
    TString splineName = paramNameTemplates[iParam]; 
    splineName =  splineName.ReplaceAll(TString(Form("_mh%d",mh0)),TString(""));  // just remove the reference to the MH value in param name
    //it's just that easy: plug the x,y values of the param into the Spline constructor
    RooSpline1D *paramSpline = new RooSpline1D(splineName.Data(),splineName.Data(),*MH,mhValues.size(),&(mhValues[0]),&(paramValues[0]),"LINEAR");
    // and save it for later use.
    splines.insert(pair<string,RooSpline1D*>(paramSpline->GetName(),paramSpline));
    if (verbosity_) std::cout << "[INFO] Linear Interp: preparing this spline " << paramSpline->GetName() << std::endl;
  }
}

// this old class is depracated as it was basically hard-coded for a sum of Gaussians functional form
// leaving it here for reference but it can probably be safely deleted 
/*void LinearInterp::interpolate(int nGaussians){
  for (int g=0; g<nGaussians; g++) {
    vector<double> xValues;
    vector<double> dmValues;
    vector<double> sigmaValues;
    for (unsigned int i=0; i<allMH_.size(); i++){
      int mh = allMH_[i];
      xValues.push_back(double(mh));
      dmValues.push_back(fitParams[mh][Form("dm_mh%d_g%d",mh,g)]->getVal());
      sigmaValues.push_back(fitParams[mh][Form("sigma_mh%d_g%d",mh,g)]->getVal());
    }
    assert(xValues.size()==dmValues.size());
    assert(xValues.size()==sigmaValues.size());
    //RooSpline1D *dmSpline = new RooSpline1D(Form("dm_g%d",g),Form("dm_g%d",g),*MH,xValues.size(),&(xValues[0]),&(dmValues[0]),"LINEAR");
    RooSpline1D *dmSpline = new RooSpline1D(Form("dm_g%d",g),Form("dm_g%d",g),*MH,xValues.size(),&(xValues[0]),&(dmValues[0]));
   // RooSpline1D *sigmaSpline = new RooSpline1D(Form("sigma_g%d",g),Form("sigma_g%d",g),*MH,xValues.size(),&(xValues[0]),&(sigmaValues[0]),"LINEAR");
    RooSpline1D *sigmaSpline = new RooSpline1D(Form("sigma_g%d",g),Form("sigma_g%d",g),*MH,xValues.size(),&(xValues[0]),&(sigmaValues[0]));
    splines.insert(pair<string,RooSpline1D*>(dmSpline->GetName(),dmSpline));
    splines.insert(pair<string,RooSpline1D*>(sigmaSpline->GetName(),sigmaSpline));
    // add secondary models as well
    if (doSecondaryModels){
      assert(secondaryModelVarsSet);
      // sm higgs as background
      RooSpline1D *dmSplineSM = new RooSpline1D(Form("dm_g%d_SM",g),Form("dm_g%d_SM",g),*MH_SM,xValues.size(),&(xValues[0]),&(dmValues[0]),"LINEAR");
      RooSpline1D *sigmaSplineSM = new RooSpline1D(Form("sigma_g%d_SM",g),Form("sigma_g%d_SM",g),*MH_SM,xValues.size(),&(xValues[0]),&(sigmaValues[0]),"LINEAR");
      splines.insert(pair<string,RooSpline1D*>(dmSplineSM->GetName(),dmSplineSM));
      splines.insert(pair<string,RooSpline1D*>(sigmaSplineSM->GetName(),sigmaSplineSM));
      // second degen higgs
      RooSpline1D *dmSpline2 = new RooSpline1D(Form("dm_g%d_2",g),Form("dm_g%d_2",g),*MH_2,xValues.size(),&(xValues[0]),&(dmValues[0]),"LINEAR");
      RooSpline1D *sigmaSpline2 = new RooSpline1D(Form("sigma_g%d_2",g),Form("sigma_g%d_2",g),*MH_2,xValues.size(),&(xValues[0]),&(sigmaValues[0]),"LINEAR");
      splines.insert(pair<string,RooSpline1D*>(dmSpline2->GetName(),dmSpline2));
      splines.insert(pair<string,RooSpline1D*>(sigmaSpline2->GetName(),sigmaSpline2));
    }
    if (g<nGaussians-1){
      vector<double> fracValues;
      for (unsigned int i=0; i<allMH_.size(); i++){
        int mh = allMH_[i];
        fracValues.push_back(fitParams[mh][Form("frac_mh%d_g%d",mh,g)]->getVal());
      }
      assert(xValues.size()==fracValues.size());
      //RooSpline1D *fracSpline = new RooSpline1D(Form("frac_g%d",g),Form("frac_g%d",g),*MH,xValues.size(),&(xValues[0]),&(fracValues[0]),"LINEAR");
      RooSpline1D *fracSpline = new RooSpline1D(Form("frac_g%d",g),Form("frac_g%d",g),*MH,xValues.size(),&(xValues[0]),&(fracValues[0]));
      splines.insert(pair<string,RooSpline1D*>(fracSpline->GetName(),fracSpline));
      // add secondary models as well
      if (doSecondaryModels){
        assert(secondaryModelVarsSet);
        // sm higgs as background
        RooSpline1D *fracSplineSM = new RooSpline1D(Form("frac_g%d_SM",g),Form("frac_g%d_SM",g),*MH,xValues.size(),&(xValues[0]),&(fracValues[0]),"LINEAR");
        splines.insert(pair<string,RooSpline1D*>(fracSplineSM->GetName(),fracSplineSM));
        // second degen higgs
        RooSpline1D *fracSpline2 = new RooSpline1D(Form("frac_g%d_2",g),Form("frac_g%d_2",g),*MH,xValues.size(),&(xValues[0]),&(fracValues[0]),"LINEAR");
        splines.insert(pair<string,RooSpline1D*>(fracSpline2->GetName(),fracSpline2));
      }
    }
  }
}*/

map<string,RooSpline1D*> LinearInterp::getSplines(){
  return splines;
}

void LinearInterp::setVerbosity(int v){
  if (v<2) {
    RooMsgService::instance().setGlobalKillBelow(RooFit::ERROR);
    RooMsgService::instance().setSilentMode(true);
  }
  verbosity_=v;
}

