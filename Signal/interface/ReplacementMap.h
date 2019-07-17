#ifndef ReplacementMap_h
#define ReplacementMap_h

#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <map>
#include <exception>

#include "TPython.h"
#include "TString.h"
#include "TROOT.h"
#include "TPython.h"

class ReplacementMap {

  public:
    ReplacementMap( std::string analysis );

    std::map<std::string,std::string> getReplacementCatRVMap();
    std::map<std::string,std::string> getReplacementProcRVMap();
    std::string getReplacementCatWV();
    std::string getReplacementProcWV();

  public:
    std::string _analysis; //e.g. hig-16-040, stage1. Add new mappings in ../python/replacementMaps.py
    std::map<std::string,std::string> _replacementCatRVMap;
    std::map<std::string,std::string> _replacementProcRVMap;
    std::string _replacementCatWV; //only need a single proc*cat for WV fit replacement
    std::string _replacementProcWV;

};
#endif
