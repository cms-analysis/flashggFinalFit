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


# Early Analysis
globalReplacementMap["earlyAnalysis"] = od()
# Wrong vertex stuff
globalReplacementMap["earlyAnalysis"]['procWV'] = "GG2H"
globalReplacementMap["earlyAnalysis"]['catWV'] = "worst_resolution"
# Relacement processes for RV
globalReplacementMap["earlyAnalysis"]['procRVMap'] = od()
globalReplacementMap["earlyAnalysis"]["procRVMap"]["best_resolution"] = "GG2H"
globalReplacementMap["earlyAnalysis"]["procRVMap"]["best_resolution"] = "VBF"
globalReplacementMap["earlyAnalysis"]["procRVMap"]["best_resolution"] = "VH"
globalReplacementMap["earlyAnalysis"]["procRVMap"]["best_resolution"] = "TTH"
# Replacement categories for RV
globalReplacementMap["earlyAnalysis"]["catRVMap"] = od()
globalReplacementMap["earlyAnalysis"]["catRVMap"]["GG2H"] = "GG2H"
globalReplacementMap["earlyAnalysis"]["catRVMap"]["VBF"]  = "VBF"
globalReplacementMap["earlyAnalysis"]["catRVMap"]["VH"]   = "VH"
globalReplacementMap["earlyAnalysis"]["catRVMap"]["TTH"]  = "TTH"


# Early Analysis WITH in/out splitting
globalReplacementMap["earlyAnalysisInOut"] = od()
# Wrong vertex stuff
#globalReplacementMap["earlyAnalysisInOut"]['procWV'] = "GG2H_in"
# With nico convention (ggh instead of GG2H)
globalReplacementMap["earlyAnalysisInOut"]['procWV'] = "ggh_in"
globalReplacementMap["earlyAnalysisInOut"]['catWV'] = "worst_resolution"
# Relacement processes for RV
globalReplacementMap["earlyAnalysisInOut"]['procRVMap'] = od()
#globalReplacementMap["earlyAnalysisInOut"]["procRVMap"]["best_resolution"] = "GG2H_in"
#globalReplacementMap["earlyAnalysisInOut"]["procRVMap"]["medium_resolution"] = "GG2H_in"
#globalReplacementMap["earlyAnalysisInOut"]["procRVMap"]["worst_resolution"] = "GG2H_in"
# With nico convention (ggh instead of GG2H)
globalReplacementMap["earlyAnalysisInOut"]["procRVMap"]["best_resolution"] = "ggh_in"
globalReplacementMap["earlyAnalysisInOut"]["procRVMap"]["medium_resolution"] = "ggh_in"
globalReplacementMap["earlyAnalysisInOut"]["procRVMap"]["worst_resolution"] = "ggh_in"
# Replacement categories for RV
globalReplacementMap["earlyAnalysisInOut"]["catRVMap"] = od()
globalReplacementMap["earlyAnalysisInOut"]["catRVMap"]["best_resolution"] = "best_resolution"
globalReplacementMap["earlyAnalysisInOut"]["catRVMap"]["medium_resolution"]  = "medium_resolution"
globalReplacementMap["earlyAnalysisInOut"]["catRVMap"]["worst_resolution"]   = "worst_resolution"


###################################################################################################################################################################################################
###################################################################################################################################################################################################
###################################################################################################################################################################################################
# Early Run3


# Differential PT
globalReplacementMap["earlyAnalysisDiffPt"] = od()
# Wrong vertex stuff, which process should be considered?
globalReplacementMap["earlyAnalysisDiffPt"]['procWV'] = "ggh_PTH_45p0_80p0_in"
globalReplacementMap["earlyAnalysisDiffPt"]['catWV'] = "RECO_PTH_45p0_80p0_cat2"
# Relacement processes for RV
globalReplacementMap["earlyAnalysisDiffPt"]['procRVMap'] = od()
globalReplacementMap["earlyAnalysisDiffPt"]["procRVMap"]["RECO_PTH_0p0_15p0_cat0"] = "ggh_PTH_0p0_15p0_in"
globalReplacementMap["earlyAnalysisDiffPt"]["procRVMap"]["RECO_PTH_0p0_15p0_cat1"] = "ggh_PTH_0p0_15p0_in"
globalReplacementMap["earlyAnalysisDiffPt"]["procRVMap"]["RECO_PTH_0p0_15p0_cat2"] = "ggh_PTH_0p0_15p0_in"
globalReplacementMap["earlyAnalysisDiffPt"]["procRVMap"]["RECO_PTH_15p0_30p0_cat0"] = "ggh_PTH_15p0_30p0_in"
globalReplacementMap["earlyAnalysisDiffPt"]["procRVMap"]["RECO_PTH_15p0_30p0_cat1"] = "ggh_PTH_15p0_30p0_in"
globalReplacementMap["earlyAnalysisDiffPt"]["procRVMap"]["RECO_PTH_15p0_30p0_cat2"] = "ggh_PTH_15p0_30p0_in"
globalReplacementMap["earlyAnalysisDiffPt"]["procRVMap"]["RECO_PTH_30p0_45p0_cat0"] = "ggh_PTH_30p0_45p0_in"
globalReplacementMap["earlyAnalysisDiffPt"]["procRVMap"]["RECO_PTH_30p0_45p0_cat1"] = "ggh_PTH_30p0_45p0_in"
globalReplacementMap["earlyAnalysisDiffPt"]["procRVMap"]["RECO_PTH_30p0_45p0_cat2"] = "ggh_PTH_30p0_45p0_in"
globalReplacementMap["earlyAnalysisDiffPt"]["procRVMap"]["RECO_PTH_45p0_80p0_cat0"] = "ggh_PTH_45p0_80p0_in"
globalReplacementMap["earlyAnalysisDiffPt"]["procRVMap"]["RECO_PTH_45p0_80p0_cat1"] = "ggh_PTH_45p0_80p0_in"
globalReplacementMap["earlyAnalysisDiffPt"]["procRVMap"]["RECO_PTH_45p0_80p0_cat2"] = "ggh_PTH_45p0_80p0_in"
globalReplacementMap["earlyAnalysisDiffPt"]["procRVMap"]["RECO_PTH_80p0_120p0_cat0"] = "ggh_PTH_80p0_120p0_in"
globalReplacementMap["earlyAnalysisDiffPt"]["procRVMap"]["RECO_PTH_80p0_120p0_cat1"] = "ggh_PTH_80p0_120p0_in"
globalReplacementMap["earlyAnalysisDiffPt"]["procRVMap"]["RECO_PTH_80p0_120p0_cat2"] = "ggh_PTH_80p0_120p0_in"
globalReplacementMap["earlyAnalysisDiffPt"]["procRVMap"]["RECO_PTH_120p0_200p0_cat0"] = "ggh_PTH_120p0_200p0_in"
globalReplacementMap["earlyAnalysisDiffPt"]["procRVMap"]["RECO_PTH_120p0_200p0_cat1"] = "ggh_PTH_120p0_200p0_in"
globalReplacementMap["earlyAnalysisDiffPt"]["procRVMap"]["RECO_PTH_120p0_200p0_cat2"] = "ggh_PTH_120p0_200p0_in"
globalReplacementMap["earlyAnalysisDiffPt"]["procRVMap"]["RECO_PTH_200p0_350p0_cat0"] = "ggh_PTH_200p0_350p0_in"
globalReplacementMap["earlyAnalysisDiffPt"]["procRVMap"]["RECO_PTH_200p0_350p0_cat1"] = "ggh_PTH_200p0_350p0_in"
globalReplacementMap["earlyAnalysisDiffPt"]["procRVMap"]["RECO_PTH_200p0_350p0_cat2"] = "ggh_PTH_200p0_350p0_in"
globalReplacementMap["earlyAnalysisDiffPt"]["procRVMap"]["RECO_PTH_350p0_10000p0_cat0"] = "ggh_PTH_350p0_10000p0_in"
globalReplacementMap["earlyAnalysisDiffPt"]["procRVMap"]["RECO_PTH_350p0_10000p0_cat1"] = "ggh_PTH_350p0_10000p0_in"
globalReplacementMap["earlyAnalysisDiffPt"]["procRVMap"]["RECO_PTH_350p0_10000p0_cat2"] = "ggh_PTH_350p0_10000p0_in"

# Replacement categories for RV
globalReplacementMap["earlyAnalysisDiffPt"]["catRVMap"] = od()
globalReplacementMap["earlyAnalysisDiffPt"]["catRVMap"]["RECO_PTH_0p0_15p0_cat0"] = "RECO_PTH_0p0_15p0_cat0"
globalReplacementMap["earlyAnalysisDiffPt"]["catRVMap"]["RECO_PTH_0p0_15p0_cat1"] = "RECO_PTH_0p0_15p0_cat1"
globalReplacementMap["earlyAnalysisDiffPt"]["catRVMap"]["RECO_PTH_0p0_15p0_cat2"] = "RECO_PTH_0p0_15p0_cat2"
globalReplacementMap["earlyAnalysisDiffPt"]["catRVMap"]["RECO_PTH_15p0_30p0_cat0"] = "RECO_PTH_15p0_30p0_cat0"
globalReplacementMap["earlyAnalysisDiffPt"]["catRVMap"]["RECO_PTH_15p0_30p0_cat1"] = "RECO_PTH_15p0_30p0_cat1"
globalReplacementMap["earlyAnalysisDiffPt"]["catRVMap"]["RECO_PTH_15p0_30p0_cat2"] = "RECO_PTH_15p0_30p0_cat2"
globalReplacementMap["earlyAnalysisDiffPt"]["catRVMap"]["RECO_PTH_30p0_45p0_cat0"] = "RECO_PTH_30p0_45p0_cat0"
globalReplacementMap["earlyAnalysisDiffPt"]["catRVMap"]["RECO_PTH_30p0_45p0_cat1"] = "RECO_PTH_30p0_45p0_cat1"
globalReplacementMap["earlyAnalysisDiffPt"]["catRVMap"]["RECO_PTH_30p0_45p0_cat2"] = "RECO_PTH_30p0_45p0_cat2"
globalReplacementMap["earlyAnalysisDiffPt"]["catRVMap"]["RECO_PTH_45p0_80p0_cat0"] = "RECO_PTH_45p0_80p0_cat0"
globalReplacementMap["earlyAnalysisDiffPt"]["catRVMap"]["RECO_PTH_45p0_80p0_cat1"] = "RECO_PTH_45p0_80p0_cat1"
globalReplacementMap["earlyAnalysisDiffPt"]["catRVMap"]["RECO_PTH_45p0_80p0_cat2"] = "RECO_PTH_45p0_80p0_cat2"
globalReplacementMap["earlyAnalysisDiffPt"]["catRVMap"]["RECO_PTH_80p0_120p0_cat0"] = "RECO_PTH_80p0_120p0_cat0"
globalReplacementMap["earlyAnalysisDiffPt"]["catRVMap"]["RECO_PTH_80p0_120p0_cat1"] = "RECO_PTH_80p0_120p0_cat1"
globalReplacementMap["earlyAnalysisDiffPt"]["catRVMap"]["RECO_PTH_80p0_120p0_cat2"] = "RECO_PTH_80p0_120p0_cat2"
globalReplacementMap["earlyAnalysisDiffPt"]["catRVMap"]["RECO_PTH_120p0_200p0_cat0"] = "RECO_PTH_120p0_200p0_cat0"
globalReplacementMap["earlyAnalysisDiffPt"]["catRVMap"]["RECO_PTH_120p0_200p0_cat1"] = "RECO_PTH_120p0_200p0_cat1"
globalReplacementMap["earlyAnalysisDiffPt"]["catRVMap"]["RECO_PTH_120p0_200p0_cat2"] = "RECO_PTH_120p0_200p0_cat2"
globalReplacementMap["earlyAnalysisDiffPt"]["catRVMap"]["RECO_PTH_200p0_350p0_cat0"] = "RECO_PTH_200p0_350p0_cat0"
globalReplacementMap["earlyAnalysisDiffPt"]["catRVMap"]["RECO_PTH_200p0_350p0_cat1"] = "RECO_PTH_200p0_350p0_cat1"
globalReplacementMap["earlyAnalysisDiffPt"]["catRVMap"]["RECO_PTH_200p0_350p0_cat2"] = "RECO_PTH_200p0_350p0_cat2"
globalReplacementMap["earlyAnalysisDiffPt"]["catRVMap"]["RECO_PTH_350p0_10000p0_cat0"] = "RECO_PTH_350p0_10000p0_cat0"
globalReplacementMap["earlyAnalysisDiffPt"]["catRVMap"]["RECO_PTH_350p0_10000p0_cat1"] = "RECO_PTH_350p0_10000p0_cat1"
globalReplacementMap["earlyAnalysisDiffPt"]["catRVMap"]["RECO_PTH_350p0_10000p0_cat2"] = "RECO_PTH_350p0_10000p0_cat2"


# Differential Y (Rapidity)
globalReplacementMap["earlyAnalysisDiffYH"] = od()
# Wrong vertex stuff, which process should be considered?
globalReplacementMap["earlyAnalysisDiffYH"]['procWV'] = "ggh_YH_0p3_0p6_in"
globalReplacementMap["earlyAnalysisDiffYH"]['catWV'] = "RECO_rapidity_0p3_0p6_cat2"
# Relacement processes for RV
globalReplacementMap["earlyAnalysisDiffYH"]['procRVMap'] = od()
globalReplacementMap["earlyAnalysisDiffYH"]["procRVMap"]["RECO_rapidity_0p0_0p15_cat0"] = "ggh_YH_0p0_0p15_in"
globalReplacementMap["earlyAnalysisDiffYH"]["procRVMap"]["RECO_rapidity_0p0_0p15_cat1"] = "ggh_YH_0p0_0p15_in"
globalReplacementMap["earlyAnalysisDiffYH"]["procRVMap"]["RECO_rapidity_0p0_0p15_cat2"] = "ggh_YH_0p0_0p15_in"
globalReplacementMap["earlyAnalysisDiffYH"]["procRVMap"]["RECO_rapidity_0p15_0p3_cat0"] = "ggh_YH_0p15_0p3_in"
globalReplacementMap["earlyAnalysisDiffYH"]["procRVMap"]["RECO_rapidity_0p15_0p3_cat1"] = "ggh_YH_0p15_0p3_in"
globalReplacementMap["earlyAnalysisDiffYH"]["procRVMap"]["RECO_rapidity_0p15_0p3_cat2"] = "ggh_YH_0p15_0p3_in"
globalReplacementMap["earlyAnalysisDiffYH"]["procRVMap"]["RECO_rapidity_0p3_0p6_cat0"] = "ggh_YH_0p3_0p6_in"
globalReplacementMap["earlyAnalysisDiffYH"]["procRVMap"]["RECO_rapidity_0p3_0p6_cat1"] = "ggh_YH_0p3_0p6_in"
globalReplacementMap["earlyAnalysisDiffYH"]["procRVMap"]["RECO_rapidity_0p3_0p6_cat2"] = "ggh_YH_0p3_0p6_in"
globalReplacementMap["earlyAnalysisDiffYH"]["procRVMap"]["RECO_rapidity_0p6_0p9_cat0"] = "ggh_YH_0p6_0p9_in"
globalReplacementMap["earlyAnalysisDiffYH"]["procRVMap"]["RECO_rapidity_0p6_0p9_cat1"] = "ggh_YH_0p6_0p9_in"
globalReplacementMap["earlyAnalysisDiffYH"]["procRVMap"]["RECO_rapidity_0p6_0p9_cat2"] = "ggh_YH_0p6_0p9_in"
globalReplacementMap["earlyAnalysisDiffYH"]["procRVMap"]["RECO_rapidity_0p9_2p5_cat0"] = "ggh_YH_0p9_2p5_in"
globalReplacementMap["earlyAnalysisDiffYH"]["procRVMap"]["RECO_rapidity_0p9_2p5_cat1"] = "ggh_YH_0p9_2p5_in"
globalReplacementMap["earlyAnalysisDiffYH"]["procRVMap"]["RECO_rapidity_0p9_2p5_cat2"] = "ggh_YH_0p9_2p5_in"


# Replacement categories for RV
globalReplacementMap["earlyAnalysisDiffYH"]["catRVMap"] = od()
globalReplacementMap["earlyAnalysisDiffYH"]["catRVMap"]["RECO_rapidity_0p0_0p15_cat0"] = "RECO_rapidity_0p0_0p15_cat0"
globalReplacementMap["earlyAnalysisDiffYH"]["catRVMap"]["RECO_rapidity_0p0_0p15_cat1"] = "RECO_rapidity_0p0_0p15_cat1"
globalReplacementMap["earlyAnalysisDiffYH"]["catRVMap"]["RECO_rapidity_0p0_0p15_cat2"] = "RECO_rapidity_0p0_0p15_cat2"
globalReplacementMap["earlyAnalysisDiffYH"]["catRVMap"]["RECO_rapidity_0p15_0p3_cat0"] = "RECO_rapidity_0p15_0p3_cat0"
globalReplacementMap["earlyAnalysisDiffYH"]["catRVMap"]["RECO_rapidity_0p15_0p3_cat1"] = "RECO_rapidity_0p15_0p3_cat1"
globalReplacementMap["earlyAnalysisDiffYH"]["catRVMap"]["RECO_rapidity_0p15_0p3_cat2"] = "RECO_rapidity_0p15_0p3_cat2"
globalReplacementMap["earlyAnalysisDiffYH"]["catRVMap"]["RECO_rapidity_0p3_0p6_cat0"] = "RECO_rapidity_0p3_0p6_cat0"
globalReplacementMap["earlyAnalysisDiffYH"]["catRVMap"]["RECO_rapidity_0p3_0p6_cat1"] = "RECO_rapidity_0p3_0p6_cat1"
globalReplacementMap["earlyAnalysisDiffYH"]["catRVMap"]["RECO_rapidity_0p3_0p6_cat2"] = "RECO_rapidity_0p3_0p6_cat2"
globalReplacementMap["earlyAnalysisDiffYH"]["catRVMap"]["RECO_rapidity_0p6_0p9_cat0"] = "RECO_rapidity_0p6_0p9_cat0"
globalReplacementMap["earlyAnalysisDiffYH"]["catRVMap"]["RECO_rapidity_0p6_0p9_cat1"] = "RECO_rapidity_0p6_0p9_cat1"
globalReplacementMap["earlyAnalysisDiffYH"]["catRVMap"]["RECO_rapidity_0p6_0p9_cat2"] = "RECO_rapidity_0p6_0p9_cat2"
globalReplacementMap["earlyAnalysisDiffYH"]["catRVMap"]["RECO_rapidity_0p9_2p5_cat0"] = "RECO_rapidity_0p9_2p5_cat0"
globalReplacementMap["earlyAnalysisDiffYH"]["catRVMap"]["RECO_rapidity_0p9_2p5_cat1"] = "RECO_rapidity_0p9_2p5_cat1"
globalReplacementMap["earlyAnalysisDiffYH"]["catRVMap"]["RECO_rapidity_0p9_2p5_cat2"] = "RECO_rapidity_0p9_2p5_cat2"


# Differential NJ (Number of Jets)
globalReplacementMap["earlyAnalysisDiffNJ"] = od()
# Wrong vertex stuff, which process should be considered?
globalReplacementMap["earlyAnalysisDiffNJ"]['procWV'] = "ggh_NJ_1p0_2p0_in"
globalReplacementMap["earlyAnalysisDiffNJ"]['catWV'] = "RECO_Njets2p5_2p0_3p0_cat2"
# Relacement processes for RV
globalReplacementMap["earlyAnalysisDiffNJ"]['procRVMap'] = od()
globalReplacementMap["earlyAnalysisDiffNJ"]["procRVMap"]["RECO_Njets2p5_0p0_1p0_cat0"] = "ggh_NJ_0p0_1p0_in"
globalReplacementMap["earlyAnalysisDiffNJ"]["procRVMap"]["RECO_Njets2p5_0p0_1p0_cat1"] = "ggh_NJ_0p0_1p0_in"
globalReplacementMap["earlyAnalysisDiffNJ"]["procRVMap"]["RECO_Njets2p5_0p0_1p0_cat2"] = "ggh_NJ_0p0_1p0_in"
globalReplacementMap["earlyAnalysisDiffNJ"]["procRVMap"]["RECO_Njets2p5_1p0_2p0_cat0"] = "ggh_NJ_1p0_2p0_in"
globalReplacementMap["earlyAnalysisDiffNJ"]["procRVMap"]["RECO_Njets2p5_1p0_2p0_cat1"] = "ggh_NJ_1p0_2p0_in"
globalReplacementMap["earlyAnalysisDiffNJ"]["procRVMap"]["RECO_Njets2p5_1p0_2p0_cat2"] = "ggh_NJ_1p0_2p0_in"
globalReplacementMap["earlyAnalysisDiffNJ"]["procRVMap"]["RECO_Njets2p5_2p0_3p0_cat0"] = "ggh_NJ_2p0_3p0_in"
globalReplacementMap["earlyAnalysisDiffNJ"]["procRVMap"]["RECO_Njets2p5_2p0_3p0_cat1"] = "ggh_NJ_2p0_3p0_in"
globalReplacementMap["earlyAnalysisDiffNJ"]["procRVMap"]["RECO_Njets2p5_2p0_3p0_cat2"] = "ggh_NJ_2p0_3p0_in"

globalReplacementMap["earlyAnalysisDiffNJ"]["procRVMap"]["RECO_Njets2p5_3p0_100p0_cat0"] = "ggh_NJ_3p0_100p0_in"
globalReplacementMap["earlyAnalysisDiffNJ"]["procRVMap"]["RECO_Njets2p5_3p0_100p0_cat1"] = "ggh_NJ_3p0_100p0_in"
globalReplacementMap["earlyAnalysisDiffNJ"]["procRVMap"]["RECO_Njets2p5_3p0_100p0_cat2"] = "ggh_NJ_3p0_100p0_in"

# 5 bin Njets2p5
# globalReplacementMap["earlyAnalysisDiffNJ"]["procRVMap"]["RECO_Njets2p5_3p0_4p0_cat0"] = "ggh_NJ_3p0_4p0_in"
# globalReplacementMap["earlyAnalysisDiffNJ"]["procRVMap"]["RECO_Njets2p5_3p0_4p0_cat1"] = "ggh_NJ_3p0_4p0_in"
# globalReplacementMap["earlyAnalysisDiffNJ"]["procRVMap"]["RECO_Njets2p5_3p0_4p0_cat2"] = "ggh_NJ_3p0_4p0_in"
# globalReplacementMap["earlyAnalysisDiffNJ"]["procRVMap"]["RECO_Njets2p5_4p0_100p0_cat0"] = "ggh_NJ_4p0_100p0_in"
# globalReplacementMap["earlyAnalysisDiffNJ"]["procRVMap"]["RECO_Njets2p5_4p0_100p0_cat1"] = "ggh_NJ_4p0_100p0_in"
# globalReplacementMap["earlyAnalysisDiffNJ"]["procRVMap"]["RECO_Njets2p5_4p0_100p0_cat2"] = "ggh_NJ_4p0_100p0_in"


# Replacement categories for RV
globalReplacementMap["earlyAnalysisDiffNJ"]["catRVMap"] = od()
globalReplacementMap["earlyAnalysisDiffNJ"]["catRVMap"]["RECO_Njets2p5_0p0_1p0_cat0"] = "RECO_Njets2p5_0p0_1p0_cat0"
globalReplacementMap["earlyAnalysisDiffNJ"]["catRVMap"]["RECO_Njets2p5_0p0_1p0_cat1"] = "RECO_Njets2p5_0p0_1p0_cat1"
globalReplacementMap["earlyAnalysisDiffNJ"]["catRVMap"]["RECO_Njets2p5_0p0_1p0_cat2"] = "RECO_Njets2p5_0p0_1p0_cat2"
globalReplacementMap["earlyAnalysisDiffNJ"]["catRVMap"]["RECO_Njets2p5_1p0_2p0_cat0"] = "RECO_Njets2p5_1p0_2p0_cat0"
globalReplacementMap["earlyAnalysisDiffNJ"]["catRVMap"]["RECO_Njets2p5_1p0_2p0_cat1"] = "RECO_Njets2p5_1p0_2p0_cat1"
globalReplacementMap["earlyAnalysisDiffNJ"]["catRVMap"]["RECO_Njets2p5_1p0_2p0_cat2"] = "RECO_Njets2p5_1p0_2p0_cat2"
globalReplacementMap["earlyAnalysisDiffNJ"]["catRVMap"]["RECO_Njets2p5_2p0_3p0_cat0"] = "RECO_Njets2p5_2p0_3p0_cat0"
globalReplacementMap["earlyAnalysisDiffNJ"]["catRVMap"]["RECO_Njets2p5_2p0_3p0_cat1"] = "RECO_Njets2p5_2p0_3p0_cat1"
globalReplacementMap["earlyAnalysisDiffNJ"]["catRVMap"]["RECO_Njets2p5_2p0_3p0_cat2"] = "RECO_Njets2p5_2p0_3p0_cat2"

globalReplacementMap["earlyAnalysisDiffNJ"]["catRVMap"]["RECO_Njets2p5_3p0_100p0_cat0"] = "RECO_Njets2p5_3p0_100p0_cat0"
globalReplacementMap["earlyAnalysisDiffNJ"]["catRVMap"]["RECO_Njets2p5_3p0_100p0_cat1"] = "RECO_Njets2p5_3p0_100p0_cat1"
globalReplacementMap["earlyAnalysisDiffNJ"]["catRVMap"]["RECO_Njets2p5_3p0_100p0_cat2"] = "RECO_Njets2p5_3p0_100p0_cat2"

# Differential PTJ0 (PT of the leading jet)
globalReplacementMap["earlyAnalysisDiffPTJ0"] = od()
# Wrong vertex stuff, which process should be considered?
globalReplacementMap["earlyAnalysisDiffPTJ0"]['procWV'] = "ggh_PTJ0_30p0_75p0_in"
globalReplacementMap["earlyAnalysisDiffPTJ0"]['catWV'] = "RECO_first_jet_pt_30p0_75p0_cat2"
# Relacement processes for RV
globalReplacementMap["earlyAnalysisDiffPTJ0"]['procRVMap'] = od()
globalReplacementMap["earlyAnalysisDiffPTJ0"]["procRVMap"]["RECO_first_jet_pt_0p0_30p0_cat0"] = "ggh_PTJ0_0p0_30p0_in"
globalReplacementMap["earlyAnalysisDiffPTJ0"]["procRVMap"]["RECO_first_jet_pt_0p0_30p0_cat1"] = "ggh_PTJ0_0p0_30p0_in"
globalReplacementMap["earlyAnalysisDiffPTJ0"]["procRVMap"]["RECO_first_jet_pt_0p0_30p0_cat2"] = "ggh_PTJ0_0p0_30p0_in"
globalReplacementMap["earlyAnalysisDiffPTJ0"]["procRVMap"]["RECO_first_jet_pt_30p0_75p0_cat0"] = "ggh_PTJ0_30p0_75p0_in"
globalReplacementMap["earlyAnalysisDiffPTJ0"]["procRVMap"]["RECO_first_jet_pt_30p0_75p0_cat1"] = "ggh_PTJ0_30p0_75p0_in"
globalReplacementMap["earlyAnalysisDiffPTJ0"]["procRVMap"]["RECO_first_jet_pt_30p0_75p0_cat2"] = "ggh_PTJ0_30p0_75p0_in"
globalReplacementMap["earlyAnalysisDiffPTJ0"]["procRVMap"]["RECO_first_jet_pt_75p0_120p0_cat0"] = "ggh_PTJ0_75p0_120p0_in"
globalReplacementMap["earlyAnalysisDiffPTJ0"]["procRVMap"]["RECO_first_jet_pt_75p0_120p0_cat1"] = "ggh_PTJ0_75p0_120p0_in"
globalReplacementMap["earlyAnalysisDiffPTJ0"]["procRVMap"]["RECO_first_jet_pt_75p0_120p0_cat2"] = "ggh_PTJ0_75p0_120p0_in"
globalReplacementMap["earlyAnalysisDiffPTJ0"]["procRVMap"]["RECO_first_jet_pt_120p0_200p0_cat0"] = "ggh_PTJ0_120p0_200p0_in"
globalReplacementMap["earlyAnalysisDiffPTJ0"]["procRVMap"]["RECO_first_jet_pt_120p0_200p0_cat1"] = "ggh_PTJ0_120p0_200p0_in"
globalReplacementMap["earlyAnalysisDiffPTJ0"]["procRVMap"]["RECO_first_jet_pt_120p0_200p0_cat2"] = "ggh_PTJ0_120p0_200p0_in"
globalReplacementMap["earlyAnalysisDiffPTJ0"]["procRVMap"]["RECO_first_jet_pt_200p0_10000p0_cat0"] = "ggh_PTJ0_200p0_10000p0_in"
globalReplacementMap["earlyAnalysisDiffPTJ0"]["procRVMap"]["RECO_first_jet_pt_200p0_10000p0_cat1"] = "ggh_PTJ0_200p0_10000p0_in"
globalReplacementMap["earlyAnalysisDiffPTJ0"]["procRVMap"]["RECO_first_jet_pt_200p0_10000p0_cat2"] = "ggh_PTJ0_200p0_10000p0_in"


# Replacement categories for RV
globalReplacementMap["earlyAnalysisDiffPTJ0"]["catRVMap"] = od()
globalReplacementMap["earlyAnalysisDiffPTJ0"]["catRVMap"]["RECO_first_jet_pt_0p0_30p0_cat0"] = "RECO_first_jet_pt_0p0_30p0_cat0"
globalReplacementMap["earlyAnalysisDiffPTJ0"]["catRVMap"]["RECO_first_jet_pt_0p0_30p0_cat1"] = "RECO_first_jet_pt_0p0_30p0_cat1"
globalReplacementMap["earlyAnalysisDiffPTJ0"]["catRVMap"]["RECO_first_jet_pt_0p0_30p0_cat2"] = "RECO_first_jet_pt_0p0_30p0_cat2"
globalReplacementMap["earlyAnalysisDiffPTJ0"]["catRVMap"]["RECO_first_jet_pt_30p0_75p0_cat0"] = "RECO_first_jet_pt_30p0_75p0_cat0"
globalReplacementMap["earlyAnalysisDiffPTJ0"]["catRVMap"]["RECO_first_jet_pt_30p0_75p0_cat1"] = "RECO_first_jet_pt_30p0_75p0_cat1"
globalReplacementMap["earlyAnalysisDiffPTJ0"]["catRVMap"]["RECO_first_jet_pt_30p0_75p0_cat2"] = "RECO_first_jet_pt_30p0_75p0_cat2"
globalReplacementMap["earlyAnalysisDiffPTJ0"]["catRVMap"]["RECO_first_jet_pt_75p0_120p0_cat0"] = "RECO_first_jet_pt_75p0_120p0_cat0"
globalReplacementMap["earlyAnalysisDiffPTJ0"]["catRVMap"]["RECO_first_jet_pt_75p0_120p0_cat1"] = "RECO_first_jet_pt_75p0_120p0_cat1"
globalReplacementMap["earlyAnalysisDiffPTJ0"]["catRVMap"]["RECO_first_jet_pt_75p0_120p0_cat2"] = "RECO_first_jet_pt_75p0_120p0_cat2"
globalReplacementMap["earlyAnalysisDiffPTJ0"]["catRVMap"]["RECO_first_jet_pt_120p0_200p0_cat0"] = "RECO_first_jet_pt_120p0_200p0_cat0"
globalReplacementMap["earlyAnalysisDiffPTJ0"]["catRVMap"]["RECO_first_jet_pt_120p0_200p0_cat1"] = "RECO_first_jet_pt_120p0_200p0_cat1"
globalReplacementMap["earlyAnalysisDiffPTJ0"]["catRVMap"]["RECO_first_jet_pt_120p0_200p0_cat2"] = "RECO_first_jet_pt_120p0_200p0_cat2"
globalReplacementMap["earlyAnalysisDiffPTJ0"]["catRVMap"]["RECO_first_jet_pt_200p0_10000p0_cat0"] = "RECO_first_jet_pt_200p0_10000p0_cat0"
globalReplacementMap["earlyAnalysisDiffPTJ0"]["catRVMap"]["RECO_first_jet_pt_200p0_10000p0_cat1"] = "RECO_first_jet_pt_200p0_10000p0_cat1"
globalReplacementMap["earlyAnalysisDiffPTJ0"]["catRVMap"]["RECO_first_jet_pt_200p0_10000p0_cat2"] = "RECO_first_jet_pt_200p0_10000p0_cat2"

# # Differential PTJ0 (PT of the leading jet)
# globalReplacementMap["earlyAnalysisDiffPTJ0"] = od()
# # Wrong vertex stuff, which process should be considered?
# globalReplacementMap["earlyAnalysisDiffPTJ0"]['procWV'] = "ggh_PTJ0_30p0_10000p0_in"
# globalReplacementMap["earlyAnalysisDiffPTJ0"]['catWV'] = "RECO_first_jet_pt_30p0_10000p0_cat2"
# # Relacement processes for RV
# globalReplacementMap["earlyAnalysisDiffPTJ0"]['procRVMap'] = od()
# globalReplacementMap["earlyAnalysisDiffPTJ0"]["procRVMap"]["RECO_first_jet_pt_0p0_30p0_cat0"] = "ggh_PTJ0_0p0_30p0_in"
# globalReplacementMap["earlyAnalysisDiffPTJ0"]["procRVMap"]["RECO_first_jet_pt_0p0_30p0_cat1"] = "ggh_PTJ0_0p0_30p0_in"
# globalReplacementMap["earlyAnalysisDiffPTJ0"]["procRVMap"]["RECO_first_jet_pt_0p0_30p0_cat2"] = "ggh_PTJ0_0p0_30p0_in"
# globalReplacementMap["earlyAnalysisDiffPTJ0"]["procRVMap"]["RECO_first_jet_pt_30p0_10000p0_cat0"] = "ggh_PTJ0_30p0_10000p0_in"
# globalReplacementMap["earlyAnalysisDiffPTJ0"]["procRVMap"]["RECO_first_jet_pt_30p0_10000p0_cat1"] = "ggh_PTJ0_30p0_10000p0_in"
# globalReplacementMap["earlyAnalysisDiffPTJ0"]["procRVMap"]["RECO_first_jet_pt_30p0_10000p0_cat2"] = "ggh_PTJ0_30p0_10000p0_in"


# # Replacement categories for RV
# globalReplacementMap["earlyAnalysisDiffPTJ0"]["catRVMap"] = od()
# globalReplacementMap["earlyAnalysisDiffPTJ0"]["catRVMap"]["RECO_first_jet_pt_0p0_30p0_cat0"] = "RECO_first_jet_pt_0p0_30p0_cat0"
# globalReplacementMap["earlyAnalysisDiffPTJ0"]["catRVMap"]["RECO_first_jet_pt_0p0_30p0_cat1"] = "RECO_first_jet_pt_0p0_30p0_cat1"
# globalReplacementMap["earlyAnalysisDiffPTJ0"]["catRVMap"]["RECO_first_jet_pt_0p0_30p0_cat2"] = "RECO_first_jet_pt_0p0_30p0_cat2"
# globalReplacementMap["earlyAnalysisDiffPTJ0"]["catRVMap"]["RECO_first_jet_pt_30p0_10000p0_cat0"] = "RECO_first_jet_pt_30p0_10000p0_cat0"
# globalReplacementMap["earlyAnalysisDiffPTJ0"]["catRVMap"]["RECO_first_jet_pt_30p0_10000p0_cat1"] = "RECO_first_jet_pt_30p0_10000p0_cat1"
# globalReplacementMap["earlyAnalysisDiffPTJ0"]["catRVMap"]["RECO_first_jet_pt_30p0_10000p0_cat2"] = "RECO_first_jet_pt_30p0_10000p0_cat2"

# Differential YJ0 (Rapidity of the leading jet)
globalReplacementMap["earlyAnalysisDiffYJ0"] = od()
# Wrong vertex stuff, which process should be considered?
globalReplacementMap["earlyAnalysisDiffYJ0"]['procWV'] = "ggh_YJ0_0p0_0p5_in"
globalReplacementMap["earlyAnalysisDiffYJ0"]['catWV'] = "RECO_first_jet_eta_0p5_1p2_cat2"
# Relacement processes for RV
globalReplacementMap["earlyAnalysisDiffYJ0"]['procRVMap'] = od()
globalReplacementMap["earlyAnalysisDiffYJ0"]["procRVMap"]["RECO_first_jet_eta_0p0_0p5_cat0"] = "ggh_YJ0_0p0_0p5_in"
globalReplacementMap["earlyAnalysisDiffYJ0"]["procRVMap"]["RECO_first_jet_eta_0p0_0p5_cat1"] = "ggh_YJ0_0p0_0p5_in"
globalReplacementMap["earlyAnalysisDiffYJ0"]["procRVMap"]["RECO_first_jet_eta_0p0_0p5_cat2"] = "ggh_YJ0_0p0_0p5_in"
globalReplacementMap["earlyAnalysisDiffYJ0"]["procRVMap"]["RECO_first_jet_eta_0p5_1p2_cat0"] = "ggh_YJ0_0p5_1p2_in"
globalReplacementMap["earlyAnalysisDiffYJ0"]["procRVMap"]["RECO_first_jet_eta_0p5_1p2_cat1"] = "ggh_YJ0_0p5_1p2_in"
globalReplacementMap["earlyAnalysisDiffYJ0"]["procRVMap"]["RECO_first_jet_eta_0p5_1p2_cat2"] = "ggh_YJ0_0p5_1p2_in"
globalReplacementMap["earlyAnalysisDiffYJ0"]["procRVMap"]["RECO_first_jet_eta_1p2_2p0_cat0"] = "ggh_YJ0_1p2_2p0_in"
globalReplacementMap["earlyAnalysisDiffYJ0"]["procRVMap"]["RECO_first_jet_eta_1p2_2p0_cat1"] = "ggh_YJ0_1p2_2p0_in"
globalReplacementMap["earlyAnalysisDiffYJ0"]["procRVMap"]["RECO_first_jet_eta_1p2_2p0_cat2"] = "ggh_YJ0_1p2_2p0_in"
globalReplacementMap["earlyAnalysisDiffYJ0"]["procRVMap"]["RECO_first_jet_eta_2p0_2p5_cat0"] = "ggh_YJ0_2p0_2p5_in"
globalReplacementMap["earlyAnalysisDiffYJ0"]["procRVMap"]["RECO_first_jet_eta_2p0_2p5_cat1"] = "ggh_YJ0_2p0_2p5_in"
globalReplacementMap["earlyAnalysisDiffYJ0"]["procRVMap"]["RECO_first_jet_eta_2p0_2p5_cat2"] = "ggh_YJ0_2p0_2p5_in"
globalReplacementMap["earlyAnalysisDiffYJ0"]["procRVMap"]["RECO_first_jet_eta_NJ0_cat0"] = "ggh_YJ0_NJ0_in"
globalReplacementMap["earlyAnalysisDiffYJ0"]["procRVMap"]["RECO_first_jet_eta_NJ0_cat1"] = "ggh_YJ0_NJ0_in"
globalReplacementMap["earlyAnalysisDiffYJ0"]["procRVMap"]["RECO_first_jet_eta_NJ0_cat2"] = "ggh_YJ0_NJ0_in"


# Replacement categories for RV
globalReplacementMap["earlyAnalysisDiffYJ0"]["catRVMap"] = od()
globalReplacementMap["earlyAnalysisDiffYJ0"]["catRVMap"]["RECO_first_jet_eta_0p0_0p5_cat0"] = "RECO_first_jet_eta_0p0_0p5_cat0"
globalReplacementMap["earlyAnalysisDiffYJ0"]["catRVMap"]["RECO_first_jet_eta_0p0_0p5_cat1"] = "RECO_first_jet_eta_0p0_0p5_cat1"
globalReplacementMap["earlyAnalysisDiffYJ0"]["catRVMap"]["RECO_first_jet_eta_0p0_0p5_cat2"] = "RECO_first_jet_eta_0p0_0p5_cat2"
globalReplacementMap["earlyAnalysisDiffYJ0"]["catRVMap"]["RECO_first_jet_eta_0p5_1p2_cat0"] = "RECO_first_jet_eta_0p5_1p2_cat0"
globalReplacementMap["earlyAnalysisDiffYJ0"]["catRVMap"]["RECO_first_jet_eta_0p5_1p2_cat1"] = "RECO_first_jet_eta_0p5_1p2_cat1"
globalReplacementMap["earlyAnalysisDiffYJ0"]["catRVMap"]["RECO_first_jet_eta_0p5_1p2_cat2"] = "RECO_first_jet_eta_0p5_1p2_cat2"
globalReplacementMap["earlyAnalysisDiffYJ0"]["catRVMap"]["RECO_first_jet_eta_1p2_2p0_cat0"] = "RECO_first_jet_eta_1p2_2p0_cat0"
globalReplacementMap["earlyAnalysisDiffYJ0"]["catRVMap"]["RECO_first_jet_eta_1p2_2p0_cat1"] = "RECO_first_jet_eta_1p2_2p0_cat1"
globalReplacementMap["earlyAnalysisDiffYJ0"]["catRVMap"]["RECO_first_jet_eta_1p2_2p0_cat2"] = "RECO_first_jet_eta_1p2_2p0_cat2"
globalReplacementMap["earlyAnalysisDiffYJ0"]["catRVMap"]["RECO_first_jet_eta_2p0_2p5_cat0"] = "RECO_first_jet_eta_2p0_2p5_cat0"
globalReplacementMap["earlyAnalysisDiffYJ0"]["catRVMap"]["RECO_first_jet_eta_2p0_2p5_cat1"] = "RECO_first_jet_eta_2p0_2p5_cat1"
globalReplacementMap["earlyAnalysisDiffYJ0"]["catRVMap"]["RECO_first_jet_eta_2p0_2p5_cat2"] = "RECO_first_jet_eta_2p0_2p5_cat2"
globalReplacementMap["earlyAnalysisDiffYJ0"]["catRVMap"]["RECO_first_jet_eta_NJ0_cat0"] = "RECO_first_jet_eta_NJ0_cat0"
globalReplacementMap["earlyAnalysisDiffYJ0"]["catRVMap"]["RECO_first_jet_eta_NJ0_cat1"] = "RECO_first_jet_eta_NJ0_cat1"
globalReplacementMap["earlyAnalysisDiffYJ0"]["catRVMap"]["RECO_first_jet_eta_NJ0_cat2"] = "RECO_first_jet_eta_NJ0_cat2"


# Differential AbsPhiHJ0 
globalReplacementMap["earlyAnalysisDiffAbsPhiHJ0"] = od()
# Wrong vertex stuff, which process should be considered?
globalReplacementMap["earlyAnalysisDiffAbsPhiHJ0"]['procWV'] = "ggh_AbsPhiHJ0_0p0_2p6_in"
globalReplacementMap["earlyAnalysisDiffAbsPhiHJ0"]['catWV'] = "RECO_AbsPhiHJ0_0p0_2p6_cat2"
# Relacement processes for RV
globalReplacementMap["earlyAnalysisDiffAbsPhiHJ0"]['procRVMap'] = od()
globalReplacementMap["earlyAnalysisDiffAbsPhiHJ0"]["procRVMap"]["RECO_AbsPhiHJ0_0p0_2p6_cat0"] = "ggh_AbsPhiHJ0_0p0_2p6_in"
globalReplacementMap["earlyAnalysisDiffAbsPhiHJ0"]["procRVMap"]["RECO_AbsPhiHJ0_0p0_2p6_cat1"] = "ggh_AbsPhiHJ0_0p0_2p6_in"
globalReplacementMap["earlyAnalysisDiffAbsPhiHJ0"]["procRVMap"]["RECO_AbsPhiHJ0_0p0_2p6_cat2"] = "ggh_AbsPhiHJ0_0p0_2p6_in"
globalReplacementMap["earlyAnalysisDiffAbsPhiHJ0"]["procRVMap"]["RECO_AbsPhiHJ0_2p6_2p9_cat0"] = "ggh_AbsPhiHJ0_2p6_2p9_in"
globalReplacementMap["earlyAnalysisDiffAbsPhiHJ0"]["procRVMap"]["RECO_AbsPhiHJ0_2p6_2p9_cat1"] = "ggh_AbsPhiHJ0_2p6_2p9_in"
globalReplacementMap["earlyAnalysisDiffAbsPhiHJ0"]["procRVMap"]["RECO_AbsPhiHJ0_2p6_2p9_cat2"] = "ggh_AbsPhiHJ0_2p6_2p9_in"
globalReplacementMap["earlyAnalysisDiffAbsPhiHJ0"]["procRVMap"]["RECO_AbsPhiHJ0_2p9_3p03_cat0"] = "ggh_AbsPhiHJ0_2p9_3p03_in"
globalReplacementMap["earlyAnalysisDiffAbsPhiHJ0"]["procRVMap"]["RECO_AbsPhiHJ0_2p9_3p03_cat1"] = "ggh_AbsPhiHJ0_2p9_3p03_in"
globalReplacementMap["earlyAnalysisDiffAbsPhiHJ0"]["procRVMap"]["RECO_AbsPhiHJ0_2p9_3p03_cat2"] = "ggh_AbsPhiHJ0_2p9_3p03_in"
# globalReplacementMap["earlyAnalysisDiffAbsPhiHJ0"]["procRVMap"]["RECO_AbsPhiHJ0_3p03_Pi_cat0"] = "ggh_AbsPhiHJ0_3p03_Pi_in"
# globalReplacementMap["earlyAnalysisDiffAbsPhiHJ0"]["procRVMap"]["RECO_AbsPhiHJ0_3p03_Pi_cat1"] = "ggh_AbsPhiHJ0_3p03_Pi_in"
# globalReplacementMap["earlyAnalysisDiffAbsPhiHJ0"]["procRVMap"]["RECO_AbsPhiHJ0_3p03_Pi_cat2"] = "ggh_AbsPhiHJ0_3p03_Pi_in"
# globalReplacementMap["earlyAnalysisDiffAbsPhiHJ0"]["procRVMap"]["RECO_AbsPhiHJ0_NJ0_cat0"] = "ggh_AbsPhiHJ0_NJ0_in"
# globalReplacementMap["earlyAnalysisDiffAbsPhiHJ0"]["procRVMap"]["RECO_AbsPhiHJ0_NJ0_cat1"] = "ggh_AbsPhiHJ0_NJ0_in"
# globalReplacementMap["earlyAnalysisDiffAbsPhiHJ0"]["procRVMap"]["RECO_AbsPhiHJ0_NJ0_cat2"] = "ggh_AbsPhiHJ0_NJ0_in"

globalReplacementMap["earlyAnalysisDiffAbsPhiHJ0"]["procRVMap"]["RECO_AbsPhiHJ0_3p03_3p1415926_cat0"] = "ggh_AbsPhiHJ0_3p03_3p1415926_in"
globalReplacementMap["earlyAnalysisDiffAbsPhiHJ0"]["procRVMap"]["RECO_AbsPhiHJ0_3p03_3p1415926_cat1"] = "ggh_AbsPhiHJ0_3p03_3p1415926_in"
globalReplacementMap["earlyAnalysisDiffAbsPhiHJ0"]["procRVMap"]["RECO_AbsPhiHJ0_3p03_3p1415926_cat2"] = "ggh_AbsPhiHJ0_3p03_3p1415926_in"
globalReplacementMap["earlyAnalysisDiffAbsPhiHJ0"]["procRVMap"]["RECO_AbsPhiHJ0_NJ_cat0"] = "ggh_AbsPhiHJ0_NJ_in"
globalReplacementMap["earlyAnalysisDiffAbsPhiHJ0"]["procRVMap"]["RECO_AbsPhiHJ0_NJ_cat1"] = "ggh_AbsPhiHJ0_NJ_in"
globalReplacementMap["earlyAnalysisDiffAbsPhiHJ0"]["procRVMap"]["RECO_AbsPhiHJ0_NJ_cat2"] = "ggh_AbsPhiHJ0_NJ_in"

# Replacement categories for RV
globalReplacementMap["earlyAnalysisDiffAbsPhiHJ0"]["catRVMap"] = od()
globalReplacementMap["earlyAnalysisDiffAbsPhiHJ0"]["catRVMap"]["RECO_AbsPhiHJ0_0p0_2p6_cat0"] = "RECO_AbsPhiHJ0_0p0_2p6_cat0"
globalReplacementMap["earlyAnalysisDiffAbsPhiHJ0"]["catRVMap"]["RECO_AbsPhiHJ0_0p0_2p6_cat1"] = "RECO_AbsPhiHJ0_0p0_2p6_cat1"
globalReplacementMap["earlyAnalysisDiffAbsPhiHJ0"]["catRVMap"]["RECO_AbsPhiHJ0_0p0_2p6_cat2"] = "RECO_AbsPhiHJ0_0p0_2p6_cat2"
globalReplacementMap["earlyAnalysisDiffAbsPhiHJ0"]["catRVMap"]["RECO_AbsPhiHJ0_2p6_2p9_cat0"] = "RECO_AbsPhiHJ0_2p6_2p9_cat0"
globalReplacementMap["earlyAnalysisDiffAbsPhiHJ0"]["catRVMap"]["RECO_AbsPhiHJ0_2p6_2p9_cat1"] = "RECO_AbsPhiHJ0_2p6_2p9_cat1"
globalReplacementMap["earlyAnalysisDiffAbsPhiHJ0"]["catRVMap"]["RECO_AbsPhiHJ0_2p6_2p9_cat2"] = "RECO_AbsPhiHJ0_2p6_2p9_cat2"
globalReplacementMap["earlyAnalysisDiffAbsPhiHJ0"]["catRVMap"]["RECO_AbsPhiHJ0_2p9_3p03_cat0"] = "RECO_AbsPhiHJ0_2p9_3p03_cat0"
globalReplacementMap["earlyAnalysisDiffAbsPhiHJ0"]["catRVMap"]["RECO_AbsPhiHJ0_2p9_3p03_cat1"] = "RECO_AbsPhiHJ0_2p9_3p03_cat1"
globalReplacementMap["earlyAnalysisDiffAbsPhiHJ0"]["catRVMap"]["RECO_AbsPhiHJ0_2p9_3p03_cat2"] = "RECO_AbsPhiHJ0_2p9_3p03_cat2"
# globalReplacementMap["earlyAnalysisDiffAbsPhiHJ0"]["catRVMap"]["RECO_AbsPhiHJ0_3p03_Pi_cat0"] = "RECO_AbsPhiHJ0_3p03_Pi_cat0"
# globalReplacementMap["earlyAnalysisDiffAbsPhiHJ0"]["catRVMap"]["RECO_AbsPhiHJ0_3p03_Pi_cat1"] = "RECO_AbsPhiHJ0_3p03_Pi_cat1"
# globalReplacementMap["earlyAnalysisDiffAbsPhiHJ0"]["catRVMap"]["RECO_AbsPhiHJ0_3p03_Pi_cat2"] = "RECO_AbsPhiHJ0_3p03_Pi_cat2"
# globalReplacementMap["earlyAnalysisDiffAbsPhiHJ0"]["catRVMap"]["RECO_AbsPhiHJ0_NJ0_cat0"] = "RECO_AbsPhiHJ0_NJ0_cat0"
# globalReplacementMap["earlyAnalysisDiffAbsPhiHJ0"]["catRVMap"]["RECO_AbsPhiHJ0_NJ0_cat1"] = "RECO_AbsPhiHJ0_NJ0_cat1"
# globalReplacementMap["earlyAnalysisDiffAbsPhiHJ0"]["catRVMap"]["RECO_AbsPhiHJ0_NJ0_cat2"] = "RECO_AbsPhiHJ0_NJ0_cat2"

globalReplacementMap["earlyAnalysisDiffAbsPhiHJ0"]["catRVMap"]["RECO_AbsPhiHJ0_3p03_3p1415926_cat0"] = "RECO_AbsPhiHJ0_3p03_3p1415926_cat0"
globalReplacementMap["earlyAnalysisDiffAbsPhiHJ0"]["catRVMap"]["RECO_AbsPhiHJ0_3p03_3p1415926_cat1"] = "RECO_AbsPhiHJ0_3p03_3p1415926_cat1"
globalReplacementMap["earlyAnalysisDiffAbsPhiHJ0"]["catRVMap"]["RECO_AbsPhiHJ0_3p03_3p1415926_cat2"] = "RECO_AbsPhiHJ0_3p03_3p1415926_cat2"
globalReplacementMap["earlyAnalysisDiffAbsPhiHJ0"]["catRVMap"]["RECO_AbsPhiHJ0_NJ_cat0"] = "RECO_AbsPhiHJ0_NJ_cat0"
globalReplacementMap["earlyAnalysisDiffAbsPhiHJ0"]["catRVMap"]["RECO_AbsPhiHJ0_NJ_cat1"] = "RECO_AbsPhiHJ0_NJ_cat1"
globalReplacementMap["earlyAnalysisDiffAbsPhiHJ0"]["catRVMap"]["RECO_AbsPhiHJ0_NJ_cat2"] = "RECO_AbsPhiHJ0_NJ_cat2"

# Differential AbsYHJ0 
globalReplacementMap["earlyAnalysisDiffAbsYHJ0"] = od()
# Wrong vertex stuff, which process should be considered?
globalReplacementMap["earlyAnalysisDiffAbsYHJ0"]['procWV'] = "ggh_AbsYHJ0_0p0_0p6_in"
globalReplacementMap["earlyAnalysisDiffAbsYHJ0"]['catWV'] = "RECO_AbsYHJ0_NJ0_cat2"
# Relacement processes for RV
globalReplacementMap["earlyAnalysisDiffAbsYHJ0"]['procRVMap'] = od()
globalReplacementMap["earlyAnalysisDiffAbsYHJ0"]["procRVMap"]["RECO_AbsYHJ0_0p0_0p6_cat0"] = "ggh_AbsYHJ0_0p0_0p6_in"
globalReplacementMap["earlyAnalysisDiffAbsYHJ0"]["procRVMap"]["RECO_AbsYHJ0_0p0_0p6_cat1"] = "ggh_AbsYHJ0_0p0_0p6_in"
globalReplacementMap["earlyAnalysisDiffAbsYHJ0"]["procRVMap"]["RECO_AbsYHJ0_0p0_0p6_cat2"] = "ggh_AbsYHJ0_0p0_0p6_in"
globalReplacementMap["earlyAnalysisDiffAbsYHJ0"]["procRVMap"]["RECO_AbsYHJ0_0p6_1p2_cat0"] = "ggh_AbsYHJ0_0p6_1p2_in"
globalReplacementMap["earlyAnalysisDiffAbsYHJ0"]["procRVMap"]["RECO_AbsYHJ0_0p6_1p2_cat1"] = "ggh_AbsYHJ0_0p6_1p2_in"
globalReplacementMap["earlyAnalysisDiffAbsYHJ0"]["procRVMap"]["RECO_AbsYHJ0_0p6_1p2_cat2"] = "ggh_AbsYHJ0_0p6_1p2_in"
globalReplacementMap["earlyAnalysisDiffAbsYHJ0"]["procRVMap"]["RECO_AbsYHJ0_1p2_1p9_cat0"] = "ggh_AbsYHJ0_1p2_1p9_in"
globalReplacementMap["earlyAnalysisDiffAbsYHJ0"]["procRVMap"]["RECO_AbsYHJ0_1p2_1p9_cat1"] = "ggh_AbsYHJ0_1p2_1p9_in"
globalReplacementMap["earlyAnalysisDiffAbsYHJ0"]["procRVMap"]["RECO_AbsYHJ0_1p2_1p9_cat2"] = "ggh_AbsYHJ0_1p2_1p9_in"
globalReplacementMap["earlyAnalysisDiffAbsYHJ0"]["procRVMap"]["RECO_AbsYHJ0_1p9_100p0_cat0"] = "ggh_AbsYHJ0_1p9_100p0_in"
globalReplacementMap["earlyAnalysisDiffAbsYHJ0"]["procRVMap"]["RECO_AbsYHJ0_1p9_100p0_cat1"] = "ggh_AbsYHJ0_1p9_100p0_in"
globalReplacementMap["earlyAnalysisDiffAbsYHJ0"]["procRVMap"]["RECO_AbsYHJ0_1p9_100p0_cat2"] = "ggh_AbsYHJ0_1p9_100p0_in"
globalReplacementMap["earlyAnalysisDiffAbsYHJ0"]["procRVMap"]["RECO_AbsYHJ0_NJ0_cat0"] = "ggh_AbsYHJ0_NJ0_in"
globalReplacementMap["earlyAnalysisDiffAbsYHJ0"]["procRVMap"]["RECO_AbsYHJ0_NJ0_cat1"] = "ggh_AbsYHJ0_NJ0_in"
globalReplacementMap["earlyAnalysisDiffAbsYHJ0"]["procRVMap"]["RECO_AbsYHJ0_NJ0_cat2"] = "ggh_AbsYHJ0_NJ0_in"


# Replacement categories for RV
globalReplacementMap["earlyAnalysisDiffAbsYHJ0"]["catRVMap"] = od()
globalReplacementMap["earlyAnalysisDiffAbsYHJ0"]["catRVMap"]["RECO_AbsYHJ0_0p0_0p6_cat0"] = "RECO_AbsYHJ0_0p0_0p6_cat0"
globalReplacementMap["earlyAnalysisDiffAbsYHJ0"]["catRVMap"]["RECO_AbsYHJ0_0p0_0p6_cat1"] = "RECO_AbsYHJ0_0p0_0p6_cat1"
globalReplacementMap["earlyAnalysisDiffAbsYHJ0"]["catRVMap"]["RECO_AbsYHJ0_0p0_0p6_cat2"] = "RECO_AbsYHJ0_0p0_0p6_cat2"
globalReplacementMap["earlyAnalysisDiffAbsYHJ0"]["catRVMap"]["RECO_AbsYHJ0_0p6_1p2_cat0"] = "RECO_AbsYHJ0_0p6_1p2_cat0"
globalReplacementMap["earlyAnalysisDiffAbsYHJ0"]["catRVMap"]["RECO_AbsYHJ0_0p6_1p2_cat1"] = "RECO_AbsYHJ0_0p6_1p2_cat1"
globalReplacementMap["earlyAnalysisDiffAbsYHJ0"]["catRVMap"]["RECO_AbsYHJ0_0p6_1p2_cat2"] = "RECO_AbsYHJ0_0p6_1p2_cat2"
globalReplacementMap["earlyAnalysisDiffAbsYHJ0"]["catRVMap"]["RECO_AbsYHJ0_1p2_1p9_cat0"] = "RECO_AbsYHJ0_1p2_1p9_cat0"
globalReplacementMap["earlyAnalysisDiffAbsYHJ0"]["catRVMap"]["RECO_AbsYHJ0_1p2_1p9_cat1"] = "RECO_AbsYHJ0_1p2_1p9_cat1"
globalReplacementMap["earlyAnalysisDiffAbsYHJ0"]["catRVMap"]["RECO_AbsYHJ0_1p2_1p9_cat2"] = "RECO_AbsYHJ0_1p2_1p9_cat2"
globalReplacementMap["earlyAnalysisDiffAbsYHJ0"]["catRVMap"]["RECO_AbsYHJ0_1p9_100p0_cat0"] = "RECO_AbsYHJ0_1p9_100p0_cat0"
globalReplacementMap["earlyAnalysisDiffAbsYHJ0"]["catRVMap"]["RECO_AbsYHJ0_1p9_100p0_cat1"] = "RECO_AbsYHJ0_1p9_100p0_cat1"
globalReplacementMap["earlyAnalysisDiffAbsYHJ0"]["catRVMap"]["RECO_AbsYHJ0_1p9_100p0_cat2"] = "RECO_AbsYHJ0_1p9_100p0_cat2"
globalReplacementMap["earlyAnalysisDiffAbsYHJ0"]["catRVMap"]["RECO_AbsYHJ0_NJ0_cat0"] = "RECO_AbsYHJ0_NJ0_cat0"
globalReplacementMap["earlyAnalysisDiffAbsYHJ0"]["catRVMap"]["RECO_AbsYHJ0_NJ0_cat1"] = "RECO_AbsYHJ0_NJ0_cat1"
globalReplacementMap["earlyAnalysisDiffAbsYHJ0"]["catRVMap"]["RECO_AbsYHJ0_NJ0_cat2"] = "RECO_AbsYHJ0_NJ0_cat2"



###################################################################################################################################################################################################
###################################################################################################################################################################################################
###################################################################################################################################################################################################
# Intermediate Run3


# Differential PT
globalReplacementMap["earlyAnalysisDiffPt23"] = od()
# Wrong vertex stuff, which process should be considered?
globalReplacementMap["earlyAnalysisDiffPt23"]['procWV'] = "ggh_PTH_45p0_80p0_in"
globalReplacementMap["earlyAnalysisDiffPt23"]['catWV'] = "RECO_PTH_45p0_80p0_cat2"
# Relacement processes for RV
globalReplacementMap["earlyAnalysisDiffPt23"]['procRVMap'] = od()
globalReplacementMap["earlyAnalysisDiffPt23"]["procRVMap"]["RECO_PTH_0p0_15p0_cat0"] = "ggh_PTH_0p0_15p0_in"
globalReplacementMap["earlyAnalysisDiffPt23"]["procRVMap"]["RECO_PTH_0p0_15p0_cat1"] = "ggh_PTH_0p0_15p0_in"
globalReplacementMap["earlyAnalysisDiffPt23"]["procRVMap"]["RECO_PTH_0p0_15p0_cat2"] = "ggh_PTH_0p0_15p0_in"
globalReplacementMap["earlyAnalysisDiffPt23"]["procRVMap"]["RECO_PTH_15p0_30p0_cat0"] = "ggh_PTH_15p0_30p0_in"
globalReplacementMap["earlyAnalysisDiffPt23"]["procRVMap"]["RECO_PTH_15p0_30p0_cat1"] = "ggh_PTH_15p0_30p0_in"
globalReplacementMap["earlyAnalysisDiffPt23"]["procRVMap"]["RECO_PTH_15p0_30p0_cat2"] = "ggh_PTH_15p0_30p0_in"
globalReplacementMap["earlyAnalysisDiffPt23"]["procRVMap"]["RECO_PTH_30p0_45p0_cat0"] = "ggh_PTH_30p0_45p0_in"
globalReplacementMap["earlyAnalysisDiffPt23"]["procRVMap"]["RECO_PTH_30p0_45p0_cat1"] = "ggh_PTH_30p0_45p0_in"
globalReplacementMap["earlyAnalysisDiffPt23"]["procRVMap"]["RECO_PTH_30p0_45p0_cat2"] = "ggh_PTH_30p0_45p0_in"
globalReplacementMap["earlyAnalysisDiffPt23"]["procRVMap"]["RECO_PTH_45p0_80p0_cat0"] = "ggh_PTH_45p0_80p0_in"
globalReplacementMap["earlyAnalysisDiffPt23"]["procRVMap"]["RECO_PTH_45p0_80p0_cat1"] = "ggh_PTH_45p0_80p0_in"
globalReplacementMap["earlyAnalysisDiffPt23"]["procRVMap"]["RECO_PTH_45p0_80p0_cat2"] = "ggh_PTH_45p0_80p0_in"
globalReplacementMap["earlyAnalysisDiffPt23"]["procRVMap"]["RECO_PTH_80p0_120p0_cat0"] = "ggh_PTH_80p0_120p0_in"
globalReplacementMap["earlyAnalysisDiffPt23"]["procRVMap"]["RECO_PTH_80p0_120p0_cat1"] = "ggh_PTH_80p0_120p0_in"
globalReplacementMap["earlyAnalysisDiffPt23"]["procRVMap"]["RECO_PTH_80p0_120p0_cat2"] = "ggh_PTH_80p0_120p0_in"
globalReplacementMap["earlyAnalysisDiffPt23"]["procRVMap"]["RECO_PTH_120p0_200p0_cat0"] = "ggh_PTH_120p0_200p0_in"
globalReplacementMap["earlyAnalysisDiffPt23"]["procRVMap"]["RECO_PTH_120p0_200p0_cat1"] = "ggh_PTH_120p0_200p0_in"
globalReplacementMap["earlyAnalysisDiffPt23"]["procRVMap"]["RECO_PTH_120p0_200p0_cat2"] = "ggh_PTH_120p0_200p0_in"
globalReplacementMap["earlyAnalysisDiffPt23"]["procRVMap"]["RECO_PTH_200p0_350p0_cat0"] = "ggh_PTH_200p0_350p0_in"
globalReplacementMap["earlyAnalysisDiffPt23"]["procRVMap"]["RECO_PTH_200p0_350p0_cat1"] = "ggh_PTH_200p0_350p0_in"
globalReplacementMap["earlyAnalysisDiffPt23"]["procRVMap"]["RECO_PTH_200p0_350p0_cat2"] = "ggh_PTH_200p0_350p0_in"
globalReplacementMap["earlyAnalysisDiffPt23"]["procRVMap"]["RECO_PTH_350p0_10000p0_cat0"] = "ggh_PTH_350p0_10000p0_in"
globalReplacementMap["earlyAnalysisDiffPt23"]["procRVMap"]["RECO_PTH_350p0_10000p0_cat1"] = "ggh_PTH_350p0_10000p0_in"
globalReplacementMap["earlyAnalysisDiffPt23"]["procRVMap"]["RECO_PTH_350p0_10000p0_cat2"] = "ggh_PTH_350p0_10000p0_in"

# Replacement categories for RV
globalReplacementMap["earlyAnalysisDiffPt23"]["catRVMap"] = od()
globalReplacementMap["earlyAnalysisDiffPt23"]["catRVMap"]["RECO_PTH_0p0_15p0_cat0"] = "RECO_PTH_0p0_15p0_cat0"
globalReplacementMap["earlyAnalysisDiffPt23"]["catRVMap"]["RECO_PTH_0p0_15p0_cat1"] = "RECO_PTH_0p0_15p0_cat1"
globalReplacementMap["earlyAnalysisDiffPt23"]["catRVMap"]["RECO_PTH_0p0_15p0_cat2"] = "RECO_PTH_0p0_15p0_cat2"
globalReplacementMap["earlyAnalysisDiffPt23"]["catRVMap"]["RECO_PTH_15p0_30p0_cat0"] = "RECO_PTH_15p0_30p0_cat0"
globalReplacementMap["earlyAnalysisDiffPt23"]["catRVMap"]["RECO_PTH_15p0_30p0_cat1"] = "RECO_PTH_15p0_30p0_cat1"
globalReplacementMap["earlyAnalysisDiffPt23"]["catRVMap"]["RECO_PTH_15p0_30p0_cat2"] = "RECO_PTH_15p0_30p0_cat2"
globalReplacementMap["earlyAnalysisDiffPt23"]["catRVMap"]["RECO_PTH_30p0_45p0_cat0"] = "RECO_PTH_30p0_45p0_cat0"
globalReplacementMap["earlyAnalysisDiffPt23"]["catRVMap"]["RECO_PTH_30p0_45p0_cat1"] = "RECO_PTH_30p0_45p0_cat1"
globalReplacementMap["earlyAnalysisDiffPt23"]["catRVMap"]["RECO_PTH_30p0_45p0_cat2"] = "RECO_PTH_30p0_45p0_cat2"
globalReplacementMap["earlyAnalysisDiffPt23"]["catRVMap"]["RECO_PTH_45p0_80p0_cat0"] = "RECO_PTH_45p0_80p0_cat0"
globalReplacementMap["earlyAnalysisDiffPt23"]["catRVMap"]["RECO_PTH_45p0_80p0_cat1"] = "RECO_PTH_45p0_80p0_cat1"
globalReplacementMap["earlyAnalysisDiffPt23"]["catRVMap"]["RECO_PTH_45p0_80p0_cat2"] = "RECO_PTH_45p0_80p0_cat2"
globalReplacementMap["earlyAnalysisDiffPt23"]["catRVMap"]["RECO_PTH_80p0_120p0_cat0"] = "RECO_PTH_80p0_120p0_cat0"
globalReplacementMap["earlyAnalysisDiffPt23"]["catRVMap"]["RECO_PTH_80p0_120p0_cat1"] = "RECO_PTH_80p0_120p0_cat1"
globalReplacementMap["earlyAnalysisDiffPt23"]["catRVMap"]["RECO_PTH_80p0_120p0_cat2"] = "RECO_PTH_80p0_120p0_cat2"
globalReplacementMap["earlyAnalysisDiffPt23"]["catRVMap"]["RECO_PTH_120p0_200p0_cat0"] = "RECO_PTH_120p0_200p0_cat0"
globalReplacementMap["earlyAnalysisDiffPt23"]["catRVMap"]["RECO_PTH_120p0_200p0_cat1"] = "RECO_PTH_120p0_200p0_cat1"
globalReplacementMap["earlyAnalysisDiffPt23"]["catRVMap"]["RECO_PTH_120p0_200p0_cat2"] = "RECO_PTH_120p0_200p0_cat2"
globalReplacementMap["earlyAnalysisDiffPt23"]["catRVMap"]["RECO_PTH_200p0_350p0_cat0"] = "RECO_PTH_200p0_350p0_cat0"
globalReplacementMap["earlyAnalysisDiffPt23"]["catRVMap"]["RECO_PTH_200p0_350p0_cat1"] = "RECO_PTH_200p0_350p0_cat1"
globalReplacementMap["earlyAnalysisDiffPt23"]["catRVMap"]["RECO_PTH_200p0_350p0_cat2"] = "RECO_PTH_200p0_350p0_cat2"
globalReplacementMap["earlyAnalysisDiffPt23"]["catRVMap"]["RECO_PTH_350p0_10000p0_cat0"] = "RECO_PTH_350p0_10000p0_cat0"
globalReplacementMap["earlyAnalysisDiffPt23"]["catRVMap"]["RECO_PTH_350p0_10000p0_cat1"] = "RECO_PTH_350p0_10000p0_cat1"
globalReplacementMap["earlyAnalysisDiffPt23"]["catRVMap"]["RECO_PTH_350p0_10000p0_cat2"] = "RECO_PTH_350p0_10000p0_cat2"