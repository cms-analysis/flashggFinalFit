# Python script to hold replacement model mapping for different analyses
from collections import OrderedDict as od

# Add analyses to globalReplacementMap. See "STXS" as an example
globalReplacementMap = od()

# Example analysis which with cats Untagged_Tag0,VBF_Tag0
globalReplacementMap['example'] = od()
# For WRONG VERTEX SCENARIO:
#  * single proc x cat for wrong vertex since for dZ > 1cm shape independent of proc x cat
#  * use proc x cat with highest number of WV events
globalReplacementMap['example']['procWV'] = "GG2H"
globalReplacementMap['example']['catWV'] = "Untagged_Tag0"
# For RIGHT VERTEX SCENARIO:
#  * default you should add is diagonal process from given category 
#  * if few events in diagonal process then may need to change the category aswell (see catRVMap)
#  * map must contain entry for all cats being processed (for replacement proc and cat)
globalReplacementMap['example']['procRVMap'] = od()
globalReplacementMap["example"]["procRVMap"]["Untagged_Tag0"] = "GG2H"
globalReplacementMap["example"]["procRVMap"]["VBF_Tag0"] = "VBF"
# Replacement category for RV fit
globalReplacementMap["example"]["catRVMap"] = od()
globalReplacementMap["example"]["catRVMap"]["Untagged_Tag0"] = "Untagged_Tag0"
globalReplacementMap["example"]["catRVMap"]["VBF_Tag0"] = "VBF_Tag0"

# Tutorial analysis
globalReplacementMap['tutorial'] = od()
# For WRONG VERTEX SCENARIO:
#  * single proc x cat for wrong vertex since for dZ > 1cm shape independent of proc x cat
#  * use proc x cat with highest number of WV events
globalReplacementMap['tutorial']['procWV'] = "GG2H"
globalReplacementMap['tutorial']['catWV'] = "EBEB_highR9highR9"
# For RIGHT VERTEX SCENARIO
#  * default mapping is to use diagonal process from given category 
#  * if few events in diagonal process then may need to change the category aswell (see catRVMap)
#  * map must contain entry for all cats being processed (for replacement proc and cat)
globalReplacementMap['tutorial']['procRVMap'] = od()
globalReplacementMap["tutorial"]["procRVMap"]["EBEB_highR9highR9"] = "GG2H"
globalReplacementMap["tutorial"]["procRVMap"]["EBEB_highR9lowR9"] = "GG2H"
globalReplacementMap["tutorial"]["procRVMap"]["EBEB_lowR9highR9"] = "GG2H"
globalReplacementMap["tutorial"]["procRVMap"]["EBEE_highR9highR9"] = "GG2H"
globalReplacementMap["tutorial"]["procRVMap"]["EBEE_highR9lowR9"] = "GG2H"
globalReplacementMap["tutorial"]["procRVMap"]["EBEE_lowR9highR9"] = "GG2H"
globalReplacementMap["tutorial"]["procRVMap"]["EEEB_highR9highR9"] = "GG2H"
globalReplacementMap["tutorial"]["procRVMap"]["EEEB_highR9lowR9"] = "GG2H"
globalReplacementMap["tutorial"]["procRVMap"]["EEEB_lowR9highR9"] = "GG2H"
globalReplacementMap["tutorial"]["procRVMap"]["EEEE_incl"] = "GG2H"
globalReplacementMap['tutorial']['catRVMap'] = od()
globalReplacementMap["tutorial"]["catRVMap"]["EBEB_highR9highR9"] = "EBEB_highR9highR9"
globalReplacementMap["tutorial"]["catRVMap"]["EBEB_highR9lowR9"] = "EBEB_highR9lowR9"
globalReplacementMap["tutorial"]["catRVMap"]["EBEB_lowR9highR9"] = "EBEB_lowR9highR9"
globalReplacementMap["tutorial"]["catRVMap"]["EBEE_highR9highR9"] = "EBEE_highR9highR9"
globalReplacementMap["tutorial"]["catRVMap"]["EBEE_highR9lowR9"] = "EBEE_highR9lowR9"
globalReplacementMap["tutorial"]["catRVMap"]["EBEE_lowR9highR9"] = "EBEE_lowR9highR9"
globalReplacementMap["tutorial"]["catRVMap"]["EEEB_highR9highR9"] = "EEEB_highR9highR9"
globalReplacementMap["tutorial"]["catRVMap"]["EEEB_highR9lowR9"] = "EEEB_highR9lowR9"
globalReplacementMap["tutorial"]["catRVMap"]["EEEB_lowR9highR9"] = "EEEB_lowR9highR9"
globalReplacementMap["tutorial"]["catRVMap"]["EEEE_incl"] = "EEEE_incl"


# STXS analysis
globalReplacementMap['STXS'] = od()
# For WRONG VERTEX SCENARIO:
#  * single proc x cat for wrong vertex since for dZ > 1cm shape independent of proc x cat
#  * use proc x cat with highest number of WV events
globalReplacementMap['STXS']['procWV'] = "GG2H_0J_PTH_GT10"
globalReplacementMap['STXS']['catWV'] = "RECO_0J_PTH_GT10_Tag1"
# For RIGHT VERTEX SCENARIO:
#  * default mapping is to use diagonal process from given category 
#  * if few events in diagonal process then may need to change the category aswell (see catRVMap)
#  * map must contain entry for all cats being processed (for replacement proc and cat)
globalReplacementMap['STXS']['procRVMap'] = od()
globalReplacementMap["STXS"]["procRVMap"]["RECO_0J_PTH_0_10_Tag0"] = "GG2H_0J_PTH_0_10"
globalReplacementMap["STXS"]["procRVMap"]["RECO_0J_PTH_0_10_Tag1"] = "GG2H_0J_PTH_0_10"
globalReplacementMap["STXS"]["procRVMap"]["RECO_0J_PTH_0_10_Tag2"] = "GG2H_0J_PTH_0_10"
globalReplacementMap["STXS"]["procRVMap"]["RECO_0J_PTH_GT10_Tag0"] = "GG2H_0J_PTH_GT10"
globalReplacementMap["STXS"]["procRVMap"]["RECO_0J_PTH_GT10_Tag1"] = "GG2H_0J_PTH_GT10"
globalReplacementMap["STXS"]["procRVMap"]["RECO_0J_PTH_GT10_Tag2"] = "GG2H_0J_PTH_GT10"
globalReplacementMap["STXS"]["procRVMap"]["RECO_1J_PTH_0_60_Tag0"] = "GG2H_1J_PTH_0_60"
globalReplacementMap["STXS"]["procRVMap"]["RECO_1J_PTH_0_60_Tag1"] = "GG2H_1J_PTH_0_60"
globalReplacementMap["STXS"]["procRVMap"]["RECO_1J_PTH_0_60_Tag2"] = "GG2H_1J_PTH_0_60"
globalReplacementMap["STXS"]["procRVMap"]["RECO_1J_PTH_120_200_Tag0"] = "GG2H_1J_PTH_120_200"
globalReplacementMap["STXS"]["procRVMap"]["RECO_1J_PTH_120_200_Tag1"] = "GG2H_1J_PTH_120_200"
globalReplacementMap["STXS"]["procRVMap"]["RECO_1J_PTH_120_200_Tag2"] = "GG2H_1J_PTH_120_200"
globalReplacementMap["STXS"]["procRVMap"]["RECO_1J_PTH_60_120_Tag0"] = "GG2H_1J_PTH_60_120"
globalReplacementMap["STXS"]["procRVMap"]["RECO_1J_PTH_60_120_Tag1"] = "GG2H_1J_PTH_60_120"
globalReplacementMap["STXS"]["procRVMap"]["RECO_1J_PTH_60_120_Tag2"] = "GG2H_1J_PTH_60_120"
globalReplacementMap["STXS"]["procRVMap"]["RECO_GE2J_PTH_0_60_Tag0"] = "GG2H_GE2J_MJJ_0_350_PTH_0_60"
globalReplacementMap["STXS"]["procRVMap"]["RECO_GE2J_PTH_0_60_Tag1"] = "GG2H_GE2J_MJJ_0_350_PTH_0_60"
globalReplacementMap["STXS"]["procRVMap"]["RECO_GE2J_PTH_0_60_Tag2"] = "GG2H_GE2J_MJJ_0_350_PTH_0_60"
globalReplacementMap["STXS"]["procRVMap"]["RECO_GE2J_PTH_120_200_Tag0"] = "GG2H_GE2J_MJJ_0_350_PTH_120_200"
globalReplacementMap["STXS"]["procRVMap"]["RECO_GE2J_PTH_120_200_Tag1"] = "GG2H_GE2J_MJJ_0_350_PTH_120_200"
globalReplacementMap["STXS"]["procRVMap"]["RECO_GE2J_PTH_120_200_Tag2"] = "GG2H_GE2J_MJJ_0_350_PTH_120_200"
globalReplacementMap["STXS"]["procRVMap"]["RECO_GE2J_PTH_60_120_Tag0"] = "GG2H_GE2J_MJJ_0_350_PTH_60_120"
globalReplacementMap["STXS"]["procRVMap"]["RECO_GE2J_PTH_60_120_Tag1"] = "GG2H_GE2J_MJJ_0_350_PTH_60_120"
globalReplacementMap["STXS"]["procRVMap"]["RECO_GE2J_PTH_60_120_Tag2"] = "GG2H_GE2J_MJJ_0_350_PTH_60_120"
globalReplacementMap["STXS"]["procRVMap"]["RECO_PTH_200_300_Tag0"] = "GG2H_PTH_200_300"
globalReplacementMap["STXS"]["procRVMap"]["RECO_PTH_200_300_Tag1"] = "GG2H_PTH_200_300"
globalReplacementMap["STXS"]["procRVMap"]["RECO_PTH_300_450_Tag0"] = "GG2H_PTH_300_450"
globalReplacementMap["STXS"]["procRVMap"]["RECO_PTH_300_450_Tag1"] = "GG2H_PTH_300_450"
globalReplacementMap["STXS"]["procRVMap"]["RECO_PTH_450_650_Tag0"] = "GG2H_PTH_450_650"
globalReplacementMap["STXS"]["procRVMap"]["RECO_PTH_GT650_Tag0"] = "GG2H_PTH_GT650"
globalReplacementMap["STXS"]["procRVMap"]["RECO_THQ_LEP"] = "THQ"
globalReplacementMap["STXS"]["procRVMap"]["RECO_TTH_HAD_PTH_0_60_Tag0"] = "TTH_PTH_0_60"
globalReplacementMap["STXS"]["procRVMap"]["RECO_TTH_HAD_PTH_0_60_Tag1"] = "TTH_PTH_0_60"
globalReplacementMap["STXS"]["procRVMap"]["RECO_TTH_HAD_PTH_0_60_Tag2"] = "TTH_PTH_0_60"
globalReplacementMap["STXS"]["procRVMap"]["RECO_TTH_HAD_PTH_0_60_Tag3"] = "TTH_PTH_0_60"
globalReplacementMap["STXS"]["procRVMap"]["RECO_TTH_HAD_PTH_120_200_Tag0"] = "TTH_PTH_120_200"
globalReplacementMap["STXS"]["procRVMap"]["RECO_TTH_HAD_PTH_120_200_Tag1"] = "TTH_PTH_120_200"
globalReplacementMap["STXS"]["procRVMap"]["RECO_TTH_HAD_PTH_120_200_Tag2"] = "TTH_PTH_120_200"
globalReplacementMap["STXS"]["procRVMap"]["RECO_TTH_HAD_PTH_120_200_Tag3"] = "TTH_PTH_120_200"
globalReplacementMap["STXS"]["procRVMap"]["RECO_TTH_HAD_PTH_200_300_Tag0"] = "TTH_PTH_200_300"
globalReplacementMap["STXS"]["procRVMap"]["RECO_TTH_HAD_PTH_200_300_Tag1"] = "TTH_PTH_200_300"
globalReplacementMap["STXS"]["procRVMap"]["RECO_TTH_HAD_PTH_200_300_Tag2"] = "TTH_PTH_200_300"
globalReplacementMap["STXS"]["procRVMap"]["RECO_TTH_HAD_PTH_60_120_Tag0"] = "TTH_PTH_60_120"
globalReplacementMap["STXS"]["procRVMap"]["RECO_TTH_HAD_PTH_60_120_Tag1"] = "TTH_PTH_60_120"
globalReplacementMap["STXS"]["procRVMap"]["RECO_TTH_HAD_PTH_60_120_Tag2"] = "TTH_PTH_60_120"
globalReplacementMap["STXS"]["procRVMap"]["RECO_TTH_HAD_PTH_60_120_Tag3"] = "TTH_PTH_60_120"
globalReplacementMap["STXS"]["procRVMap"]["RECO_TTH_HAD_PTH_GT300_Tag0"] = "TTH_PTH_GT300"
globalReplacementMap["STXS"]["procRVMap"]["RECO_TTH_HAD_PTH_GT300_Tag1"] = "TTH_PTH_GT300"
globalReplacementMap["STXS"]["procRVMap"]["RECO_TTH_HAD_PTH_GT300_Tag2"] = "TTH_PTH_GT300"
globalReplacementMap["STXS"]["procRVMap"]["RECO_TTH_LEP_PTH_0_60_Tag0"] = "TTH_PTH_0_60"
globalReplacementMap["STXS"]["procRVMap"]["RECO_TTH_LEP_PTH_0_60_Tag1"] = "TTH_PTH_0_60"
globalReplacementMap["STXS"]["procRVMap"]["RECO_TTH_LEP_PTH_0_60_Tag2"] = "TTH_PTH_0_60"
globalReplacementMap["STXS"]["procRVMap"]["RECO_TTH_LEP_PTH_120_200_Tag0"] = "TTH_PTH_120_200"
globalReplacementMap["STXS"]["procRVMap"]["RECO_TTH_LEP_PTH_120_200_Tag1"] = "TTH_PTH_120_200"
globalReplacementMap["STXS"]["procRVMap"]["RECO_TTH_LEP_PTH_200_300_Tag0"] = "TTH_PTH_200_300"
globalReplacementMap["STXS"]["procRVMap"]["RECO_TTH_LEP_PTH_200_300_Tag1"] = "TTH_PTH_200_300"
globalReplacementMap["STXS"]["procRVMap"]["RECO_TTH_LEP_PTH_60_120_Tag0"] = "TTH_PTH_60_120"
globalReplacementMap["STXS"]["procRVMap"]["RECO_TTH_LEP_PTH_60_120_Tag1"] = "TTH_PTH_60_120"
globalReplacementMap["STXS"]["procRVMap"]["RECO_TTH_LEP_PTH_60_120_Tag2"] = "TTH_PTH_60_120"
globalReplacementMap["STXS"]["procRVMap"]["RECO_TTH_LEP_PTH_GT300_Tag0"] = "TTH_PTH_GT300"
globalReplacementMap["STXS"]["procRVMap"]["RECO_VBFLIKEGGH_Tag0"] = "GG2H_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25"
globalReplacementMap["STXS"]["procRVMap"]["RECO_VBFLIKEGGH_Tag1"] = "GG2H_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25"
globalReplacementMap["STXS"]["procRVMap"]["RECO_VBFTOPO_BSM_Tag0"] = "VBF_GE2J_MJJ_GT350_PTH_GT200"
globalReplacementMap["STXS"]["procRVMap"]["RECO_VBFTOPO_BSM_Tag1"] = "VBF_GE2J_MJJ_GT350_PTH_GT200"
globalReplacementMap["STXS"]["procRVMap"]["RECO_VBFTOPO_JET3VETO_HIGHMJJ_Tag0"] = "VBF_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25"
globalReplacementMap["STXS"]["procRVMap"]["RECO_VBFTOPO_JET3VETO_HIGHMJJ_Tag1"] = "VBF_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25"
globalReplacementMap["STXS"]["procRVMap"]["RECO_VBFTOPO_JET3VETO_LOWMJJ_Tag0"] = "VBF_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25"
globalReplacementMap["STXS"]["procRVMap"]["RECO_VBFTOPO_JET3VETO_LOWMJJ_Tag1"] = "VBF_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25"
globalReplacementMap["STXS"]["procRVMap"]["RECO_VBFTOPO_JET3_HIGHMJJ_Tag0"] = "VBF_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25"
globalReplacementMap["STXS"]["procRVMap"]["RECO_VBFTOPO_JET3_HIGHMJJ_Tag1"] = "VBF_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25"
globalReplacementMap["STXS"]["procRVMap"]["RECO_VBFTOPO_JET3_LOWMJJ_Tag0"] = "GG2H_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25"
globalReplacementMap["STXS"]["procRVMap"]["RECO_VBFTOPO_JET3_LOWMJJ_Tag1"] = "GG2H_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25"
globalReplacementMap["STXS"]["procRVMap"]["RECO_VBFTOPO_VHHAD_Tag0"] = "WH2HQQ_GE2J_MJJ_60_120"
globalReplacementMap["STXS"]["procRVMap"]["RECO_VBFTOPO_VHHAD_Tag1"] = "GG2H_GE2J_MJJ_0_350_PTH_120_200"
globalReplacementMap["STXS"]["procRVMap"]["RECO_VH_MET_Tag0"] = "QQ2HLL_PTV_150_250_0J"
globalReplacementMap["STXS"]["procRVMap"]["RECO_VH_MET_Tag1"] = "QQ2HLL_PTV_75_150"
globalReplacementMap["STXS"]["procRVMap"]["RECO_VH_MET_Tag2"] = "QQ2HLL_PTV_75_150"
globalReplacementMap["STXS"]["procRVMap"]["RECO_WH_LEP_PTV_0_75_Tag0"] = "QQ2HLNU_PTV_0_75"
globalReplacementMap["STXS"]["procRVMap"]["RECO_WH_LEP_PTV_0_75_Tag1"] = "QQ2HLNU_PTV_0_75"
globalReplacementMap["STXS"]["procRVMap"]["RECO_WH_LEP_PTV_75_150_Tag0"] = "QQ2HLNU_PTV_75_150"
globalReplacementMap["STXS"]["procRVMap"]["RECO_WH_LEP_PTV_75_150_Tag1"] = "QQ2HLNU_PTV_75_150"
globalReplacementMap["STXS"]["procRVMap"]["RECO_WH_LEP_PTV_GT150_Tag0"] = "QQ2HLNU_PTV_150_250_0J"
globalReplacementMap["STXS"]["procRVMap"]["RECO_ZH_LEP_Tag0"] = "QQ2HLL_PTV_0_75"
globalReplacementMap["STXS"]["procRVMap"]["RECO_ZH_LEP_Tag1"] = "QQ2HLL_PTV_0_75"
# Replacement category for RV fit
globalReplacementMap["STXS"]["catRVMap"] = od()
globalReplacementMap["STXS"]["catRVMap"]["RECO_0J_PTH_0_10_Tag0"] = "RECO_0J_PTH_0_10_Tag0"
globalReplacementMap["STXS"]["catRVMap"]["RECO_0J_PTH_0_10_Tag1"] = "RECO_0J_PTH_0_10_Tag1"
globalReplacementMap["STXS"]["catRVMap"]["RECO_0J_PTH_0_10_Tag2"] = "RECO_0J_PTH_0_10_Tag2"
globalReplacementMap["STXS"]["catRVMap"]["RECO_0J_PTH_GT10_Tag0"] = "RECO_0J_PTH_GT10_Tag0"
globalReplacementMap["STXS"]["catRVMap"]["RECO_0J_PTH_GT10_Tag1"] = "RECO_0J_PTH_GT10_Tag1"
globalReplacementMap["STXS"]["catRVMap"]["RECO_0J_PTH_GT10_Tag2"] = "RECO_0J_PTH_GT10_Tag2"
globalReplacementMap["STXS"]["catRVMap"]["RECO_1J_PTH_0_60_Tag0"] = "RECO_1J_PTH_0_60_Tag0"
globalReplacementMap["STXS"]["catRVMap"]["RECO_1J_PTH_0_60_Tag1"] = "RECO_1J_PTH_0_60_Tag1"
globalReplacementMap["STXS"]["catRVMap"]["RECO_1J_PTH_0_60_Tag2"] = "RECO_1J_PTH_0_60_Tag2"
globalReplacementMap["STXS"]["catRVMap"]["RECO_1J_PTH_120_200_Tag0"] = "RECO_1J_PTH_120_200_Tag0"
globalReplacementMap["STXS"]["catRVMap"]["RECO_1J_PTH_120_200_Tag1"] = "RECO_1J_PTH_120_200_Tag1"
globalReplacementMap["STXS"]["catRVMap"]["RECO_1J_PTH_120_200_Tag2"] = "RECO_1J_PTH_120_200_Tag2"
globalReplacementMap["STXS"]["catRVMap"]["RECO_1J_PTH_60_120_Tag0"] = "RECO_1J_PTH_60_120_Tag0"
globalReplacementMap["STXS"]["catRVMap"]["RECO_1J_PTH_60_120_Tag1"] = "RECO_1J_PTH_60_120_Tag1"
globalReplacementMap["STXS"]["catRVMap"]["RECO_1J_PTH_60_120_Tag2"] = "RECO_1J_PTH_60_120_Tag2"
globalReplacementMap["STXS"]["catRVMap"]["RECO_GE2J_PTH_0_60_Tag0"] = "RECO_GE2J_PTH_0_60_Tag0"
globalReplacementMap["STXS"]["catRVMap"]["RECO_GE2J_PTH_0_60_Tag1"] = "RECO_GE2J_PTH_0_60_Tag1"
globalReplacementMap["STXS"]["catRVMap"]["RECO_GE2J_PTH_0_60_Tag2"] = "RECO_GE2J_PTH_0_60_Tag2"
globalReplacementMap["STXS"]["catRVMap"]["RECO_GE2J_PTH_120_200_Tag0"] = "RECO_GE2J_PTH_120_200_Tag0"
globalReplacementMap["STXS"]["catRVMap"]["RECO_GE2J_PTH_120_200_Tag1"] = "RECO_GE2J_PTH_120_200_Tag1"
globalReplacementMap["STXS"]["catRVMap"]["RECO_GE2J_PTH_120_200_Tag2"] = "RECO_GE2J_PTH_120_200_Tag2"
globalReplacementMap["STXS"]["catRVMap"]["RECO_GE2J_PTH_60_120_Tag0"] = "RECO_GE2J_PTH_60_120_Tag0"
globalReplacementMap["STXS"]["catRVMap"]["RECO_GE2J_PTH_60_120_Tag1"] = "RECO_GE2J_PTH_60_120_Tag1"
globalReplacementMap["STXS"]["catRVMap"]["RECO_GE2J_PTH_60_120_Tag2"] = "RECO_GE2J_PTH_60_120_Tag2"
globalReplacementMap["STXS"]["catRVMap"]["RECO_PTH_200_300_Tag0"] = "RECO_PTH_200_300_Tag0"
globalReplacementMap["STXS"]["catRVMap"]["RECO_PTH_200_300_Tag1"] = "RECO_PTH_200_300_Tag1"
globalReplacementMap["STXS"]["catRVMap"]["RECO_PTH_300_450_Tag0"] = "RECO_PTH_300_450_Tag0"
globalReplacementMap["STXS"]["catRVMap"]["RECO_PTH_300_450_Tag1"] = "RECO_PTH_300_450_Tag1"
globalReplacementMap["STXS"]["catRVMap"]["RECO_PTH_450_650_Tag0"] = "RECO_PTH_450_650_Tag0"
globalReplacementMap["STXS"]["catRVMap"]["RECO_PTH_GT650_Tag0"] = "RECO_PTH_GT650_Tag0"
globalReplacementMap["STXS"]["catRVMap"]["RECO_THQ_LEP"] = "RECO_THQ_LEP"
globalReplacementMap["STXS"]["catRVMap"]["RECO_TTH_HAD_PTH_0_60_Tag0"] = "RECO_TTH_HAD_PTH_0_60_Tag0"
globalReplacementMap["STXS"]["catRVMap"]["RECO_TTH_HAD_PTH_0_60_Tag1"] = "RECO_TTH_HAD_PTH_0_60_Tag1"
globalReplacementMap["STXS"]["catRVMap"]["RECO_TTH_HAD_PTH_0_60_Tag2"] = "RECO_TTH_HAD_PTH_0_60_Tag2"
globalReplacementMap["STXS"]["catRVMap"]["RECO_TTH_HAD_PTH_0_60_Tag3"] = "RECO_TTH_HAD_PTH_0_60_Tag3"
globalReplacementMap["STXS"]["catRVMap"]["RECO_TTH_HAD_PTH_120_200_Tag0"] = "RECO_TTH_HAD_PTH_120_200_Tag0"
globalReplacementMap["STXS"]["catRVMap"]["RECO_TTH_HAD_PTH_120_200_Tag1"] = "RECO_TTH_HAD_PTH_120_200_Tag1"
globalReplacementMap["STXS"]["catRVMap"]["RECO_TTH_HAD_PTH_120_200_Tag2"] = "RECO_TTH_HAD_PTH_120_200_Tag2"
globalReplacementMap["STXS"]["catRVMap"]["RECO_TTH_HAD_PTH_120_200_Tag3"] = "RECO_TTH_HAD_PTH_120_200_Tag3"
globalReplacementMap["STXS"]["catRVMap"]["RECO_TTH_HAD_PTH_200_300_Tag0"] = "RECO_TTH_HAD_PTH_200_300_Tag0"
globalReplacementMap["STXS"]["catRVMap"]["RECO_TTH_HAD_PTH_200_300_Tag1"] = "RECO_TTH_HAD_PTH_200_300_Tag1"
globalReplacementMap["STXS"]["catRVMap"]["RECO_TTH_HAD_PTH_200_300_Tag2"] = "RECO_TTH_HAD_PTH_200_300_Tag2"
globalReplacementMap["STXS"]["catRVMap"]["RECO_TTH_HAD_PTH_60_120_Tag0"] = "RECO_TTH_HAD_PTH_60_120_Tag0"
globalReplacementMap["STXS"]["catRVMap"]["RECO_TTH_HAD_PTH_60_120_Tag1"] = "RECO_TTH_HAD_PTH_60_120_Tag1"
globalReplacementMap["STXS"]["catRVMap"]["RECO_TTH_HAD_PTH_60_120_Tag2"] = "RECO_TTH_HAD_PTH_60_120_Tag2"
globalReplacementMap["STXS"]["catRVMap"]["RECO_TTH_HAD_PTH_60_120_Tag3"] = "RECO_TTH_HAD_PTH_60_120_Tag3"
globalReplacementMap["STXS"]["catRVMap"]["RECO_TTH_HAD_PTH_GT300_Tag0"] = "RECO_TTH_HAD_PTH_GT300_Tag0"
globalReplacementMap["STXS"]["catRVMap"]["RECO_TTH_HAD_PTH_GT300_Tag1"] = "RECO_TTH_HAD_PTH_GT300_Tag1"
globalReplacementMap["STXS"]["catRVMap"]["RECO_TTH_HAD_PTH_GT300_Tag2"] = "RECO_TTH_HAD_PTH_GT300_Tag2"
globalReplacementMap["STXS"]["catRVMap"]["RECO_TTH_LEP_PTH_0_60_Tag0"] = "RECO_TTH_LEP_PTH_0_60_Tag0"
globalReplacementMap["STXS"]["catRVMap"]["RECO_TTH_LEP_PTH_0_60_Tag1"] = "RECO_TTH_LEP_PTH_0_60_Tag1"
globalReplacementMap["STXS"]["catRVMap"]["RECO_TTH_LEP_PTH_0_60_Tag2"] = "RECO_TTH_LEP_PTH_0_60_Tag2"
globalReplacementMap["STXS"]["catRVMap"]["RECO_TTH_LEP_PTH_120_200_Tag0"] = "RECO_TTH_LEP_PTH_120_200_Tag0"
globalReplacementMap["STXS"]["catRVMap"]["RECO_TTH_LEP_PTH_120_200_Tag1"] = "RECO_TTH_LEP_PTH_120_200_Tag1"
globalReplacementMap["STXS"]["catRVMap"]["RECO_TTH_LEP_PTH_200_300_Tag0"] = "RECO_TTH_LEP_PTH_200_300_Tag0"
globalReplacementMap["STXS"]["catRVMap"]["RECO_TTH_LEP_PTH_200_300_Tag1"] = "RECO_TTH_LEP_PTH_200_300_Tag1"
globalReplacementMap["STXS"]["catRVMap"]["RECO_TTH_LEP_PTH_60_120_Tag0"] = "RECO_TTH_LEP_PTH_60_120_Tag0"
globalReplacementMap["STXS"]["catRVMap"]["RECO_TTH_LEP_PTH_60_120_Tag1"] = "RECO_TTH_LEP_PTH_60_120_Tag1"
globalReplacementMap["STXS"]["catRVMap"]["RECO_TTH_LEP_PTH_60_120_Tag2"] = "RECO_TTH_LEP_PTH_60_120_Tag2"
globalReplacementMap["STXS"]["catRVMap"]["RECO_TTH_LEP_PTH_GT300_Tag0"] = "RECO_TTH_LEP_PTH_GT300_Tag0"
globalReplacementMap["STXS"]["catRVMap"]["RECO_VBFLIKEGGH_Tag0"] = "RECO_VBFLIKEGGH_Tag0"
globalReplacementMap["STXS"]["catRVMap"]["RECO_VBFLIKEGGH_Tag1"] = "RECO_VBFLIKEGGH_Tag1"
globalReplacementMap["STXS"]["catRVMap"]["RECO_VBFTOPO_BSM_Tag0"] = "RECO_VBFTOPO_BSM_Tag0"
globalReplacementMap["STXS"]["catRVMap"]["RECO_VBFTOPO_BSM_Tag1"] = "RECO_VBFTOPO_BSM_Tag1"
globalReplacementMap["STXS"]["catRVMap"]["RECO_VBFTOPO_JET3VETO_HIGHMJJ_Tag0"] = "RECO_VBFTOPO_JET3VETO_HIGHMJJ_Tag0"
globalReplacementMap["STXS"]["catRVMap"]["RECO_VBFTOPO_JET3VETO_HIGHMJJ_Tag1"] = "RECO_VBFTOPO_JET3VETO_HIGHMJJ_Tag1"
globalReplacementMap["STXS"]["catRVMap"]["RECO_VBFTOPO_JET3VETO_LOWMJJ_Tag0"] = "RECO_VBFTOPO_JET3VETO_LOWMJJ_Tag0"
globalReplacementMap["STXS"]["catRVMap"]["RECO_VBFTOPO_JET3VETO_LOWMJJ_Tag1"] = "RECO_VBFTOPO_JET3VETO_LOWMJJ_Tag1"
globalReplacementMap["STXS"]["catRVMap"]["RECO_VBFTOPO_JET3_HIGHMJJ_Tag0"] = "RECO_VBFTOPO_JET3_HIGHMJJ_Tag0"
globalReplacementMap["STXS"]["catRVMap"]["RECO_VBFTOPO_JET3_HIGHMJJ_Tag1"] = "RECO_VBFTOPO_JET3_HIGHMJJ_Tag1"
globalReplacementMap["STXS"]["catRVMap"]["RECO_VBFTOPO_JET3_LOWMJJ_Tag0"] = "RECO_VBFTOPO_JET3_LOWMJJ_Tag0"
globalReplacementMap["STXS"]["catRVMap"]["RECO_VBFTOPO_JET3_LOWMJJ_Tag1"] = "RECO_VBFTOPO_JET3_LOWMJJ_Tag1"
globalReplacementMap["STXS"]["catRVMap"]["RECO_VBFTOPO_VHHAD_Tag0"] = "RECO_VBFTOPO_VHHAD_Tag0"
globalReplacementMap["STXS"]["catRVMap"]["RECO_VBFTOPO_VHHAD_Tag1"] = "RECO_VBFTOPO_VHHAD_Tag1"
globalReplacementMap["STXS"]["catRVMap"]["RECO_VH_MET_Tag0"] = "RECO_VH_MET_Tag0"
globalReplacementMap["STXS"]["catRVMap"]["RECO_VH_MET_Tag1"] = "RECO_VH_MET_Tag1"
globalReplacementMap["STXS"]["catRVMap"]["RECO_VH_MET_Tag2"] = "RECO_VH_MET_Tag2"
globalReplacementMap["STXS"]["catRVMap"]["RECO_WH_LEP_PTV_0_75_Tag0"] = "RECO_WH_LEP_PTV_0_75_Tag0"
globalReplacementMap["STXS"]["catRVMap"]["RECO_WH_LEP_PTV_0_75_Tag1"] = "RECO_WH_LEP_PTV_0_75_Tag1"
globalReplacementMap["STXS"]["catRVMap"]["RECO_WH_LEP_PTV_75_150_Tag0"] = "RECO_WH_LEP_PTV_75_150_Tag0"
globalReplacementMap["STXS"]["catRVMap"]["RECO_WH_LEP_PTV_75_150_Tag1"] = "RECO_WH_LEP_PTV_75_150_Tag1"
globalReplacementMap["STXS"]["catRVMap"]["RECO_WH_LEP_PTV_GT150_Tag0"] = "RECO_WH_LEP_PTV_GT150_Tag0"
globalReplacementMap["STXS"]["catRVMap"]["RECO_ZH_LEP_Tag0"] = "RECO_ZH_LEP_Tag0"
globalReplacementMap["STXS"]["catRVMap"]["RECO_ZH_LEP_Tag1"] = "RECO_ZH_LEP_Tag1"

###################################################################################################################################################################################################
###################################################################################################################################################################################################
###################################################################################################################################################################################################
# Run 3 Fiducial XS analysis: use 13.6 TeV cross sections and branching fraction

globalReplacementMap["Run3FidXSAnalysis"] = od()
# Wrong vertex stuff
globalReplacementMap["Run3FidXSAnalysis"]['procWV'] = "GG2H"
globalReplacementMap["Run3FidXSAnalysis"]['catWV'] = "cat2"
# Relacement processes for RV
globalReplacementMap["Run3FidXSAnalysis"]['procRVMap'] = od()
globalReplacementMap["Run3FidXSAnalysis"]["procRVMap"]["cat0"] = "GG2H"
globalReplacementMap["Run3FidXSAnalysis"]["procRVMap"]["cat0"] = "VBF"
globalReplacementMap["Run3FidXSAnalysis"]["procRVMap"]["cat0"] = "VH"
globalReplacementMap["Run3FidXSAnalysis"]["procRVMap"]["cat0"] = "TTH"
# Replacement categories for RV
globalReplacementMap["Run3FidXSAnalysis"]["catRVMap"] = od()
globalReplacementMap["Run3FidXSAnalysis"]["catRVMap"]["GG2H"] = "GG2H"
globalReplacementMap["Run3FidXSAnalysis"]["catRVMap"]["VBF"]  = "VBF"
globalReplacementMap["Run3FidXSAnalysis"]["catRVMap"]["VH"]   = "VH"
globalReplacementMap["Run3FidXSAnalysis"]["catRVMap"]["TTH"]  = "TTH"


# WITH in/out splitting
globalReplacementMap["Run3FidXSAnalysisInclusive"] = od()
# Wrong vertex stuff
globalReplacementMap["Run3FidXSAnalysisInclusive"]['procWV'] = "ggh_in"
globalReplacementMap["Run3FidXSAnalysisInclusive"]['catWV'] = "cat2"
# Relacement processes for RV
globalReplacementMap["Run3FidXSAnalysisInclusive"]['procRVMap'] = od()
# With nico convention (ggh instead of GG2H)
globalReplacementMap["Run3FidXSAnalysisInclusive"]["procRVMap"]["cat0"] = "ggh_in"
globalReplacementMap["Run3FidXSAnalysisInclusive"]["procRVMap"]["cat1"] = "ggh_in"
globalReplacementMap["Run3FidXSAnalysisInclusive"]["procRVMap"]["cat2"] = "ggh_in"
# Replacement categories for RV
globalReplacementMap["Run3FidXSAnalysisInclusive"]["catRVMap"] = od()
globalReplacementMap["Run3FidXSAnalysisInclusive"]["catRVMap"]["cat0"] = "cat0"
globalReplacementMap["Run3FidXSAnalysisInclusive"]["catRVMap"]["cat1"]  = "cat1"
globalReplacementMap["Run3FidXSAnalysisInclusive"]["catRVMap"]["cat2"]   = "cat2"


# Differential PT
globalReplacementMap["Run3FidXSAnalysisPTH"] = od()
# Wrong vertex stuff, which process should be considered?
globalReplacementMap["Run3FidXSAnalysisPTH"]['procWV'] = "ggh_PTH_45p0_80p0_in"
globalReplacementMap["Run3FidXSAnalysisPTH"]['catWV'] = "RECO_PTH_45p0_80p0_cat2"
# Relacement processes for RV
globalReplacementMap["Run3FidXSAnalysisPTH"]['procRVMap'] = od()
globalReplacementMap["Run3FidXSAnalysisPTH"]["procRVMap"]["RECO_PTH_0p0_15p0_cat0"] = "ggh_PTH_0p0_15p0_in"
globalReplacementMap["Run3FidXSAnalysisPTH"]["procRVMap"]["RECO_PTH_0p0_15p0_cat1"] = "ggh_PTH_0p0_15p0_in"
globalReplacementMap["Run3FidXSAnalysisPTH"]["procRVMap"]["RECO_PTH_0p0_15p0_cat2"] = "ggh_PTH_0p0_15p0_in"
globalReplacementMap["Run3FidXSAnalysisPTH"]["procRVMap"]["RECO_PTH_15p0_30p0_cat0"] = "ggh_PTH_15p0_30p0_in"
globalReplacementMap["Run3FidXSAnalysisPTH"]["procRVMap"]["RECO_PTH_15p0_30p0_cat1"] = "ggh_PTH_15p0_30p0_in"
globalReplacementMap["Run3FidXSAnalysisPTH"]["procRVMap"]["RECO_PTH_15p0_30p0_cat2"] = "ggh_PTH_15p0_30p0_in"
globalReplacementMap["Run3FidXSAnalysisPTH"]["procRVMap"]["RECO_PTH_30p0_45p0_cat0"] = "ggh_PTH_30p0_45p0_in"
globalReplacementMap["Run3FidXSAnalysisPTH"]["procRVMap"]["RECO_PTH_30p0_45p0_cat1"] = "ggh_PTH_30p0_45p0_in"
globalReplacementMap["Run3FidXSAnalysisPTH"]["procRVMap"]["RECO_PTH_30p0_45p0_cat2"] = "ggh_PTH_30p0_45p0_in"
globalReplacementMap["Run3FidXSAnalysisPTH"]["procRVMap"]["RECO_PTH_45p0_80p0_cat0"] = "ggh_PTH_45p0_80p0_in"
globalReplacementMap["Run3FidXSAnalysisPTH"]["procRVMap"]["RECO_PTH_45p0_80p0_cat1"] = "ggh_PTH_45p0_80p0_in"
globalReplacementMap["Run3FidXSAnalysisPTH"]["procRVMap"]["RECO_PTH_45p0_80p0_cat2"] = "ggh_PTH_45p0_80p0_in"
globalReplacementMap["Run3FidXSAnalysisPTH"]["procRVMap"]["RECO_PTH_80p0_120p0_cat0"] = "ggh_PTH_80p0_120p0_in"
globalReplacementMap["Run3FidXSAnalysisPTH"]["procRVMap"]["RECO_PTH_80p0_120p0_cat1"] = "ggh_PTH_80p0_120p0_in"
globalReplacementMap["Run3FidXSAnalysisPTH"]["procRVMap"]["RECO_PTH_80p0_120p0_cat2"] = "ggh_PTH_80p0_120p0_in"
globalReplacementMap["Run3FidXSAnalysisPTH"]["procRVMap"]["RECO_PTH_120p0_200p0_cat0"] = "ggh_PTH_120p0_200p0_in"
globalReplacementMap["Run3FidXSAnalysisPTH"]["procRVMap"]["RECO_PTH_120p0_200p0_cat1"] = "ggh_PTH_120p0_200p0_in"
globalReplacementMap["Run3FidXSAnalysisPTH"]["procRVMap"]["RECO_PTH_120p0_200p0_cat2"] = "ggh_PTH_120p0_200p0_in"
globalReplacementMap["Run3FidXSAnalysisPTH"]["procRVMap"]["RECO_PTH_200p0_350p0_cat0"] = "ggh_PTH_200p0_350p0_in"
globalReplacementMap["Run3FidXSAnalysisPTH"]["procRVMap"]["RECO_PTH_200p0_350p0_cat1"] = "ggh_PTH_200p0_350p0_in"
globalReplacementMap["Run3FidXSAnalysisPTH"]["procRVMap"]["RECO_PTH_200p0_350p0_cat2"] = "ggh_PTH_200p0_350p0_in"
globalReplacementMap["Run3FidXSAnalysisPTH"]["procRVMap"]["RECO_PTH_350p0_10000p0_cat0"] = "ggh_PTH_350p0_10000p0_in"
globalReplacementMap["Run3FidXSAnalysisPTH"]["procRVMap"]["RECO_PTH_350p0_10000p0_cat1"] = "ggh_PTH_350p0_10000p0_in"
globalReplacementMap["Run3FidXSAnalysisPTH"]["procRVMap"]["RECO_PTH_350p0_10000p0_cat2"] = "ggh_PTH_350p0_10000p0_in"

# Replacement categories for RV
globalReplacementMap["Run3FidXSAnalysisPTH"]["catRVMap"] = od()
globalReplacementMap["Run3FidXSAnalysisPTH"]["catRVMap"]["RECO_PTH_0p0_15p0_cat0"] = "RECO_PTH_0p0_15p0_cat0"
globalReplacementMap["Run3FidXSAnalysisPTH"]["catRVMap"]["RECO_PTH_0p0_15p0_cat1"] = "RECO_PTH_0p0_15p0_cat1"
globalReplacementMap["Run3FidXSAnalysisPTH"]["catRVMap"]["RECO_PTH_0p0_15p0_cat2"] = "RECO_PTH_0p0_15p0_cat2"
globalReplacementMap["Run3FidXSAnalysisPTH"]["catRVMap"]["RECO_PTH_15p0_30p0_cat0"] = "RECO_PTH_15p0_30p0_cat0"
globalReplacementMap["Run3FidXSAnalysisPTH"]["catRVMap"]["RECO_PTH_15p0_30p0_cat1"] = "RECO_PTH_15p0_30p0_cat1"
globalReplacementMap["Run3FidXSAnalysisPTH"]["catRVMap"]["RECO_PTH_15p0_30p0_cat2"] = "RECO_PTH_15p0_30p0_cat2"
globalReplacementMap["Run3FidXSAnalysisPTH"]["catRVMap"]["RECO_PTH_30p0_45p0_cat0"] = "RECO_PTH_30p0_45p0_cat0"
globalReplacementMap["Run3FidXSAnalysisPTH"]["catRVMap"]["RECO_PTH_30p0_45p0_cat1"] = "RECO_PTH_30p0_45p0_cat1"
globalReplacementMap["Run3FidXSAnalysisPTH"]["catRVMap"]["RECO_PTH_30p0_45p0_cat2"] = "RECO_PTH_30p0_45p0_cat2"
globalReplacementMap["Run3FidXSAnalysisPTH"]["catRVMap"]["RECO_PTH_45p0_80p0_cat0"] = "RECO_PTH_45p0_80p0_cat0"
globalReplacementMap["Run3FidXSAnalysisPTH"]["catRVMap"]["RECO_PTH_45p0_80p0_cat1"] = "RECO_PTH_45p0_80p0_cat1"
globalReplacementMap["Run3FidXSAnalysisPTH"]["catRVMap"]["RECO_PTH_45p0_80p0_cat2"] = "RECO_PTH_45p0_80p0_cat2"
globalReplacementMap["Run3FidXSAnalysisPTH"]["catRVMap"]["RECO_PTH_80p0_120p0_cat0"] = "RECO_PTH_80p0_120p0_cat0"
globalReplacementMap["Run3FidXSAnalysisPTH"]["catRVMap"]["RECO_PTH_80p0_120p0_cat1"] = "RECO_PTH_80p0_120p0_cat1"
globalReplacementMap["Run3FidXSAnalysisPTH"]["catRVMap"]["RECO_PTH_80p0_120p0_cat2"] = "RECO_PTH_80p0_120p0_cat2"
globalReplacementMap["Run3FidXSAnalysisPTH"]["catRVMap"]["RECO_PTH_120p0_200p0_cat0"] = "RECO_PTH_120p0_200p0_cat0"
globalReplacementMap["Run3FidXSAnalysisPTH"]["catRVMap"]["RECO_PTH_120p0_200p0_cat1"] = "RECO_PTH_120p0_200p0_cat1"
globalReplacementMap["Run3FidXSAnalysisPTH"]["catRVMap"]["RECO_PTH_120p0_200p0_cat2"] = "RECO_PTH_120p0_200p0_cat2"
globalReplacementMap["Run3FidXSAnalysisPTH"]["catRVMap"]["RECO_PTH_200p0_350p0_cat0"] = "RECO_PTH_200p0_350p0_cat0"
globalReplacementMap["Run3FidXSAnalysisPTH"]["catRVMap"]["RECO_PTH_200p0_350p0_cat1"] = "RECO_PTH_200p0_350p0_cat1"
globalReplacementMap["Run3FidXSAnalysisPTH"]["catRVMap"]["RECO_PTH_200p0_350p0_cat2"] = "RECO_PTH_200p0_350p0_cat2"
globalReplacementMap["Run3FidXSAnalysisPTH"]["catRVMap"]["RECO_PTH_350p0_10000p0_cat0"] = "RECO_PTH_350p0_10000p0_cat0"
globalReplacementMap["Run3FidXSAnalysisPTH"]["catRVMap"]["RECO_PTH_350p0_10000p0_cat1"] = "RECO_PTH_350p0_10000p0_cat1"
globalReplacementMap["Run3FidXSAnalysisPTH"]["catRVMap"]["RECO_PTH_350p0_10000p0_cat2"] = "RECO_PTH_350p0_10000p0_cat2"


# Differential Y (Rapidity)
globalReplacementMap["Run3FidXSAnalysisYH"] = od()
# Wrong vertex stuff, which process should be considered?
globalReplacementMap["Run3FidXSAnalysisYH"]['procWV'] = "ggh_YH_0p3_0p6_in"
globalReplacementMap["Run3FidXSAnalysisYH"]['catWV'] = "RECO_rapidity_0p3_0p6_cat2"
# Relacement processes for RV
globalReplacementMap["Run3FidXSAnalysisYH"]['procRVMap'] = od()
globalReplacementMap["Run3FidXSAnalysisYH"]["procRVMap"]["RECO_rapidity_0p0_0p15_cat0"] = "ggh_YH_0p0_0p15_in"
globalReplacementMap["Run3FidXSAnalysisYH"]["procRVMap"]["RECO_rapidity_0p0_0p15_cat1"] = "ggh_YH_0p0_0p15_in"
globalReplacementMap["Run3FidXSAnalysisYH"]["procRVMap"]["RECO_rapidity_0p0_0p15_cat2"] = "ggh_YH_0p0_0p15_in"
globalReplacementMap["Run3FidXSAnalysisYH"]["procRVMap"]["RECO_rapidity_0p15_0p3_cat0"] = "ggh_YH_0p15_0p3_in"
globalReplacementMap["Run3FidXSAnalysisYH"]["procRVMap"]["RECO_rapidity_0p15_0p3_cat1"] = "ggh_YH_0p15_0p3_in"
globalReplacementMap["Run3FidXSAnalysisYH"]["procRVMap"]["RECO_rapidity_0p15_0p3_cat2"] = "ggh_YH_0p15_0p3_in"
globalReplacementMap["Run3FidXSAnalysisYH"]["procRVMap"]["RECO_rapidity_0p3_0p6_cat0"] = "ggh_YH_0p3_0p6_in"
globalReplacementMap["Run3FidXSAnalysisYH"]["procRVMap"]["RECO_rapidity_0p3_0p6_cat1"] = "ggh_YH_0p3_0p6_in"
globalReplacementMap["Run3FidXSAnalysisYH"]["procRVMap"]["RECO_rapidity_0p3_0p6_cat2"] = "ggh_YH_0p3_0p6_in"
globalReplacementMap["Run3FidXSAnalysisYH"]["procRVMap"]["RECO_rapidity_0p6_0p9_cat0"] = "ggh_YH_0p6_0p9_in"
globalReplacementMap["Run3FidXSAnalysisYH"]["procRVMap"]["RECO_rapidity_0p6_0p9_cat1"] = "ggh_YH_0p6_0p9_in"
globalReplacementMap["Run3FidXSAnalysisYH"]["procRVMap"]["RECO_rapidity_0p6_0p9_cat2"] = "ggh_YH_0p6_0p9_in"
globalReplacementMap["Run3FidXSAnalysisYH"]["procRVMap"]["RECO_rapidity_0p9_2p5_cat0"] = "ggh_YH_0p9_2p5_in"
globalReplacementMap["Run3FidXSAnalysisYH"]["procRVMap"]["RECO_rapidity_0p9_2p5_cat1"] = "ggh_YH_0p9_2p5_in"
globalReplacementMap["Run3FidXSAnalysisYH"]["procRVMap"]["RECO_rapidity_0p9_2p5_cat2"] = "ggh_YH_0p9_2p5_in"


# Replacement categories for RV
globalReplacementMap["Run3FidXSAnalysisYH"]["catRVMap"] = od()
globalReplacementMap["Run3FidXSAnalysisYH"]["catRVMap"]["RECO_rapidity_0p0_0p15_cat0"] = "RECO_rapidity_0p0_0p15_cat0"
globalReplacementMap["Run3FidXSAnalysisYH"]["catRVMap"]["RECO_rapidity_0p0_0p15_cat1"] = "RECO_rapidity_0p0_0p15_cat1"
globalReplacementMap["Run3FidXSAnalysisYH"]["catRVMap"]["RECO_rapidity_0p0_0p15_cat2"] = "RECO_rapidity_0p0_0p15_cat2"
globalReplacementMap["Run3FidXSAnalysisYH"]["catRVMap"]["RECO_rapidity_0p15_0p3_cat0"] = "RECO_rapidity_0p15_0p3_cat0"
globalReplacementMap["Run3FidXSAnalysisYH"]["catRVMap"]["RECO_rapidity_0p15_0p3_cat1"] = "RECO_rapidity_0p15_0p3_cat1"
globalReplacementMap["Run3FidXSAnalysisYH"]["catRVMap"]["RECO_rapidity_0p15_0p3_cat2"] = "RECO_rapidity_0p15_0p3_cat2"
globalReplacementMap["Run3FidXSAnalysisYH"]["catRVMap"]["RECO_rapidity_0p3_0p6_cat0"] = "RECO_rapidity_0p3_0p6_cat0"
globalReplacementMap["Run3FidXSAnalysisYH"]["catRVMap"]["RECO_rapidity_0p3_0p6_cat1"] = "RECO_rapidity_0p3_0p6_cat1"
globalReplacementMap["Run3FidXSAnalysisYH"]["catRVMap"]["RECO_rapidity_0p3_0p6_cat2"] = "RECO_rapidity_0p3_0p6_cat2"
globalReplacementMap["Run3FidXSAnalysisYH"]["catRVMap"]["RECO_rapidity_0p6_0p9_cat0"] = "RECO_rapidity_0p6_0p9_cat0"
globalReplacementMap["Run3FidXSAnalysisYH"]["catRVMap"]["RECO_rapidity_0p6_0p9_cat1"] = "RECO_rapidity_0p6_0p9_cat1"
globalReplacementMap["Run3FidXSAnalysisYH"]["catRVMap"]["RECO_rapidity_0p6_0p9_cat2"] = "RECO_rapidity_0p6_0p9_cat2"
globalReplacementMap["Run3FidXSAnalysisYH"]["catRVMap"]["RECO_rapidity_0p9_2p5_cat0"] = "RECO_rapidity_0p9_2p5_cat0"
globalReplacementMap["Run3FidXSAnalysisYH"]["catRVMap"]["RECO_rapidity_0p9_2p5_cat1"] = "RECO_rapidity_0p9_2p5_cat1"
globalReplacementMap["Run3FidXSAnalysisYH"]["catRVMap"]["RECO_rapidity_0p9_2p5_cat2"] = "RECO_rapidity_0p9_2p5_cat2"


# Differential NJ (Number of Jets)
globalReplacementMap["Run3FidXSAnalysisNJ"] = od()
# Wrong vertex stuff, which process should be considered?
globalReplacementMap["Run3FidXSAnalysisNJ"]['procWV'] = "ggh_NJ_1p0_2p0_in"
globalReplacementMap["Run3FidXSAnalysisNJ"]['catWV'] = "RECO_NJ_2p0_3p0_cat2"
# Relacement processes for RV
globalReplacementMap["Run3FidXSAnalysisNJ"]['procRVMap'] = od()
globalReplacementMap["Run3FidXSAnalysisNJ"]["procRVMap"]["RECO_NJ_0p0_1p0_cat0"] = "ggh_NJ_0p0_1p0_in"
globalReplacementMap["Run3FidXSAnalysisNJ"]["procRVMap"]["RECO_NJ_0p0_1p0_cat1"] = "ggh_NJ_0p0_1p0_in"
globalReplacementMap["Run3FidXSAnalysisNJ"]["procRVMap"]["RECO_NJ_0p0_1p0_cat2"] = "ggh_NJ_0p0_1p0_in"
globalReplacementMap["Run3FidXSAnalysisNJ"]["procRVMap"]["RECO_NJ_1p0_2p0_cat0"] = "ggh_NJ_1p0_2p0_in"
globalReplacementMap["Run3FidXSAnalysisNJ"]["procRVMap"]["RECO_NJ_1p0_2p0_cat1"] = "ggh_NJ_1p0_2p0_in"
globalReplacementMap["Run3FidXSAnalysisNJ"]["procRVMap"]["RECO_NJ_1p0_2p0_cat2"] = "ggh_NJ_1p0_2p0_in"
globalReplacementMap["Run3FidXSAnalysisNJ"]["procRVMap"]["RECO_NJ_2p0_3p0_cat0"] = "ggh_NJ_2p0_3p0_in"
globalReplacementMap["Run3FidXSAnalysisNJ"]["procRVMap"]["RECO_NJ_2p0_3p0_cat1"] = "ggh_NJ_2p0_3p0_in"
globalReplacementMap["Run3FidXSAnalysisNJ"]["procRVMap"]["RECO_NJ_2p0_3p0_cat2"] = "ggh_NJ_2p0_3p0_in"
globalReplacementMap["Run3FidXSAnalysisNJ"]["procRVMap"]["RECO_NJ_3p0_100p0_cat0"] = "ggh_NJ_3p0_100p0_in"
globalReplacementMap["Run3FidXSAnalysisNJ"]["procRVMap"]["RECO_NJ_3p0_100p0_cat1"] = "ggh_NJ_3p0_100p0_in"
globalReplacementMap["Run3FidXSAnalysisNJ"]["procRVMap"]["RECO_NJ_3p0_100p0_cat2"] = "ggh_NJ_3p0_100p0_in"


# Replacement categories for RV
globalReplacementMap["Run3FidXSAnalysisNJ"]["catRVMap"] = od()
globalReplacementMap["Run3FidXSAnalysisNJ"]["catRVMap"]["RECO_NJ_0p0_1p0_cat0"] = "RECO_NJ_0p0_1p0_cat0"
globalReplacementMap["Run3FidXSAnalysisNJ"]["catRVMap"]["RECO_NJ_0p0_1p0_cat1"] = "RECO_NJ_0p0_1p0_cat1"
globalReplacementMap["Run3FidXSAnalysisNJ"]["catRVMap"]["RECO_NJ_0p0_1p0_cat2"] = "RECO_NJ_0p0_1p0_cat2"
globalReplacementMap["Run3FidXSAnalysisNJ"]["catRVMap"]["RECO_NJ_1p0_2p0_cat0"] = "RECO_NJ_1p0_2p0_cat0"
globalReplacementMap["Run3FidXSAnalysisNJ"]["catRVMap"]["RECO_NJ_1p0_2p0_cat1"] = "RECO_NJ_1p0_2p0_cat1"
globalReplacementMap["Run3FidXSAnalysisNJ"]["catRVMap"]["RECO_NJ_1p0_2p0_cat2"] = "RECO_NJ_1p0_2p0_cat2"
globalReplacementMap["Run3FidXSAnalysisNJ"]["catRVMap"]["RECO_NJ_2p0_3p0_cat0"] = "RECO_NJ_2p0_3p0_cat0"
globalReplacementMap["Run3FidXSAnalysisNJ"]["catRVMap"]["RECO_NJ_2p0_3p0_cat1"] = "RECO_NJ_2p0_3p0_cat1"
globalReplacementMap["Run3FidXSAnalysisNJ"]["catRVMap"]["RECO_NJ_2p0_3p0_cat2"] = "RECO_NJ_2p0_3p0_cat2"
globalReplacementMap["Run3FidXSAnalysisNJ"]["catRVMap"]["RECO_NJ_3p0_100p0_cat0"] = "RECO_NJ_3p0_100p0_cat0"
globalReplacementMap["Run3FidXSAnalysisNJ"]["catRVMap"]["RECO_NJ_3p0_100p0_cat1"] = "RECO_NJ_3p0_100p0_cat1"
globalReplacementMap["Run3FidXSAnalysisNJ"]["catRVMap"]["RECO_NJ_3p0_100p0_cat2"] = "RECO_NJ_3p0_100p0_cat2"

# Differential PTJ0 (PT of the leading jet)
globalReplacementMap["Run3FidXSAnalysisPTJ0"] = od()
# Wrong vertex stuff, which process should be considered?
globalReplacementMap["Run3FidXSAnalysisPTJ0"]['procWV'] = "ggh_PTJ0_30p0_75p0_in"
globalReplacementMap["Run3FidXSAnalysisPTJ0"]['catWV'] = "RECO_PTJ0_30p0_75p0_cat2"
# Relacement processes for RV
globalReplacementMap["Run3FidXSAnalysisPTJ0"]['procRVMap'] = od()
globalReplacementMap["Run3FidXSAnalysisPTJ0"]["procRVMap"]["RECO_PTJ0_0p0_30p0_cat0"] = "ggh_PTJ0_0p0_30p0_in"
globalReplacementMap["Run3FidXSAnalysisPTJ0"]["procRVMap"]["RECO_PTJ0_0p0_30p0_cat1"] = "ggh_PTJ0_0p0_30p0_in"
globalReplacementMap["Run3FidXSAnalysisPTJ0"]["procRVMap"]["RECO_PTJ0_0p0_30p0_cat2"] = "ggh_PTJ0_0p0_30p0_in"
globalReplacementMap["Run3FidXSAnalysisPTJ0"]["procRVMap"]["RECO_PTJ0_30p0_75p0_cat0"] = "ggh_PTJ0_30p0_75p0_in"
globalReplacementMap["Run3FidXSAnalysisPTJ0"]["procRVMap"]["RECO_PTJ0_30p0_75p0_cat1"] = "ggh_PTJ0_30p0_75p0_in"
globalReplacementMap["Run3FidXSAnalysisPTJ0"]["procRVMap"]["RECO_PTJ0_30p0_75p0_cat2"] = "ggh_PTJ0_30p0_75p0_in"
globalReplacementMap["Run3FidXSAnalysisPTJ0"]["procRVMap"]["RECO_PTJ0_75p0_120p0_cat0"] = "ggh_PTJ0_75p0_120p0_in"
globalReplacementMap["Run3FidXSAnalysisPTJ0"]["procRVMap"]["RECO_PTJ0_75p0_120p0_cat1"] = "ggh_PTJ0_75p0_120p0_in"
globalReplacementMap["Run3FidXSAnalysisPTJ0"]["procRVMap"]["RECO_PTJ0_75p0_120p0_cat2"] = "ggh_PTJ0_75p0_120p0_in"
globalReplacementMap["Run3FidXSAnalysisPTJ0"]["procRVMap"]["RECO_PTJ0_120p0_200p0_cat0"] = "ggh_PTJ0_120p0_200p0_in"
globalReplacementMap["Run3FidXSAnalysisPTJ0"]["procRVMap"]["RECO_PTJ0_120p0_200p0_cat1"] = "ggh_PTJ0_120p0_200p0_in"
globalReplacementMap["Run3FidXSAnalysisPTJ0"]["procRVMap"]["RECO_PTJ0_120p0_200p0_cat2"] = "ggh_PTJ0_120p0_200p0_in"
globalReplacementMap["Run3FidXSAnalysisPTJ0"]["procRVMap"]["RECO_PTJ0_200p0_10000p0_cat0"] = "ggh_PTJ0_200p0_10000p0_in"
globalReplacementMap["Run3FidXSAnalysisPTJ0"]["procRVMap"]["RECO_PTJ0_200p0_10000p0_cat1"] = "ggh_PTJ0_200p0_10000p0_in"
globalReplacementMap["Run3FidXSAnalysisPTJ0"]["procRVMap"]["RECO_PTJ0_200p0_10000p0_cat2"] = "ggh_PTJ0_200p0_10000p0_in"


# Replacement categories for RV
globalReplacementMap["Run3FidXSAnalysisPTJ0"]["catRVMap"] = od()
globalReplacementMap["Run3FidXSAnalysisPTJ0"]["catRVMap"]["RECO_PTJ0_0p0_30p0_cat0"] = "RECO_PTJ0_0p0_30p0_cat0"
globalReplacementMap["Run3FidXSAnalysisPTJ0"]["catRVMap"]["RECO_PTJ0_0p0_30p0_cat1"] = "RECO_PTJ0_0p0_30p0_cat1"
globalReplacementMap["Run3FidXSAnalysisPTJ0"]["catRVMap"]["RECO_PTJ0_0p0_30p0_cat2"] = "RECO_PTJ0_0p0_30p0_cat2"
globalReplacementMap["Run3FidXSAnalysisPTJ0"]["catRVMap"]["RECO_PTJ0_30p0_75p0_cat0"] = "RECO_PTJ0_30p0_75p0_cat0"
globalReplacementMap["Run3FidXSAnalysisPTJ0"]["catRVMap"]["RECO_PTJ0_30p0_75p0_cat1"] = "RECO_PTJ0_30p0_75p0_cat1"
globalReplacementMap["Run3FidXSAnalysisPTJ0"]["catRVMap"]["RECO_PTJ0_30p0_75p0_cat2"] = "RECO_PTJ0_30p0_75p0_cat2"
globalReplacementMap["Run3FidXSAnalysisPTJ0"]["catRVMap"]["RECO_PTJ0_75p0_120p0_cat0"] = "RECO_PTJ0_75p0_120p0_cat0"
globalReplacementMap["Run3FidXSAnalysisPTJ0"]["catRVMap"]["RECO_PTJ0_75p0_120p0_cat1"] = "RECO_PTJ0_75p0_120p0_cat1"
globalReplacementMap["Run3FidXSAnalysisPTJ0"]["catRVMap"]["RECO_PTJ0_75p0_120p0_cat2"] = "RECO_PTJ0_75p0_120p0_cat2"
globalReplacementMap["Run3FidXSAnalysisPTJ0"]["catRVMap"]["RECO_PTJ0_120p0_200p0_cat0"] = "RECO_PTJ0_120p0_200p0_cat0"
globalReplacementMap["Run3FidXSAnalysisPTJ0"]["catRVMap"]["RECO_PTJ0_120p0_200p0_cat1"] = "RECO_PTJ0_120p0_200p0_cat1"
globalReplacementMap["Run3FidXSAnalysisPTJ0"]["catRVMap"]["RECO_PTJ0_120p0_200p0_cat2"] = "RECO_PTJ0_120p0_200p0_cat2"
globalReplacementMap["Run3FidXSAnalysisPTJ0"]["catRVMap"]["RECO_PTJ0_200p0_10000p0_cat0"] = "RECO_PTJ0_200p0_10000p0_cat0"
globalReplacementMap["Run3FidXSAnalysisPTJ0"]["catRVMap"]["RECO_PTJ0_200p0_10000p0_cat1"] = "RECO_PTJ0_200p0_10000p0_cat1"
globalReplacementMap["Run3FidXSAnalysisPTJ0"]["catRVMap"]["RECO_PTJ0_200p0_10000p0_cat2"] = "RECO_PTJ0_200p0_10000p0_cat2"

# Differential YJ0 (Rapidity of the leading jet)
globalReplacementMap["Run3FidXSAnalysisYJ0"] = od()
# Wrong vertex stuff, which process should be considered?
globalReplacementMap["Run3FidXSAnalysisYJ0"]['procWV'] = "ggh_YJ0_0p0_0p5_in"
globalReplacementMap["Run3FidXSAnalysisYJ0"]['catWV'] = "RECO_first_jet_eta_0p5_1p2_cat2"
# Relacement processes for RV
globalReplacementMap["Run3FidXSAnalysisYJ0"]['procRVMap'] = od()
globalReplacementMap["Run3FidXSAnalysisYJ0"]["procRVMap"]["RECO_first_jet_eta_0p0_0p5_cat0"] = "ggh_YJ0_0p0_0p5_in"
globalReplacementMap["Run3FidXSAnalysisYJ0"]["procRVMap"]["RECO_first_jet_eta_0p0_0p5_cat1"] = "ggh_YJ0_0p0_0p5_in"
globalReplacementMap["Run3FidXSAnalysisYJ0"]["procRVMap"]["RECO_first_jet_eta_0p0_0p5_cat2"] = "ggh_YJ0_0p0_0p5_in"
globalReplacementMap["Run3FidXSAnalysisYJ0"]["procRVMap"]["RECO_first_jet_eta_0p5_1p2_cat0"] = "ggh_YJ0_0p5_1p2_in"
globalReplacementMap["Run3FidXSAnalysisYJ0"]["procRVMap"]["RECO_first_jet_eta_0p5_1p2_cat1"] = "ggh_YJ0_0p5_1p2_in"
globalReplacementMap["Run3FidXSAnalysisYJ0"]["procRVMap"]["RECO_first_jet_eta_0p5_1p2_cat2"] = "ggh_YJ0_0p5_1p2_in"
globalReplacementMap["Run3FidXSAnalysisYJ0"]["procRVMap"]["RECO_first_jet_eta_1p2_2p0_cat0"] = "ggh_YJ0_1p2_2p0_in"
globalReplacementMap["Run3FidXSAnalysisYJ0"]["procRVMap"]["RECO_first_jet_eta_1p2_2p0_cat1"] = "ggh_YJ0_1p2_2p0_in"
globalReplacementMap["Run3FidXSAnalysisYJ0"]["procRVMap"]["RECO_first_jet_eta_1p2_2p0_cat2"] = "ggh_YJ0_1p2_2p0_in"
globalReplacementMap["Run3FidXSAnalysisYJ0"]["procRVMap"]["RECO_first_jet_eta_2p0_2p5_cat0"] = "ggh_YJ0_2p0_2p5_in"
globalReplacementMap["Run3FidXSAnalysisYJ0"]["procRVMap"]["RECO_first_jet_eta_2p0_2p5_cat1"] = "ggh_YJ0_2p0_2p5_in"
globalReplacementMap["Run3FidXSAnalysisYJ0"]["procRVMap"]["RECO_first_jet_eta_2p0_2p5_cat2"] = "ggh_YJ0_2p0_2p5_in"
globalReplacementMap["Run3FidXSAnalysisYJ0"]["procRVMap"]["RECO_first_jet_eta_NJ0_cat0"] = "ggh_YJ0_NJ0_in"
globalReplacementMap["Run3FidXSAnalysisYJ0"]["procRVMap"]["RECO_first_jet_eta_NJ0_cat1"] = "ggh_YJ0_NJ0_in"
globalReplacementMap["Run3FidXSAnalysisYJ0"]["procRVMap"]["RECO_first_jet_eta_NJ0_cat2"] = "ggh_YJ0_NJ0_in"


# Replacement categories for RV
globalReplacementMap["Run3FidXSAnalysisYJ0"]["catRVMap"] = od()
globalReplacementMap["Run3FidXSAnalysisYJ0"]["catRVMap"]["RECO_first_jet_eta_0p0_0p5_cat0"] = "RECO_first_jet_eta_0p0_0p5_cat0"
globalReplacementMap["Run3FidXSAnalysisYJ0"]["catRVMap"]["RECO_first_jet_eta_0p0_0p5_cat1"] = "RECO_first_jet_eta_0p0_0p5_cat1"
globalReplacementMap["Run3FidXSAnalysisYJ0"]["catRVMap"]["RECO_first_jet_eta_0p0_0p5_cat2"] = "RECO_first_jet_eta_0p0_0p5_cat2"
globalReplacementMap["Run3FidXSAnalysisYJ0"]["catRVMap"]["RECO_first_jet_eta_0p5_1p2_cat0"] = "RECO_first_jet_eta_0p5_1p2_cat0"
globalReplacementMap["Run3FidXSAnalysisYJ0"]["catRVMap"]["RECO_first_jet_eta_0p5_1p2_cat1"] = "RECO_first_jet_eta_0p5_1p2_cat1"
globalReplacementMap["Run3FidXSAnalysisYJ0"]["catRVMap"]["RECO_first_jet_eta_0p5_1p2_cat2"] = "RECO_first_jet_eta_0p5_1p2_cat2"
globalReplacementMap["Run3FidXSAnalysisYJ0"]["catRVMap"]["RECO_first_jet_eta_1p2_2p0_cat0"] = "RECO_first_jet_eta_1p2_2p0_cat0"
globalReplacementMap["Run3FidXSAnalysisYJ0"]["catRVMap"]["RECO_first_jet_eta_1p2_2p0_cat1"] = "RECO_first_jet_eta_1p2_2p0_cat1"
globalReplacementMap["Run3FidXSAnalysisYJ0"]["catRVMap"]["RECO_first_jet_eta_1p2_2p0_cat2"] = "RECO_first_jet_eta_1p2_2p0_cat2"
globalReplacementMap["Run3FidXSAnalysisYJ0"]["catRVMap"]["RECO_first_jet_eta_2p0_2p5_cat0"] = "RECO_first_jet_eta_2p0_2p5_cat0"
globalReplacementMap["Run3FidXSAnalysisYJ0"]["catRVMap"]["RECO_first_jet_eta_2p0_2p5_cat1"] = "RECO_first_jet_eta_2p0_2p5_cat1"
globalReplacementMap["Run3FidXSAnalysisYJ0"]["catRVMap"]["RECO_first_jet_eta_2p0_2p5_cat2"] = "RECO_first_jet_eta_2p0_2p5_cat2"
globalReplacementMap["Run3FidXSAnalysisYJ0"]["catRVMap"]["RECO_first_jet_eta_NJ0_cat0"] = "RECO_first_jet_eta_NJ0_cat0"
globalReplacementMap["Run3FidXSAnalysisYJ0"]["catRVMap"]["RECO_first_jet_eta_NJ0_cat1"] = "RECO_first_jet_eta_NJ0_cat1"
globalReplacementMap["Run3FidXSAnalysisYJ0"]["catRVMap"]["RECO_first_jet_eta_NJ0_cat2"] = "RECO_first_jet_eta_NJ0_cat2"


# Differential AbsPhiHJ0 
globalReplacementMap["Run3FidXSAnalysisAbsPhiJ0"] = od()
# Wrong vertex stuff, which process should be considered?
globalReplacementMap["Run3FidXSAnalysisAbsPhiJ0"]['procWV'] = "ggh_AbsPhiHJ0_0p0_2p6_in"
globalReplacementMap["Run3FidXSAnalysisAbsPhiJ0"]['catWV'] = "RECO_AbsPhiHJ0_0p0_2p6_cat2"
# Relacement processes for RV
globalReplacementMap["Run3FidXSAnalysisAbsPhiJ0"]['procRVMap'] = od()
globalReplacementMap["Run3FidXSAnalysisAbsPhiJ0"]["procRVMap"]["RECO_AbsPhiHJ0_0p0_2p6_cat0"] = "ggh_AbsPhiHJ0_0p0_2p6_in"
globalReplacementMap["Run3FidXSAnalysisAbsPhiJ0"]["procRVMap"]["RECO_AbsPhiHJ0_0p0_2p6_cat1"] = "ggh_AbsPhiHJ0_0p0_2p6_in"
globalReplacementMap["Run3FidXSAnalysisAbsPhiJ0"]["procRVMap"]["RECO_AbsPhiHJ0_0p0_2p6_cat2"] = "ggh_AbsPhiHJ0_0p0_2p6_in"
globalReplacementMap["Run3FidXSAnalysisAbsPhiJ0"]["procRVMap"]["RECO_AbsPhiHJ0_2p6_2p9_cat0"] = "ggh_AbsPhiHJ0_2p6_2p9_in"
globalReplacementMap["Run3FidXSAnalysisAbsPhiJ0"]["procRVMap"]["RECO_AbsPhiHJ0_2p6_2p9_cat1"] = "ggh_AbsPhiHJ0_2p6_2p9_in"
globalReplacementMap["Run3FidXSAnalysisAbsPhiJ0"]["procRVMap"]["RECO_AbsPhiHJ0_2p6_2p9_cat2"] = "ggh_AbsPhiHJ0_2p6_2p9_in"
globalReplacementMap["Run3FidXSAnalysisAbsPhiJ0"]["procRVMap"]["RECO_AbsPhiHJ0_2p9_3p03_cat0"] = "ggh_AbsPhiHJ0_2p9_3p03_in"
globalReplacementMap["Run3FidXSAnalysisAbsPhiJ0"]["procRVMap"]["RECO_AbsPhiHJ0_2p9_3p03_cat1"] = "ggh_AbsPhiHJ0_2p9_3p03_in"
globalReplacementMap["Run3FidXSAnalysisAbsPhiJ0"]["procRVMap"]["RECO_AbsPhiHJ0_2p9_3p03_cat2"] = "ggh_AbsPhiHJ0_2p9_3p03_in"
globalReplacementMap["Run3FidXSAnalysisAbsPhiJ0"]["procRVMap"]["RECO_AbsPhiHJ0_3p03_3p1415926_cat0"] = "ggh_AbsPhiHJ0_3p03_3p1415926_in"
globalReplacementMap["Run3FidXSAnalysisAbsPhiJ0"]["procRVMap"]["RECO_AbsPhiHJ0_3p03_3p1415926_cat1"] = "ggh_AbsPhiHJ0_3p03_3p1415926_in"
globalReplacementMap["Run3FidXSAnalysisAbsPhiJ0"]["procRVMap"]["RECO_AbsPhiHJ0_3p03_3p1415926_cat2"] = "ggh_AbsPhiHJ0_3p03_3p1415926_in"
globalReplacementMap["Run3FidXSAnalysisAbsPhiJ0"]["procRVMap"]["RECO_AbsPhiHJ0_NJ_cat0"] = "ggh_AbsPhiHJ0_NJ_in"
globalReplacementMap["Run3FidXSAnalysisAbsPhiJ0"]["procRVMap"]["RECO_AbsPhiHJ0_NJ_cat1"] = "ggh_AbsPhiHJ0_NJ_in"
globalReplacementMap["Run3FidXSAnalysisAbsPhiJ0"]["procRVMap"]["RECO_AbsPhiHJ0_NJ_cat2"] = "ggh_AbsPhiHJ0_NJ_in"

# Replacement categories for RV
globalReplacementMap["Run3FidXSAnalysisAbsPhiJ0"]["catRVMap"] = od()
globalReplacementMap["Run3FidXSAnalysisAbsPhiJ0"]["catRVMap"]["RECO_AbsPhiHJ0_0p0_2p6_cat0"] = "RECO_AbsPhiHJ0_0p0_2p6_cat0"
globalReplacementMap["Run3FidXSAnalysisAbsPhiJ0"]["catRVMap"]["RECO_AbsPhiHJ0_0p0_2p6_cat1"] = "RECO_AbsPhiHJ0_0p0_2p6_cat1"
globalReplacementMap["Run3FidXSAnalysisAbsPhiJ0"]["catRVMap"]["RECO_AbsPhiHJ0_0p0_2p6_cat2"] = "RECO_AbsPhiHJ0_0p0_2p6_cat2"
globalReplacementMap["Run3FidXSAnalysisAbsPhiJ0"]["catRVMap"]["RECO_AbsPhiHJ0_2p6_2p9_cat0"] = "RECO_AbsPhiHJ0_2p6_2p9_cat0"
globalReplacementMap["Run3FidXSAnalysisAbsPhiJ0"]["catRVMap"]["RECO_AbsPhiHJ0_2p6_2p9_cat1"] = "RECO_AbsPhiHJ0_2p6_2p9_cat1"
globalReplacementMap["Run3FidXSAnalysisAbsPhiJ0"]["catRVMap"]["RECO_AbsPhiHJ0_2p6_2p9_cat2"] = "RECO_AbsPhiHJ0_2p6_2p9_cat2"
globalReplacementMap["Run3FidXSAnalysisAbsPhiJ0"]["catRVMap"]["RECO_AbsPhiHJ0_2p9_3p03_cat0"] = "RECO_AbsPhiHJ0_2p9_3p03_cat0"
globalReplacementMap["Run3FidXSAnalysisAbsPhiJ0"]["catRVMap"]["RECO_AbsPhiHJ0_2p9_3p03_cat1"] = "RECO_AbsPhiHJ0_2p9_3p03_cat1"
globalReplacementMap["Run3FidXSAnalysisAbsPhiJ0"]["catRVMap"]["RECO_AbsPhiHJ0_2p9_3p03_cat2"] = "RECO_AbsPhiHJ0_2p9_3p03_cat2"
globalReplacementMap["Run3FidXSAnalysisAbsPhiJ0"]["catRVMap"]["RECO_AbsPhiHJ0_3p03_3p1415926_cat0"] = "RECO_AbsPhiHJ0_3p03_3p1415926_cat0"
globalReplacementMap["Run3FidXSAnalysisAbsPhiJ0"]["catRVMap"]["RECO_AbsPhiHJ0_3p03_3p1415926_cat1"] = "RECO_AbsPhiHJ0_3p03_3p1415926_cat1"
globalReplacementMap["Run3FidXSAnalysisAbsPhiJ0"]["catRVMap"]["RECO_AbsPhiHJ0_3p03_3p1415926_cat2"] = "RECO_AbsPhiHJ0_3p03_3p1415926_cat2"
globalReplacementMap["Run3FidXSAnalysisAbsPhiJ0"]["catRVMap"]["RECO_AbsPhiHJ0_NJ_cat0"] = "RECO_AbsPhiHJ0_NJ_cat0"
globalReplacementMap["Run3FidXSAnalysisAbsPhiJ0"]["catRVMap"]["RECO_AbsPhiHJ0_NJ_cat1"] = "RECO_AbsPhiHJ0_NJ_cat1"
globalReplacementMap["Run3FidXSAnalysisAbsPhiJ0"]["catRVMap"]["RECO_AbsPhiHJ0_NJ_cat2"] = "RECO_AbsPhiHJ0_NJ_cat2"

# Differential AbsYHJ0 
globalReplacementMap["Run3FidXSAnalysisAbsYHJ0"] = od()
# Wrong vertex stuff, which process should be considered?
globalReplacementMap["Run3FidXSAnalysisAbsYHJ0"]['procWV'] = "ggh_AbsYHJ0_0p0_0p6_in"
globalReplacementMap["Run3FidXSAnalysisAbsYHJ0"]['catWV'] = "RECO_AbsYHJ0_NJ0_cat2"
# Relacement processes for RV
globalReplacementMap["Run3FidXSAnalysisAbsYHJ0"]['procRVMap'] = od()
globalReplacementMap["Run3FidXSAnalysisAbsYHJ0"]["procRVMap"]["RECO_AbsYHJ0_0p0_0p6_cat0"] = "ggh_AbsYHJ0_0p0_0p6_in"
globalReplacementMap["Run3FidXSAnalysisAbsYHJ0"]["procRVMap"]["RECO_AbsYHJ0_0p0_0p6_cat1"] = "ggh_AbsYHJ0_0p0_0p6_in"
globalReplacementMap["Run3FidXSAnalysisAbsYHJ0"]["procRVMap"]["RECO_AbsYHJ0_0p0_0p6_cat2"] = "ggh_AbsYHJ0_0p0_0p6_in"
globalReplacementMap["Run3FidXSAnalysisAbsYHJ0"]["procRVMap"]["RECO_AbsYHJ0_0p6_1p2_cat0"] = "ggh_AbsYHJ0_0p6_1p2_in"
globalReplacementMap["Run3FidXSAnalysisAbsYHJ0"]["procRVMap"]["RECO_AbsYHJ0_0p6_1p2_cat1"] = "ggh_AbsYHJ0_0p6_1p2_in"
globalReplacementMap["Run3FidXSAnalysisAbsYHJ0"]["procRVMap"]["RECO_AbsYHJ0_0p6_1p2_cat2"] = "ggh_AbsYHJ0_0p6_1p2_in"
globalReplacementMap["Run3FidXSAnalysisAbsYHJ0"]["procRVMap"]["RECO_AbsYHJ0_1p2_1p9_cat0"] = "ggh_AbsYHJ0_1p2_1p9_in"
globalReplacementMap["Run3FidXSAnalysisAbsYHJ0"]["procRVMap"]["RECO_AbsYHJ0_1p2_1p9_cat1"] = "ggh_AbsYHJ0_1p2_1p9_in"
globalReplacementMap["Run3FidXSAnalysisAbsYHJ0"]["procRVMap"]["RECO_AbsYHJ0_1p2_1p9_cat2"] = "ggh_AbsYHJ0_1p2_1p9_in"
globalReplacementMap["Run3FidXSAnalysisAbsYHJ0"]["procRVMap"]["RECO_AbsYHJ0_1p9_100p0_cat0"] = "ggh_AbsYHJ0_1p9_100p0_in"
globalReplacementMap["Run3FidXSAnalysisAbsYHJ0"]["procRVMap"]["RECO_AbsYHJ0_1p9_100p0_cat1"] = "ggh_AbsYHJ0_1p9_100p0_in"
globalReplacementMap["Run3FidXSAnalysisAbsYHJ0"]["procRVMap"]["RECO_AbsYHJ0_1p9_100p0_cat2"] = "ggh_AbsYHJ0_1p9_100p0_in"
globalReplacementMap["Run3FidXSAnalysisAbsYHJ0"]["procRVMap"]["RECO_AbsYHJ0_NJ0_cat0"] = "ggh_AbsYHJ0_NJ0_in"
globalReplacementMap["Run3FidXSAnalysisAbsYHJ0"]["procRVMap"]["RECO_AbsYHJ0_NJ0_cat1"] = "ggh_AbsYHJ0_NJ0_in"
globalReplacementMap["Run3FidXSAnalysisAbsYHJ0"]["procRVMap"]["RECO_AbsYHJ0_NJ0_cat2"] = "ggh_AbsYHJ0_NJ0_in"


# Replacement categories for RV
globalReplacementMap["Run3FidXSAnalysisAbsYHJ0"]["catRVMap"] = od()
globalReplacementMap["Run3FidXSAnalysisAbsYHJ0"]["catRVMap"]["RECO_AbsYHJ0_0p0_0p6_cat0"] = "RECO_AbsYHJ0_0p0_0p6_cat0"
globalReplacementMap["Run3FidXSAnalysisAbsYHJ0"]["catRVMap"]["RECO_AbsYHJ0_0p0_0p6_cat1"] = "RECO_AbsYHJ0_0p0_0p6_cat1"
globalReplacementMap["Run3FidXSAnalysisAbsYHJ0"]["catRVMap"]["RECO_AbsYHJ0_0p0_0p6_cat2"] = "RECO_AbsYHJ0_0p0_0p6_cat2"
globalReplacementMap["Run3FidXSAnalysisAbsYHJ0"]["catRVMap"]["RECO_AbsYHJ0_0p6_1p2_cat0"] = "RECO_AbsYHJ0_0p6_1p2_cat0"
globalReplacementMap["Run3FidXSAnalysisAbsYHJ0"]["catRVMap"]["RECO_AbsYHJ0_0p6_1p2_cat1"] = "RECO_AbsYHJ0_0p6_1p2_cat1"
globalReplacementMap["Run3FidXSAnalysisAbsYHJ0"]["catRVMap"]["RECO_AbsYHJ0_0p6_1p2_cat2"] = "RECO_AbsYHJ0_0p6_1p2_cat2"
globalReplacementMap["Run3FidXSAnalysisAbsYHJ0"]["catRVMap"]["RECO_AbsYHJ0_1p2_1p9_cat0"] = "RECO_AbsYHJ0_1p2_1p9_cat0"
globalReplacementMap["Run3FidXSAnalysisAbsYHJ0"]["catRVMap"]["RECO_AbsYHJ0_1p2_1p9_cat1"] = "RECO_AbsYHJ0_1p2_1p9_cat1"
globalReplacementMap["Run3FidXSAnalysisAbsYHJ0"]["catRVMap"]["RECO_AbsYHJ0_1p2_1p9_cat2"] = "RECO_AbsYHJ0_1p2_1p9_cat2"
globalReplacementMap["Run3FidXSAnalysisAbsYHJ0"]["catRVMap"]["RECO_AbsYHJ0_1p9_100p0_cat0"] = "RECO_AbsYHJ0_1p9_100p0_cat0"
globalReplacementMap["Run3FidXSAnalysisAbsYHJ0"]["catRVMap"]["RECO_AbsYHJ0_1p9_100p0_cat1"] = "RECO_AbsYHJ0_1p9_100p0_cat1"
globalReplacementMap["Run3FidXSAnalysisAbsYHJ0"]["catRVMap"]["RECO_AbsYHJ0_1p9_100p0_cat2"] = "RECO_AbsYHJ0_1p9_100p0_cat2"
globalReplacementMap["Run3FidXSAnalysisAbsYHJ0"]["catRVMap"]["RECO_AbsYHJ0_NJ0_cat0"] = "RECO_AbsYHJ0_NJ0_cat0"
globalReplacementMap["Run3FidXSAnalysisAbsYHJ0"]["catRVMap"]["RECO_AbsYHJ0_NJ0_cat1"] = "RECO_AbsYHJ0_NJ0_cat1"
globalReplacementMap["Run3FidXSAnalysisAbsYHJ0"]["catRVMap"]["RECO_AbsYHJ0_NJ0_cat2"] = "RECO_AbsYHJ0_NJ0_cat2"
