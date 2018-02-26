#include "../interface/WSTFileWrapper.h"

#include <sstream>
#include <iostream>

WSTFileWrapper::WSTFileWrapper( std::string files, std::string wsname ) {
  std::stringstream ss(files);
  while( ss.good() ) {
    std::string substr;
    getline( ss, substr, ',' );
    fnList.push_back( substr );
  }
  wsName_ = wsname;

  std::cout << "inside WST contructor, about to loop over files" << std:: endl;
  for ( std::vector<std::string>::iterator fn = fnList.begin() ; fn != fnList.end() ; fn++ ) {
    std::string keyName = std::string( fileToKey( *fn ) );
    fileList.emplace( keyName, TFile::Open(fn->c_str()) );
    if (fileList.rbegin()->second == 0) {
      std::cout << "[WSTFileWrapper] got 0 for what should be this file: " << (*fn) << std::endl;
    } else if (fileList.rbegin()->second->IsZombie()) {
      std::cout << "[WSTFileWrapper] got that this file is a zombie: " << (*fn) << std::endl;
    } else {
      // this is very verbose otherwise!
      std::cout << "[WSTFileWrapper] successfully opened this file: " << (*fn) << std::endl;
    }
    // this is the part that needed to be removed, due to memory issues
    // try to just access when necessary instead
    // for now keep the wsList and just add the first one
    // useful e.g. for keeping existing constructors, and accessing just the necessary vars (only need one workspace for that)
    if( fn == fnList.begin() ) { 
      wsList.push_back((RooWorkspace*)fileList.begin()->second->Get(wsname.c_str()));
      if (wsList.back() == 0) {
        std::cout << "[WSTFileWrapper] on file " << (*fn) << " failed to obtain workspace named: " << wsname << std::endl;
      } else {
        // this is very verbose otherwise!
        std::cout << "[WSTFileWrapper] on file " << (*fn) << " opened workspace named: " << wsname << std::endl;
      }
    }
  }
  std::cout << "inside WST contructor, done loop over files" << std:: endl;
}

WSTFileWrapper::WSTFileWrapper( TFile *tf ,RooWorkspace *inWS ) {
  wsName_ = inWS->GetName();
  wsList.push_back(inWS);
  fnList.push_back("current file");
  fileList.emplace("current file",tf);
}

WSTFileWrapper::WSTFileWrapper( RooWorkspace *inWS ) {
  TFile *outF = new TFile("WSTFileWrapper.root","RECREATE");
  wsName_ = inWS->GetName();
  wsList.push_back(inWS);
  fnList.push_back("current file");
  fileList.emplace("current file",outF);
}

RooWorkspace* WSTFileWrapper::getSpecificWorkspace( std::string keyName ) {
 fileList[keyName]->cd();
 return (RooWorkspace*)fileList[keyName]->Get(wsName_.c_str());
}

RooRealVar* WSTFileWrapper::var(std::string varName) {
  fileList.begin()->second->cd();
  return wsList[0]->var(varName.c_str());
}

std::string WSTFileWrapper::fileToKey( std::string fileName ) {
    TString procName = TString(fileName);
    procName.Remove( 0, procName.Index("pythia8_")+8 ); // all file names must end pythia8_procName.root
    procName.Resize( procName.Index(".root") ); // all file names must end pythia8_procName.root
    TString massVal = TString(fileName);
    massVal = massVal.Replace(0, massVal.Index("_13TeV_")-3, ""); //and have mass in the form M1??_13TeV_
    massVal.Resize(3);
    std::string keyName = TString( TString(massVal.Data()) + TString(procName.Data()) ).Data();
    return keyName;
}

std::pair<std::string,std::string> WSTFileWrapper::convertTemplatedName(std::string dataName) {
  TString theDataName = TString(dataName);
  std::string theProcName = "";
  std::map<std::string,std::string> tpMap;
  tpMap["GG2H"] = "ggh";
  tpMap["VBF"] = "vbf";
  tpMap["TTH"] = "tth";
  tpMap["QQ2HLNU"] = "wh";
  tpMap["QQ2HLL"] = "zh";
  tpMap["WH2HQQ"] = "wh";
  tpMap["ZH2HQQ"] = "zh";
  tpMap["testBBH"] = "bbh";
  tpMap["testTHW"] = "th";
  tpMap["testTHQ"] = "th";
  for( std::map<std::string,std::string>::iterator it = tpMap.begin(); it != tpMap.end(); it++ ) {
    if( theDataName.BeginsWith(it->first) ) { 
      TString theDataNameCopy = theDataName;
      theDataNameCopy.Resize( theDataName.Index("_13TeV_")-4 ); //works because always of form proc_M1??_13TeV_cat
      theProcName = theDataNameCopy.Data();
      theDataName.Replace( 0, theProcName.size(), it->second );
    }
  }
  std::pair<std::string,std::string> thePair;
  thePair.first  = theDataName.Data();
  thePair.second = theProcName;
  return thePair;
}

RooAbsData* WSTFileWrapper::data(std::string dataName) {
  std::pair<std::string,std::string> thePair = convertTemplatedName(dataName);
  std::string newDataName = thePair.first;
  std::string newProcName = thePair.second;
  RooAbsData* result = 0;
  bool complained_yet = 0;
  // this skips the loop process when the wrapper is not actually considering all files
  if( fileList.size()==1 ) { 
    result = (RooAbsData*)wsList[0]->data(newDataName.c_str());
    if( result ) { return result; }
  }
  for( auto it=fileList.begin(); it!=fileList.end(); it++ ) {
    TString tempFileName = TString(it->second->GetName());
    if( tempFileName.Index(newProcName) < 0  && newProcName!="" ) { continue; }
    it->second->cd();
    std::cout << "trying to get data with name " << newDataName << std::endl;
    std::cout << "the workspace looks like this: " << std::endl;
    wsList[0]->Print();
    std::cout << "its name is " << wsName_ << std::endl;
    std::cout << "the length of the file list is " << fileList.size() << std::endl;
    std::cout << "this file name is " << tempFileName << std::endl;
    RooAbsData* this_result = (RooAbsData*)((RooWorkspace*)it->second->Get(wsName_.c_str()))->data(newDataName.c_str());
    if (result && this_result && !complained_yet) {
      std::cout << "[WSTFileWrapper] Uh oh, multiple RooAbsDatas from the file list with the same name: " <<  newDataName << std::endl;
      complained_yet = true;
    }
    if (this_result) {
      result = this_result;
      std::cout << "[WSTFileWrapper] Got non-zero RooAbsData from " << it->second->GetName() << " with name " << newDataName << std::endl;
    }
  }
  if (!result) {
    std::cout << "[WSTFileWrapper] Uh oh, never got a good RooAbsData with name " << newDataName << std::endl;
  }
  return result;
}

RooAbsData* WSTFileWrapper::data(std::string keyName, std::string dataName) {
  std::pair<std::string,std::string> thePair = convertTemplatedName(dataName);
  std::string newDataName = thePair.first;
  fileList[keyName]->cd();
  RooAbsData* result = (RooAbsData*)((RooWorkspace*)fileList[keyName]->Get(wsName_.c_str()))->data(newDataName.c_str());
  if (!result) {
    std::cout << "[WSTFileWrapper] Uh oh, never got a good RooAbsData with name " << newDataName << std::endl;
  }
  return result;
}

RooAbsPdf* WSTFileWrapper::pdf(std::string pdfName) {
  RooAbsPdf* result = 0;
  bool complained_yet = 0;
  // this skips the loop process when the wrapper is not actually considering all files
  if( fileList.size()==1 ) { 
    result = (RooAbsPdf*)wsList[0]->pdf(pdfName.c_str());
    if( result ) { return result; }
  }
  for( auto it=fileList.begin(); it!=fileList.end(); it++ ) {
    it->second->cd();
    RooAbsPdf* this_result = (RooAbsPdf*)((RooWorkspace*)it->second->Get(wsName_.c_str()))->pdf(pdfName.c_str());
    if (result && this_result && !complained_yet) {
      std::cout << "[WSTFileWrapper] Uh oh, multiple RooAbsPdfs from the file list with the same name: " <<  pdfName << std::endl;
      complained_yet = true;
    }
    if (this_result) {
      result = this_result;
      std::cout << "[WSTFileWrapper] Got non-zero RooAbsPdf from " << it->second->GetName() << " with name " << pdfName << std::endl;
    }
  }
  if (!result) {
    std::cout << "[WSTFileWrapper] Uh oh, never got a good RooAbsPdf with name " << pdfName << std::endl;
  }
  return result;
}

RooAbsPdf* WSTFileWrapper::pdf(std::string keyName, std::string pdfName) {
  fileList[keyName]->cd();
  RooAbsPdf* result = (RooAbsPdf*)((RooWorkspace*)fileList[keyName]->Get(wsName_.c_str()))->pdf(pdfName.c_str());
  if (!result) {
    std::cout << "[WSTFileWrapper] Uh oh, never got a good RooAbsPdf with name " << pdfName << std::endl;
  }
  return result;
}

RooCategory* WSTFileWrapper::cat(std::string catName) {
  RooCategory* result = 0;
  bool complained_yet = 0;
  // this skips the loop process when the wrapper is not actually considering all files
  if( fileList.size()==1 ) { 
    result = (RooCategory*)wsList[0]->cat(catName.c_str());
    if( result ) { return result; }
  }
  for( auto it=fileList.begin(); it!=fileList.end(); it++ ) {
    it->second->cd();
    RooCategory* this_result = (RooCategory*)((RooWorkspace*)it->second->Get(wsName_.c_str()))->cat(catName.c_str());
    if (result && this_result && !complained_yet) {
      std::cout << "[WSTFileWrapper] Uh oh, multiple RooCategories from the file list with the same name: " <<  catName << std::endl;
      complained_yet = true;
    }
    if (this_result) {
      result = this_result;
      std::cout << "[WSTFileWrapper] Got non-zero RooCategory from " << it->second->GetName() << " with name " << catName << std::endl;
    }
  }
  if (!result) {
    std::cout << "[WSTFileWrapper] Uh oh, never got a good RooCategory with name " << catName << std::endl;
  }
  return result;
}

RooCategory* WSTFileWrapper::cat(std::string keyName, std::string catName) {
  fileList[keyName]->cd();
  RooCategory* result = (RooCategory*)((RooWorkspace*)fileList[keyName]->Get(wsName_.c_str()))->cat(catName.c_str());
  if (!result) {
    std::cout << "[WSTFileWrapper] Uh oh, never got a good RooCategory with name " << catName << std::endl;
  }
  return result;
}

RooAbsReal* WSTFileWrapper::function(std::string functionName) {
  RooAbsReal* result = 0;
  bool complained_yet = 0;
  // this skips the loop process when the wrapper is not actually considering all files
  if( fileList.size()==1 ) { 
    result = (RooAbsReal*)wsList[0]->function(functionName.c_str());
    if( result ) { return result; }
  }
  for( auto it=fileList.begin(); it!=fileList.end(); it++ ) {
    it->second->cd();
    RooAbsReal* this_result = (RooAbsReal*)((RooWorkspace*)it->second->Get(wsName_.c_str()))->function(functionName.c_str());
    if (result && this_result && !complained_yet) {
      std::cout << "[WSTFileWrapper] Uh oh, multiple RooAbsReals from the file list with the same name: " <<  functionName << std::endl;
      complained_yet = true;
    }
    if (this_result) {
      result = this_result;
      std::cout << "[WSTFileWrapper] Got non-zero RooAbsData from " << it->second->GetName() << " with name " << functionName << std::endl;
    }
  }
  if (!result) {
    std::cout << "[WSTFileWrapper] Uh oh, never got a good RooAbsReal with name " << functionName << std::endl;
  }
  return result;
}

RooAbsReal* WSTFileWrapper::function(std::string keyName, std::string functionName) {
  fileList[keyName]->cd();
  RooAbsReal* result = (RooAbsReal*)((RooWorkspace*)fileList[keyName]->Get(wsName_.c_str()))->function(functionName.c_str());
  if (!result) {
    std::cout << "[WSTFileWrapper] Uh oh, never got a good RooAbsReal with name " << functionName << std::endl;
  }
  return result;
}

void WSTFileWrapper::Close() {
  for (auto it = fileList.begin(); it != fileList.end() ; it++) {
    it->second->Close();
  }
}
