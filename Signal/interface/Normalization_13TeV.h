#ifndef Normalization_13TeV_h
#define Normalization_13TeV_h

#include <vector>
#include <map>
#include <iostream>

#include "TH1F.h"
#include "TGraph.h"
#include "TCanvas.h"
#include "TString.h"
#include "TROOT.h"
#include "TLegend.h"
#include "TPython.h"
#include "HiggsAnalysis/CombinedLimit/interface/RooSpline1D.h"

using namespace std;

class Normalization_13TeV {

  public:
	Normalization_13TeV();

	int Init(int sqrtS);

	double GetBR(double);
	double GetXsection(double,TString);
	double GetXsection(double);
	double GetNorm(double,TH1F*,double, TH1F*,double);

	TGraph * GetSigmaGraph(TString process);
	TGraph * GetBrGraph();

  private:
	std::map<double,double> BranchingRatioMap;
	std::map<double,double> XSectionMap_ggh;
	std::map<double,double> XSectionMap_vbf;
	std::map<double,double> XSectionMap_wh;
	std::map<double,double> XSectionMap_zh;
	std::map<double,double> XSectionMap_tth;

  // Stage 0 STXS
	std::map<double,double> XSectionMap_QQ2HLNU;
	std::map<double,double> XSectionMap_QQ2HLL;
	std::map<double,double> XSectionMap_GG2HLL;
	std::map<double,double> XSectionMap_WH2HQQ;
	std::map<double,double> XSectionMap_ZH2HQQ;

  // STXS stage 1.2
    std::map<double,double> XSectionMap_GG2H_FWDH;
    std::map<double,double> XSectionMap_GG2H_PTH_200_300;
    std::map<double,double> XSectionMap_GG2H_PTH_300_450;
    std::map<double,double> XSectionMap_GG2H_PTH_450_650;
    std::map<double,double> XSectionMap_GG2H_PTH_GT650;
    std::map<double,double> XSectionMap_GG2H_0J_PTH_0_10;
    std::map<double,double> XSectionMap_GG2H_0J_PTH_GT10;
    std::map<double,double> XSectionMap_GG2H_1J_PTH_0_60;
    std::map<double,double> XSectionMap_GG2H_1J_PTH_60_120;
    std::map<double,double> XSectionMap_GG2H_1J_PTH_120_200;
    std::map<double,double> XSectionMap_GG2H_GE2J_MJJ_0_350_PTH_0_60;
    std::map<double,double> XSectionMap_GG2H_GE2J_MJJ_0_350_PTH_60_120;
    std::map<double,double> XSectionMap_GG2H_GE2J_MJJ_0_350_PTH_120_200;
    std::map<double,double> XSectionMap_GG2H_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25;
    std::map<double,double> XSectionMap_GG2H_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25;
    std::map<double,double> XSectionMap_GG2H_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25;
    std::map<double,double> XSectionMap_GG2H_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25;
    std::map<double,double> XSectionMap_VBF_FWDH;
    std::map<double,double> XSectionMap_VBF_0J;
    std::map<double,double> XSectionMap_VBF_1J;
    std::map<double,double> XSectionMap_VBF_GE2J_MJJ_0_60;
    std::map<double,double> XSectionMap_VBF_GE2J_MJJ_60_120;
    std::map<double,double> XSectionMap_VBF_GE2J_MJJ_120_350;
    std::map<double,double> XSectionMap_VBF_GE2J_MJJ_GT350_PTH_GT200;
    std::map<double,double> XSectionMap_VBF_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25;
    std::map<double,double> XSectionMap_VBF_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25;
    std::map<double,double> XSectionMap_VBF_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25;
    std::map<double,double> XSectionMap_VBF_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25;
    std::map<double,double> XSectionMap_WH2HQQ_FWDH;
    std::map<double,double> XSectionMap_WH2HQQ_0J;
    std::map<double,double> XSectionMap_WH2HQQ_1J;
    std::map<double,double> XSectionMap_WH2HQQ_GE2J_MJJ_0_60;
    std::map<double,double> XSectionMap_WH2HQQ_GE2J_MJJ_60_120;
    std::map<double,double> XSectionMap_WH2HQQ_GE2J_MJJ_120_350;
    std::map<double,double> XSectionMap_WH2HQQ_GE2J_MJJ_GT350_PTH_GT200;
    std::map<double,double> XSectionMap_WH2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25;
    std::map<double,double> XSectionMap_WH2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25;
    std::map<double,double> XSectionMap_WH2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25;
    std::map<double,double> XSectionMap_WH2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25;
    std::map<double,double> XSectionMap_ZH2HQQ_FWDH;
    std::map<double,double> XSectionMap_ZH2HQQ_0J;
    std::map<double,double> XSectionMap_ZH2HQQ_1J;
    std::map<double,double> XSectionMap_ZH2HQQ_GE2J_MJJ_0_60;
    std::map<double,double> XSectionMap_ZH2HQQ_GE2J_MJJ_60_120;
    std::map<double,double> XSectionMap_ZH2HQQ_GE2J_MJJ_120_350;
    std::map<double,double> XSectionMap_ZH2HQQ_GE2J_MJJ_GT350_PTH_GT200;
    std::map<double,double> XSectionMap_ZH2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25;
    std::map<double,double> XSectionMap_ZH2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25;
    std::map<double,double> XSectionMap_ZH2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25;
    std::map<double,double> XSectionMap_ZH2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25;
    std::map<double,double> XSectionMap_QQ2HLNU_FWDH;
    std::map<double,double> XSectionMap_QQ2HLNU_PTV_0_75;
    std::map<double,double> XSectionMap_QQ2HLNU_PTV_75_150;
    std::map<double,double> XSectionMap_QQ2HLNU_PTV_150_250_0J;
    std::map<double,double> XSectionMap_QQ2HLNU_PTV_150_250_GE1J;
    std::map<double,double> XSectionMap_QQ2HLNU_PTV_GT250;
    std::map<double,double> XSectionMap_QQ2HLL_FWDH;
    std::map<double,double> XSectionMap_QQ2HLL_PTV_0_75;
    std::map<double,double> XSectionMap_QQ2HLL_PTV_75_150;
    std::map<double,double> XSectionMap_QQ2HLL_PTV_150_250_0J;
    std::map<double,double> XSectionMap_QQ2HLL_PTV_150_250_GE1J;
    std::map<double,double> XSectionMap_QQ2HLL_PTV_GT250;
    std::map<double,double> XSectionMap_GG2HQQ_FWDH;
    std::map<double,double> XSectionMap_GG2HQQ_PTH_200_300;
    std::map<double,double> XSectionMap_GG2HQQ_PTH_300_450;
    std::map<double,double> XSectionMap_GG2HQQ_PTH_450_650;
    std::map<double,double> XSectionMap_GG2HQQ_PTH_GT650;
    std::map<double,double> XSectionMap_GG2HQQ_0J_PTH_0_10;
    std::map<double,double> XSectionMap_GG2HQQ_0J_PTH_GT10;
    std::map<double,double> XSectionMap_GG2HQQ_1J_PTH_0_60;
    std::map<double,double> XSectionMap_GG2HQQ_1J_PTH_60_120;
    std::map<double,double> XSectionMap_GG2HQQ_1J_PTH_120_200;
    std::map<double,double> XSectionMap_GG2HQQ_GE2J_MJJ_0_350_PTH_0_60;
    std::map<double,double> XSectionMap_GG2HQQ_GE2J_MJJ_0_350_PTH_60_120;
    std::map<double,double> XSectionMap_GG2HQQ_GE2J_MJJ_0_350_PTH_120_200;
    std::map<double,double> XSectionMap_GG2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25;
    std::map<double,double> XSectionMap_GG2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25;
    std::map<double,double> XSectionMap_GG2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25;
    std::map<double,double> XSectionMap_GG2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25;
    std::map<double,double> XSectionMap_GG2HLL_FWDH;
    std::map<double,double> XSectionMap_GG2HLL_PTV_0_75;
    std::map<double,double> XSectionMap_GG2HLL_PTV_75_150;
    std::map<double,double> XSectionMap_GG2HLL_PTV_150_250_0J;
    std::map<double,double> XSectionMap_GG2HLL_PTV_150_250_GE1J;
    std::map<double,double> XSectionMap_GG2HLL_PTV_GT250;
    std::map<double,double> XSectionMap_GG2HNUNU_FWDH;
    std::map<double,double> XSectionMap_GG2HNUNU_PTV_0_75;
    std::map<double,double> XSectionMap_GG2HNUNU_PTV_75_150;
    std::map<double,double> XSectionMap_GG2HNUNU_PTV_150_250_0J;
    std::map<double,double> XSectionMap_GG2HNUNU_PTV_150_250_GE1J;
    std::map<double,double> XSectionMap_GG2HNUNU_PTV_GT250;
    std::map<double,double> XSectionMap_TTH_FWDH;
    std::map<double,double> XSectionMap_TTH_PTH_0_60;
    std::map<double,double> XSectionMap_TTH_PTH_60_120;
    std::map<double,double> XSectionMap_TTH_PTH_120_200; 
    std::map<double,double> XSectionMap_TTH_PTH_200_300;
    std::map<double,double> XSectionMap_TTH_PTH_GT300;
    std::map<double,double> XSectionMap_BBH_FWDH;
    std::map<double,double> XSectionMap_BBH;
    std::map<double,double> XSectionMap_THQ_FWDH;
    std::map<double,double> XSectionMap_THQ;
    std::map<double,double> XSectionMap_THW_FWDH;
    std::map<double,double> XSectionMap_THW;


};
#endif
