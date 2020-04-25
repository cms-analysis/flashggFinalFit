#include "../interface/Normalization_13TeV.h"

#include "TSystem.h"

Normalization_13TeV::Normalization_13TeV(){}

int Normalization_13TeV::Init(int sqrtS){

    TPython::Exec("import os,imp");
    const char * env = gSystem->Getenv("CMSSW_BASE");
    std::string globeRt = env;
    if (globeRt !=0){
        globeRt = globeRt+"/src/flashggFinalFit/Signal";
    }
    if( ! TPython::Exec(Form("buildSMHiggsSignalXSBR = imp.load_source('*', '%s/python/buildSMHiggsSignalXSBR.py')",globeRt.c_str())) ) {
        std::cout<<  "[ERROR] Importing buildSMHiggsSignalXSBR from python failed. exit." << std::endl;
        return 0;
    }
    TPython::Eval(Form("buildSMHiggsSignalXSBR.Init%dTeV()", sqrtS));
    
    for (double mH=120;mH<130.05;mH+=0.1){ // breaks when extended beyond 130
        double valBR           = (double)TPython::Eval(Form("buildSMHiggsSignalXSBR.getBR(%f)",mH));
        double valXSggH        = (double)TPython::Eval(Form("buildSMHiggsSignalXSBR.getXS(%f,'%s')",mH,"ggH"));
        double valXSqqH        = (double)TPython::Eval(Form("buildSMHiggsSignalXSBR.getXS(%f,'%s')",mH,"qqH"));
        double valXSttH        = (double)TPython::Eval(Form("buildSMHiggsSignalXSBR.getXS(%f,'%s')",mH,"ttH"));
        double valXSWH         = (double)TPython::Eval(Form("buildSMHiggsSignalXSBR.getXS(%f,'%s')",mH,"WH"));
        double valXSZH         = (double)TPython::Eval(Form("buildSMHiggsSignalXSBR.getXS(%f,'%s')",mH,"ZH"));
        double valXSbbH        = (double)TPython::Eval(Form("buildSMHiggsSignalXSBR.getXS(%f,'%s')",mH,"bbH"));
        double valXStHq        = (double)TPython::Eval(Form("buildSMHiggsSignalXSBR.getXS(%f,'%s')",mH,"tHq"));
        double valXStHW        = (double)TPython::Eval(Form("buildSMHiggsSignalXSBR.getXS(%f,'%s')",mH,"tHW"));
        double valXSggZH       = (double)TPython::Eval(Form("buildSMHiggsSignalXSBR.getXS(%f,'%s')",mH,"ggZH"));
        double valXSQQ2HLNU    = valXSWH*(3.*10.86*0.01)/*3xBR(W to lv)*/;  
        double valXSQQ2HLL     = (valXSZH-valXSggZH)*(3*3.3658*0.01 + 20.00*0.01)/*BR(Z to ll) + BR(Z to invisible)*/;  
        double valXSGG2HLL     = valXSggZH*(3*3.3658*0.01)/*BR(Z to ll)*/;  
        double valXSGG2HNUNU   = valXSggZH*(20.00*0.01)/*BR(Z to invisible)*/;  
        double valXSGG2HQQ     = valXSggZH*(69.91*0.01)/*BR(Z to hadrons)*/;  
        double valXSWH2HQQ     = valXSWH*(67.41*0.01)/*BR(W to hadrons)*/;
        double valXSZH2HQQ     = valXSZH*(69.91*0.01)/*BR(Z to hadrons)*/;  

        BranchingRatioMap[mH] = valBR;

        XSectionMap_ggh[mH] = valXSggH;   
        XSectionMap_vbf[mH] = valXSqqH;   
        XSectionMap_tth[mH] = valXSttH;   
        XSectionMap_wh[mH]  = valXSWH;  
        XSectionMap_zh[mH]  = valXSZH;  

        XSectionMap_QQ2HLNU[mH] = valXSQQ2HLNU;
        XSectionMap_QQ2HLL[mH]  = valXSQQ2HLL;
        XSectionMap_GG2HLL[mH]  = valXSGG2HLL;
        XSectionMap_WH2HQQ[mH]  = valXSWH2HQQ;
        XSectionMap_ZH2HQQ[mH]  = valXSZH2HQQ;

        // Stage 1.2: now include forward as separate process (taken from 2018 only: need to compare)
        XSectionMap_GG2H_FWDH[mH] = 0.0810 * valXSggH;
        XSectionMap_GG2H_PTH_200_300[mH] = 0.0118 * valXSggH;
        XSectionMap_GG2H_PTH_300_450[mH] = 0.0032 * valXSggH;
        XSectionMap_GG2H_PTH_450_650[mH] = 0.0006 * valXSggH;
        XSectionMap_GG2H_PTH_GT650[mH] = 0.0001 * valXSggH;
        XSectionMap_GG2H_0J_PTH_0_10[mH] = 0.1348 * valXSggH;
        XSectionMap_GG2H_0J_PTH_GT10[mH] = 0.3919 * valXSggH;
        XSectionMap_GG2H_1J_PTH_0_60[mH] = 0.1469 * valXSggH;
        XSectionMap_GG2H_1J_PTH_60_120[mH] = 0.1021 * valXSggH;
        XSectionMap_GG2H_1J_PTH_120_200[mH] = 0.0193 * valXSggH;
        XSectionMap_GG2H_GE2J_MJJ_0_350_PTH_0_60[mH] = 0.0260 * valXSggH;
        XSectionMap_GG2H_GE2J_MJJ_0_350_PTH_60_120[mH] = 0.0403 * valXSggH;
        XSectionMap_GG2H_GE2J_MJJ_0_350_PTH_120_200[mH] = 0.0209 * valXSggH;
        XSectionMap_GG2H_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25[mH] = 0.0064 * valXSggH;
        XSectionMap_GG2H_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25[mH] = 0.0081 * valXSggH;
        XSectionMap_GG2H_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25[mH] = 0.0030 * valXSggH;
        XSectionMap_GG2H_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25[mH] = 0.0033 * valXSggH;       

        // UPDATE: switched to POWHEG numbers for qqH
        XSectionMap_VBF_FWDH[mH] = 0.067 * valXSqqH;
        XSectionMap_VBF_0J[mH] = 0.069 * valXSqqH;
        XSectionMap_VBF_1J[mH] = 0.329 * valXSqqH;
        XSectionMap_VBF_GE2J_MJJ_0_60[mH] = 0.014 * valXSqqH;
        XSectionMap_VBF_GE2J_MJJ_60_120[mH] = 0.024 * valXSqqH;
        XSectionMap_VBF_GE2J_MJJ_120_350[mH] = 0.123 * valXSqqH;
        XSectionMap_VBF_GE2J_MJJ_GT350_PTH_GT200[mH] = 0.040 * valXSqqH;
        XSectionMap_VBF_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25[mH] = 0.103 * valXSqqH;
        XSectionMap_VBF_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25[mH] = 0.038 * valXSqqH;
        XSectionMap_VBF_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25[mH] = 0.151 * valXSqqH;
        XSectionMap_VBF_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25[mH] = 0.042 * valXSqqH;

        XSectionMap_WH2HQQ_FWDH[mH] = 0.1257 * valXSWH2HQQ;
        XSectionMap_WH2HQQ_0J[mH] = 0.0570 * valXSWH2HQQ;
        XSectionMap_WH2HQQ_1J[mH] = 0.3113 * valXSWH2HQQ;
        XSectionMap_WH2HQQ_GE2J_MJJ_0_60[mH] = 0.0358 * valXSWH2HQQ;
        XSectionMap_WH2HQQ_GE2J_MJJ_60_120[mH] = 0.2943 * valXSWH2HQQ;
        XSectionMap_WH2HQQ_GE2J_MJJ_120_350[mH] = 0.1392 * valXSWH2HQQ;
        XSectionMap_WH2HQQ_GE2J_MJJ_GT350_PTH_GT200[mH] = 0.0088 * valXSWH2HQQ;
        XSectionMap_WH2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25[mH] = 0.0044 * valXSWH2HQQ;
        XSectionMap_WH2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25[mH] = 0.0186 * valXSWH2HQQ;
        XSectionMap_WH2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25[mH] = 0.0009 * valXSWH2HQQ;
        XSectionMap_WH2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25[mH] = 0.0040 * valXSWH2HQQ;

        XSectionMap_ZH2HQQ_FWDH[mH] = 0.1143 * valXSZH2HQQ;
        XSectionMap_ZH2HQQ_0J[mH] = 0.0433 * valXSZH2HQQ;
        XSectionMap_ZH2HQQ_1J[mH] = 0.2906 * valXSZH2HQQ;
        XSectionMap_ZH2HQQ_GE2J_MJJ_0_60[mH] = 0.0316 * valXSZH2HQQ;
        XSectionMap_ZH2HQQ_GE2J_MJJ_60_120[mH] = 0.3360 * valXSZH2HQQ;
        XSectionMap_ZH2HQQ_GE2J_MJJ_120_350[mH] = 0.1462 * valXSZH2HQQ;
        XSectionMap_ZH2HQQ_GE2J_MJJ_GT350_PTH_GT200[mH] = 0.0083 * valXSZH2HQQ;
        XSectionMap_ZH2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25[mH] = 0.0041 * valXSZH2HQQ;
        XSectionMap_ZH2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25[mH] = 0.0202 * valXSZH2HQQ;
        XSectionMap_ZH2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25[mH] = 0.0009 * valXSZH2HQQ;
        XSectionMap_ZH2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25[mH] = 0.0045 * valXSZH2HQQ;

        XSectionMap_QQ2HLNU_FWDH[mH] = 0.1238 * valXSQQ2HLNU;
        XSectionMap_QQ2HLNU_PTV_0_75[mH] = 0.4642 * valXSQQ2HLNU;
        XSectionMap_QQ2HLNU_PTV_75_150[mH] = 0.2922 * valXSQQ2HLNU;
        XSectionMap_QQ2HLNU_PTV_150_250_0J[mH] = 0.0509 * valXSQQ2HLNU;
        XSectionMap_QQ2HLNU_PTV_150_250_GE1J[mH] = 0.0395 * valXSQQ2HLNU;
        XSectionMap_QQ2HLNU_PTV_GT250[mH] = 0.0294 * valXSQQ2HLNU;

        XSectionMap_QQ2HLL_FWDH[mH] = 0.1131 * valXSQQ2HLL;
        XSectionMap_QQ2HLL_PTV_0_75[mH] = 0.4556 * valXSQQ2HLL;
        XSectionMap_QQ2HLL_PTV_75_150[mH] = 0.3076 * valXSQQ2HLL;
        XSectionMap_QQ2HLL_PTV_150_250_0J[mH] = 0.0516 * valXSQQ2HLL;
        XSectionMap_QQ2HLL_PTV_150_250_GE1J[mH] = 0.0421 * valXSQQ2HLL;
        XSectionMap_QQ2HLL_PTV_GT250[mH] = 0.0299 * valXSQQ2HLL;

        XSectionMap_GG2HQQ_FWDH[mH] = 0.0282 * valXSGG2HQQ;
        XSectionMap_GG2HQQ_PTH_200_300[mH] = 0.1361 * valXSGG2HQQ;
        XSectionMap_GG2HQQ_PTH_300_450[mH] = 0.0372 * valXSGG2HQQ;
        XSectionMap_GG2HQQ_PTH_450_650[mH] = 0.0075 * valXSGG2HQQ;
        XSectionMap_GG2HQQ_PTH_GT650[mH] = 0.0019 * valXSGG2HQQ;
        XSectionMap_GG2HQQ_0J_PTH_0_10[mH] = 0.0001 * valXSGG2HQQ;
        XSectionMap_GG2HQQ_0J_PTH_GT10[mH] = 0.0029 * valXSGG2HQQ;
        XSectionMap_GG2HQQ_1J_PTH_0_60[mH] = 0.0209 * valXSGG2HQQ;
        XSectionMap_GG2HQQ_1J_PTH_60_120[mH] = 0.0528 * valXSGG2HQQ;
        XSectionMap_GG2HQQ_1J_PTH_120_200[mH] = 0.0359 * valXSGG2HQQ;
        XSectionMap_GG2HQQ_GE2J_MJJ_0_350_PTH_0_60[mH] = 0.0575 * valXSGG2HQQ;
        XSectionMap_GG2HQQ_GE2J_MJJ_0_350_PTH_60_120[mH] = 0.1993 * valXSGG2HQQ;
        XSectionMap_GG2HQQ_GE2J_MJJ_0_350_PTH_120_200[mH] = 0.2962 * valXSGG2HQQ;
        XSectionMap_GG2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25[mH] = 0.0118 * valXSGG2HQQ;
        XSectionMap_GG2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25[mH] = 0.0807 * valXSGG2HQQ;
        XSectionMap_GG2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25[mH] = 0.0038 * valXSGG2HQQ;
        XSectionMap_GG2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25[mH] = 0.0270 * valXSGG2HQQ;       

        XSectionMap_GG2HLL_FWDH[mH] = 0.0268 * valXSGG2HLL;
        XSectionMap_GG2HLL_PTV_0_75[mH] = 0.1604 * valXSGG2HLL;
        XSectionMap_GG2HLL_PTV_75_150[mH] = 0.4344 * valXSGG2HLL;
        XSectionMap_GG2HLL_PTV_150_250_0J[mH] = 0.0916 * valXSGG2HLL;
        XSectionMap_GG2HLL_PTV_150_250_GE1J[mH] = 0.2030 * valXSGG2HLL;
        XSectionMap_GG2HLL_PTV_GT250[mH] = 0.0838 * valXSGG2HLL;

        XSectionMap_GG2HNUNU_FWDH[mH] = 0.0272 * valXSGG2HNUNU;
        XSectionMap_GG2HNUNU_PTV_0_75[mH] = 0.1594 * valXSGG2HNUNU;
        XSectionMap_GG2HNUNU_PTV_75_150[mH] = 0.4342 * valXSGG2HNUNU;
        XSectionMap_GG2HNUNU_PTV_150_250_0J[mH] = 0.0906 * valXSGG2HNUNU;
        XSectionMap_GG2HNUNU_PTV_150_250_GE1J[mH] = 0.2044 * valXSGG2HNUNU;
        XSectionMap_GG2HNUNU_PTV_GT250[mH] = 0.0841 * valXSGG2HNUNU;

        XSectionMap_TTH_FWDH[mH]                 = 0.0142 * valXSttH;
        XSectionMap_TTH_PTH_0_60[mH]             = 0.2239 * valXSttH;
        XSectionMap_TTH_PTH_60_120[mH]           = 0.3520 * valXSttH;
        XSectionMap_TTH_PTH_120_200[mH]          = 0.2543 * valXSttH;
        XSectionMap_TTH_PTH_200_300[mH]          = 0.1070 * valXSttH;
        XSectionMap_TTH_PTH_GT300[mH]            = 0.0486 * valXSttH;

        // FIXME: add correct fwd splits for subdominant modes
        XSectionMap_BBH_FWDH[mH]                 = 0.0001* valXSbbH;
        XSectionMap_BBH[mH]                      = 0.9999* valXSbbH;

        XSectionMap_THQ_FWDH[mH]                 = 0.00005 * valXStHq;
        XSectionMap_THQ[mH]                      = 0.99995 * valXStHq;

        XSectionMap_THW_FWDH[mH]                 = 0.02 * valXStHW;
        XSectionMap_THW[mH]                      = 0.98 * valXStHW;

    }
}

TGraph * Normalization_13TeV::GetSigmaGraph(TString process)
{
  TGraph * gr = new TGraph();
  std::map<double, double> * XSectionMap = 0;
  // Stage 1.2
  if ( process == "GG2H_FWDH" ){
          XSectionMap = &XSectionMap_GG2H_FWDH;
  } else if ( process == "GG2H_PTH_200_300" ){
          XSectionMap = &XSectionMap_GG2H_PTH_200_300;
  } else if ( process == "GG2H_PTH_300_450" ){
          XSectionMap = &XSectionMap_GG2H_PTH_300_450;
  } else if ( process == "GG2H_PTH_450_650" ){
          XSectionMap = &XSectionMap_GG2H_PTH_450_650;
  } else if ( process == "GG2H_PTH_GT650" ){
          XSectionMap = &XSectionMap_GG2H_PTH_GT650;
  } else if ( process == "GG2H_0J_PTH_0_10" ){
          XSectionMap = &XSectionMap_GG2H_0J_PTH_0_10;
  } else if ( process == "GG2H_0J_PTH_GT10" ){
          XSectionMap = &XSectionMap_GG2H_0J_PTH_GT10;
  } else if ( process == "GG2H_1J_PTH_0_60" ){
          XSectionMap = &XSectionMap_GG2H_1J_PTH_0_60;
  } else if ( process == "GG2H_1J_PTH_60_120" ){
          XSectionMap = &XSectionMap_GG2H_1J_PTH_60_120;
  } else if ( process == "GG2H_1J_PTH_120_200" ){
          XSectionMap = &XSectionMap_GG2H_1J_PTH_120_200;
  } else if ( process == "GG2H_GE2J_MJJ_0_350_PTH_0_60" ){
          XSectionMap = &XSectionMap_GG2H_GE2J_MJJ_0_350_PTH_0_60;
  } else if ( process == "GG2H_GE2J_MJJ_0_350_PTH_60_120" ){
          XSectionMap = &XSectionMap_GG2H_GE2J_MJJ_0_350_PTH_60_120;
  } else if ( process == "GG2H_GE2J_MJJ_0_350_PTH_120_200" ){
          XSectionMap = &XSectionMap_GG2H_GE2J_MJJ_0_350_PTH_120_200;
  } else if ( process == "GG2H_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25" ){
          XSectionMap = &XSectionMap_GG2H_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25;
  } else if ( process == "GG2H_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25" ){
          XSectionMap = &XSectionMap_GG2H_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25;
  } else if ( process == "GG2H_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25" ){
          XSectionMap = &XSectionMap_GG2H_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25;
  } else if ( process == "GG2H_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25" ){
          XSectionMap = &XSectionMap_GG2H_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25;
  } else if ( process == "VBF_FWDH" ){
          XSectionMap = &XSectionMap_VBF_FWDH;
  } else if ( process == "VBF_0J" ){
          XSectionMap = &XSectionMap_VBF_0J;
  } else if ( process == "VBF_1J" ){
          XSectionMap = &XSectionMap_VBF_1J;
  } else if ( process == "VBF_GE2J_MJJ_0_60" ){
          XSectionMap = &XSectionMap_VBF_GE2J_MJJ_0_60;
  } else if ( process == "VBF_GE2J_MJJ_60_120" ){
          XSectionMap = &XSectionMap_VBF_GE2J_MJJ_60_120;
  } else if ( process == "VBF_GE2J_MJJ_120_350" ){
          XSectionMap = &XSectionMap_VBF_GE2J_MJJ_120_350;
  } else if ( process == "VBF_GE2J_MJJ_GT350_PTH_GT200" ){
          XSectionMap = &XSectionMap_VBF_GE2J_MJJ_GT350_PTH_GT200;
  } else if ( process == "VBF_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25" ){
          XSectionMap = &XSectionMap_VBF_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25;
  } else if ( process == "VBF_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25" ){
          XSectionMap = &XSectionMap_VBF_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25;
  } else if ( process == "VBF_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25" ){
          XSectionMap = &XSectionMap_VBF_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25;
  } else if ( process == "VBF_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25" ){
          XSectionMap = &XSectionMap_VBF_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25;
  } else if ( process == "WH2HQQ_FWDH" ){
          XSectionMap = &XSectionMap_WH2HQQ_FWDH;
  } else if ( process == "WH2HQQ_0J" ){
          XSectionMap = &XSectionMap_WH2HQQ_0J;
  } else if ( process == "WH2HQQ_1J" ){
          XSectionMap = &XSectionMap_WH2HQQ_1J;
  } else if ( process == "WH2HQQ_GE2J_MJJ_0_60" ){
          XSectionMap = &XSectionMap_WH2HQQ_GE2J_MJJ_0_60;
  } else if ( process == "WH2HQQ_GE2J_MJJ_60_120" ){
          XSectionMap = &XSectionMap_WH2HQQ_GE2J_MJJ_60_120;
  } else if ( process == "WH2HQQ_GE2J_MJJ_120_350" ){
          XSectionMap = &XSectionMap_WH2HQQ_GE2J_MJJ_120_350;
  } else if ( process == "WH2HQQ_GE2J_MJJ_GT350_PTH_GT200" ){
          XSectionMap = &XSectionMap_WH2HQQ_GE2J_MJJ_GT350_PTH_GT200;
  } else if ( process == "WH2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25" ){
          XSectionMap = &XSectionMap_WH2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25;
  } else if ( process == "WH2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25" ){
          XSectionMap = &XSectionMap_WH2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25;
  } else if ( process == "WH2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25" ){
          XSectionMap = &XSectionMap_WH2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25;
  } else if ( process == "WH2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25" ){
          XSectionMap = &XSectionMap_WH2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25;
  } else if ( process == "ZH2HQQ_FWDH" ){
          XSectionMap = &XSectionMap_ZH2HQQ_FWDH;
  } else if ( process == "ZH2HQQ_0J" ){
          XSectionMap = &XSectionMap_ZH2HQQ_0J;
  } else if ( process == "ZH2HQQ_1J" ){
          XSectionMap = &XSectionMap_ZH2HQQ_1J;
  } else if ( process == "ZH2HQQ_GE2J_MJJ_0_60" ){
          XSectionMap = &XSectionMap_ZH2HQQ_GE2J_MJJ_0_60;
  } else if ( process == "ZH2HQQ_GE2J_MJJ_60_120" ){
          XSectionMap = &XSectionMap_ZH2HQQ_GE2J_MJJ_60_120;
  } else if ( process == "ZH2HQQ_GE2J_MJJ_120_350" ){
          XSectionMap = &XSectionMap_ZH2HQQ_GE2J_MJJ_120_350;
  } else if ( process == "ZH2HQQ_GE2J_MJJ_GT350_PTH_GT200" ){
          XSectionMap = &XSectionMap_ZH2HQQ_GE2J_MJJ_GT350_PTH_GT200;
  } else if ( process == "ZH2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25" ){
          XSectionMap = &XSectionMap_ZH2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25;
  } else if ( process == "ZH2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25" ){
          XSectionMap = &XSectionMap_ZH2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25;
  } else if ( process == "ZH2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25" ){
          XSectionMap = &XSectionMap_ZH2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25;
  } else if ( process == "ZH2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25" ){
          XSectionMap = &XSectionMap_ZH2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25;
  } else if ( process == "QQ2HLNU_FWDH" ){
          XSectionMap = &XSectionMap_QQ2HLNU_FWDH;
  } else if ( process == "QQ2HLNU_PTV_0_75" ){
          XSectionMap = &XSectionMap_QQ2HLNU_PTV_0_75;
  } else if ( process == "QQ2HLNU_PTV_75_150" ){
          XSectionMap = &XSectionMap_QQ2HLNU_PTV_75_150;
  } else if ( process == "QQ2HLNU_PTV_150_250_0J" ){
          XSectionMap = &XSectionMap_QQ2HLNU_PTV_150_250_0J;
  } else if ( process == "QQ2HLNU_PTV_150_250_GE1J" ){
          XSectionMap = &XSectionMap_QQ2HLNU_PTV_150_250_GE1J;
  } else if ( process == "QQ2HLNU_PTV_GT250" ){
          XSectionMap = &XSectionMap_QQ2HLNU_PTV_GT250;
  } else if ( process == "QQ2HLL_FWDH" ){
          XSectionMap = &XSectionMap_QQ2HLL_FWDH;
  } else if ( process == "QQ2HLL_PTV_0_75" ){
          XSectionMap = &XSectionMap_QQ2HLL_PTV_0_75;
  } else if ( process == "QQ2HLL_PTV_75_150" ){
          XSectionMap = &XSectionMap_QQ2HLL_PTV_75_150;
  } else if ( process == "QQ2HLL_PTV_150_250_0J" ){
          XSectionMap = &XSectionMap_QQ2HLL_PTV_150_250_0J;
  } else if ( process == "QQ2HLL_PTV_150_250_GE1J" ){
          XSectionMap = &XSectionMap_QQ2HLL_PTV_150_250_GE1J;
  } else if ( process == "QQ2HLL_PTV_GT250" ){
          XSectionMap = &XSectionMap_QQ2HLL_PTV_GT250;
  } else if ( process == "GG2HQQ_FWDH" ){
          XSectionMap = &XSectionMap_GG2HQQ_FWDH;
  } else if ( process == "GG2HQQ_PTH_200_300" ){
          XSectionMap = &XSectionMap_GG2HQQ_PTH_200_300;
  } else if ( process == "GG2HQQ_PTH_300_450" ){
          XSectionMap = &XSectionMap_GG2HQQ_PTH_300_450;
  } else if ( process == "GG2HQQ_PTH_450_650" ){
          XSectionMap = &XSectionMap_GG2HQQ_PTH_450_650;
  } else if ( process == "GG2HQQ_PTH_GT650" ){
          XSectionMap = &XSectionMap_GG2HQQ_PTH_GT650;
  } else if ( process == "GG2HQQ_0J_PTH_0_10" ){
          XSectionMap = &XSectionMap_GG2HQQ_0J_PTH_0_10;
  } else if ( process == "GG2HQQ_0J_PTH_GT10" ){
          XSectionMap = &XSectionMap_GG2HQQ_0J_PTH_GT10;
  } else if ( process == "GG2HQQ_1J_PTH_0_60" ){
          XSectionMap = &XSectionMap_GG2HQQ_1J_PTH_0_60;
  } else if ( process == "GG2HQQ_1J_PTH_60_120" ){
          XSectionMap = &XSectionMap_GG2HQQ_1J_PTH_60_120;
  } else if ( process == "GG2HQQ_1J_PTH_120_200" ){
          XSectionMap = &XSectionMap_GG2HQQ_1J_PTH_120_200;
  } else if ( process == "GG2HQQ_GE2J_MJJ_0_350_PTH_0_60" ){
          XSectionMap = &XSectionMap_GG2HQQ_GE2J_MJJ_0_350_PTH_0_60;
  } else if ( process == "GG2HQQ_GE2J_MJJ_0_350_PTH_60_120" ){
          XSectionMap = &XSectionMap_GG2HQQ_GE2J_MJJ_0_350_PTH_60_120;
  } else if ( process == "GG2HQQ_GE2J_MJJ_0_350_PTH_120_200" ){
          XSectionMap = &XSectionMap_GG2HQQ_GE2J_MJJ_0_350_PTH_120_200;
  } else if ( process == "GG2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25" ){
          XSectionMap = &XSectionMap_GG2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25;
  } else if ( process == "GG2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25" ){
          XSectionMap = &XSectionMap_GG2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25;
  } else if ( process == "GG2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25" ){
          XSectionMap = &XSectionMap_GG2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25;
  } else if ( process == "GG2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25" ){
          XSectionMap = &XSectionMap_GG2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25;
  } else if ( process == "GG2HLL_FWDH" ){
          XSectionMap = &XSectionMap_GG2HLL_FWDH;
  } else if ( process == "GG2HLL_PTV_0_75" ){
          XSectionMap = &XSectionMap_GG2HLL_PTV_0_75;
  } else if ( process == "GG2HLL_PTV_75_150" ){
          XSectionMap = &XSectionMap_GG2HLL_PTV_75_150;
  } else if ( process == "GG2HLL_PTV_150_250_0J" ){
          XSectionMap = &XSectionMap_GG2HLL_PTV_150_250_0J;
  } else if ( process == "GG2HLL_PTV_150_250_GE1J" ){
          XSectionMap = &XSectionMap_GG2HLL_PTV_150_250_GE1J;
  } else if ( process == "GG2HLL_PTV_GT250" ){
          XSectionMap = &XSectionMap_GG2HLL_PTV_GT250;
  } else if ( process == "GG2HNUNU_FWDH" ){
          XSectionMap = &XSectionMap_GG2HNUNU_FWDH;
  } else if ( process == "GG2HNUNU_PTV_0_75" ){
          XSectionMap = &XSectionMap_GG2HNUNU_PTV_0_75;
  } else if ( process == "GG2HNUNU_PTV_75_150" ){
          XSectionMap = &XSectionMap_GG2HNUNU_PTV_75_150;
  } else if ( process == "GG2HNUNU_PTV_150_250_0J" ){
          XSectionMap = &XSectionMap_GG2HNUNU_PTV_150_250_0J;
  } else if ( process == "GG2HNUNU_PTV_150_250_GE1J" ){
          XSectionMap = &XSectionMap_GG2HNUNU_PTV_150_250_GE1J;
  } else if ( process == "GG2HNUNU_PTV_GT250" ){
          XSectionMap = &XSectionMap_GG2HNUNU_PTV_GT250;
  } else if ( process == "TTH_FWDH" ){
          XSectionMap = &XSectionMap_TTH_FWDH;
  } else if ( process == "TTH_PTH_0_60" ){
          XSectionMap = &XSectionMap_TTH_PTH_0_60;
  } else if ( process == "TTH_PTH_60_120" ){
          XSectionMap = &XSectionMap_TTH_PTH_60_120;
  } else if ( process == "TTH_PTH_120_200" ){
          XSectionMap = &XSectionMap_TTH_PTH_120_200;
  } else if ( process == "TTH_PTH_200_300" ){
          XSectionMap = &XSectionMap_TTH_PTH_200_300;
  } else if ( process == "TTH_PTH_GT300" ){
          XSectionMap = &XSectionMap_TTH_PTH_GT300;
  } else if ( process == "BBH_FWDH" ){
          XSectionMap = &XSectionMap_BBH_FWDH;
  } else if ( process == "BBH" ){
          XSectionMap = &XSectionMap_BBH;
  } else if ( process == "THQ_FWDH" ){
          XSectionMap = &XSectionMap_THQ_FWDH;
  } else if ( process == "THQ" ){
          XSectionMap = &XSectionMap_THQ;
  } else if ( process == "TH_FWDH" ){
          XSectionMap = &XSectionMap_THQ_FWDH;
  } else if ( process == "TH" ){
          XSectionMap = &XSectionMap_THQ;
  } else if ( process == "THW_FWDH" ){
          XSectionMap = &XSectionMap_THW_FWDH;
  } else if ( process == "THW" ){
          XSectionMap = &XSectionMap_THW;
  // Stage 0
  } else if ( process == "ggh" || process=="GG2H" ) {
    XSectionMap = &XSectionMap_ggh;
  } else if ( process == "vbf" || process=="VBF" ) {
    XSectionMap = &XSectionMap_vbf;
  } else if ( process == "tth" || process=="TTH" ) {
    XSectionMap = &XSectionMap_tth;
  } else if ( process == "wh") {
    XSectionMap = &XSectionMap_wh;
  } else if ( process == "zh") {
    XSectionMap = &XSectionMap_zh;
  } else if ( process=="QQ2HLNU" ) {
    XSectionMap = &XSectionMap_QQ2HLNU;
  } else if ( process=="QQ2HLL" ) {
    XSectionMap = &XSectionMap_QQ2HLL;
  } else if ( process=="GG2HLL" ) {
    XSectionMap = &XSectionMap_GG2HLL;
  } else if ( process=="WH2HQQ" ) {
    XSectionMap = &XSectionMap_WH2HQQ;
  } else if ( process=="ZH2HQQ" ) {
    XSectionMap = &XSectionMap_ZH2HQQ;
  } else {
    std::cout << "[WARNING] Normalization_13TeV: No known process found in the name!!" << std::endl;
    std::cout << "[DEBUG] Normalization_13TeV failed for process = " << process << std::endl;
    //exit(1);
  }

  for (std::map<double, double>::const_iterator iter = XSectionMap->begin();  iter != XSectionMap->end(); ++iter) {
      gr->SetPoint(gr->GetN(),iter->first, iter->second );
  }

  return gr;
}

TGraph * Normalization_13TeV::GetBrGraph()
{
  TGraph * gr = new TGraph();
  for (std::map<double, double>::const_iterator iter = BranchingRatioMap.begin();  iter != BranchingRatioMap.end(); ++iter) {
      gr->SetPoint(gr->GetN(),iter->first, iter->second );
  }
  return gr;
}

double Normalization_13TeV::GetBR(double mass) {

    for (std::map<double, double>::const_iterator iter = BranchingRatioMap.begin();  iter != BranchingRatioMap.end(); ++iter) {
        if (abs(mass-iter->first)<0.001) return iter->second;
        if (mass>iter->first) {
            double lowmass = iter->first;
            double lowbr = iter->second;
            ++iter;
            if (mass<iter->first) {
                double highmass = iter->first;
                double highbr = iter->second;
                double br = (highbr-lowbr)/(highmass-lowmass)*(mass-lowmass)+lowbr;
                return br;
            }
            --iter;
        }
    }

    std::cout << "[WARNING] Warning branching ratio outside range of 90-250GeV!!!!" << std::endl;
    //std::exit(1);
    return -1;
}

double Normalization_13TeV::GetXsection(double mass, TString HistName) {

  std::map<double,double> *XSectionMap;
  // Stage 1.2
  if ( HistName.Contains("GG2H_FWDH") ){
          XSectionMap = &XSectionMap_GG2H_FWDH;
  } else if ( HistName.Contains("GG2H_PTH_200_300") ){
          XSectionMap = &XSectionMap_GG2H_PTH_200_300;
  } else if ( HistName.Contains("GG2H_PTH_300_450") ){
          XSectionMap = &XSectionMap_GG2H_PTH_300_450;
  } else if ( HistName.Contains("GG2H_PTH_450_650") ){
          XSectionMap = &XSectionMap_GG2H_PTH_450_650;
  } else if ( HistName.Contains("GG2H_PTH_GT650") ){
          XSectionMap = &XSectionMap_GG2H_PTH_GT650;
  } else if ( HistName.Contains("GG2H_0J_PTH_0_10") ){
          XSectionMap = &XSectionMap_GG2H_0J_PTH_0_10;
  } else if ( HistName.Contains("GG2H_0J_PTH_GT10") ){
          XSectionMap = &XSectionMap_GG2H_0J_PTH_GT10;
  } else if ( HistName.Contains("GG2H_1J_PTH_0_60") ){
          XSectionMap = &XSectionMap_GG2H_1J_PTH_0_60;
  } else if ( HistName.Contains("GG2H_1J_PTH_60_120") ){
          XSectionMap = &XSectionMap_GG2H_1J_PTH_60_120;
  } else if ( HistName.Contains("GG2H_1J_PTH_120_200") ){
          XSectionMap = &XSectionMap_GG2H_1J_PTH_120_200;
  } else if ( HistName.Contains("GG2H_GE2J_MJJ_0_350_PTH_0_60") ){
          XSectionMap = &XSectionMap_GG2H_GE2J_MJJ_0_350_PTH_0_60;
  } else if ( HistName.Contains("GG2H_GE2J_MJJ_0_350_PTH_60_120") ){
          XSectionMap = &XSectionMap_GG2H_GE2J_MJJ_0_350_PTH_60_120;
  } else if ( HistName.Contains("GG2H_GE2J_MJJ_0_350_PTH_120_200") ){
          XSectionMap = &XSectionMap_GG2H_GE2J_MJJ_0_350_PTH_120_200;
  } else if ( HistName.Contains("GG2H_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25") ){
          XSectionMap = &XSectionMap_GG2H_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25;
  } else if ( HistName.Contains("GG2H_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25") ){
          XSectionMap = &XSectionMap_GG2H_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25;
  } else if ( HistName.Contains("GG2H_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25") ){
          XSectionMap = &XSectionMap_GG2H_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25;
  } else if ( HistName.Contains("GG2H_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25") ){
          XSectionMap = &XSectionMap_GG2H_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25;
  } else if ( HistName.Contains("VBF_FWDH") ){
          XSectionMap = &XSectionMap_VBF_FWDH;
  } else if ( HistName.Contains("VBF_0J") ){
          XSectionMap = &XSectionMap_VBF_0J;
  } else if ( HistName.Contains("VBF_1J") ){
          XSectionMap = &XSectionMap_VBF_1J;
  } else if ( HistName.Contains("VBF_GE2J_MJJ_0_60") ){
          XSectionMap = &XSectionMap_VBF_GE2J_MJJ_0_60;
  } else if ( HistName.Contains("VBF_GE2J_MJJ_60_120") ){
          XSectionMap = &XSectionMap_VBF_GE2J_MJJ_60_120;
  } else if ( HistName.Contains("VBF_GE2J_MJJ_120_350") ){
          XSectionMap = &XSectionMap_VBF_GE2J_MJJ_120_350;
  } else if ( HistName.Contains("VBF_GE2J_MJJ_GT350_PTH_GT200") ){
          XSectionMap = &XSectionMap_VBF_GE2J_MJJ_GT350_PTH_GT200;
  } else if ( HistName.Contains("VBF_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25") ){
          XSectionMap = &XSectionMap_VBF_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25;
  } else if ( HistName.Contains("VBF_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25") ){
          XSectionMap = &XSectionMap_VBF_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25;
  } else if ( HistName.Contains("VBF_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25") ){
          XSectionMap = &XSectionMap_VBF_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25;
  } else if ( HistName.Contains("VBF_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25") ){
          XSectionMap = &XSectionMap_VBF_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25;
  } else if ( HistName.Contains("WH2HQQ_FWDH") ){
          XSectionMap = &XSectionMap_WH2HQQ_FWDH;
  } else if ( HistName.Contains("WH2HQQ_0J") ){
          XSectionMap = &XSectionMap_WH2HQQ_0J;
  } else if ( HistName.Contains("WH2HQQ_1J") ){
          XSectionMap = &XSectionMap_WH2HQQ_1J;
  } else if ( HistName.Contains("WH2HQQ_GE2J_MJJ_0_60") ){
          XSectionMap = &XSectionMap_WH2HQQ_GE2J_MJJ_0_60;
  } else if ( HistName.Contains("WH2HQQ_GE2J_MJJ_60_120") ){
          XSectionMap = &XSectionMap_WH2HQQ_GE2J_MJJ_60_120;
  } else if ( HistName.Contains("WH2HQQ_GE2J_MJJ_120_350") ){
          XSectionMap = &XSectionMap_WH2HQQ_GE2J_MJJ_120_350;
  } else if ( HistName.Contains("WH2HQQ_GE2J_MJJ_GT350_PTH_GT200") ){
          XSectionMap = &XSectionMap_WH2HQQ_GE2J_MJJ_GT350_PTH_GT200;
  } else if ( HistName.Contains("WH2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25") ){
          XSectionMap = &XSectionMap_WH2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25;
  } else if ( HistName.Contains("WH2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25") ){
          XSectionMap = &XSectionMap_WH2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25;
  } else if ( HistName.Contains("WH2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25") ){
          XSectionMap = &XSectionMap_WH2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25;
  } else if ( HistName.Contains("WH2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25") ){
          XSectionMap = &XSectionMap_WH2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25;
  } else if ( HistName.Contains("ZH2HQQ_FWDH") ){
          XSectionMap = &XSectionMap_ZH2HQQ_FWDH;
  } else if ( HistName.Contains("ZH2HQQ_0J") ){
          XSectionMap = &XSectionMap_ZH2HQQ_0J;
  } else if ( HistName.Contains("ZH2HQQ_1J") ){
          XSectionMap = &XSectionMap_ZH2HQQ_1J;
  } else if ( HistName.Contains("ZH2HQQ_GE2J_MJJ_0_60") ){
          XSectionMap = &XSectionMap_ZH2HQQ_GE2J_MJJ_0_60;
  } else if ( HistName.Contains("ZH2HQQ_GE2J_MJJ_60_120") ){
          XSectionMap = &XSectionMap_ZH2HQQ_GE2J_MJJ_60_120;
  } else if ( HistName.Contains("ZH2HQQ_GE2J_MJJ_120_350") ){
          XSectionMap = &XSectionMap_ZH2HQQ_GE2J_MJJ_120_350;
  } else if ( HistName.Contains("ZH2HQQ_GE2J_MJJ_GT350_PTH_GT200") ){
          XSectionMap = &XSectionMap_ZH2HQQ_GE2J_MJJ_GT350_PTH_GT200;
  } else if ( HistName.Contains("ZH2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25") ){
          XSectionMap = &XSectionMap_ZH2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25;
  } else if ( HistName.Contains("ZH2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25") ){
          XSectionMap = &XSectionMap_ZH2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25;
  } else if ( HistName.Contains("ZH2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25") ){
          XSectionMap = &XSectionMap_ZH2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25;
  } else if ( HistName.Contains("ZH2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25") ){
          XSectionMap = &XSectionMap_ZH2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25;
  } else if ( HistName.Contains("QQ2HLNU_FWDH") ){
          XSectionMap = &XSectionMap_QQ2HLNU_FWDH;
  } else if ( HistName.Contains("QQ2HLNU_PTV_0_75") ){
          XSectionMap = &XSectionMap_QQ2HLNU_PTV_0_75;
  } else if ( HistName.Contains("QQ2HLNU_PTV_75_150") ){
          XSectionMap = &XSectionMap_QQ2HLNU_PTV_75_150;
  } else if ( HistName.Contains("QQ2HLNU_PTV_150_250_0J") ){
          XSectionMap = &XSectionMap_QQ2HLNU_PTV_150_250_0J;
  } else if ( HistName.Contains("QQ2HLNU_PTV_150_250_GE1J") ){
          XSectionMap = &XSectionMap_QQ2HLNU_PTV_150_250_GE1J;
  } else if ( HistName.Contains("QQ2HLNU_PTV_GT250") ){
          XSectionMap = &XSectionMap_QQ2HLNU_PTV_GT250;
  } else if ( HistName.Contains("QQ2HLL_FWDH") ){
          XSectionMap = &XSectionMap_QQ2HLL_FWDH;
  } else if ( HistName.Contains("QQ2HLL_PTV_0_75") ){
          XSectionMap = &XSectionMap_QQ2HLL_PTV_0_75;
  } else if ( HistName.Contains("QQ2HLL_PTV_75_150") ){
          XSectionMap = &XSectionMap_QQ2HLL_PTV_75_150;
  } else if ( HistName.Contains("QQ2HLL_PTV_150_250_0J") ){
          XSectionMap = &XSectionMap_QQ2HLL_PTV_150_250_0J;
  } else if ( HistName.Contains("QQ2HLL_PTV_150_250_GE1J") ){
          XSectionMap = &XSectionMap_QQ2HLL_PTV_150_250_GE1J;
  } else if ( HistName.Contains("QQ2HLL_PTV_GT250") ){
          XSectionMap = &XSectionMap_QQ2HLL_PTV_GT250;
  } else if ( HistName.Contains("GG2HQQ_FWDH") ){
          XSectionMap = &XSectionMap_GG2HQQ_FWDH;
  } else if ( HistName.Contains("GG2HQQ_PTH_200_300") ){
          XSectionMap = &XSectionMap_GG2HQQ_PTH_200_300;
  } else if ( HistName.Contains("GG2HQQ_PTH_300_450") ){
          XSectionMap = &XSectionMap_GG2HQQ_PTH_300_450;
  } else if ( HistName.Contains("GG2HQQ_PTH_450_650") ){
          XSectionMap = &XSectionMap_GG2HQQ_PTH_450_650;
  } else if ( HistName.Contains("GG2HQQ_PTH_GT650") ){
          XSectionMap = &XSectionMap_GG2HQQ_PTH_GT650;
  } else if ( HistName.Contains("GG2HQQ_0J_PTH_0_10") ){
          XSectionMap = &XSectionMap_GG2HQQ_0J_PTH_0_10;
  } else if ( HistName.Contains("GG2HQQ_0J_PTH_GT10") ){
          XSectionMap = &XSectionMap_GG2HQQ_0J_PTH_GT10;
  } else if ( HistName.Contains("GG2HQQ_1J_PTH_0_60") ){
          XSectionMap = &XSectionMap_GG2HQQ_1J_PTH_0_60;
  } else if ( HistName.Contains("GG2HQQ_1J_PTH_60_120") ){
          XSectionMap = &XSectionMap_GG2HQQ_1J_PTH_60_120;
  } else if ( HistName.Contains("GG2HQQ_1J_PTH_120_200") ){
          XSectionMap = &XSectionMap_GG2HQQ_1J_PTH_120_200;
  } else if ( HistName.Contains("GG2HQQ_GE2J_MJJ_0_350_PTH_0_60") ){
          XSectionMap = &XSectionMap_GG2HQQ_GE2J_MJJ_0_350_PTH_0_60;
  } else if ( HistName.Contains("GG2HQQ_GE2J_MJJ_0_350_PTH_60_120") ){
          XSectionMap = &XSectionMap_GG2HQQ_GE2J_MJJ_0_350_PTH_60_120;
  } else if ( HistName.Contains("GG2HQQ_GE2J_MJJ_0_350_PTH_120_200") ){
          XSectionMap = &XSectionMap_GG2HQQ_GE2J_MJJ_0_350_PTH_120_200;
  } else if ( HistName.Contains("GG2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25") ){
          XSectionMap = &XSectionMap_GG2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25;
  } else if ( HistName.Contains("GG2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25") ){
          XSectionMap = &XSectionMap_GG2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25;
  } else if ( HistName.Contains("GG2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25") ){
          XSectionMap = &XSectionMap_GG2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25;
  } else if ( HistName.Contains("GG2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25") ){
          XSectionMap = &XSectionMap_GG2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25;
  } else if ( HistName.Contains("GG2HLL_FWDH") ){
          XSectionMap = &XSectionMap_GG2HLL_FWDH;
  } else if ( HistName.Contains("GG2HLL_PTV_0_75") ){
          XSectionMap = &XSectionMap_GG2HLL_PTV_0_75;
  } else if ( HistName.Contains("GG2HLL_PTV_75_150") ){
          XSectionMap = &XSectionMap_GG2HLL_PTV_75_150;
  } else if ( HistName.Contains("GG2HLL_PTV_150_250_0J") ){
          XSectionMap = &XSectionMap_GG2HLL_PTV_150_250_0J;
  } else if ( HistName.Contains("GG2HLL_PTV_150_250_GE1J") ){
          XSectionMap = &XSectionMap_GG2HLL_PTV_150_250_GE1J;
  } else if ( HistName.Contains("GG2HLL_PTV_GT250") ){
          XSectionMap = &XSectionMap_GG2HLL_PTV_GT250;
  } else if ( HistName.Contains("GG2HNUNU_FWDH") ){
          XSectionMap = &XSectionMap_GG2HNUNU_FWDH;
  } else if ( HistName.Contains("GG2HNUNU_PTV_0_75") ){
          XSectionMap = &XSectionMap_GG2HNUNU_PTV_0_75;
  } else if ( HistName.Contains("GG2HNUNU_PTV_75_150") ){
          XSectionMap = &XSectionMap_GG2HNUNU_PTV_75_150;
  } else if ( HistName.Contains("GG2HNUNU_PTV_150_250_0J") ){
          XSectionMap = &XSectionMap_GG2HNUNU_PTV_150_250_0J;
  } else if ( HistName.Contains("GG2HNUNU_PTV_150_250_GE1J") ){
          XSectionMap = &XSectionMap_GG2HNUNU_PTV_150_250_GE1J;
  } else if ( HistName.Contains("GG2HNUNU_PTV_GT250") ){
          XSectionMap = &XSectionMap_GG2HNUNU_PTV_GT250;
  } else if ( HistName.Contains("TTH_FWDH") ){
          XSectionMap = &XSectionMap_TTH_FWDH;
  } else if ( HistName.Contains("TTH_PTH_0_60") ){
          XSectionMap = &XSectionMap_TTH_PTH_0_60;
  } else if ( HistName.Contains("TTH_PTH_60_120") ){
          XSectionMap = &XSectionMap_TTH_PTH_60_120;
  } else if ( HistName.Contains("TTH_PTH_120_200") ){
          XSectionMap = &XSectionMap_TTH_PTH_120_200;
  } else if ( HistName.Contains("TTH_PTH_200_300") ){
          XSectionMap = &XSectionMap_TTH_PTH_200_300;
  } else if ( HistName.Contains("TTH_PTH_GT300") ){
          XSectionMap = &XSectionMap_TTH_PTH_GT300;
  } else if ( HistName.Contains("BBH_FWDH") ){
          XSectionMap = &XSectionMap_BBH_FWDH;
  } else if ( HistName.Contains("BBH") ){
          XSectionMap = &XSectionMap_BBH;
  } else if ( HistName.Contains("THQ_FWDH") ){
          XSectionMap = &XSectionMap_THQ_FWDH;
  } else if ( HistName.Contains("THQ") ){
          XSectionMap = &XSectionMap_THQ;
  } else if ( HistName.Contains("THW_FWDH") ){
          XSectionMap = &XSectionMap_THW_FWDH;
  } else if ( HistName.Contains("THW") ){
          XSectionMap = &XSectionMap_THW;
  } else if ( HistName.Contains("TH_FWDH") ){
          XSectionMap = &XSectionMap_THQ_FWDH;
  } else if ( HistName.Contains("TH") ){
          XSectionMap = &XSectionMap_THQ;
  // Stage 0
  } else if ( HistName.Contains("ggh") || HistName.Contains("GG2H") ) {
    XSectionMap = &XSectionMap_ggh;
  } else if ( HistName.Contains("vbf") || HistName.Contains("VBF") ) {
    XSectionMap = &XSectionMap_vbf;
  } else if ( HistName.Contains("tth") || HistName.Contains("TTH") ) {
    XSectionMap = &XSectionMap_tth;
  } else if ( HistName.Contains("wh") ) {
    XSectionMap = &XSectionMap_wh;
  } else if ( HistName.Contains("zh") ) {
    XSectionMap = &XSectionMap_zh;
  } else if ( HistName.Contains("WH2HQQ") ) {
    XSectionMap = &XSectionMap_WH2HQQ;
  } else if ( HistName.Contains("ZH2HQQ") ) {
    XSectionMap = &XSectionMap_ZH2HQQ;
  } else if ( HistName.Contains("QQ2HLNU") ) {
    XSectionMap = &XSectionMap_QQ2HLNU;
  } else if ( HistName.Contains("QQ2HLL") ) {
    XSectionMap = &XSectionMap_QQ2HLL;
  } else if ( HistName.Contains("GG2HLL") ) {
    XSectionMap = &XSectionMap_GG2HLL;
  } else if ( HistName.Contains("BBH") ) {
    XSectionMap = &XSectionMap_BBH;
  } else if ( HistName.Contains("THQ") ) {
    XSectionMap = &XSectionMap_THQ;
  } else if ( HistName.Contains("THW") ) {
    XSectionMap = &XSectionMap_THW;
  } else {
    std::cout << "[WARNING] Normalization_13TeV: No known process found in the name!!" << HistName << std::endl;
    //exit(1);
  }

  for (std::map<double, double>::const_iterator iter = XSectionMap->begin();  iter != XSectionMap->end(); ++iter) {
      if (abs(mass-iter->first)<0.001) return iter->second;
      if (mass>iter->first) {
          double lowmass = iter->first;
          double lowxsec = iter->second;
          ++iter;
          if (mass<iter->first) {
              double highmass = iter->first;
              double highxsec = iter->second;
              double xsec = (highxsec-lowxsec)/(highmass-lowmass)*(mass-lowmass)+lowxsec;
              return xsec;
          }
          --iter;
      }
  }

  std::cout << "[WARNING] Warning cross section outside range of 80-300GeV!!!!" << std::endl;
  //exit(1);
  return -1;
}

double Normalization_13TeV::GetXsection(double mass) {
    return GetXsection(mass,"ggh") + GetXsection(mass,"vbf") + GetXsection(mass,"wh") + GetXsection(mass,"zh") + GetXsection(mass,"tth");
}

double Normalization_13TeV::GetNorm(double mass1, TH1F* hist1, double mass2, TH1F* hist2, double mass) {

  double br = GetBR(mass);
  double br1 = GetBR(mass1);
  double br2 = GetBR(mass2);

  double xsec = GetXsection(mass, hist1->GetName());
  double xsec1 = GetXsection(mass1, hist1->GetName());
  double xsec2 = GetXsection(mass2, hist2->GetName());

  double alpha = 1.0*(mass-mass1)/(mass2-mass1);
  double effAcc1 = hist1->Integral()/(xsec1*br1);
  double effAcc2 = hist2->Integral()/(xsec2*br2);

  double Normalization = (xsec*br)*(effAcc1 + alpha * (effAcc2 - effAcc1));

  return Normalization;
}
