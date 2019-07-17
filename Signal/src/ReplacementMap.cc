#include "../interface/ReplacementMap.h"
#include "TSystem.h"

// Constructor
ReplacementMap::ReplacementMap( std::string analysis ){ 
  
  // set analysis string
  _analysis=analysis;

  // set replacement cat/proc map from ../python/replacementMaps.py
  TPython::Exec("import os,imp");
  const char *env = gSystem->Getenv("CMSSW_BASE");
  std::string globeRt = env;
  if (globeRt !=0){
    globeRt = globeRt+"/src/flashggFinalFit/Signal";
  }
  if( ! TPython::Exec(Form("replacementMap = imp.load_source('*', '%s/python/replacementMap.py')",globeRt.c_str())) ) {
    throw std::runtime_error("[ERROR] Importing replacementMap from python failed. exit."); 
  }

  // Extracting mapping for RV fits...
  // loop over cats: and fill proc map
  int ncats = (int)TPython::Eval(Form("len(replacementMap.replacementProcRVMap['%s'])", _analysis.c_str()));
  for( int icat=0; icat<ncats; ++icat ){
    std::string cat = (std::string)TPython::Eval(Form("replacementMap.replacementProcRVMap['%s'][%i].split(\':\')[0]",_analysis.c_str(),icat));
    std::string reproc = (std::string)TPython::Eval(Form("replacementMap.replacementProcRVMap['%s'][%i].split(\':\')[1]",_analysis.c_str(),icat));
    _replacementProcRVMap[ cat ] = reproc;
  }

  // loop over cats: and fill cat map
  ncats = (int)TPython::Eval(Form("len(replacementMap.replacementCatRVMap['%s'])", _analysis.c_str()));
  for( int icat=0; icat<ncats; ++icat ){
    std::string cat = (std::string)TPython::Eval(Form("replacementMap.replacementCatRVMap['%s'][%i].split(\':\')[0]",_analysis.c_str(),icat));
    std::string recat = (std::string)TPython::Eval(Form("replacementMap.replacementCatRVMap['%s'][%i].split(\':\')[1]",_analysis.c_str(),icat));
    _replacementCatRVMap[ cat ] = recat;
  }

  // Extracting mapping for WV fits (single replacement)...
  _replacementProcWV = (std::string)TPython::Eval(Form("replacementMap.replacementProcWV['%s']",_analysis.c_str()));
  _replacementCatWV = (std::string)TPython::Eval(Form("replacementMap.replacementCatWV['%s']",_analysis.c_str()));
}

// Get functions: extract correct mapping for given analysis
std::map<std::string,std::string> ReplacementMap::getReplacementProcRVMap(){ return _replacementProcRVMap; }
std::map<std::string,std::string> ReplacementMap::getReplacementCatRVMap(){ return _replacementCatRVMap; }
std::string ReplacementMap::getReplacementProcWV(){ return _replacementProcWV; }
std::string ReplacementMap::getReplacementCatWV(){ return _replacementCatWV; }
