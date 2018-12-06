#include "../interface/Normalization_13TeV.h"

#include "TSystem.h"

Normalization_13TeV::Normalization_13TeV(){
}

int Normalization_13TeV::Init(int sqrtS){

    //TPython::Exec("import $(CMSSW_BASE).src.h2gglobe.AnalysisScripts.AnalysisScripts.python.buildSMHiggsSignalXSBR");
    TPython::Exec("import os,imp");
    const char * env = gSystem->Getenv("CMSSW_BASE");
    //std::string globeRt = ( env != 0 ? env : H2GGLOBE_BASE "/AnalysisScripts");
   // std::string globeRt = ( env != 0 ? env : env + "src/flashggFinalFits/Signal")
	 std::string globeRt = env;
	 if (globeRt !=0){
	 globeRt = globeRt+"/src/flashggFinalFit/Signal";
	 }
	// std::cout << " Form " << Form("buildSMHiggsSignalXSBR = imp.load_source('*', '%s/python/buildSMHiggsSignalXSBR.py')",globeRt.c_str()) << std::endl;
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
        double valXSQQ2HLNU    = valXSWH*(3.*10.86*0.01)/*3xBR(W to lv)*/;	
        double valXSQQ2HLL     = valXSZH*(3*3.3658*0.01 + 20.00*0.01)/*BR(Z to ll) + BR(Z to invisible)*/;	
        double valXSVH2HQQ     = valXSWH*(67.41*0.01)/*BR(W to hadrons)*/ + valXSZH*(69.91*0.01)/*BR(Z to hadrons)*/;	
        double valXSWH2HQQ     = valXSWH*(67.41*0.01)/*BR(W to hadrons)*/;
        double valXSZH2HQQ     = valXSZH*(69.91*0.01)/*BR(Z to hadrons)*/;	
        double valXSTHQ        = 0.074;
        double valXSTHW        = 0.015;

	BranchingRatioMap[mH]	= valBR;
        XSectionMap_ggh[mH]	= valXSggH; 	
        XSectionMap_vbf[mH]	= valXSqqH; 	
        XSectionMap_tth[mH]	= valXSttH; 	
        XSectionMap_wh[mH]	= valXSWH; 	
        XSectionMap_zh[mH]	= valXSZH;	

        XSectionMap_QQ2HLNU[mH]	= valXSQQ2HLNU;
        XSectionMap_QQ2HLL[mH]	= valXSQQ2HLL;
        XSectionMap_VH2HQQ[mH]	= valXSVH2HQQ;
        XSectionMap_WH2HQQ[mH]	= valXSWH2HQQ;
        XSectionMap_ZH2HQQ[mH]	= valXSZH2HQQ;

        XSectionMap_BBH[mH]	= valXSbbH;
        XSectionMap_THQ[mH]	= valXSTHQ;
        XSectionMap_THW[mH]	= valXSTHW;
	
        //Stage 1 
        XSectionMap_GG2H_0J[mH]                  = 0.6077*valXSggH;
        XSectionMap_GG2H_1J_PTH_0_60[mH]         = 0.1487*valXSggH;
        XSectionMap_GG2H_1J_PTH_60_120[mH]       = 0.1022*valXSggH;
        XSectionMap_GG2H_1J_PTH_120_200[mH]      = 0.0164*valXSggH;
        XSectionMap_GG2H_1J_PTH_GT200[mH]        = 0.0033*valXSggH;
        XSectionMap_GG2H_GE2J_PTH_0_60[mH]       = 0.0280*valXSggH;
        XSectionMap_GG2H_GE2J_PTH_60_120[mH]     = 0.0453*valXSggH;
        XSectionMap_GG2H_GE2J_PTH_120_200[mH]    = 0.0237*valXSggH;
        XSectionMap_GG2H_GE2J_PTH_GT200[mH]      = 0.0101*valXSggH;
        XSectionMap_GG2H_VBFTOPO_JET3VETO[mH]    = 0.0056*valXSggH;
        XSectionMap_GG2H_VBFTOPO_JET3[mH]        = 0.0089*valXSggH;

        XSectionMap_VBF_PTJET1_GT200[mH]         = 0.0447*valXSqqH;
        XSectionMap_VBF_VH2JET[mH]               = 0.0256*valXSqqH;
        XSectionMap_VBF_VBFTOPO_JET3VETO[mH]     = 0.1732*valXSqqH;
        XSectionMap_VBF_VBFTOPO_JET3[mH]         = 0.1411*valXSqqH;
        XSectionMap_VBF_REST[mH]                 = 0.6153*valXSqqH;

        XSectionMap_QQ2HLNU_PTV_0_150[mH]        = 0.8670*valXSQQ2HLNU;
        XSectionMap_QQ2HLNU_PTV_150_250_0J[mH]   = 0.0570*valXSQQ2HLNU;
        XSectionMap_QQ2HLNU_PTV_150_250_GE1J[mH] = 0.0462*valXSQQ2HLNU;
        XSectionMap_QQ2HLNU_PTV_GT250[mH]        = 0.0297*valXSQQ2HLNU;

        XSectionMap_QQ2HLL_PTV_0_150[mH]         = 0.8663*valXSQQ2HLL;
        XSectionMap_QQ2HLL_PTV_150_250_0J[mH]    = 0.0557*valXSQQ2HLL;
        XSectionMap_QQ2HLL_PTV_150_250_GE1J[mH]  = 0.0464*valXSQQ2HLL;
        XSectionMap_QQ2HLL_PTV_GT250[mH]         = 0.0315*valXSQQ2HLL;

        XSectionMap_WH2HQQ_PTJET1_GT200[mH]      = 0.0417*valXSWH2HQQ;
        XSectionMap_WH2HQQ_VH2JET[mH]            = 0.3105*valXSWH2HQQ;
        XSectionMap_WH2HQQ_VBFTOPO_JET3VETO[mH]  = 0.0021*valXSWH2HQQ;
        XSectionMap_WH2HQQ_VBFTOPO_JET3[mH]      = 0.0086*valXSWH2HQQ;
        XSectionMap_WH2HQQ_REST[mH]              = 0.6371*valXSWH2HQQ;

        XSectionMap_ZH2HQQ_PTJET1_GT200[mH]      = 0.0429*valXSZH2HQQ;
        XSectionMap_ZH2HQQ_VH2JET[mH]            = 0.3614*valXSZH2HQQ;
        XSectionMap_ZH2HQQ_VBFTOPO_JET3VETO[mH]  = 0.0016*valXSZH2HQQ;
        XSectionMap_ZH2HQQ_VBFTOPO_JET3[mH]      = 0.0118*valXSZH2HQQ;
        XSectionMap_ZH2HQQ_REST[mH]              = 0.5824*valXSZH2HQQ;

        XSectionMap_TTH[mH]                      = valXSttH;
        XSectionMap_BBH[mH]                      = valXSbbH;
        XSectionMap_THQ[mH]                      = valXSTHQ;
        XSectionMap_THW[mH]                      = valXSTHW;
    }
}

TGraph * Normalization_13TeV::GetSigmaGraph(TString process)
{
	TGraph * gr = new TGraph();
	std::map<double, double> * XSectionMap = 0;
        if ( process == "GG2H_0J" ) {
                XSectionMap = &XSectionMap_GG2H_0J;
        } else if ( process == "GG2H_1J_PTH_0_60" ) {
                XSectionMap = &XSectionMap_GG2H_1J_PTH_0_60;
        } else if ( process == "GG2H_1J_PTH_60_120" ) {
                XSectionMap = &XSectionMap_GG2H_1J_PTH_60_120;
        } else if ( process == "GG2H_1J_PTH_120_200" ) {
                XSectionMap = &XSectionMap_GG2H_1J_PTH_120_200;
        } else if ( process == "GG2H_1J_PTH_GT200" ) {
                XSectionMap = &XSectionMap_GG2H_1J_PTH_GT200;
        } else if ( process == "GG2H_GE2J_PTH_0_60" ) {
                XSectionMap = &XSectionMap_GG2H_GE2J_PTH_0_60;
        } else if ( process == "GG2H_GE2J_PTH_60_120" ) {
                XSectionMap = &XSectionMap_GG2H_GE2J_PTH_60_120;
        } else if ( process == "GG2H_GE2J_PTH_120_200" ) {
                XSectionMap = &XSectionMap_GG2H_GE2J_PTH_120_200;
        } else if ( process == "GG2H_GE2J_PTH_GT200" ) {
                XSectionMap = &XSectionMap_GG2H_GE2J_PTH_GT200;
        } else if ( process == "GG2H_VBFTOPO_JET3VETO" ) {
                XSectionMap = &XSectionMap_GG2H_VBFTOPO_JET3VETO;
        } else if ( process == "GG2H_VBFTOPO_JET3" ) {
                XSectionMap = &XSectionMap_GG2H_VBFTOPO_JET3;
        } else if ( process == "VBF_PTJET1_GT200" ) {
                XSectionMap = &XSectionMap_VBF_PTJET1_GT200;
        } else if ( process == "VBF_VH2JET" ) {
                XSectionMap = &XSectionMap_VBF_VH2JET;
        } else if ( process == "VBF_VBFTOPO_JET3VETO" ) {
                XSectionMap = &XSectionMap_VBF_VBFTOPO_JET3VETO;
        } else if ( process == "VBF_VBFTOPO_JET3" ) {
                XSectionMap = &XSectionMap_VBF_VBFTOPO_JET3;
        } else if ( process == "VBF_REST" ) {
                XSectionMap = &XSectionMap_VBF_REST;
        } else if ( process == "TTH" ) {
                XSectionMap = &XSectionMap_TTH;
        } else if ( process == "QQ2HLNU_PTV_GT250" ) {
                XSectionMap = &XSectionMap_QQ2HLNU_PTV_GT250;
        } else if ( process == "QQ2HLNU_PTV_150_250_GE1J" ) {
                XSectionMap = &XSectionMap_QQ2HLNU_PTV_150_250_GE1J;
        } else if ( process == "QQ2HLNU_PTV_150_250_0J" ) {
                XSectionMap = &XSectionMap_QQ2HLNU_PTV_150_250_0J;
        } else if ( process == "QQ2HLNU_PTV_0_150" ) {
                XSectionMap = &XSectionMap_QQ2HLNU_PTV_0_150;
        } else if ( process == "WH2HQQ_PTJET1_GT200" ) {
                XSectionMap = &XSectionMap_WH2HQQ_PTJET1_GT200;
        } else if ( process == "WH2HQQ_VH2JET" ) {
                XSectionMap = &XSectionMap_WH2HQQ_VH2JET;
        } else if ( process == "WH2HQQ_VBFTOPO_JET3VETO" ) {
                XSectionMap = &XSectionMap_WH2HQQ_VBFTOPO_JET3VETO;
        } else if ( process == "WH2HQQ_VBFTOPO_JET3" ) {
                XSectionMap = &XSectionMap_WH2HQQ_VBFTOPO_JET3;
        } else if ( process == "WH2HQQ_REST" ) {
                XSectionMap = &XSectionMap_WH2HQQ_REST;
        } else if ( process == "QQ2HLL_PTV_GT250" ) {
                XSectionMap = &XSectionMap_QQ2HLL_PTV_GT250;
        } else if ( process == "QQ2HLL_PTV_150_250_GE1J" ) {
                XSectionMap = &XSectionMap_QQ2HLL_PTV_150_250_GE1J;
        } else if ( process == "QQ2HLL_PTV_150_250_0J" ) {
                XSectionMap = &XSectionMap_QQ2HLL_PTV_150_250_0J;
        } else if ( process == "QQ2HLL_PTV_0_150" ) {
                XSectionMap = &XSectionMap_QQ2HLL_PTV_0_150;
        } else if ( process == "ZH2HQQ_PTJET1_GT200" ) {
                XSectionMap = &XSectionMap_ZH2HQQ_PTJET1_GT200;
        } else if ( process == "ZH2HQQ_VH2JET" ) {
                XSectionMap = &XSectionMap_ZH2HQQ_VH2JET;
        } else if ( process == "ZH2HQQ_VBFTOPO_JET3VETO" ) {
                XSectionMap = &XSectionMap_ZH2HQQ_VBFTOPO_JET3VETO;
        } else if ( process == "ZH2HQQ_VBFTOPO_JET3" ) {
                XSectionMap = &XSectionMap_ZH2HQQ_VBFTOPO_JET3;
        } else if ( process == "ZH2HQQ_REST" ) {
                XSectionMap = &XSectionMap_ZH2HQQ_REST;
        } else if ( process == "BBH" ) {
                XSectionMap = &XSectionMap_BBH;
        } else if ( process == "THQ" ) {
                XSectionMap = &XSectionMap_THQ;
        } else if ( process == "THW" ) {
                XSectionMap = &XSectionMap_THW;
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
	} else if ( process=="VH2HQQ" ) {
		XSectionMap = &XSectionMap_VH2HQQ;
	} else if ( process=="WH2HQQ" ) {
		XSectionMap = &XSectionMap_WH2HQQ;
	} else if ( process=="ZH2HQQ" ) {
		XSectionMap = &XSectionMap_ZH2HQQ;
	} else if ( process=="BBH" ) {
		XSectionMap = &XSectionMap_BBH;
	} else if ( process=="THQ" ) {
		XSectionMap = &XSectionMap_THQ;
	} else if ( process=="THW" ) {
		XSectionMap = &XSectionMap_THW;
	} else {
		std::cout << "[WARNING] Normalization_13TeV: No known process found in the name!!" << std::endl;
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
		//if (mass==iter->first) return iter->second;
		if (abs(mass-iter->first)<0.001) return iter->second; //FIXME
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

        if ( HistName.Contains("GG2H_0J") ) {
                XSectionMap = &XSectionMap_GG2H_0J;
        } else if ( HistName.Contains("GG2H_1J_PTH_0_60") ) {
                XSectionMap = &XSectionMap_GG2H_1J_PTH_0_60;
        } else if ( HistName.Contains("GG2H_1J_PTH_60_120") ) {
                XSectionMap = &XSectionMap_GG2H_1J_PTH_60_120;
        } else if ( HistName.Contains("GG2H_1J_PTH_120_200") ) {
                XSectionMap = &XSectionMap_GG2H_1J_PTH_120_200;
        } else if ( HistName.Contains("GG2H_1J_PTH_GT200") ) {
                XSectionMap = &XSectionMap_GG2H_1J_PTH_GT200;
        } else if ( HistName.Contains("GG2H_GE2J_PTH_0_60") ) {
                XSectionMap = &XSectionMap_GG2H_GE2J_PTH_0_60;
        } else if ( HistName.Contains("GG2H_GE2J_PTH_60_120") ) {
                XSectionMap = &XSectionMap_GG2H_GE2J_PTH_60_120;
        } else if ( HistName.Contains("GG2H_GE2J_PTH_120_200") ) {
                XSectionMap = &XSectionMap_GG2H_GE2J_PTH_120_200;
        } else if ( HistName.Contains("GG2H_GE2J_PTH_GT200") ) {
                XSectionMap = &XSectionMap_GG2H_GE2J_PTH_GT200;
        } else if ( HistName.Contains("GG2H_VBFTOPO_JET3VETO") ) {
                XSectionMap = &XSectionMap_GG2H_VBFTOPO_JET3VETO;
        } else if ( HistName.Contains("GG2H_VBFTOPO_JET3") ) {
                XSectionMap = &XSectionMap_GG2H_VBFTOPO_JET3;
        } else if ( HistName.Contains("VBF_PTJET1_GT200") ) {
                XSectionMap = &XSectionMap_VBF_PTJET1_GT200;
        } else if ( HistName.Contains("VBF_VH2JET") ) {
                XSectionMap = &XSectionMap_VBF_VH2JET;
        } else if ( HistName.Contains("VBF_VBFTOPO_JET3VETO") ) {
                XSectionMap = &XSectionMap_VBF_VBFTOPO_JET3VETO;
        } else if ( HistName.Contains("VBF_VBFTOPO_JET3") ) {
                XSectionMap = &XSectionMap_VBF_VBFTOPO_JET3;
        } else if ( HistName.Contains("VBF_REST") ) {
                XSectionMap = &XSectionMap_VBF_REST;
        } else if ( HistName.Contains("TTH") ) {
                XSectionMap = &XSectionMap_TTH;
        } else if ( HistName.Contains("QQ2HLNU_PTV_GT250") ) {
                XSectionMap = &XSectionMap_QQ2HLNU_PTV_GT250;
        } else if ( HistName.Contains("QQ2HLNU_PTV_150_250_GE1J") ) {
                XSectionMap = &XSectionMap_QQ2HLNU_PTV_150_250_GE1J;
        } else if ( HistName.Contains("QQ2HLNU_PTV_150_250_0J") ) {
                XSectionMap = &XSectionMap_QQ2HLNU_PTV_150_250_0J;
        } else if ( HistName.Contains("QQ2HLNU_PTV_0_150") ) {
                XSectionMap = &XSectionMap_QQ2HLNU_PTV_0_150;
        } else if ( HistName.Contains("WH2HQQ_PTJET1_GT200") ) {
                XSectionMap = &XSectionMap_WH2HQQ_PTJET1_GT200;
        } else if ( HistName.Contains("WH2HQQ_VH2JET") ) {
                XSectionMap = &XSectionMap_WH2HQQ_VH2JET;
        } else if ( HistName.Contains("WH2HQQ_VBFTOPO_JET3VETO") ) {
                XSectionMap = &XSectionMap_WH2HQQ_VBFTOPO_JET3VETO;
        } else if ( HistName.Contains("WH2HQQ_VBFTOPO_JET3") ) {
                XSectionMap = &XSectionMap_WH2HQQ_VBFTOPO_JET3;
        } else if ( HistName.Contains("WH2HQQ_REST") ) {
                XSectionMap = &XSectionMap_WH2HQQ_REST;
        } else if ( HistName.Contains("QQ2HLL_PTV_GT250") ) {
                XSectionMap = &XSectionMap_QQ2HLL_PTV_GT250;
        } else if ( HistName.Contains("QQ2HLL_PTV_150_250_GE1J") ) {
                XSectionMap = &XSectionMap_QQ2HLL_PTV_150_250_GE1J;
        } else if ( HistName.Contains("QQ2HLL_PTV_150_250_0J") ) {
                XSectionMap = &XSectionMap_QQ2HLL_PTV_150_250_0J;
        } else if ( HistName.Contains("QQ2HLL_PTV_0_150") ) {
                XSectionMap = &XSectionMap_QQ2HLL_PTV_0_150;
        } else if ( HistName.Contains("ZH2HQQ_PTJET1_GT200") ) {
                XSectionMap = &XSectionMap_ZH2HQQ_PTJET1_GT200;
        } else if ( HistName.Contains("ZH2HQQ_VH2JET") ) {
                XSectionMap = &XSectionMap_ZH2HQQ_VH2JET;
        } else if ( HistName.Contains("ZH2HQQ_VBFTOPO_JET3VETO") ) {
                XSectionMap = &XSectionMap_ZH2HQQ_VBFTOPO_JET3VETO;
        } else if ( HistName.Contains("ZH2HQQ_VBFTOPO_JET3") ) {
                XSectionMap = &XSectionMap_ZH2HQQ_VBFTOPO_JET3;
        } else if ( HistName.Contains("ZH2HQQ_REST") ) {
                XSectionMap = &XSectionMap_ZH2HQQ_REST;
        } else if ( HistName.Contains("BBH") ) {
                XSectionMap = &XSectionMap_BBH;
        } else if ( HistName.Contains("THQ") ) {
                XSectionMap = &XSectionMap_THQ;
        } else if ( HistName.Contains("THW") ) {
                XSectionMap = &XSectionMap_THW;
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
	} else if ( HistName.Contains("QQ2HLNU") ) {
		XSectionMap = &XSectionMap_QQ2HLNU;
	} else if ( HistName.Contains("QQ2HLL") ) {
		XSectionMap = &XSectionMap_QQ2HLL;
	} else if ( HistName.Contains("VH2HQQ") ) {
		XSectionMap = &XSectionMap_VH2HQQ;
	} else if ( HistName.Contains("WH2HQQ") ) {
		XSectionMap = &XSectionMap_WH2HQQ;
	} else if ( HistName.Contains("ZH2HQQ") ) {
		XSectionMap = &XSectionMap_ZH2HQQ;
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
		//if (mass==iter->first) return iter->second;
		if (abs(mass-iter->first)<0.001) return iter->second; //FIXME
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
